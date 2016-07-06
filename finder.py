'''
This module takes a collection as input, and builds a "reversed index":
word -> items

There are then 3 ways to search:

exact=True -> finds all items containing the exact term
exact=False -> finds all items containing the prefix (slower)

TODO!!!
onlyin=[keys] -> returns only the items where the term/prefix is contained in one of the keys

weights={key1:weight1,...} -> retrieves all items matching, score them and sort them. 
It's slower since all items have to be retrieved and sorted first.
'''

import sys
sys.path.append('../pysos')
import string
import pysos
import re
import bisect
import os.path
from collections import namedtuple

Hit = namedtuple('Hit', 'key, value, score')

# small words like "a", "the", etc. are usually associated with so many items that the cost overweights the benefits.
# for small words, you can as well iterate over all values.
# in the ideal case, it should depend on the frequency of the word rather than the length.
# However, doing that adds complexity, slowness and non-determinism: 
# depending on the order in which you update entries, a word might still be contained ...or not.
MIN_TOKEN_LENGTH = 3
# this limit is used in order to avoid giant tokens due to binary/encoded data items
TOKEN_SIZE_LIMIT = 20

SPLIT_INNER_PUNCTUATION = True

def _walk(obj):
    if not obj:
        return
    if isinstance(obj,dict):
        for child in obj.values():
            for leaf in _walk(child):
                yield leaf
    elif isinstance(obj,list):
        for child in obj:
            for leaf in _walk(child):
                yield leaf
    else:
        yield obj
        


    
    
def tokenize(val):
    tokens = str(val).lower().split()
    tokens = [ t.strip(string.punctuation)[:TOKEN_SIZE_LIMIT] for t in tokens ]
    if SPLIT_INNER_PUNCTUATION:
        more = []
        for t in tokens:
            ts = re.split('\W+', t)
            if len(ts) > 1:
                more += ts
        tokens += more
    # split big tokens according to punctuation?
    # support non-latin languages punctuation?
    # chinese/japanese word splitting?
    #map( lambda t: t.strip(string.punctuation)[:TOKEN_SIZE_LIMIT], tokens )
    return tokens


def iterate(obj):
    if isinstance(obj, dict):
        return obj.keys()
    if isinstance(obj, list):
        return range(len(obj))
    raise Exception("Can only iterate over lists or dicts.")


def index(collection, keys=None):
    '''Returns an index: word -> ["key1","key2",...]'''

    indexes = {}
    i = 0
    for key in iterate(collection):
        i += 1
        if i % 1000 == 0:
            print('%12d' % i)
            
        item = collection[key]
        
        unique = set()
        for val in _walk(item):
            tokens = tokenize(val)
            for t in tokens:
                if len(t) < MIN_TOKEN_LENGTH:
                    continue
                unique.add(t)
        
        for u in unique:
            if u in indexes:
                indexes[u].append(key)
                #hits = indexes[t]
                #if hits:
                #    hits.append(key)
                #    if len(hits) > 10000:
                #        indexes[t] = False
                #        print('Too big: ' + t)
            else:
                indexes[u] = [key]
    
    #import pysos.pysos as pysos
    #d = pysos.Dict('temp.index.sos')
    #for k,v in indexes.items():
    #    d[k] = v
    #d.close()
    
    return indexes


def score(obj, word, weights={}, exact=True):
    s = 0
    
    if not weights:
        tokens = []
        for val in _walk(obj):
            tokens += tokenize(val)
        if exact:
            s = tokens.count(word) / len(tokens)
        else:
            n = 0
            for t in tokens:
                if t.startswith(word):
                    n += 1
            s = n / len(tokens)
    else:  
        for (key, weight) in weights.items():
            if not weight:
                continue
            if isinstance(obj, list):
                key = int(key)
                if key >= len(obj):
                    continue
            else:
                if key not in obj:
                    continue
            val = obj[key]
            tokens = tokenize(val)
            if exact:
                s += weight * tokens.count(word) / len(tokens)
            else:
                n = 0
                for t in tokens:
                    if t.startswith(word):
                        n += 1
                s += weight * n / len(tokens)
            
    return s

def filt(obj, word, keys):
    if not keys:
        raise Exception('No keys provided!')
        
class Finder:
    
    def __init__(self, collection, index_file=None, keys=None):
        self._collection = collection
        self._keys = keys
        
        if index_file:
            if os.path.exists(index_file):
                # load it from file
                self._index = pysos.Dict(index_file)
            else:
                # create it
                self._index = pysos.Dict(index_file)
                for k,v in index(collection, keys).items():
                    self._index[k] = v    
        else:
            # use an in-memory one
            self._index = index(collection, keys)    
        self._voc = sorted(self._index.keys())
        
    def words(self, prefix):
        '''Returns all words in the vocabulary starting with prefix'''
        i = bisect.bisect_left( self._voc, prefix )
        j = bisect.bisect_right( self._voc, prefix + 'z' )
        return self._voc[i:j]
    
    
    def searchKeys(self, word, exact=True):
        word = tokenize(word)[0]
        if exact:
            if word not in self._index:
                return
            for key in self._index[word]:
                yield key
        else:
            for w in self.words(word):
                for key in self._index[w]:
                    yield key
        
    def searchValues(self, word, exact=True):
        for key in self.searchKeys(word, exact):
            yield self._collection[key]
    
  
    def find(self, word, exact=True, weights={}):
        word = tokenize(word)[0]
        results = []
        i = 0
        for key in self.searchKeys(word, exact):
            val = self._collection[key]
            s = score(val, word, weights, exact)
            assert weights or s > 0
            if s <= 0:
                continue
            
            results.append( Hit(key, val, s) )
        print("Total searched: %d " % i)
        results.sort(key=lambda hit: -hit.score)
        return results
    
    def update(self, key, val, old):
        assert val != None or old != None
        if old == None:
            # a new value
            idx = index({key: val}, self._keys)
            for word, k in idx.items():
                assert [key] == k
                if word in self._index:
                    self._index[word].append(key)
                else:
                    self._index[word] = [key]
                    bisect.insort(self._voc, word)
        elif val == None:
            # a deleted value
            idx = index({key: old}, self._keys)
            for word, k in idx.items():
                assert [key] == k
                assert (word in self._index)
                self._index[word].remove(key)
                if not self._index[word]:
                    del self._index[word]
                    i = bisect.bisect_left(self._voc, word)
                    del self._voc[ i ]
        else:
            # an updated value
            #idx_old = index({key: old}, self._keys)
            #idx_val = index({key: val}, self._keys)
            # TODO: optimize this quick and dirty trick by comparing the two outputs
            # delete it first
            self.update(key, None, old)
            # add the new one afterwards
            self.update(key, val, None)
        

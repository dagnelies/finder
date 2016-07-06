import random
import time
import os
import sys
sys.path.append('../pysos')
import pysos
import finder
import psutil
import gc
import pickle
import cProfile
from finder import Hit

db = ["Alice's Adventures in Wonderland", "Bob the average dude", "Charlie's angels", "Dude", "Elisabeth, Queen of England", 1234.5678]
f = finder.Finder(db)

# find everythin containing "dude"
assert f.find('dude') == [Hit(key=3, value='Dude', score=1.0), Hit(key=1, value='Bob the average dude', score=0.25)]

# casing is ignored
assert f.find('DuDe') == [Hit(key=3, value='Dude', score=1.0), Hit(key=1, value='Bob the average dude', score=0.25)]

# searching a word must fit perfectly
assert f.find('wonder') == []

# or you specify exact=False, to search all words starting with "wonder". It's slower though.
assert f.find('wonder', exact=False) == [Hit(key=0, value="Alice's Adventures in Wonderland", score=1/6)]

# you can also search for numbers
print(f.find('1234.5678'))


exit()


def RAM(obj):
    temp = obj._collection
    obj._collection = None
    size = len(pickle.dumps(obj)) / 1024 / 1024
    obj._collection = temp
    return size
    
start = time.time()

FILE = 'omdb_10k.sos'
db = pysos.List(FILE)

print("%.2fs: %d items loaded" % (time.time() - start, len(db)))

#cProfile.run('finder = finder.Finder(db)')

finder = finder.Finder(db, FILE + '.idx')

print("%.2fs" % (time.time() - start))
print("%.2fs: %d indexed words" % (time.time() - start, len(finder._voc)) )
#print("%.2fs: RAM: %.2f mb" % (time.time() - start, RAM(finder)) )
print("%.2fs" % (time.time() - start))

f = finder
db.observe(f.update)

db[111] = {'foo': 'testtest'}

res = f.search('testtest')
print(next(res))

#res = f.find('ali', exact=False, weights={'Title':1})
res = f.search('alice')
print(next(res))
print("%.2fs first found" % (time.time() - start))
print( len(list(res)) )
print("%.2fs all found" % (time.time() - start))
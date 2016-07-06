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


def RAM(obj):
    temp = obj._collection
    obj._collection = None
    size = len(pickle.dumps(obj)) / 1024 / 1024
    obj._collection = temp
    return size
    
start = time.time()

db = pysos.List('omdb.txt.sos_10k')

print("%.2fs: %d items loaded" % (time.time() - start, len(db)))

#cProfile.run('finder = finder.Finder(db)')

finder = finder.Finder(db)

print("%.2fs" % (time.time() - start))
print("%.2fs: %d indexed words" % (time.time() - start, len(finder._voc)) )
print("%.2fs: RAM: %.2f mb" % (time.time() - start, RAM(finder)) )
print("%.2fs" % (time.time() - start))

f = finder
#res = f.find('ali', exact=False, weights={'Title':1})
res = f.search('alice')
print(next(res))
print("%.2fs first found" % (time.time() - start))
print( len(list(res)) )
print("%.2fs all found" % (time.time() - start))
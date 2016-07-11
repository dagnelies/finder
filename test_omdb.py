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
print(res)

print("---------------")

start = time.time()
res = f.search('alice') 
cProfile.run("res = f.search('alice')")
print(len(res))
print("%.2fs normal search" % (time.time() - start))

start = time.time()
res = f.search_old('the')
print("%.2fs old search" % (time.time() - start))


start = time.time()
#res = f.find('ali', exact=False, weights={'Title':1})
#cProfile.run("res = f.search('the')")
res = f.search('the')
#print(next(res))
print("%.2fs normal search" % (time.time() - start))


start = time.time()
res = f.search_old('the')
print("%.2fs old search" % (time.time() - start))
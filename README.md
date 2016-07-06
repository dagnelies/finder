Finder
======

This python module performs indexing and full text search on a dict, list, or any compatible data structure such as a DB mapping.

Usage:
```
from finder import Finder, Hit

db = ["Alice's Adventures in Wonderland", "Bob the average dude", "Charlie's angels", "Dude", "Elisabeth, Queen of England", 1234.5678]
f = Finder(db)

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
```
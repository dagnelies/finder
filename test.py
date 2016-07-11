import finder
import cProfile
from finder import Hit


db = ["Alice's Adventures in Wonderland", "Bob the average dude", "Charlie's angels", "Dude", "Elisabeth, Queen of England", 1234.5678]
f = finder.Finder(db)

# find everythin containing "dude"
assert f.search('dude') == [Hit(key=3, value='Dude', score=1.0), Hit(key=1, value='Bob the average dude', score=0.25)]

# casing is ignored
assert f.search(' DuDe ') == [Hit(key=3, value='Dude', score=1.0), Hit(key=1, value='Bob the average dude', score=0.25)]

# searching a word must fit perfectly
assert f.search('wonder') == []

# or you specify exact=False, to search all words starting with "wonder". It's slower though.
assert f.search('wonder', exact=False) == [Hit(key=0, value="Alice's Adventures in Wonderland", score=0.2)]

# you can also search for numbers
assert f.search('1234.5678') == [Hit(key=5, value=1234.5678, score=1.0)]



from setuptools import setup, find_packages


setup(
    name='finder',
    version='0.2.0',
    py_modules=['finder'],
    scripts=['finder.py'],
    description='Performs full text search on large python dict/lists.',
    url='https://github.com/dagnelies/finder',
    author='Arnaud Dagnelies',
    author_email='arnaud.dagnelies@gmail.com',
    license='MIT',
    classifiers=[],
    keywords='full text search reverse index'
)
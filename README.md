# Wikipedia Search Engine

- Sanchit Arora (2019101047)

Provide efficient search results on Wikipedia data of huge size.

## Installation

1. Ensure Python 3.8+ & `pip` is installed.
2. Install all requirements (preferably inside virtual environment): `pip3 install -r requirements.txt`

## File Descriptions

`constants.py`
As the name suggests, it contains important constants.

`file_mappings.py`
It contains functions to get file names of index files depending on token, doc number, etc.

`helper.py`
Contains helper functions for tokenization, text cleaning, etc.

`index.py`
Contains code for `Index` class. Used for adding token in index, searching, compressing, decompressing, etc.

`indexer.py`
Main code for indexing whole data

`number_system`
Contains code for `NumberSystem` class. Used to encode and decode decimal numbers to base 64.

`search.py`
Main code for searching

`stop_words.py` and `stemmed_stop_words.py`
Contains list of stop words

`stemmer.py`
Contains code for `Stemmer` class. Used to stem tokens

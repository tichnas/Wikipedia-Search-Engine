# Wikipedia Search Engine

- Sanchit Arora (2019101047)

Provide efficient search results on Wikipedia data of huge size.

## Installation

1. Ensure Python 3.8+ & `pip` is installed.
2. Install all requirements (preferably inside virtual environment): `pip3 install -r requirements.txt`

## Running

1. Build index: `bash index.sh <path_to_wiki_dump> <path_to_inverted_index_directory> <path_to_stat_file>`.
2. Search: `bash search.sh <path_to_inverted_index_directory> <query_string>`

## Performance

On a data size of ~190 MB:

1. Index is built in ~120 seconds
2. Index size is ~27 MB

import sys, os, re, bisect

from stemmer import Stemmer
from index import Index
from file_mappings import is_token_index_file, get_token_index_file


INDEX_FOLDER = "index_data"
QUERY = "football world cup"

get_file_path = lambda filename: os.path.join(INDEX_FOLDER, filename)

stemmer = Stemmer()
index = Index()

index_files = sorted(
    [filename for filename in os.listdir(INDEX_FOLDER) if is_token_index_file(filename)]
)


tokens = re.split(" |t:|i:|c:", QUERY)

for token in tokens:
    token = stemmer.stem(token.lower())

    file_index = bisect.bisect(index_files, get_token_index_file(token)) - 1

    docs = (
        []
        if file_index == -1
        else index.search(token, get_file_path(index_files[file_index]))
    )

    print(token)
    for doc in docs:
        print(doc)
    print()

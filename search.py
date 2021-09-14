import sys, os, re, bisect, math, time, heapq

from stemmer import Stemmer
from index import Index
from number_system import NumberSystem
from file_mappings import (
    is_token_index_file,
    get_token_index_file,
    get_doc_title_file,
)
from constants import PAGES_IN_TITLE_FILE, TOTAL_PAGES

start_time = time.time()

INDEX_FOLDER = "index_data"
QUERY = "football world cup"

get_file_path = lambda filename: os.path.join(INDEX_FOLDER, filename)

stemmer = Stemmer()
index = Index()
number_system = NumberSystem()

index_files = sorted(
    [filename for filename in os.listdir(INDEX_FOLDER) if is_token_index_file(filename)]
)

doc_term_counts = {}
doc_scores = {}

get_doc_title_time = 0


def tokenize(text):
    return re.split("[^a-zA-Z0-9]+", text)


def get_doc_title(docid):
    global get_doc_title_time

    s = time.time()

    file = open(get_file_path(get_doc_title_file(docid)), "r")

    line = None
    for i in range((docid - 1) % PAGES_IN_TITLE_FILE + 1):
        line = file.readline()

    file.close()

    e = time.time()
    get_doc_title_time += e - s

    return line[:-1]


def assign_scores(docs):
    for doc in docs:
        doc_id = doc[0]
        tf = (doc[1] * 2.2) / (doc[1] + 1.2)
        idf = math.log(TOTAL_PAGES / (len(docs) + 1))

        if doc_id not in doc_scores:
            doc_scores[doc_id] = [0, 1]

        doc_scores[doc_id][0] += tf * idf
        doc_scores[doc_id][1] *= 1 + tf * idf


get_doc_rank = lambda doc_id: doc_scores[doc_id][0] * math.log(doc_scores[doc_id][1])


def get_top_results(count):
    doc_data = [(get_doc_rank(doc), doc) for doc in doc_scores]

    top_docs = heapq.nlargest(count, doc_data)

    top_results = [doc[1] for doc in top_docs]

    return top_results


tokens = tokenize(QUERY)

index_search_time = 0
score_assign_time = 0

tokens_time = []


for token in tokens:
    ts = time.time()

    token = stemmer.stem(token.lower())

    file_index = bisect.bisect(index_files, get_token_index_file(token)) - 1

    print(token + " " + index_files[file_index])

    s = time.time()

    docs = (
        []
        if file_index == -1
        else index.search(token, get_file_path(index_files[file_index]))
    )

    e = time.time()
    index_search_time += e - s

    s = time.time()

    assign_scores(docs)

    e = time.time()
    score_assign_time += e - s

    te = time.time()
    tokens_time.append(str(te - ts)[0:5])


top_start_time = time.time()

top_10_results = get_top_results(10)

for doc in top_10_results:
    print(str(doc) + ":", get_doc_title(doc))


end_time = time.time()

print()
print("Time taken:", str(end_time - start_time)[0:5], "seconds")
print("Top 10 Time taken:", str(end_time - top_start_time)[0:5], "seconds")
print("Title fetch time:", str(get_doc_title_time)[0:5], "seconds")
print("Index search fetch time:", str(index_search_time)[0:5], "seconds")
print("Score assign time:", str(score_assign_time)[0:5], "seconds")
print("Tokens time:", tokens_time)

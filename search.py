import sys, os, re, bisect, math, time

from stemmer import Stemmer
from index import Index
from number_system import NumberSystem
from file_mappings import (
    is_token_index_file,
    get_token_index_file,
    get_doc_terms_count_file,
    get_doc_title_file,
)
from constants import PAGES_IN_TITLE_FILE, PAGES_IN_TOKEN_COUNT_FILE, TOTAL_PAGES

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

get_doc_term_time = 0
get_doc_title_time = 0


def tokenize(text):
    return re.split("[^a-zA-Z0-9]+", text)


def get_doc_term_count(docid):
    global get_doc_term_time
    if docid in doc_term_counts:
        return doc_term_counts[docid]

    s = time.time()

    file = open(get_file_path(get_doc_terms_count_file(docid)), "r")

    line = None
    for i in range((docid - 1) % PAGES_IN_TOKEN_COUNT_FILE + 1):
        line = file.readline()

    file.close()
    doc_term_counts[docid] = number_system.decode(line[:-1])

    e = time.time()
    get_doc_term_time += e - s

    return doc_term_counts[docid]


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
        doc_term_count = get_doc_term_count(doc_id)
        doc_term_count = 1
        tf = doc[1] / doc_term_count
        idf = math.log(TOTAL_PAGES / (len(docs) + 1))

        if doc_term_count < 60:
            tf /= 10

        if doc_id not in doc_scores:
            doc_scores[doc_id] = [0, 1]

        doc_scores[doc_id][0] += tf * idf
        doc_scores[doc_id][1] *= tf * idf


get_doc_rank = lambda doc_id: doc_scores[doc_id][0] * math.log(doc_scores[doc_id][1])


def get_top_results(count):
    res = []

    for i in range(count):
        max_score = 0
        max_score_doc = None

        for doc in doc_scores:
            if get_doc_rank(doc) > max_score:
                max_score = get_doc_rank(doc)
                max_score_doc = doc

        if max_score_doc:
            res.append(max_score_doc)
            doc_scores[max_score_doc] = [0, 1]
        else:
            break

    return res


tokens = tokenize(QUERY)


for token in tokens:
    token = stemmer.stem(token.lower())

    file_index = bisect.bisect(index_files, get_token_index_file(token)) - 1

    docs = (
        []
        if file_index == -1
        else index.search(token, get_file_path(index_files[file_index]))
    )

    assign_scores(docs)


top_start_time = time.time()

top_10_results = get_top_results(10)

for doc in top_10_results:
    print(str(doc) + ":", get_doc_title(doc))


end_time = time.time()

print()
print("Time taken:", str(end_time - start_time)[0:5], "seconds")
print("Top 10 Time taken:", str(end_time - top_start_time)[0:5], "seconds")
print("Title fetch time:", str(get_doc_title_time)[0:5], "seconds")
print("Term Count fetch time:", str(get_doc_term_time)[0:5], "seconds")

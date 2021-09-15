import sys, os, re, bisect, math, time, heapq

from stemmer import Stemmer
from index import Index
from number_system import NumberSystem
from file_mappings import (
    is_token_index_file,
    get_token_index_file,
    get_doc_title_file,
)
from constants import (
    PAGES_IN_TITLE_FILE,
    SEARCH_RESULTS_FILE,
    TOTAL_PAGES,
    INDEX_FOLDER,
)


QUERIES_FILE = sys.argv[1]

get_file_path = lambda filename: os.path.join(INDEX_FOLDER, filename)

stemmer = Stemmer()
index = Index()
number_system = NumberSystem()

index_files = sorted(
    [filename for filename in os.listdir(INDEX_FOLDER) if is_token_index_file(filename)]
)

doc_scores = {}


field_symbols = {"t:": 0, "b:": 1, "i:": 2, "c:": 3, "l:": 4, "r:": 5}


def tokenize(text):
    tokens = []

    fields_separated = re.split("(t:|b:|i:|c:|l:|r:)", text)

    for t in fields_separated:
        if t in field_symbols:
            tokens.append(t)
        else:
            tokens.extend(re.split("[^a-zA-Z0-9]+", t))

    return tokens


def get_doc_title(docid):
    file = open(get_file_path(get_doc_title_file(docid)), "r")

    line = None
    for i in range((docid - 1) % PAGES_IN_TITLE_FILE + 1):
        line = file.readline()

    file.close()

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


def search(query, output_file):
    global doc_scores

    doc_scores = {}
    field_selected = -1

    start_time = time.time()

    tokens = tokenize(query)

    for token in tokens:
        if not token:
            continue

        if token in field_symbols:
            field_selected = field_symbols[token]
            continue

        token = stemmer.stem(token.lower())

        file_index = bisect.bisect(index_files, get_token_index_file(token)) - 1

        docs = (
            []
            if file_index == -1
            else index.search(token, get_file_path(index_files[file_index]))
        )

        if field_selected != -1:
            docs = list(filter(lambda doc: doc[2][field_selected], docs))

        assign_scores(docs)

    top_10_results = get_top_results(10)

    for doc in top_10_results:
        output_file.write(str(doc) + ": " + get_doc_title(doc) + "\n")

    if len(top_10_results) == 0:
        output_file.write(
            "Your search - " + query + " - did not match any documents.\n"
        )
        output_file.write("Suggestions: \n")
        output_file.write("- Make sure that all words are spelled correctly.\n")
        output_file.write("- Try different keywords.\n")
        output_file.write("- Try more general keywords.\n")

    end_time = time.time()

    output_file.write(
        "\nTime taken: " + str(end_time - start_time)[0:5] + " seconds\n\n"
    )


output_file = open(SEARCH_RESULTS_FILE, "w")
query_file = open(QUERIES_FILE, "r")

while True:
    line = query_file.readline()

    if not line:
        break

    search(line[:-1], output_file)

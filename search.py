import re
import pickle

from stemmer import Stemmer
from number_system import char_to_dec
from stop_words import stop_words
from stemmed_stop_words import stemmed_stop_words

stemmer = Stemmer()

index = pickle.load(open("index0", "rb"))

query = "t:World Cup i:2018 c:Football"

tokens = re.split(" |t:|i:|c:", query)

result = {}

for token in tokens:
    if not token:
        continue

    stemmed_token = stemmer.stem(token.lower())

    field_names = ["title", "body", "infobox", "categories", "references", "links"]
    field_docs = [[], [], [], [], [], []]

    for doc in index[stemmed_token]:
        doc_id = doc[0]
        existence = char_to_dec[doc[1][-1]]

        for type in range(6):
            if existence & (1 << type):
                if len(field_docs[type]) < 10:
                    field_docs[type].append(str(doc_id) + ":" + doc[1][:-1])

    result[token] = {}
    for type in range(6):
        result[token][field_names[type]] = field_docs[type]

for word in result:
    print("=====", word, "=====")
    for type in result[word]:
        print(type, "->", result[word][type])
    print()

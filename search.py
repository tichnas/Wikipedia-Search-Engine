import re
import json

from stemmer import Stemmer
from index import Index

stemmer = Stemmer()
index = Index()

index.load(open("index0", "r"))

query = "t:World Cup i:2018 c:Football"

tokens = re.split(" |t:|i:|c:", query)

result = {}

for token in tokens:
    if not token:
        continue

    result[token] = {}

    stemmed_token = stemmer.stem(token.lower())

    search_result = index.search(stemmed_token)

    field_names = ["title", "body", "infobox", "categories", "links", "references"]

    for name in field_names:
        result[token][name] = []

    for res in search_result:
        for i in range(6):
            if res[2][i]:
                result[token][field_names[i]].append(res[0])


print(json.dumps(result, indent=4, sort_keys=True))

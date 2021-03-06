##################################
##
##   NOTE: Assumes filling in order of page, i.e., all tokens of page 1 are added before tokens of page 2
##
##   Index Format:
##
##   token -> [
##      [page num change from previous, score, [inTitle, inBody, inInfobox, inCategory, inLink, inReference]],
##      ...
##      ]
##
##
##   Compressed Index Format:
##
##   token doc_id1 score1score_type1 doc_id2 score2_score_type2 ...
##   ...
##
##   score_typei is type of score, i.e., a single letter storing info about places where token occured in that doc (in title, body, etc.)
##   scorei is simply the weighted score for that token in that doc
##   doc_idi is page or document number starting from 1
##   Everything is encoded using custom number system (base 64)
##
##################################

import heapq
from constants import WEIGHTAGE
from number_system import NumberSystem
from file_mappings import get_token_id


class Index:
    def __init__(self, benchmark_score=0):
        self._index = {}
        self._token_score = {}
        self._benchmark_score = benchmark_score
        self._number_system = NumberSystem()

    def reset(self):
        self._index = {}
        self._token_score = {}

    def add(self, token, page, type):
        if token not in self._index:
            self._index[token] = []

        if not self._index[token] or self._index[token][-1][0] != page:
            self._index[token].append([page, 0, [0, 0, 0, 0, 0, 0]])

        self._index[token][-1][1] += WEIGHTAGE[type]
        self._index[token][-1][2][type] = 1

        if token not in self._token_score:
            self._token_score[token] = 0
        self._token_score[token] += WEIGHTAGE[type]

    def _compress_token(self, token, output):
        output.append(token)
        output.append(" ")

        for doc in self._index[token]:
            output.append(self._number_system.encode(doc[0]))
            output.append(" ")
            output.append(self._number_system.encode(doc[1]))

            score_type = 0
            p = 1
            for i in doc[2]:
                score_type += i * p
                p <<= 1

            output.append(self._number_system.encode(score_type))
            output.append(" ")

        output[-1] = "\n"

    def _decompress_token(self, data):
        data = data.split(" ")

        result = []
        last_doc_id = 0

        for i in range(1, len(data), 2):
            doc_id = self._number_system.decode(data[i]) + last_doc_id
            last_doc_id = doc_id
            score = self._number_system.decode(data[i + 1][:-1])
            score_type = self._number_system.decode(data[i + 1][-1])

            existence = []
            for p in range(6):
                existence.append(1 if score_type & (1 << p) else 0)

            result.append([doc_id, score, existence])

        return result

    def get_compressed(self):
        output = {}

        for token in self._index:
            if self._token_score[token] > self._benchmark_score:
                id = get_token_id(token)
                if id not in output:
                    output[id] = []

                self._compress_token(token, output[id])

        for id in output:
            output[id] = "".join(output[id])

        return output

    def load_merge_write(self, file_path):
        # Doesn't change/use current state
        # Sorts by token
        # Keeps only top 1e5 (1 lakh) docs for each token

        file_obj = open(file_path, "a+")

        file_obj.seek(0)
        index = {}

        while True:
            line = file_obj.readline()

            if not line:
                break

            pos = 0

            token = []
            for i in line:
                pos += 1
                if i == " ":
                    break
                token.append(i)
            token = "".join(token)

            if token not in index:
                index[token] = [token]

            index[token].extend(line[pos:-1].split(" "))

        output = []

        for token in sorted(index.keys()):
            doc_data = []
            for i in range(1, len(index[token]), 2):
                doc_data.append(
                    (
                        self._number_system.decode(index[token][i + 1][:-1]),
                        index[token][i],
                    )
                )

            top_docs_list = heapq.nlargest(int(1e5), doc_data)
            top_docs = set()
            for doc in top_docs_list:
                top_docs.add(doc[1])

            top_index = [token]

            prefix_sum = 0
            for i in range(1, len(index[token]), 2):
                if index[token][i] not in top_docs:
                    continue

                num = self._number_system.decode(index[token][i])
                num -= prefix_sum
                prefix_sum += num

                top_index.append(self._number_system.encode(num))
                top_index.append(index[token][i + 1])

            output.append(" ".join(top_index))
            output.append("\n")

        file_obj.truncate(0)
        file_obj.seek(0)
        file_obj.write("".join(output))

        file_obj.close()

    def search(self, token, file_path):
        file = open(file_path, "r")
        data = token

        while True:
            line = file.readline()

            if not line:
                break

            cur_token = []
            for i in line:
                if i == " ":
                    break
                cur_token.append(i)
            cur_token = "".join(cur_token)

            if cur_token == token:
                data = line[:-1]
                break

        file.close()

        return self._decompress_token(data)

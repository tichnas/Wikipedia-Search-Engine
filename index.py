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

from constants import WEIGHTAGE
from number_system import NumberSystem
from file_mappings import get_token_id


class Index:
    def __init__(self, benchmark_score=0):
        self._index = {}
        self._compressed_index = {}
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

        prefix_sum = 0

        for doc in self._index[token]:
            # store only the change from last doc id
            doc[0] -= prefix_sum
            prefix_sum += doc[0]

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

    def _decompress_token(self, token):
        if token not in self._compressed_index:
            return []

        self._index[token] = []
        data = self._compressed_index[token].split(" ")

        for i in range(1, len(data), 2):
            doc_id = self._number_system.decode(data[i])
            score = self._number_system.decode(data[i + 1][:-1])
            score_type = self._number_system.decode(data[i + 1][-1])

            existence = []
            for p in range(6):
                existence.append(1 if score_type & (1 << p) else 0)

            self._index[token].append([doc_id, score, existence])

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

    def load(self, file_obj):
        while True:
            line = file_obj.readline()

            if not line:
                break

            token = []
            for i in line:
                if i == " ":
                    break
                token.append(i)
            token = "".join(token)

            self._compressed_index[token] = line[:-1]

    def load_merge_write(self, file_path):
        # Doesn't change/use current state
        # Sorts by token

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
                if i == " ":
                    break
                pos += 1
                token.append(i)
            token = "".join(token)

            if token not in index:
                index[token] = [token]

            index[token].append(line[pos:-1])

        output = []

        for token in sorted(index.keys()):
            output.append("".join(index[token]))
            output.append("\n")

        file_obj.truncate(0)
        file_obj.seek(0)
        file_obj.write("".join(output))

        file_obj.close()

    def search(self, token):
        if token not in self._compressed_index:
            return []

        if token not in self._index:
            self._decompress_token(token)

        return self._index[token]

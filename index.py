##################################
##
##   NOTE: Assumes filling in order of page, i.e., all tokens of page 1 are added before tokens of page 2
##
##   Index Format:
##
##   token -> [
##      [page num, score, [inTitle, inBody, inInfobox, inCategory, inLink, inReference]],
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


class Index:
    def __init__(self, benchmark_score):
        self._index = {}
        self._token_score = {}
        self._benchmark_score = benchmark_score
        self._number_system = NumberSystem()

    def reset(self):
        self._index = []
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

    def get_compressed(self, tokens_indexed):
        output = []

        for token in self._index:
            if self._token_score[token] > self._benchmark_score:
                tokens_indexed.add(token)
                self._compress_token(token, output)

        return "".join(output)

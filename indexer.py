import xml.sax
import re
from nltk.stem import PorterStemmer
import pickle

from constants import DATA_FILE, PAGES_IN_FILE
from stop_words import stop_words

##################################
##   Index Format 1
##
##   token -> [
##       [
##           page num,
##           freq of token in Title,
##           freq of token in Body,
##           freq of token in Infobox,
##           freq of token in Category,
##       ],
##       ...
##   ]
##
##
##   Index Format 2
##
##   token -> [
##       [
##           page num,
##          {
##              't': freq of token in Title,
##              'b': freq of token in Body,
##              'i': freq of token in Infobox,
##              'c': freq of token in Category,
##          }
##       ],
##       ...
##   ]
##
##################################

index = {}
page_num = 0
pages_done = 0
dump_num = 0
title = ""
text = ""

stemmer = PorterStemmer()
stemmed_token = {}


class XMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.data = ""

    def startElement(self, name, attrs):
        global page_num

        self.data = ""

        if name == "page":
            if pages_done == PAGES_IN_FILE:
                dump()

            page_num += 1

    def endElement(self, name):
        global page_num, pages_done, title, text

        if name == "mediawiki":
            dump()
        elif name == "page":
            pages_done += 1
            index_page_1()
        elif name == "title":
            title = self.data
        elif name == "text":
            text = self.data

    def characters(self, content):
        self.data += content


def stem(token):
    if token not in stemmed_token:
        stemmed_token[token] = stemmer.stem(token)

    return stemmed_token[token]


def tokenize(data):
    to_keep = {"Infobox", "}}", "[[Category:", "]]"}
    escaped_to_keep = ["Infobox", "\}\}", "\[\[Category:", "\]\]"]

    left = re.split("(" + ")|(".join(escaped_to_keep) + ")", data)
    ans = []

    for token in left:
        if not token:
            continue
        if token in to_keep:
            ans.append(token)
        else:
            ans.extend(re.split("[^a-zA-Z0-9]+", token))

    return ans


def index_page_1():
    index_tokens_1(1, tokenize(title))

    text_tokens = tokenize(text)

    body_tokens = []
    infobox_tokens = []
    category_tokens = []

    is_special = False  # Anything True will result in special as True
    is_infobox = False
    is_category = False

    for token in text_tokens:
        if token == "Infobox" and not is_special:
            is_infobox = True
            is_special = True
        elif token == "[[Category:" and not is_special:
            is_category = True
            is_special = True
        elif token == "}}" and is_infobox:
            is_infobox = False
            is_special = False
        elif token == "]]" and is_category:
            is_category = False
            is_special = False
        elif token.isalnum():
            if is_infobox:
                infobox_tokens.append(token)
            elif is_category:
                category_tokens.append(token)
            else:
                body_tokens.append(token)

    index_tokens_1(2, body_tokens)
    index_tokens_1(3, infobox_tokens)
    index_tokens_1(4, category_tokens)


def index_page_2():
    index_tokens_2("t", tokenize(title))

    text_tokens = tokenize(text)

    body_tokens = []
    infobox_tokens = []
    category_tokens = []

    is_special = False  # Anything True will result in special as True
    is_infobox = False
    is_category = False

    for token in text_tokens:
        if token == "Infobox" and not is_special:
            is_infobox = True
            is_special = True
        elif token == "[[Category:" and not is_special:
            is_category = True
            is_special = True
        elif token == "}}" and is_infobox:
            is_infobox = False
            is_special = False
        elif token == "]]" and is_category:
            is_category = False
            is_special = False
        elif token.isalnum():
            if is_infobox:
                infobox_tokens.append(token)
            elif is_category:
                category_tokens.append(token)
            else:
                body_tokens.append(token)

    index_tokens_2("b", body_tokens)
    index_tokens_2("i", infobox_tokens)
    index_tokens_2("c", category_tokens)


def index_tokens_1(type, tokens):
    for token in tokens:
        if not token or len(token) <= 1 or token.lower() in stop_words:
            continue

        token = stem(token)

        if token not in index:
            index[token] = []

        if not index[token] or index[token][-1][0] != page_num:
            index[token].append([page_num, 0, 0, 0, 0])

        index[token][-1][type] += 1


def index_tokens_2(type, tokens):
    for token in tokens:
        if not token or len(token) <= 1 or token.lower() in stop_words:
            continue

        token = stem(token)

        if token not in index:
            index[token] = []

        if not index[token] or index[token][-1][0] != page_num:
            index[token].append([page_num, dict()])

        if type not in index[token][-1][1]:
            index[token][-1][1][type] = 1
        else:
            index[token][-1][1][type] += 1


def dump():
    global index, pages_done, dump_num

    print()
    print(dump_num)
    print()
    for token in index:
        print(token, ": ", index[token])
    print()

    pickle.dump(index, open("index" + str(dump_num), "wb"))

    index = {}
    pages_done = 0
    dump_num += 1


parser = xml.sax.make_parser()
parser.setContentHandler(XMLHandler())

data_file = open(DATA_FILE, "r")

while True:
    line = data_file.readline()

    if not line:
        break

    parser.feed(line)

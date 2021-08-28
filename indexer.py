import xml.sax
import re
from nltk.stem import PorterStemmer
import pickle

from constants import DATA_FILE, PAGES_IN_FILE, WEIGHTAGE
from stop_words import stop_words
from stemmed_stop_words import stemmed_stop_words

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
##
##   Index Format 3
##
##   token -> [ [page num, score] , ... ]
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
            index_page_3()
        elif name == "title":
            title = self.data
        elif name == "text":
            text = clean(self.data)

    def characters(self, content):
        self.data += content


def stem(token):
    if token not in stemmed_token:
        stemmed_token[token] = stemmer.stem(token)

    return stemmed_token[token]


def tokenize(data):
    data = data.lower()

    to_keep = {
        "infobox",
        "info-end}}",
        "[[category:",
        "]]",
        "==external links==",
        "==references==",
        "==link or reference end==",
    }
    escaped_to_keep = [
        "infobox",
        "info-end\}\}",
        "\[\[category:",
        "\]\]",
        "==external links==",
        "==references==",
        "==link or reference end==",
    ]

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


def clean(data):
    data = data.lower()

    # remove URLs
    data = re.sub("https?:\/\/[^ \|\}<\n]*", " ", data)

    data = re.sub("<redirect", " ", data)

    data = re.sub("name=", " ", data)

    data = re.sub("ref=", " ", data)
    data = re.sub("\/ref", " ", data)
    data = re.sub("referee=", " ", data)

    data = re.sub("colspan=[^ ]*", " ", data)
    data = re.sub("rowspan=[^ ]*", " ", data)

    data = re.sub("\{\{reflist\}\}", " ", data)

    data = re.sub("\{\{in lang.*\}\}", " ", data)

    data = re.sub("url=", " ", data)

    data = re.sub("short description", " ", data)

    data = re.sub("\{\{cite", " ", data)

    data = re.sub("date=", " ", data)

    data = re.sub("see also", " ", data)

    data = re.sub(".jpg", " ", data)
    data = re.sub(".png", " ", data)

    data = re.sub("\{\{defaultsort:", " ", data)

    # remove everything like &lt; something &gt;
    data = re.sub("&lt; *[^ ]* *&gt;", " ", data)

    # remove css
    data = re.sub("style=&quot;.*&quot;", " ", data)

    # remove everything like |something=
    data = re.sub("\|.{0,50}=", " ", data)

    data = re.sub("nbsp;", " ", data)
    data = re.sub("&amp;", " ", data)
    data = re.sub("&lt;", " ", data)
    data = re.sub("&gt;", " ", data)

    data = re.sub("[0-9]*px", " ", data)

    data = re.sub("wikipedia:", " ", data)

    return data


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


def index_page_3():
    index_tokens_3(0, tokenize(title), False)

    text_tokens = tokenize(text)

    body_tokens = []
    infobox_tokens = []
    category_tokens = []
    reference_tokens = []
    link_tokens = []

    is_special = False  # Anything True will result in special as True
    is_infobox = False
    is_category = False
    is_link = False
    is_reference = False

    for token in text_tokens:
        if token == "infobox" and not is_special:
            is_infobox = True
        elif token == "[[category:" and not is_special:
            is_category = True
        elif token == "==external links==" and not is_special:
            is_link = True
        elif token == "==references==" and not is_special:
            is_reference = True
        elif token == "info-end}}" and is_infobox:
            is_infobox = False
        elif token == "]]" and is_category:
            is_category = False
        elif token == "==link or reference end==" and is_link:
            is_link = False
        elif token == "==link or reference end==" and is_reference:
            is_reference = False
        elif token.isalnum():
            if is_infobox:
                infobox_tokens.append(token)
            elif is_category:
                category_tokens.append(token)
            elif is_link:
                link_tokens.append(token)
            elif is_reference:
                reference_tokens.append(token)
            else:
                body_tokens.append(token)

        is_special = is_infobox or is_category or is_link or is_reference

    index_tokens_3(1, body_tokens)
    index_tokens_3(2, infobox_tokens)
    index_tokens_3(3, category_tokens)
    index_tokens_3(4, link_tokens)
    index_tokens_3(5, reference_tokens)


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


def index_tokens_3(type, tokens, check_stop_words=True):
    for token in tokens:
        if not token or len(token) <= 1:
            continue

        if token.isnumeric() and len(token) > 4:
            continue

        if check_stop_words and token in stop_words:
            continue

        token = stem(token)

        if check_stop_words and token in stemmed_stop_words:
            continue

        if token not in index:
            index[token] = []

        if not index[token] or index[token][-1][0] != page_num:
            index[token].append([page_num, 0])

        index[token][-1][1] += WEIGHTAGE[type]


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

    if len(line) == 1:
        line = "==link or reference end==" + line

    if line == "}}\n":
        line = "info-end}}\n"

    parser.feed(line)

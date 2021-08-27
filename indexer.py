import xml.sax
import re

from constants import DATA_FILE, PAGES_IN_FILE

##################################
##   Index Format
##
##   token -> [
##       [
##           page num,
##           freq of token in title,
##           freq of token in text
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
            index_page()
        elif name == "title":
            title = self.data
        elif name == "text":
            text = self.data

    def characters(self, content):
        self.data += content


def tokenize(data):
    return re.split(r"[^a-zA-Z0-9]+", data)


def index_page():
    types = [title, text]
    for i in range(0, len(types)):
        index_tokens(i + 1, tokenize(types[i]))


def index_tokens(type, tokens):
    for token in tokens:
        if not token:
            continue

        if token not in index:
            index[token] = []

        if not index[token] or index[token][-1][0] != page_num:
            index[token].append([page_num, 0, 0])

        index[token][-1][type] += 1


def dump():
    global index, pages_done, dump_num

    # TODO: write in file
    print()
    print(dump_num)
    print()
    for token in index:
        print(token, ": ", index[token])
    print()

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

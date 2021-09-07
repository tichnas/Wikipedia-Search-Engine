import xml.sax
import sys, os, time, resource

from constants import PAGES_IN_FILE, WEIGHTAGE, ALLOW_PAUSE, PAUSE_FILE
from stop_words import stop_words
from stemmed_stop_words import stemmed_stop_words
from stemmer import Stemmer
from index import Index
from helper import tokenize, clean


DATA_FILE = "data_example"
INDEX_FOLDER = "index_data"

page_num = 0
pages_done = 0
title = ""
text = ""
index_files = {}

benchmark_score = 0
for i in WEIGHTAGE:
    benchmark_score += i

index = Index(benchmark_score / 5)
stemmer = Stemmer()


class XMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.data = []

    def startElement(self, name, attrs):
        global page_num

        self.data = []

        if name == "page":
            if pages_done == PAGES_IN_FILE:
                dump()

            page_num += 1

            if ALLOW_PAUSE and page_num % 2000 == 0:
                check_pause()

            # if page_num % 2000 == 0:
            #     print(page_num)

    def endElement(self, name):
        global page_num, pages_done, title, text

        if name == "mediawiki":
            dump()
        elif name == "page":
            pages_done += 1
            index_page()
        elif name == "title":
            title = "".join(self.data)
        elif name == "text":
            text = clean("".join(self.data))

    def characters(self, content):
        self.data.append(content)


def index_page():
    index_tokens(0, tokenize(title), False)

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
    is_ref = False

    for token in text_tokens:
        if token == "<ref" or token == "&lt;ref":
            is_ref = True
        elif token == "/ref>" or token == "/ref&gt;":
            is_ref = False
        elif token == "{{infobox" and not is_special:
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
            if is_reference or is_ref:
                reference_tokens.append(token)
            elif is_infobox:
                infobox_tokens.append(token)
            elif is_category:
                category_tokens.append(token)
            elif is_link:
                link_tokens.append(token)
            else:
                body_tokens.append(token)

        is_special = is_infobox or is_category or is_link or is_reference

    index_tokens(1, body_tokens)
    index_tokens(2, infobox_tokens)
    index_tokens(3, category_tokens)
    index_tokens(4, link_tokens)
    index_tokens(5, reference_tokens)


def index_tokens(type, tokens, check_stop_words=True):
    for token in tokens:
        if not token or len(token) <= 1:
            continue

        if token.isnumeric() and len(token) > 4:
            continue

        if check_stop_words and token in stop_words:
            continue

        if check_stop_words and len(token) <= 2:
            continue

        token = stemmer.stem(token)

        if len(token) <= 1:
            continue

        if check_stop_words and token in stemmed_stop_words:
            continue

        index.add(token, page_num, type)


def dump():
    global index, pages_done

    data = index.get_compressed()

    for id in data:
        index_files[id].write(data[id])

    index.reset()

    pages_done = 0


def create_index_files():
    letters = [chr(i) for i in range(ord("a"), ord("z") + 1)]

    for i in letters:
        for j in letters:
            path = os.path.join(INDEX_FOLDER, "index_" + (i + j))
            file = open(path, "w+")
            index_files[i + j] = file

    path = os.path.join(INDEX_FOLDER, "index_.other")
    file = open(path, "w+")
    index_files["other"] = file


def merge_tokens_index():
    for id in index_files:
        index.load_merge_write(index_files[id])


def parse():
    parser = xml.sax.make_parser()
    parser.setContentHandler(XMLHandler())

    data_file = open(DATA_FILE, "r")

    while True:
        line = data_file.readline()

        if not line:
            break

        if len(line) == 1:
            line = "==link or reference end==" + line

        if line[0:2] == "}}" or line[0:3] == "|}}":
            line = "info-end}} " + line

        parser.feed(line)


def setup_pause():
    global pause_file
    pause_file = open(PAUSE_FILE, "w+")
    pause_file.write("0")


def check_pause():
    while True:
        pause_file.seek(0)
        pause = int(pause_file.readline())

        if pause:
            print('Sleeping...')
            time.sleep(60)
        else:
            break


start_time = time.time()

if ALLOW_PAUSE:
    setup_pause()

create_index_files()

parse()

merge_tokens_index()

end_time = time.time()

print("Time taken:", str(end_time - start_time)[0:5], "seconds")
print(
    "Peak RAM Usage:", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1000, "MB"
)

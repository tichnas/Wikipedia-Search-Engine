import xml.sax
import sys, os, time, resource

from constants import (
    PAGES_IN_RAM,
    PAGES_IN_TITLE_FILE,
    PAGES_IN_TOKEN_COUNT_FILE,
    WEIGHTAGE,
    ALLOW_PAUSE,
    PAUSE_FILE,
    MAX_FILE_DESCRIPTORS,
    INDEX_FILE_SIZE,
)
from stop_words import stop_words
from stemmed_stop_words import stemmed_stop_words
from stemmer import Stemmer
from index import Index
from helper import tokenize, clean
from file_mappings import (
    get_token_intermediate_index_file,
    get_doc_title_file,
    get_doc_terms_count_file,
    is_token_intermediate_index_file,
    get_token_index_file,
)
from number_system import NumberSystem


DATA_FILE = "data_example"
INDEX_FOLDER = "index_data"

page_num = 0
title = ""
text = ""
page_titles = []
page_token_count = []

benchmark_score = 0
for i in WEIGHTAGE:
    benchmark_score += i

index = Index(benchmark_score / 5)
stemmer = Stemmer()
number_system = NumberSystem()

titles_to_skip = ["Wikipedia:", "File:", "Category:", "Template:", "Portal:"]


class XMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.data = []

    def startElement(self, name, attrs):
        global page_num

        self.data = []

        if name == "page":
            if page_num:
                if page_num % PAGES_IN_RAM == 0:
                    dump()
                if page_num % PAGES_IN_TITLE_FILE == 0:
                    dump_titles()
                if page_num % PAGES_IN_TOKEN_COUNT_FILE == 0:
                    dump_token_counts()

            page_num += 1

            if ALLOW_PAUSE and page_num % 2000 == 0:
                check_pause()

            # if page_num % 2000 == 0:
            #     print(page_num)

    def endElement(self, name):
        global page_num, title, text

        if name == "mediawiki":
            if page_num % PAGES_IN_RAM:
                dump()
            if page_num % PAGES_IN_TITLE_FILE:
                dump_titles()
            if page_num % PAGES_IN_TOKEN_COUNT_FILE:
                dump_token_counts()
        elif name == "page":
            index_page()
        elif name == "title":
            title = "".join(self.data)
            page_titles.append(title)
        elif name == "text":
            text = clean("".join(self.data))

    def characters(self, content):
        self.data.append(content)


def index_page():
    page_token_count.append(0)

    for t in titles_to_skip:
        if title.startswith(t):
            return

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

        page_token_count[-1] += WEIGHTAGE[type]
        index.add(token, page_num, type)


get_file_path = lambda filename: os.path.join(INDEX_FOLDER, filename)


def dump():
    global index

    index_files = {}
    data = index.get_compressed()

    for id in data:
        if id not in index_files:
            if len(index_files) == MAX_FILE_DESCRIPTORS:
                for file in index_files.values():
                    file.close()
                index_files = {}

            file_path = get_file_path(get_token_intermediate_index_file(id))
            index_files[id] = open(file_path, "a")

        index_files[id].write(data[id])

    index.reset()
    for file in index_files.values():
        file.close()


def dump_titles():
    global page_num, page_titles

    page_titles.append("")
    title_string = "\n".join(page_titles)
    page_titles = []

    title_file = open(get_file_path(get_doc_title_file(page_num)), "w")

    title_file.write(title_string)


def dump_token_counts():
    global page_num, page_token_count

    token_count = [number_system.encode(count) for count in page_token_count]
    token_count.append("")
    token_count_string = "\n".join(token_count)
    page_token_count = []

    token_count_file = open(get_file_path(get_doc_terms_count_file(page_num)), "w")

    token_count_file.write(token_count_string)


def merge_tokens_index():
    for filename in os.listdir(INDEX_FOLDER):
        if is_token_intermediate_index_file(filename):
            index.load_merge_write(get_file_path(filename))


def break_index_files():
    size_done = 0
    write_file = None

    for filename in sorted(os.listdir(INDEX_FOLDER)):
        if not is_token_intermediate_index_file(filename):
            continue

        file = open(get_file_path(filename), "r")

        while True:
            line = file.readline()

            if not line:
                break

            if not write_file or size_done + len(line) > INDEX_FILE_SIZE * 1024 * 1024:
                token = []
                for i in line:
                    if i == " ":
                        break
                    token.append(i)
                token = "".join(token)

                if write_file:
                    write_file.close()

                write_file = open(get_file_path(get_token_index_file(token)), "w")
                size_done = 0

            write_file.write(line)
            size_done += len(line)

        file.close()
        os.remove(get_file_path(filename))


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
            print("Sleeping...")
            time.sleep(60)
        else:
            break


def empty_index_dir():
    for file in os.listdir(INDEX_FOLDER):
        file_path = get_file_path(file)
        os.remove(file_path)


start_time = time.time()

if ALLOW_PAUSE:
    setup_pause()

empty_index_dir()

parse()

merge_tokens_index()
break_index_files()

end_time = time.time()

print("Time taken:", str(end_time - start_time)[0:5], "seconds")
print(
    "Peak RAM Usage:", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1000, "MB"
)

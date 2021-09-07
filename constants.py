PAGES_IN_RAM = 50000
PAGES_IN_META_FILE = int(2e5)  # meta = title, total tokens
WEIGHTAGE = [10, 1, 1, 5, 1, 1]  # [title, body, infobox, category, link, reference]
ALLOW_PAUSE = True
PAUSE_FILE = "is_paused"
MAX_FILE_DESCRIPTORS = 1000
INDEX_FILE_SIZE = 5  # in MB

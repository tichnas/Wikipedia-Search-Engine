from constants import PAGES_IN_META_FILE


get_token_id = lambda token: token[:2]

get_token_index_file = lambda token: "index_" + token

is_token_index_file = lambda filename: filename.startswith("index_")

get_token_intermediate_index_file = lambda token_id: "int_index_" + token_id

is_token_intermediate_index_file = lambda filename: filename.startswith("int_index_")

get_doc_terms_count_file = lambda last_page_num: "count_" + str(
    (last_page_num - 1) // PAGES_IN_META_FILE
)

get_doc_title_file = lambda last_page_num: "title_" + str(
    (last_page_num - 1) // PAGES_IN_META_FILE
)

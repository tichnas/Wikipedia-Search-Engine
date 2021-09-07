double_gap_4 = {"b", "g", "h", "j", "k", "o", "v", "w"}
single = {"q", "x", "y", "z"}
double_gap_3 = {"t"}
double_gap_14 = {"u"}


def get_token_id(token):
    if not token[:2].isalpha():
        return ".other"

    id = [token[0]]

    if token[0] in double_gap_4:
        id.append(str((ord(token[1]) - ord("a")) // 4))
    elif token[0] in single:
        pass
    elif token[0] in double_gap_3:
        id.append(str((ord(token[1]) - ord("a")) // 3))
    elif token[0] in double_gap_14:
        id.append(str((ord(token[1]) - ord("a")) // 14))
    else:
        if len(token) < 3 or not token[2].isalpha():
            id = [".small"]
        else:
            id.append(token[1])
            id.append(str((ord(token[2]) - ord("a")) // 13))

    return "".join(id)


get_token_index_file = lambda token_id: "index_" + token_id

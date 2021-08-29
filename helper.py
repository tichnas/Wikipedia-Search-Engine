import re
import unicodedata


def strip_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def tokenize(data):
    data = data.lower()
    data = strip_accents(data)

    to_keep = {
        "infobox",
        "info-end}}",
        "[[category:",
        "]]",
        "==external links==",
        "==references==",
        "==link or reference end==",
        "<ref",
        "</ref>",
    }
    escaped_to_keep = [
        "infobox",
        "info-end\}\}",
        "\[\[category:",
        "\]\]",
        "==external links==",
        "==references==",
        "==link or reference end==",
        "<ref",
        "<\/ref>",
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
    data = re.sub("referee=", " ", data)

    data = re.sub("colspan=[^ ]*", " ", data)
    data = re.sub("rowspan=[^ ]*", " ", data)

    data = re.sub("\{\{reflist\}\}", " ", data)

    data = re.sub("\{\{in lang.*\}\}", " ", data)
    data = re.sub("language=.*\}\}", " ", data)

    data = re.sub("url=", " ", data)

    data = re.sub("short description", " ", data)

    data = re.sub("\{\{cite[^\|]*", " ", data)

    data = re.sub("date=", " ", data)

    data = re.sub("see also", " ", data)

    data = re.sub(".jpg", " ", data)
    data = re.sub(".png", " ", data)
    data = re.sub(".svg", " ", data)

    data = re.sub("\{\{defaultsort:", " ", data)

    # remove css
    data = re.sub('style=".*"', " ", data)

    # remove everything like |something=
    data = re.sub("\|.{0,50}=", " ", data)

    data = re.sub("[0-9]*px", " ", data)

    data = re.sub("wikipedia:", " ", data)

    return data

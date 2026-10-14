def _normalize_with_map(text):
    out, idx = [], []
    prev_space = False
    for i, ch in enumerate(text):
        if ch.isspace():
            if not prev_space:
                out.append(" ")
                idx.append(i)
            prev_space = True
        else:
            for c in ch.lower():
                out.append(c)
                idx.append(i)
            prev_space = False
    return "".join(out), idx


def find_citation(cited, text, offset=0):
    needle = " ".join(cited.split()).lower()
    if not needle:
        return None
    norm, idx = _normalize_with_map(text)
    pos = norm.find(needle)
    if pos == -1:
        return None
    start = idx[pos]
    end = idx[pos + len(needle) - 1] + 1
    return offset + start, offset + end
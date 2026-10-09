import re


def fixed_chunks(text, size=1000, overlap=200):
    chunks = []
    step = size - overlap
    for start in range(0, len(text), step):
        end = min(start + size, len(text))
        chunks.append({"start": start, "end": end, "text": text[start:end]})
        if end == len(text):
            break
    return chunks


def overlaps(chunk, spans):
    return any(chunk["start"] < e and s < chunk["end"] for s, e in spans)


HEADING = re.compile(
    r"^[ \t]*(?:\d+(?:\.\d+)*\.?|ARTICLE|Article|SECTION|Section)[ \t]+[A-Z0-9]",
    re.M,
)


def clause_chunks(text, min_size=200, max_size=2000, overlap=200):
    starts = [m.start() for m in HEADING.finditer(text)]
    if len(starts) < 5:
        starts = [m.end() for m in re.finditer(r"\n[ \t]*\n", text)]

    bounds = sorted(set([0] + starts + [len(text)]))
    segments = list(zip(bounds[:-1], bounds[1:]))

    merged = []
    for s, e in segments:
        if merged and (merged[-1][1] - merged[-1][0]) < min_size:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))

    chunks = []
    for s, e in merged:
        if e - s <= max_size:
            chunks.append({"start": s, "end": e, "text": text[s:e]})
        else:
            for sub in fixed_chunks(text[s:e], max_size, overlap):
                chunks.append({
                    "start": s + sub["start"],
                    "end": s + sub["end"],
                    "text": sub["text"],
                })
    return chunks
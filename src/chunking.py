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
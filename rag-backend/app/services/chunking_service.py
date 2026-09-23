import re


def chunk_text(text: str, strategy: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    if strategy == "fixed_size":
        return _fixed_size_chunks(text, chunk_size, overlap)
    elif strategy == "recursive":
        return _recursive_chunks(text, chunk_size)
    raise ValueError(f"Unknown strategy: '{strategy}'. Use 'fixed_size' or 'recursive'.")


def _fixed_size_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(text):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks


def _recursive_chunks(text: str, chunk_size: int) -> list[str]:
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        if len(paragraph) > chunk_size:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
            chunks.extend(_split_sentences(paragraph, chunk_size))
            continue

        if len(current_chunk) + len(paragraph) + 2 > chunk_size:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"
        else:
            current_chunk += paragraph + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def _split_sentences(text: str, chunk_size: int) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= chunk_size:
            current += sentence + " "
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence + " "

    if current.strip():
        chunks.append(current.strip())

    return chunks

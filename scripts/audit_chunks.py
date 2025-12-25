import json
from pathlib import Path
from collections import defaultdict

CHUNKS_FILE = Path("data/chunks/chunks.json")

# threshold
MIN_CHARS = 200
MAX_CHARS = 2500


def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def has_section_header(text: str) -> bool:
    first_line = text.strip().split("\n")[0]
    return (
        first_line[0].isdigit() and "." in first_line
        or first_line.isupper()
        or first_line.lower().startswith("acknowledgment")
    )


def audit():
    chunks = load_chunks()

    total_chunks = len(chunks)
    lengths = []
    by_doc = defaultdict(list)

    short_chunks = []
    long_chunks = []
    no_header = []

    for chunk in chunks:
        text = chunk["text"]
        length = len(text)
        lengths.append(length)

        doc_id = chunk["doc_id"]
        by_doc[doc_id].append(chunk)

        if length < MIN_CHARS:
            short_chunks.append(chunk)

        if length > MAX_CHARS:
            long_chunks.append(chunk)

        if not has_section_header(text):
            no_header.append(chunk)

    # summary
    print("\n===== CHUNK QUALITY AUDIT =====\n")
    print(f"Total chunks: {total_chunks}")
    print(f"Shortest chunk: {min(lengths)} chars")
    print(f"Longest chunk: {max(lengths)} chars")
    print(f"Average chunk size: {sum(lengths) // total_chunks} chars\n")

    print("Chunks per document:")
    for doc_id, doc_chunks in by_doc.items():
        print(f"  {doc_id}: {len(doc_chunks)}")

    # warnings
    print("\n===== WARNINGS =====")

    print(f"\nChunks below {MIN_CHARS} chars: {len(short_chunks)}")
    for c in short_chunks[:3]:
        print(f"  - {c['chunk_id']} ({len(c['text'])} chars)")

    print(f"\nChunks above {MAX_CHARS} chars: {len(long_chunks)}")
    for c in long_chunks[:3]:
        print(f"  - {c['chunk_id']} ({len(c['text'])} chars)")

    print(f"\nChunks missing section header: {len(no_header)}")
    for c in no_header[:3]:
        print(f"  - {c['chunk_id']}")

    print("\n===== AUDIT COMPLETE =====\n")


if __name__ == "__main__":
    audit()

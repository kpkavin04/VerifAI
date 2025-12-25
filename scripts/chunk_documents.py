import json
import re
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
CHUNKS_DIR = Path("data/chunks")
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = CHUNKS_DIR / "chunks.json"

# Quality threshold
MIN_CHARS = 200


def is_section_header(line: str) -> bool:
    line = line.strip()
    if not line:
        return False

    # looking for numbered sections
    if re.match(r"^\d+\.\s+", line):
        return True

    # capitalised Document titles 
    if line.isupper() and len(line.split()) <= 10:
        return True

    # Acknowledgment sections
    if line.lower().startswith("acknowledgment"):
        return True

    return False


def chunk_document(text: str, doc_id: str, source: str):
    lines = text.split("\n")

    raw_chunks = []
    current_section = None
    buffer = []

    for line in lines:
        if is_section_header(line):
            if current_section:
                raw_chunks.append({
                    "header": current_section,
                    "body": "\n".join(buffer).strip()
                })

            current_section = line.strip()
            buffer = []
        else:
            buffer.append(line)

    if current_section:
        raw_chunks.append({
            "header": current_section,
            "body": "\n".join(buffer).strip()
        })

    # merge small chunks
    merged_chunks = []

    for chunk in raw_chunks:
        text = f"{chunk['header']}\n{chunk['body']}".strip()

        if len(text) < MIN_CHARS and merged_chunks:
            # Merge into previous chunk in the case where the text length is too short
            merged_chunks[-1]["body"] += "\n\n" + chunk["header"] + "\n" + chunk["body"]
        else:
            merged_chunks.append(chunk)

    # finalise chunks
    final_chunks = []
    for idx, chunk in enumerate(merged_chunks):
        final_chunks.append({
            "doc_id": doc_id,
            "chunk_id": f"{doc_id}_{idx}",
            "text": f"{chunk['header']}\n{chunk['body']}".strip(),
            "source": source
        })

    return final_chunks


def main():
    all_chunks = []

    for file_path in sorted(PROCESSED_DIR.glob("*.txt")):
        doc_id = file_path.stem
        source = file_path.name

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        document_chunks = chunk_document(
            text=text,
            doc_id=doc_id,
            source=source
        )

        all_chunks.extend(document_chunks)
        print(f"Chunked {file_path.name}: {len(document_chunks)} chunks")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(all_chunks)} chunks into {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

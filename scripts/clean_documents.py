import os
import re
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def is_section_header(line: str) -> bool:
    line = line.strip()

    if not line:
        return False

    # Numbered sections: "1. Introduction"
    if re.match(r"^\d+\.\s+[A-Z]", line):
        return True

    # ALL CAPS headers
    if line.isupper() and len(line.split()) <= 10:
        return True

    return False


def is_list_item(line: str) -> bool:
    return bool(
        re.match(r"^(\-|\•|\*|\w+:\s)", line.strip())
    )


def normalize_whitespace(text: str) -> str:
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing spaces
    text = "\n".join(line.rstrip() for line in text.splitlines())

    # Collapse excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def merge_broken_lines(text: str) -> str:
    lines = text.split("\n")
    cleaned_lines = []

    buffer = ""

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if buffer:
                cleaned_lines.append(buffer.strip())
                buffer = ""
            cleaned_lines.append("")
            continue

        if is_section_header(stripped) or is_list_item(stripped):
            if buffer:
                cleaned_lines.append(buffer.strip())
                buffer = ""
            cleaned_lines.append(stripped)
        else:
            if buffer:
                buffer += " " + stripped
            else:
                buffer = stripped

    if buffer:
        cleaned_lines.append(buffer.strip())

    return "\n".join(cleaned_lines)


def clean_document(text: str) -> str:
    text = normalize_whitespace(text)
    text = merge_broken_lines(text)
    text = normalize_whitespace(text)
    return text


def process_file(input_path: Path, output_path: Path):
    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned_text = clean_document(raw_text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)


def main():
    for file in RAW_DIR.glob("*.txt"):
        output_file = PROCESSED_DIR / file.name
        process_file(file, output_file)
        print(f"Cleaned: {file.name}")


if __name__ == "__main__":
    main()
import re
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text, write_text

INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "input", "raw_contracts.txt")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "clauses.txt")

CLAUSE_SPLITTERS = re.compile(
    r"\s*,\s*(?=[Nn]ếu|[Vv]à|[Hh]oặc|[Nn]hưng|[Dd]o đó|[Vv]ì vậy|[Tt]rong trường hợp|[Mm]ặc dù|[Tt]uy nhiên))\s*",
)

def segment_clauses(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.;])\s+|\n+", text.strip())

    clauses = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        parts = CLAUSE_SPLITTERS.split(sentence)
        for part in parts:
            part = part.strip()
            if part:
                part = part[0].upper() + part[1:]
                if not part.endswith(('.', ';')):
                    part += '.'
                clauses.append(part)

    return clauses

def main():
    raw_text = read_text(INPUT_PATH)
    clauses = segment_clauses(raw_text)
    
    output = "\n".join(clauses)
    
    write_text(OUTPUT_PATH, output)
    print(f"[segmenter] {len(clauses)} clauses written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
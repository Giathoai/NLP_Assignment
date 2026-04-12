import re
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text, write_text
from underthesea import sent_tokenize

INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "input", "raw_contracts.txt")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "clauses.txt")

# Vietnamese subordinating connectors (ordered longest-first)
SUBORDINATORS = [
    'nếu như', 'trừ khi', 'miễn là',
    'trong khi', 'khi mà', 'ngay khi',
    'mặc dù', 'bởi vì',
    'sau khi', 'trước khi', 'sao cho',
    'nếu', 'khi', 'dù', 'vì', 'để', 'nhằm',
]

# Vietnamese coordinating conjunctions
COORDINATORS = ['và', 'hoặc', 'hay', 'nhưng', 'song']

# Build regex alternation (longest first for proper matching)
_sub_alt = '|'.join(re.escape(s) for s in SUBORDINATORS)
_coord_alt = '|'.join(re.escape(c) for c in COORDINATORS)


def split_clauses(sentence: str) -> list:
    sentence = sentence.strip()
    if not sentence:
        return []

    # Remember ending punctuation
    has_ending = sentence[-1] in '.!?'
    if has_ending:
        sentence = sentence[:-1].strip()

    DELIM = '\x00'
    text = sentence

    text = re.sub(
        rf'[,;]\s*(?:{_coord_alt})\s+({_sub_alt})\b',
        DELIM + r'\1', text, flags=re.IGNORECASE,
    )

    text = re.sub(
        rf'[,;]\s*({_sub_alt})\b',
        DELIM + r'\1', text, flags=re.IGNORECASE,
    )

    text = re.sub(
        rf'[,;]\s*(?:{_coord_alt})\s+(Bên\s+[A-ZĐa-zđ])',
        DELIM + r'\1', text,
    )

    text = re.sub(
        r'[,;]\s*(Bên\s+[A-ZĐ])',
        DELIM + r'\1', text,
    )

    text = re.sub(r':\s+', DELIM, text)

    parts = text.split(DELIM)
    clauses = []
    for part in parts:
        part = part.strip().rstrip(',;').strip()
        if not part:
            continue
        # Capitalize first character
        part = part[0].upper() + part[1:]
        # Ensure sentence-ending punctuation
        if part[-1] not in '.!?':
            part += '.'
        clauses.append(part)

    return clauses if clauses else [sentence + '.']


def segment_clauses(contract_text: str) -> list:
    """Full pipeline: sentence segmentation -> clause splitting."""
    sentences = sent_tokenize(contract_text)
    all_clauses = []
    for sent in sentences:
        all_clauses.extend(split_clauses(sent))
    return all_clauses


def main():
    raw_text = read_text(INPUT_PATH)
    clauses = segment_clauses(raw_text)

    output = "\n".join(clauses)
    write_text(OUTPUT_PATH, output)

    print(f"[segmenter] Input:  {INPUT_PATH}")
    print(f"[segmenter] Output: {OUTPUT_PATH}")
    print(f"[segmenter] Clauses extracted: {len(clauses)}")
    for i, c in enumerate(clauses, 1):
        print(f"  {i}. {c}")


if __name__ == "__main__":
    main()
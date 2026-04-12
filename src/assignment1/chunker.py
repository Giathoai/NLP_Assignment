import sys
import os
import re
from underthesea import chunk as ud_chunk
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text, write_text

INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "clauses.txt")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "chunks.txt")


def _should_merge(prev_pos: str, curr_pos: str, curr_word: str) -> bool:
    n_syl = len(curr_word.split())

    # Rule 1 – proper noun continuation
    if curr_pos == 'Np' and n_syl <= 1:
        return True
    # Rule 2 – noun after determiner / classifier
    if curr_pos in ('N', 'Nu', 'Ny') and prev_pos == 'L':
        return True
    # Rule 3 – noun after numeral
    if curr_pos in ('N', 'Nu') and prev_pos == 'M':
        return True
    # Rule 4 – numeral after noun
    if curr_pos == 'M' and prev_pos in ('N', 'Nu', 'Ny'):
        return True
    # Rule 5 – single-syllable nouns merge
    if n_syl <= 1 and curr_pos in ('N', 'Nu', 'Ny') and prev_pos in ('N', 'Np', 'Nu', 'Ny'):
        return True

    return False


def chunk_clause_iob(clause: str) -> list:
    chunk_results = ud_chunk(clause)

    output = []
    prev_compound_pos = None   # POS of the last compound word
    prev_was_np = False

    for word, pos, chunk_tag in chunk_results:
        syllables = word.split()          # compound words use spaces
        is_np = chunk_tag in ('B-NP', 'I-NP')

        if is_np:
            merge = (chunk_tag == 'B-NP'
                     and prev_was_np
                     and _should_merge(prev_compound_pos, pos, word))

            for idx, syl in enumerate(syllables):
                if chunk_tag == 'B-NP' and idx == 0:
                    output.append((syl, 'I-NP' if merge else 'B-NP'))
                else:
                    output.append((syl, 'I-NP'))

            prev_compound_pos = pos
            prev_was_np = True
        else:
            for syl in syllables:
                output.append((syl, 'O'))
            prev_compound_pos = pos
            prev_was_np = False

    return output


def chunk_clauses(text: str) -> str:
    clauses = [
        line.strip()
        for line in text.strip().splitlines()
        if line.strip()
    ]

    lines = []
    for clause in clauses:
        iob_tags = chunk_clause_iob(clause)
        for token, tag in iob_tags:
            lines.append(f'{token}\t{tag}')
        lines.append('')   # blank line between clauses

    return '\n'.join(lines)


def main():
    raw_text = read_text(INPUT_PATH)
    result = chunk_clauses(raw_text)
    write_text(OUTPUT_PATH, result)

    print(f'[chunker] Input:  {INPUT_PATH}')
    print(f'[chunker] Output: {OUTPUT_PATH}')

    clauses = [
        line.strip()
        for line in raw_text.strip().splitlines()
        if line.strip()
    ]
    print(f'[chunker] Clauses processed: {len(clauses)}')

    for idx, clause in enumerate(clauses, 1):
        iob_tags = chunk_clause_iob(clause)
        print(f'\n--- Clause {idx}: {clause}')
        for token, tag in iob_tags:
            print(f'  {token:<15} {tag}')


if __name__ == '__main__':
    main()
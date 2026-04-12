import json
import sys
import os
from underthesea import dependency_parse as ud_dep_parse
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text, write_json
from underthesea import pos_tag
_USE_NEURAL = True

INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "clauses.txt")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "dependency.json")

def _parse_neural(clause: str) -> list:
    """Use underthesea's pre-trained model."""
    raw = ud_dep_parse(clause)
    deps = []
    for item in raw:
        deps.append({
            'index': item[0],
            'token': item[1],
            'pos': item[2] if len(item) > 2 else '',
            'head': item[3] if len(item) > 3 else 0,
            'deprel': item[4] if len(item) > 4 else 'dep',
        })
    return deps


# Tokens that act as auxiliaries rather than main predicates
_AUXILIARIES = {
    'sẽ', 'đã', 'đang', 'sắp',
    'được', 'bị', 'phải',
    'có thể', 'cần', 'nên', 'còn',
}


def _find_nearest(tags, start, direction, target_pos):
    """Find nearest token with a POS in *target_pos* in a given direction."""
    step = 1 if direction == 'right' else -1
    i = start + step
    while 0 <= i < len(tags):
        if tags[i][1] in target_pos:
            return i
        i += step
    return None


def _parse_heuristic(clause: str) -> list:
    """POS-based dependency heuristic (simplified but reasonable)."""
    tags = pos_tag(clause)
    n = len(tags)

    root_idx = None
    for i, (word, pos) in enumerate(tags):
        if pos in ('V', 'Va', 'Vb') and word.lower() not in _AUXILIARIES:
            root_idx = i
            break
    if root_idx is None:
        # Fall back to first verb, including auxiliaries
        for i, (word, pos) in enumerate(tags):
            if pos in ('V', 'Va', 'Vb'):
                root_idx = i
                break
    if root_idx is None:
        root_idx = 0  # last resort

    NOUN_POS = {'N', 'Np', 'Nu', 'Ny'}
    deps = []
    for i, (word, pos) in enumerate(tags):
        if i == root_idx:
            deps.append(_entry(i, word, pos, head=0, deprel='root'))
            continue

        head = root_idx + 1  # default head = root

        if word.lower() in _AUXILIARIES and pos in ('V', 'R'):
            deprel = 'aux'
        elif pos in NOUN_POS:
            deprel = 'nsubj' if i < root_idx else 'obj'
        elif pos == 'A':  # adjective -> modifier of nearest noun
            nn = _find_nearest(tags, i, 'left', NOUN_POS)
            head = (nn + 1) if nn is not None else root_idx + 1
            deprel = 'amod'
        elif pos == 'R' and word.lower() not in _AUXILIARIES:
            deprel = 'advmod'
        elif pos == 'E':  # preposition / case marker
            nn = _find_nearest(tags, i, 'right', NOUN_POS)
            head = (nn + 1) if nn is not None else root_idx + 1
            deprel = 'case'
        elif pos == 'M':  # numeral
            nn = _find_nearest(tags, i, 'right', NOUN_POS) or \
                 _find_nearest(tags, i, 'left', NOUN_POS)
            head = (nn + 1) if nn is not None else root_idx + 1
            deprel = 'nummod'
        elif pos == 'L':  # determiner / classifier
            nn = _find_nearest(tags, i, 'right', NOUN_POS)
            head = (nn + 1) if nn is not None else root_idx + 1
            deprel = 'det'
        elif pos in ('C', 'CC'):
            deprel = 'cc'
        elif pos == 'CH':
            deprel = 'punct'
        elif pos in ('V', 'Va', 'Vb'):
            # Secondary verb (e.g. serial verb, complement)
            deprel = 'xcomp' if i > root_idx else 'advcl'
        else:
            deprel = 'dep'

        deps.append(_entry(i, word, pos, head=head, deprel=deprel))

    return deps


def _entry(i, word, pos, head, deprel):
    return {
        'index': i + 1,
        'token': word,
        'pos': pos,
        'head': head,
        'deprel': deprel,
    }

def _convert_to_output_format(deps: list) -> list:
    """Convert internal dep format to output format with Token/Head/Dependency keys."""
    id_to_text = {d['index']: d['token'] for d in deps}
    id_to_text[0] = 'root'

    tokens = []
    for d in deps:
        tokens.append({
            'Token': d['token'],
            'Head': id_to_text.get(d['head'], 'root'),
            'Dependency': d['deprel'],
        })
    return tokens


def parse_clause(clause: str) -> dict:
    """Return dependency parse for a single clause."""
    if _USE_NEURAL:
        deps = _parse_neural(clause)
    else:
        deps = _parse_heuristic(clause)
    return {
        'clause': clause,
        'dependencies': _convert_to_output_format(deps),
    }


def parse_dependencies(text: str) -> list:
    """Parse all clauses (newline-separated text) and return list of results."""
    clauses = [line.strip() for line in text.strip().split('\n') if line.strip()]
    return [parse_clause(c) for c in clauses]


def main():
    clauses_text = read_text(INPUT_PATH)
    if not clauses_text:
        print("[parser] Input file is empty!")
        return

    dep_data = parse_dependencies(clauses_text)
    write_json(OUTPUT_PATH, dep_data)

    print(f'[parser] Input:  {INPUT_PATH}')
    print(f'[parser] Output: {OUTPUT_PATH}')
    print(f'[parser] Clauses analysed: {len(dep_data)}')

    for item in dep_data:
        print(f'\n--- {item["clause"]}')
        for tok in item['dependencies']:
            print(f"  {tok['Token']:<20} -> {tok['Head']:<15} [{tok['Dependency']}]")


if __name__ == '__main__':
    main()

if __name__ == "__main__":
    main()
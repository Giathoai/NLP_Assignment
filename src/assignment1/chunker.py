import sys
import os
import re
from underthesea import chunk, word_tokenize

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text, write_text

INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "clauses.txt")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "chunks.txt")

RE_NUMBERING = re.compile(r'^\d+\.\s*')
RE_BEN_AB = re.compile(r'^([Bb]ên)\s*([A-ZĐ])$')

def chunk_clauses(text: str) -> str:
    lines = []
    clauses = text.strip().split('\n')
    
    for clause_text in clauses:
        clause_text = clause_text.strip()
        clause_text = RE_NUMBERING.sub('', clause_text)
        if not clause_text:
            continue

        clause_text = re.sub(r'([Bb]ên)\s*([A-ZĐ])', r'\1 \2', clause_text)
        tokens = word_tokenize(clause_text)
        processed_text = " ".join([t.replace('_', ' ') for t in tokens])
            
        tagged = chunk(processed_text)
        prev_tag_type = None 
        
        for i, (word, pos, chunk_tag) in enumerate(tagged):
            match = RE_BEN_AB.match(word)
            if match:
                part1, part2 = match.group(1), match.group(2)
                iob1 = "B-NP" if prev_tag_type != "NP" else "I-NP"
                lines.append(f"{part1}")
                lines.append(f"{iob1}")
                lines.append(f"{part2}")
                lines.append(f"I-NP")
                prev_tag_type = "NP"
                continue

            legal_keywords = ["tnhh", "cổ phần", "thương mại", "dịch vụ", "tư vấn", "phần mềm", "đúng hạn", "hạn"]
            is_legal_suffix = word.lower() in legal_keywords
            is_identifier = (word in ["A", "B", "C"] and i > 0 and tagged[i-1][0].lower() == "bên")
            
            if "NP" in chunk_tag or is_legal_suffix or is_identifier:
                iob = "I-NP" if prev_tag_type == "NP" else "B-NP"
                prev_tag_type = "NP"
            else:
                iob = "O"
                prev_tag_type = "O"
                
            lines.append(f"{word}")
            lines.append(f"{iob}")
            
        lines.append("") 
        
    return "\n".join(lines)
def main():
    raw_text = read_text(INPUT_PATH)
    result = chunk_clauses(raw_text)
    write_text(OUTPUT_PATH, result)
    print(f"[chunker] IOB-tagged output written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
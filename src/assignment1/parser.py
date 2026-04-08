import sys
import os
from underthesea import dependency_parse

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text, write_json

INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "clauses.txt")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "dependency.json")

def parse_dependencies(text: str) -> list[dict]:
    clauses = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    results = []
    for clause in clauses:
        parsed_data = dependency_parse(clause)
        
        id_to_text = {i+1: item[0] for i, item in enumerate(parsed_data)}
        id_to_text[0] = "root" 

        tokens = []
        for item in parsed_data:
            if len(item) == 3:
                word, head_id, dep_label = item
            else:
                _, word, head_id, dep_label = item
            
            tokens.append({
                "Token": word,
                "Head": id_to_text.get(head_id, "root"),
                "Dependency": dep_label 
            })
            
        results.append({
            "clause": clause,
            "dependencies": tokens
        })
        
    return results

def main():
    clauses_text = read_text(INPUT_PATH)
    if not clauses_text:
        print("[parser] File đầu vào trống!")
        return
        
    dep_data = parse_dependencies(clauses_text)
    write_json(OUTPUT_PATH, dep_data)
    print(f"[parser] Done! Đã lưu {len(dep_data)} mệnh đề vào {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
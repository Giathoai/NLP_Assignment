"""
Task 2.3 – Intent Classification
Phân loại ý định của mệnh đề hợp đồng (Baseline TF-IDF + LR hoặc Transformer).
Kết quả lưu ra output/intent_classification.txt
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text, write_text
from src.assignment1.segmenter import segment_clauses

INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "input", "raw_contracts.txt")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "intent_classification.txt")

INTENT_LABELS = [
    "OBLIGATION",       # "The party shall / must …"
    "PROHIBITION",      # "The party shall not / may not …"
    "PERMISSION",       # "The party may …"
    "DEFINITION",       # "For the purposes of this Agreement …"
    "TERMINATION",      # "This Agreement shall terminate …"
    "PAYMENT",          # "The fee / payment shall be …"
    "CONFIDENTIALITY",  # "Each party agrees to keep … confidential"
    "INDEMNITY",        # "Party A shall indemnify …"
    "GOVERNING_LAW",    # "This Agreement shall be governed by …"
    "OTHER",
]

KEYWORD_MAP = {
    "OBLIGATION":      ["shall", "must", "agrees to", "is required"],
    "PROHIBITION":     ["shall not", "may not", "must not", "is prohibited"],
    "PERMISSION":      ["may", "is entitled to", "has the right to"],
    "DEFINITION":      ["means", "defined as", "for the purposes of", "refers to"],
    "TERMINATION":     ["terminat", "expire", "cancel", "end of term"],
    "PAYMENT":         ["pay", "fee", "invoice", "amount", "price", "compensation"],
    "CONFIDENTIALITY": ["confidential", "non-disclosure", "nda", "secret"],
    "INDEMNITY":       ["indemnif", "hold harmless", "defend"],
    "GOVERNING_LAW":   ["governed by", "jurisdiction", "applicable law"],
}

def main():
   

if __name__ == "__main__":
    main()

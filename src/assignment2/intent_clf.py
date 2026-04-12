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

VI_KEYWORD_MAP = {
    "OBLIGATION": ["có nghĩa vụ", "phải", "có trách nhiệm", "cam kết"],
    "PROHIBITION": ["không được", "cấm", "nghiêm cấm"],
    "PERMISSION": ["được quyền", "có quyền", "được phép"],
    "DEFINITION": ["được hiểu là", "định nghĩa", "có nghĩa là"],
    "TERMINATION": ["chấm dứt", "hết hiệu lực", "kết thúc"],
    "PAYMENT": ["thanh toán", "chi trả", "phí", "giá trị hợp đồng"],
    "CONFIDENTIALITY": ["bảo mật", "bí mật", "không tiết lộ"],
    "INDEMNITY": ["bồi thường", "miễn trừ trách nhiệm"],
    "GOVERNING_LAW": ["luật áp dụng", "thẩm quyền", "tòa án"],
}


def classify_clause(clause: str) -> tuple[str, float]:
    text = clause.lower()
    scores = {label: 0 for label in INTENT_LABELS}

    for label, kws in KEYWORD_MAP.items():
        for kw in kws:
            if kw in text:
                scores[label] += 1

    for label, kws in VI_KEYWORD_MAP.items():
        for kw in kws:
            if kw in text:
                scores[label] += 2

    best_label = "OTHER"
    best_score = 0
    for label, score in scores.items():
        if label == "OTHER":
            continue
        if score > best_score:
            best_score = score
            best_label = label

    confidence = min(1.0, 0.35 + best_score * 0.2) if best_score > 0 else 0.2
    return (best_label if best_score > 0 else "OTHER", round(confidence, 2))

def main():
    raw_text = read_text(INPUT_PATH).strip()
    if not raw_text:
        print("[intent_clf] Input trống, không thể phân loại.")
        return

    clauses = segment_clauses(raw_text)
    output_lines = []

    for i, clause in enumerate(clauses, 1):
        label, conf = classify_clause(clause)
        output_lines.append(f"{i}\t{label}\t{conf}\t{clause}")

    write_text(OUTPUT_PATH, "\n".join(output_lines))
    print(f"[intent_clf] Đã phân loại {len(clauses)} clauses -> {OUTPUT_PATH}")

if __name__ == "__main__":
    main()

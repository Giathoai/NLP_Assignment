"""
Task 2.1 – Contract-domain NER Model
Huấn luyện (hoặc fine-tune) và chạy inference NER trên văn bản hợp đồng.
Kết quả lưu ra output/ner_results.json
"""

import sys
import os
import re

import spacy
from spacy.training import Example

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text, read_json, write_json
from src.assignment1.segmenter import segment_clauses

INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "input", "raw_contracts.txt")
TRAIN_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "train_ner.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "ner_results.json")

LABELS = ["ORG", "PERSON", "DATE", "MONEY", "LOC", "CLAUSE_ID", "LEGAL_TERM"]


def load_train_data() -> list[tuple[str, dict]]:
    if not os.path.exists(TRAIN_PATH):
        return []

    raw = read_json(TRAIN_PATH)
    data = []
    for item in raw:
        text = item.get("text", "")
        ents = []
        for ent in item.get("entities", []):
            start = int(ent["start"])
            end = int(ent["end"])
            label = ent["label"]
            ents.append((start, end, label))
        if text:
            data.append((text, {"entities": ents}))
    return data


def train_small_ner(train_data: list[tuple[str, dict]], n_iter: int = 12):
    if not train_data:
        return None

    nlp = spacy.blank("xx")
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    for label in LABELS:
        ner.add_label(label)

    optimizer = nlp.begin_training()
    for _ in range(n_iter):
        losses = {}
        for text, ann in train_data:
            example = Example.from_dict(nlp.make_doc(text), ann)
            nlp.update([example], sgd=optimizer, losses=losses)
    return nlp


def regex_entities(text: str) -> list[dict]:
    patterns = [
        (r"\b\d{1,2}/\d{1,2}/\d{4}\b", "DATE"),
        (r"\b\d+[\.,]?\d*\s*(VND|USD|đồng)\b", "MONEY"),
        (r"\b(TP\.HCM|Hà Nội|Đà Nẵng|Việt Nam)\b", "LOC"),
        (r"\b(Công ty\s+[A-ZĐA-Za-zÀ-ỹ0-9\s\.-]+)", "ORG"),
        (r"\b(Điều\s+\d+)\b", "CLAUSE_ID"),
    ]

    entities = []
    for pattern, label in patterns:
        for m in re.finditer(pattern, text):
            entities.append({
                "text": m.group(0),
                "label": label,
                "start": m.start(),
                "end": m.end(),
            })
    entities.sort(key=lambda x: x["start"])
    return entities


def run_inference(clauses: list[str], model) -> list[dict]:
    results = []
    for clause in clauses:
        if model is not None:
            doc = model(clause)
            entities = [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                }
                for ent in doc.ents
            ]
            if not entities:
                entities = regex_entities(clause)
        else:
            entities = regex_entities(clause)

        results.append({"clause": clause, "entities": entities})
    return results



def main():
    raw_text = read_text(INPUT_PATH).strip()
    if not raw_text:
        print("[ner_model] Input trống, không có dữ liệu để xử lý.")
        return

    clauses = segment_clauses(raw_text)
    train_data = load_train_data()

    model = None
    if train_data:
        try:
            model = train_small_ner(train_data)
            print(f"[ner_model] Train nhanh trên {len(train_data)} mẫu.")
        except Exception as e:
            print(f"[ner_model] Train lỗi, chuyển sang regex fallback: {e}")

    results = run_inference(clauses, model)
    write_json(OUTPUT_PATH, results)
    print(f"[ner_model] Đã lưu {len(results)} clauses vào {OUTPUT_PATH}")

if __name__ == "__main__":
    main()

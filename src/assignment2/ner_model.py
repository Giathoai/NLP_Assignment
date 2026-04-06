"""
Task 2.1 – Contract-domain NER Model
Huấn luyện (hoặc fine-tune) và chạy inference NER trên văn bản hợp đồng.
Kết quả lưu ra output/ner_results.json
"""

import sys
import os

import spacy
from spacy.training import Example

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text, read_json, write_json

INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "input", "raw_contracts.txt")
TRAIN_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "train_ner.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "ner_results.json")

LABELS = ["ORG", "PERSON", "DATE", "MONEY", "LOC", "CLAUSE_ID", "LEGAL_TERM"]



def main():

if __name__ == "__main__":
    main()

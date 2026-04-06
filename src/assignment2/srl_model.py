"""
Task 2.2 – Semantic Role Labeling (SRL)
Gán nhãn vai trò ngữ nghĩa dựa trên vị ngữ chính bằng AllenNLP hoặc spaCy.
Kết quả lưu ra output/srl_results.json
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text, write_json

INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "input", "raw_contracts.txt")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "srl_results.json")


def main():








if __name__ == "__main__":
    main()

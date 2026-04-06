# NLP Contract Analysis

Dự án phân tích văn bản hợp đồng sử dụng các kỹ thuật NLP cho môn học NLP – HK2 2024-25.

---

## Cấu trúc thư mục

```
nlp_contract_analysis/
├── input/raw_contracts.txt          # Văn bản hợp đồng đầu vào
├── output/                          # Kết quả đầu ra của từng pipeline
│   ├── clauses.txt                  # Task 1.1: Mệnh đề độc lập
│   ├── chunks.txt                   # Task 1.2: Cụm danh từ IOB
│   ├── dependency.json              # Task 1.3: Phân tích phụ thuộc
│   ├── ner_results.json             # Task 2.1: Nhận dạng thực thể
│   ├── srl_results.json             # Task 2.2: Vai trò ngữ nghĩa
│   └── intent_classification.txt   # Task 2.3: Phân loại ý định
├── data/train_ner.json              # Dữ liệu huấn luyện NER
├── src/
│   ├── assignment1/                 # Pipeline cú pháp
│   ├── assignment2/                 # Pipeline ngữ nghĩa
│   ├── assignment3/                 # Hệ thống RAG
│   └── utils/file_io.py            # Tiện ích I/O
├── notebooks/                       # Jupyter notebooks thực nghiệm
├── requirements.txt
└── README.md
```

---

## Cài đặt

```bash
# 1. Tạo môi trường ảo
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Tải mô hình spaCy
python -m spacy download en_core_web_sm
```

---

## Cách chạy

### Assignment 1 – Syntactic Pipeline

```bash
# Task 1.1: Tách mệnh đề
python -m src.assignment1.segmenter

# Task 1.2: Gắn nhãn IOB (Noun Phrase Chunking)
python -m src.assignment1.chunker

# Task 1.3: Phân tích phụ thuộc
python -m src.assignment1.parser
```

### Assignment 2 – Semantic Pipeline

```bash
# Task 2.1: Nhận dạng thực thể (NER)
python -m src.assignment2.ner_model

# Task 2.2: Gán nhãn vai trò ngữ nghĩa (SRL)
python -m src.assignment2.srl_model

# Task 2.3: Phân loại ý định
python -m src.assignment2.intent_clf
```

### Assignment 3 – RAG Interface

```bash
# Bước 1: Xây dựng vector database
python -m src.assignment3.vector_db

# Bước 2: Chạy giao diện Streamlit
streamlit run src/assignment3/app.py

# Hoặc chạy giao diện console (không cần Streamlit)
python src/assignment3/app.py
```

---

## Ghi chú

- Đặt văn bản hợp đồng vào `input/raw_contracts.txt` trước khi chạy bất kỳ pipeline nào.
- Backend SRL mặc định là `spacy` (heuristic); đổi sang `allennlp` trong `srl_model.py` nếu cần độ chính xác cao hơn (yêu cầu cài thêm).
- Backend Intent Classification mặc định là `baseline` (keyword-based); đổi sang `transformer` để dùng zero-shot.

---

## Repository

> Thêm link GitHub repository tại đây sau khi push code.

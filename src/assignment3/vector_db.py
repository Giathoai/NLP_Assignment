"""
Assignment 3 – Vector Database for RAG
Khởi tạo và truy vấn cơ sở dữ liệu vector (ChromaDB) để hỗ trợ Retrieval-Augmented Generation.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text
from src.assignment1.segmenter import segment_clauses

INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "input", "raw_contracts.txt")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "output", "chroma_db")

COLLECTION_NAME = "contract_clauses"
_EMBEDDER = None


def get_embedder():
    """Return a sentence-transformers embedding function."""
    global _EMBEDDER
    if _EMBEDDER is not None:
        return _EMBEDDER

    from sentence_transformers import SentenceTransformer
    _EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBEDDER


def build_vector_db(clauses: list[str]):
    """
    Index clauses into ChromaDB.
    Requires: pip install chromadb sentence-transformers
    """
    import chromadb

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(COLLECTION_NAME)

    embedder = get_embedder()
    embeddings = embedder.encode(clauses).tolist()

    ids = [f"clause_{i}" for i in range(len(clauses))]
    collection.upsert(
        ids=ids,
        documents=clauses,
        embeddings=embeddings,
    )
    print(f"[vector_db] Indexed {len(clauses)} clauses into '{COLLECTION_NAME}'.")
    return collection


def query_vector_db(query: str, n_results: int = 5) -> list[dict]:
    """
    Retrieve top-k relevant clauses for a query.
    Returns a list of {id, document, distance} dicts.
    """
    import chromadb

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        # Tự build DB nếu chưa có collection.
        raw_text = read_text(INPUT_PATH)
        clauses = segment_clauses(raw_text)
        collection = build_vector_db(clauses)

    embedder = get_embedder()
    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(query_embeddings=query_embedding, n_results=n_results)
    output = []
    for id_, doc, dist in zip(
        results["ids"][0], results["documents"][0], results["distances"][0]
    ):
        output.append({"id": id_, "document": doc, "distance": dist})
    return output


def main():
    raw_text = read_text(INPUT_PATH)
    clauses = segment_clauses(raw_text)
    build_vector_db(clauses)


if __name__ == "__main__":
    main()

"""
Assignment 3 – RAG Interactive Interface
Giao diện tương tác Streamlit cho hệ thống hỏi-đáp hợp đồng (RAG).
Chạy: streamlit run src/assignment3/app.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.assignment3.vector_db import query_vector_db

try:
    import streamlit as st
    USE_STREAMLIT = True
except ImportError:
    USE_STREAMLIT = False


def generate_answer(query: str, context_clauses: list[str]) -> str:
    """
    Generate an answer from retrieved context using an LLM.
    Falls back to a simple extractive answer if no LLM is available.
    """
    context = "\n".join(f"- {c}" for c in context_clauses)
    try:
        from transformers import pipeline
        qa = pipeline("question-answering")
        result = qa(question=query, context="\n".join(context_clauses))
        return result["answer"]
    except Exception:
        # Fallback: return the most relevant clause
        return context_clauses[0] if context_clauses else "Không tìm thấy thông tin liên quan."


def streamlit_ui():
    st.set_page_config(page_title="Contract Q&A (RAG)", page_icon="📄")
    st.title("📄 Contract Analysis – Q&A Interface")
    st.markdown("Đặt câu hỏi về nội dung hợp đồng. Hệ thống sẽ truy xuất các điều khoản liên quan và tổng hợp câu trả lời.")

    query = st.text_input("💬 Câu hỏi của bạn:", placeholder="Ví dụ: Điều khoản thanh toán quy định gì?")
    n_results = st.slider("Số điều khoản truy xuất", 1, 10, 5)

    if st.button("Tìm kiếm") and query:
        with st.spinner("Đang truy xuất …"):
            hits = query_vector_db(query, n_results=n_results)
        clauses = [h["document"] for h in hits]

        st.subheader("📋 Điều khoản liên quan")
        for i, hit in enumerate(hits):
            st.markdown(f"**{i+1}.** {hit['document']}  \n`distance: {hit['distance']:.4f}`")

        st.subheader("🤖 Câu trả lời tổng hợp")
        answer = generate_answer(query, clauses)
        st.success(answer)


def console_ui():
    print("=== Contract Q&A (RAG) – Console Mode ===")
    print("Nhập 'exit' để thoát.\n")
    while True:
        query = input("Câu hỏi: ").strip()
        if query.lower() in ("exit", "quit"):
            break
        hits = query_vector_db(query, n_results=5)
        clauses = [h["document"] for h in hits]
        print("\nĐiều khoản liên quan:")
        for i, hit in enumerate(hits):
            print(f"  {i+1}. {hit['document']}")
        print("\nCâu trả lời:")
        print(f"  {generate_answer(query, clauses)}\n")


if __name__ == "__main__":
    if USE_STREAMLIT:
        streamlit_ui()
    else:
        console_ui()

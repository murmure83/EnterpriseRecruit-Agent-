
from pathlib import Path

import jieba
from rank_bm25 import BM25Okapi

from rag.document_loader import load_text_file
from rag.text_splitter import split_documents
from rag.vector_store import load_vector_store


PROJECT_ROOT = Path(__file__).resolve().parents[1]

KNOWLEDGE_FILE = (
    PROJECT_ROOT / "data" / "knowledge_base" / "knowledge.txt"
)


def get_bm25_retriever():
    """
    加载知识库，并构建 BM25 关键词检索器。
    """

    documents = load_text_file(str(KNOWLEDGE_FILE))
    chunks = split_documents(documents)

    # 使用 jieba 对中文文本进行分词
    tokenized_corpus = [
        jieba.lcut(chunk.page_content)
        for chunk in chunks
    ]

    bm25 = BM25Okapi(tokenized_corpus)

    print("BM25 检索器构建成功")
    print(f"BM25 文本块数量：{len(chunks)}")

    return bm25, chunks


def hybrid_search(
    question: str,
    k: int = 3,
    fetch_k: int = 5
):
    """
    使用 BM25 + 向量检索进行混合检索。

    通过 RRF（倒数排序融合）合并两种检索结果。
    """

    if not question.strip():
        raise ValueError("检索问题不能为空")

    # 1. 构建 BM25 检索器
    bm25, chunks = get_bm25_retriever()

    # 2. BM25 关键词检索
    tokenized_question = jieba.lcut(question)

    bm25_scores = bm25.get_scores(tokenized_question)

    bm25_results = sorted(
        enumerate(bm25_scores),
        key=lambda item: item[1],
        reverse=True
    )[:fetch_k]

    # 3. 向量检索
    vectorstore = load_vector_store()

    vector_results = vectorstore.similarity_search(
        question,
        k=fetch_k
    )

    # 4. RRF 倒数排序融合
    rrf_scores = {}
    doc_mapping = {}

    rrf_constant = 60

    # 融合 BM25 排名
    for rank, (index, score) in enumerate(
        bm25_results,
        start=1
    ):
        doc = chunks[index]
        key = doc.page_content

        doc_mapping[key] = doc

        rrf_scores[key] = (
            rrf_scores.get(key, 0)
            + 1 / (rrf_constant + rank)
        )

    # 融合向量检索排名
    for rank, doc in enumerate(
        vector_results,
        start=1
    ):
        key = doc.page_content

        doc_mapping[key] = doc

        rrf_scores[key] = (
            rrf_scores.get(key, 0)
            + 1 / (rrf_constant + rank)
        )

    # 5. 根据 RRF 分数重新排序
    ranked_results = sorted(
        rrf_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )[:k]

    print(f"\n问题：{question}")
    print("\n========== 混合检索结果 ==========")

    results = []

    for rank, (content, score) in enumerate(
        ranked_results,
        start=1
    ):
        doc = doc_mapping[content]
        results.append((doc, score))

        print(f"\n第 {rank} 名")
        print(f"RRF 分数：{score:.6f}")
        print(f"内容：\n{doc.page_content}")

    return results

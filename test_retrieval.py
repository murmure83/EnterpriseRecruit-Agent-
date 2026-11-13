
from rag.vector_store import load_vector_store


def test_retrieval():
    vectorstore = load_vector_store()

    questions = [
        "周末加班一天有多少补贴？",
        "周末加班的餐饮补贴标准是什么？",
        "周末加班除了调休还有什么福利？",
        "公司周末加班补贴多少钱？"
    ]

    for question in questions:
        results = vectorstore.similarity_search_with_score(
            question,
            k=3
        )

        print("\n" + "=" * 60)
        print(f"测试问题：{question}")
        print("=" * 60)

        for index, (doc, score) in enumerate(results, start=1):
            print(f"\n第 {index} 名")
            print(f"距离分数：{score:.4f}")
            print(f"文本内容：\n{doc.page_content}")


if __name__ == "__main__":
    test_retrieval()

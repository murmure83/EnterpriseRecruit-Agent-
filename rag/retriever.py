from rag.vector_store import load_vector_store

def get_retriever(search_k: int = 3):
    """
    创建知识库检索器。
    search_k：每次检索返回多少个相关文本块。
    """
    vectorstore = load_vector_store()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": search_k}
    )
    return retriever

def search_knowledge(question: str, search_k: int = 3):
    """
    根据问题检索企业知识库。
    返回相关 Document 列表。
    """

    if not question.strip():
        raise ValueError("检索问题不能为空")

    retriever = get_retriever(search_k)
    documents = retriever.invoke(question)

    print(f"\n问题：{question}")
    print(f"检索到 {len(documents)} 条相关资料")

    for index, doc in enumerate(documents, start=1):
        print(f"\n========== 结果 {index} ==========")
        print(f"来源：{doc.metadata.get('source', '未知')}")
        print(f"内容：{doc.page_content}")
    return documents


from langchain_core.tools import tool

from rag.retriever import search_knowledge


@tool
def knowledge_search_tool(question: str) -> str:
    """
    搜索企业内部知识库。

    当用户询问企业规章制度、考勤、福利、
    研发规范等内部信息时，调用此工具。
    """

    if not question.strip():
        return "检索问题不能为空。"

    documents = search_knowledge(
        question=question,
        search_k=3
    )

    if not documents:
        return "知识库中没有找到相关资料。"

    # 整理检索结果，返回给 Agent
    context = "\n\n".join(
        doc.page_content for doc in documents
    )

    return context

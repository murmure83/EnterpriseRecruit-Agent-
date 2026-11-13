
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from rag.retriever import search_knowledge


# 获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 加载项目根目录的 .env
load_dotenv(PROJECT_ROOT / ".env")


def get_llm():
    """创建 DeepSeek 大模型"""

    api_key = (
        os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("DEEPSEEK_KEY")
    )

    if not api_key:
        raise ValueError(
            "没有找到 DeepSeek API Key，请检查 .env 文件"
        )

    return ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        temperature=0
    )


def answer_question(question: str):
    """
    先检索知识库，再让 DeepSeek 根据资料回答。
    """

    # 1. 检索相关资料
    documents = search_knowledge(question, search_k=3)

    # 2. 整理检索结果
    context = "\n\n".join(
        doc.page_content for doc in documents
    )

    # 3. 获取大模型
    llm = get_llm()

    # 4. 构建提示词
    prompt = f"""
你是星火科技的企业知识库问答助手。

请严格根据下面提供的参考资料回答问题。

要求：
1. 只能根据参考资料回答，不要编造信息。
2. 如果资料中没有答案，请明确说不知道。
3. 回答要简洁、准确。

参考资料：
{context}

用户问题：
{question}

请给出回答：
"""

    # 5. 调用 DeepSeek
    response = llm.invoke(prompt)

    return response.content

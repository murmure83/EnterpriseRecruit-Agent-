import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

# 读取项目根目录的 .env
load_dotenv()


def get_embeddings():
    """
    创建 SiliconFlow Embedding 模型。
    使用 BAAI/bge-m3 将文本转换成向量。
    """

    api_key = os.getenv("SILICON_API_KEY")

    if not api_key:
        raise ValueError(
            "没有找到SILICON_API_KEY，请检查项目根目录的 .env文件"
        )

    embeddings = OpenAIEmbeddings(
        model="BAAI/bge-m3",
        api_key=api_key,
        base_url="https://api.siliconflow.cn/v1"
    )

    return embeddings

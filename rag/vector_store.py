from pathlib import Path
from langchain_chroma import Chroma
from rag.embedding import get_embeddings


# 项目根目录下的向量数据库目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]
VECTOR_DB_DIR = PROJECT_ROOT / "data" / "chroma_db"


def create_vector_store(chunks):
    """
    将文本块向量化并存入 ChromaDB。
    """
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_DIR),
        collection_name="enterprise_knowledge"
    )

    print(f"向量数据库创建成功：{VECTOR_DB_DIR}")
    print(f"写入文本块数量：{len(chunks)}")
    return vectorstore


def load_vector_store():
    """
    加载已经存在的 ChromaDB。
    """
    if not VECTOR_DB_DIR.exists():
        raise FileNotFoundError(
            "向量数据库不存在，请先执行 create_vector_store()"
        )
    embeddings = get_embeddings()
    vectorstore = Chroma(
        collection_name="enterprise_knowledge",
        embedding_function=embeddings,
        persist_directory=str(VECTOR_DB_DIR)
    )

    print("向量数据库加载成功")
    return vectorstore

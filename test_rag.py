from pathlib import Path
from rag.document_loader import load_text_file
from rag.text_splitter import split_documents
from rag.vector_store import create_vector_store
from rag.retriever import search_knowledge


# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 企业制度知识库文件
KNOWLEDGE_FILE = (
    BASE_DIR / "data" / "knowledge_base" / "knowledge.txt"
)

def build_knowledge_base():
    """首次构建知识库"""

    documents = load_text_file(str(KNOWLEDGE_FILE))
    chunks = split_documents(
        documents,
        chunk_size=300,
        chunk_overlap=50
    )
    create_vector_store(chunks)


if __name__ == "__main__":

    # 第一次运行时，构建知识库
    build_knowledge_base()
    # 测试检索
    question = "周末加班一天有多少补贴？"
    results = search_knowledge(question)
    print("\nRAG 检索测试完成！")

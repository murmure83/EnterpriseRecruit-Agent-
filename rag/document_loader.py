
from pathlib import Path
from langchain_community.document_loaders import TextLoader


def load_text_file(file_path: str):
    """
    加载文本文件，返回 LangChain Document 列表。
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{path}")

    loader = TextLoader(
        str(path),
        encoding="utf-8"
    )

    documents = loader.load()

    print(f"成功加载文档：{path.name}")
    print(f"文档数量：{len(documents)}")

    return documents

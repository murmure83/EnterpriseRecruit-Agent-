
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(
    documents,
    chunk_size: int = 180,
    chunk_overlap: int = 30
):
    """
    将文档切分成较小的文本块。

    chunk_size：每个文本块的目标长度。
    chunk_overlap：相邻文本块的重叠长度。
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            "。",
            "！",
            "？",
            "；",
            "，",
            " "
        ]
    )

    chunks = splitter.split_documents(documents)

    print(f"原始文档数量：{len(documents)}")
    print(f"切分后文本块数量：{len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n========== 文本块 {index} ==========")
        print(chunk.page_content)

    return chunks


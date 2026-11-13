
from pathlib import Path
from pypdf import PdfReader
from docx import Document


def parse_pdf(file_path: str) -> str:
    """解析 PDF 简历"""
    reader = PdfReader(file_path)

    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)

    return "\n".join(text)


def parse_word(file_path: str) -> str:
    """解析 Word 简历"""
    document = Document(file_path)

    text = []

    # 提取段落
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    # 提取表格
    for table in document.tables:
        for row in table.rows:
            row_text = [
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            ]
            if row_text:
                text.append(" | ".join(row_text))

    return "\n".join(text)


def parse_resume(file_path: str) -> str:
    """根据文件类型自动解析简历"""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"简历文件不存在：{path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        content = parse_pdf(str(path))
    elif suffix == ".docx":
        content = parse_word(str(path))
    else:
        raise ValueError("目前只支持 PDF 和 DOCX 格式的简历")

    if not content.strip():
        raise ValueError(
            "没有提取到简历文字，可能是扫描版 PDF，需要 OCR 处理"
        )

    print(f"简历解析成功：{path.name}")
    print(f"提取文字长度：{len(content)}")

    return content

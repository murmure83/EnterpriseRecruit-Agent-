
from services.resume_parser import parse_resume
from pathlib import Path


# 自动读取 data/resumes 文件夹中的第一份简历
resume_dir = Path("data/resumes")

files = list(resume_dir.glob("*.pdf"))
files += list(resume_dir.glob("*.docx"))

if not files:
    print("请先将一份 PDF 或 DOCX 简历放入 data/resumes 文件夹")
else:
    content = parse_resume(str(files[0]))

    print("\n========== 简历内容 ==========")
    print(content)

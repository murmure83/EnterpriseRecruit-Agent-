
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from services.resume_parser import parse_resume


# 加载项目根目录的环境变量
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")



# 1. 教育经历
class Education(BaseModel):
    school: str = Field(default="", description="学校名称")
    major: str = Field(default="", description="专业")
    degree: str = Field(default="", description="学历或学位")
    time: str = Field(default="", description="就读时间")


# 2. 专业技能
class SkillsProfile(BaseModel):
    programming_languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    technical_abilities: list[str] = Field(default_factory=list)


# 3. 项目经历
class Project(BaseModel):
    name: str = Field(default="", description="项目名称")
    tech_stack: list[str] = Field(
        default_factory=list,
        description="项目技术栈"
    )
    description: str = Field(default="", description="项目具体内容")


# 4. 最终简历数据结构
class ResumeProfile(BaseModel):
    name: str = Field(default="", description="姓名")
    education: list[Education] = Field(default_factory=list)
    skills: SkillsProfile = Field(default_factory=SkillsProfile)
    projects: list[Project] = Field(default_factory=list)
    work_experience: list[str] = Field(default_factory=list)
    self_evaluation: str = Field(default="")


# 4. 创建 DeepSeek 模型
def get_resume_llm():
    api_key = (
        os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("DEEPSEEK_KEY")
    )

    if not api_key:
        raise ValueError("没有找到 DeepSeek API Key")

    return ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        temperature=0
    )


# 5. 使用大模型提取结构化简历
def analyze_resume(resume_text: str) -> ResumeProfile:
    if not resume_text.strip():
        raise ValueError("简历内容不能为空")

    llm = get_resume_llm()

    structured_llm = llm.with_structured_output(
        ResumeProfile,
        method="json_mode"
    )

    prompt = f"""
你是一名专业的简历信息提取助手。

请严格按照 JSON 格式输出，字段必须符合给定的数据结构。

提取要求：
1. 只能提取原文明确提供的信息，不允许编造。
2. 教育经历需要提取学校、专业、学历和时间。
3. 专业技能需要提取编程语言、框架、工具和技术能力。
4. 项目经历需要提取项目名称、技术栈和具体工作内容。
5. 如果没有工作或实习经历，返回空列表。
6. 如果某项信息缺失，使用空字符串或空列表。
7. 忽略民族、政治面貌、出生日期、性别、电话、
   邮箱和家庭住址等个人属性或联系方式。
8. 不要根据年龄、民族、政治面貌等信息评价候选人。

简历原文：
{resume_text}
"""
    result = structured_llm.invoke(prompt)
    return result


# 6. 测试入口
if __name__ == "__main__":
    resume_dir = PROJECT_ROOT / "data" / "resumes"

    files = list(resume_dir.glob("*.pdf"))
    files += list(resume_dir.glob("*.docx"))

    if not files:
        print("请先将简历放入 data/resumes 文件夹")
    else:
        print(f"正在分析简历：{files[0].name}")

        text = parse_resume(str(files[0]))
        profile = analyze_resume(text)

        print("\n========== AI 简历结构化分析结果 ==========")
        print(profile.model_dump_json(indent=2))

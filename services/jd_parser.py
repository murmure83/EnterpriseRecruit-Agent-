
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, ValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


# 1. 定义岗位数据结构
class JobProfile(BaseModel):
    job_title: str = Field(default="", description="岗位名称")
    responsibilities: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    education_requirement: str = Field(default="")
    experience_requirement: str = Field(default="")
    other_requirements: list[str] = Field(default_factory=list)


# 2. 创建 DeepSeek 模型
def get_jd_llm():
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


# 3. 解析岗位描述
def parse_jd(jd_text: str) -> JobProfile:
    if not jd_text.strip():
        raise ValueError("岗位描述不能为空")

    llm = get_jd_llm()

    prompt = f"""
你是一名专业的招聘岗位分析助手。

请从下面的岗位描述中提取信息。

必须遵守：
1. 提取岗位名称。
2. 提取所有明确的岗位职责。
3. 将明确要求掌握的技能放入 required_skills。
4. 将带有“优先”“加分”等字样的技能放入 preferred_skills。
5. 提取学历和工作经验要求。
6. 不允许编造原文没有的信息。
7. 必须返回完整JSON，不能返回空对象。
8. 如果原文明确出现某项信息，必须提取出来。

JSON结构示例：
{{
    "job_title": "AI应用开发工程师",
    "responsibilities": ["参与AI应用开发"],
    "required_skills": ["Python", "LangChain或LangGraph"],
    "preferred_skills": ["RAG", "FastAPI"],
    "education_requirement": "本科及以上学历",
    "experience_requirement": "",
    "other_requirements": []
}}

岗位原文：
{jd_text}
"""

    response = llm.invoke(
        prompt,
        response_format={"type": "json_object"}
    )

    print("\n========== DeepSeek JD原始返回 ==========")
    print(response.content)

    try:
        data = json.loads(response.content)
        result = JobProfile.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"JD解析结果格式错误：{e}")

    if not result.job_title or not result.required_skills:
        raise ValueError(
            "JD解析结果不完整，请检查DeepSeek原始返回内容。"
        )

    return result


# 4. 测试入口
if __name__ == "__main__":

    sample_jd = """
招聘岗位：AI应用开发工程师

岗位职责：
1. 参与基于大语言模型的AI应用开发。
2. 负责RAG知识库搭建与优化。
3. 参与Agent工作流设计与开发。
4. 负责后端接口开发和系统集成。

任职要求：
1. 熟练掌握Python。
2. 熟悉LangChain或LangGraph。
3. 了解大语言模型API调用和Prompt Engineering。
4. 熟悉RAG、向量数据库者优先。
5. 具备FastAPI开发经验者优先。
6. 本科及以上学历。
"""

    profile = parse_jd(sample_jd)

    print("\n========== JD岗位解析结果 ==========")
    print(profile.model_dump_json(indent=2))

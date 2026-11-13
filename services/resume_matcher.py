from services.interview_generator import generate_interview_questions
import json
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from services.resume_parser import parse_resume
from services.resume_analyzer import analyze_resume
from services.jd_parser import parse_jd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


# 1. 单项技能匹配结果
class SkillAssessment(BaseModel):
    skill: str = Field(default="", description="技能名称")

    status: Literal[
        "matched",
        "partial",
        "not_found"
    ] = Field(description="匹配状态")

    evidence: str = Field(
        default="",
        description="简历中支持该判断的具体证据"
    )


# 2. 项目经历匹配分析
class ProjectAssessment(BaseModel):
    project_name: str = Field(default="", description="项目名称")

    relevance: str = Field(
        default="",
        description="项目与岗位的关联分析"
    )

    evidence: str = Field(
        default="",
        description="简历中的具体证据"
    )


# 3. 最终匹配结果
class MatchResult(BaseModel):
    required_skill_assessments: list[SkillAssessment] = Field(
        default_factory=list
    )

    preferred_skill_assessments: list[SkillAssessment] = Field(
        default_factory=list
    )

    project_assessments: list[ProjectAssessment] = Field(
        default_factory=list
    )

    match_score: int = Field(
        default=0,
        ge=0,
        le=100,
        description="综合技能匹配度"
    )

    strengths: list[str] = Field(
        default_factory=list,
        description="候选人的岗位相关优势"
    )

    gaps: list[str] = Field(
        default_factory=list,
        description="尚未体现或存在不足的岗位要求"
    )

    review_notes: list[str] = Field(
        default_factory=list,
        description="需要HR进一步核实的信息"
    )

    summary: str = Field(
        default="",
        description="综合匹配分析"
    )


# 4. 创建 DeepSeek 模型
def get_match_llm():
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


# 5. 简历与岗位匹配

def match_resume_to_jd(resume, job) -> MatchResult:

    llm = get_match_llm()

    resume_data = resume.model_dump(
        exclude={"name", "self_evaluation"}
    )

    job_data = job.model_dump()

    prompt = f"""
你是一名专业的招聘辅助分析助手。

请根据候选人简历和岗位JD进行匹配分析。

候选人简历：
{json.dumps(resume_data, ensure_ascii=False)}

岗位JD：
{json.dumps(job_data, ensure_ascii=False)}

请严格输出JSON对象，必须包含以下字段：

{{
    "required_skill_assessments": [
        {{
            "skill": "技能名称",
            "status": "matched",
            "evidence": "简历中的具体证据"
        }}
    ],
    "preferred_skill_assessments": [
        {{
            "skill": "技能名称",
            "status": "partial",
            "evidence": "简历中的具体证据"
        }}
    ],
    "project_assessments": [
        {{
            "project_name": "项目名称",
            "relevance": "与岗位的关联分析",
            "evidence": "简历中的具体证据"
        }}
    ],
    "match_score": 70,
    "strengths": ["岗位相关优势"],
    "gaps": ["尚未体现的岗位要求"],
    "review_notes": ["需要HR进一步核实的信息"],
    "summary": "综合匹配分析"
}}

分析规则：

1. 必须逐项分析JD中的所有必需技能和加分技能。
2. matched表示有明确证据。
3. partial表示有相关经验但证据不足。
4. not_found表示简历没有体现。
5. 每项技能必须给出简历证据，没有证据时写明未体现。
6. 项目经历必须结合实际项目分析。
7. 不允许编造候选人的技能或经历。
8. 不使用姓名、民族、性别、年龄等个人属性评价候选人。
9. 不得直接给出录用或淘汰决定。
10. match_score按照必需技能70%、加分技能30%的权重计算；
    matched计1分，partial计0.5分，not_found计0分。
    如果某类技能为空，则由另一类承担全部权重。
11. 所有字段都必须填写，列表没有内容时返回空列表。
12. status只能使用matched、partial、not_found。
13. 只返回JSON，不要输出Markdown代码块。
"""

    # 直接使用 JSON Mode 获取模型原始输出
    response = llm.invoke(
        prompt,
        response_format={"type": "json_object"}
    )
    print("\n========== DeepSeek 原始返回内容 ==========")
    print(response.content)
    # 解析JSON并进行Pydantic校验
    result = MatchResult.model_validate_json(
        response.content
    )

    # 防止模型返回空结果却被误认为成功
    if not result.required_skill_assessments:
        raise ValueError("模型没有返回必需技能匹配结果")

    return result



# 6. 测试入口
if __name__ == "__main__":

    # 读取简历
    resume_dir = PROJECT_ROOT / "data" / "resumes"

    files = list(resume_dir.glob("*.pdf"))
    files += list(resume_dir.glob("*.docx"))

    if not files:
        print("请先将简历放入 data/resumes 文件夹")
        raise SystemExit

    resume_text = parse_resume(str(files[0]))

    print("\n正在提取简历信息...")
    resume_profile = analyze_resume(resume_text)

    # 测试岗位JD
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

    print("\n正在解析岗位JD...")
    job_profile = parse_jd(sample_jd)
    print("\n========== JD解析结果 ==========")
    print(job_profile.model_dump_json(indent=2))

    print("\n正在进行简历与岗位匹配...")
    result = match_resume_to_jd(
        resume_profile,
        job_profile
    )
    print("\n正在生成针对性面试题...")

    interview_plan = generate_interview_questions(
        resume_profile,
        job_profile,
        result
    )

    print("\n========== 面试题生成结果 ==========")
    print(interview_plan.model_dump_json(indent=2))
    from services.report_generator import save_recruitment_report

    save_recruitment_report(
        resume_profile,
        job_profile,
        result,
        interview_plan
    )
    print("\n========== 简历与岗位匹配结果 ==========")
    print(result.model_dump_json(indent=2))

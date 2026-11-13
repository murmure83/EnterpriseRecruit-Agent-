from __future__ import annotations
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from services.resume_analyzer import ResumeProfile
from services.jd_parser import JobProfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.resume_matcher import MatchResult


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


# 1. 定义面试题数据结构
class InterviewQuestion(BaseModel):
    category: str = Field(description="考察方向")
    question: str = Field(description="面试问题")
    purpose: str = Field(description="考察目的")
    evaluation_points: list[str] = Field(
        default_factory=list,
        description="回答评价要点"
    )
    follow_up: str = Field(
        default="",
        description="可选追问"
    )


class InterviewPlan(BaseModel):
    job_title: str = Field(default="")
    candidate_summary: str = Field(default="")
    questions: list[InterviewQuestion] = Field(
        default_factory=list
    )
    interviewer_notes: list[str] = Field(
        default_factory=list
    )


# 2. 创建 DeepSeek 模型
def get_interview_llm():
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
        temperature=0.3
    )


# 3. 生成针对性面试题
def generate_interview_questions(
    resume: ResumeProfile,
    job: JobProfile,
    match_result: MatchResult
) -> InterviewPlan:

    llm = get_interview_llm()

    resume_data = resume.model_dump(
        exclude={"name", "self_evaluation"}
    )

    job_data = job.model_dump()
    match_data = match_result.model_dump()

    prompt = f"""
你是一名专业的技术面试官。

请根据候选人简历、岗位要求和技能匹配分析结果，
生成一份有针对性的技术面试计划。

岗位信息：
{json.dumps(job_data, ensure_ascii=False)}

候选人简历：
{json.dumps(resume_data, ensure_ascii=False)}

技能匹配分析：
{json.dumps(match_data, ensure_ascii=False)}

生成要求：

1. 生成8道有针对性的技术面试题。
2. 必须围绕岗位职责和候选人实际项目经历。
3. 优先考察匹配分析中指出的能力缺口。
4. 重点考察LangChain、RAG、Agent、FastAPI及大模型应用开发。
5. 问题应具体，不能只问概念定义。
6. 每道题提供考察目的、回答评价要点和一个追问。
7. 评价要点应帮助面试官判断候选人是否真正参与过项目。
8. 不得编造候选人没有做过的项目经历。
9. 不得将姓名、性别、民族、出生日期等个人属性作为考察依据。
10. 问题应适合技术面试，难度由基础到深入。

请只返回符合指定JSON结构的内容。

JSON结构：
{{
    "job_title": "岗位名称",
    "candidate_summary": "候选人的技术背景简述",
    "questions": [
        {{
            "category": "RAG项目实战",
            "question": "具体面试问题",
            "purpose": "考察目的",
            "evaluation_points": [
                "评价要点1",
                "评价要点2"
            ],
            "follow_up": "进一步追问"
        }}
    ],
    "interviewer_notes": [
        "面试官需要重点核实的内容"
    ]
}}
"""

    response = llm.invoke(
        prompt,
        response_format={"type": "json_object"}
    )

    print("\n========== DeepSeek面试题原始返回 ==========")
    print(response.content)

    try:
        data = json.loads(response.content)
        result = InterviewPlan.model_validate(data)
    except Exception as e:
        raise ValueError(f"面试题解析失败：{e}")

    if len(result.questions) < 8:
        raise ValueError(
            f"面试题数量不足，当前只有{len(result.questions)}道"
        )

    return result

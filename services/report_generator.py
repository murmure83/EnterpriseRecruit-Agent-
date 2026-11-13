
import json
from datetime import datetime
from pathlib import Path

from services.resume_analyzer import ResumeProfile
from services.jd_parser import JobProfile
from services.resume_matcher import MatchResult
from services.interview_generator import InterviewPlan


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"


def generate_markdown_report(
    resume: ResumeProfile,
    job: JobProfile,
    match_result: MatchResult,
    interview_plan: InterviewPlan
) -> str:

    lines = []

    lines.append("# 企业招聘评估报告")
    lines.append("")
    lines.append(f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**招聘岗位：** {job.job_title}")
    lines.append("")
    lines.append("---")

    # 一、岗位信息
    lines.append("")
    lines.append("## 一、岗位信息")
    lines.append("")
    lines.append("### 岗位职责")

    for item in job.responsibilities:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("### 必需技能")

    for item in job.required_skills:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("### 加分技能")

    for item in job.preferred_skills:
        lines.append(f"- {item}")

    lines.append("")
    lines.append(f"**学历要求：** {job.education_requirement or '未明确'}")
    lines.append(f"**经验要求：** {job.experience_requirement or '未明确'}")

    # 二、候选人技术背景
    lines.append("")
    lines.append("## 二、候选人技术背景")

    lines.append("")
    lines.append("### 教育经历")

    for edu in resume.education:
        lines.append(
            f"- {edu.school}，{edu.major}，"
            f"{edu.degree}，{edu.time}"
        )

    lines.append("")
    lines.append("### 技能情况")

    skills = resume.skills

    lines.append(
        f"- 编程语言：{', '.join(skills.programming_languages) or '未提供'}"
    )
    lines.append(
        f"- 开发框架：{', '.join(skills.frameworks) or '未提供'}"
    )
    lines.append(
        f"- 开发工具：{', '.join(skills.tools) or '未提供'}"
    )
    lines.append(
        f"- 技术能力：{', '.join(skills.technical_abilities) or '未提供'}"
    )

    # 三、岗位匹配分析
    lines.append("")
    lines.append("## 三、岗位匹配分析")
    lines.append("")
    lines.append(
        f"**技能匹配分数：{match_result.match_score}/100**"
    )
    lines.append("")
    lines.append(
        "> 此分数为模型辅助评估结果，不代表客观录用概率，"
        "应结合项目证据和面试表现综合判断。"
    )

    lines.append("")
    lines.append("### 必需技能匹配")

    for item in match_result.required_skill_assessments:
        lines.append(f"- **{item.skill}**：{item.status}")
        lines.append(f"  - 证据：{item.evidence}")

    lines.append("")
    lines.append("### 加分技能匹配")

    for item in match_result.preferred_skill_assessments:
        lines.append(f"- **{item.skill}**：{item.status}")
        lines.append(f"  - 证据：{item.evidence}")

    lines.append("")
    lines.append("### 优势")

    for item in match_result.strengths:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("### 能力缺口")

    for item in match_result.gaps:
        lines.append(f"- {item}")

    # 四、项目分析
    lines.append("")
    lines.append("## 四、项目经历分析")

    for project in match_result.project_assessments:
        lines.append("")
        lines.append(f"### {project.project_name}")
        lines.append(f"- 关联分析：{project.relevance}")
        lines.append(f"- 项目证据：{project.evidence}")

    # 五、面试题
    lines.append("")
    lines.append("## 五、针对性技术面试题")

    for index, question in enumerate(interview_plan.questions, 1):
        lines.append("")
        lines.append(
            f"### {index}. [{question.category}] {question.question}"
        )
        lines.append(f"**考察目的：** {question.purpose}")
        lines.append("")
        lines.append("**回答评价要点：**")

        for point in question.evaluation_points:
            lines.append(f"- {point}")

        if question.follow_up:
            lines.append("")
            lines.append(f"**追问：** {question.follow_up}")

    # 六、面试官建议
    lines.append("")
    lines.append("## 六、面试官重点核实事项")

    for item in match_result.review_notes:
        lines.append(f"- {item}")

    for item in interview_plan.interviewer_notes:
        lines.append(f"- {item}")

    # 七、综合结论
    lines.append("")
    lines.append("## 七、综合评估结论")
    lines.append("")
    lines.append(match_result.summary)
    lines.append("")
    lines.append(
        "**建议：** 结合技术面试中的实际回答、项目真实性和岗位需求，"
        "由招聘人员综合判断后续流程。"
    )

    lines.append("")
    lines.append("---")
    lines.append(
        "本报告仅用于招聘辅助评估，不应作为自动淘汰或录用的唯一依据。"
    )

    return "\n".join(lines)


def save_recruitment_report(
    resume: ResumeProfile,
    job: JobProfile,
    match_result: MatchResult,
    interview_plan: InterviewPlan
):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report_content = generate_markdown_report(
        resume,
        job,
        match_result,
        interview_plan
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    markdown_path = OUTPUT_DIR / f"招聘评估报告_{timestamp}.md"
    json_path = OUTPUT_DIR / f"招聘评估数据_{timestamp}.json"

    # 保存 Markdown 报告
    markdown_path.write_text(
        report_content,
        encoding="utf-8"
    )

    # 保存结构化 JSON 数据
    report_data = {
        "job": job.model_dump(),
        "resume": resume.model_dump(
            exclude={"name", "self_evaluation"}
        ),
        "match_result": match_result.model_dump(),
        "interview_plan": interview_plan.model_dump()
    }

    json_path.write_text(
        json.dumps(
            report_data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n========== 招聘报告生成成功 ==========")
    print(f"Markdown报告：{markdown_path}")
    print(f"JSON数据：{json_path}")

    return markdown_path, json_path

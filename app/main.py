import sys
import json
from pathlib import Path

import streamlit as st

# 获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 将项目根目录加入 Python 搜索路径
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 导入项目模块（必须放在路径设置之后）
from services.resume_parser import parse_resume
from services.resume_analyzer import analyze_resume
from services.jd_parser import parse_jd
from services.resume_matcher import match_resume_to_jd
from services.interview_generator import generate_interview_questions
from services.report_generator import (
    generate_markdown_report,
    save_recruitment_report
)
from agent.graph import chat as agent_chat

st.set_page_config(
    page_title="EnterpriseRecruit AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 EnterpriseRecruit AI")
st.caption("基于大语言模型与 RAG 的企业智能招聘辅助系统")

st.divider()

st.subheader("一、上传候选人简历")

uploaded_file = st.file_uploader(
    "请选择 PDF 或 DOCX 格式的简历",
    type=["pdf", "docx"]
)

st.subheader("二、填写招聘岗位 JD")

jd_text = st.text_area(
    "请粘贴岗位描述",
    height=220,
    placeholder="请在这里粘贴岗位职责、任职要求和技能要求..."
)

analyze_button = st.button(
    "开始智能招聘分析",
    type="primary",
    use_container_width=True
)

if analyze_button:

    if uploaded_file is None:
        st.error("请先上传候选人简历。")

    elif not jd_text.strip():
        st.error("请先填写招聘岗位 JD。")

    else:
        try:
            with st.spinner("正在分析简历与岗位要求，请稍候..."):

                # 1. 保存上传文件
                resume_dir = PROJECT_ROOT / "outputs" / "uploads"
                resume_dir.mkdir(parents=True, exist_ok=True)

                file_path = resume_dir / uploaded_file.name
                file_path.write_bytes(uploaded_file.getvalue())

                # 2. 解析简历
                resume_text = parse_resume(str(file_path))

                # 3. 简历结构化分析
                resume_profile = analyze_resume(resume_text)

                # 4. JD 解析
                job_profile = parse_jd(jd_text)

                # 5. 简历与岗位匹配
                match_result = match_resume_to_jd(
                    resume_profile,
                    job_profile
                )

                # 6. 生成针对性面试题
                interview_plan = generate_interview_questions(
                    resume_profile,
                    job_profile,
                    match_result
                )

                # 7. 保存招聘报告
                markdown_path, json_path = save_recruitment_report(
                    resume_profile,
                    job_profile,
                    match_result,
                    interview_plan
                )

            st.success("招聘分析完成！")

            # 匹配结果
            st.divider()
            st.subheader("三、岗位匹配分析")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "模型辅助匹配分数",
                    f"{match_result.match_score}/100"
                )

            with col2:
                st.metric(
                    "生成面试题数量",
                    len(interview_plan.questions)
                )

            st.info(
                "匹配分数仅为模型辅助评估结果，"
                "不代表客观录用概率，不应作为自动淘汰或录用的唯一依据。"
            )

            st.markdown("### 综合评估")
            st.write(match_result.summary)

            st.markdown("### 优势")
            for item in match_result.strengths:
                st.write(f"- {item}")

            st.markdown("### 能力缺口")
            for item in match_result.gaps:
                st.write(f"- {item}")

            st.markdown("### 必需技能匹配")

            for item in match_result.required_skill_assessments:
                st.write(f"**{item.skill}**：{item.status}")
                st.caption(f"证据：{item.evidence}")

            st.markdown("### 加分技能匹配")

            for item in match_result.preferred_skill_assessments:
                st.write(f"**{item.skill}**：{item.status}")
                st.caption(f"证据：{item.evidence}")

            # 面试题
            st.divider()
            st.subheader("四、针对性技术面试题")

            for index, question in enumerate(
                interview_plan.questions, 1
            ):
                with st.expander(
                    f"{index}. [{question.category}] {question.question}"
                ):
                    st.write("**考察目的**")
                    st.write(question.purpose)

                    st.write("**回答评价要点**")
                    for point in question.evaluation_points:
                        st.write(f"- {point}")

                    if question.follow_up:
                        st.write("**追问**")
                        st.write(question.follow_up)

            # 面试官建议
            st.divider()
            st.subheader("五、面试官重点核实事项")

            for item in match_result.review_notes:
                st.write(f"- {item}")

            for item in interview_plan.interviewer_notes:
                st.write(f"- {item}")

            # 报告下载
            st.divider()
            st.subheader("六、招聘评估报告下载")

            report_content = generate_markdown_report(
                resume_profile,
                job_profile,
                match_result,
                interview_plan
            )

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    "下载 Markdown 招聘报告",
                    data=report_content,
                    file_name="招聘评估报告.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            with col2:
                json_content = json_path.read_text(
                    encoding="utf-8"
                )

                st.download_button(
                    "下载 JSON 评估数据",
                    data=json_content,
                    file_name="招聘评估数据.json",
                    mime="application/json",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"分析过程中出现错误：{e}")
            st.exception(e)

# ==============================
# 七、企业知识库智能问答
# ==============================

st.divider()
st.subheader("七、企业知识库智能问答")

st.caption(
    "基于 LangGraph Agent 与 RAG 知识库，"
    "回答企业考勤、福利、研发规范等内部问题。"
)

# 初始化聊天记录
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

# 显示历史聊天记录
for message in st.session_state.agent_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入问题
question = st.chat_input(
    "例如：周末加班一天有多少补贴？"
)

if question:
    # 显示并保存用户问题
    st.session_state.agent_messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # 调用企业知识库 Agent
    with st.chat_message("assistant"):
        with st.spinner("Agent 正在检索企业知识库..."):
            try:
                answer = agent_chat(question)
                st.markdown(answer)

                st.session_state.agent_messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error(f"知识库问答失败：{e}")
                st.exception(e)

# EnterpriseRecruit-Agent

基于大语言模型、RAG 和 LangGraph 的企业智能招聘辅助系统。

## 一、项目简介

EnterpriseRecruit-Agent 是一个面向企业招聘场景的 AI 辅助系统，结合大语言模型与检索增强生成（RAG）技术，实现简历解析、岗位匹配、面试题生成、招聘报告生成以及企业知识库问答等功能。

系统通过 Streamlit 提供交互式网页界面，帮助招聘人员提高简历分析和面试准备效率。

本项目定位为招聘辅助工具，分析结果仅供人工参考，不作为自动录用或淘汰候选人的唯一依据。

## 二、核心功能

### 1. 简历智能解析
- 支持 PDF、DOCX 格式简历上传。
- 提取简历文本内容。
- 使用 DeepSeek 对简历进行结构化分析。
- 提取教育经历、专业技能、项目经历和工作经历。

### 2. JD 岗位解析
- 输入招聘岗位描述（JD）。
- 自动提取岗位职责、必需技能和加分技能。
- 结构化整理岗位要求。

### 3. 简历与岗位智能匹配
- 分析候选人技能与岗位要求的匹配情况。
- 将技能分为匹配、部分匹配和未体现。
- 结合项目经历分析岗位相关性。
- 输出匹配分数、优势、能力缺口和待核实事项。

### 4. AI 面试题生成
- 根据候选人简历和岗位要求生成针对性技术面试题。
- 提供考察目的、回答评价要点和追问建议。
- 辅助面试官制定技术面试计划。

### 5. 招聘报告生成
- 自动生成 Markdown 招聘评估报告。
- 保存 JSON 格式的结构化评估数据。
- 支持网页端下载分析报告。

### 6. 企业知识库智能问答
- 基于 RAG 检索企业内部知识文档。
- 使用 LangGraph 构建 Agent 工作流。
- 支持企业考勤、福利和研发规范等知识问答。

## 三、技术栈

| 技术 | 用途 |
|---|---|
| Python | 后端开发语言 |
| DeepSeek | 大语言模型与文本分析 |
| LangChain | 大模型应用开发框架 |
| LangGraph | Agent 工作流构建 |
| RAG | 企业知识库检索增强生成 |
| ChromaDB | 向量数据库 |
| BGE-M3 | 文本向量化 |
| Pydantic | 结构化数据建模与校验 |
| Streamlit | Web 交互界面 |
| PyPDF | PDF 简历解析 |
| python-docx | Word 简历解析 |

## 四、项目结构

```text
EnterpriseRecruit-Agent/
│
├── agent/
│   ├── tools.py
│   └── graph.py
│
├── app/
│   └── main.py
│
├── data/
│   ├── knowledge_base/
│   ├── resumes/
│   └── chroma_db/
│
├── outputs/
│
├── rag/
│   ├── document_loader.py
│   ├── text_splitter.py
│   ├── embedding.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── qa.py
│   ├── test_rag.py
│   └── hybrid_retriever.py
│
├── services/
│   ├── resume_parser.py
│   ├── resume_analyzer.py
│   ├── jd_parser.py
│   ├── resume_matcher.py
│   ├── interview_generator.py
│   └── report_generator.py
│
├── .env
└── README.md
```

## 五、环境配置

建议使用 Python 虚拟环境安装项目依赖。

在项目根目录创建 `.env` 文件，并配置自己的 API Key：

```env
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
SILICON_API_KEY=你的SiliconFlow_API_Key
```

请勿将包含真实 API Key 的 `.env` 文件上传到 GitHub。

## 六、项目运行

确保已经配置好 Python 环境、依赖和 API Key，并准备好企业知识库数据及对应的向量索引。

在项目根目录打开终端，运行：

```bash
streamlit run app/main.py
```

启动成功后，在浏览器访问：

```text
http://localhost:8501
```

即可进入系统网页。

## 七、系统业务流程

```text
上传候选人简历 + 输入岗位 JD
              |
              v
          简历解析
              |
              v
        简历结构化提取
              |
              v
           JD 解析
              |
              v
        简历与岗位匹配
              |
              v
        针对性面试题生成
              |
              v
          招聘报告生成
              |
              v
       Markdown / JSON 下载
```

企业知识问答采用独立的 Agent + RAG 流程：

```text
用户提出企业内部问题
          |
          v
      LangGraph Agent
          |
          v
    企业知识库检索工具
          |
          v
       ChromaDB 检索
          |
          v
       DeepSeek 生成回答
          |
          v
        返回答案
```

## 八、项目特点

- 将大语言模型应用于实际企业招聘场景。
- 结合结构化信息提取与岗位技能匹配。
- 根据候选人经历生成有针对性的技术面试题。
- 通过 RAG 实现企业内部知识检索与问答。
- 使用 LangGraph 实现 Agent 工具调用流程。
- 提供 Streamlit 可视化交互界面。
- 支持招聘分析报告导出。

## 九、后续优化方向

- 增加多候选人批量分析能力。
- 优化技能匹配的证据追踪与可解释性。
- 增加面试评价记录和人工反馈机制。
- 完善知识库文档管理与检索效果评估。
- 增加用户权限与招聘数据安全管理。

---

**声明：** 本项目为 AI 招聘辅助系统，模型生成的分析结果可能存在误差。招聘人员应结合候选人的实际能力、项目证据和面试表现进行人工判断。
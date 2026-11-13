
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from agent.tools import knowledge_search_tool


# 加载环境变量
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


# 注册 Agent 可以使用的工具
tools = [knowledge_search_tool]


def get_llm():
    """创建 DeepSeek 模型"""

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


# 让大模型具备工具调用能力
llm = get_llm()
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: MessagesState):
    """Agent 思考节点"""

    response = llm_with_tools.invoke(state["messages"])

    return {"messages": [response]}


# 创建 LangGraph 工作流
builder = StateGraph(MessagesState)

builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "chatbot")

# 根据模型是否发出工具调用，决定下一步
builder.add_conditional_edges(
    "chatbot",
    tools_condition
)

# 工具执行完后，返回模型继续处理
builder.add_edge("tools", "chatbot")

# 编译工作流
agent = builder.compile()


def chat(question: str):
    """与 Agent 对话"""

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    return result["messages"][-1].content

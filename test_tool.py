
from agent.tools import knowledge_search_tool


if __name__ == "__main__":

    result = knowledge_search_tool.invoke({
        "question": "周末加班一天有多少补贴？"
    })

    print("\n========== Agent 工具调用结果 ==========")
    print(result)

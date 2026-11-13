from agent.graph import chat

if __name__ == "__main__":

    questions = [
        "你好，请介绍一下你自己。",
        "周末加班一天有多少补贴？"
    ]

    for question in questions:

        print("\n========== 用户问题 ==========")
        print(question)
        answer=chat(question)
        print("\n========== Agent 回答 ==========")
        print(answer)

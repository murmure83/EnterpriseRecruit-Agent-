
from rag.qa import answer_question


if __name__ == "__main__":

    question = "周末加班一天有多少补贴？"

    answer = answer_question(question)

    print("\n========== DeepSeek 回答 ==========")
    print(answer)

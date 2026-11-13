
from rag.hybrid_retriever import hybrid_search


# 测试问题与正确答案关键词
TEST_CASES = [
    {
        "question": "周末加班一天有多少补贴？",
        "keywords": ["150 元", "餐饮补贴"]
    },
    {
        "question": "周末加班的餐饮补贴标准是什么？",
        "keywords": ["150 元", "餐饮补贴"]
    },
    {
        "question": "周末加班除了调休还有什么福利？",
        "keywords": ["150 元", "餐饮补贴"]
    },
    {
        "question": "公司周末加班补贴多少钱？",
        "keywords": ["150 元", "餐饮补贴"]
    },
    {
        "question": "员工每个月有几次忘打卡补签机会？",
        "keywords": ["3 次", "忘打卡补签"]
    },
    {
        "question": "入职三年可以休几天年假？",
        "keywords": ["10 天"]
    },
    {
        "question": "员工生日有什么福利？",
        "keywords": ["300 元", "生日假"]
    },
    {
        "question": "公司什么时候组织年度体检？",
        "keywords": ["9 月份"]
    },
    {
        "question": "代码合并到 develop 前需要经过什么流程？",
        "keywords": ["Code Review", "高级工程师"]
    },
    {
        "question": "发现 P0 级故障后多久需要拉起紧急会议？",
        "keywords": ["5 分钟"]
    },
]


def evaluate_retrieval():
    top1_hits = 0
    top3_hits = 0

    print("\n========== 混合检索自动评估 ==========")

    for index, case in enumerate(TEST_CASES, start=1):
        question = case["question"]
        keywords = case["keywords"]

        results = hybrid_search(
            question=question,
            k=3,
            fetch_k=5
        )

        ranks = []

        for rank, (doc, score) in enumerate(results, start=1):
            content = doc.page_content

            if all(keyword in content for keyword in keywords):
                ranks.append(rank)

        if ranks:
            best_rank = min(ranks)

            if best_rank == 1:
                top1_hits += 1

            top3_hits += 1

            print(f"\n测试 {index}：通过")
            print(f"最佳排名：第 {best_rank} 名")
        else:
            print(f"\n测试 {index}：未命中")
            print(f"问题：{question}")

    total = len(TEST_CASES)

    print("\n========== 最终评估结果 ==========")
    print(f"测试问题总数：{total}")
    print(f"Top-1 命中率：{top1_hits}/{total} = {top1_hits / total:.2%}")
    print(f"Top-3 命中率：{top3_hits}/{total} = {top3_hits / total:.2%}")


if __name__ == "__main__":
    evaluate_retrieval()


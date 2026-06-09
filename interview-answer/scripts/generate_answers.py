"""AI 生成面试参考答案"""
import json, os, sys
from dotenv import load_dotenv
import os as _os
# 从 backend 目录加载 .env
_env_path = _os.path.join(_os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')
load_dotenv(_env_path)
# fallback: 当前目录
if not _os.getenv("DEEPSEEK_API_KEY"):
    load_dotenv()

INPUT = "filtered_questions.json"
OUTPUT = "answered_questions.json"
RESUME = os.getenv("RESUME_TEXT", "有产品实习经历")
JD = os.getenv("JD_TEXT", "商业产品经理")


def gen_answer(question, client, used_experiences):
    prompt = f"""你是资深面试官。为以下面试题生成参考答案。

候选人真实背景（只能从以下经历选取，不能编造或替换）:
{RESUME}

目标岗位: {JD}

当前面试题: {question}

已在前面的回答中使用过的经历（本轮禁止重复使用）: {used_experiences}

生成要求:
1. 'intent': 面试官这道题到底在考什么（一句话说透）
2. 'answer': 参考答案(200-300字)。STAR结构。必须从候选人真实背景中选经历，禁止编造。如果简历里没有匹配经历，诚实地说"可以从XX角度回答"并给出框架。
3. 'logic': 回答的逻辑线——为什么这样说、先说什么后说什么、关键转折点在哪里（用2-3句说明）
4. 'pitfalls': 最常见翻车点（1-2个）

重要原则:
- 不同问题尽量用不同经历，避免所有题都举同一个项目
- 回答要像真人在说话，不是AI写论文
- 禁止说"我表现出了XX能力"——用事实和行为展示能力
- 如果经历和问题不直接匹配，教ta如何bridge

返回JSON: {{"intent":"...","answer":"...","logic":"...","pitfalls":["..."]}}"""
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role":"system","content":"你是面试辅导专家。只返回JSON。"},{"role":"user","content":prompt}],
            temperature=0.7, max_tokens=2048, response_format={"type":"json_object"}
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        return {"intent":"","answer":f"(生成失败:{e})","logic":"","pitfalls":[]}


def main():
    if not os.path.exists(INPUT):
        print(f"未找到 {INPUT}，先运行 question-filter")
        return

    with open(INPUT, encoding="utf-8") as f:
        questions = json.load(f)

    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("未配置 DEEPSEEK_API_KEY")
        return

    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    results = []
    used = []
    for i, q in enumerate(questions):
        used_str = ", ".join(used[-3:]) if used else "无"
        print(f"[{i+1}/{len(questions)}] {q['question'][:50]}...")
        ai = gen_answer(q["question"], client, used_str)
        # 记录这次用了什么经历（从答案里提取关键词）
        answer_text = ai.get("answer", "")
        for keyword in ["高德", "Soul", "ICAN", "会员", "冷启动", "智慧养殖"]:
            if keyword in answer_text and keyword not in used:
                used.append(keyword)
        results.append({**q, **ai})

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ {len(results)} 题 → {OUTPUT}")


if __name__ == "__main__":
    main()

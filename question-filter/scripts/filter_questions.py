"""面试题筛选 — 正则初筛 + DeepSeek AI 精筛"""
import json, re, os, sys
from dotenv import load_dotenv

# 加载 API Key
_env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')
if os.path.exists(_env_path):
    load_dotenv(_env_path)
load_dotenv()


def is_valid_question_regex(text):
    """正则初筛：快速过滤明显非问题的文本"""
    t = text.strip()
    if len(t) < 12 or len(t) > 300:
        return False
    if re.search(r'[（(](已off|已offer|力竭版|踩坑版|附tl)[）)]', t):
        return False
    if re.search(r'\d{1,2}[:：]\d{2}', t):
        return False
    if t[-1] in '的在和了开对从与把被让给到为因随跟比' and len(t) < 30:
        return False
    if any(w in t[:10] for w in ['今天','内容','希望能','给大家','集美','offer','入职']):
        return False
    has_q = '？' in t or '?' in t
    has_qw = any(w in t for w in ['怎么','为什么','如何','什么是','能不能','会不会','请介绍','请描述','请说明','谈谈','聊聊','你认为','你怎么看','如何设计','如何评估','手撕','给定'])
    if not has_q and not has_qw:
        return False
    return True


def load_raw(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ai_filter(questions, company, position, stage):
    """DeepSeek AI 精筛：保留与公司/岗位/阶段匹配的真实面试题"""
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("(无 DeepSeek Key，跳过 AI 筛选)")
        return questions

    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # 分批处理，每批 30 条
    batch_size = 30
    kept = []
    total = len(questions)

    for start in range(0, total, batch_size):
        batch = questions[start:start+batch_size]
        items_text = "\n".join([
            f"{i+1}. {q['question'][:120]}"
            for i, q in enumerate(batch)
        ])

        prompt = f"""你是面试题库筛选专家。从以下 {len(batch)} 条候选文本中，筛选出真正的面试题。

目标公司: {company}
目标岗位: {position}
面试阶段: {stage}

筛选规则:
1. 必须是面试官会问的问题（不是闲聊、不是标题、不是个人感想）
2. 看内容是否和{company}、{position}相关（无关公司的直接排除）
3. 看难度是否适合{stage}（一面侧重项目经验+基础，二面侧重技术深度，HR面侧重软素质）
4. 排除：纯算法题（手撕）、offer相关讨论、入职体验、薪资讨论、公司吐槽

候选文本:
{items_text}

返回JSON，列出保留的序号（从1开始）:
{{"keep": [1, 3, 5, ...], "reason": "简短说明筛选逻辑"}}"""

        try:
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role":"system","content":"你是面试题库专家。只返回JSON。"},{"role":"user","content":prompt}],
                temperature=0.3, max_tokens=2048, response_format={"type":"json_object"}
            )
            result = json.loads(resp.choices[0].message.content)
            keep_indices = result.get("keep", [])
            for idx in keep_indices:
                if 1 <= idx <= len(batch):
                    kept.append(batch[idx-1])
            print(f"  批次 {start//batch_size+1}: {len(keep_indices)}/{len(batch)} 保留")
        except Exception as e:
            print(f"  AI筛选失败: {e}, 保留整批")
            kept.extend(batch)

    print(f"AI筛选: {len(kept)}/{total} 题保留")
    return kept


def merge_dedupe(qs):
    seen = set()
    unique = []
    for q in qs:
        key = q["question"][:25]
        if key not in seen:
            seen.add(key)
            unique.append(q)
    return unique


def filter_all(company=None, position=None, stage=None, use_ai=True):
    qs = []
    qs.extend(load_raw("niuke_raw.json"))
    qs.extend(load_raw("xhs_raw.json"))
    qs.extend(load_raw("ocr_text.json"))

    if not qs:
        print("未找到任何数据文件 (niuke_raw.json / xhs_raw.json / ocr_text.json)")
        return

    # 正则初筛
    qs = [q for q in qs if is_valid_question_regex(q.get("question", q.get("text", "")))]
    print(f"正则初筛: {len(qs)} 条")

    # AI 精筛
    if use_ai and company:
        qs = ai_filter(qs, company, position or "", stage or "")
    else:
        print("跳过 AI 筛选")

    # 去重
    qs = merge_dedupe(qs)
    print(f"去重后: {len(qs)} 条")

    with open("filtered_questions.json", "w", encoding="utf-8") as f:
        json.dump(qs, f, ensure_ascii=False, indent=2)

    nk = sum(1 for q in qs if q.get("source") == "牛客")
    xhs = sum(1 for q in qs if q.get("source") == "小红书")
    print(f"完成: {len(qs)} 题 (牛客{nk}+小红书{xhs}) -> filtered_questions.json")


if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else None
    position = sys.argv[2] if len(sys.argv) > 2 else None
    stage = sys.argv[3] if len(sys.argv) > 3 else None
    filter_all(company, position, stage)

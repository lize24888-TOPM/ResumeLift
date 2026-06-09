"""一键生成：公司+岗位+阶段 → 独立HTML备考包（无需后端，直接分享）"""
import json, os, sys
from datetime import datetime

SKILLS = os.path.dirname(__file__)


def build(company, position, stage):
    print(f"生成: {company} {position} {stage}")

    # 1. 牛客预设
    import subprocess
    subprocess.run([
        "python", f"{SKILLS}/niuke-crawler/scripts/crawl_niuke.py",
        company, position, stage
    ], cwd=SKILLS, capture_output=True)

    # 2. AI 筛选
    subprocess.run([
        "python", f"{SKILLS}/question-filter/scripts/filter_questions.py",
        company, position, stage
    ], cwd=SKILLS, capture_output=True)

    # 3. 读数据
    try:
        with open(f"{SKILLS}/filtered_questions.json", encoding="utf-8") as f:
            questions = json.load(f)
    except:
        questions = []

    if not questions:
        print("未找到题目，检查 SKILL 管线")
        return

    # 4. 生成 HTML
    title = f"{company} · {position} · {stage}"
    date = datetime.now().strftime("%Y-%m-%d")

    q_html = ""
    for i, q in enumerate(questions):
        src = q.get("source", "牛客")
        sc = "src-niuke" if src != "小红书" else "src-xhs"
        q_html += f'<div class="q-item"><div class="q-text"><span class="q-num">{i+1}</span>{q["question"]}</div><div class="q-meta"><span class="source-tag {sc}">{src}</span></div></div>\n'

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} - ResumeLift</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC',sans-serif;background:#f8f9fb;color:#1e293b}}
.hero{{background:linear-gradient(135deg,#6366f1,#a855f7);color:#fff;padding:32px;text-align:center}}
.hero h1{{font-size:1.6rem;font-weight:700}}
.hero p{{opacity:.85;margin-top:8px;font-size:.95rem}}
.container{{max-width:780px;margin:0 auto;padding:24px}}
.card{{background:#fff;border-radius:16px;padding:24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.card h3{{font-size:1rem;margin-bottom:16px}}
.q-item{{padding:14px 0;border-bottom:1px solid #f1f5f9}}
.q-item:last-child{{border-bottom:none}}
.q-num{{display:inline-block;background:#eef2ff;color:#4f46e5;width:26px;height:26px;border-radius:8px;text-align:center;line-height:26px;font-size:.8rem;font-weight:700;margin-right:8px}}
.q-text{{font-size:.95rem;font-weight:500}}
.q-meta{{font-size:.75rem;color:#94a3b8;margin-top:4px}}
.source-tag{{padding:2px 8px;border-radius:6px;font-size:.7rem;font-weight:600;margin-right:6px}}
.src-niuke{{background:#ecfdf5;color:#059669}}
.src-xhs{{background:#fdf2f8;color:#db2777}}
.footer{{text-align:center;padding:32px;color:#94a3b8;font-size:.8rem}}
@media print{{body{{background:#fff}}.hero{{background:#6366f1!important;-webkit-print-color-adjust:exact}}.card{{box-shadow:none;border:1px solid #e2e8f0}}}}
</style>
</head>
<body>
<div class="hero">
  <h1>{title}</h1>
  <p>{len(questions)} 题 · 牛客+小红书 · {date}</p>
</div>
<div class="container">
  <div class="card"><h3>面经题目列表</h3>
{q_html}
  </div>
</div>
<div class="footer">由 ResumeLift 生成 · 可打印/分享 · 数据来源公开面经帖</div>
</body></html>'''

    out = f"备考包_{company}_{position}_{stage}.html".replace(" ", "_")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Done: {len(questions)} 题 → {os.path.abspath(out)}")
    print("双击打开即可查看，无需后端！")


if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else "蚂蚁集团"
    position = sys.argv[2] if len(sys.argv) > 2 else "商业产品经理"
    stage = sys.argv[3] if len(sys.argv) > 3 else "业务面"
    build(company, position, stage)

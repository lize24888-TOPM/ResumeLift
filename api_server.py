"""轻量 Flask API — 接前端，调 SKILL 管线"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess, json, os

app = Flask(__name__)
CORS(app)

SKILLS_DIR = os.path.dirname(__file__)


@app.route("/api/extract", methods=["POST"])
def extract():
    """面经提取: 公司+岗位+阶段 → 题库"""
    data = request.get_json()
    company = data.get("company", "")
    position = data.get("position", "")
    stage = data.get("stage", "一面")

    if not position:
        return jsonify({"error": "岗位不能为空"}), 400

    # 直接走预设题库 + AI筛选
    try:
        result = subprocess.run([
            "python", f"{SKILLS_DIR}/niuke-crawler/scripts/crawl_niuke.py",
            company, position, stage
        ], cwd=SKILLS_DIR, capture_output=True, text=True, timeout=30)
        print("Niuke:", result.stdout[-200:] if result.stdout else "done")
    except Exception as e:
        print(f"Niuke error: {e}")

    try:
        result = subprocess.run([
            "python", f"{SKILLS_DIR}/question-filter/scripts/filter_questions.py",
            company, position, stage
        ], cwd=SKILLS_DIR, capture_output=True, text=True, timeout=60)
        print("Filter:", result.stdout[-200:] if result.stdout else "done")
    except Exception as e:
        print(f"Filter error: {e}")

    questions = []
    for path in [f"{SKILLS_DIR}/filtered_questions.json", f"{SKILLS_DIR}/niuke_raw.json"]:
        try:
            with open(path, encoding="utf-8") as f:
                questions = json.load(f)
                break
        except:
            pass

    return jsonify({
        "company": company,
        "position": position,
        "stage": stage,
        "questions": questions,
        "total": len(questions),
        "powered_by": "SKILL pipeline",
    })


@app.route("/api/extract/export", methods=["POST"])
def export():
    """导出 Word"""
    data = request.get_json()
    resume = data.get("resume_text", "")
    jd = data.get("jd_text", "")
    questions = data.get("questions", [])

    # 保存 filtered_questions
    with open(f"{SKILLS_DIR}/filtered_questions.json", "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False)

    # 生成答案
    env = os.environ.copy()
    env["RESUME_TEXT"] = resume[:500]
    env["JD_TEXT"] = jd[:500]
    subprocess.run([
        "python", f"{SKILLS_DIR}/interview-answer/scripts/generate_answers.py",
    ], cwd=SKILLS_DIR, env=env, capture_output=True)

    # 导出Word
    subprocess.run([
        "python", f"{SKILLS_DIR}/resume-optimizer/scripts/export_docs.py",
    ], cwd=SKILLS_DIR, capture_output=True)

    word_path = f"{SKILLS_DIR}/面试备考包.docx"
    if os.path.exists(word_path):
        return send_file(word_path, as_attachment=True, download_name="面试备考包.docx")

    return jsonify({"error": "导出失败"}), 500


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "version": "skill-pipeline"})


if __name__ == "__main__":
    print("SKILL API: http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)

<div align="center">
<img src="https://img.shields.io/badge/status-active-success?style=flat-square" alt="Status">
<img src="https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python" alt="Python">
<img src="https://img.shields.io/badge/DeepSeek-AI-4f46e5?style=flat-square" alt="DeepSeek">
<img src="https://img.shields.io/badge/license-Proprietary-red?style=flat-square" alt="License">
<br>
<h1>ResumeLift</h1>
<h3>简历驱动的 AI 面试备考引擎</h3>
</div>

---

## 这是什么

面试官按**简历**问，不是按题库目录问。ResumeLift 从牛客和小红书抓取真实面经，结合你的简历经历和岗位 JD，生成个性化的面试备考包——包含面试题、参考答案、面试官意图和翻车点。

**不是通用题库，只练面试官会追问你的题。**

## 与同类工具的区别

| | InterviewRadar | ResumeLift |
|---|:---:|:---:|
| 搜索方式 | 模糊岗位方向泛搜 | **公司+岗位+面试阶段精确匹配** |
| 小红书 | MediaCrawler（常被墙） | **Playwright 真浏览器扫码+原图 OCR** |
| 阶段感知 | 无 | **业务面/一面/二面/三面/HR面分别出题** |
| 答案生成 | 无 | **AI 生成参考答案+逻辑线+翻车点** |
| 题目筛选 | 时间过滤 | **正则初筛+DeepSeek AI 精筛** |

## 快速开始

```bash
git clone https://github.com/lize24888-TOPM/ResumeLift.git
cd ResumeLift
pip install -r requirements.txt

# 一键生成备考包 HTML
python build_html.py "蚂蚁集团" "商业产品经理" "业务面"
```

双击生成的 HTML 文件即可查看，无需后端。

## SKILL 流水线

```
公司 + 岗位 + 面试阶段
        │
        ▼
┌──────────────────┐
│  xhs-crawler     │  Playwright 扫码登录 → 拦截搜索 API → 获取笔记列表
│  niuke-crawler   │  预设题库(秒出) + 实时爬取(扫码)
└──────┬───────────┘
       │ xhs_raw.json / niuke_raw.json
       ▼
┌──────────────────┐
│  image-to-text   │  EasyOCR 识别笔记图片中的面试题
└──────┬───────────┘
       │ ocr_text.json
       ▼
┌──────────────────┐
│  question-filter │  正则初筛 → DeepSeek AI 精筛（按公司/阶段匹配）
└──────┬───────────┘
       │ filtered_questions.json
       ▼
┌──────────────────┐
│ interview-answer │  DeepSeek 生成参考答案 + 意图分析 + 逻辑线 + 翻车点
└──────┬───────────┘
       │ answered_questions.json
       ▼
┌──────────────────┐
│ resume-optimizer │  导出 HTML / Word / Markdown
└──────────────────┘
```

## 项目结构

```
skills/
├── build_html.py              # 一键生成：输入公司岗位阶段 → 输出 HTML
├── api_server.py              # Flask API（供前端 index.html 调用）
├── index.html                 # Web 前端界面
├── requirements.txt
│
├── xhs-crawler/               # SKILL 01: 小红书面经搜索
│   ├── SKILL.md
│   ├── references/            # XHS-Downloader 配置指南
│   └── scripts/crawl_xhs.py
│
├── niuke-crawler/             # SKILL 02: 牛客面经题库
│   ├── SKILL.md
│   └── scripts/
│       ├── crawl_niuke.py     # 预设模式（秒出）
│       └── crawl_niuke_live.py # 实时爬取
│
├── image-to-text/             # SKILL 03: OCR 图片转文字
│   ├── SKILL.md
│   └── scripts/ocr_images.py
│
├── question-filter/           # SKILL 04: AI 智能筛选
│   ├── SKILL.md
│   └── scripts/filter_questions.py
│
├── interview-answer/          # SKILL 05: AI 生成答案
│   ├── SKILL.md
│   └── scripts/generate_answers.py
│
└── resume-optimizer/          # SKILL 06: 文档导出
    ├── SKILL.md
    └── scripts/export_docs.py
```

## 配置

创建 `.env` 文件：
```bash
DEEPSEEK_API_KEY=sk-xxx     # DeepSeek API Key（必需）
```

## 常见问题

<details>
<summary>小红书爬取失败？</summary>
小红书有反爬机制。API 拦截模式可获取笔记标题列表；深爬（点进笔记）可能被拦截。备选方案：配置 XHS-Downloader 工具的 Cookie。
</details>

<details>
<summary>牛客没有我的岗位？</summary>
支持模糊匹配，未命中自动回退通用题库。也可用 `crawl_niuke_live.py` 实时爬取。
</details>

<details>
<summary>如何部署给别人用？</summary>
1. `python api_server.py` 启动后端
2. 双击 `index.html` 打开前端
3. 同网络下其他人也能访问（或部署到服务器）
</details>

## 路线图

- [x] 牛客预设题库
- [x] 小红书 API 拦截
- [x] OCR 图片识别
- [x] AI 智能筛选
- [x] AI 答案生成
- [x] HTML/Word 导出
- [ ] 小红书深爬（反反爬）
- [ ] 面试复盘模块
- [ ] 自我介绍生成
- [ ] 会员系统

---

<div align="center">
<sub>Created with ❤️ for job seekers | Proprietary — All Rights Reserved</sub>
</div>

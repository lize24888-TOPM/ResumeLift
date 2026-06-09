# ResumeLift — AI 面试备考 SKILL 套装

7 个独立 SKILL，按流水线串联，输入公司+岗位+阶段，输出面试备考包（HTML/Word/Markdown）。

## 快速开始

```bash
# 一键生成
python build_html.py "蚂蚁集团" "商业产品经理" "业务面"
# → 备考包_蚂蚁集团_商业产品经理_业务面.html（双击打开，可分享）
```

## SKILL 流水线

```
公司+岗位+阶段
    ↓
[01] xhs-crawler       小红书搜索（Playwright 扫码）
[02] niuke-crawler      牛客题库（预设+实时）
    ↓
[03] image-to-text      图片OCR转文字（EasyOCR）
    ↓
[04] question-filter    正则初筛 + DeepSeek AI精筛
    ↓
[05] interview-answer   AI生成参考答案（DeepSeek）
    ↓
[06] resume-optimizer   简历匹配优化
    ↓
[07] exporter           导出 HTML / Word / Markdown
```

## 安装

```bash
git clone https://github.com/你的用户名/ResumeLift.git
cd ResumeLift/skills
pip install -r requirements.txt
```

## 各 SKILL 详情

| # | SKILL | 输入 | 输出 | 依赖 |
|---|-------|------|------|------|
| 01 | `xhs-crawler` | 搜索关键词 | `xhs_raw.json` | Playwright |
| 02 | `niuke-crawler` | 公司 岗位 阶段 | `niuke_raw.json` | 预设题库 |
| 03 | `image-to-text` | `xhs_images/` | `ocr_text.json` | EasyOCR |
| 04 | `question-filter` | raw数据+公司岗位阶段 | `filtered_questions.json` | DeepSeek API |
| 05 | `interview-answer` | 题目+简历+JD | `answered_questions.json` | DeepSeek API |
| 06 | `resume-optimizer` | 答案+简历 | `面试备考包.docx/.md` | python-docx |

## 环境变量

创建 `.env` 文件：
```bash
DEEPSEEK_API_KEY=sk-xxx
RESUME_TEXT=你的简历文本
JD_TEXT=目标岗位JD
```

## 常见问题

**Q: 小红书爬取失败？**
A: 小红书有反爬，推荐用 XHS-Downloader 工具替代。参考 `xhs-crawler/references/`。

**Q: 牛客没有我的岗位？**
A: `niuke-crawler` 支持模糊匹配，未命中自动回退通用题库。也可以跑 `crawl_niuke_live.py` 实时爬取。

**Q: 如何部署给别人用？**
A: `python api_server.py` 启动后端，双击 `index.html` 即可使用。

## 许可证

MIT

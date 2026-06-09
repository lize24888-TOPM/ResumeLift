"""牛客实时爬取 v3 — 直接请求面试板块+解析"""
import json, sys, time, re
from playwright.sync_api import sync_playwright


def scrape(keyword, max_posts=20):
    seen = set()
    all_qs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 直接进面试经验板块（不需要搜索）
        print("🔍 进入牛客面试经验板块...")
        page.goto("https://www.nowcoder.com/discuss/tag/725", timeout=30000, wait_until="domcontentloaded")
        time.sleep(5)

        # 手动登录
        print("请在Chrome中扫码登录，登录后按Enter继续...")
        input()
        time.sleep(3)

        # 用搜索框搜索
        print(f"🔍 搜索: {keyword}")
        # 找搜索框并输入
        try:
            search_input = page.locator('input[placeholder*="搜索"]').first
            if search_input.is_visible():
                search_input.fill(keyword)
                search_input.press("Enter")
                print("   搜索框中搜索...")
                time.sleep(5)
        except:
            pass

        # 如果在搜索页，直接用URL搜
        if "search" not in page.url:
            encoded = keyword.replace(" ", "%20")
            page.goto(f"https://www.nowcoder.com/search?type=post&query={encoded}", timeout=30000)
            time.sleep(5)

        # 点击加载更多
        print("📜 点击加载更多...")
        for i in range(15):
            page.mouse.wheel(0, 800)
            time.sleep(1.5)
            # 点击加载更多按钮
            btns = page.locator('text=加载更多, text=查看更多, text=点击加载').all()
            for btn in btns:
                try:
                    if btn.is_visible():
                        btn.click()
                        time.sleep(1.5)
                except:
                    pass

        # 获取所有链接
        html = page.content()

        # 试试解析 JSON 数据（牛客经常把数据内嵌在 <script> 标签里）
        json_data = re.findall(r'window\.__INITIAL_STATE__\s*=\s*({.+?});\s*</script>', html, re.DOTALL)
        print(f"   找到 {len(json_data)} 个数据块")

        # 直接从链接提取
        links = re.findall(r'/discuss/(\d+)', html)
        for pid in links:
            if pid not in seen:
                seen.add(pid)

        print(f"   找到 {len(seen)} 个帖子")

        # 打开帖子
        ids = list(seen)[:max_posts]
        for i, pid in enumerate(ids):
            try:
                url = f"https://www.nowcoder.com/discuss/{pid}"
                page.goto(url, timeout=15000, wait_until="domcontentloaded")
                time.sleep(2)
                text = page.inner_text("body")

                for line in text.split('\n'):
                    line = line.strip()
                    if len(line) < 15 or len(line) > 300:
                        continue
                    has_q = '？' in line or '?' in line
                    is_numbered = bool(re.match(r'^[Q\d]+[\.、）\)\.]\s*.{10,}', line))
                    if has_q or is_numbered:
                        clean = re.sub(r'^[\dQq]+[\.、）\)\.:\s]+', '', line).strip()
                        if len(clean) > 10:
                            all_qs.append({
                                "question": clean[:200],
                                "source": "牛客",
                                "post_url": url,
                            })
                print(f"   [{i+1}/{len(ids)}] /discuss/{pid} ({sum(1 for q in all_qs if q['post_url']==url)} 题)")
            except Exception as e:
                print(f"   [{i+1}] 失败: {e}")

        browser.close()

    # 去重
    seen_q = set()
    unique = []
    for q in all_qs:
        key = q["question"][:25]
        if key not in seen_q:
            seen_q.add(key)
            unique.append(q)

    out = "niuke_raw.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"\n✅ {len(unique)} 题 → {out}")


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "商业产品经理 面经"
    scrape(kw)

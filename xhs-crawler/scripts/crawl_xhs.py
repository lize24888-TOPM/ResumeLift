"""
SKILL 01: 小红书爬取
输入: 搜索关键词
输出: xhs_raw.json — 笔记列表(title, desc, author, images, url)
"""
import json, sys, time, os, random
from pathlib import Path
from playwright.sync_api import sync_playwright
import requests

OUTPUT = "xhs_raw.json"
IMG_DIR = Path("xhs_images")
IMG_DIR.mkdir(exist_ok=True)


def scrape(keyword, max_notes=30):
    notes = []
    seen = set()

    def on_response(resp):
        try:
            url = resp.url
            if '/api/sns/web/v1/search/notes' in url or '/api/sns/web/v1/worldcup/search' in url:
                data = resp.json()
                items = data.get("data", {}).get("items", [])
                if items:
                    for item in items:
                        nid = item.get("id", "")
                        if nid and nid not in seen:
                            seen.add(nid)
                            nc = item.get("note_card", {})
                            imgs = nc.get("image_list", [])
                            notes.append({
                                "id": nid,
                                "title": nc.get("display_title", ""),
                                "desc": nc.get("desc", ""),
                                "author": nc.get("user", {}).get("nickname", ""),
                                "likes": nc.get("interact_info", {}).get("liked_count", ""),
                                "url": f"https://www.xiaohongshu.com/explore/{nid}",
                                "tags": [t.get("name", "") for t in nc.get("tag_list", [])],
                                "images": [i.get("url_default", i.get("url", "")) for i in imgs],
                            })
                    print(f"   +{len(items)} 条, 累计 {len(notes)} 条")
        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 先注册拦截，再导航
        page.on("response", on_response)

        # 日志：打印所有搜索相关请求
        def log_request(req):
            if 'search' in req.url.lower() or 'api/sns' in req.url:
                print(f"  🔗 {req.method} {req.url[:120]}")

        page.on("request", log_request)

        print(f"打开小红书搜索: {keyword}")
        page.goto(f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes",
                  timeout=60000, wait_until="domcontentloaded")
        print("等待页面加载...")
        time.sleep(8)
        print(f"当前URL: {page.url[:100]}")

        # 给足够时间手动登录
        print("请在Chrome中扫码登录，登录后按Enter继续...")
        input()

        print("滚动加载...")
        for i in range(15):
            page.mouse.wheel(0, 1000)
            time.sleep(2)
            if len(notes) >= max_notes:
                break

        # 点进每篇笔记（慢速，防反爬）
        print(f"\n📖 逐篇获取完整内容（共{len(notes)}篇, 间隔3-5秒）...")
        success = 0
        for idx, note in enumerate(notes[:20]):  # 最多20篇
            try:
                time.sleep(random.uniform(3, 5))  # 随机延迟
                page.goto(note["url"], timeout=20000, wait_until="domcontentloaded")
                time.sleep(2)

                # 检查是否被拦截
                if "笔记无法浏览" in page.inner_text("body") or "无法访问" in page.inner_text("body"):
                    print(f"   [{idx+1}] ⚠ 被拦截，跳过")
                    continue

                full_text = page.inner_text("body")
                note["full_text"] = full_text[:3000]

                real_images = []
                for img in page.locator("img").all():
                    try:
                        src = img.get_attribute("src")
                        if src and ("sns-webpic" in src or "xhscdn" in src or "ci.xiaohongshu" in src):
                            real_images.append(src)
                    except: pass
                note["real_images"] = real_images[:10]

                note_dir = IMG_DIR / note["id"]
                note_dir.mkdir(exist_ok=True)
                for j, url in enumerate(real_images[:5]):
                    try:
                        r = requests.get(url, headers={"Referer":"https://www.xiaohongshu.com/"}, timeout=10)
                        if r.status_code == 200 and len(r.content) > 500:
                            (note_dir / f"{j}.jpg").write_bytes(r.content)
                    except: pass

                success += 1
                print(f"   [{idx+1}/{min(len(notes),20)}] {note['title'][:40]}... ({len(full_text)}字, {len(real_images)}图)")
            except Exception as e:
                print(f"   [{idx+1}] 跳过: {e}")

        print(f"\n   成功获取 {success}/{min(len(notes),20)} 篇")
        browser.close()

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    print(f"完成: {len(notes)} 条 → {OUTPUT}")


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "AI产品经理 面经"
    scrape(kw)

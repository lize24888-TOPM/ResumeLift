"""
SKILL 01: 小红书爬取
输入: 搜索关键词
输出: xhs_raw.json — 笔记列表(title, desc, author, images, url)
"""
import json, sys, time, os
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
        url = resp.url
        if '/api/sns/web/v1/search/notes' in url:
            try:
                data = resp.json()
                items = data.get("data", {}).get("items", [])
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
        page.on("response", on_response)

        print(f"打开小红书搜索: {keyword}")
        page.goto(f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes",
                  timeout=30000)
        time.sleep(5)

        if "login" in page.url:
            print("请扫码登录 (120秒)")
            for i in range(120):
                time.sleep(1)
                if "login" not in page.url:
                    print("   已登录")
                    break

        print("滚动加载...")
        for i in range(15):
            page.mouse.wheel(0, 1000)
            time.sleep(2)
            if len(notes) >= max_notes:
                break

        # 下载图片
        print(f"下载图片...")
        for idx, note in enumerate(notes):
            note_dir = IMG_DIR / note["id"]
            note_dir.mkdir(exist_ok=True)
            for j, url in enumerate(note["images"]):
                if not url: continue
                try:
                    r = requests.get(url, headers={"Referer": "https://www.xiaohongshu.com/"}, timeout=10)
                    if r.status_code == 200 and len(r.content) > 500:
                        (note_dir / f"{j}.jpg").write_bytes(r.content)
                except:
                    pass

        browser.close()

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    print(f"完成: {len(notes)} 条 → {OUTPUT}")


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "AI产品经理 面经"
    scrape(kw)

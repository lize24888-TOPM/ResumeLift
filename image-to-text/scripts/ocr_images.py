"""OCR 图片转文字 — 输入 xhs_images/，输出 ocr_text.json"""
import json, os, sys
from pathlib import Path
from PIL import Image
import numpy as np

IMG_DIR = Path("xhs_images")
OUTPUT = "ocr_text.json"


def ocr_all():
    print("加载 EasyOCR（首次需下载模型）...")
    import easyocr
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    print("就绪\n")

    results = []
    total_chars = 0
    dirs = [d for d in IMG_DIR.iterdir() if d.is_dir()]
    if not dirs:
        print("未找到 xhs_images/ 目录，先运行 xhs-crawler")
        return

    for i, note_dir in enumerate(sorted(dirs)):
        note_id = note_dir.name
        images = sorted(note_dir.glob("*.jpg"))
        if not images:
            continue

        ocr_texts = []
        for img_path in images:
            try:
                img = Image.open(str(img_path)).convert('RGB')
                img_np = np.array(img)
                ocr = reader.readtext(img_np)
                text = '\n'.join([t[1] for t in ocr if t[2] > 0.3])
                if text.strip():
                    ocr_texts.append(text)
                    total_chars += len(text)
            except Exception as e:
                print(f"  ⚠ {img_path.name}: {e}")

        results.append({
            "note_id": note_id,
            "image_count": len(images),
            "ocr_texts": ocr_texts,
            "merged": "\n".join(ocr_texts),
        })
        if (i+1) % 5 == 0:
            print(f"  [{i+1}/{len(dirs)}] {note_id[:16]}... {sum(len(t) for t in ocr_texts)}字")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    q_notes = sum(1 for r in results if r["ocr_texts"])
    print(f"\n✅ {q_notes}篇有文字 | {total_chars}字 → {OUTPUT}")


if __name__ == "__main__":
    ocr_all()

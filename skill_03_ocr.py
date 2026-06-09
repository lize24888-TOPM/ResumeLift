"""
SKILL 03: 图片转文字 (OCR)
输入: xhs_images/ 目录下的图片
输出: xhs_ocr.json — 每张图的识别文字
"""
import json, os
from pathlib import Path
from PIL import Image
import numpy as np

IMG_DIR = Path("xhs_images")


def ocr_all():
    print("加载 EasyOCR...")
    import easyocr
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)

    results = []
    for note_dir in sorted(IMG_DIR.iterdir()):
        if not note_dir.is_dir():
            continue
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
            except:
                pass

        results.append({
            "note_id": note_id,
            "ocr_texts": ocr_texts,
            "merged": "\n".join(ocr_texts),
        })
        print(f"  {note_id[:16]}: {len(ocr_texts)} 张图, {sum(len(t) for t in ocr_texts)} 字")

    with open("xhs_ocr.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"完成: {len(results)} 条 → xhs_ocr.json")


if __name__ == "__main__":
    ocr_all()

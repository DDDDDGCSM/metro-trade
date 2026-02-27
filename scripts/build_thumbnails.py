#!/usr/bin/env python3
"""
为商品列表生成缩略图，加快首屏加载。将 static/product-images/ 下的图片
缩成最大边长 400px 的缩略图，保存到 static/product-images/thumb/。
在项目根目录执行: pip install Pillow && python scripts/build_thumbnails.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "static" / "data" / "products.json"
IMAGES_DIR = ROOT / "static" / "product-images"
THUMB_DIR = IMAGES_DIR / "thumb"
MAX_SIZE = 400
QUALITY = 82

try:
    from PIL import Image
except ImportError:
    print("请先安装 Pillow: pip install Pillow")
    exit(1)


def make_thumb(src_path: Path, dest_path: Path) -> bool:
    try:
        img = Image.open(src_path)
        img = img.convert("RGB") if img.mode in ("RGBA", "P") else img
        w, h = img.size
        if w <= MAX_SIZE and h <= MAX_SIZE:
            img.save(dest_path, "JPEG", quality=QUALITY, optimize=True)
            return True
        if w >= h:
            nw, nh = MAX_SIZE, int(h * MAX_SIZE / w)
        else:
            nw, nh = int(w * MAX_SIZE / h), MAX_SIZE
        img = img.resize((nw, nh), Image.Resampling.LANCZOS)
        THUMB_DIR.mkdir(parents=True, exist_ok=True)
        img.save(dest_path, "JPEG", quality=QUALITY, optimize=True)
        return True
    except Exception as e:
        print(f"  Skip {src_path.name}: {e}")
        return False


def main():
    if not JSON_PATH.exists():
        print(f"Not found: {JSON_PATH}")
        return 1
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    products = data.get("products", [])
    seen = set()
    done = 0
    for p in products:
        img = (p.get("image") or "").strip()
        if not img or not img.startswith("/static/product-images/"):
            continue
        # /static/product-images/1.jpg -> 1.jpg
        name = img.split("/static/product-images/")[-1].lstrip("/")
        if not name or name.startswith("thumb/"):
            continue
        if name in seen:
            continue
        seen.add(name)
        src = IMAGES_DIR / name
        if not src.is_file():
            continue
        dest = (THUMB_DIR / name).with_suffix(".jpg")
        if dest.exists() and src.stat().st_mtime <= dest.stat().st_mtime:
            done += 1
            continue
        if make_thumb(src, dest):
            done += 1
    print(f"Done. Thumbnails in {THUMB_DIR} ({done} processed).")
    return 0


if __name__ == "__main__":
    exit(main())

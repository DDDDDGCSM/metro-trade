#!/usr/bin/env python3
"""
将 products.json 中的商品图片下载到本地 static/product-images/，
并改写 JSON 中的 image 为本地路径，避免外链失效。
在项目根目录执行: python scripts/download_product_images.py
"""
import json
import re
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "static" / "data" / "products.json"
IMAGES_DIR = ROOT / "static" / "product-images"


def get_extension(url, content_type):
    if content_type:
        if "png" in content_type:
            return ".png"
        if "gif" in content_type:
            return ".gif"
        if "webp" in content_type:
            return ".webp"
    if ".png" in url.lower():
        return ".png"
    if ".gif" in url.lower():
        return ".gif"
    if ".webp" in url.lower():
        return ".webp"
    return ".jpg"


def download_image(url, dest_path):
    req = Request(url, headers={"User-Agent": "MetroTrade/1.0"})
    with urlopen(req, timeout=15) as r:
        content_type = r.headers.get("Content-Type", "")
        data = r.read()
    ext = get_extension(url, content_type)
    path = dest_path.with_suffix(ext)
    path.write_bytes(data)
    return path


def main():
    if not JSON_PATH.exists():
        print(f"Not found: {JSON_PATH}")
        return 1
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    products = data.get("products", [])
    updated = 0
    failed = 0
    for p in products:
        pid = p.get("id")
        img = (p.get("image") or "").strip()
        if not img or not (img.startswith("http://") or img.startswith("https://")):
            continue
        existing = next(IMAGES_DIR.glob(f"{pid}.*"), None)
        if existing:
            p["image"] = f"/static/product-images/{existing.name}"
            updated += 1
            continue
        try:
            path = download_image(img, IMAGES_DIR / str(pid))
            p["image"] = f"/static/product-images/{path.name}"
            updated += 1
        except (URLError, HTTPError, OSError) as e:
            print(f"  Skip id={pid}: {e}")
            failed += 1
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Done. Updated {updated} image paths, {failed} failed.")
    return 0


if __name__ == "__main__":
    exit(main())

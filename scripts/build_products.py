#!/usr/bin/env python3
"""
从 地铁交易-供给.xlsx 生成 static/data/products.json，供 app 启动时加载。
在项目根目录执行: python scripts/build_products.py
"""
import json
import re
import os
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("pip install pandas openpyxl")
    raise

ROOT = Path(__file__).resolve().parent.parent
EXCEL_PATH = ROOT.parent / "地铁交易-供给.xlsx"
OUT_PATH = ROOT / "static" / "data" / "products.json"


def parse_metro_lines(cell):
    """从地铁列解析出线路标识列表，如 ['all'] 或 ['1','2','A']"""
    if pd.isna(cell) or str(cell).strip() == "":
        return ["all"]
    s = str(cell).replace("\xa0", " ").strip()
    if s.lower() == "all":
        return ["all"]
    # Línea 1, Línea 2, Línea A, Línea B, Línea 12 ...
    parts = re.findall(r"L[ií]nea\s*([A-Za-z0-9]+)", s, re.IGNORECASE)
    if not parts:
        return ["all"]
    return list(dict.fromkeys(parts))  # unique order preserved


def row_to_product(i, row):
    """Excel 一行 -> 一条 product 字典"""
    metro_raw = row.get("地铁", row.iloc[0])
    metro_lines = parse_metro_lines(metro_raw)
    price = row.get("价格", row.iloc[1])
    if pd.isna(price):
        price = ""
    else:
        price = str(int(price)) if isinstance(price, (int, float)) else str(price)
    copy_raw = row.get("文案", row.iloc[2])
    if pd.isna(copy_raw):
        title, description = "", ""
    else:
        copy_text = str(copy_raw).strip()
        if "\n" in copy_text:
            parts = copy_text.split("\n", 1)
            title = (parts[0] or "").strip()
            description = (parts[1] or "").strip()
        else:
            title = copy_text
            description = ""
    image = row.get("图片", row.iloc[3])
    image = "" if pd.isna(image) else str(image).strip()
    # 第五列：联系方式（主链接）
    col4 = row.iloc[4] if len(row) > 4 else None
    contact_link = "" if pd.isna(col4) else str(col4).strip()
    col5 = row.get("联系方式跳转链接", row.iloc[5] if len(row) > 5 else None)
    contact_link_2 = "" if pd.isna(col5) else str(col5).strip()
    return {
        "id": i + 1,
        "metro_lines": metro_lines,
        "price": price,
        "title": title,
        "description": description,
        "image": image,
        "contact_link": contact_link,
        "contact_link_2": contact_link_2 or contact_link,
    }


def main():
    if not EXCEL_PATH.exists():
        print(f"Excel not found: {EXCEL_PATH}")
        return 1
    df = pd.read_excel(EXCEL_PATH)
    products = []
    for i in range(len(df)):
        try:
            products.append(row_to_product(i, df.iloc[i]))
        except Exception as e:
            print(f"Row {i+1} error: {e}")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"products": products}, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(products)} products to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    exit(main())

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

# 优先使用你最新的 Excel（带 (1) 的文件），若不存在则回退到旧文件名
_EXCEL_CANDIDATES = [
    ROOT.parent / "地铁交易-供给 (1).xlsx",
    ROOT.parent / "地铁交易-供给.xlsx",
]
EXCEL_PATH = next((p for p in _EXCEL_CANDIDATES if p.exists()), _EXCEL_CANDIDATES[0])

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


def normalize_contact(value: str) -> str:
    """
    归一化联系方式：
    - 若是 http/https 开头，原样返回（已是完整链接）
    - 若是纯号码（可带 +、空格、-），自动转为 WhatsApp 链接：https://wa.me/号码
    - 其它情况（如用户名）直接返回原值
    """
    if not value:
        return ""
    s = str(value).strip()
    if s.lower().startswith(("http://", "https://")):
        return s
    # 只保留数字和前导 +
    num = re.sub(r"[^\d+]", "", s)
    # 简单判定为电话号码：至少 6 位数字
    digits = re.sub(r"\D", "", num)
    if len(digits) >= 6:
        return f"https://wa.me/{digits}"
    return s


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
    # 第五列：联系方式（主号码或链接）
    col4 = row.iloc[4] if len(row) > 4 else None
    contact_link_raw = "" if pd.isna(col4) else str(col4).strip()
    contact_link = normalize_contact(contact_link_raw)
    col5 = row.get("联系方式跳转链接", row.iloc[5] if len(row) > 5 else None)
    contact_link_2_raw = "" if pd.isna(col5) else str(col5).strip()
    contact_link_2 = normalize_contact(contact_link_2_raw)
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

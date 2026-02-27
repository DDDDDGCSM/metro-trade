#!/usr/bin/env python3
"""
重命名目录为英文，并更新所有代码引用
"""

import os
import shutil
from pathlib import Path
import re

# 目录映射
OLD_DIR = '墨西哥书'
NEW_DIR = 'libros-mexico'

def rename_directory():
    """重命名目录"""
    static_dir = Path(__file__).parent / 'static'
    old_path = static_dir / OLD_DIR
    new_path = static_dir / NEW_DIR
    
    print("=" * 60)
    print("📁 重命名目录")
    print("=" * 60)
    
    if not old_path.exists():
        print(f"⚠️  目录不存在: {old_path}")
        return False
    
    try:
        shutil.move(str(old_path), str(new_path))
        print(f"✅ {OLD_DIR} → {NEW_DIR}")
        return True
    except Exception as e:
        print(f"❌ 重命名失败: {e}")
        return False

def update_html():
    """更新HTML文件中的路径"""
    html_file = Path(__file__).parent / 'templates' / 'index.html'
    
    print("\n" + "=" * 60)
    print("📝 更新HTML文件")
    print("=" * 60)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换所有路径
    old_pattern = f'/static/{OLD_DIR}/'
    new_pattern = f'/static/{NEW_DIR}/'
    
    count = content.count(old_pattern)
    content = content.replace(old_pattern, new_pattern)
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 共更新 {count} 处路径")
    return count > 0

def main():
    """主函数"""
    print("🚀 开始重命名目录并更新代码...\n")
    
    # 重命名目录
    dir_renamed = rename_directory()
    
    # 更新HTML
    html_updated = update_html()
    
    print("\n" + "=" * 60)
    if dir_renamed and html_updated:
        print("✅ 所有修改完成！")
        print("=" * 60)
        print(f"\n📋 目录结构：")
        print(f"   旧: static/{OLD_DIR}/")
        print(f"   新: static/{NEW_DIR}/")
        print(f"\n📋 路径格式：")
        print(f"   旧: /static/{OLD_DIR}/文件名")
        print(f"   新: /static/{NEW_DIR}/文件名")
    else:
        print("⚠️  部分修改未完成，请检查")
        print("=" * 60)

if __name__ == "__main__":
    main()


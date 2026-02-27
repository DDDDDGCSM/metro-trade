#!/usr/bin/env python3
"""
替换所有pravatar头像为本地SVG头像
"""

import re
import hashlib
import urllib.parse
from pathlib import Path

def generate_avatar_svg(name, size=150):
    """根据用户名生成SVG头像"""
    # 获取首字母
    words = name.split()
    if len(words) >= 2:
        initials = words[0][0].upper() + words[1][0].upper()
    elif len(words) == 1:
        initials = words[0][0].upper() + (words[0][1].upper() if len(words[0]) > 1 else words[0][0].upper())
    else:
        initials = 'U'
    
    # 根据名字生成颜色（确保一致性）
    hash_obj = hashlib.md5(name.encode())
    hash_hex = hash_obj.hexdigest()
    
    # 生成柔和的颜色
    r = int(hash_hex[0:2], 16) % 100 + 100  # 100-200
    g = int(hash_hex[2:4], 16) % 100 + 100
    b = int(hash_hex[4:6], 16) % 100 + 100
    
    bg_color = f"rgb({r}, {g}, {b})"
    text_color = "#FFFFFF"
    
    # 生成SVG
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <rect width="{size}" height="{size}" fill="{bg_color}" rx="{size//2}"/>
  <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="{size//3}" font-weight="bold" fill="{text_color}" text-anchor="middle" dominant-baseline="central">{initials}</text>
</svg>'''
    
    # 转换为data URI
    encoded = urllib.parse.quote(svg)
    return f"data:image/svg+xml,{encoded}"

def replace_avatars():
    """替换HTML中的所有pravatar头像"""
    html_file = Path(__file__).parent / 'templates' / 'index.html'
    
    print("=" * 60)
    print("🖼️  替换头像为本地SVG")
    print("=" * 60)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有用户数据
    pattern = r"user: \{ name: '([^']+)', avatar: '([^']+)'"
    matches = list(re.finditer(pattern, content))
    
    print(f"\n找到 {len(matches)} 个用户头像需要替换\n")
    
    # 从后往前替换，避免索引问题
    for match in reversed(matches):
        name = match.group(1)
        old_avatar = match.group(2)
        new_avatar = generate_avatar_svg(name)
        
        # 替换这一行的avatar
        start = match.start()
        end = match.end()
        before = content[:start]
        after = content[end:]
        middle = match.group(0).replace(old_avatar, new_avatar)
        
        content = before + middle + after
        
        print(f"✅ {name}: {old_avatar[:40]}... → SVG头像")
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 共替换 {len(matches)} 个头像")
    return len(matches)

if __name__ == "__main__":
    replace_avatars()


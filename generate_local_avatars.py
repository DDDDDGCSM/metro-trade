#!/usr/bin/env python3
"""
生成本地SVG头像，替代第三方头像服务
"""

from pathlib import Path
import hashlib

def generate_avatar_svg(name, size=150):
    """
    根据用户名生成SVG头像
    
    Args:
        name: 用户名
        size: 头像大小
    
    Returns:
        SVG字符串（data URI格式）
    """
    # 获取首字母
    initials = ''.join([word[0].upper() for word in name.split()[:2]])[:2]
    if not initials:
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
    import urllib.parse
    encoded = urllib.parse.quote(svg)
    return f"data:image/svg+xml,{encoded}"

def update_avatars_in_html():
    """更新HTML中的头像URL"""
    html_file = Path(__file__).parent / 'templates' / 'index.html'
    
    print("=" * 60)
    print("🖼️  生成本地头像")
    print("=" * 60)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有用户名
    import re
    user_matches = re.findall(r"user: \{ name: '([^']+)'", content)
    
    updated_count = 0
    for name in set(user_matches):
        # 生成头像
        avatar_svg = generate_avatar_svg(name)
        
        # 替换pravatar URL
        old_pattern = f"https://i.pravatar.cc/150\\?img=\\d+"
        # 查找这个用户的所有头像引用
        if f"name: '{name}'" in content:
            # 使用更精确的替换
            pattern = rf"(avatar: ')(https://i\.pravatar\.cc/150\?img=\d+)('.*?name: '{re.escape(name)}')"
            replacement = rf"\1{avatar_svg}\3"
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                updated_count += 1
                print(f"✅ {name}: {avatar_svg[:50]}...")
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 共更新 {updated_count} 个用户头像")
    return updated_count

if __name__ == "__main__":
    update_avatars_in_html()


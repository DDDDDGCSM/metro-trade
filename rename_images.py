#!/usr/bin/env python3
"""
重命名图片文件为英文，并更新所有代码引用
"""

import os
import shutil
from pathlib import Path

# 文件名映射（中文 -> 英文）
FILE_MAPPING = {
    # 原始文件名 -> 新文件名
    '佩德罗・帕拉莫.jpeg': 'pedro-paramo.jpeg',
    'Narrativa completa.png': 'narrativa-completa.png',
    'Narrativa completa.jpg': 'narrativa-completa.jpg',
    '阿尔特米奥·克罗斯之死.png': 'muerte-artemio-cruz.png',
    '爱情和其他魔鬼.png': 'amor-otros-demonios.png',
    '爱情和其他魔鬼.jpg': 'amor-otros-demonios.jpg',
    '百年孤独.png': 'cien-anos-soledad.png',
    '百年孤独.jpg': 'cien-anos-soledad.jpg',
    '野蛮侦探.png': 'detectives-salvajes.png',
    '假证件.png': 'papeles-falsos.png',
    '墨西哥的五个太阳.png': 'rituales-caos.png',
    '南方女王.png': 'reina-del-sur.png',
    '破角的春天.png': 'noche-tlatelolco.png',
    '沙之书.png': 'libro-arena.png',
    '太阳石.png': 'piedra-sol.png',
    '我的牙齿故事.png': 'historia-mis-dientes.png',
    '像水一样浓.png': 'agua-chocolate.png',
    '像水一样浓.jpg': 'agua-chocolate.jpg',
    '小王子.png': 'principito.png',
    '原子习惯.png': 'habitos-atomicos.png',
    '最明净的地区.png': 'region-transparente.png',
}

# HTML中的路径映射（需要更新的路径）
PATH_MAPPING = {
    '/static/墨西哥书/佩德罗・帕拉莫.jpeg': '/static/墨西哥书/pedro-paramo.jpeg',
    '/static/墨西哥书/Narrativa completa.png': '/static/墨西哥书/narrativa-completa.png',
    '/static/墨西哥书/Narrativa completa.jpg': '/static/墨西哥书/narrativa-completa.jpg',
    '/static/墨西哥书/阿尔特米奥·克罗斯之死.png': '/static/墨西哥书/muerte-artemio-cruz.png',
    '/static/墨西哥书/爱情和其他魔鬼.png': '/static/墨西哥书/amor-otros-demonios.png',
    '/static/墨西哥书/爱情和其他魔鬼.jpg': '/static/墨西哥书/amor-otros-demonios.jpg',
    '/static/墨西哥书/百年孤独.png': '/static/墨西哥书/cien-anos-soledad.png',
    '/static/墨西哥书/百年孤独.jpg': '/static/墨西哥书/cien-anos-soledad.jpg',
    '/static/墨西哥书/野蛮侦探.png': '/static/墨西哥书/detectives-salvajes.png',
    '/static/墨西哥书/假证件.png': '/static/墨西哥书/papeles-falsos.png',
    '/static/墨西哥书/墨西哥的五个太阳.png': '/static/墨西哥书/rituales-caos.png',
    '/static/墨西哥书/南方女王.png': '/static/墨西哥书/reina-del-sur.png',
    '/static/墨西哥书/破角的春天.png': '/static/墨西哥书/noche-tlatelolco.png',
    '/static/墨西哥书/沙之书.png': '/static/墨西哥书/libro-arena.png',
    '/static/墨西哥书/太阳石.png': '/static/墨西哥书/piedra-sol.png',
    '/static/墨西哥书/我的牙齿故事.png': '/static/墨西哥书/historia-mis-dientes.png',
    '/static/墨西哥书/像水一样浓.png': '/static/墨西哥书/agua-chocolate.png',
    '/static/墨西哥书/像水一样浓.jpg': '/static/墨西哥书/agua-chocolate.jpg',
    '/static/墨西哥书/小王子.png': '/static/墨西哥书/principito.png',
    '/static/墨西哥书/原子习惯.png': '/static/墨西哥书/habitos-atomicos.png',
    '/static/墨西哥书/最明净的地区.png': '/static/墨西哥书/region-transparente.png',
}

def rename_files():
    """重命名文件"""
    static_dir = Path(__file__).parent / 'static' / '墨西哥书'
    
    print("=" * 60)
    print("📸 重命名图片文件")
    print("=" * 60)
    
    renamed_count = 0
    
    for old_name, new_name in FILE_MAPPING.items():
        old_path = static_dir / old_name
        new_path = static_dir / new_name
        
        if old_path.exists():
            try:
                shutil.move(str(old_path), str(new_path))
                print(f"✅ {old_name} → {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"❌ {old_name}: {e}")
        else:
            print(f"⚠️  文件不存在: {old_name}")
    
    print(f"\n✅ 共重命名 {renamed_count} 个文件")
    return renamed_count > 0

def update_html():
    """更新HTML文件中的路径"""
    html_file = Path(__file__).parent / 'templates' / 'index.html'
    
    print("\n" + "=" * 60)
    print("📝 更新HTML文件")
    print("=" * 60)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updated_count = 0
    for old_path, new_path in PATH_MAPPING.items():
        if old_path in content:
            content = content.replace(old_path, new_path)
            updated_count += 1
            print(f"✅ {old_path} → {new_path}")
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 共更新 {updated_count} 处路径")
    return updated_count > 0

def main():
    """主函数"""
    print("🚀 开始重命名图片文件并更新代码...\n")
    
    # 重命名文件
    files_renamed = rename_files()
    
    # 更新HTML
    html_updated = update_html()
    
    print("\n" + "=" * 60)
    if files_renamed and html_updated:
        print("✅ 所有修改完成！")
        print("=" * 60)
        print("\n📋 下一步：")
        print("  1. 检查文件重命名是否正确")
        print("  2. 检查HTML路径是否已更新")
        print("  3. 提交并推送到GitHub")
        print("  4. 等待Vercel自动部署")
    else:
        print("⚠️  部分修改未完成，请检查")
        print("=" * 60)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
压缩图片文件 - 优化大于300KB的图片
"""

from PIL import Image
import os
from pathlib import Path

def compress_image(input_path, output_path, max_size_kb=300, quality=85):
    """
    压缩图片
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        max_size_kb: 目标最大大小（KB）
        quality: JPEG质量（1-100）
    """
    try:
        img = Image.open(input_path)
        
        # 如果是RGBA模式，转换为RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # 获取原始大小
        original_size = os.path.getsize(input_path) / 1024
        
        # 如果已经是PNG，尝试转换为JPEG（通常更小）
        if input_path.suffix.lower() == '.png' and original_size > max_size_kb:
            output_path = output_path.with_suffix('.jpg')
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
        else:
            # 保持原格式，但优化
            if input_path.suffix.lower() == '.png':
                img.save(output_path, 'PNG', optimize=True)
            else:
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        new_size = os.path.getsize(output_path) / 1024
        reduction = ((original_size - new_size) / original_size) * 100
        
        print(f"  ✅ {input_path.name}")
        print(f"     原始: {original_size:.1f} KB → 压缩后: {new_size:.1f} KB (减少 {reduction:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ {input_path.name}: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("📸 图片压缩工具")
    print("=" * 60)
    
    image_dir = Path(__file__).parent / "static" / "墨西哥书"
    
    if not image_dir.exists():
        print(f"❌ 目录不存在: {image_dir}")
        return
    
    # 需要压缩的图片（>300KB）
    large_images = [
        "百年孤独.png",
        "像水一样浓.png",
        "Narrativa completa.png",
        "爱情和其他魔鬼.png"
    ]
    
    print(f"\n📁 图片目录: {image_dir}")
    print(f"\n🔍 查找需要压缩的图片...\n")
    
    compressed_count = 0
    
    for img_name in large_images:
        img_path = image_dir / img_name
        
        if not img_path.exists():
            print(f"⚠️  文件不存在: {img_name}")
            continue
        
        original_size = img_path.stat().st_size / 1024
        
        if original_size > 300:
            print(f"📦 压缩: {img_name} ({original_size:.1f} KB)")
            
            # 创建备份
            backup_path = img_path.with_suffix(img_path.suffix + '.backup')
            if not backup_path.exists():
                import shutil
                shutil.copy2(img_path, backup_path)
            
            # 压缩
            if compress_image(img_path, img_path, max_size_kb=300, quality=85):
                compressed_count += 1
            print()
        else:
            print(f"✅ {img_name}: {original_size:.1f} KB (无需压缩)\n")
    
    print("=" * 60)
    print(f"✅ 压缩完成！共处理 {compressed_count} 张图片")
    print("=" * 60)
    
    # 显示最终大小
    print("\n📊 最终图片大小：")
    for img_name in large_images:
        img_path = image_dir / img_name
        if img_path.exists():
            size = img_path.stat().st_size / 1024
            print(f"  {img_name}: {size:.1f} KB")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
清理与 bookforMX 项目无关的文件
只保留核心项目文件
"""
import os
import subprocess
from datetime import datetime

DIR = "/Users/a58/cursor/归档/OK 调研/bookforMX"

# 需要保留的核心文件
KEEP_FILES = {
    # 核心应用文件
    'app.py',
    'requirements.txt',
    'vercel.json',
    '.gitignore',
    'README.md',
    
    # 目录（整个目录保留）
    'static',
    'templates',
}

# 需要删除的文件模式（所有其他文件）
# 我们将列出所有文件，然后删除不在 KEEP_FILES 中的

def git(args):
    r = subprocess.run(['/usr/bin/git'] + args, cwd=DIR, capture_output=True, text=True, check=False)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def should_keep(filepath):
    """判断文件是否应该保留"""
    # 获取文件名（不含路径）
    filename = os.path.basename(filepath)
    
    # 如果是保留的文件，直接返回 True
    if filename in KEEP_FILES:
        return True
    
    # 如果在保留的目录中，返回 True
    for keep_dir in KEEP_FILES:
        if filepath.startswith(keep_dir + '/') or filepath.startswith(keep_dir + '\\'):
            return True
    
    # .git 目录永远保留
    if filepath.startswith('.git'):
        return True
    
    return False

print("🧹 开始清理无关文件...\n")

# 获取所有已跟踪的文件
stdout, _, _ = git(['ls-files'])
all_files = [f.strip() for f in stdout.split('\n') if f.strip()]

# 分类文件
files_to_keep = []
files_to_remove = []

for filepath in all_files:
    if should_keep(filepath):
        files_to_keep.append(filepath)
    else:
        files_to_remove.append(filepath)

print(f"📊 文件统计：")
print(f"   - 保留: {len(files_to_keep)} 个文件")
print(f"   - 删除: {len(files_to_remove)} 个文件")
print()

if files_to_remove:
    print("🗑️  将删除以下文件：")
    for f in files_to_remove[:20]:  # 只显示前20个
        print(f"   - {f}")
    if len(files_to_remove) > 20:
        print(f"   ... 还有 {len(files_to_remove) - 20} 个文件")
    print()
    
    # 从 Git 中删除文件
    print("📋 从 Git 中删除文件...")
    for f in files_to_remove:
        git(['rm', '--cached', f])
    
    # 删除物理文件
    print("📋 删除物理文件...")
    for f in files_to_remove:
        full_path = os.path.join(DIR, f)
        try:
            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    import shutil
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
        except Exception as e:
            print(f"   ⚠️  无法删除 {f}: {e}")
    
    print("✅ 文件删除完成")
else:
    print("✅ 没有需要删除的文件")

print("\n📋 提交更改...")
msg = f"Clean: Remove non-project files - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
git(['add', '-A'])
_, stderr, code = git(['commit', '-m', msg])
if code == 0:
    print("✅ 已提交")
else:
    if 'nothing to commit' not in stderr.lower():
        print(f"⚠️  提交失败: {stderr[:100]}")

print("\n📊 清理完成！")
print(f"   - 保留文件: {len(files_to_keep)} 个")
print(f"   - 删除文件: {len(files_to_remove)} 个")


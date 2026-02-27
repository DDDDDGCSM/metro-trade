#!/usr/bin/env python3
"""
彻底清理：只保留 bookforMX 项目核心文件
"""
import os
import subprocess
from datetime import datetime

DIR = "/Users/a58/cursor/归档/OK 调研/bookforMX"

# 只保留这些核心文件
CORE_FILES = {
    'app.py',
    'requirements.txt',
    'vercel.json',
    '.gitignore',
    'README.md',
}

# 只保留这些目录
CORE_DIRS = {
    'static',
    'templates',
}

def git(args):
    r = subprocess.run(['/usr/bin/git'] + args, cwd=DIR, capture_output=True, text=True, check=False)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def is_core_file(filepath):
    """判断是否是核心文件"""
    filename = os.path.basename(filepath)
    
    # 核心文件
    if filename in CORE_FILES:
        return True
    
    # 核心目录中的文件
    for core_dir in CORE_DIRS:
        if filepath.startswith(core_dir + '/'):
            return True
    
    # .git 永远保留
    if filepath.startswith('.git'):
        return True
    
    return False

print("🧹 彻底清理无关文件...\n")

# 获取所有已跟踪的文件
stdout, _, _ = git(['ls-files'])
all_files = [f.strip() for f in stdout.split('\n') if f.strip()]

# 分类
files_to_remove = [f for f in all_files if not is_core_file(f)]

print(f"📊 文件统计：")
print(f"   - 总文件数: {len(all_files)}")
print(f"   - 将删除: {len(files_to_remove)} 个文件")
print(f"   - 将保留: {len(all_files) - len(files_to_remove)} 个文件")
print()

if files_to_remove:
    print("🗑️  删除文件列表：")
    for f in files_to_remove:
        print(f"   - {f}")
    print()
    
    # 从 Git 删除
    print("📋 从 Git 中删除...")
    for f in files_to_remove:
        git(['rm', '--cached', '-f', f])
    
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
            print(f"   ⚠️  {f}: {e}")
    
    print("✅ 删除完成")
    
    # 提交
    print("\n📋 提交更改...")
    git(['add', '-A'])
    msg = f"Clean: Remove all non-core files - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    _, stderr, code = git(['commit', '-m', msg])
    if code == 0:
        print("✅ 已提交")
    else:
        if 'nothing to commit' not in stderr.lower():
            print(f"⚠️  {stderr[:100]}")
else:
    print("✅ 没有需要删除的文件")

# 显示保留的文件
print("\n📋 保留的核心文件：")
stdout, _, _ = git(['ls-files'])
remaining = [f.strip() for f in stdout.split('\n') if f.strip()]
for f in sorted(remaining):
    print(f"   ✅ {f}")

print(f"\n✅ 清理完成！保留 {len(remaining)} 个核心文件")


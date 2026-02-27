#!/usr/bin/env python3
"""
BookForMX 智能自动部署脚本
- 自动检测更改
- 自动提交和推送
- 自动检查部署状态（可选）
"""
import subprocess
import os
import sys
import time
from datetime import datetime

DIR = "/Users/a58/cursor/归档/OK 调研/bookforMX"
USER = "DDDDDGCSM"
REPO = "bookforMX"
GITHUB_URL = f"https://github.com/{USER}/{REPO}.git"

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN') or (
    sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].startswith('ghp_') else None
)

def git(args):
    r = subprocess.run(['/usr/bin/git'] + args, cwd=DIR, capture_output=True, text=True, check=False)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def print_header():
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║      🤖 BookForMX 智能自动部署 🤖                           ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()

def check_changes():
    """检查是否有未提交的更改"""
    print("📋 步骤 1/4: 检查代码更改...")
    print("=" * 60)
    
    stdout, _, _ = git(['status', '--short'])
    changes = [l for l in stdout.split('\n') if l.strip()]
    
    if not changes:
        print("✅ 没有未提交的更改")
        return False
    
    print(f"📝 发现 {len(changes)} 个更改：")
    for change in changes[:10]:
        print(f"   {change}")
    if len(changes) > 10:
        print(f"   ... 还有 {len(changes) - 10} 个更改")
    
    return True

def commit_and_push(message=None):
    """提交并推送代码"""
    print("\n📋 步骤 2/4: 提交并推送代码...")
    print("=" * 60)
    
    if not GITHUB_TOKEN:
        print("⚠️  未提供 GitHub Token，无法推送")
        return False
    
    # 添加所有更改
    git(['add', '.'])
    print("✅ 已添加所有更改")
    
    # 提交
    if not message:
        message = f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    _, stderr, code = git(['commit', '-m', message])
    if code == 0:
        stdout, _, _ = git(['log', '-1', '--pretty=format:%h'])
        print(f"✅ 已提交 (ID: {stdout})")
    elif 'nothing to commit' not in stderr.lower():
        print(f"⚠️  提交失败: {stderr[:100]}")
        return False
    
    # 配置远程仓库
    url = f"https://{GITHUB_TOKEN}@github.com/{USER}/{REPO}.git"
    git(['remote', 'set-url', 'origin', url])
    
    # 推送
    print("🚀 正在推送到 GitHub...")
    stdout, stderr, code = git(['push', '-u', 'origin', 'main'])
    
    if code == 0:
        print("✅ 推送成功！")
        print(f"   GitHub: {GITHUB_URL}")
        return True
    else:
        print(f"⚠️  推送失败: {stderr[:200]}")
        return False

def show_deployment_info():
    """显示部署信息"""
    print("\n📋 步骤 3/4: 部署信息")
    print("=" * 60)
    print()
    print("🌐 Vercel 自动部署：")
    print("   - Vercel 会自动检测 GitHub 推送")
    print("   - 自动开始部署（通常 1-2 分钟）")
    print("   - 无需手动操作")
    print()
    print("📊 查看部署状态：")
    print("   - Vercel 控制台: https://vercel.com/jameswhites-projects-ef45e7ad/bookfor-mx")
    print("   - 部署链接: https://bookfor-mx.vercel.app")
    print()

def wait_for_deployment():
    """等待部署完成（可选）"""
    print("\n📋 步骤 4/4: 等待部署完成（可选）")
    print("=" * 60)
    print()
    print("⏳ 部署进行中...")
    print("   Vercel 通常需要 1-2 分钟完成部署")
    print("   您可以在 Vercel 控制台查看实时进度")
    print()
    print("💡 提示：")
    print("   - 部署完成后，网站会自动更新")
    print("   - 访问: https://bookfor-mx.vercel.app")
    print("   - 每次推送都会自动触发新部署")
    print()

def main():
    print_header()
    
    try:
        # 检查更改
        has_changes = check_changes()
        
        if not has_changes:
            print("\n💡 没有需要部署的更改")
            response = input("是否强制推送？（y/n）: ").strip().lower()
            if response != 'y':
                print("\n✅ 已取消")
                return
        
        # 获取提交信息
        commit_msg = None
        if len(sys.argv) > 2:
            commit_msg = sys.argv[2]
        elif has_changes:
            commit_msg = input("\n📝 请输入提交信息（直接回车使用默认）: ").strip()
            if not commit_msg:
                commit_msg = None
        
        # 提交并推送
        if commit_and_push(commit_msg):
            show_deployment_info()
            wait_for_deployment()
            
            print("\n╔═══════════════════════════════════════════════════════════════╗")
            print("║              ✅ 自动部署流程完成！                           ║")
            print("╚═══════════════════════════════════════════════════════════════╝")
            print()
            print("📦 GitHub: 代码已推送")
            print("🚀 Vercel: 自动部署中...")
            print("🌐 网站: https://bookfor-mx.vercel.app")
            print()
            print("💡 下次只需运行此脚本即可自动部署！")
        else:
            print("\n⚠️  部署流程未完成，请检查错误信息")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  部署已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


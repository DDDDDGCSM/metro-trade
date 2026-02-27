#!/usr/bin/env python3
"""
立即部署到 Vercel - 自动打开浏览器并引导部署
"""
import subprocess
import os
import sys
import webbrowser
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
    print("║         🚀 BookForMX 立即部署到 Vercel 🚀                   ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()

def ensure_github_updated():
    """确保 GitHub 代码是最新的"""
    print("📋 步骤 1/3: 确保 GitHub 代码最新...")
    print("=" * 60)
    
    if not GITHUB_TOKEN:
        print("⚠️  未提供 GitHub Token，跳过推送")
        return True
    
    git(['add', '.'])
    msg = f"Deploy: BookForMX - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    git(['commit', '-m', msg])
    
    url = f"https://{GITHUB_TOKEN}@github.com/{USER}/{REPO}.git"
    git(['remote', 'set-url', 'origin', url])
    
    stdout, stderr, code = git(['push', '-u', 'origin', 'main'])
    if code == 0:
        print("✅ GitHub 代码已更新")
        return True
    else:
        print(f"⚠️  GitHub 推送失败，但继续部署流程")
        return True

def open_vercel_deploy():
    """打开 Vercel 部署页面"""
    print("\n📋 步骤 2/3: 打开 Vercel 部署页面...")
    print("=" * 60)
    
    # Vercel 导入项目的直接链接
    vercel_url = "https://vercel.com/new"
    
    print(f"🌐 正在打开: {vercel_url}")
    print()
    print("📝 部署步骤（请在浏览器中完成）：")
    print()
    print("   1. 如果还没登录，使用 GitHub 登录")
    print("   2. 点击 'Import Git Repository'")
    print(f"   3. 搜索或选择: {REPO} 或 {USER}/{REPO}")
    print("   4. 点击 'Import'")
    print("   5. 保持所有默认设置（Vercel 会自动检测 Flask）")
    print("   6. 点击 'Deploy'")
    print("   7. 等待 1-2 分钟")
    print("   8. 看到 '🎉 Congratulations!' 表示成功")
    print("   9. 点击 'Visit' 获得部署链接")
    print()
    
    try:
        webbrowser.open(vercel_url)
        print("✅ 已自动打开浏览器")
        print()
        print("⏳ 等待您在浏览器中完成部署...")
        print("   完成后，您将获得类似这样的链接：")
        print("   https://bookformx.vercel.app")
        print()
    except Exception as e:
        print(f"⚠️  无法自动打开浏览器: {e}")
        print(f"   请手动访问: {vercel_url}")

def show_deployment_info():
    """显示部署信息"""
    print("\n📋 步骤 3/3: 部署信息")
    print("=" * 60)
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║              📦 部署信息                                       ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print(f"📦 GitHub 仓库: {GITHUB_URL}")
    print("🌐 Vercel 部署: https://vercel.com/new")
    print()
    print("💡 提示：")
    print("  - 部署通常需要 1-2 分钟")
    print("  - 部署完成后会获得访问链接")
    print("  - 链接格式: https://bookformx.vercel.app")
    print("  - 或: https://bookformx-[随机字符].vercel.app")
    print()
    print("📊 查看部署状态：")
    print("  - Vercel 控制台: https://vercel.com/dashboard")
    print("  - 选择项目: bookformx")
    print("  - 查看 'Deployments' 标签")
    print()

def main():
    print_header()
    
    try:
        ensure_github_updated()
        open_vercel_deploy()
        show_deployment_info()
        
        print("\n🎉 部署流程已启动！")
        print("   请在浏览器中完成 Vercel 部署，完成后即可获得访问链接。")
        print()
        
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


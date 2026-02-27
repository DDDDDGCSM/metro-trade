#!/usr/bin/env python3
"""
BookForMX 完全自动化部署脚本
包括 GitHub 推送和 Vercel 自动部署
"""
import subprocess
import os
import sys
import requests
import json
from datetime import datetime

# 项目配置
DIR = "/Users/a58/cursor/归档/OK 调研/bookforMX"
USER = "DDDDDGCSM"
REPO = "bookforMX"
GITHUB_URL = f"https://github.com/{USER}/{REPO}.git"

# 从环境变量或参数获取 Token
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN') or (
    sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].startswith('ghp_') else None
)
VERCEL_TOKEN = os.environ.get('VERCEL_TOKEN') or (
    sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].startswith('vercel_') else None
)

def git(args):
    """执行 Git 命令"""
    r = subprocess.run(['/usr/bin/git'] + args, cwd=DIR, capture_output=True, text=True, check=False)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def print_header():
    """打印标题"""
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║      🚀 BookForMX 完全自动化部署（GitHub + Vercel）🚀       ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()

def push_to_github():
    """推送到 GitHub"""
    print("📋 步骤 1/3: 推送到 GitHub...")
    print("=" * 60)
    
    if not GITHUB_TOKEN:
        print("⚠️  未提供 GitHub Token，跳过 GitHub 推送")
        return False
    
    # 添加文件
    git(['add', '.'])
    
    # 提交
    msg = f"Deploy: BookForMX - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    _, stderr, code = git(['commit', '-m', msg])
    if code != 0 and 'nothing to commit' not in stderr.lower():
        print(f"⚠️  提交失败: {stderr[:100]}")
    
    # 配置远程仓库（带认证）
    url = f"https://{GITHUB_TOKEN}@github.com/{USER}/{REPO}.git"
    git(['remote', 'set-url', 'origin', url])
    
    # 推送
    print("🚀 正在推送到 GitHub...")
    stdout, stderr, code = git(['push', '-u', 'origin', 'main'])
    
    if code == 0:
        print("✅ GitHub 推送成功！")
        print(f"   仓库: {GITHUB_URL}")
        return True
    else:
        print(f"⚠️  GitHub 推送失败: {stderr[:200]}")
        return False

def deploy_to_vercel():
    """使用 Vercel API 自动部署"""
    print("\n📋 步骤 2/3: 部署到 Vercel...")
    print("=" * 60)
    
    if not VERCEL_TOKEN:
        print("⚠️  未提供 Vercel Token，无法自动部署")
        print("\n💡 获取 Vercel Token：")
        print("   1. 访问: https://vercel.com/account/tokens")
        print("   2. 点击: 'Create Token'")
        print("   3. 输入名称: BookForMX Deploy")
        print("   4. 选择过期时间: 90 days")
        print("   5. 点击: 'Create'")
        print("   6. 复制 Token")
        print("\n使用方法:")
        print("   export VERCEL_TOKEN=your_token")
        print("   python3 完全自动部署.py github_token vercel_token")
        return False
    
    VERCEL_API = "https://api.vercel.com"
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json"
    }
    
    project_name = "bookformx"
    
    # 1. 检查项目是否存在
    print("🔍 检查 Vercel 项目...")
    response = requests.get(
        f"{VERCEL_API}/v9/projects/{project_name}",
        headers=headers
    )
    
    if response.status_code == 404:
        # 创建项目
        print("📦 创建 Vercel 项目...")
        data = {
            "name": project_name,
            "gitRepository": {
                "type": "github",
                "repo": f"{USER}/{REPO}"
            },
            "framework": None,
            "rootDirectory": None,
            "buildCommand": None,
            "outputDirectory": None,
            "installCommand": None,
        }
        
        response = requests.post(
            f"{VERCEL_API}/v10/projects",
            headers=headers,
            json=data
        )
        
        if response.status_code in [200, 201]:
            project = response.json()
            print(f"✅ 项目创建成功: {project.get('name')}")
        elif response.status_code == 409:
            print("ℹ️  项目已存在")
        else:
            print(f"⚠️  创建项目失败: {response.status_code}")
            print(f"   错误: {response.text[:200]}")
            return False
    elif response.status_code == 200:
        print("✅ 项目已存在")
    else:
        print(f"⚠️  检查项目失败: {response.status_code}")
        return False
    
    # 2. 触发部署
    print("\n🚀 触发部署...")
    data = {
        "name": project_name,
        "gitSource": {
            "type": "github",
            "repo": f"{USER}/{REPO}",
            "ref": "main"
        }
    }
    
    response = requests.post(
        f"{VERCEL_API}/v13/deployments",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        deployment = response.json()
        deployment_id = deployment.get('uid')
        url = deployment.get('url', 'N/A')
        
        print("✅ 部署已触发！")
        print(f"   部署 ID: {deployment_id}")
        print(f"   URL: https://{url}")
        print("\n⏳ 部署进行中（通常需要 1-2 分钟）...")
        print(f"   查看状态: https://vercel.com/dashboard")
        
        return True
    else:
        print(f"⚠️  触发部署失败: {response.status_code}")
        print(f"   错误: {response.text[:200]}")
        return False

def show_summary():
    """显示总结"""
    print("\n📋 步骤 3/3: 部署总结")
    print("=" * 60)
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║              ✅ 自动化部署完成！                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print(f"📦 GitHub: {GITHUB_URL}")
    print("🌐 Vercel: https://vercel.com/dashboard")
    print()
    print("💡 提示：")
    print("  - 部署通常需要 1-2 分钟完成")
    print("  - 可以在 Vercel 控制台查看实时日志")
    print("  - 部署完成后会获得访问链接")
    print()

def main():
    """主函数"""
    print_header()
    
    try:
        # 推送到 GitHub
        github_ok = push_to_github()
        
        # 部署到 Vercel
        if github_ok:
            vercel_ok = deploy_to_vercel()
            if vercel_ok:
                show_summary()
            else:
                print("\n⚠️  Vercel 自动部署失败，请手动部署：")
                print("   访问: https://vercel.com/new")
        else:
            print("\n⚠️  GitHub 推送失败，请检查后重试")
    
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


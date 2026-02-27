#!/usr/bin/env python3
"""
使用 Vercel API 自动部署 BookForMX
需要 Vercel Token（从 https://vercel.com/account/tokens 获取）
"""
import requests
import json
import os
import sys

# Vercel API 配置
VERCEL_API_URL = "https://api.vercel.com"
VERCEL_TOKEN = os.environ.get('VERCEL_TOKEN') or sys.argv[1] if len(sys.argv) > 1 else None

if not VERCEL_TOKEN:
    print("❌ 错误: 需要提供 Vercel Token")
    print("\n📋 获取 Token 的步骤：")
    print("   1. 访问: https://vercel.com/account/tokens")
    print("   2. 点击: 'Create Token'")
    print("   3. 输入名称: BookForMX Deploy")
    print("   4. 选择过期时间: 90 days")
    print("   5. 点击: 'Create'")
    print("   6. 复制 Token")
    print("\n使用方法:")
    print("   export VERCEL_TOKEN=your_token")
    print("   python3 自动部署到Vercel.py")
    print("\n或者:")
    print("   python3 自动部署到Vercel.py your_token")
    sys.exit(1)

# GitHub 仓库信息
GITHUB_REPO = "DDDDDGCSM/bookforMX"

headers = {
    "Authorization": f"Bearer {VERCEL_TOKEN}",
    "Content-Type": "application/json"
}

def create_project():
    """创建 Vercel 项目"""
    print("📋 步骤 1/3: 创建 Vercel 项目...")
    
    data = {
        "name": "bookformx",
        "gitRepository": {
            "type": "github",
            "repo": GITHUB_REPO
        },
        "framework": None,  # 让 Vercel 自动检测
        "rootDirectory": None,  # 使用根目录
        "buildCommand": None,  # 自动检测
        "outputDirectory": None,  # 自动检测
        "installCommand": None,  # 自动检测
    }
    
    try:
        response = requests.post(
            f"{VERCEL_API_URL}/v10/projects",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            project = response.json()
            print(f"✅ 项目创建成功: {project.get('name')}")
            return project
        elif response.status_code == 409:
            print("ℹ️  项目已存在，继续部署...")
            # 获取现有项目
            response = requests.get(
                f"{VERCEL_API_URL}/v9/projects/bookformx",
                headers=headers
            )
            if response.status_code == 200:
                return response.json()
        else:
            print(f"⚠️  创建项目失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def deploy_project(project_name):
    """部署项目"""
    print("\n📋 步骤 2/3: 触发部署...")
    
    try:
        response = requests.post(
            f"{VERCEL_API_URL}/v13/deployments",
            headers=headers,
            json={
                "name": project_name,
                "gitSource": {
                    "type": "github",
                    "repo": GITHUB_REPO,
                    "ref": "main"
                }
            }
        )
        
        if response.status_code == 200:
            deployment = response.json()
            print(f"✅ 部署已触发")
            print(f"   部署 ID: {deployment.get('uid')}")
            print(f"   URL: {deployment.get('url')}")
            return deployment
        else:
            print(f"⚠️  部署失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def get_deployment_status(deployment_id):
    """获取部署状态"""
    print("\n📋 步骤 3/3: 检查部署状态...")
    
    try:
        response = requests.get(
            f"{VERCEL_API_URL}/v13/deployments/{deployment_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            deployment = response.json()
            state = deployment.get('readyState', 'UNKNOWN')
            url = deployment.get('url', 'N/A')
            
            print(f"   状态: {state}")
            print(f"   URL: https://{url}")
            
            if state == 'READY':
                print("\n🎉 部署成功！")
                print(f"   访问: https://{url}")
            elif state == 'ERROR':
                print("\n❌ 部署失败")
                print("   请查看 Vercel 控制台的日志")
            else:
                print("\n⏳ 部署进行中...")
                print("   请稍后在 Vercel 控制台查看状态")
            
            return deployment
        else:
            print(f"⚠️  无法获取状态: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def main():
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║         🚀 BookForMX 自动部署到 Vercel 🚀                    ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print(f"📦 GitHub 仓库: {GITHUB_REPO}")
    print()
    
    # 创建项目
    project = create_project()
    if not project:
        print("\n❌ 无法创建项目，请检查：")
        print("   1. Vercel Token 是否正确")
        print("   2. GitHub 仓库是否存在")
        print("   3. Vercel 是否已连接 GitHub")
        sys.exit(1)
    
    project_name = project.get('name', 'bookformx')
    
    # 部署项目
    deployment = deploy_project(project_name)
    if not deployment:
        print("\n❌ 无法触发部署")
        sys.exit(1)
    
    deployment_id = deployment.get('uid')
    
    # 检查状态
    get_deployment_status(deployment_id)
    
    print("\n📝 提示：")
    print("   - 部署通常需要 1-2 分钟")
    print("   - 可以在 Vercel 控制台查看实时日志")
    print("   - 访问: https://vercel.com/dashboard")
    print()

if __name__ == "__main__":
    main()


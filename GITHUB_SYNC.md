# 同步到 GitHub 后会更方便

本地已执行：`git init`、`git add -A`、`git commit`，metro-trade 已是独立仓库。

## 你只需做两步

### 1. 在 GitHub 创建空仓库

已为你打开 **New repository** 页面（若未打开请访问 https://github.com/new）：

- **Repository name**：`metro-trade`（或你喜欢的名字）
- **Description**：可选，如 `Metro Trade - 地铁交易`
- **Public**，**不要**勾选 "Add a README"
- 点击 **Create repository**

### 2. 在终端执行（把 YOUR_USERNAME 换成你的 GitHub 用户名）

```bash
cd "/Users/a58/cursor/归档/OK 调研/metro-trade"
git remote add origin https://github.com/YOUR_USERNAME/metro-trade.git
git branch -M main
git push -u origin main
```

若用 SSH：`git remote add origin git@github.com:YOUR_USERNAME/metro-trade.git` 再 push。

---

## 同步到 GitHub 后的好处

1. **Vercel 连 GitHub**：在 Vercel 项目 metro-trade 里 Settings → Git，把 Git 仓库连到这个 GitHub 仓库，之后每次 `git push` 会自动部署，不用再跑 `vercel --prod`。
2. **环境变量在 Vercel 配一次**：在 Vercel 里填好 `DATABASE_URL`、`ADMIN_TOKEN` 等，每次自动部署都会带上。
3. **数据库**：在 Neon 官网创建一个项目，把连接串填到 Vercel 的 Environment Variables 即可，无需再认领 pg.new。

创建好仓库并 push 成功后，在 Vercel 里把该项目连到这个 GitHub 仓库即可实现「改代码 → push → 自动部署」。

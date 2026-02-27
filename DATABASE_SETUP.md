# 数据库设置指南（与 bookforME 相同流程）

**不要用 pg.new 认领**（会卡在 Claim 置灰）。按下面在 Neon 官网直接创建项目即可。

## 步骤 1：在 Neon 官网创建项目

1. 打开 **https://neon.tech**，用 **GitHub** 登录。
2. 登录后点击 **「Create a project」**。
3. 填写：
   - **Project name**：`metro-trade`（或任意）
   - **Region**：选一个即可（如 US East）
4. 点击 **「Create project」**。
5. 创建完成后，在页面上找到 **Connection string**，选择 **Pooled**，复制整串（形如 `postgresql://...?sslmode=require`）。

## 步骤 2：在 Vercel 配置环境变量

1. 打开 **https://vercel.com** → 进入项目 **metro-trade**。
2. 进入 **Settings** → **Environment Variables**。
3. 新增或编辑：
   - **Name**：`DATABASE_URL`
   - **Value**：粘贴刚才复制的连接串。
   - **Environment**：勾选 Production（以及 Preview 如需要）。
4. 保存。

## 步骤 3：重新部署

1. 在项目里进入 **Deployments**。
2. 最新部署右侧 **「...」** → **「Redeploy」**。
3. 等待部署完成。

## 验证

- 访问 https://metro-trade.vercel.app 做几次浏览、点击联系、收藏。
- 打开 https://metro-trade.vercel.app/admin/stats?token=20260109ForMXG 查看 PV/UV、喜欢次数、点击联系等是否有数据。

---

**若你之前打开了 pg.new 的认领弹窗**：直接点 **Cancel** 关闭即可，改按上面步骤在 neon.tech 创建新项目。

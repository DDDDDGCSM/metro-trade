# 🚇 Metro Trade - Trueque en el Metro

基于地铁线的交易/求购平台：按地铁线筛选商品，支持西语/英语切换，风格贴合拉美与地铁场景。

## ✨ 功能

- 🚇 **按地铁线筛选**：Tab 切换 L1–L12、LA、LB 或「Todos」
- 📦 **商品卡片**：图片、标题、简介、价格
- 📲 **联系我**：点击跳转第五列链接（WhatsApp/Messenger 等，新标签页）
- 🌐 **西语/英语**：默认西语；英语版使用路径 `/en`（如 `https://你的域名/en`），页头 ES | EN 切换会同步 URL
- 🎨 **拉美 + 地铁风格**：暖色、Outfit 字体、站牌式 Tab

## 📂 供给数据

- 商品列表来自 `static/data/products.json`（应用启动时加载）。
- 从 Excel 重新生成 JSON（需将 `地铁交易-供给.xlsx` 放在项目**上一级**目录）：
  ```bash
  pip install pandas openpyxl
  python3 scripts/build_products.py
  ```
- **图片本地化**（避免外链失效）：将商品图片下载到 `static/product-images/` 并改写 JSON 中的链接为本地路径：
  ```bash
  python3 scripts/download_product_images.py
  ```

## 🚀 本地运行

```bash
pip install -r requirements.txt
python3 app.py
```

访问 http://localhost:5000/ 为西语首页，http://localhost:5000/en 为英语首页。

## 🌐 部署上线（Vercel）

- **默认西语**：根路径 `/` 为西语版。
- **英语版**：路径 `/en` 为英语版（如 `https://你的项目.vercel.app/en`）。

部署方式任选其一：

1. **Vercel 网页**：在 [vercel.com/new](https://vercel.com/new) 导入本仓库，直接 Deploy。
2. **Vercel CLI**：
   ```bash
   npx vercel --prod
   ```
   按提示登录并选择生产部署即可。

## 📊 数据监控（PV / UV 与关键行为）

- **入口**：访问 **`/admin/stats`**，需携带 token 才能查看。
- **默认 token**：`20260109ForMXG`（可在 Vercel/环境变量中设置 `ADMIN_TOKEN` 覆盖）。
- **访问示例**：
  - 本地：`http://localhost:5000/admin/stats?token=20260109ForMXG`
  - 线上：`https://你的域名.vercel.app/admin/stats?token=20260109ForMXG`
- **地铁交易关键指标**（后台首屏）：
  - **PV 总浏览量**、**UV 独立访客数**
  - **喜欢/收藏次数**（metro_favorite）
  - **点击联系次数**（metro_contact_click）
  - **点击上传(发布)次数**（metro_publish_click）
  - **提交成功次数**（metro_publish_success）
- **按天 PV/UV**：最近 30 天每日的 PV、UV 表格。
- **持久化**：在 Vercel 上若未配置 **DATABASE_URL**（如 Neon/Postgres），埋点仅存内存，实例休眠后数据会丢失。请在 Vercel 项目环境变量中配置 `DATABASE_URL`，应用会自动建表并持久化埋点。

---

# 📚 BookForMX - 墨西哥图书交换平台（原项目说明保留）

## ✨ 功能特性

- 📖 **20本精选图书**：每本书都有独特的故事
- 💬 **故事分享**：了解每本书背后的情感
- 🤝 **交换申请**：简单的申请流程
- 📱 **移动端适配**：完美支持手机访问
- 💬 **WhatsApp 集成**：直接联系交换伙伴
- 🌐 **西班牙语界面**：符合本地表达习惯

## 🚀 快速部署

### 方法一：自动化部署（推荐）

#### 一键部署（半自动）

```bash
python3 一键部署.py your_github_token
```

自动完成：
- ✅ 推送到 GitHub
- ✅ 提供 Vercel 部署指引

#### 完全自动部署

```bash
python3 完全自动部署.py github_token vercel_token
```

自动完成：
- ✅ 推送到 GitHub
- ✅ 创建 Vercel 项目
- ✅ 触发部署
- ✅ 完全无需手动操作

详细说明请查看：[自动化部署说明.md](自动化部署说明.md)

### 方法二：网页部署

1. 访问: https://vercel.com/new
2. 使用 GitHub 登录
3. 导入仓库: `DDDDDGCSM/bookforMX`
4. 点击: "Deploy"

详细步骤请查看：[快速部署指南.md](快速部署指南.md)

### 方法三：使用 Vercel CLI

```bash
npm install -g vercel
vercel login
vercel
```

## 📁 项目结构

```
bookforMX/
├── app.py                    # Flask 后端应用
├── requirements.txt          # Python 依赖
├── vercel.json              # Vercel 配置
├── 一键部署.py              # 半自动部署脚本
├── 完全自动部署.py          # 全自动部署脚本
├── templates/               # HTML 模板
│   └── index.html          # 主页面
└── static/                 # 静态资源
    ├── css/
    │   └── style.css       # 样式文件
    └── js/                 # JavaScript 文件
```

## 🛠️ 本地开发

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python3 app.py
```

访问: http://localhost:5000

## 📋 技术栈

- **后端**: Flask 3.0.0
- **前端**: HTML, CSS, JavaScript
- **部署**: Vercel
- **语言**: 西班牙语

## 🌐 部署后访问

部署成功后，您将获得一个 Vercel 链接，例如：
```
https://bookformx.vercel.app
```

## 📝 更新部署

修改代码后，只需运行部署脚本：

```bash
# 使用一键部署
python3 一键部署.py your_token

# 或使用完全自动部署
python3 完全自动部署.py github_token vercel_token
```

Vercel 会自动检测并重新部署（约 1-2 分钟）

## 📚 相关文档

- [自动化部署说明.md](自动化部署说明.md) - 自动化部署详细说明
- [快速部署指南.md](快速部署指南.md) - 网页部署步骤
- [VERCEL_DEPLOY_GUIDE.md](VERCEL_DEPLOY_GUIDE.md) - Vercel 完整指南

## 🎯 下一步

1. 运行自动化部署脚本
2. 测试所有功能
3. 收集用户反馈
4. 持续优化体验

---

**祝您部署顺利！** 🚀

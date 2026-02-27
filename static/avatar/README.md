# 头像图片说明

请将你朋友的头像图片放到这个目录下，文件名为：`friend-avatar.jpg`

**图片要求：**
- 文件名：`friend-avatar.jpg`
- 建议尺寸：150x150 像素或更大（正方形）
- 格式：JPG 或 PNG（如果是 PNG，请重命名为 `friend-avatar.png` 并更新代码中的路径）

**当前路径：**
`/static/avatar/friend-avatar.jpg`

**如何更新：**
如果你使用的是 PNG 格式，需要修改 `templates/index.html` 中所有书籍的 `avatar` 字段，将路径改为 `/static/avatar/friend-avatar.png`

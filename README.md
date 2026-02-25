# 智能排版

一款基于飞书多维表格的智能排版打印插件，支持 AI 模板生成、电子签名、批量打印等功能。

## 📁 项目结构

```
feishu3/
├── feishu-print/          # 主前端应用 (Vue 3 + TypeScript)
├── feishu-print-admin/    # 管理后台 (Vue 3 + TypeScript)
├── feishu-print-backend/  # 后端 API (Python FastAPI)
└── DEPLOY.md              # 服务器部署指南
```

## 🛠️ 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端框架 | Vue 3 + TypeScript + Vite |
| 状态管理 | Pinia |
| UI 组件 | Element Plus |
| 富文本编辑 | TinyMCE |
| 后端框架 | Python FastAPI |
| 数据库 | MySQL |
| AI 能力 | 通义千问 (qwen-max) |
| 部署 | Nginx + Uvicorn + HTTPS |

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/feishu-print.git
cd feishu-print
```

### 2. 启动后端

```bash
cd feishu-print-backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入数据库连接和 API 密钥

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 3. 启动前端

```bash
# 主应用
cd feishu-print
npm install
npm run dev

# 管理后台 (新终端)
cd feishu-print-admin
npm install
npm run dev
```

### 4. 访问地址

| 服务 | 地址 |
| --- | --- |
| 主应用 | http://localhost:5155 |
| 管理后台 | http://localhost:5156 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

## ⚙️ 环境变量配置

### 后端 `.env`

```env
# 数据库
DATABASE_URL=mysql+pymysql://用户名:密码@localhost:3306/数据库名

# JWT 密钥
JWT_SECRET_KEY=你的密钥

# 通义千问 API
DASHSCOPE_API_KEY=你的API密钥

# CORS 允许的域名
CORS_ORIGINS=http://localhost:5155,http://localhost:5156
```

### 前端 `.env.production`

```env
VITE_API_BASE=https://你的域名
```

## 📦 生产环境部署

详见 [DEPLOY.md](./DEPLOY.md)

### 快速部署命令

```bash
# 前端打包
cd feishu-print && npm run build
cd feishu-print-admin && npm run build

# 上传到服务器
scp -r feishu-print/dist/* root@服务器IP:/var/www/feishu-print/frontend/
scp -r feishu-print-admin/dist/* root@服务器IP:/var/www/feishu-print/admin/
```

## 🔑 核心功能

- **AI 模板生成**：通过自然语言描述生成专业 HTML 打印模板
- **电子签名**：支持远程签名链接，签名后自动嵌入文档
- **字段映射**：自动解析飞书多维表格字段并映射到模板
- **批量打印**：一键批量打印多条数据记录
- **模板管理**：保存、编辑、复用打印模板

## 📝 API 接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/ai/generate-template-stream` | POST | AI 流式生成模板 |
| `/api/signatures/` | POST | 创建签名请求 |
| `/api/signatures/token/{token}` | GET | 获取签名详情 |
| `/api/templates/` | GET/POST | 模板 CRUD |
| `/api/user/` | GET/POST | 用户管理 |

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'feat: 添加xxx功能'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 提交 Pull Request

## 📄 许可证

MIT License

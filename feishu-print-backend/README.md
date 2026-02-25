# 智能排版后端

智能排版模板管理系统后端 API - 基于 FastAPI + MySQL

## 📋 功能特性

- ✅ RESTful API 设计
- ✅ MySQL 数据库持久化
- ✅ CORS 跨域支持
- ✅ 自动生成 API 文档
- ✅ 完整的 CRUD 操作

## 🛠️ 技术栈

- **FastAPI** - 现代化 Python Web 框架
- **SQLAlchemy** - ORM 数据库映射
- **MySQL** - 关系型数据库
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI 服务器

## 📁 项目结构

```
feishu-print-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── database.py             # 数据库连接配置
│   ├── config.py               # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   └── template.py         # SQLAlchemy 模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── template.py         # Pydantic 模式
│   └── routers/
│       ├── __init__.py
│       └── templates.py        # 路由处理
├── requirements.txt            # Python 依赖
├── .env                        # 环境变量配置
├── database.sql                # 数据库初始化脚本
└── README.md
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd feishu-print-backend
pip install -r requirements.txt
```

### 2. 配置数据库

编辑 `.env` 文件，设置数据库连接：

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/feishu_print
CORS_ORIGINS=http://localhost:5173
```

### 3. 初始化数据库

在 MySQL 中执行：

```bash
mysql -u root -p < database.sql
```

### 4. 运行服务器

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📝 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/templates/` | 获取所有模板 |
| GET | `/api/templates/{id}` | 获取单个模板 |
| POST | `/api/templates/` | 创建新模板 |
| PUT | `/api/templates/{id}` | 更新模板 |
| DELETE | `/api/templates/{id}` | 删除模板 |

## 📦 数据模型

### Template

```json
{
  "id": 1,
  "name": "模板名称",
  "content": "<p>HTML 内容</p>",
  "created_at": "2024-12-24T10:00:00",
  "updated_at": "2024-12-24T10:00:00"
}
```

## 🔧 开发说明

### 添加新路由

1. 在 `app/routers/` 创建新的路由文件
2. 在 `app/main.py` 中注册路由

### 修改数据库模型

1. 修改 `app/models/*.py`
2. 使用 Alembic 进行数据库迁移（可选）

## 📄 许可证

MIT

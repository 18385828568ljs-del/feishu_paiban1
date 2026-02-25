# 智能排版 部署指南

## 服务器环境要求

- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 7+)
- **Python**: 3.9+
- **Node.js**: 18+ (仅本地构建需要)
- **MySQL**: 5.7+ 或 8.0+
- **Nginx**: 1.18+
- **systemd**: 用于管理后端服务

## 一、服务器准备

### 1.1 创建部署目录

```bash
# 后端代码目录
sudo mkdir -p /opt/feishu-print/backend

# 前端静态文件目录
sudo mkdir -p /var/www/feishu-print/frontend
sudo mkdir -p /var/www/feishu-print/admin

# 设置权限
sudo chown -R $USER:$USER /opt/feishu-print
sudo chown -R www-data:www-data /var/www/feishu-print
```

### 1.2 安装依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3-pip python3-venv mysql-server nginx

# CentOS/RHEL
sudo yum install -y python3-pip python3-venv mysql-server nginx
```

## 二、后端部署

### 2.1 上传代码

```bash
# 方式1: 使用 git
cd /opt/feishu-print/backend
git clone https://你的仓库地址 .
# 或使用 scp 上传整个 feishu-print-backend 目录
```

### 2.2 创建虚拟环境并安装依赖

```bash
cd /opt/feishu-print/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2.3 配置环境变量

```bash
# 复制模板文件
cp .env.example .env

# 编辑 .env 文件，填入真实配置
nano .env
```

**重要配置项**：
- `DATABASE_URL`: 数据库连接字符串，格式：`mysql+pymysql://用户名:密码@主机:端口/数据库名`
- `JWT_SECRET_KEY`: 强随机密钥（生产环境必须修改，建议使用至少32位的随机字符串）
- `DASHSCOPE_API_KEY`: 通义千问 API 密钥
- `CORS_ORIGINS`: 允许的前端域名（多个用逗号分隔，不要有空格），例如：`https://example.com,https://admin.example.com`
- `ENVIRONMENT=production`

### 2.4 初始化数据库

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE feishu_print CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 运行迁移（如果有）
python run_migration.py
```

### 2.5 创建 systemd 服务

创建 `/etc/systemd/system/feishu-print-backend.service`：

```ini
[Unit]
Description=Feishu Print Backend API
After=network.target mysql.service

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/opt/feishu-print/backend
Environment="PATH=/opt/feishu-print/backend/venv/bin"
ExecStart=/opt/feishu-print/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable feishu-print-backend
sudo systemctl start feishu-print-backend
sudo systemctl status feishu-print-backend
```

查看日志：

```bash
sudo journalctl -u feishu-print-backend -f
```

## 三、前端本地构建

### 3.1 构建主应用

在本地 Windows 机器上执行：

```bash
cd feishu-print

# 创建生产环境配置
cp .env.production.example .env.production
# 编辑 .env.production，设置 VITE_API_BASE=https://你的域名

# 安装依赖（如果还没安装）
npm ci

# 构建
npm run build
```

构建产物在 `feishu-print/dist/` 目录。

### 3.2 构建管理后台

```bash
cd feishu-print-admin

# 创建生产环境配置
cp .env.production.example .env.production
# 编辑 .env.production，设置 VITE_API_BASE=https://你的域名

# 安装依赖（如果还没安装）
npm ci

# 构建
npm run build
```

构建产物在 `feishu-print-admin/dist/` 目录。

## 四、前端部署

### 4.1 上传构建产物

从本地 Windows 上传（使用 PowerShell 或 Git Bash）：

```bash
# 使用 scp
scp -r feishu-print/dist/* root@服务器IP:/var/www/feishu-print/frontend/
scp -r feishu-print-admin/dist/* root@服务器IP:/var/www/feishu-print/admin/

# 或使用 rsync（如果已安装）
rsync -av --delete feishu-print/dist/ root@服务器IP:/var/www/feishu-print/frontend/
rsync -av --delete feishu-print-admin/dist/ root@服务器IP:/var/www/feishu-print/admin/
```

### 4.2 设置权限

在服务器上执行：

```bash
sudo chown -R www-data:www-data /var/www/feishu-print
sudo chmod -R 755 /var/www/feishu-print
```

## 五、Nginx 配置

### 5.1 创建配置文件

创建 `/etc/nginx/sites-available/feishu-print`：

```nginx
# HTTP 配置（主应用和管理后台）
server {
    listen 80;
    server_name 你的域名;

    # 重定向到 HTTPS（如果已配置 SSL）
    # return 301 https://$server_name$request_uri;

    # 主应用前端
    location / {
        root /var/www/feishu-print/frontend;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # 管理后台
    location /admin {
        alias /var/www/feishu-print/admin;
        try_files $uri $uri/ /admin/index.html;
        index index.html;
    }

    # API 反向代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}

# HTTPS 配置（可选，使用 Let's Encrypt）
# server {
#     listen 443 ssl http2;
#     server_name 你的域名;
#
#     ssl_certificate /etc/letsencrypt/live/你的域名/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/你的域名/privkey.pem;
#
#     # SSL 配置
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers HIGH:!aNULL:!MD5;
#     ssl_prefer_server_ciphers on;
#
#     # 主应用前端
#     location / {
#         root /var/www/feishu-print/frontend;
#         try_files $uri $uri/ /index.html;
#         index index.html;
#     }
#
#     # 管理后台
#     location /admin {
#         alias /var/www/feishu-print/admin;
#         try_files $uri $uri/ /admin/index.html;
#         index index.html;
#     }
#
#     # API 反向代理
#     location /api {
#         proxy_pass http://127.0.0.1:8000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#     }
#
#     # 健康检查
#     location /health {
#         proxy_pass http://127.0.0.1:8000/health;
#     }
# }
```

### 5.2 启用站点

```bash
sudo ln -s /etc/nginx/sites-available/feishu-print /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 六、SSL 证书配置（可选但强烈推荐）

使用 Let's Encrypt 免费 SSL 证书：

```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx

# 获取证书（会自动配置 Nginx）
sudo certbot --nginx -d 你的域名

# 自动续期测试
sudo certbot renew --dry-run
```

## 七、验证部署

### 7.1 后端健康检查

```bash
# 本地检查
curl http://localhost:8000/health

# 通过 Nginx 检查
curl http://你的域名/health
```

### 7.2 前端访问

- 主应用: `http://你的域名/` 或 `https://你的域名/`
- 管理后台: `http://你的域名/admin` 或 `https://你的域名/admin`

### 7.3 API 测试

```bash
curl http://你的域名/api/health
```

## 八、常见问题

### 8.1 后端服务无法启动

**检查步骤**：
1. 查看服务状态：`sudo systemctl status feishu-print-backend`
2. 查看日志：`sudo journalctl -u feishu-print-backend -f`
3. 检查 `.env` 配置是否正确
4. 检查数据库连接：`mysql -u 用户名 -p -h 主机 数据库名`
5. 检查端口是否被占用：`sudo netstat -tlnp | grep 8000`

### 8.2 前端 API 请求失败（CORS 错误）

**解决方案**：
1. 确认前端 `.env.production` 中的 `VITE_API_BASE` 配置正确
2. 检查后端 `.env` 中的 `CORS_ORIGINS` 是否包含前端域名（不要有空格）
3. 重启后端服务：`sudo systemctl restart feishu-print-backend`

### 8.3 静态文件 404

**检查步骤**：
1. 检查文件是否存在：`ls -la /var/www/feishu-print/frontend/`
2. 检查文件权限：`sudo chown -R www-data:www-data /var/www/feishu-print`
3. 检查 Nginx 配置中的路径是否正确
4. 检查 `try_files` 配置是否正确
5. 查看 Nginx 错误日志：`sudo tail -f /var/log/nginx/error.log`

### 8.4 管理后台路由 404

**解决方案**：
确保 Nginx 配置中 `/admin` 路径使用 `alias` 而不是 `root`，并且 `try_files` 指向 `/admin/index.html`。

### 8.5 数据库连接失败

**检查步骤**：
1. 确认 MySQL 服务运行：`sudo systemctl status mysql`
2. 检查数据库用户权限
3. 检查防火墙是否允许连接
4. 确认 `DATABASE_URL` 格式正确

## 九、更新部署流程

### 9.1 更新后端

```bash
cd /opt/feishu-print/backend
git pull
source venv/bin/activate
pip install -r requirements.txt

# 如果有数据库迁移
python run_migration.py

# 重启服务
sudo systemctl restart feishu-print-backend
```

### 9.2 更新前端

1. **本地重新构建**：
   ```bash
   cd feishu-print
   npm run build
   
   cd ../feishu-print-admin
   npm run build
   ```

2. **上传新的 dist 目录**：
   ```bash
   scp -r feishu-print/dist/* root@服务器IP:/var/www/feishu-print/frontend/
   scp -r feishu-print-admin/dist/* root@服务器IP:/var/www/feishu-print/admin/
   ```

3. **无需重启服务**（静态文件直接生效）

## 十、备份和恢复

### 10.1 数据库备份

```bash
# 备份
mysqldump -u 用户名 -p feishu_print > backup_$(date +%Y%m%d).sql

# 恢复
mysql -u 用户名 -p feishu_print < backup_20240101.sql
```

### 10.2 代码备份

```bash
# 备份整个后端目录
tar -czf feishu-print-backend-backup.tar.gz /opt/feishu-print/backend

# 备份前端静态文件
tar -czf feishu-print-frontend-backup.tar.gz /var/www/feishu-print
```

## 十一、监控和维护

### 11.1 日志管理

```bash
# 后端日志
sudo journalctl -u feishu-print-backend -n 100

# Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

### 11.2 性能监控

```bash
# 检查服务状态
sudo systemctl status feishu-print-backend

# 检查资源使用
top
htop

# 检查端口监听
sudo netstat -tlnp | grep 8000
```

## 十二、安全建议

1. **定期更新系统**：`sudo apt update && sudo apt upgrade`
2. **使用强密码**：数据库密码、JWT_SECRET_KEY 等
3. **启用防火墙**：只开放必要端口（80, 443, 22）
4. **使用 HTTPS**：生产环境必须启用 SSL
5. **定期备份**：数据库和重要配置文件
6. **限制 SSH 访问**：使用密钥认证，禁用密码登录
7. **监控日志**：定期检查错误日志和访问日志

---

**部署完成后，请确保**：
- ✅ 后端服务正常运行（`systemctl status`）
- ✅ 前端页面可以正常访问
- ✅ API 接口可以正常调用
- ✅ CORS 配置正确
- ✅ SSL 证书已配置（生产环境）
- ✅ 数据库连接正常
- ✅ 日志记录正常


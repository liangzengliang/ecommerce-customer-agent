# 部署指南

## 一、环境要求

### 硬件

| 项 | 最低 | 推荐 |
|---|---|---|
| CPU | 4 核 | 8 核 |
| 内存 | 8 GB | 16 GB |
| 磁盘 | 20 GB | 50 GB |

### 软件

| 软件 | 版本 | 用途 |
|---|---|---|
| Python | 3.11+ | 后端运行时 |
| Node.js | 20+ | 前端构建 |
| MySQL | 8.0+ | 业务数据库 |
| Redis | 6.0+ | 缓存/会话 |
| Milvus | 2.6+ | 向量数据库 |
| Docker | 24+ | 容器化部署 |

## 二、依赖服务部署

### 2.1 MySQL

**Docker 部署**：

```bash
docker run -d --name mysql8 \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -e MYSQL_DATABASE=customer_service \
  -v /data/mysql:/var/lib/mysql \
  --restart unless-stopped \
  mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

**允许远程访问**：

```sql
CREATE USER 'root'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

### 2.2 Redis

```bash
docker run -d --name redis-7.2 \
  -p 6379:6379 \
  -v /opt/module/redis/data:/data \
  --restart unless-stopped \
  redis:7.2-alpine \
  redis-server --requirepass your_password --appendonly yes
```

### 2.3 Milvus（单机版）

```bash
docker run -d --name milvus-standalone \
  -p 19530:19530 -p 9091:9091 \
  -v /data/milvus:/var/lib/milvus \
  milvusdb/milvus:v3.0.2 \
  milvus run standalone
```

验证：

```bash
curl http://localhost:9091/healthz
# 预期：OK
```

## 三、后端部署

### 3.1 拉取代码

```bash
git clone <your-repo-url>
cd ecommerce-customer-service/backend
```

### 3.2 创建虚拟环境

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3.3 安装依赖

```bash
pip install -r requirements.txt
```

### 3.4 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`：

```env
DATABASE_URL=mysql+aiomysql://root:your_password@localhost:3306/customer_service
REDIS_URL=redis://:your_password@localhost:6379/0
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION=ecommerce_knowledge

OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=Qwen/Qwen2.5-7B-Instruct

EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIM=1024
EMBEDDING_API_KEY=sk-your-key
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1

SECRET_KEY=generate-a-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 3.5 初始化数据库

```bash
# 方式 1：用 SQL 脚本
mysql -u root -p customer_service < ../schema.sql

# 方式 2：用 Alembic
alembic upgrade head
```

初始化意图配置和管理员：

```bash
python -m scripts.init_db
```

### 3.6 启动服务

**开发模式**：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**生产模式**（多 worker）：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**用 systemd 托管**（Linux）：

创建 `/etc/systemd/system/customer-service.service`：

```ini
[Unit]
Description=Customer Service Backend
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ecommerce-customer-service/backend
Environment="PATH=/opt/ecommerce-customer-service/venv/bin"
ExecStart=/opt/ecommerce-customer-service/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用：

```bash
sudo systemctl daemon-reload
sudo systemctl enable customer-service
sudo systemctl start customer-service
sudo systemctl status customer-service
```

### 3.7 启动 Celery（异步任务）

```bash
# Linux / macOS
celery -A app.tasks.celery_app.celery_app worker --loglevel=info

# Windows
celery -A app.tasks.celery_app.celery_app worker --loglevel=info --pool=solo
```

## 四、前端部署

### 4.1 安装依赖

```bash
cd frontend
npm install
```

### 4.2 配置 API 地址

编辑 `.env.production`：

```env
VITE_API_BASE_URL=https://your-domain.com/api/v1
```

修改 `src/api/index.ts` 里的 `baseURL`：

```typescript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  ...
})
```

### 4.3 构建

```bash
npm run build
```

产物在 `dist/` 目录。

### 4.4 用 Nginx 托管

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/customer-service/dist;
    index index.html;

    # SPA 路由 fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 代理 API 到后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # SSE 需要
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
    }
}
```

## 五、Docker 部署

### 5.1 后端 Dockerfile

`docker/backend/Dockerfile`：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y \
    gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 前端 Dockerfile

`docker/frontend/Dockerfile`：

```dockerfile
# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 5.3 docker-compose.yml

```yaml
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_DATABASE: customer_service
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s

  redis:
    image: redis:7.2-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mysql_data:
  redis_data:
```

启动：

```bash
docker compose up -d
```

## 六、验证部署

### 6.1 后端健康检查

```bash
curl http://localhost:8000/health
# 预期：{"status":"ok"}
```

### 6.2 API 文档

浏览器打开 `http://localhost:8000/docs`。

### 6.3 前端

浏览器打开 `http://localhost` 或 `http://your-domain.com`。

### 6.4 端到端测试

```bash
# 注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123456"}'

# 记录 token，然后发消息
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message":"你好"}'
```

## 七、常见问题

| 问题 | 原因 | 解决 |
|---|---|---|
| `Can't connect to MySQL` | 连接串错 | 检查 `.env` |
| `Event loop is closed` | Windows 事件循环 | `main.py` 顶部加修复 |
| `pydantic-core 版本不兼容` | 依赖冲突 | `pip install pydantic==2.10.0` |
| `bcrypt 报错` | passlib 与 bcrypt 5.x 不兼容 | `pip install bcrypt==4.0.1` |
| SSE 没数据 | Nginx 缓冲 | 加 `proxy_buffering off;` |
| 前端 404 | SPA 路由没 fallback | Nginx 加 `try_files` |
| 跨域报错 | CORS 配置 | 检查 `main.py` 的 CORSMiddleware |

## 八、备份与恢复

### 备份 MySQL

```bash
mysqldump -u root -p customer_service > backup_$(date +%Y%m%d).sql
```

### 恢复

```bash
mysql -u root -p customer_service < backup_20260926.sql
```

### 备份 Milvus

Milvus 数据在 `/data/milvus` 目录，直接打包即可。

### 备份 Redis

Redis 数据在 `/opt/module/redis/data` 目录，`dump.rdb` 和 `appendonly.aof`。

## 九、升级流程

1. **停服务**
   ```bash
   sudo systemctl stop customer-service
   ```

2. **备份数据库**
   ```bash
   mysqldump -u root -p customer_service > backup.sql
   ```

3. **拉新代码**
   ```bash
   git pull
   ```

4. **装新依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **数据库迁移**
   ```bash
   alembic upgrade head
   ```

6. **启动服务**
   ```bash
   sudo systemctl start customer-service
   ```

7. **验证**
   ```bash
   curl http://localhost:8000/health
   ```
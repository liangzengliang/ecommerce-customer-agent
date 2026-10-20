# 电商智能客服系统

基于 **FastAPI + Vue3 + LangGraph + RAG + NLU** 的电商智能客服 Agent，支持多轮对话、意图识别、情感分析、知识库检索、工具调用和人工转接。

## 功能特性

- **智能对话**：基于 LLM 的多轮对话，支持流式输出（SSE）
- **意图识别**：22 种电商意图分类（商品咨询、订单查询、退款、投诉等）
- **情感分析**：识别用户情绪（positive / neutral / negative），负面情绪自动转人工
- **RAG 检索**：基于 Milvus 的知识库检索，回答商品政策类问题
- **工具调用**：订单查询、物流追踪、商品搜索、创建工单、退款申请等
- **人工转接**：复杂问题或用户主动要求时转接人工客服
- **会话记忆**：Redis 存储多轮对话历史
- **数据看板**：会话量、消息量、情感分布等统计

## 技术栈

### 后端

| 技术 | 版本 | 用途 |
|---|---|---|
| Python | 3.11+ | 运行时 |
| FastAPI | 0.115.0 | Web 框架 |
| SQLAlchemy | 2.0.36 | ORM |
| LangChain | 1.2.12 | LLM 编排 |
| LangGraph | 1.1.2 | Agent 工作流 |
| MySQL | 8.0 | 业务数据 |
| Redis | 7.2 | 会话记忆 |
| Milvus | 3.0 | 向量检索 |
| Celery | 5.4.0 | 异步任务 |

### 前端

| 技术 | 版本 |
|---|---|
| Vue | 3.5.x |
| TypeScript | 5.6.x |
| Vite | 5.4.x |
| Pinia | 2.2.x |
| Element Plus | 2.8.x |

### LLM

- **对话模型**：Qwen/Qwen2.5-7B-Instruct（硅基流动）
- **嵌入模型**：BAAI/bge-m3（API 调用，无需本地部署）

## 项目结构

```text
ecommerce-customer-service/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # API 路由
│   │   ├── core/               # 核心配置
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # 业务逻辑服务
│   │   ├── agents/             # LangGraph Agent
│   │   ├── nlu/                # NLU 模块
│   │   ├── rag/                # RAG 模块
│   │   ├── tasks/              # Celery 异步任务
│   │   ├── middlewares/        # FastAPI 中间件
│   │   ├── utils/              # 工具函数
│   │   └── main.py             # FastAPI 入口
│   ├── alembic/                # 数据库迁移
│   ├── tests/                  # 测试
│   ├── scripts/                # 运维脚本
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/                   # Vue3 前端
│   ├── src/
│   │   ├── api/                # API 封装
│   │   ├── components/         # 组件
│   │   ├── views/              # 页面
│   │   ├── stores/             # Pinia 状态
│   │   ├── router/             # 路由
│   │   ├── services/           # 业务服务
│   │   ├── utils/              # 工具
│   │   └── main.ts             # 入口
│   ├── package.json
│   └── vite.config.ts
├── config/                     # YAML 配置
├── docs/                       # 项目文档
├── knowledge_base/             # 知识库原始文件
├── docker/                     # Docker 配置
├── scripts/                    # 运维脚本
├── logs/                       # 日志目录
└── README.md
```

## 快速开始

### 1. 环境要求

- Python 3.11+
- Node.js 20+
- MySQL 8.0+
- Redis 6.0+
- Milvus 2.6+
- Docker（可选，用于运行依赖服务）

### 2. 启动依赖服务

**MySQL**：

```bash
docker run -d --name mysql8 \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -e MYSQL_DATABASE=customer_service \
  mysql:8.0 --character-set-server=utf8mb4
```

**Redis**：

```bash
docker run -d --name redis-7.2 \
  -p 6379:6379 \
  redis:7.2-alpine \
  redis-server --requirepass your_password --appendonly yes
```

**Milvus**：

```bash
docker run -d --name milvus-standalone \
  -p 19530:19530 -p 9091:9091 \
  milvusdb/milvus:v3.0.2 milvus run standalone
```

### 3. 后端启动

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入数据库、Redis、Milvus、LLM 的配置

# 建表
mysql -u root -p customer_service < ../schema.sql

# 初始化数据
python -m scripts.init_db

# 启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

看到以下输出说明启动成功：

```text
[OK] Redis 连接成功
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 4. 前端启动

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://localhost:5173

## 使用说明

1. 打开 http://localhost:5173，注册一个账号
2. 进入对话页，输入消息
3. 系统自动识别意图、分析情感、检索知识、生成回复
4. 触发转人工时，会话状态变为 `transferred`

### 测试对话示例

| 消息 | 预期行为 |
|---|---|
| `你好` | LLM 直接回复 |
| `怎么申请退款` | RAG 检索知识库回答 |
| `查订单 ORDER20261001001` | 工具调用查询订单 |
| `我要投诉` | 创建工单 |
| `你们太差劲了！` | 负面情绪，转人工 |

## API 文档

后端启动后，访问：

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

详细接口规范见 [docs/API_SPEC.md](docs/API_SPEC.md)。

## 数据库

12 张表，详见 [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)。

| 表名 | 说明 |
|---|---|
| users | 用户 |
| agents | 客服坐席 |
| intents | 意图配置 |
| products | 商品 |
| sessions | 会话 |
| orders | 订单 |
| order_items | 订单明细 |
| messages | 消息 |
| knowledge | 知识库 |
| conversation_ratings | 会话评分 |
| tickets | 工单 |
| ticket_logs | 工单日志 |

## 架构设计

详见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

## 部署

详见 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。

## 常见问题

| 问题 | 原因 | 解决 |
|---|---|---|
| `No module named 'app'` | 工作目录不对 | `cd backend` |
| `No module named 'backend'` | 代码里有 `from backend.app` | 改成 `from app` |
| `Event loop is closed` | Windows 事件循环 | `main.py` 顶部加修复 |
| `pydantic-core 版本不兼容` | 依赖冲突 | `pip install pydantic==2.10.0` |
| `bcrypt 报错` | passlib 与 bcrypt 5.x 不兼容 | `pip install bcrypt==4.0.1` |
| `Redis 连接失败` | 密码错/保护模式 | 检查 `.env` 的 `REDIS_URL` |
| `Data truncated for column 'user_type'` | ENUM 值不一致 | `ALTER TABLE users MODIFY COLUMN user_type ENUM('customer','agent','admin') DEFAULT 'customer';` |
| `422 Unprocessable Entity` | 参数校验失败 | 登录用 form 格式，注册用 JSON |
| 前端 `npm install` 慢 | 网络问题 | `npm config set registry https://registry.npmmirror.com` |

## 开发规范

### 后端

- 所有导入用 `from app.xxx`，**不要**用 `from backend.app.xxx`
- 所有命令在 `backend/` 目录下执行
- 新增依赖后同步更新 `requirements.txt` 和 `pyproject.toml`
- 数据库模型变更后用 Alembic 生成迁移

### 前端

- 组件命名用 PascalCase
- API 调用统一走 `src/api/`
- 状态管理用 Pinia

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request。
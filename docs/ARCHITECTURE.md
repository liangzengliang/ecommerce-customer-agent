# 架构设计文档

## 一、项目概述

电商智能客服系统，基于 FastAPI + LangGraph + RAG + NLU 构建，支持多轮对话、意图识别、情感分析、知识库检索、工具调用和人工转接。

## 二、技术栈

### 后端

| 技术 | 版本 | 用途 |
|---|---|---|
| Python | 3.12 | 运行时 |
| FastAPI | 0.115.0 | Web 框架 |
| Uvicorn | 0.32.0 | ASGI 服务器 |
| SQLAlchemy | 2.0.36 | ORM |
| aiomysql | 0.2.0 | MySQL 异步驱动 |
| Alembic | 1.13.3 | 数据库迁移 |
| LangChain | 1.2.12 | LLM 编排 |
| LangGraph | 1.1.2 | Agent 工作流 |
| langchain-openai | 1.1.1 | OpenAI 协议适配 |
| langchain-redis | 0.2.5 | Redis 集成 |
| langchain-milvus | 0.3.3 | Milvus 集成 |
| pymilvus | 2.6.x | 向量库客户端 |
| Celery | 5.4.0 | 异步任务 |
| Redis | 5.2.0 | 缓存/记忆 |

### 前端

| 技术 | 版本 | 用途 |
|---|---|---|
| Vue | 3.5.x | 前端框架 |
| TypeScript | 5.6.x | 类型系统 |
| Vite | 5.4.x | 构建工具 |
| Pinia | 2.2.x | 状态管理 |
| Vue Router | 4.4.x | 路由 |
| Element Plus | 2.8.x | UI 组件库 |
| Axios | 1.7.x | HTTP 客户端 |
| dayjs | 1.11.x | 时间处理 |

### 数据存储

| 技术 | 用途 |
|---|---|
| MySQL 8.0 | 业务数据 |
| Redis 7.2 | 会话记忆、缓存、限流、Celery broker |
| Milvus 3.0 | 向量存储（RAG 检索） |

### LLM

| 项 | 值 |
|---|---|
| 供应商 | 硅基流动 |
| 对话模型 | Qwen/Qwen2.5-7B-Instruct |
| 嵌入模型 | BAAI/bge-m3（API 调用，不本地部署） |
| 向量维度 | 1024 |

## 三、系统分层

```text
┌─────────────────────────────────────────────┐
│ 【客户端层】                                 │
│  Web (Vue3) | H5 | 小程序 | 客服工作台       │
└──────────────────┬──────────────────────────┘
                   │ HTTP / SSE
┌──────────────────▼──────────────────────────┐
│ 【网关接入层】                               │
│  Nginx / Caddy | API Gateway | WebSocket    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│ 【FastAPI 后端服务层】                       │
│  Chat API | Intent API | Agent API | ...    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│ 【Agent 编排层 (LangGraph)】                 │
│  意图路由 | 记忆管理 | RAG检索 | 工具调用    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│ 【AI 服务层】                                │
│  LLM 路由 | Embedding | RAG Engine          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│ 【数据存储层】                               │
│  MySQL | Redis | Milvus | MinIO             │
└─────────────────────────────────────────────┘
```

## 四、核心模块

### 4.1 NLU 模块（`app/nlu/`）

| 文件 | 职责 |
|---|---|
| `intent_classifier.py` | 基于 LLM 的意图识别，映射到预定义意图编码 |
| `sentiment_analyzer.py` | 情感分析，返回 positive/neutral/negative |
| `entity_extractor.py` | 实体抽取（订单号、手机号） |
| `slot_filling.py` | 槽位检查与澄清追问 |

### 4.2 RAG 模块（`app/rag/`）

| 文件 | 职责 |
|---|---|
| `embedding_model.py` | 嵌入模型（API 版本，不依赖 PyTorch） |
| `vector_store.py` | Milvus 向量库管理 |
| `retriever.py` | 检索器 |
| `document_loader.py` | 文档加载（txt/md） |
| `text_splitter.py` | 文本分块 |

### 4.3 Agent 模块（`app/agents/`）

| 文件/目录 | 职责 |
|---|---|
| `graph/state.py` | LangGraph 状态定义 |
| `graph/workflow.py` | 工作流编译 |
| `graph/nodes/router.py` | NLU 分析 + 路由决策 |
| `graph/nodes/rag_node.py` | RAG 检索节点 |
| `graph/nodes/tool_node.py` | 工具调用节点 |
| `graph/nodes/sentiment.py` | 情感检查节点 |
| `graph/nodes/generate.py` | 回复生成节点 |
| `graph/nodes/human.py` | 人工转接节点 |
| `tools/*.py` | 6 个业务工具 |

### 4.4 服务层（`app/services/`）

| 服务 | 职责 |
|---|---|
| `chat_service.py` | 对话编排 |
| `memory_service.py` | Redis 会话记忆 |
| `intent_service.py` | 意图识别 |
| `sentiment_service.py` | 情感分析 |
| `agent_service.py` | Agent 执行 |
| `rag_service.py` | RAG 检索 |
| `llm_service.py` | LLM 工厂 |
| `order_service.py` | 订单业务 |
| `product_service.py` | 商品业务 |
| `knowledge_service.py` | 知识库业务 |

## 五、对话处理流程

```text
用户发送消息
    ↓
① API 层接收（POST /api/v1/chat/stream）
    ↓
② ChatService 编排
    ├── 加载 Redis 会话记忆
    └── 构造 AgentState
    ↓
③ LangGraph 工作流
    ├── analyze 节点：NLU（意图+情感+实体）
    ├── 条件路由
    │   ├── PRD_* → rag 节点（RAG 检索）
    │   ├── ORD_*/PAY_* → tool 节点（工具调用）
    │   ├── CMP_* → tool 节点（工单/转人工）
    │   └── 其它 → generate 节点
    ├── sentiment 节点：负面情绪标记转人工
    ├── generate 节点：LLM 生成回复
    └── escalate 节点：如需转人工
    ↓
④ 持久化
    ├── Redis：会话记忆（TTL 24h）
    └── MySQL：messages 表、sessions 表
    ↓
⑤ SSE 流式返回给前端
```

## 六、意图分类体系

### 商品与活动咨询（PRD_*）

| 编码 | 名称 | 处理类型 |
|---|---|---|
| PRD_001 | 商品详情 | rag |
| PRD_002 | 促销活动 | rag |
| PRD_003 | 商品推荐 | rag |
| PRD_004 | 会员权益 | rag |
| PRD_005 | 配送时效 | rag |
| PRD_006 | 库存查询 | tool |

### 订单与物流（ORD_*）

| 编码 | 名称 | 处理类型 |
|---|---|---|
| ORD_001 | 订单查询 | tool |
| ORD_002 | 订单修改 | tool |
| ORD_003 | 取消订单 | tool |
| ORD_004 | 物流追踪 | tool |
| ORD_005 | 催促发货 | tool |
| ORD_006 | 修改地址 | tool |

### 支付与售后（PAY_*）

| 编码 | 名称 | 处理类型 |
|---|---|---|
| PAY_001 | 支付问题 | rag |
| PAY_002 | 申请退款 | tool |
| PAY_003 | 优惠券使用 | rag |
| PAY_004 | 售后政策 | rag |
| PAY_005 | 发票问题 | rag |

### 投诉与人工（CMP_*）

| 编码 | 名称 | 处理类型 |
|---|---|---|
| CMP_001 | 投诉建议 | tool |
| CMP_002 | 退款退货 | tool |
| CMP_003 | 人工客服 | transfer |
| CMP_004 | 建议反馈 | tool |
| FALLBACK | 闲聊/未知 | fallback |

## 七、部署拓扑

```text
Windows 本地
  ├── PyCharm 运行 FastAPI（8000）
  ├── Vite 运行 Vue3（5173）
  └── Docker Desktop 运行 Milvus（19530）

CentOS 服务器（Redis）
  └── Docker 运行 Redis 7.2（6379）

CentOS 服务器（MySQL）
  └── MySQL 8.0（3306）
```
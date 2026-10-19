# 数据库设计文档

## 一、数据库信息

| 项 | 值 |
|---|---|
| 数据库 | `customer_service` |
| 字符集 | `utf8mb4` |
| 排序规则 | `utf8mb4_unicode_ci` |
| 引擎 | InnoDB |
| MySQL 版本 | 8.0+ |

## 二、表清单

| 序号 | 表名 | 说明 |
|---|---|---|
| 1 | `users` | 用户表 |
| 2 | `agents` | 客服坐席表 |
| 3 | `intents` | 意图配置表 |
| 4 | `products` | 商品表 |
| 5 | `sessions` | 会话表 |
| 6 | `orders` | 订单表 |
| 7 | `order_items` | 订单明细表 |
| 8 | `messages` | 消息表 |
| 9 | `knowledge` | 知识库表 |
| 10 | `conversation_ratings` | 会话评分表 |
| 11 | `tickets` | 工单表 |
| 12 | `ticket_logs` | 工单处理日志表 |

## 三、ER 关系

```text
users ──1:N──> sessions ──1:N──> messages ──N:1──> intents
  │               │
  │               └──1:N──> conversation_ratings
  │               └──N:1──> agents
  │
  ├──1:N──> orders ──1:N──> order_items ──N:1──> products
  │
  └──1:N──> tickets ──1:N──> ticket_logs
                ├──N:1──> agents
                └──N:1──> orders
```

## 四、表结构

### 4.1 users（用户表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 用户ID |
| username | VARCHAR(50) UNIQUE | 用户名 |
| password_hash | VARCHAR(255) | 密码哈希 |
| email | VARCHAR(100) UNIQUE | 邮箱 |
| phone | VARCHAR(20) UNIQUE | 手机号 |
| user_type | ENUM | customer/agent/admin |
| avatar_url | VARCHAR(500) | 头像URL |
| is_active | BOOLEAN | 是否激活 |
| status | TINYINT | 1正常 0禁用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 4.2 agents（客服坐席表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 客服ID |
| name | VARCHAR(50) | 姓名 |
| email | VARCHAR(100) | 邮箱 |
| description | VARCHAR(255) | 描述 |
| is_active | BOOLEAN | 是否启用 |
| status | ENUM | online/busy/offline |
| created_at | TIMESTAMP | 创建时间 |

### 4.3 intents（意图配置表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 意图ID |
| intent_name | VARCHAR(100) | 意图名称 |
| intent_code | VARCHAR(50) UNIQUE | 意图编码 |
| confidence | DECIMAL(5,4) | 默认置信度 |
| description | VARCHAR(255) | 描述 |
| handler_type | ENUM | rag/tool/transfer/fallback |
| handler_config | JSON | 处理配置 |
| sample_utterances | TEXT | 示例语料 |
| priority | INT | 优先级 |
| is_active | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 4.4 products（商品表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 商品ID |
| name | VARCHAR(200) | 商品名 |
| category | VARCHAR(50) | 分类 |
| price | DECIMAL(10,2) | 价格 |
| description | TEXT | 描述 |
| stock | INT | 库存 |
| images | JSON | 图片列表 |
| status | ENUM | on_sale/off_sale |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 4.5 sessions（会话表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 会话主键 |
| session_id | VARCHAR(64) UNIQUE | 会话业务ID |
| user_id | BIGINT FK | 用户ID |
| agent_id | BIGINT FK | 客服ID |
| status | ENUM | active/waiting/transferred/closed |
| channel | VARCHAR(20) | 来源渠道 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| ended_at | DATETIME | 结束时间 |
| last_message_at | DATETIME | 最后消息时间 |
| message_count | INT | 消息数 |
| satisfaction_score | TINYINT | 满意度（冗余） |

### 4.6 orders（订单表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 订单ID |
| order_no | VARCHAR(32) UNIQUE | 订单号 |
| user_id | BIGINT FK | 用户ID |
| status | ENUM | 见下方枚举 |
| total_amount | DECIMAL(10,2) | 总金额 |
| pay_amount | DECIMAL(10,2) | 实付金额 |
| shipping_address | JSON | 收货地址 |
| receiver_name | VARCHAR(50) | 收货人 |
| receiver_phone | VARCHAR(20) | 联系电话 |
| tracking_no | VARCHAR(50) | 物流单号 |
| remark | TEXT | 备注 |
| paid_at | DATETIME | 支付时间 |
| shipped_at | DATETIME | 发货时间 |
| delivered_at | DATETIME | 收货时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**status 枚举**：pending/paid/shipped/delivered/completed/cancelled/refunding/refunded

### 4.7 order_items（订单明细表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 明细ID |
| order_id | BIGINT FK | 订单ID |
| product_id | BIGINT FK | 商品ID |
| quantity | INT | 数量 |
| unit_price | DECIMAL(10,2) | 单价 |

### 4.8 messages（消息表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 消息ID |
| session_id | VARCHAR(64) FK | 会话业务ID |
| sender_type | ENUM | user/bot/agent |
| sender_id | BIGINT | 发送方ID |
| content | TEXT | 内容 |
| content_type | ENUM | text/image/voice/file/quick_reply |
| intent_id | BIGINT FK | 意图ID |
| intent_confidence | DECIMAL(5,4) | 意图置信度 |
| sentiment | ENUM | positive/neutral/negative |
| sentiment_score | DECIMAL(3,2) | 情感得分 |
| is_human_transfer | BOOLEAN | 是否转人工 |
| is_generated | BOOLEAN | 是否 AI 生成 |
| metadata | JSON | 元数据（token 消耗等） |
| created_at | DATETIME | 创建时间 |

**索引**：`idx_session_created (session_id, created_at)`

### 4.9 knowledge（知识库表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 知识ID |
| category | VARCHAR(50) | 分类 |
| question | TEXT | 问题 |
| answer | TEXT | 答案 |
| keywords | VARCHAR(500) | 关键词 |
| vector_id | VARCHAR(100) | Milvus 向量ID |
| embedding_model | VARCHAR(50) | 嵌入模型 |
| hit_count | INT | 命中次数 |
| satisfaction_rate | DECIMAL(5,2) | 满意度 |
| is_active | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 4.10 conversation_ratings（会话评分表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 评分ID |
| session_id | VARCHAR(64) FK | 会话ID |
| rating_score | TINYINT | 1-5 |
| rating_comment | TEXT | 评价内容 |
| rating_time | TIMESTAMP | 评分时间 |

### 4.11 tickets（工单表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 工单ID |
| ticket_no | VARCHAR(32) UNIQUE | 工单号 |
| session_id | VARCHAR(64) | 会话ID |
| user_id | BIGINT FK | 用户ID |
| order_id | BIGINT FK | 关联订单 |
| type | ENUM | complaint/refund/consult/suggestion/other |
| title | VARCHAR(200) | 标题 |
| content | TEXT | 内容 |
| status | ENUM | pending/processing/resolved/closed |
| priority | ENUM | low/normal/high/urgent |
| assigned_to | BIGINT FK | 处理客服 |
| resolution | TEXT | 处理结果 |
| resolved_at | DATETIME | 解决时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 4.12 ticket_logs（工单处理日志表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | 日志ID |
| ticket_id | BIGINT FK | 工单ID |
| operator_type | ENUM | user/agent/system |
| operator_id | BIGINT | 操作人ID |
| action | VARCHAR(50) | 操作类型 |
| content | TEXT | 操作内容 |
| created_at | TIMESTAMP | 创建时间 |

## 五、常见 SQL

### 查询用户所有会话

```sql
SELECT s.session_id, s.status, s.message_count, s.created_at
FROM sessions s
WHERE s.user_id = 1
ORDER BY s.created_at DESC;
```

### 查询某会话的所有消息

```sql
SELECT sender_type, content, sentiment, created_at
FROM messages
WHERE session_id = 'sess_xxx'
ORDER BY created_at;
```

### 查询待处理工单

```sql
SELECT ticket_no, type, title, priority, created_at
FROM tickets
WHERE status = 'pending'
ORDER BY priority DESC, created_at;
```

### 意图命中统计

```sql
SELECT i.intent_name, COUNT(m.id) AS count
FROM messages m
JOIN intents i ON m.intent_id = i.id
GROUP BY i.intent_name
ORDER BY count DESC;
```

### 情感分布统计

```sql
SELECT sentiment, COUNT(*) AS count
FROM messages
WHERE sender_type = 'user'
GROUP BY sentiment;
```
# API 接口规范

## 基础信息

| 项 | 值 |
|---|---|
| Base URL | `http://localhost:8000/api/v1` |
| 认证方式 | JWT（Bearer Token） |
| 请求格式 | JSON（登录接口除外，用 form-urlencoded） |
| 响应格式 | JSON |
| 流式响应 | SSE（text/event-stream） |

## 认证

除注册、登录、健康检查外，所有接口都需要在请求头带：

```http
Authorization: Bearer <access_token>
```

Token 有效期：24 小时（可配置）。

---

## 1. 认证接口

### 1.1 注册

**POST** `/auth/register`

请求体（JSON）：

```json
{
  "username": "testuser",
  "password": "test123456",
  "email": "test@example.com",
  "phone": "13800138000"
}
```

响应 200：

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "testuser"
}
```

错误：
- 400：用户名已存在
- 422：参数校验失败

### 1.2 登录

**POST** `/auth/login`

**注意**：必须用 `application/x-www-form-urlencoded` 格式，不是 JSON。

请求体：

```text
username=testuser&password=test123456
```

响应 200：

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "testuser"
}
```

错误：
- 401：用户名或密码错误
- 422：格式错误

---

## 2. 对话接口

### 2.1 同步对话

**POST** `/chat`

请求体：

```json
{
  "message": "你好",
  "session_id": "sess_xxx"
}
```

响应 200：

```json
{
  "session_id": "sess_xxx",
  "content": "您好，我是智能客服...",
  "intent_code": "FALLBACK",
  "sentiment": "positive"
}
```

### 2.2 流式对话（SSE）

**POST** `/chat/stream`

请求体同上。

响应（text/event-stream）：

```text
data: {"session_id": "sess_xxx"}
data: {"delta": "您好"}
data: {"delta": "，我是"}
data: {"delta": "智能客服"}
data: {"done": true, "intent_code": "FALLBACK"}
```

---

## 3. 意图接口

### 3.1 意图识别调试

**POST** `/intent/classify`

请求体：

```json
{"text": "我想查订单"}
```

响应：

```json
{
  "intent_code": "ORD_001",
  "intent_name": "订单查询",
  "confidence": 0.95,
  "entities": [],
  "slots": {}
}
```

### 3.2 列出意图

**GET** `/intent/list`

响应：意图数组。

### 3.3 创建意图

**POST** `/intent/create`

### 3.4 更新意图

**PUT** `/intent/{intent_id}`

### 3.5 删除意图

**DELETE** `/intent/{intent_id}`

---

## 4. 客服接口

### 4.1 列出客服

**GET** `/agent/list`

### 4.2 创建客服

**POST** `/agent/create`

### 4.3 更新客服

**PUT** `/agent/{agent_id}`

### 4.4 客服负责的会话

**GET** `/agent/{agent_id}/sessions`

---

## 5. 知识库接口

### 5.1 列出知识

**GET** `/knowledge/list?category=faqs`

响应：

```json
{
  "items": [
    {
      "id": 1,
      "category": "faqs",
      "question": "怎么申请退款",
      "answer": "在订单详情页...",
      "vector_id": "xxx"
    }
  ],
  "total": 1
}
```

---

## 6. 订单接口

### 6.1 查询订单

**GET** `/order/{order_no}`

### 6.2 列出订单

**GET** `/order/list/all?status=paid`

### 6.3 更新订单

**PUT** `/order/{order_no}`

---

## 7. 商品接口

### 7.1 搜索商品

**GET** `/product/search?keyword=耳机&limit=5`

### 7.2 商品详情

**GET** `/product/{product_id}`

### 7.3 创建商品

**POST** `/product/create`

### 7.4 更新商品

**PUT** `/product/{product_id}`

---

## 8. 数据分析接口

### 8.1 总览统计

**GET** `/analytics/overview`

响应：

```json
{
  "session_count": 10,
  "message_count": 42,
  "ticket_count": 2,
  "avg_rating": 4.5
}
```

### 8.2 情感分布

**GET** `/analytics/sentiment`

响应：

```json
{
  "positive": 20,
  "neutral": 15,
  "negative": 7
}
```

### 8.3 意图分布

**GET** `/analytics/intents`

### 8.4 最近会话

**GET** `/analytics/sessions/recent?limit=10`

---

## 9. 健康检查

**GET** `/health`

响应：

```json
{"status": "ok"}
```

---

## 错误响应格式

所有错误返回统一格式：

```json
{
  "detail": "错误描述"
}
```

或 Pydantic 校验失败：

```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "String should have at least 6 characters",
      "type": "string_too_short"
    }
  ]
}
```

## 状态码

| 码 | 含义 |
|---|---|
| 200 | 成功 |
| 400 | 请求错误 |
| 401 | 未认证 / Token 失效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 参数校验失败 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |
#!/bin/bash
# ============================================================
# API 测试脚本
# 用途：一键测试后端所有主要接口
# 用法：bash scripts/test_api.sh
# 前置：后端已在 8000 端口运行
# ============================================================

BASE_URL="http://127.0.0.1:8000"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }
info() { echo -e "${YELLOW}[TEST]${NC} $1"; }

# 测试计数器
PASSED=0
FAILED=0

# 断言响应中包含字符串
assert_contains() {
    local response="$1"
    local expected="$2"
    local name="$3"
    if echo "$response" | grep -q "$expected"; then
        pass "$name"
        PASSED=$((PASSED + 1))
    else
        fail "$name — 期望包含 '$expected'，实际：$response"
        FAILED=$((FAILED + 1))
    fi
}

# ============ 1. 健康检查 ============
info "1. 健康检查"
RESP=$(curl -s "${BASE_URL}/health")
assert_contains "$RESP" "ok" "GET /health"

# ============ 2. 注册用户 ============
info "2. 注册用户"
USERNAME="test_$(date +%s)"
RESP=$(curl -s -X POST "${BASE_URL}/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${USERNAME}\",\"password\":\"test123456\"}")
assert_contains "$RESP" "access_token" "POST /auth/register"

# 提取 token
TOKEN=$(echo "$RESP" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -z "$TOKEN" ]; then
    fail "无法提取 token，后续测试中止"
    exit 1
fi
info "Token: ${TOKEN:0:30}..."

# ============ 3. 登录 ============
info "3. 登录"
RESP=$(curl -s -X POST "${BASE_URL}/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=${USERNAME}&password=test123456")
assert_contains "$RESP" "access_token" "POST /auth/login"

# ============ 4. 未授权访问 ============
info "4. 未授权访问"
RESP=$(curl -s -X POST "${BASE_URL}/api/v1/chat" \
    -H "Content-Type: application/json" \
    -d '{"message":"你好"}')
assert_contains "$RESP" "Not authenticated" "未带 token 返回 401"

# ============ 5. 同步对话 ============
info "5. 同步对话"
RESP=$(curl -s -X POST "${BASE_URL}/api/v1/chat" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -d '{"message":"你好"}')
assert_contains "$RESP" "content" "POST /chat"

# ============ 6. 意图识别 ============
info "6. 意图识别"
RESP=$(curl -s -X POST "${BASE_URL}/api/v1/chat" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -d '{"message":"我想查一下订单号是 ORDER20260315001 的物流"}')
assert_contains "$RESP" "intent_code" "识别意图"

# ============ 7. 意图配置列表 ============
info "7. 意图配置列表"
RESP=$(curl -s "${BASE_URL}/api/v1/intent/list" \
    -H "Authorization: Bearer ${TOKEN}")
assert_contains "$RESP" "intent_code" "GET /intent/list"

# ============ 8. 知识库列表 ============
info "8. 知识库列表"
RESP=$(curl -s "${BASE_URL}/api/v1/knowledge/list" \
    -H "Authorization: Bearer ${TOKEN}")
assert_contains "$RESP" "items" "GET /knowledge/list"

# ============ 9. 数据分析 ============
info "9. 数据分析总览"
RESP=$(curl -s "${BASE_URL}/api/v1/analytics/overview" \
    -H "Authorization: Bearer ${TOKEN}")
assert_contains "$RESP" "session_count" "GET /analytics/overview"

# ============ 10. 流式对话 ============
info "10. 流式对话（SSE）"
RESP=$(curl -s -N -X POST "${BASE_URL}/api/v1/chat/stream" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -d '{"message":"你好"}' \
    --max-time 30 | head -20)
assert_contains "$RESP" "data:" "POST /chat/stream"

# ============ 汇总 ============
echo ""
echo "============================================"
echo -e "测试结果：${GREEN}通过 ${PASSED}${NC} / ${RED}失败 ${FAILED}${NC}"
echo "============================================"

if [ $FAILED -gt 0 ]; then
    exit 1
fi
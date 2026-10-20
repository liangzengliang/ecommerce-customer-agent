<template>
  <div class="chat-page">
    <!-- ========== 左侧：会话列表 ========== -->
    <aside class="session-sidebar">
      <div class="sidebar-header">
        <div class="title-row">
          <h3>智能客服</h3>
          <el-button type="primary" size="small" :icon="Plus" @click="handleNewSession">
            新会话
          </el-button>
        </div>
        <div class="count">{{ sessions.length }} 个会话 · 近一个月</div>
      </div>

      <div class="session-list" v-loading="sessionsLoading">
        <div
          v-for="s in sessions"
          :key="s.session_id"
          class="session-item"
          :class="{ active: s.session_id === currentSessionId }"
          @click="switchSession(s)"
        >
          <div class="item-header">
            <el-icon v-if="s.is_pinned" class="pin-icon" :size="12">
              <StarFilled />
            </el-icon>

            <span class="item-title">{{ s.title }}</span>

            <span
              class="item-status"
              :class="s.session_id === currentSessionId ? 'active' : 'completed'"
            >
              {{ s.session_id === currentSessionId ? '进行中' : '已结束' }}
            </span>

            <el-dropdown
              trigger="click"
              placement="bottom-end"
              @command="(cmd: string) => handleCommand(cmd, s)"
              @click.stop
            >
              <el-icon class="more-btn" :size="14" @click.stop>
                <MoreFilled />
              </el-icon>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="rename">
                    <el-icon><EditPen /></el-icon>
                    <span>重命名</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="pin">
                    <el-icon>
                      <Star v-if="!s.is_pinned" />
                      <StarFilled v-else />
                    </el-icon>
                    <span>{{ s.is_pinned ? '取消置顶' : '置顶' }}</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>
                    <el-icon><Delete /></el-icon>
                    <span>删除</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="item-preview">{{ s.preview }}</div>
          <div class="item-footer">
            <span class="msg-count">{{ s.message_count }} 条消息</span>
            <span class="time">{{ s.updated_at }}</span>
          </div>
        </div>

        <el-empty
          v-if="!sessionsLoading && sessions.length === 0"
          description="最近一个月暂无会话"
          :image-size="80"
        />
      </div>
    </aside>

    <!-- ========== 中间：对话区 ========== -->
    <main class="chat-main">
      <header class="chat-header">
        <div class="header-left">
          <span class="session-title">{{ currentSessionTitle }}</span>
          <span class="status-badge active">进行中</span>
        </div>
        <div class="header-right">
          <el-button text @click="router.push('/dashboard')">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据看板</span>
          </el-button>
          <el-button type="primary" plain @click="router.push('/dashboard')">
            <el-icon><HomeFilled /></el-icon>
            <span>返回首页</span>
          </el-button>
        </div>
      </header>

      <!-- ========== 演示版提示条 ========== -->
      <div class="demo-tips">
        <div class="demo-tip tip-llm">
          <el-icon><Warning /></el-icon>
          <span>请配置大模型 Key，聊天才能启动 LLM 回答；未配置时仅为模板回答。</span>
        </div>
        <div class="demo-tip tip-orders">
          <el-icon><Document /></el-icon>
          <span>演示版只有 ORDER20261001001 ~ ORDER20261001010 有基础订单数据，可输入订单号继续查询。</span>
        </div>
      </div>

      <div class="message-area" ref="messageAreaRef">
        <div v-if="messages.length === 0" class="empty-chat">
          <el-icon :size="56" color="#cbd5e1"><ChatDotRound /></el-icon>
          <h3>您好，我是电商智能客服</h3>
          <p>可以帮您查询订单、物流、退款、商品信息等</p>
        </div>

        <template v-else>
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="message-row"
            :class="`role-${msg.role}`"
          >
            <div v-if="msg.role !== 'user'" class="msg-avatar ai-avatar">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none"
                   stroke="currentColor" stroke-width="2" stroke-linecap="round"
                   stroke-linejoin="round">
                <path d="M3 18v-6a9 9 0 0 1 18 0v6" />
                <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" />
              </svg>
            </div>

            <div class="msg-bubble">
              <div class="bubble-content">
                <span v-if="msg.loading && !msg.content" class="typing">
                  <span></span><span></span><span></span>
                </span>
                <span v-else v-html="renderContent(msg)"></span>
                <span v-if="msg.loading && msg.content" class="cursor">▍</span>
              </div>
            </div>

            <div v-if="msg.role === 'user'" class="msg-avatar user-avatar">
              <span>{{ userInitial }}</span>
            </div>
          </div>
        </template>
      </div>

      <!-- ========== 快捷查询 ========== -->
      <div class="quick-actions">
        <span class="qa-label">快捷查询：</span>
        <div class="qa-list">
          <div
            v-for="act in quickActions"
            :key="act.label"
            class="qa-item"
            @click="handleSend(act.text)"
          >
            <el-icon :size="13"><component :is="act.icon" /></el-icon>
            <span>{{ act.label }}</span>
          </div>
        </div>
      </div>

      <!-- ========== 免责声明 ========== -->
      <div class="disclaimer">
        <el-icon><Warning /></el-icon>
        <span>回答由 AI 自动生成，仅供参考。如需人工服务，请输入"人工客服"。</span>
      </div>

      <!-- ========== 输入区 ========== -->
      <div class="input-area">
        <transition name="fade">
          <div v-if="showHistory && historyList.length > 0" class="history-panel">
            <div class="history-header">
              <span>历史提问</span>
              <el-button text size="small" @click="handleClearHistory">
                清空
              </el-button>
            </div>
            <div class="history-list">
              <div
                v-for="(h, i) in historyList"
                :key="i"
                class="history-item"
                @click="pickHistory(h.text)"
              >
                <el-icon><Clock /></el-icon>
                <span class="text">{{ h.text }}</span>
                <span v-if="h.count && h.count > 1" class="count">
                  {{ h.count }}次
                </span>
              </div>
            </div>
          </div>
        </transition>

        <div class="input-wrapper">
          <el-input
            v-model="inputText"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 4 }"
            resize="none"
            placeholder="请描述您的问题，例如：我想查订单 ORDER20261001001"
            @keydown.enter="handleEnter"
            @focus="showHistory = true"
            @blur="handleBlur"
          />
          <el-button
            type="primary"
            class="send-btn"
            :loading="loading"
            :disabled="!inputText.trim()"
            @click="handleSend(inputText)"
          >
            发送
          </el-button>
        </div>
      </div>
    </main>

    <!-- ========== 右侧信息栏 ========== -->
    <aside class="info-sidebar">
      <div class="info-card">
        <div class="card-header">
          <span class="card-title">高频问题推荐</span>
          <el-button text size="small" :icon="Refresh" @click="refreshHotQuestions">
            刷新
          </el-button>
        </div>
        <div class="hot-list">
          <div
            v-for="(q, i) in hotQuestions"
            :key="q.text"
            class="hot-item"
            @click="handleSend(q.text)"
          >
            <span class="rank" :class="`rank-${i + 1}`">{{ i + 1 }}</span>
            <span class="text">{{ q.text }}</span>
            <span class="count">{{ q.count }}次</span>
          </div>
        </div>
      </div>

      <div class="info-card">
        <div class="card-header">
          <span class="card-title">Agent 能力说明</span>
        </div>
        <div class="ability-list">
          <div v-for="a in abilities" :key="a.label" class="ability-item">
            <span class="ability-tag" :class="a.color">{{ a.label }}</span>
            <span class="ability-desc">{{ a.desc }}</span>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, DataAnalysis, HomeFilled, ChatDotRound, Warning, Refresh, Clock,
  Document, Van, Money, Goods, Service,
  MoreFilled, EditPen, StarFilled, Star, Delete,
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'
import {
  listSessions,
  getSessionMessages,
  renameSession,
  pinSession,
  deleteSession,
  type SessionItem,
} from '@/api/session'
import { addHistory, getTopHistory, clearHistory, type QuestionRecord } from '@/utils/history'

const router = useRouter()
const chatStore = useChatStore()
const userStore = useUserStore()

const inputText = ref('')
const messageAreaRef = ref<HTMLElement>()
const currentSessionId = ref('')
const sessionsLoading = ref(false)

// ============ 快捷查询 ============
const quickActions = [
  { label: '查订单', text: '我想查订单 ORDER20261001001 的详细信息', icon: Document },
  { label: '查物流', text: '我的快递到哪了', icon: Van },
  { label: '申请退款', text: '我要申请退款', icon: Money },
  { label: '商品咨询', text: '无线耳机续航多久', icon: Goods },
  { label: '人工客服', text: '转人工客服', icon: Service },
]

// ============ 会话列表 ============
const sessions = ref<SessionItem[]>([])

async function loadSessions() {
  sessionsLoading.value = true
  try {
    const res = await listSessions(30)
    const all = res.items || []
    // 过滤空会话
    sessions.value = all.filter((s) => (s.message_count || 0) > 0)

    // 保持当前选中，或自动选第一条
    if (currentSessionId.value) {
      const exists = sessions.value.find((s) => s.session_id === currentSessionId.value)
      if (!exists && sessions.value.length > 0) {
        currentSessionId.value = sessions.value[0].session_id
        chatStore.sessionId = sessions.value[0].session_id
      }
    } else if (sessions.value.length > 0) {
      currentSessionId.value = sessions.value[0].session_id
      chatStore.sessionId = sessions.value[0].session_id
    }
  } catch (e) {
    console.error('加载会话失败', e)
  } finally {
    sessionsLoading.value = false
  }
}

const currentSessionTitle = computed(() => {
  const s = sessions.value.find((x) => x.session_id === currentSessionId.value)
  return s?.title || '新会话'
})

const userInitial = computed(() => {
  const name = userStore.username || 'User'
  return name.charAt(0).toUpperCase()
})

// ============ 历史提问 ============
const showHistory = ref(false)
const historyList = ref<QuestionRecord[]>([])

function loadHistory() {
  historyList.value = getTopHistory(8)
}

function pickHistory(text: string) {
  inputText.value = text
  showHistory.value = false
}

function handleBlur() {
  setTimeout(() => {
    showHistory.value = false
  }, 200)
}

async function handleClearHistory() {
  try {
    await ElMessageBox.confirm('确定清空历史提问记录？', '提示', { type: 'warning' })
    clearHistory()
    historyList.value = []
    ElMessage.success('已清空')
  } catch (e) {}
}

// ============ 高频问题 ============
const hotQuestions = ref([
  { text: '怎么查询订单状态', count: 5 },
  { text: '退款多久到账', count: 4 },
  { text: '耳机续航多久', count: 3 },
  { text: '物流到哪了', count: 3 },
  { text: '电脑保修多久', count: 2 },
  { text: '怎么联系人工客服', count: 2 },
])

function refreshHotQuestions() {
  hotQuestions.value = [...hotQuestions.value]
    .sort(() => Math.random() - 0.5)
    .map((q) => ({ ...q, count: Math.max(1, q.count + Math.floor(Math.random() * 3) - 1) }))
  ElMessage.success('已刷新')
}

// ============ Agent 能力 ============
const abilities = [
  { label: '商品咨询', desc: '手机、电脑、耳机等商品知识库', color: 'blue' },
  { label: '订单查询', desc: '订单状态、物流、收货信息', color: 'green' },
  { label: '售后支持', desc: '退款、退货、保修、工单处理', color: 'orange' },
  { label: '多轮追问', desc: '自动记忆上下文，无需重复描述', color: 'gray' },
]

// ============ 消息 ============
const messages = computed(() => chatStore.messages)
const loading = computed(() => chatStore.loading)

function renderContent(msg: any): string {
  if (msg.role === 'bot') {
    return marked.parse(msg.content || '') as string
  }
  return (msg.content || '')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
}

// ============ 发送 ============
async function handleSend(text: string) {
  const value = (text || '').trim()
  if (!value || loading.value) return

  inputText.value = ''
  showHistory.value = false

  addHistory(value)
  loadHistory()

  await chatStore.sendMessage(value)

  if (chatStore.sessionId && chatStore.sessionId !== currentSessionId.value) {
    currentSessionId.value = chatStore.sessionId
  }

  await scrollToBottom()
  await loadSessions()
}

function handleEnter(e: KeyboardEvent) {
  if (e.shiftKey) return
  e.preventDefault()
  handleSend(inputText.value)
}

async function scrollToBottom() {
  await nextTick()
  if (messageAreaRef.value) {
    messageAreaRef.value.scrollTop = messageAreaRef.value.scrollHeight
  }
}

watch(() => messages.value.length, () => scrollToBottom())
watch(
  () => messages.value[messages.value.length - 1]?.content,
  () => scrollToBottom(),
)

// ============ 新会话 ============
function handleNewSession() {
  chatStore.clear()
  currentSessionId.value = ''
  ElMessage.success('已开启新会话')
}

// ============ 切换会话 ============
async function switchSession(s: SessionItem) {
  if (s.session_id === currentSessionId.value) return

  currentSessionId.value = s.session_id
  chatStore.sessionId = s.session_id
  chatStore.messages.splice(0, chatStore.messages.length)

  try {
    const res = await getSessionMessages(s.session_id)
    for (const m of res.messages) {
      chatStore.messages.push({
        id: m.id,
        role: m.role,
        content: m.content,
        sentiment: m.sentiment as any,
      })
    }
    await scrollToBottom()
  } catch (e) {
    ElMessage.error('加载历史消息失败')
  }
}

// ============ 会话操作：重命名/置顶/删除 ============
function handleCommand(cmd: string, s: SessionItem) {
  if (cmd === 'rename') handleRename(s)
  else if (cmd === 'pin') handlePin(s)
  else if (cmd === 'delete') handleDeleteSession(s)
}

async function handleRename(s: SessionItem) {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的会话名称', '重命名', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: s.title,
      inputValidator: (v: string) => {
        if (!v || !v.trim()) return '名称不能为空'
        if (v.length > 50) return '名称不能超过 50 字'
        return true
      },
    })
    await renameSession(s.session_id, value.trim())
    ElMessage.success('已重命名')
    await loadSessions()
  } catch (e: any) {
    if (e !== 'cancel' && e !== 'close') {
      ElMessage.error(e?.response?.data?.detail || '操作失败')
    }
  }
}

async function handlePin(s: SessionItem) {
  try {
    await pinSession(s.session_id, !s.is_pinned)
    ElMessage.success(s.is_pinned ? '已取消置顶' : '已置顶')
    await loadSessions()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '操作失败')
  }
}

async function handleDeleteSession(s: SessionItem) {
  try {
    await ElMessageBox.confirm(
      `确定删除会话「${s.title}」？删除后不可恢复。`,
      '删除会话',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger',
      },
    )
  } catch {
    return
  }

  try {
    await deleteSession(s.session_id)
    ElMessage.success('已删除')

    if (s.session_id === currentSessionId.value) {
      currentSessionId.value = ''
      chatStore.clear()
    }
    await loadSessions()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

// ============ 初始化 ============
onMounted(async () => {
  await loadSessions()
  loadHistory()
  await scrollToBottom()
})
</script>

<style scoped lang="scss">
.chat-page {
  display: flex;
  height: 100vh;
  background: #f7f8fa;
}

// ========== 左侧 ==========
.session-sidebar {
  width: 260px;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;

  .sidebar-header {
    padding: 16px;
    border-bottom: 1px solid #f1f5f9;

    .title-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 6px;

      h3 { margin: 0; font-size: 15px; font-weight: 600; color: #1e293b; }
    }

    .count { font-size: 12px; color: #94a3b8; }
  }

  .session-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }

  .session-item {
    padding: 12px;
    border-radius: 10px;
    cursor: pointer;
    margin-bottom: 6px;
    border: 1px solid transparent;
    transition: all 0.2s ease;

    &:hover { background: #f8fafc; }
    &.active { background: #eff6ff; border-color: #bfdbfe; }

    .item-header {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 6px;

      .pin-icon {
        color: #f59e0b;
        flex-shrink: 0;
      }

      .item-title {
        font-size: 13px;
        font-weight: 600;
        color: #1e293b;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
        min-width: 0;
      }

      .item-status {
        font-size: 11px;
        padding: 1px 6px;
        border-radius: 4px;
        flex-shrink: 0;

        &.active { background: #dbeafe; color: #1e40af; }
        &.completed { background: #f1f5f9; color: #64748b; }
      }

      .more-btn {
        color: #94a3b8;
        cursor: pointer;
        padding: 2px;
        border-radius: 4px;
        opacity: 0;
        transition: all 0.15s ease;
        flex-shrink: 0;

        &:hover {
          background: #e5e7eb;
          color: #1e293b;
        }
      }
    }

    &:hover .more-btn {
      opacity: 1;
    }

    .item-preview {
      font-size: 12.5px;
      color: #64748b;
      margin-bottom: 6px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .item-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 11.5px;
      color: #94a3b8;
    }
  }
}

// ========== 中间 ==========
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #fff;
}

.chat-header {
  height: 56px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;

    .session-title { font-size: 15px; font-weight: 600; color: #1e293b; }

    .status-badge {
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 4px;
      &.active { background: #dbeafe; color: #1e40af; }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.demo-tips {
  padding: 8px 20px 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: #fff;
  flex-shrink: 0;
}

.demo-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  padding: 6px 10px;
  border-radius: 6px;
  line-height: 1.4;
}

.tip-llm {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
}

.tip-orders {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
}

.message-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 20px;
}

.empty-chat {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  gap: 12px;

  h3 { margin: 12px 0 0; font-size: 18px; color: #475569; font-weight: 600; }
  p { margin: 0; font-size: 13.5px; }
}

.message-row {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;

  &.role-user {
    flex-direction: row-reverse;
    .msg-bubble { align-items: flex-end; }
    .bubble-content {
      background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
      color: #fff;
      border-radius: 12px 2px 12px 12px;
    }
  }

  &.role-bot .bubble-content {
    background: #f8fafc;
    color: #1e293b;
    border-radius: 2px 12px 12px 12px;
    border: 1px solid #f1f5f9;
  }
}

.msg-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 700;
  color: #fff;

  &.ai-avatar {
    background: #22c55e;
    box-shadow: 0 2px 6px rgba(34, 197, 94, 0.3);
  }

  &.user-avatar {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  }
}

.msg-bubble {
  display: flex;
  flex-direction: column;
  max-width: 70%;

  .bubble-content {
    padding: 10px 14px;
    line-height: 1.7;
    font-size: 14px;
    word-break: break-word;

    :deep(p) { margin: 0 0 8px; &:last-child { margin-bottom: 0; } }
    :deep(code) {
      background: rgba(0, 0, 0, 0.08);
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'Consolas', monospace;
      font-size: 13px;
    }
    :deep(ul), :deep(ol) { margin: 6px 0; padding-left: 20px; }

    .cursor { animation: blink 1s infinite; margin-left: 2px; }

    .typing {
      display: inline-flex;
      gap: 4px;
      padding: 4px 0;

      span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #94a3b8;
        animation: bounce 1.4s infinite ease-in-out;

        &:nth-child(2) { animation-delay: 0.2s; }
        &:nth-child(3) { animation-delay: 0.4s; }
      }
    }
  }
}

// ========== 快捷查询 ==========
.quick-actions {
  padding: 10px 20px 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-top: 1px solid #f1f5f9;
  background: #fff;
  flex-shrink: 0;
  flex-wrap: wrap;

  .qa-label {
    font-size: 12.5px;
    color: #94a3b8;
    flex-shrink: 0;
  }

  .qa-list {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .qa-item {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 14px;
    background: #f0fdf4;
    color: #16a34a;
    font-size: 12.5px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;

    &:hover {
      background: #dcfce7;
      border-color: #86efac;
      transform: translateY(-1px);
    }

    .el-icon { font-size: 13px; }
  }
}

// ========== 免责声明 ==========
.disclaimer {
  padding: 6px 20px 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  color: #94a3b8;
  background: #fff;
  flex-shrink: 0;

  .el-icon { color: #cbd5e1; }
}

// ========== 输入区 ==========
.input-area {
  padding: 0 20px 20px;
  background: #fff;
  flex-shrink: 0;
  position: relative;

  .history-panel {
    position: absolute;
    bottom: 100%;
    left: 20px;
    right: 20px;
    margin-bottom: 8px;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
    max-height: 260px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    z-index: 100;

    .history-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 12px;
      border-bottom: 1px solid #f1f5f9;
      font-size: 12.5px;
      color: #64748b;
      font-weight: 500;
    }

    .history-list {
      overflow-y: auto;
      padding: 4px;

      .history-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 10px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        color: #475569;
        transition: background 0.15s;

        &:hover { background: #f0fdf4; color: #16a34a; }

        .el-icon { color: #94a3b8; flex-shrink: 0; }

        .text {
          flex: 1;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .count { font-size: 11px; color: #94a3b8; flex-shrink: 0; }
      }
    }
  }

  .input-wrapper {
    display: flex;
    gap: 10px;
    padding: 8px 12px;
    background: #f8fafc;
    border: 1.5px solid #e5e7eb;
    border-radius: 12px;
    transition: all 0.2s ease;

    &:focus-within {
      border-color: #22c55e;
      background: #fff;
      box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
    }

    :deep(.el-textarea__inner) {
      background: transparent;
      border: none;
      box-shadow: none;
      font-size: 14px;
      padding: 6px 0;
      color: #1e293b;

      &::placeholder { color: #94a3b8; }
    }

    .send-btn {
      align-self: flex-end;
      background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
      border: none;
      border-radius: 8px;
      padding: 8px 20px;
      font-weight: 500;

      &:hover:not(:disabled) {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
      }

      &:disabled { opacity: 0.4; }
    }
  }
}

// ========== 右侧 ==========
.info-sidebar {
  width: 230px;
  background: #f7f8fa;
  border-left: 1px solid #e5e7eb;
  overflow-y: auto;
  padding: 10px;
  flex-shrink: 0;

  .info-card {
    background: #fff;
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 10px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;

      .card-title { font-size: 12.5px; font-weight: 600; color: #1e293b; }

      :deep(.el-button) { font-size: 11px; padding: 2px 6px; height: 20px; }
    }
  }

  .hot-list {
    display: flex;
    flex-direction: column;
    gap: 1px;

    .hot-item {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 5px 3px;
      border-radius: 5px;
      cursor: pointer;
      transition: all 0.15s ease;

      &:hover {
        background: #f8fafc;
        .text { color: #22c55e; }
      }

      .rank {
        width: 15px;
        height: 15px;
        border-radius: 3px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 9.5px;
        font-weight: 700;
        color: #fff;
        flex-shrink: 0;
        background: #cbd5e1;

        &.rank-1 { background: #ef4444; }
        &.rank-2 { background: #f59e0b; }
        &.rank-3 { background: #3b82f6; }
      }

      .text {
        flex: 1;
        font-size: 11.5px;
        color: #475569;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        transition: color 0.15s;
      }

      .count { font-size: 10px; color: #94a3b8; flex-shrink: 0; }
    }
  }

  .ability-list {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .ability-item {
      display: flex;
      flex-direction: column;
      gap: 3px;

      .ability-tag {
        align-self: flex-start;
        font-size: 10.5px;
        padding: 1px 6px;
        border-radius: 3px;
        font-weight: 500;
        line-height: 1.5;

        &.blue { background: #dbeafe; color: #1e40af; }
        &.green { background: #dcfce7; color: #15803d; }
        &.orange { background: #ffedd5; color: #c2410c; }
        &.gray { background: #f1f5f9; color: #475569; }
      }

      .ability-desc { font-size: 11px; color: #64748b; line-height: 1.5; }
    }
  }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes blink { 50% { opacity: 0; } }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.6; }
  40% { transform: scale(1); opacity: 1; }
}
</style>
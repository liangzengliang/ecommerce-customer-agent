/**
 * 对话状态
 * 管理消息列表、会话ID、加载状态、意图、情感
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { streamMessage } from '@/api/chat'
import type { Message, Sentiment } from '@/types/chat'

export const useChatStore = defineStore('chat', () => {
  // ===== 状态 =====
  const messages = ref<Message[]>([])
  // ★ 初始化时从 localStorage 读
   const sessionId = ref<string>(localStorage.getItem('current_session_id') || '')
  const loading = ref<boolean>(false)
  const currentIntent = ref<string>('')
  const currentSentiment = ref<Sentiment>('neutral')

  // ===== 计算属性 =====
  const messageCount = computed(() => messages.value.length)
  const lastMessage = computed(() => messages.value[messages.value.length - 1])

  // ===== 方法 =====

  /** 添加一条消息 */
  function addMessage(msg: Omit<Message, 'id'>) {
    messages.value.push({
      id: `msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      ...msg,
    })
  }

  /** 更新最后一条 bot 消息的内容（流式追加） */
  function appendToLastBot(delta: string) {
    const last = messages.value[messages.value.length - 1]
    if (last && last.role === 'bot') {
      last.content += delta
    }
  }

  /** 更新最后一条 bot 消息的 loading 状态 */
  function setLastBotLoading(value: boolean) {
    const last = messages.value[messages.value.length - 1]
    if (last && last.role === 'bot') {
      last.loading = value
    }
  }

  /**
   * 发送消息并接收流式回复
   * 关键：如果已有 session_id 就带上，避免后端每次都创建新会话
   */
  async function sendMessage(text: string) {
    if (loading.value) return
    loading.value = true

    // 1. 添加用户消息
    addMessage({ role: 'user', content: text })

    // 2. 添加空的 bot 消息占位
    addMessage({ role: 'bot', content: '', loading: true })

    // 3. 流式接收
    await streamMessage(
      // ★ 已有 session_id 就带上，没有就传 undefined（后端创建新会话）
      { message: text, session_id: sessionId.value || undefined },

      // onChunk：追加内容
      (delta) => appendToLastBot(delta),

      // onDone：结束处理
      (intentCode) => {
        setLastBotLoading(false)
        loading.value = false
        if (intentCode) currentIntent.value = intentCode
      },

      // ★ onSessionId：保存后端返回的会话ID
      (sid) => {
        if (sid && sid !== sessionId.value) {
          sessionId.value = sid
          console.log('[chat] session_id 已更新:', sid)
        }
      },

      // onError：错误处理
      (err) => {
        setLastBotLoading(false)
        loading.value = false
        appendToLastBot(`\n[错误] ${err.message}`)
      },
    )
  }

  /**
   * 清空对话（包括 session_id）
   * 用于"新会话"按钮
   */
  function clear() {
    messages.value = []
    sessionId.value = ''
    currentIntent.value = ''
    currentSentiment.value = 'neutral'
  }

  /**
   * 只清空消息，保留 session_id
   * 用于切换到某个历史会话时（消息会被重新拉取）
   */
  function clearMessages() {
    messages.value = []
    currentIntent.value = ''
    currentSentiment.value = 'neutral'
  }

  return {
    // 状态
    messages,
    sessionId,
    loading,
    currentIntent,
    currentSentiment,
    // 计算
    messageCount,
    lastMessage,
    // 方法
    addMessage,
    appendToLastBot,
    sendMessage,
    clear,
    clearMessages,
  }
})
/**
 * 对话逻辑复用
 * 把 store 的对话能力封装成组合式函数，供多个组件使用。
 */
import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'

export function useChat() {
  const store = useChatStore()

  const messages = computed(() => store.messages)
  const loading = computed(() => store.loading)

  /** 发送消息 */
  async function send(text: string) {
    await store.sendMessage(text)
  }

  /** 清空对话 */
  function clear() {
    store.clear()
  }

  return { messages, loading, send, clear }
}
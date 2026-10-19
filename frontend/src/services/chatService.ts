/**
 * 对话业务服务
 * 对 store 层做一层薄封装，方便组件直接调用。
 */
import { useChatStore } from '@/stores/chat'

export const chatService = {
  /** 发送消息 */
  async send(text: string) {
    const store = useChatStore()
    await store.sendMessage(text)
  },

  /** 清空对话 */
  clear() {
    const store = useChatStore()
    store.clear()
  },
}
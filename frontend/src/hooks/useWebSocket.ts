/**
 * WebSocket 连接复用
 * 用于需要实时双向通信的场景（如人工客服接管后）。
 */
import { ref, onUnmounted } from 'vue'

export function useWebSocket(url: string) {
  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const lastMessage = ref<string>('')

  /** 连接 */
  function connect() {
    ws.value = new WebSocket(url)
    ws.value.onopen = () => {
      connected.value = true
    }
    ws.value.onmessage = (event) => {
      lastMessage.value = event.data
    }
    ws.value.onclose = () => {
      connected.value = false
    }
  }

  /** 发送消息 */
  function send(data: string | object) {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) return
    ws.value.send(typeof data === 'string' ? data : JSON.stringify(data))
  }

  /** 断开连接 */
  function close() {
    ws.value?.close()
  }

  onUnmounted(() => close())

  return { connected, lastMessage, connect, send, close }
}
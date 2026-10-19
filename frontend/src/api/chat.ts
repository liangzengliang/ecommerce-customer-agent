/**
 * 对话相关接口
 */
import api from './index'
import type { ChatRequest, ChatResponse } from '@/types/chat'

/** 同步对话 */
export function sendMessage(params: ChatRequest) {
  return api.post<any, ChatResponse>('/chat', params)
}

/**
 * SSE 流式对话
 *
 * @param params      请求参数（message, session_id）
 * @param onChunk     收到内容片段时回调（用于逐字追加）
 * @param onDone      流结束时回调，参数是意图编码
 * @param onSessionId 后端首次返回 session_id 时回调（关键：保存会话ID）
 * @param onError     出错时回调
 */
export async function streamMessage(
  params: ChatRequest,
  onChunk: (delta: string) => void,
  onDone: (intentCode?: string) => void,
  onSessionId: (sessionId: string) => void,
  onError?: (err: Error) => void,
): Promise<void> {
  const token = localStorage.getItem('access_token')

  try {
    const response = await fetch('/api/v1/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      // 保留最后一行（可能不完整）
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6).trim()
        if (!payload) continue

        try {
          const chunk = JSON.parse(payload)

          // ★ 第一块返回 session_id：通知上层保存
          if (chunk.session_id) {
            onSessionId(chunk.session_id)
          }

          // 内容片段
          if (chunk.delta) {
            onChunk(chunk.delta)
          }

          // 结束标记
          if (chunk.done) {
            onDone(chunk.intent_code)
          }
        } catch (e) {
          console.warn('解析 SSE 数据失败:', payload)
        }
      }
    }
  } catch (err) {
    onError?.(err as Error)
  }
}
/**
 * 会话列表接口
 */
import api from './index'

export interface SessionItem {
  session_id: string
  title: string
  preview: string
  status: 'active' | 'completed'
  message_count: number
  is_pinned?: boolean
  custom_title?: string | null
  created_at: string
  updated_at: string
}

export interface SessionMessage {
  id: string
  role: 'user' | 'bot'
  content: string
  sentiment?: string
  created_at: string
}

/** 列出最近 N 天的会话 */
export function listSessions(days: number = 30) {
  return api.get<any, { items: SessionItem[]; total: number }>(
    '/sessions/list',
    { params: { days } },
  )
}

/** 拉取会话的历史消息 */
export function getSessionMessages(sessionId: string) {
  return api.get<any, { session_id: string; messages: SessionMessage[] }>(
    `/sessions/${sessionId}/messages`,
  )
}

/** 重命名会话 */
export function renameSession(sessionId: string, title: string) {
  return api.put(`/sessions/${sessionId}/rename`, { title })
}

/** 置顶/取消置顶 */
export function pinSession(sessionId: string, pinned: boolean) {
  return api.put(`/sessions/${sessionId}/pin`, { pinned })
}

/** 删除会话 */
export function deleteSession(sessionId: string) {
  return api.delete(`/sessions/${sessionId}`)
}
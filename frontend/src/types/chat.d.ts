/**
 * 对话相关类型定义
 */

/** 消息发送方 */
export type SenderType = 'user' | 'bot' | 'agent'

/** 消息内容类型 */
export type ContentType = 'text' | 'image' | 'voice' | 'file' | 'quick_reply'

/** 情感倾向 */
export type Sentiment = 'positive' | 'neutral' | 'negative'

/** 单条消息 */
export interface Message {
  id: string
  role: SenderType
  content: string
  contentType?: ContentType
  sentiment?: Sentiment
  createdAt?: string
  loading?: boolean       // 是否处于流式接收中
  references?: string[]   // 引用来源（RAG 检索结果）
}

/** 对话请求体 */
export interface ChatRequest {
  message: string
  session_id?: string
}

/** 对话响应体 */
export interface ChatResponse {
  session_id: string
  content: string
  intent_code?: string
  sentiment?: string
}

/** SSE 流式数据块 */
export interface StreamChunk {
  session_id?: string
  delta?: string
  done?: boolean
  intent_code?: string
}
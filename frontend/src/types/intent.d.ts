/**
 * 意图相关类型定义
 */

/** 意图信息 */
export interface Intent {
  id: number
  intent_name: string
  intent_code: string
  confidence: number
  description?: string
  handler_type: 'rag' | 'tool' | 'transfer' | 'fallback'
  handler_config?: Record<string, any>
  sample_utterances?: string
  priority: number
  is_active: boolean
  created_at: string
  updated_at: string
}

/** 实体 */
export interface Entity {
  type: string
  value: string
  normalized?: string
  start?: number
  end?: number
  confidence: number
  slot?: string
}

/** 意图识别响应 */
export interface IntentClassifyResponse {
  intent_code: string
  intent_name: string
  confidence: number
  entities?: Entity[]
  slots?: Record<string, any>
}
/**
 * Agent 相关类型定义
 */

/** Agent 状态 */
export type AgentStatus = 'online' | 'busy' | 'offline'

/** 客服信息 */
export interface Agent {
  id: number
  name: string
  email?: string
  description?: string
  is_active: boolean
  status: AgentStatus
  created_at: string
}

/** 会话状态 */
export type SessionStatus = 'active' | 'waiting' | 'transferred' | 'closed'

/** 会话信息 */
export interface Session {
  session_id: string
  user_id: number
  agent_id?: number
  status: SessionStatus
  channel: string
  message_count: number
  satisfaction_score?: number
  created_at: string
  updated_at: string
}

/** 工具调用结果 */
export interface ToolResult {
  tool: string
  result: Record<string, any>
}
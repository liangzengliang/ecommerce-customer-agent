/**
 * Agent 相关服务
 */
import api from '@/api'
import type { Agent } from '@/types/agent'

export const agentService = {
  /** 获取客服列表 */
  list(): Promise<Agent[]> {
    return api.get<any, Agent[]>('/agent/list')
  },

  /** 创建客服 */
  create(data: Partial<Agent>) {
    return api.post<any, Agent>('/agent/create', data)
  },

  /** 更新客服 */
  update(id: number, data: Partial<Agent>) {
    return api.put<any, Agent>(`/agent/${id}`, data)
  },
}
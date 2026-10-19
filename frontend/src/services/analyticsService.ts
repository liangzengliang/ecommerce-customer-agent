/**
 * 数据分析服务
 */
import api from '@/api'

/** 总览统计 */
export interface Overview {
  session_count: number
  message_count: number
  ticket_count: number
  avg_rating: number | null
}

export const analyticsService = {
  /** 获取总览 */
  overview(): Promise<Overview> {
    return api.get<any, Overview>('/analytics/overview')
  },

  /** 情感分布 */
  sentiment(): Promise<Record<string, number>> {
    return api.get<any, Record<string, number>>('/analytics/sentiment')
  },

  /** 意图分布 */
  intents(): Promise<Record<string, number>> {
    return api.get<any, Record<string, number>>('/analytics/intents')
  },

  /** 最近会话 */
  recentSessions(limit = 10): Promise<any[]> {
    return api.get<any, any[]>('/analytics/sessions/recent', { params: { limit } })
  },
}
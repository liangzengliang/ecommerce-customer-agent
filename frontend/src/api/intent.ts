/**
 * 意图相关接口
 */
import api from './index'
import type { Intent, IntentClassifyResponse } from '@/types/intent'

/** 意图识别调试 */
export function classifyIntent(text: string) {
  return api.post<any, IntentClassifyResponse>('/intent/classify', { text })
}

/** 获取所有意图 */
export function listIntents() {
  return api.get<any, Intent[]>('/intent/list')
}

/** 创建意图 */
export function createIntent(data: Partial<Intent>) {
  return api.post<any, Intent>('/intent/create', data)
}

/** 更新意图 */
export function updateIntent(id: number, data: Partial<Intent>) {
  return api.put<any, Intent>(`/intent/${id}`, data)
}

/** 删除意图 */
export function deleteIntent(id: number) {
  return api.delete(`/intent/${id}`)
}
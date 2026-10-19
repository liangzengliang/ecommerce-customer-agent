/**
 * 模型配置接口
 */
import api from './index'

export interface ModelConfig {
  id?: number
  name: string
  provider: string
  type: 'chat' | 'embedding'
  model: string
  base_url: string
  api_key: string
  temperature?: number
  max_tokens?: number
  is_default?: boolean
  is_active?: boolean
  status?: string
  description?: string
}

export interface TestResult {
  success: boolean
  message: string
  response?: string
  dimension?: number
  elapsed_ms?: number
}

export function listModels(type?: string) {
  return api.get<any, ModelConfig[]>('/models/list', { params: { type } })
}

export function createModel(data: ModelConfig) {
  return api.post<any, ModelConfig>('/models/create', data)
}

export function updateModel(id: number, data: Partial<ModelConfig>) {
  return api.put<any, ModelConfig>(`/models/${id}`, data)
}

export function deleteModel(id: number) {
  return api.delete(`/models/${id}`)
}

export function setDefaultModel(id: number) {
  return api.post<any, ModelConfig>(`/models/${id}/set-default`)
}

/** ★ 启用/停用 */
export function toggleModel(id: number, isActive: boolean) {
  return api.put<any, ModelConfig>(`/models/${id}/toggle`, { is_active: isActive })
}

/** 测试模型连通性 */
export function testModel(data: ModelConfig) {
  return api.post<any, TestResult>('/models/test', data)
}
/**
 * 记忆库接口
 */
import api from './index'

export function listMemory(params: {
  title?: string
  type?: string
  page?: number
  size?: number
}) {
  return api.get('/memory/list', { params })
}

export function deleteMemory(id: number) {
  return api.delete(`/memory/${id}`)
}

export function batchDeleteMemory(ids: number[]) {
  return api.post('/memory/batch-delete', ids)
}

export function clearAllMemory() {
  return api.delete('/memory/clear/all')
}

export function memoryStats() {
  return api.get('/memory/stats')
}

export function semanticSearch(keyword: string) {
  return api.post('/memory/semantic-search', null, { params: { keyword } })
}
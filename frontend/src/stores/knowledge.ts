/**
 * 知识库状态
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

/** 知识条目 */
export interface KnowledgeItem {
  id: number
  category: string
  question: string
  answer: string
  vector_id?: string
}

export const useKnowledgeStore = defineStore('knowledge', () => {
  const items = ref<KnowledgeItem[]>([])
  const loading = ref(false)

  /** 加载知识库列表 */
  async function fetchList(category?: string) {
    loading.value = true
    try {
      const res = await api.get<any, { items: KnowledgeItem[] }>('/knowledge/list', {
        params: { category },
      })
      items.value = res.items
    } finally {
      loading.value = false
    }
  }

  return { items, loading, fetchList }
})
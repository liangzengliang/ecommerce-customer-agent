/**
 * 历史提问本地存储
 * 保留最近 50 条，一个月内
 */

const STORAGE_KEY = 'user_question_history'
const MAX_ITEMS = 50
const MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000  // 30 天

export interface QuestionRecord {
  text: string
  timestamp: number
  count?: number  // 相同问题的出现次数
}

/** 读取历史（自动过滤超过 30 天的） */
export function getHistory(): QuestionRecord[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const list: QuestionRecord[] = JSON.parse(raw)
    const now = Date.now()
    const valid = list.filter((item) => now - item.timestamp < MAX_AGE_MS)
    // 清理过期数据
    if (valid.length !== list.length) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(valid))
    }
    return valid
  } catch (e) {
    return []
  }
}

/** 添加一条历史 */
export function addHistory(text: string): void {
  const value = text.trim()
  if (!value || value.length < 2) return

  let list = getHistory()
  const now = Date.now()

  // 如果已存在相同的，更新时间和次数，移到最前
  const existing = list.find((item) => item.text === value)
  if (existing) {
    existing.timestamp = now
    existing.count = (existing.count || 1) + 1
    list = [existing, ...list.filter((item) => item.text !== value)]
  } else {
    list.unshift({ text: value, timestamp: now, count: 1 })
  }

  // 限制条数
  list = list.slice(0, MAX_ITEMS)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
}

/** 清空历史 */
export function clearHistory(): void {
  localStorage.removeItem(STORAGE_KEY)
}

/** 获取排序后的历史（按次数+时间加权） */
export function getTopHistory(limit: number = 8): QuestionRecord[] {
  const list = getHistory()
  return list
    .sort((a, b) => {
      // 出现次数优先，其次时间
      const countDiff = (b.count || 1) - (a.count || 1)
      if (countDiff !== 0) return countDiff
      return b.timestamp - a.timestamp
    })
    .slice(0, limit)
}
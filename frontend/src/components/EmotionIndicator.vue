<template>
  <span class="emotion-indicator" :class="sentiment">
    <el-icon><component :is="icon" /></el-icon>
    <span class="text">{{ label }}</span>
  </span>
</template>

<script setup lang="ts">
/**
 * 情感指示器
 * 根据情感标签显示不同图标和颜色。
 */
import { computed } from 'vue'
import type { Sentiment } from '@/types/chat'

const props = defineProps<{ sentiment: Sentiment }>()

const icon = computed(() => {
  switch (props.sentiment) {
    case 'positive': return 'Sunny'
    case 'negative': return 'Cloudy'
    default: return 'MostlyCloudy'
  }
})

const label = computed(() => {
  switch (props.sentiment) {
    case 'positive': return '积极'
    case 'negative': return '消极'
    default: return '中性'
  }
})
</script>

<style scoped lang="scss">
.emotion-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  margin-top: 4px;

  &.positive { color: #67c23a; }
  &.neutral  { color: #909399; }
  &.negative { color: #f56c6c; }
}
</style>
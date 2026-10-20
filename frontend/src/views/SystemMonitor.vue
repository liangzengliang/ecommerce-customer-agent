<template>
  <div class="system-monitor">
    <h2>系统监控</h2>
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>情感分布</template>
          <div v-if="Object.keys(sentiment).length" class="bar-chart">
            <div v-for="(v, k) in sentiment" :key="k" class="bar-row">
              <span class="bar-label">{{ k }}</span>
              <el-progress :percentage="pct(v)" :stroke-width="18" />
            </div>
          </div>
          <el-empty v-else description="暂无情感数据" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>意图分布</template>
          <div v-if="Object.keys(intents).length" class="intent-list">
            <div v-for="(v, k) in intents" :key="k" class="intent-row">
              <span>{{ k }}</span>
              <el-tag size="small">{{ v }}</el-tag>
            </div>
          </div>
          <el-empty v-else description="暂无意图数据" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { analyticsService, type Overview } from '@/services/analyticsService'

const overview = ref<Overview | null>(null)
const sentiment = ref<Record<string, number>>({})
const intents = ref<Record<string, number>>({})
const loading = ref(false)

const cards = computed(() => [
  { label: '会话数', value: overview.value?.session_count ?? 0 },
  { label: '消息数', value: overview.value?.message_count ?? 0 },
  { label: '工单数', value: overview.value?.ticket_count ?? 0 },
  { label: '平均评分', value: overview.value?.avg_rating ?? '—' },
])

function pct(v: number): number {
  const total = Object.values(sentiment.value).reduce((a, b) => a + b, 0)
  return total ? Math.round((v / total) * 100) : 0
}

onMounted(async () => {
  loading.value = true
  try {
    overview.value = await analyticsService.overview()
    sentiment.value = await analyticsService.sentiment()
    intents.value = await analyticsService.intents()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.system-monitor {
  padding: 20px;

  .stat-card {
    text-align: center;
    padding: 12px 0;

    .stat-value {
      font-size: 32px;
      font-weight: 600;
      color: #409eff;
    }

    .stat-label {
      margin-top: 8px;
      color: #909399;
      font-size: 14px;
    }
  }

  .bar-chart {
    .bar-row {
      display: flex;
      align-items: center;
      margin-bottom: 12px;
      gap: 12px;

      .bar-label {
        width: 80px;
        color: #606266;
      }
    }
  }

  .intent-list {
    .intent-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;
      color: #606266;
    }
  }
}
</style>

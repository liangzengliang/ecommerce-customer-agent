<template>
  <div class="run-monitor">
    <h2>运行监控</h2>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>情感分布</template>
          <div v-if="Object.keys(sentiment).length" class="chart">
            <div v-for="(v, k) in sentiment" :key="k" class="row">
              <span class="label">{{ k }}</span>
              <el-progress :percentage="pct(v)" :stroke-width="20" />
              <span class="count">{{ v }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无情感数据" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>意图分布</template>
          <div v-if="Object.keys(intents).length" class="chart">
            <div v-for="(v, k) in intents" :key="k" class="row">
              <span class="label">{{ k }}</span>
              <el-progress :percentage="pct2(v)" :stroke-width="20" />
              <span class="count">{{ v }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无意图数据" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { analyticsService } from '@/services/analyticsService'

const sentiment = ref<Record<string, number>>({})
const intents = ref<Record<string, number>>({})

function pct(v: number): number {
  const total = Object.values(sentiment.value).reduce((a, b) => a + b, 0)
  return total ? Math.round((v / total) * 100) : 0
}
function pct2(v: number): number {
  const total = Object.values(intents.value).reduce((a, b) => a + b, 0)
  return total ? Math.round((v / total) * 100) : 0
}

onMounted(async () => {
  sentiment.value = await analyticsService.sentiment()
  intents.value = await analyticsService.intents()
})
</script>

<style scoped lang="scss">
.run-monitor {
  padding: 20px;

  .chart {
    .row {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 14px;

      .label {
        width: 100px;
        color: #606266;
        font-size: 14px;
      }

      .count {
        width: 40px;
        text-align: right;
        color: #909399;
      }
    }
  }
}
</style>

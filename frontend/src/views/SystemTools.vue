<template>
  <div class="system-tools">
    <h2>系统工具</h2>
    <el-row :gutter="16">
      <el-col :span="8" v-for="tool in tools" :key="tool.name">
        <el-card shadow="hover" class="tool-card">
          <template #header>
            <div class="tool-header">
              <el-icon :size="18"><component :is="tool.icon" /></el-icon>
              <span>{{ tool.name }}</span>
            </div>
          </template>
          <p class="tool-desc">{{ tool.description }}</p>
          <el-tag size="small" :type="tool.status === '可用' ? 'success' : 'info'">
            {{ tool.status }}
          </el-tag>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { Odometer, ChatDotRound, Document, Connection, DataAnalysis } from '@element-plus/icons-vue'

const tools = [
  { name: '订单查询', description: '根据订单号查询订单状态、物流信息、商品明细。', icon: Odometer, status: '可用' },
  { name: '商品咨询', description: '查询商品详情、价格、库存等。', icon: Connection, status: '可用' },
  { name: '申请退款', description: '提供订单号并说明原因，自动创建退款工单。', icon: Document, status: '可用' },
  { name: '转人工客服', description: '复杂问题转接人工客服处理。', icon: ChatDotRound, status: '可用' },
  { name: '智能对话', description: '基于 LLM 的智能问答，需要配置模型后使用。', icon: ChatDotRound, status: '可用' },
  { name: '数据分析', description: '查看会话统计、情感分布、意图分布。', icon: DataAnalysis, status: '可用' },
]
</script>

<style scoped lang="scss">
.system-tools {
  padding: 20px;

  .tool-card {
    margin-bottom: 16px;

    .tool-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
    }

    .tool-desc {
      color: #606266;
      min-height: 40px;
      line-height: 1.6;
    }
  }
}
</style>

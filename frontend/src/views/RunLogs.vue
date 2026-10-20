<template>
  <div class="run-logs">
    <div class="header">
      <h2>运行日志</h2>
      <el-button type="primary" :loading="loading" @click="load">刷新</el-button>
    </div>

    <el-table :data="sessions" v-loading="loading" stripe>
      <el-table-column prop="session_id" label="会话ID" width="260" />
      <el-table-column prop="user_id" label="用户ID" width="100" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="message_count" label="消息数" width="100" />
      <el-table-column prop="created_at" label="创建时间" />
    </el-table>
    <el-empty v-if="!loading && !sessions.length" description="暂无运行日志" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { analyticsService } from '@/services/analyticsService'

const sessions = ref<any[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    sessions.value = await analyticsService.recentSessions(50)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.run-logs {
  padding: 20px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
}
</style>

<template>
  <div class="history-page">
    <div class="header">
      <h2>历史会话</h2>
      <el-button @click="router.push('/chat')">返回对话</el-button>
    </div>

    <el-table :data="sessions" v-loading="loading" stripe>
      <el-table-column prop="session_id" label="会话ID" width="240" />
      <el-table-column prop="user_id" label="用户ID" width="100" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="message_count" label="消息数" width="100" />
      <el-table-column prop="created_at" label="创建时间" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * 历史会话页
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { analyticsService } from '@/services/analyticsService'

const router = useRouter()
const sessions = ref<any[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    sessions.value = await analyticsService.recentSessions(50)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.history-page {
  padding: 20px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
}
</style>
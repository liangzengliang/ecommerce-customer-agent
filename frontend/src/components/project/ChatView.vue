<template>
  <div class="chat-view">
    <div class="chat-header">
      <el-icon :size="16"><ChatDotRound /></el-icon>
      <span>项目讨论</span>
    </div>

    <div class="chat-body" v-loading="loading">
      <div class="chat-list">
        <div v-for="c in comments" :key="c.id" class="chat-item">
          <div class="chat-avatar">{{ (c.username || 'U').charAt(0).toUpperCase() }}</div>
          <div class="chat-main">
            <div class="chat-meta">
              <span class="chat-author">{{ c.username || `用户${c.user_id}` }}</span>
              <span class="chat-time">{{ c.created_at || '' }}</span>
            </div>
            <div class="chat-content">{{ c.content }}</div>
          </div>
        </div>
        <el-empty v-if="!loading && comments.length === 0" description="暂无讨论，发送第一条消息" :image-size="50" />
      </div>
    </div>

    <div class="chat-input">
      <el-input
        v-model="draft"
        type="textarea"
        :rows="2"
        placeholder="输入消息，Enter 发送（Shift+Enter 换行）"
        resize="none"
        @keydown.enter.exact.prevent="send"
      />
      <el-button type="primary" :loading="sending" :icon="Promotion" @click="send">发送</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Promotion } from '@element-plus/icons-vue'
import { listComments, createComment } from '@/api/project'
import type { ProjectComment } from '@/types/project'

const props = defineProps<{ projectId: number }>()
const emit = defineEmits<{ (e: 'changed'): void }>()

const loading = ref(false)
const sending = ref(false)
const comments = ref<ProjectComment[]>([])
const draft = ref('')

async function load() {
  loading.value = true
  try {
    comments.value = await listComments(props.projectId)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载讨论失败')
  } finally {
    loading.value = false
  }
}

async function send() {
  const content = draft.value.trim()
  if (!content) return
  sending.value = true
  try {
    await createComment(props.projectId, content)
    draft.value = ''
    await load()
    emit('changed')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '发送失败')
  } finally {
    sending.value = false
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.chat-view {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  overflow: hidden;

  .chat-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    border-bottom: 1px solid #f1f5f9;
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
  }

  .chat-body {
    max-height: 360px;
    overflow-y: auto;
    padding: 12px 16px;

    .chat-list {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .chat-item {
        display: flex;
        gap: 10px;

        .chat-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 13px;
          font-weight: 600;
          flex-shrink: 0;
        }

        .chat-main {
          flex: 1;
          min-width: 0;

          .chat-meta {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 2px;

            .chat-author {
              font-size: 13px;
              font-weight: 600;
              color: #1e293b;
            }

            .chat-time {
              font-size: 12px;
              color: #94a3b8;
            }
          }

          .chat-content {
            font-size: 14px;
            color: #334155;
            line-height: 1.6;
            word-break: break-word;
          }
        }
      }
    }
  }

  .chat-input {
    display: flex;
    gap: 8px;
    padding: 12px 16px;
    border-top: 1px solid #f1f5f9;
    align-items: flex-end;
  }
}
</style>
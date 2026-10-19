<template>
  <div class="message-bubble" :class="[`role-${message.role}`]">
    <!-- 头像 -->
    <div class="avatar">
      <el-icon v-if="message.role === 'user'" :size="24"><User /></el-icon>
      <el-icon v-else :size="24"><Service /></el-icon>
    </div>

    <!-- 消息内容 -->
    <div class="content-wrapper">
      <div class="bubble">
        <span v-if="message.loading && !message.content" class="typing">
          <span></span><span></span><span></span>
        </span>
        <span v-else v-html="renderedContent"></span>
        <span v-if="message.loading && message.content" class="cursor">▍</span>
      </div>

      <!-- 情感标识 -->
      <EmotionIndicator v-if="message.sentiment" :sentiment="message.sentiment" />

      <!-- 时间 -->
      <div class="time">{{ time }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 消息气泡组件
 * 展示单条消息，区分用户和机器人样式，支持 Markdown 渲染。
 */
import { computed } from 'vue'
import { marked } from 'marked'
import type { Message } from '@/types/chat'
import { formatTime } from '@/utils/formatTime'
import EmotionIndicator from './EmotionIndicator.vue'

const props = defineProps<{ message: Message }>()

/** 渲染 Markdown（bot 消息） */
const renderedContent = computed(() => {
  if (props.message.role === 'bot') {
    return marked.parse(props.message.content || '')
  }
  // 用户消息直接显示，避免 XSS
  return props.message.content.replace(/</g, '&lt;').replace(/>/g, '&gt;')
})

/** 格式化时间 */
const time = computed(() =>
  props.message.createdAt ? formatTime(props.message.createdAt) : '',
)
</script>

<style scoped lang="scss">
.message-bubble {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;

  &.role-user {
    flex-direction: row-reverse;

    .bubble {
      background: #409eff;
      color: #fff;
    }

    .time {
      text-align: right;
    }
  }

  &.role-bot {
    .bubble {
      background: #fff;
      color: #303133;
    }
  }

  .avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #e4e7ed;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .content-wrapper {
    max-width: 70%;
    display: flex;
    flex-direction: column;
  }

  .bubble {
    padding: 10px 14px;
    border-radius: 8px;
    line-height: 1.6;
    word-break: break-word;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);

    :deep(p) {
      margin: 0 0 6px;
      &:last-child { margin-bottom: 0; }
    }

    .cursor {
      animation: blink 1s infinite;
    }

    .typing {
      display: inline-flex;
      gap: 4px;

      span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #c0c4cc;
        animation: bounce 1.4s infinite ease-in-out;

        &:nth-child(2) { animation-delay: 0.2s; }
        &:nth-child(3) { animation-delay: 0.4s; }
      }
    }
  }

  .time {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
}

@keyframes blink {
  50% { opacity: 0; }
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
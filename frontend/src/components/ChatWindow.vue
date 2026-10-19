<template>
  <div class="chat-window" ref="listRef">
    <!-- 空状态提示 -->
    <div v-if="messages.length === 0" class="empty">
      <el-icon :size="60" color="#c0c4cc"><ChatDotRound /></el-icon>
      <p>您好，我是智能客服，有什么可以帮您？</p>
    </div>

    <!-- 消息列表 -->
    <MessageBubble
      v-for="msg in messages"
      :key="msg.id"
      :message="msg"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 聊天窗口组件
 * 展示消息列表，自动滚动到底部。
 */
import { ref, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import MessageBubble from './MessageBubble.vue'

const chatStore = useChatStore()
const { messages } = storeToRefs(chatStore)

const listRef = ref<HTMLElement>()

/** 滚动到底部 */
async function scrollToBottom() {
  await nextTick()
  if (listRef.value) {
    listRef.value.scrollTop = listRef.value.scrollHeight
  }
}

// 监听消息变化，自动滚动
watch(() => messages.value.length, scrollToBottom)
watch(
  () => messages.value[messages.value.length - 1]?.content,
  scrollToBottom,
)
</script>

<style scoped lang="scss">
.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f7f8fa;

  .empty {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #909399;
    gap: 12px;
  }
}
</style>
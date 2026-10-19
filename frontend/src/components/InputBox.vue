<template>
  <div class="input-box">
    <el-input
      v-model="text"
      type="textarea"
      :rows="2"
      resize="none"
      placeholder="请输入您的问题，Enter 发送，Shift+Enter 换行"
      @keydown.enter="handleEnter"
    />
    <div class="actions">
      <el-button
        type="primary"
        :loading="loading"
        :disabled="!text.trim()"
        @click="handleSend"
      >
        发送
      </el-button>
      <el-button @click="handleClear">清空</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 输入框组件
 * 支持 Enter 发送、Shift+Enter 换行、清空对话。
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

defineProps<{ loading?: boolean }>()
const emit = defineEmits<{
  (e: 'send', text: string): void
  (e: 'clear'): void
}>()

const text = ref('')

/** 处理 Enter 键 */
function handleEnter(e: KeyboardEvent) {
  if (e.shiftKey) return  // Shift+Enter 换行
  e.preventDefault()
  handleSend()
}

/** 发送消息 */
function handleSend() {
  const value = text.value.trim()
  if (!value) {
    ElMessage.warning('请输入内容')
    return
  }
  emit('send', value)
  text.value = ''
}

/** 清空对话 */
function handleClear() {
  emit('clear')
}
</script>

<style scoped lang="scss">
.input-box {
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #ebeef5;

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 8px;
  }
}
</style>
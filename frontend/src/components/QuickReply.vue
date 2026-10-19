<template>
  <div class="quick-reply">
    <el-tag
      v-for="item in replies"
      :key="item"
      class="tag"
      @click="emit('select', item)"
    >
      {{ item }}
    </el-tag>
  </div>
</template>

<script setup lang="ts">
/**
 * 快捷回复组件
 * 展示常见问题快捷入口，点击后直接发送。
 */
const emit = defineEmits<{ (e: 'select', text: string): void }>()

const replies = [
  '查订单',
  '物流到哪了',
  '怎么退款',
  '商品推荐',
  '人工客服',
]
</script>

<style scoped lang="scss">
.quick-reply {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 16px;
  background: #fff;
  border-top: 1px solid #ebeef5;

  .tag {
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
    }
  }
}
</style>
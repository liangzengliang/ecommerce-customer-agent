<template>
  <div class="kanban-board">
    <div class="kanban-toolbar">
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>
    <div class="kanban-columns" v-loading="loading">
      <div v-for="col in columns" :key="col.status" class="kanban-column">
        <div class="column-header">
          <span class="column-dot" :style="{ background: col.color }"></span>
          <span class="column-title">{{ col.label }}</span>
          <span class="column-count">{{ tasksByStatus(col.status).length }}</span>
        </div>
        <div class="column-body">
          <div
            v-for="task in tasksByStatus(col.status)"
            :key="task.id"
            class="kanban-card"
            :class="{ done: task.status === 'done' }"
          >
            <div class="card-title">{{ task.title }}</div>
            <div class="card-meta">
              <el-tag :type="priorityTagType(task.priority)" size="small" effect="plain">
                {{ priorityLabel(task.priority) }}
              </el-tag>
              <span class="card-assignee" v-if="task.assignee_id">#{{ task.assignee_id }}</span>
            </div>
            <div class="card-actions">
              <el-button
                v-if="col.status !== 'todo'"
                link
                size="small"
                @click="moveTask(task, prevStatus(col.status))"
              >
                左移
              </el-button>
              <el-button
                v-if="col.status !== 'done'"
                link
                size="small"
                type="primary"
                @click="moveTask(task, nextStatus(col.status))"
              >
                右移
              </el-button>
            </div>
          </div>
          <el-empty v-if="tasksByStatus(col.status).length === 0" description="无任务" :image-size="40" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { listTasks, updateTask } from '@/api/project'
import type { ProjectTask, TaskStatus, ProjectPriority } from '@/types/project'

const props = defineProps<{ projectId: number }>()
const emit = defineEmits<{ (e: 'changed'): void }>()

const loading = ref(false)
const list = ref<ProjectTask[]>([])

interface KanbanColumn {
  status: TaskStatus
  label: string
  color: string
}

const columns: KanbanColumn[] = [
  { status: 'todo', label: '待办', color: '#94a3b8' },
  { status: 'in_progress', label: '进行中', color: '#3b82f6' },
  { status: 'review', label: '评审', color: '#eab308' },
  { status: 'done', label: '完成', color: '#10b981' },
]

async function load() {
  loading.value = true
  try {
    list.value = await listTasks(props.projectId)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载看板失败')
  } finally {
    loading.value = false
  }
}

function tasksByStatus(status: TaskStatus): ProjectTask[] {
  return list.value.filter((t) => t.status === status)
}

function prevStatus(s: TaskStatus): TaskStatus {
  const order: TaskStatus[] = ['todo', 'in_progress', 'review', 'done']
  const i = order.indexOf(s)
  return order[Math.max(0, i - 1)]
}

function nextStatus(s: TaskStatus): TaskStatus {
  const order: TaskStatus[] = ['todo', 'in_progress', 'review', 'done']
  const i = order.indexOf(s)
  return order[Math.min(order.length - 1, i + 1)]
}

async function moveTask(task: ProjectTask, target: TaskStatus) {
  if (task.status === target) return
  try {
    await updateTask(props.projectId, task.id, { status: target })
    task.status = target
    ElMessage.success('任务状态已更新')
    emit('changed')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '更新失败')
  }
}

// ============ 类型化辅助函数 ============
function priorityLabel(p: ProjectPriority): string {
  return { low: '低', medium: '中', high: '高', urgent: '紧急' }[p] || p
}

function priorityTagType(p: ProjectPriority): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<ProjectPriority, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    low: 'info',
    medium: 'primary',
    high: 'warning',
    urgent: 'danger',
  }
  return map[p]
}

onMounted(load)
</script>

<style scoped lang="scss">
.kanban-board {
  .kanban-toolbar {
    margin-bottom: 12px;
  }

  .kanban-columns {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    min-height: 200px;

    @media (max-width: 1200px) {
      grid-template-columns: repeat(2, 1fr);
    }

    .kanban-column {
      background: #f8fafc;
      border-radius: 10px;
      padding: 10px;
      border: 1px solid #f1f5f9;

      .column-header {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 10px;

        .column-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        .column-title {
          font-size: 14px;
          font-weight: 600;
          color: #1e293b;
        }

        .column-count {
          margin-left: auto;
          font-size: 12px;
          color: #94a3b8;
          background: #f1f5f9;
          border-radius: 10px;
          padding: 1px 8px;
        }
      }

      .column-body {
        display: flex;
        flex-direction: column;
        gap: 8px;
        min-height: 80px;
      }

      .kanban-card {
        background: #fff;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;

        &.done {
          opacity: 0.7;
        }

        .card-title {
          font-size: 14px;
          font-weight: 500;
          color: #1e293b;
          margin-bottom: 8px;
          line-height: 1.4;
        }

        .card-meta {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 6px;
          margin-bottom: 6px;

          .card-assignee {
            font-size: 12px;
            color: #94a3b8;
          }
        }

        .card-actions {
          display: flex;
          gap: 4px;
        }
      }
    }
  }
}
</style>
<template>
  <!-- 根容器：无 task 时渲染 WBS 树容器 -->
  <div v-if="!task" class="wbs-tree">
    <div class="wbs-toolbar">
      <el-button type="primary" :icon="Plus" :loading="saving" @click="handleAddRoot">添加根节点</el-button>
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>

    <el-empty v-if="!loading && roots.length === 0" description="暂无 WBS 节点，点击上方添加" />

    <div v-loading="loading" class="wbs-node-list">
      <WbsTreeNode
        v-for="node in roots"
        :key="node.id"
        :task="node"
        :project-id="projectId"
        :depth="0"
        @changed="load"
      />
    </div>
  </div>

  <!-- 递归节点 -->
  <div v-else class="wbs-node" :style="{ paddingLeft: `${depth * 20}px` }">
    <div class="wbs-node-row" :class="{ selected: selectedId === task.id }">
      <span class="wbs-node-code">{{ task.wbs_code || '-' }}</span>
      <span class="wbs-node-title">{{ task.title }}</span>
      <el-tag :type="taskStatusTagType(task.status)" size="small">{{ taskStatusLabel(task.status) }}</el-tag>
      <el-tag :type="priorityTagType(task.priority)" size="small" effect="plain">{{ priorityLabel(task.priority) }}</el-tag>
      <span class="wbs-node-progress">{{ task.progress || 0 }}%</span>
      <div class="wbs-node-actions">
        <el-button link type="primary" size="small" :icon="Plus" @click="handleAddChild(task)">子节点</el-button>
        <el-button link type="primary" size="small" :icon="Edit" @click="openEdit(task)">编辑</el-button>
        <el-button link type="danger" size="small" :icon="Delete" @click="handleDelete(task)">删除</el-button>
      </div>
    </div>

    <!-- 子节点 -->
    <div v-if="childrenOf(task.id).length" class="wbs-node-children">
      <WbsTreeNode
        v-for="child in childrenOf(task.id)"
        :key="child.id"
        :task="child"
        :project-id="projectId"
        :depth="depth + 1"
        @changed="load"
      />
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" :title="'编辑节点：' + task.title" width="520px" append-to-body>
      <el-form :model="editForm" label-width="90px">
        <el-form-item label="WBS编码">
          <el-input v-model="editForm.wbs_code" placeholder="如 1.2.3" maxlength="50" />
        </el-form-item>
        <el-form-item label="节点名称" required>
          <el-input v-model="editForm.title" maxlength="200" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="待办" value="todo" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="评审" value="review" />
            <el-option label="完成" value="done" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="editForm.priority" style="width: 100%">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="进度(%)">
          <el-slider v-model="editForm.progress" :max="100" show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { listTasks, createTask, updateTask, deleteTask } from '@/api/project'
import type { ProjectTask, TaskStatus, ProjectPriority } from '@/types/project'

const props = withDefaults(defineProps<{
  projectId: number
  task?: ProjectTask
  depth?: number
}>(), {
  depth: 0,
})

const emit = defineEmits<{ (e: 'changed'): void }>()

const loading = ref(false)
const saving = ref(false)
const list = ref<ProjectTask[]>([])
const selectedId = ref<number | null>(null)
const editVisible = ref(false)
const editingId = ref<number | null>(null)

const roots = computed(() => list.value.filter((t) => !t.parent_id))

const editForm = reactive({
  wbs_code: '',
  title: '',
  description: '',
  status: 'todo' as TaskStatus,
  priority: 'medium' as ProjectPriority,
  progress: 0,
})

async function load() {
  loading.value = true
  try {
    list.value = await listTasks(props.projectId)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载 WBS 失败')
  } finally {
    loading.value = false
  }
}

function childrenOf(parentId: number): ProjectTask[] {
  return list.value.filter((t) => t.parent_id === parentId)
}

async function handleAddRoot() {
  saving.value = true
  try {
    await createTask(props.projectId, {
      title: '新 WBS 节点',
      wbs_code: '',
      description: '',
      status: 'todo',
      priority: 'medium',
      progress: 0,
      parent_id: undefined,
    })
    ElMessage.success('节点已创建')
    await load()
    emit('changed')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '创建节点失败')
  } finally {
    saving.value = false
  }
}

async function handleAddChild(parent: ProjectTask) {
  saving.value = true
  try {
    await createTask(props.projectId, {
      title: '新子节点',
      wbs_code: parent.wbs_code ? `${parent.wbs_code}.1` : '',
      description: '',
      status: 'todo',
      priority: 'medium',
      progress: 0,
      parent_id: parent.id,
    })
    ElMessage.success('子节点已创建')
    await load()
    emit('changed')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '创建子节点失败')
  } finally {
    saving.value = false
  }
}

function openEdit(task: ProjectTask) {
  editingId.value = task.id
  selectedId.value = task.id
  Object.assign(editForm, {
    wbs_code: task.wbs_code || '',
    title: task.title,
    description: task.description || '',
    status: task.status,
    priority: task.priority,
    progress: task.progress || 0,
  })
  editVisible.value = true
}

async function handleSaveEdit() {
  if (!editForm.title.trim()) {
    ElMessage.warning('请输入节点名称')
    return
  }
  if (!editingId.value) return
  saving.value = true
  try {
    await updateTask(props.projectId, editingId.value, {
      wbs_code: editForm.wbs_code.trim() || undefined,
      title: editForm.title.trim(),
      description: editForm.description || undefined,
      status: editForm.status,
      priority: editForm.priority,
      progress: editForm.progress,
    })
    ElMessage.success('节点已更新')
    editVisible.value = false
    await load()
    emit('changed')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '更新节点失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(task: ProjectTask) {
  try {
    await ElMessageBox.confirm(`确定删除节点「${task.title}」及其子节点？`, '提示', { type: 'warning' })
    await deleteTask(props.projectId, task.id)
    ElMessage.success('节点已删除')
    await load()
    emit('changed')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || '删除节点失败')
  }
}

// ============ 类型化辅助函数 ============
function taskStatusLabel(status: TaskStatus): string {
  return { todo: '待办', in_progress: '进行中', review: '评审', done: '完成' }[status] || status
}

function taskStatusTagType(status: TaskStatus): 'primary' | 'success' | 'warning' | 'info' | 'danger' {
  const map: Record<TaskStatus, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    todo: 'info',
    in_progress: 'primary',
    review: 'warning',
    done: 'success',
  }
  return map[status]
}

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

onMounted(() => {
  if (!props.task) load()
})
</script>

<style scoped lang="scss">
.wbs-tree {
  .wbs-toolbar {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  .wbs-node-list {
    min-height: 60px;
  }
}

.wbs-node {
  .wbs-node-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 8px;
    border: 1px solid #f1f5f9;
    background: #fff;
    margin-bottom: 6px;
    transition: all 0.2s;

    &:hover {
      border-color: #bfdbfe;
      background: #f8fafc;
    }

    &.selected {
      border-color: #3b82f6;
      background: #eff6ff;
    }

    .wbs-node-code {
      font-family: monospace;
      font-size: 13px;
      color: #3b82f6;
      min-width: 60px;
    }

    .wbs-node-title {
      font-size: 14px;
      font-weight: 500;
      color: #1e293b;
      flex: 1;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .wbs-node-progress {
      font-size: 12px;
      color: #64748b;
      min-width: 40px;
      text-align: right;
    }

    .wbs-node-actions {
      display: flex;
      align-items: center;
      gap: 2px;
    }
  }

  .wbs-node-children {
    margin-top: 2px;
  }
}
</style>
<template>
  <div class="tasks-tab">
    <div class="tab-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="openCreate">新建任务</el-button>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
      </div>
      <div class="toolbar-right">
        <el-select v-model="filterStatus" placeholder="全部状态" clearable style="width: 130px" @change="load">
          <el-option label="待办" value="todo" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="评审" value="review" />
          <el-option label="完成" value="done" />
        </el-select>
      </div>
    </div>

    <el-table :data="filteredList" v-loading="loading" stripe>
      <el-table-column prop="wbs_code" label="WBS" width="110">
        <template #default="{ row }">
          <span class="wbs-code">{{ row.wbs_code || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="任务名称" min-width="220" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="taskStatusTagType(row.status)" size="small">{{ taskStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="优先级" width="90">
        <template #default="{ row }">
          <el-tag :type="priorityTagType(row.priority)" size="small" effect="plain">{{ priorityLabel(row.priority) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="负责人" width="100">
        <template #default="{ row }">
          <span>{{ row.assignee_id ? `#${row.assignee_id}` : '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="截止日期" width="110">
        <template #default="{ row }">
          <span>{{ row.due_date || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="进度" width="140">
        <template #default="{ row }">
          <el-progress :percentage="Number(row.progress) || 0" :stroke-width="6" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" :icon="Edit" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" :icon="Delete" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新建/编辑 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑任务' : '新建任务'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="WBS编号">
          <el-input v-model="form.wbs_code" placeholder="如 1.2.3" maxlength="50" />
        </el-form-item>
        <el-form-item label="任务名称" required>
          <el-input v-model="form.title" maxlength="200" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="待办" value="todo" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="评审" value="review" />
            <el-option label="完成" value="done" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority" style="width: 100%">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人ID">
          <el-input-number v-model="form.assignee_id" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="进度(%)">
          <el-slider v-model="form.progress" :max="100" show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
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

const props = defineProps<{ projectId: number }>()
const emit = defineEmits<{ (e: 'changed'): void }>()

const loading = ref(false)
const saving = ref(false)
const list = ref<ProjectTask[]>([])
const filterStatus = ref('')
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({
  wbs_code: '',
  title: '',
  description: '',
  status: 'todo' as TaskStatus,
  priority: 'medium' as ProjectPriority,
  assignee_id: undefined as number | undefined,
  start_date: '',
  due_date: '',
  progress: 0,
})

const filteredList = computed(() => {
  if (!filterStatus.value) return list.value
  return list.value.filter((t) => t.status === filterStatus.value)
})

async function load() {
  loading.value = true
  try {
    list.value = await listTasks(props.projectId)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载任务失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    wbs_code: '', title: '', description: '',
    status: 'todo', priority: 'medium',
    assignee_id: undefined, start_date: '', due_date: '', progress: 0,
  })
  dialogVisible.value = true
}

function openEdit(row: ProjectTask) {
  editingId.value = row.id
  Object.assign(form, {
    wbs_code: row.wbs_code || '',
    title: row.title,
    description: row.description || '',
    status: row.status,
    priority: row.priority,
    assignee_id: row.assignee_id || undefined,
    start_date: row.start_date || '',
    due_date: row.due_date || '',
    progress: row.progress || 0,
  })
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.title.trim()) {
    ElMessage.warning('请输入任务名称')
    return
  }
  saving.value = true
  try {
    const payload = {
      wbs_code: form.wbs_code.trim() || undefined,
      title: form.title.trim(),
      description: form.description || undefined,
      status: form.status,
      priority: form.priority,
      assignee_id: form.assignee_id || undefined,
      start_date: form.start_date || undefined,
      due_date: form.due_date || undefined,
      progress: form.progress,
    }
    if (editingId.value) {
      await updateTask(props.projectId, editingId.value, payload)
      ElMessage.success('任务已更新')
    } else {
      await createTask(props.projectId, payload)
      ElMessage.success('任务已创建')
    }
    dialogVisible.value = false
    await load()
    emit('changed')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: ProjectTask) {
  try {
    await ElMessageBox.confirm(`确定删除任务「${row.title}」？`, '提示', { type: 'warning' })
    await deleteTask(props.projectId, row.id)
    ElMessage.success('任务已删除')
    await load()
    emit('changed')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || '删除失败')
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

onMounted(load)
</script>

<style scoped lang="scss">
.tasks-tab {
  .tab-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;

    .toolbar-left,
    .toolbar-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .wbs-code {
    font-family: monospace;
    font-size: 13px;
    color: #3b82f6;
  }
}
</style>
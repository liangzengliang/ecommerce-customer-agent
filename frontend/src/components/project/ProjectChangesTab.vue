<template>
  <div class="changes-tab">
    <div class="tab-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="openCreate">新建变更</el-button>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
      </div>
      <div class="toolbar-right">
        <el-select v-model="filterStatus" placeholder="全部状态" clearable style="width: 130px" @change="load">
          <el-option label="建议中" value="proposed" />
          <el-option label="已批准" value="approved" />
          <el-option label="已拒绝" value="rejected" />
          <el-option label="已实施" value="implemented" />
        </el-select>
      </div>
    </div>

    <el-table :data="filteredList" v-loading="loading" stripe>
      <el-table-column prop="title" label="变更标题" min-width="200" show-overflow-tooltip />
      <el-table-column label="类型" width="110">
        <template #default="{ row }">
          <el-tag size="small" effect="plain">{{ changeTypeLabel(row.change_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="changeStatusTagType(row.status)" size="small">{{ changeStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="影响分析" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.impact || '-' }}</span>
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
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑变更' : '新建变更'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="变更标题" required>
          <el-input v-model="form.title" maxlength="200" />
        </el-form-item>
        <el-form-item label="变更类型">
          <el-select v-model="form.change_type" style="width: 100%">
            <el-option label="范围" value="scope" />
            <el-option label="进度" value="schedule" />
            <el-option label="成本" value="cost" />
            <el-option label="质量" value="quality" />
            <el-option label="资源" value="resource" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="建议中" value="proposed" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已实施" value="implemented" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="影响分析">
          <el-input v-model="form.impact" type="textarea" :rows="3" />
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
import { listChanges, createChange, updateChange, deleteChange } from '@/api/project'
import type { ProjectChange, ChangeType, ChangeStatus } from '@/types/project'

const props = defineProps<{ projectId: number }>()
const emit = defineEmits<{ (e: 'changed'): void }>()

const loading = ref(false)
const saving = ref(false)
const list = ref<ProjectChange[]>([])
const filterStatus = ref('')
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({
  title: '',
  description: '',
  change_type: 'scope' as ChangeType,
  status: 'proposed' as ChangeStatus,
  impact: '',
})

const filteredList = computed(() => {
  if (!filterStatus.value) return list.value
  return list.value.filter((c) => c.status === filterStatus.value)
})

async function load() {
  loading.value = true
  try {
    list.value = await listChanges(props.projectId)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载变更失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    title: '', description: '',
    change_type: 'scope', status: 'proposed', impact: '',
  })
  dialogVisible.value = true
}

function openEdit(row: ProjectChange) {
  editingId.value = row.id
  Object.assign(form, {
    title: row.title,
    description: row.description || '',
    change_type: row.change_type,
    status: row.status,
    impact: row.impact || '',
  })
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.title.trim()) {
    ElMessage.warning('请输入变更标题')
    return
  }
  saving.value = true
  try {
    const payload = {
      title: form.title.trim(),
      description: form.description || undefined,
      change_type: form.change_type,
      status: form.status,
      impact: form.impact || undefined,
    }
    if (editingId.value) {
      await updateChange(props.projectId, editingId.value, payload)
      ElMessage.success('变更已更新')
    } else {
      await createChange(props.projectId, payload)
      ElMessage.success('变更已创建')
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

async function handleDelete(row: ProjectChange) {
  try {
    await ElMessageBox.confirm(`确定删除变更「${row.title}」？`, '提示', { type: 'warning' })
    await deleteChange(props.projectId, row.id)
    ElMessage.success('变更已删除')
    await load()
    emit('changed')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

// ============ 类型化辅助函数 ============
function changeTypeLabel(t: ChangeType): string {
  return { scope: '范围', schedule: '进度', cost: '成本', quality: '质量', resource: '资源', other: '其他' }[t] || t
}

function changeStatusLabel(s: ChangeStatus): string {
  return { proposed: '建议中', approved: '已批准', rejected: '已拒绝', implemented: '已实施' }[s] || s
}

function changeStatusTagType(s: ChangeStatus): 'primary' | 'success' | 'warning' | 'info' | 'danger' {
  const map: Record<ChangeStatus, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    proposed: 'warning',
    approved: 'success',
    rejected: 'danger',
    implemented: 'primary',
  }
  return map[s]
}

onMounted(load)
</script>

<style scoped lang="scss">
.changes-tab {
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
}
</style>
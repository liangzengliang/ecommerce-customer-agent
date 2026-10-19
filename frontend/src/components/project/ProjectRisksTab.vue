<template>
  <div class="risks-tab">
    <div class="tab-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="openCreate">新建风险</el-button>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
      </div>
      <div class="toolbar-right">
        <el-select v-model="filterLevel" placeholder="全部等级" clearable style="width: 130px" @change="load">
          <el-option label="低" value="low" />
          <el-option label="中" value="medium" />
          <el-option label="高" value="high" />
          <el-option label="严重" value="critical" />
        </el-select>
      </div>
    </div>

    <el-table :data="filteredList" v-loading="loading" stripe>
      <el-table-column prop="title" label="风险名称" min-width="200" show-overflow-tooltip />
      <el-table-column label="等级" width="100">
        <template #default="{ row }">
          <el-tag :type="riskLevelTagType(row.level)" size="small">{{ riskLevelLabel(row.level) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="riskStatusTagType(row.status)" size="small" effect="plain">{{ riskStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="负责人" width="100">
        <template #default="{ row }">
          <span>{{ row.owner_id ? `#${row.owner_id}` : '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="截止日期" width="110">
        <template #default="{ row }">
          <span>{{ row.due_date || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="应对措施" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.mitigation || '-' }}</span>
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
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑风险' : '新建风险'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="风险名称" required>
          <el-input v-model="form.title" maxlength="200" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="form.level" style="width: 100%">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="严重" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="未关闭" value="open" />
            <el-option label="缓解中" value="mitigating" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人ID">
          <el-input-number v-model="form.owner_id" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="应对措施">
          <el-input v-model="form.mitigation" type="textarea" :rows="3" />
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
import { listRisks, createRisk, updateRisk, deleteRisk } from '@/api/project'
import type { ProjectRisk, RiskLevel, RiskStatus } from '@/types/project'

const props = defineProps<{ projectId: number }>()
const emit = defineEmits<{ (e: 'changed'): void }>()

const loading = ref(false)
const saving = ref(false)
const list = ref<ProjectRisk[]>([])
const filterLevel = ref('')
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({
  title: '',
  description: '',
  level: 'medium' as RiskLevel,
  status: 'open' as RiskStatus,
  owner_id: undefined as number | undefined,
  due_date: '',
  mitigation: '',
})

const filteredList = computed(() => {
  if (!filterLevel.value) return list.value
  return list.value.filter((r) => r.level === filterLevel.value)
})

async function load() {
  loading.value = true
  try {
    list.value = await listRisks(props.projectId)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载风险失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    title: '', description: '',
    level: 'medium', status: 'open',
    owner_id: undefined, due_date: '', mitigation: '',
  })
  dialogVisible.value = true
}

function openEdit(row: ProjectRisk) {
  editingId.value = row.id
  Object.assign(form, {
    title: row.title,
    description: row.description || '',
    level: row.level,
    status: row.status,
    owner_id: row.owner_id || undefined,
    due_date: row.due_date || '',
    mitigation: row.mitigation || '',
  })
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.title.trim()) {
    ElMessage.warning('请输入风险名称')
    return
  }
  saving.value = true
  try {
    const payload = {
      title: form.title.trim(),
      description: form.description || undefined,
      level: form.level,
      status: form.status,
      owner_id: form.owner_id || undefined,
      due_date: form.due_date || undefined,
      mitigation: form.mitigation || undefined,
    }
    if (editingId.value) {
      await updateRisk(props.projectId, editingId.value, payload)
      ElMessage.success('风险已更新')
    } else {
      await createRisk(props.projectId, payload)
      ElMessage.success('风险已创建')
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

async function handleDelete(row: ProjectRisk) {
  try {
    await ElMessageBox.confirm(`确定删除风险「${row.title}」？`, '提示', { type: 'warning' })
    await deleteRisk(props.projectId, row.id)
    ElMessage.success('风险已删除')
    await load()
    emit('changed')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

// ============ 类型化辅助函数 ============
function riskLevelLabel(level: RiskLevel): string {
  return { low: '低', medium: '中', high: '高', critical: '严重' }[level] || level
}

function riskLevelTagType(level: RiskLevel): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<RiskLevel, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    low: 'info',
    medium: 'primary',
    high: 'warning',
    critical: 'danger',
  }
  return map[level]
}

function riskStatusLabel(status: RiskStatus): string {
  return { open: '未关闭', mitigating: '缓解中', closed: '已关闭' }[status] || status
}

function riskStatusTagType(status: RiskStatus): 'primary' | 'success' | 'warning' | 'info' | 'danger' {
  const map: Record<RiskStatus, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    open: 'danger',
    mitigating: 'warning',
    closed: 'success',
  }
  return map[status]
}

onMounted(load)
</script>

<style scoped lang="scss">
.risks-tab {
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
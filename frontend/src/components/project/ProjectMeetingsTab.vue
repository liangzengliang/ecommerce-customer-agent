<template>
  <div class="meetings-tab">
    <div class="tab-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="openCreate">新建会议</el-button>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
      </div>
    </div>

    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="title" label="会议主题" min-width="200" show-overflow-tooltip />
      <el-table-column label="会议日期" width="120">
        <template #default="{ row }">
          <span>{{ row.meeting_date || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="地点" width="140">
        <template #default="{ row }">
          <span>{{ row.location || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="参会人员" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.attendees || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="议题" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.agenda || '-' }}</span>
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
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑会议' : '新建会议'" width="600px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="会议主题" required>
          <el-input v-model="form.title" maxlength="200" />
        </el-form-item>
        <el-form-item label="会议日期">
          <el-date-picker v-model="form.meeting_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="地点">
          <el-input v-model="form.location" maxlength="200" />
        </el-form-item>
        <el-form-item label="参会人员">
          <el-input v-model="form.attendees" placeholder="姓名 / ID，逗号分隔" maxlength="500" />
        </el-form-item>
        <el-form-item label="议题">
          <el-input v-model="form.agenda" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="会议纪要">
          <el-input v-model="form.minutes" type="textarea" :rows="5" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { listMeetings, createMeeting, updateMeeting, deleteMeeting } from '@/api/project'
import type { ProjectMeeting } from '@/types/project'

const props = defineProps<{ projectId: number }>()
const emit = defineEmits<{ (e: 'changed'): void }>()

const loading = ref(false)
const saving = ref(false)
const list = ref<ProjectMeeting[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({
  title: '',
  meeting_date: '',
  location: '',
  attendees: '',
  agenda: '',
  minutes: '',
})

async function load() {
  loading.value = true
  try {
    list.value = await listMeetings(props.projectId)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载会议失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    title: '', meeting_date: '', location: '', attendees: '', agenda: '', minutes: '',
  })
  dialogVisible.value = true
}

function openEdit(row: ProjectMeeting) {
  editingId.value = row.id
  Object.assign(form, {
    title: row.title,
    meeting_date: row.meeting_date || '',
    location: row.location || '',
    attendees: row.attendees || '',
    agenda: row.agenda || '',
    minutes: row.minutes || '',
  })
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.title.trim()) {
    ElMessage.warning('请输入会议主题')
    return
  }
  saving.value = true
  try {
    const payload = {
      title: form.title.trim(),
      meeting_date: form.meeting_date || undefined,
      location: form.location || undefined,
      attendees: form.attendees || undefined,
      agenda: form.agenda || undefined,
      minutes: form.minutes || undefined,
    }
    if (editingId.value) {
      await updateMeeting(props.projectId, editingId.value, payload)
      ElMessage.success('会议已更新')
    } else {
      await createMeeting(props.projectId, payload)
      ElMessage.success('会议已创建')
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

async function handleDelete(row: ProjectMeeting) {
  try {
    await ElMessageBox.confirm(`确定删除会议「${row.title}」？`, '提示', { type: 'warning' })
    await deleteMeeting(props.projectId, row.id)
    ElMessage.success('会议已删除')
    await load()
    emit('changed')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.meetings-tab {
  .tab-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;

    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}
</style>
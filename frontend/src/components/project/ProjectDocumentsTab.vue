<template>
  <div class="documents-tab">
    <div class="tab-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="openCreate">上传文档</el-button>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
      </div>
    </div>

    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="title" label="文档名称" min-width="220" show-overflow-tooltip />
      <el-table-column label="类型" width="120">
        <template #default="{ row }">
          <el-tag size="small" effect="plain">{{ row.doc_type || '其他' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="版本" width="90">
        <template #default="{ row }">
          <span>{{ row.version || 'v1.0' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="链接" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <a v-if="row.url" :href="row.url" target="_blank" rel="noopener" class="doc-link">{{ row.url }}</a>
          <span v-else>-</span>
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
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑文档' : '上传文档'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="文档名称" required>
          <el-input v-model="form.title" maxlength="200" />
        </el-form-item>
        <el-form-item label="文档类型">
          <el-input v-model="form.doc_type" placeholder="如 需求文档 / 设计文档 / 会议纪要" maxlength="50" />
        </el-form-item>
        <el-form-item label="版本">
          <el-input v-model="form.version" placeholder="如 v1.0" maxlength="30" />
        </el-form-item>
        <el-form-item label="链接">
          <el-input v-model="form.url" placeholder="https://..." maxlength="500" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="4" />
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
import { listDocuments, createDocument, updateDocument, deleteDocument } from '@/api/project'
import type { ProjectDocument } from '@/types/project'

const props = defineProps<{ projectId: number }>()
const emit = defineEmits<{ (e: 'changed'): void }>()

const loading = ref(false)
const saving = ref(false)
const list = ref<ProjectDocument[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({
  title: '',
  doc_type: '',
  url: '',
  content: '',
  version: 'v1.0',
})

async function load() {
  loading.value = true
  try {
    list.value = await listDocuments(props.projectId)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载文档失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    title: '', doc_type: '', url: '', content: '', version: 'v1.0',
  })
  dialogVisible.value = true
}

function openEdit(row: ProjectDocument) {
  editingId.value = row.id
  Object.assign(form, {
    title: row.title,
    doc_type: row.doc_type || '',
    url: row.url || '',
    content: row.content || '',
    version: row.version || 'v1.0',
  })
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.title.trim()) {
    ElMessage.warning('请输入文档名称')
    return
  }
  saving.value = true
  try {
    const payload = {
      title: form.title.trim(),
      doc_type: form.doc_type.trim() || '其他',
      url: form.url.trim() || undefined,
      content: form.content || undefined,
      version: form.version.trim() || 'v1.0',
    }
    if (editingId.value) {
      await updateDocument(props.projectId, editingId.value, payload)
      ElMessage.success('文档已更新')
    } else {
      await createDocument(props.projectId, payload)
      ElMessage.success('文档已创建')
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

async function handleDelete(row: ProjectDocument) {
  try {
    await ElMessageBox.confirm(`确定删除文档「${row.title}」？`, '提示', { type: 'warning' })
    await deleteDocument(props.projectId, row.id)
    ElMessage.success('文档已删除')
    await load()
    emit('changed')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.documents-tab {
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

  .doc-link {
    color: #3b82f6;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
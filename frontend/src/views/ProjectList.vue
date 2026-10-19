<template>
  <div class="project-list-page">
    <!-- 头部 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">项目管理</h2>
        <p class="page-subtitle">统一管理项目、任务、风险、会议、文档与变更</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="loadList">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建项目</el-button>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <el-input
        v-model="query.keyword"
        placeholder="搜索项目名称 / 编号"
        clearable
        style="width: 240px"
        :prefix-icon="Search"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 140px" @change="handleSearch">
        <el-option label="规划中" value="planning" />
        <el-option label="进行中" value="active" />
        <el-option label="已暂停" value="paused" />
        <el-option label="已完成" value="completed" />
        <el-option label="已归档" value="archived" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
    </div>

    <!-- 项目卡片列表 -->
    <div v-loading="loading" class="project-grid">
      <el-card
        v-for="p in list"
        :key="p.id"
        class="project-card"
        shadow="hover"
        @click="goDetail(p.id)"
      >
        <div class="card-header">
          <div class="card-title">
            <span class="code" v-if="p.code">{{ p.code }}</span>
            <span class="name">{{ p.name }}</span>
          </div>
          <div class="card-tools">
            <el-tag :type="statusTagType(p.status)" size="small">{{ statusLabel(p.status) }}</el-tag>
            <el-button link type="primary" :icon="Edit" size="small" @click.stop="openEdit(p)">编辑</el-button>
          </div>
        </div>
        <div class="card-desc">{{ p.description || '暂无描述' }}</div>
        <div class="card-meta">
          <el-tag :type="priorityTagType(p.priority)" size="small" effect="plain">
            {{ priorityLabel(p.priority) }}
          </el-tag>
          <span class="date" v-if="p.due_date">截止 {{ p.due_date }}</span>
        </div>
        <div class="card-progress">
          <span class="progress-label">进度</span>
          <el-progress :percentage="p.progress || 0" :stroke-width="8" />
        </div>
      </el-card>
    </div>

    <el-empty v-if="!loading && list.length === 0" description="暂无项目，点击右上角新建" />

    <!-- 新建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑项目' : '新建项目'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="项目名称" required>
          <el-input v-model="form.name" placeholder="请输入项目名称" maxlength="200" />
        </el-form-item>
        <el-form-item label="项目编号">
          <el-input v-model="form.code" placeholder="如 PRJ-2025-001" maxlength="50" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="项目目标、范围等" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="规划中" value="planning" />
            <el-option label="进行中" value="active" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已完成" value="completed" />
            <el-option label="已归档" value="archived" />
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Refresh, Search, Edit } from '@element-plus/icons-vue'
import { listProjects, createProject, updateProject } from '@/api/project'
import type { Project, ProjectStatus, ProjectPriority } from '@/types/project'

const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const list = ref<Project[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const query = reactive({
  keyword: '',
  status: '' as ProjectStatus | '',
})

const form = reactive({
  name: '',
  code: '',
  description: '',
  status: 'planning' as ProjectStatus,
  priority: 'medium' as ProjectPriority,
  start_date: '',
  due_date: '',
  progress: 0,
})

// ============ 加载 ============
async function loadList() {
  loading.value = true
  try {
    list.value = await listProjects({
      keyword: query.keyword || undefined,
      status: query.status || undefined,
    })
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载项目列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  loadList()
}

// ============ 新建/编辑 ============
function openCreate() {
  editingId.value = null
  Object.assign(form, {
    name: '', code: '', description: '',
    status: 'planning', priority: 'medium',
    start_date: '', due_date: '', progress: 0,
  })
  dialogVisible.value = true
}

function openEdit(p: Project) {
  editingId.value = p.id
  Object.assign(form, {
    name: p.name,
    code: p.code || '',
    description: p.description || '',
    status: p.status,
    priority: p.priority,
    start_date: p.start_date || '',
    due_date: p.due_date || '',
    progress: p.progress || 0,
  })
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入项目名称')
    return
  }
  saving.value = true
  try {
    const payload = {
      name: form.name.trim(),
      code: form.code.trim() || undefined,
      description: form.description || undefined,
      status: form.status,
      priority: form.priority,
      start_date: form.start_date || undefined,
      due_date: form.due_date || undefined,
      progress: form.progress,
    }
    if (editingId.value) {
      await updateProject(editingId.value, payload)
      ElMessage.success('项目已更新')
    } else {
      await createProject(payload)
      ElMessage.success('项目已创建')
    }
    dialogVisible.value = false
    await loadList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// ============ 跳转 ============
function goDetail(id: number) {
  router.push(`/projects/${id}`)
}

// ============ 展示辅助 ============
function statusLabel(s: ProjectStatus): string {
  return { planning: '规划中', active: '进行中', paused: '已暂停', completed: '已完成', archived: '已归档' }[s] || s
}

function statusTagType(s: ProjectStatus): 'primary' | 'success' | 'warning' | 'info' | 'danger' {
  const map: Record<ProjectStatus, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    planning: 'info',
    active: 'primary',
    paused: 'warning',
    completed: 'success',
    archived: 'info',
  }
  return map[s]
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

onMounted(loadList)
</script>

<style scoped lang="scss">
.project-list-page {
  padding: 4px 0;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 16px;

  .page-title {
    font-size: 22px;
    font-weight: 700;
    margin: 0 0 4px;
  }

  .page-subtitle {
    font-size: 13px;
    color: #94a3b8;
    margin: 0;
  }
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.project-card {
  cursor: pointer;

  .card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;

    .card-title {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;

      .code {
        font-size: 12px;
        color: #3b82f6;
        background: #eff6ff;
        border-radius: 4px;
        padding: 2px 6px;
        white-space: nowrap;
      }

      .name {
        font-size: 15px;
        font-weight: 600;
        color: #1e293b;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }

  .card-desc {
    font-size: 13px;
    color: #64748b;
    margin: 10px 0;
    min-height: 20px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .card-tools {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .card-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;

    .date {
      font-size: 12px;
      color: #94a3b8;
    }
  }

  .card-progress {
    display: flex;
    align-items: center;
    gap: 10px;

    .progress-label {
      font-size: 12px;
      color: #94a3b8;
      flex-shrink: 0;
    }
  }
}
</style>
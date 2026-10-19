<template>
  <div class="project-detail-page" v-loading="loading">
    <template v-if="project">
      <!-- 头部 -->
      <div class="page-header">
        <div class="header-left">
          <el-button link :icon="ArrowLeft" @click="goBack">返回</el-button>
          <div>
            <div class="title-row">
              <span class="code" v-if="project.code">{{ project.code }}</span>
              <h2 class="name">{{ project.name }}</h2>
              <el-tag :type="statusTagType(project.status)" size="small">{{ statusLabel(project.status) }}</el-tag>
              <el-tag :type="priorityTagType(project.priority)" size="small" effect="plain">
                {{ priorityLabel(project.priority) }}
              </el-tag>
            </div>
            <p class="desc">{{ project.description || '暂无描述' }}</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button :icon="Edit" @click="openEdit">编辑</el-button>
          <el-button :icon="User" @click="membersVisible = true">成员管理</el-button>
          <el-dropdown @command="handleMore">
            <el-button :icon="MoreFilled">更多</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="refresh">刷新</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除项目</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stat-grid">
        <div class="stat-card" v-for="s in statCards" :key="s.label" @click="s.key ? activeTab = s.key : undefined">
          <div class="stat-icon" :style="{ background: s.bg, color: s.color }">
            <el-icon :size="18"><component :is="s.icon" /></el-icon>
          </div>
          <div class="stat-body">
            <div class="stat-value">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </div>
      </div>

      <!-- 标签页 -->
      <div class="tab-card">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="任务" name="tasks">
            <ProjectTasksTab :project-id="project.id" @changed="loadStats" />
          </el-tab-pane>
          <el-tab-pane label="看板" name="kanban">
            <KanbanBoard :project-id="project.id" @changed="loadStats" />
          </el-tab-pane>
          <el-tab-pane label="WBS" name="wbs">
            <div class="wbs-container">
              <WbsTreeNode :project-id="project.id" />
            </div>
          </el-tab-pane>
          <el-tab-pane label="风险" name="risks">
            <ProjectRisksTab :project-id="project.id" @changed="loadStats" />
          </el-tab-pane>
          <el-tab-pane label="会议" name="meetings">
            <ProjectMeetingsTab :project-id="project.id" @changed="loadStats" />
          </el-tab-pane>
          <el-tab-pane label="文档" name="documents">
            <ProjectDocumentsTab :project-id="project.id" @changed="loadStats" />
          </el-tab-pane>
          <el-tab-pane label="变更" name="changes">
            <ProjectChangesTab :project-id="project.id" @changed="loadStats" />
          </el-tab-pane>
          <el-tab-pane label="讨论" name="comments">
            <div class="comments-panel">
              <div class="comment-input">
                <el-input
                  v-model="commentText"
                  type="textarea"
                  :rows="2"
                  placeholder="发表评论 / 项目动态..."
                />
                <el-button type="primary" :loading="commentSaving" @click="sendComment">发表</el-button>
              </div>
              <div class="comment-list" v-loading="commentLoading">
                <div v-for="c in comments" :key="c.id" class="comment-item">
                  <div class="comment-head">
                    <span class="author">{{ c.username || '用户' }}</span>
                    <span class="time">{{ c.created_at }}</span>
                  </div>
                  <div class="comment-content">{{ c.content }}</div>
                </div>
                <el-empty v-if="!commentLoading && comments.length === 0" description="暂无评论" :image-size="60" />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 聊天视图 -->
      <ChatView :project-id="project.id" class="chat-view" />

      <!-- 成员管理对话框 -->
      <ProjectMembersDialog
        v-model="membersVisible"
        :project-id="project.id"
        @changed="loadStats"
      />
    </template>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="编辑项目" width="560px">
      <el-form :model="editForm" label-width="90px">
        <el-form-item label="项目名称" required>
          <el-input v-model="editForm.name" maxlength="200" />
        </el-form-item>
        <el-form-item label="项目编号">
          <el-input v-model="editForm.code" maxlength="50" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="规划中" value="planning" />
            <el-option label="进行中" value="active" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已完成" value="completed" />
            <el-option label="已归档" value="archived" />
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
        <el-form-item label="开始日期">
          <el-date-picker v-model="editForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="editForm.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="进度(%)">
          <el-slider v-model="editForm.progress" :max="100" show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Edit, User, MoreFilled,
  List, Checked, Warning, Calendar, Document, RefreshRight, Share,
} from '@element-plus/icons-vue'
import { getProject, updateProject, deleteProject, getProjectStats, listComments, createComment } from '@/api/project'
import type { Project, ProjectStats, ProjectStatus, ProjectPriority, ProjectComment } from '@/types/project'
import ProjectTasksTab from '@/components/project/ProjectTasksTab.vue'
import KanbanBoard from '@/components/project/KanbanBoard.vue'
import WbsTreeNode from '@/components/project/WbsTreeNode.vue'
import ProjectRisksTab from '@/components/project/ProjectRisksTab.vue'
import ProjectMeetingsTab from '@/components/project/ProjectMeetingsTab.vue'
import ProjectDocumentsTab from '@/components/project/ProjectDocumentsTab.vue'
import ProjectChangesTab from '@/components/project/ProjectChangesTab.vue'
import ProjectMembersDialog from '@/components/project/ProjectMembersDialog.vue'
import ChatView from '@/components/project/ChatView.vue'

const route = useRoute()
const router = useRouter()

const projectId = computed(() => Number(route.params.id))

const loading = ref(false)
const saving = ref(false)
const project = ref<Project | null>(null)
const stats = ref<ProjectStats | null>(null)
const activeTab = ref('tasks')

const membersVisible = ref(false)
const editVisible = ref(false)

const comments = ref<ProjectComment[]>([])
const commentText = ref('')
const commentLoading = ref(false)
const commentSaving = ref(false)

const editForm = reactive({
  name: '',
  code: '',
  description: '',
  status: 'planning' as ProjectStatus,
  priority: 'medium' as ProjectPriority,
  start_date: '',
  due_date: '',
  progress: 0,
})

// ============ 统计卡片 ============
const statCards = computed(() => [
  { label: '任务总数', value: stats.value?.task_total ?? 0, key: 'tasks', icon: List, bg: '#eff6ff', color: '#3b82f6' },
  { label: '已完成任务', value: stats.value?.task_done ?? 0, key: 'tasks', icon: Checked, bg: '#ecfdf5', color: '#10b981' },
  { label: '未关闭风险', value: stats.value?.risk_open ?? 0, key: 'risks', icon: Warning, bg: '#fef2f2', color: '#ef4444' },
  { label: '会议', value: stats.value?.meeting_total ?? 0, key: 'meetings', icon: Calendar, bg: '#fefce8', color: '#eab308' },
  { label: '文档', value: stats.value?.document_total ?? 0, key: 'documents', icon: Document, bg: '#f5f3ff', color: '#8b5cf6' },
  { label: '待批变更', value: stats.value?.change_open ?? 0, key: 'changes', icon: RefreshRight, bg: '#fff7ed', color: '#f97316' },
  { label: '成员', value: stats.value?.member_total ?? 0, key: '', icon: User, bg: '#ecfeff', color: '#06b6d4' },
  { label: '评论', value: stats.value?.comment_total ?? 0, key: 'comments', icon: Share, bg: '#f1f5f9', color: '#64748b' },
])

// ============ 加载 ============
async function loadProject() {
  try {
    project.value = await getProject(projectId.value)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载项目失败')
  }
}

async function loadStats() {
  try {
    stats.value = await getProjectStats(projectId.value)
  } catch (e: any) {
    // 忽略统计错误
  }
}

async function loadComments() {
  commentLoading.value = true
  try {
    comments.value = await listComments(projectId.value)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载评论失败')
  } finally {
    commentLoading.value = false
  }
}

async function sendComment() {
  const content = commentText.value.trim()
  if (!content) return
  commentSaving.value = true
  try {
    await createComment(projectId.value, content)
    commentText.value = ''
    ElMessage.success('评论已发布')
    await loadComments()
    await loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '发布失败')
  } finally {
    commentSaving.value = false
  }
}

// ============ 编辑 ============
function openEdit() {
  if (!project.value) return
  Object.assign(editForm, {
    name: project.value.name,
    code: project.value.code || '',
    description: project.value.description || '',
    status: project.value.status,
    priority: project.value.priority,
    start_date: project.value.start_date || '',
    due_date: project.value.due_date || '',
    progress: project.value.progress || 0,
  })
  editVisible.value = true
}

async function handleEditSave() {
  if (!editForm.name.trim()) {
    ElMessage.warning('请输入项目名称')
    return
  }
  saving.value = true
  try {
    project.value = await updateProject(projectId.value, {
      name: editForm.name.trim(),
      code: editForm.code.trim() || undefined,
      description: editForm.description || undefined,
      status: editForm.status,
      priority: editForm.priority,
      start_date: editForm.start_date || undefined,
      due_date: editForm.due_date || undefined,
      progress: editForm.progress,
    })
    editVisible.value = false
    ElMessage.success('项目已更新')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '更新失败')
  } finally {
    saving.value = false
  }
}

// ============ 更多操作 ============
async function handleMore(cmd: string) {
  if (cmd === 'refresh') {
    await Promise.all([loadProject(), loadStats(), loadComments()])
  } else if (cmd === 'delete') {
    try {
      await ElMessageBox.confirm('确定删除该项目？此操作不可恢复！', '警告', { type: 'error' })
      await deleteProject(projectId.value)
      ElMessage.success('项目已删除')
      router.push('/projects')
    } catch (e: any) {
      if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || '删除失败')
    }
  }
}

function goBack() {
  router.push('/projects')
}

// ============ 辅助 ============
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

onMounted(() => {
  Promise.all([loadProject(), loadStats(), loadComments()])
})
</script>

<style scoped lang="scss">
.project-detail-page {
  padding: 4px 0;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;

  .header-left {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    min-width: 0;

    .title-row {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;

      .code {
        font-size: 12px;
        color: #3b82f6;
        background: #eff6ff;
        border-radius: 4px;
        padding: 2px 6px;
      }

      .name {
        font-size: 20px;
        font-weight: 700;
        margin: 0;
        color: #1e293b;
      }
    }

    .desc {
      font-size: 13px;
      color: #64748b;
      margin: 6px 0 0;
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 12px;
  margin-bottom: 16px;

  @media (max-width: 1400px) {
    grid-template-columns: repeat(4, 1fr);
  }

  .stat-card {
    background: #fff;
    border-radius: 10px;
    padding: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    border: 1px solid #f1f5f9;
    cursor: default;

    .stat-icon {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .stat-body {
      .stat-value {
        font-size: 18px;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.2;
      }

      .stat-label {
        font-size: 12px;
        color: #94a3b8;
      }
    }
  }
}

.tab-card {
  background: #fff;
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  border: 1px solid #f1f5f9;
  min-height: 400px;
}

.wbs-container {
  padding: 8px 0;
}

.comments-panel {
  .comment-input {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
  }

  .comment-list {
    max-height: 480px;
    overflow-y: auto;

    .comment-item {
      padding: 10px 0;
      border-bottom: 1px dashed #f1f5f9;

      &:last-child {
        border-bottom: none;
      }

      .comment-head {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;

        .author {
          font-size: 13px;
          font-weight: 600;
          color: #1e293b;
        }

        .time {
          font-size: 12px;
          color: #94a3b8;
        }
      }

      .comment-content {
        font-size: 14px;
        color: #334155;
        line-height: 1.6;
      }
    }
  }
}

.chat-view {
  margin-top: 16px;
}
</style>
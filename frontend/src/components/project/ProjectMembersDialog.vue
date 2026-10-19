<template>
  <el-dialog
    :model-value="modelValue"
    title="成员管理"
    width="640px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="members-dialog">
      <div class="add-row">
        <el-input-number v-model="newUserId" :min="1" :controls="false" placeholder="用户ID" style="width: 140px" />
        <el-select v-model="newRole" style="width: 120px">
          <el-option label="管理员" value="admin" />
          <el-option label="成员" value="member" />
          <el-option label="只读" value="viewer" />
        </el-select>
        <el-button type="primary" :icon="Plus" :loading="saving" @click="handleAdd">添加成员</el-button>
      </div>

      <el-table :data="list" v-loading="loading" size="small" stripe>
        <el-table-column prop="user_id" label="用户ID" width="90" />
        <el-table-column label="用户名" min-width="120">
          <template #default="{ row }">
            <span>{{ row.username || `#${row.user_id}` }}</span>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="110">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="加入时间" width="120">
          <template #default="{ row }">
            <span>{{ row.joined_at || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <template v-if="row.role !== 'owner'">
              <el-dropdown @command="(cmd: string) => handleRoleCommand(cmd, row)">
                <el-button link type="primary">角色</el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="admin">设为管理员</el-dropdown-item>
                    <el-dropdown-item command="member">设为成员</el-dropdown-item>
                    <el-dropdown-item command="viewer">设为只读</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button link type="danger" :icon="Delete" @click="handleRemove(row)">移除</el-button>
            </template>
            <span v-else class="owner-text">所有者</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { listMembers, addMember, updateMemberRole, removeMember } from '@/api/project'
import type { ProjectMember, ProjectMemberRole } from '@/types/project'

const props = defineProps<{
  modelValue: boolean
  projectId: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'changed'): void
}>()

const loading = ref(false)
const saving = ref(false)
const list = ref<ProjectMember[]>([])
const newUserId = ref<number | undefined>(undefined)
const newRole = ref<ProjectMemberRole>('member')

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) load()
  },
)

async function load() {
  loading.value = true
  try {
    list.value = await listMembers(props.projectId)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载成员失败')
  } finally {
    loading.value = false
  }
}

async function handleAdd() {
  if (!newUserId.value) {
    ElMessage.warning('请输入用户ID')
    return
  }
  saving.value = true
  try {
    await addMember(props.projectId, { user_id: newUserId.value, role: newRole.value })
    ElMessage.success('成员已添加')
    newUserId.value = undefined
    await load()
    emit('changed')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '添加成员失败')
  } finally {
    saving.value = false
  }
}

async function handleRoleCommand(cmd: string, row: ProjectMember) {
  if (row.role === cmd) return
  try {
    await updateMemberRole(props.projectId, row.id, cmd as ProjectMemberRole)
    ElMessage.success('角色已更新')
    await load()
    emit('changed')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '更新角色失败')
  }
}

async function handleRemove(row: ProjectMember) {
  try {
    await ElMessageBox.confirm(`确定移除成员「${row.username || row.user_id}」？`, '提示', { type: 'warning' })
    await removeMember(props.projectId, row.id)
    ElMessage.success('成员已移除')
    await load()
    emit('changed')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || '移除成员失败')
  }
}

// ============ 类型化辅助函数 ============
function roleLabel(role: ProjectMemberRole): string {
  return { owner: '所有者', admin: '管理员', member: '成员', viewer: '只读' }[role] || role
}

function roleTagType(role: ProjectMemberRole): 'primary' | 'success' | 'warning' | 'info' | 'danger' {
  const map: Record<ProjectMemberRole, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    owner: 'danger',
    admin: 'warning',
    member: 'primary',
    viewer: 'info',
  }
  return map[role]
}

onMounted(() => {
  if (props.modelValue) load()
})
</script>

<style scoped lang="scss">
.members-dialog {
  .add-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  .owner-text {
    font-size: 12px;
    color: #94a3b8;
  }
}
</style>
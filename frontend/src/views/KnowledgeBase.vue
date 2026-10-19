<template>
  <div class="knowledge-page">
    <!-- ========== 搜索栏 ========== -->
    <div class="search-bar">
      <div class="form-item">
        <label>标题</label>
        <el-input
          v-model="query.title"
          placeholder="请输入标题"
          clearable
          style="width: 180px"
          @keyup.enter="handleSearch"
        />
      </div>

      <div class="form-item">
        <label>类型</label>
        <el-select v-model="query.type" placeholder="全部" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="用户消息" value="user" />
          <el-option label="机器人消息" value="bot" />
          <el-option label="人工消息" value="agent" />
        </el-select>
      </div>

      <div class="form-item">
        <label>标签</label>
        <el-select v-model="query.tag" placeholder="全部" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="对话" value="dialog" />
          <el-option label="商品" value="product" />
        </el-select>
      </div>

      <div class="form-item">
        <label>创建时间</label>
        <el-date-picker
          v-model="query.dateRange"
          type="daterange"
          range-separator="→"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 240px"
          value-format="YYYY-MM-DD"
        />
      </div>

      <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
      <el-button :icon="RefreshLeft" @click="handleReset">重置</el-button>
    </div>

    <!-- ========== 工具栏 ========== -->
    <div class="toolbar">
      <el-button type="primary" :icon="Plus" @click="handleAdd">新增记忆</el-button>
      <el-button type="success" :icon="Upload" @click="handleImport">文件导入</el-button>
      <el-button type="warning" :icon="Link" @click="handleWebImport">网页采集</el-button>
      <el-button :icon="Search" @click="handleSemanticSearch">语义检索</el-button>
      <el-button :icon="DataAnalysis" @click="handleStats">统计</el-button>
      <el-button type="danger" :icon="Delete" @click="handleBatchDelete">批量删除</el-button>
      <el-button type="danger" plain :icon="DeleteFilled" @click="handleClearAll">清空记忆库</el-button>
    </div>

    <!-- ========== 表格 ========== -->
    <el-table
      :data="list"
      v-loading="loading"
      stripe
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="50" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" show-overflow-tooltip min-width="240" />
      <el-table-column prop="type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag type="info" size="small">{{ row.type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="tag" label="标签" width="120">
        <template #default="{ row }">
          <el-tag size="small">{{ row.tag }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="source" label="来源" width="180" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" :icon="View" @click="handleView(row)">查看</el-button>
          <el-button link type="warning" :icon="Edit" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="danger" :icon="Delete" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- ========== 分页 ========== -->
    <div class="pagination">
      <span class="total">共 {{ total }} 条</span>
      <el-pagination
        v-model:current-page="page.current"
        v-model:page-size="page.size"
        :page-sizes="[10, 20, 50, 100]"
        layout="sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- ========== 查看详情弹窗 ========== -->
    <el-dialog v-model="viewVisible" title="记忆详情" width="600px">
      <div v-if="currentRow" class="detail">
        <div class="detail-item">
          <span class="label">ID：</span>
          <span>{{ currentRow.id }}</span>
        </div>
        <div class="detail-item">
          <span class="label">类型：</span>
          <span>{{ currentRow.type }}</span>
        </div>
        <div class="detail-item">
          <span class="label">来源：</span>
          <span>{{ currentRow.source }}</span>
        </div>
        <div class="detail-item">
          <span class="label">时间：</span>
          <span>{{ currentRow.created_at }}</span>
        </div>
        <div class="detail-item">
          <span class="label">内容：</span>
          <div class="content">{{ currentRow.title }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, RefreshLeft, Plus, Upload, Link, DataAnalysis,
  Delete, DeleteFilled, View, Edit,
} from '@element-plus/icons-vue'
import {
  listMemory,
  deleteMemory,
  batchDeleteMemory,
  clearAllMemory,
} from '@/api/memory'

// ============ 状态 ============
const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const selectedRows = ref<any[]>([])
const viewVisible = ref(false)
const currentRow = ref<any>(null)

const query = ref({
  title: '',
  type: '',
  tag: '',
  dateRange: [] as string[],
})

const page = ref({
  current: 1,
  size: 10,
})

// ============ 加载列表 ============
async function loadList() {
  loading.value = true
  try {
    const res: any = await listMemory({
      title: query.value.title || undefined,
      type: query.value.type || undefined,
      page: page.value.current,
      size: page.value.size,
    })
    list.value = res.items || []
    total.value = res.total || 0
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载失败')
    list.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// ============ 搜索 ============
function handleSearch() {
  page.value.current = 1
  loadList()
}

function handleReset() {
  query.value = { title: '', type: '', tag: '', dateRange: [] }
  page.value.current = 1
  loadList()
}

// ============ 分页 ============
function handleSizeChange(size: number) {
  page.value.size = size
  page.value.current = 1
  loadList()
}

function handlePageChange(current: number) {
  page.value.current = current
  loadList()
}

// ============ 多选 ============
function handleSelectionChange(rows: any[]) {
  selectedRows.value = rows
}

// ============ 工具栏操作 ============
function handleAdd() {
  ElMessage.info('新增记忆功能待开发')
}

function handleImport() {
  ElMessage.info('文件导入功能待开发')
}

function handleWebImport() {
  ElMessage.info('网页采集功能待开发')
}

async function handleSemanticSearch() {
  const { value } = await ElMessageBox.prompt('请输入检索关键词', '语义检索', {
    confirmButtonText: '检索',
    cancelButtonText: '取消',
  }).catch(() => ({ value: '' }))

  if (!value) return
  loading.value = true
  try {
    const res: any = await import('@/api/memory').then((m) =>
      m.semanticSearch(value),
    )
    list.value = (res.items || []).map((item: any) => ({
      id: item.id,
      title: item.content,
      type: item.sender_type === 'user' ? '用户消息' : '机器人消息',
      tag: '对话',
      source: `message-${item.id}`,
      created_at: item.created_at,
    }))
    total.value = list.value.length
    ElMessage.success(`检索到 ${total.value} 条`)
  } catch (e) {
    ElMessage.error('检索失败')
  } finally {
    loading.value = false
  }
}

async function handleStats() {
  try {
    const res: any = await import('@/api/memory').then((m) => m.memoryStats())
    ElMessageBox.alert(
      `总记忆：${res.total} 条\n用户消息：${res.user_count} 条\n机器人消息：${res.bot_count} 条`,
      '记忆统计',
      { confirmButtonText: '知道了' },
    )
  } catch (e) {
    ElMessage.error('统计失败')
  }
}

// ============ 删除操作 ============
async function handleBatchDelete() {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先勾选要删除的记录')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedRows.value.length} 条记录？`,
      '提示',
      { type: 'warning' },
    )
    const ids = selectedRows.value.map((r) => r.id)
    await batchDeleteMemory(ids)
    ElMessage.success('删除成功')
    selectedRows.value = []
    await loadList()
  } catch (e) {
    // 用户取消或删除失败
  }
}

async function handleClearAll() {
  try {
    await ElMessageBox.confirm('确定清空整个记忆库？此操作不可恢复！', '警告', {
      type: 'error',
      confirmButtonText: '确定清空',
      cancelButtonText: '取消',
    })
    await clearAllMemory()
    ElMessage.success('已清空')
    page.value.current = 1
    await loadList()
  } catch (e) {
    // 用户取消
  }
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(`确定删除 #${row.id}？`, '提示', {
      type: 'warning',
    })
    await deleteMemory(row.id)
    ElMessage.success('删除成功')
    await loadList()
  } catch (e) {
    // 用户取消
  }
}

// ============ 查看/编辑 ============
function handleView(row: any) {
  currentRow.value = row
  viewVisible.value = true
}

function handleEdit(row: any) {
  ElMessage.info(`编辑 #${row.id} 功能待开发`)
}

// ============ 初始化 ============
onMounted(loadList)
</script>

<style scoped lang="scss">
.knowledge-page {
  background: #fff;
  padding: 16px 20px;
  border-radius: 12px;
  min-height: calc(100vh - 140px);
}

// ========== 搜索栏 ==========
.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 16px;

  .form-item {
    display: flex;
    align-items: center;
    gap: 8px;

    label {
      font-size: 13px;
      color: #64748b;
      white-space: nowrap;
    }
  }
}

// ========== 工具栏 ==========
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;

  :deep(.el-button) {
    border-radius: 6px;
  }
}

// ========== 分页 ==========
.pagination {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;

  .total {
    font-size: 13px;
    color: #64748b;
  }
}

// ========== 详情弹窗 ==========
.detail {
  .detail-item {
    display: flex;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px dashed #f1f5f9;
    font-size: 14px;

    &:last-child {
      border-bottom: none;
    }

    .label {
      color: #64748b;
      flex-shrink: 0;
      width: 60px;
    }

    .content {
      flex: 1;
      color: #1e293b;
      line-height: 1.7;
      word-break: break-word;
    }
  }
}
</style>
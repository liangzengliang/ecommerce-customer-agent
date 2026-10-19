<template>
  <div class="model-page">
    <!-- ========== 顶部提示 ========== -->
    <div class="tip-banner">
      <el-icon><InfoFilled /></el-icon>
      <span>
        所有模型均在页面配置：厂商统一走 OpenAI 兼容协议（baseUrl + apiKey + model），
        chat 类型用于对话与工具调用，embedding 类型用于记忆向量化。
        <strong>已启用的默认模型优先级高于 .env 文件。</strong>
      </span>
    </div>

    <!-- ========== 搜索栏 ========== -->
    <div class="search-bar">
      <div class="form-item">
        <label>类型</label>
        <el-select v-model="query.type" placeholder="全部" clearable style="width: 140px">
          <el-option label="全部" value="" />
          <el-option label="对话" value="chat" />
          <el-option label="向量" value="embedding" />
        </el-select>
      </div>

      <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
      <el-button :icon="RefreshLeft" @click="handleReset">重置</el-button>
    </div>

    <!-- ========== 工具栏 ========== -->
    <div class="toolbar">
      <el-button type="primary" :icon="Plus" @click="handleAdd">新增模型</el-button>
      <el-button :icon="Refresh" @click="handleRefresh">刷新</el-button>
      <el-button :icon="Tools" @click="handleTools">可用工具清单</el-button>
    </div>

    <!-- ========== 表格 ========== -->
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column type="selection" width="50" />
      <el-table-column prop="id" label="ID" width="70" />

      <el-table-column prop="name" label="配置名称" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <span :class="{ 'disabled-text': !row.is_active }">{{ row.name }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="provider" label="服务商" width="110" />
      <el-table-column prop="type" label="类型" width="90">
        <template #default="{ row }">
          <el-tag :type="row.type === 'chat' ? 'primary' : 'success'" size="small">
            {{ row.type === 'chat' ? '对话' : '向量' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="model" label="模型名称" min-width="160" show-overflow-tooltip />

      <el-table-column prop="is_default" label="默认" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="warning" size="small">默认</el-tag>
          <span v-else style="color: #94a3b8">-</span>
        </template>
      </el-table-column>

      <!-- ★ 状态列：启用/停用 -->
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag v-if="row.is_active" type="success" size="small" effect="light">
            已启用
          </el-tag>
          <el-tag v-else type="info" size="small" effect="light">
            已停用
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="380" fixed="right">
        <template #default="{ row }">
          <el-button link type="success" :icon="Connection" @click="handleTestExisting(row)">
            测试
          </el-button>

          <!-- ★ 启用/停用切换 -->
          <el-button
            link
            :type="row.is_active ? 'info' : 'success'"
            :icon="row.is_active ? VideoPause : VideoPlay"
            @click="handleToggle(row)"
          >
            {{ row.is_active ? '暂停' : '启用' }}
          </el-button>

          <el-button
            link
            type="primary"
            :icon="Select"
            :disabled="row.is_default || !row.is_active"
            @click="handleSetDefault(row)"
          >
            设为默认
          </el-button>
          <el-button link type="warning" :icon="Edit" @click="handleEdit(row)">修改</el-button>
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
        :page-sizes="[10, 20, 50]"
        layout="sizes, prev, pager, next, jumper"
        :total="total"
      />
    </div>

    <!-- ========== 新增/编辑弹窗 ========== -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增模型' : '编辑模型'"
      width="620px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="配置名称" required>
          <el-input v-model="form.name" placeholder="如：DeepSeek-V3对话模型" />
        </el-form-item>

        <el-form-item label="服务商" required>
          <el-select v-model="form.provider" placeholder="请选择" style="width: 100%">
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="硅基流动" value="siliconflow" />
            <el-option label="通义千问" value="dashscope" />
            <el-option label="智谱 GLM" value="zhipu" />
            <el-option label="小米 MiMo" value="xiaomi" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="类型" required>
          <el-radio-group v-model="form.type">
            <el-radio value="chat">对话 (chat)</el-radio>
            <el-radio value="embedding">向量 (embedding)</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="模型名称" required>
          <el-input v-model="form.model" placeholder="如：deepseek-flash" />
        </el-form-item>

        <el-form-item label="接口地址" required>
          <el-input v-model="form.base_url" placeholder="https://api.deepseek.com/v1" />
        </el-form-item>

        <el-form-item label="API Key" required>
          <el-input v-model="form.api_key" placeholder="sk-xxx" show-password />
        </el-form-item>

        <el-form-item label="温度">
          <el-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>

        <el-form-item label="最大Token">
          <el-input-number v-model="form.max_tokens" :min="1" :max="128000" />
        </el-form-item>

        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="2"
            placeholder="可选"
          />
        </el-form-item>

        <!-- 测试结果 -->
        <el-form-item v-if="testResult" label="测试结果">
          <div class="test-result" :class="testResult.success ? 'success' : 'error'">
            <el-icon>
              <CircleCheckFilled v-if="testResult.success" />
              <CircleCloseFilled v-else />
            </el-icon>
            <span>{{ testResult.message }}</span>
            <span v-if="testResult.elapsed_ms" class="elapsed">
              ({{ testResult.elapsed_ms }}ms)
            </span>
            <div v-if="testResult.response" class="response">
              AI 回复：{{ testResult.response }}
            </div>
            <div v-if="testResult.dimension" class="response">
              向量维度：{{ testResult.dimension }}
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button :loading="testing" @click="handleTest">
          <el-icon><Connection /></el-icon>
          <span>测试连接</span>
        </el-button>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, RefreshLeft, Plus, Refresh, Tools,
  Select, Edit, Delete, InfoFilled,
  Connection, CircleCheckFilled, CircleCloseFilled,
  VideoPause, VideoPlay,                          // ★ 新增
} from '@element-plus/icons-vue'
import {
  listModels, createModel, updateModel, deleteModel, setDefaultModel,
  toggleModel, testModel,                          // ★ 新增 toggleModel
  type ModelConfig, type TestResult,
} from '@/api/model'

const loading = ref(false)
const list = ref<ModelConfig[]>([])
const total = ref(0)

const query = ref({ type: '' })
const page = ref({ current: 1, size: 10 })

const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const testing = ref(false)
const testResult = ref<TestResult | null>(null)
const editingId = ref<number | null>(null)

const defaultForm = (): ModelConfig => ({
  name: '',
  provider: 'deepseek',
  type: 'chat',
  model: '',
  base_url: '',
  api_key: '',
  temperature: 0.7,
  max_tokens: 2048,
  is_default: false,
  is_active: true,
  description: '',
})

const form = ref<ModelConfig>(defaultForm())

// ============ 加载列表 ============
async function loadList() {
  loading.value = true
  try {
    const res = await listModels(query.value.type || undefined)
    list.value = (res as any) || []
    total.value = list.value.length
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载失败')
    list.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value.current = 1
  loadList()
}

function handleReset() {
  query.value = { type: '' }
  page.value.current = 1
  loadList()
}

function handleRefresh() {
  loadList()
  ElMessage.success('已刷新')
}

function handleTools() {
  ElMessageBox.alert(
    '可用工具：\n' +
      '1. search_knowledge - 知识库检索\n' +
      '2. query_order - 订单查询\n' +
      '3. query_product - 商品查询\n' +
      '4. request_refund - 申请退款\n' +
      '5. create_ticket - 创建工单\n' +
      '6. transfer_human - 转人工',
    '可用工具清单',
    { confirmButtonText: '知道了' },
  )
}

// ============ ★ 启用/停用 ============
async function handleToggle(row: ModelConfig) {
  const next = !row.is_active
  try {
    await ElMessageBox.confirm(
      next
        ? `确定启用「${row.name}」？`
        : `确定暂停「${row.name}」？暂停后该模型不会被使用。`,
      next ? '启用模型' : '暂停模型',
      { type: 'warning' },
    )
    await toggleModel(row.id!, next)
    ElMessage.success(next ? '已启用' : '已暂停')
    await loadList()
  } catch (e) {}
}

// ============ 测试（弹窗内）============
async function handleTest() {
  if (!form.value.model || !form.value.base_url || !form.value.api_key) {
    ElMessage.warning('请先填写模型名称、接口地址、API Key')
    return
  }
  testing.value = true
  testResult.value = null
  try {
    const res = await testModel(form.value)
    testResult.value = res as any
    if ((res as any).success) ElMessage.success('连通正常')
    else ElMessage.error('测试失败')
  } catch (e: any) {
    testResult.value = {
      success: false,
      message: e?.response?.data?.detail || '测试请求失败',
    }
    ElMessage.error('测试请求失败')
  } finally {
    testing.value = false
  }
}

// ============ 测试（表格行）============
async function handleTestExisting(row: ModelConfig) {
  testing.value = true
  try {
    const res = await testModel(row)
    const r = res as any
    if (r.success) {
      ElMessage.success(`${row.name} 连通正常 (${r.elapsed_ms}ms)`)
    } else {
      ElMessageBox.alert(r.message, `${row.name} 测试失败`, { type: 'error' })
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '测试请求失败')
  } finally {
    testing.value = false
  }
}

// ============ 新增/编辑 ============
function handleAdd() {
  dialogMode.value = 'create'
  editingId.value = null
  form.value = defaultForm()
  testResult.value = null
  dialogVisible.value = true
}

function handleEdit(row: ModelConfig) {
  dialogMode.value = 'edit'
  editingId.value = row.id || null
  form.value = { ...row }
  testResult.value = null
  dialogVisible.value = true
}

// ============ 提交 ============
async function handleSubmit() {
  if (!form.value.name || !form.value.model || !form.value.base_url || !form.value.api_key) {
    ElMessage.warning('请填写必填项')
    return
  }
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await createModel(form.value)
      ElMessage.success('新增成功')
    } else if (editingId.value) {
      await updateModel(editingId.value, form.value)
      ElMessage.success('修改成功')
    }
    dialogVisible.value = false
    await loadList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

// ============ 设为默认 ============
async function handleSetDefault(row: ModelConfig) {
  try {
    await ElMessageBox.confirm(
      `确定将 "${row.name}" 设为默认？之后新的对话将使用此模型。`,
      '提示',
      { type: 'warning' },
    )
    await setDefaultModel(row.id!)
    ElMessage.success('已设为默认')
    await loadList()
  } catch (e) {}
}

// ============ 删除 ============
async function handleDelete(row: ModelConfig) {
  try {
    await ElMessageBox.confirm(`确定删除 "${row.name}"？`, '提示', { type: 'warning' })
    await deleteModel(row.id!)
    ElMessage.success('删除成功')
    await loadList()
  } catch (e) {}
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.model-page {
  background: #fff;
  padding: 16px 20px;
  border-radius: 12px;
  min-height: calc(100vh - 140px);
}

.tip-banner {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 14px;
  background: #eff6ff;
  border-left: 3px solid #3b82f6;
  border-radius: 6px;
  color: #1e40af;
  font-size: 13px;
  line-height: 1.7;
  margin-bottom: 16px;

  .el-icon { color: #3b82f6; flex-shrink: 0; margin-top: 3px; }
}

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

    label { font-size: 13px; color: #64748b; white-space: nowrap; }
  }
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;

  :deep(.el-button) { border-radius: 6px; }
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;

  .total { font-size: 13px; color: #64748b; }
}

// ★ 停用模型文字置灰
.disabled-text {
  color: #94a3b8;
  text-decoration: line-through;
}

.test-result {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.6;
  width: 100%;

  &.success {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;

    .el-icon { color: #22c55e; }
  }

  &.error {
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;

    .el-icon { color: #ef4444; }
  }

  .elapsed {
    font-size: 12px;
    opacity: 0.7;
  }

  .response {
    width: 100%;
    margin-top: 4px;
    padding-top: 6px;
    border-top: 1px dashed currentColor;
    font-size: 12.5px;
    word-break: break-all;
    opacity: 0.9;
  }
}
</style>
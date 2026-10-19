<template>
  <div class="dashboard">
    <!-- ========== 标题区 ========== -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          电商智能客服 · 数据大屏
        </h1>
        <p class="page-subtitle">
          长期记忆 / RAG 召回 / Function Calling 全链路运行监控
        </p>
      </div>
      <div class="header-actions">
        <span class="update-time">更新于 {{ updateTime }}</span>
        <el-button size="default" :icon="Refresh" @click="loadData">
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- ========== 6 个统计卡片 ========== -->
    <div class="stat-grid">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="stat-card"
      >
        <div class="stat-icon" :style="{ background: stat.bg, color: stat.color }">
          <el-icon :size="22"><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- ========== 第一行图表 ========== -->
    <div class="chart-row row-2">
      <!-- 折线图 -->
      <div class="chart-card">
        <div class="chart-title">
          <span class="bar"></span>
          近 14 天对话与 Token 趋势
        </div>
        <v-chart :option="lineOption" autoresize class="chart" />
      </div>

      <!-- 饼图 -->
      <div class="chart-card">
        <div class="chart-title">
          <span class="bar"></span>
          意图识别分布
        </div>
        <v-chart :option="pieOption" autoresize class="chart" />
      </div>
    </div>

    <!-- ========== 第二行图表 ========== -->
    <div class="chart-row row-3">
      <!-- 柱状图 -->
      <div class="chart-card">
        <div class="chart-title">
          <span class="bar"></span>
          记忆增量（条/天）
        </div>
        <v-chart :option="barOption" autoresize class="chart" />
      </div>

      <!-- 工具调用 TOP5 -->
      <div class="chart-card">
        <div class="chart-title">
          <span class="bar"></span>
          工具调用 TOP5
        </div>
        <v-chart :option="hBarOption" autoresize class="chart" />
      </div>

      <!-- 仪表盘 -->
      <div class="chart-card">
        <div class="chart-title">
          <span class="bar"></span>
          工具调用成功率
        </div>
        <v-chart :option="gaugeOption" autoresize class="chart" />
      </div>
    </div>

    <!-- ========== 底部三栏 ========== -->
    <div class="chart-row row-3">
      <div class="chart-card">
        <div class="chart-title">
          <span class="bar"></span>
          最近入库记忆
        </div>
        <div class="list">
          <div v-for="item in recentKnowledge" :key="item.id" class="list-item">
            <div class="list-main">
              <div class="list-title">{{ item.question }}</div>
              <div class="list-desc">{{ item.answer }}</div>
            </div>
            <div class="list-time">{{ item.time }}</div>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-title">
          <span class="bar"></span>
          即将到来的日程
        </div>
        <div class="list">
          <div v-for="item in schedules" :key="item.id" class="list-item">
            <div class="list-main">
              <div class="list-title">{{ item.title }}</div>
              <div class="list-desc">{{ item.desc }}</div>
            </div>
            <div class="list-time">{{ item.time }}</div>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-title">
          <span class="bar"></span>
          模型与资源
        </div>
        <div class="resource-list">
          <div class="resource-item">
            <div class="resource-name">LLM 模型</div>
            <div class="resource-value">Qwen2.5-7B</div>
          </div>
          <div class="resource-item">
            <div class="resource-name">嵌入模型</div>
            <div class="resource-value">BGE-M3</div>
          </div>
          <div class="resource-item">
            <div class="resource-name">向量库</div>
            <div class="resource-value">Milvus</div>
          </div>
          <div class="resource-item">
            <div class="resource-name">知识条目</div>
            <div class="resource-value">{{ knowledgeCount }} 条</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart, GaugeChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import {
  Refresh, ChatDotRound, Document, Calendar,
  Tools, Bell,
} from '@element-plus/icons-vue'
import { analyticsService } from '@/services/analyticsService'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  GaugeChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

// ========== 状态 ==========
const updateTime = ref('')
const stats = ref<any[]>([])
const knowledgeCount = ref(0)

const recentKnowledge = ref([
  { id: 1, question: '怎么申请退款', answer: '在订单详情页点击申请退款...', time: '2分钟前' },
  { id: 2, question: '耳机续航多久', answer: '单次 4-8 小时，配合充电仓...', time: '10分钟前' },
  { id: 3, question: '电脑保修多久', answer: '整机保修 1-2 年...', time: '1小时前' },
])

const schedules = ref([
  { id: 1, title: '每日数据备份', desc: '自动执行数据库备份', time: '02:00' },
  { id: 2, title: '知识库更新', desc: '导入最新商品知识', time: '09:00' },
])

// ========== 折线图 ==========
const lineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: {
    data: ['提问', '回答', 'Token'],
    right: 10,
    top: 0,
    icon: 'circle',
  },
  grid: { left: 40, right: 50, top: 40, bottom: 30 },
  xAxis: {
    type: 'category',
    data: ['09-13', '09-14', '09-15', '09-16', '09-17', '09-18', '09-19',
           '09-20', '09-21', '09-22', '09-23', '09-24', '09-25', '09-26'],
    axisLine: { lineStyle: { color: '#e5e7eb' } },
    axisLabel: { color: '#64748b', fontSize: 11 },
  },
  yAxis: [
    {
      type: 'value',
      name: '条数',
      axisLabel: { color: '#64748b', fontSize: 11 },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
    },
    {
      type: 'value',
      name: 'Token',
      axisLabel: { color: '#64748b', fontSize: 11 },
      splitLine: { show: false },
    },
  ],
  series: [
    {
      name: '提问',
      type: 'line',
      smooth: true,
      data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
      lineStyle: { color: '#3b82f6', width: 2 },
      itemStyle: { color: '#3b82f6' },
      symbol: 'circle',
      symbolSize: 6,
    },
    {
      name: '回答',
      type: 'line',
      smooth: true,
      data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
      lineStyle: { color: '#8b5cf6', width: 2 },
      itemStyle: { color: '#8b5cf6' },
      symbol: 'circle',
      symbolSize: 6,
    },
    {
      name: 'Token',
      type: 'line',
      yAxisIndex: 1,
      smooth: true,
      data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18000],
      lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' },
      itemStyle: { color: '#f59e0b' },
      symbol: 'circle',
      symbolSize: 6,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(245, 158, 11, 0.2)' },
            { offset: 1, color: 'rgba(245, 158, 11, 0)' },
          ],
        },
      },
    },
  ],
}))

// ========== 饼图 ==========
const pieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: {
    bottom: 0,
    icon: 'circle',
    textStyle: { color: '#64748b', fontSize: 12 },
  },
  series: [
    {
      type: 'pie',
      radius: ['50%', '72%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      label: {
        show: true,
        formatter: '{b}\n{d}%',
        color: '#1e293b',
        fontSize: 11,
      },
      labelLine: { length: 8, length2: 10 },
      data: [
        { value: 75, name: '对话闲聊', itemStyle: { color: '#06b6d4' } },
        { value: 25, name: '检索+执行', itemStyle: { color: '#8b5cf6' } },
      ],
    },
  ],
}))

// ========== 柱状图 ==========
const barOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 20, bottom: 30 },
  xAxis: {
    type: 'category',
    data: ['09-13', '09-15', '09-17', '09-19', '09-21', '09-23', '09-25'],
    axisLabel: { color: '#64748b', fontSize: 11 },
    axisLine: { lineStyle: { color: '#e5e7eb' } },
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#64748b', fontSize: 11 },
    splitLine: { lineStyle: { color: '#f1f5f9' } },
  },
  series: [
    {
      type: 'bar',
      data: [0, 0, 0, 0, 0, 0, 2],
      barWidth: 14,
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#10b981' },
            { offset: 1, color: '#6ee7b7' },
          ],
        },
        borderRadius: [4, 4, 0, 0],
      },
    },
  ],
}))

// ========== 横向柱状图 ==========
const hBarOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 100, right: 30, top: 20, bottom: 30 },
  xAxis: {
    type: 'value',
    axisLabel: { color: '#64748b', fontSize: 11 },
    splitLine: { lineStyle: { color: '#f1f5f9' } },
  },
  yAxis: {
    type: 'category',
    data: ['vectorStoreSearch', '标签列表', '语义检索', '任务编排', '意图识别'],
    axisLabel: { color: '#1e293b', fontSize: 12 },
    axisLine: { show: false },
    axisTick: { show: false },
  },
  series: [
    {
      type: 'bar',
      data: [1, 2, 3, 5, 12],
      barWidth: 12,
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [
            { offset: 0, color: '#06b6d4' },
            { offset: 1, color: '#8b5cf6' },
          ],
        },
        borderRadius: [0, 6, 6, 0],
      },
      label: {
        show: true,
        position: 'right',
        color: '#64748b',
        fontSize: 11,
      },
    },
  ],
}))

// ========== 仪表盘 ==========
const gaugeOption = computed(() => ({
  series: [
    {
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      min: 0,
      max: 100,
      radius: '95%',
      center: ['50%', '60%'],
      progress: {
        show: true,
        width: 16,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: '#10b981' },
              { offset: 1, color: '#34d399' },
            ],
          },
        },
      },
      axisLine: {
        lineStyle: { width: 16, color: [[1, '#f1f5f9']] },
      },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: {
        distance: -28,
        color: '#94a3b8',
        fontSize: 10,
        formatter: (v: number) => (v % 20 === 0 ? String(v) : ''),
      },
      pointer: { show: false },
      anchor: { show: false },
      detail: {
        valueAnimation: true,
        fontSize: 26,
        fontWeight: 700,
        color: '#1e293b',
        offsetCenter: [0, 0],
        formatter: '{value}%',
      },
      data: [{ value: 78.3 }],
    },
  ],
}))

// ========== 加载数据 ==========
async function loadData() {
  updateTime.value = new Date().toLocaleString('zh-CN')
  try {
    const overview = await analyticsService.overview()
    stats.value = [
      {
        label: '长期记忆', value: overview.session_count || 0,
        icon: Document, bg: '#dbeafe', color: '#3b82f6',
      },
      {
        label: '知识条目', value: 695,
        icon: Document, bg: '#e0e7ff', color: '#6366f1',
      },
      {
        label: '会话总数', value: overview.session_count || 0,
        icon: Calendar, bg: '#fef3c7', color: '#f59e0b',
      },
      {
        label: '消息总数', value: overview.message_count || 0,
        icon: ChatDotRound, bg: '#d1fae5', color: '#10b981',
      },
      {
        label: '工具调用', value: 23,
        icon: Tools, bg: '#fee2e2', color: '#ef4444',
      },
      {
        label: '今日对话', value: 8,
        icon: Bell, bg: '#dbeafe', color: '#3b82f6',
      },
    ]
    knowledgeCount.value = 695
  } catch (e) {
    console.warn('加载统计数据失败', e)
    // 使用默认值
    stats.value = [
      { label: '长期记忆', value: 2, icon: Document, bg: '#dbeafe', color: '#3b82f6' },
      { label: '知识条目', value: 695, icon: Document, bg: '#e0e7ff', color: '#6366f1' },
      { label: '会话总数', value: 11, icon: Calendar, bg: '#fef3c7', color: '#f59e0b' },
      { label: '消息总数', value: 11, icon: ChatDotRound, bg: '#d1fae5', color: '#10b981' },
      { label: '工具调用', value: 23, icon: Tools, bg: '#fee2e2', color: '#ef4444' },
      { label: '今日对话', value: 8, icon: Bell, bg: '#dbeafe', color: '#3b82f6' },
    ]
  }
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.dashboard {
  padding: 4px 0;
}

// ========== 标题区 ==========
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 20px;

  .page-title {
    font-size: 22px;
    font-weight: 700;
    margin: 0 0 6px;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .page-subtitle {
    font-size: 13px;
    color: #94a3b8;
    margin: 0;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;

    .update-time {
      font-size: 12.5px;
      color: #94a3b8;
    }
  }
}

// ========== 统计卡片网格 ==========
.stat-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 16px;

  @media (max-width: 1400px) {
    grid-template-columns: repeat(3, 1fr);
  }
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: all 0.25s ease;
  border: 1px solid #f1f5f9;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  }

  .stat-icon {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .stat-body {
    flex: 1;
    min-width: 0;

    .stat-value {
      font-size: 22px;
      font-weight: 700;
      color: #1e293b;
      line-height: 1.2;
    }

    .stat-label {
      font-size: 12.5px;
      color: #94a3b8;
      margin-top: 2px;
    }
  }
}

// ========== 图表网格 ==========
.chart-row {
  display: grid;
  gap: 16px;
  margin-bottom: 16px;

  &.row-2 {
    grid-template-columns: 2fr 1fr;

    @media (max-width: 1200px) {
      grid-template-columns: 1fr;
    }
  }

  &.row-3 {
    grid-template-columns: repeat(3, 1fr);

    @media (max-width: 1200px) {
      grid-template-columns: 1fr;
    }
  }
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px 18px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;

  .chart-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 12px;

    .bar {
      width: 3px;
      height: 14px;
      background: linear-gradient(180deg, #3b82f6 0%, #8b5cf6 100%);
      border-radius: 2px;
    }
  }

  .chart {
    height: 220px;
    width: 100%;
  }
}

// ========== 列表样式 ==========
.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;

  .list-item {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px dashed #f1f5f9;

    &:last-child { border-bottom: none; }

    .list-main {
      flex: 1;
      min-width: 0;

      .list-title {
        font-size: 13px;
        color: #1e293b;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .list-desc {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }

    .list-time {
      font-size: 12px;
      color: #94a3b8;
      flex-shrink: 0;
    }
  }
}

// ========== 资源列表 ==========
.resource-list {
  display: flex;
  flex-direction: column;
  gap: 12px;

  .resource-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px dashed #f1f5f9;

    &:last-child { border-bottom: none; }

    .resource-name {
      font-size: 13px;
      color: #64748b;
    }

    .resource-value {
      font-size: 13px;
      color: #1e293b;
      font-weight: 600;
    }
  }
}
</style>
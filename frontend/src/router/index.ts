import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' },
  },
  // ===== 独立页面：智能对话（无后台布局）=====
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/ChatPage.vue'),
    meta: { title: '智能对话', requiresAuth: true },
  },
  // ===== 后台布局 =====
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '数据大屏' },
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('@/views/KnowledgeBase.vue'),
        meta: { title: '记忆库' },
      },
      {
        path: 'models',
        name: 'ModelConfig',
        component: () => import('@/views/ModelConfig.vue'),
        meta: { title: '模型配置' },
      },
      {
        path: 'agent-config',
        name: 'AgentConfig',
        component: () => import('@/views/ModelConfig.vue'),
        meta: { title: 'Agent 参数' },
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/views/RunLogs.vue'),
        meta: { title: '运行日志' },
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/SessionHistory.vue'),
        meta: { title: '会话历史' },
      },
      {
        path: 'monitor',
        name: 'Monitor',
        component: () => import('@/views/SystemMonitor.vue'),
        meta: { title: '系统监控' },
      },
      {
        path: 'monitor-agent',
        name: 'MonitorAgent',
        component: () => import('@/views/RunMonitor.vue'),
        meta: { title: '运行监控' },
      },
      {
        path: 'tools',
        name: 'Tools',
        component: () => import('@/views/SystemTools.vue'),
        meta: { title: '系统工具' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '首页'} - 电商智能客服`
})

export default router

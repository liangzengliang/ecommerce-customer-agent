<template>
  <div class="main-layout">
    <!-- ========== 左侧边栏 ========== -->
    <aside class="sidebar" :class="{ collapsed }">
      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="logo-icon">
          <el-icon :size="20"><Service /></el-icon>
        </div>
        <span v-show="!collapsed" class="logo-text">电商智能客服</span>
      </div>

      <!-- 菜单 -->
      <nav class="sidebar-menu">
        <template v-for="menu in menus" :key="menu.title">
          <!-- 有子菜单 -->
          <div v-if="menu.children" class="menu-group">
            <div class="menu-group-header" @click="toggleGroup(menu.title)">
              <el-icon :size="18"><component :is="menu.icon" /></el-icon>
              <span v-show="!collapsed">{{ menu.title }}</span>
              <el-icon
                v-show="!collapsed"
                class="arrow"
                :class="{ open: openGroups.includes(menu.title) }"
              >
                <ArrowRight />
              </el-icon>
            </div>
            <div
              v-show="openGroups.includes(menu.title) && !collapsed"
              class="submenu"
            >
              <div
                v-for="sub in menu.children"
                :key="sub.path"
                class="menu-item sub-item"
                :class="{ active: isActive(sub.path!) }"
                @click="router.push(sub.path!)"
              >
                <el-icon :size="16"><component :is="sub.icon" /></el-icon>
                <span>{{ sub.title }}</span>
              </div>
            </div>
          </div>

          <!-- 无子菜单 -->
          <div
            v-else
            class="menu-item"
            :class="{ active: isActive(menu.path!) }"
            @click="router.push(menu.path!)"
          >
            <el-icon :size="18"><component :is="menu.icon" /></el-icon>
            <span v-show="!collapsed">{{ menu.title }}</span>
          </div>
        </template>
      </nav>

      <!-- 底部折叠按钮 -->
      <div class="sidebar-footer">
        <div class="menu-item" @click="collapsed = !collapsed">
          <el-icon :size="18">
            <Fold v-if="!collapsed" />
            <Expand v-else />
          </el-icon>
          <span v-show="!collapsed">收起菜单</span>
        </div>
      </div>
    </aside>

    <!-- ========== 右侧主体 ========== -->
    <div class="main-container">
      <!-- 顶部栏 -->
      <header class="topbar">
        <div class="left">
          <el-icon class="collapse-icon" :size="20" @click="collapsed = !collapsed">
            <Fold v-if="!collapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="right">
          <el-icon class="top-icon"><Search /></el-icon>
          <el-icon class="top-icon"><Bell /></el-icon>
          <el-icon class="top-icon"><FullScreen /></el-icon>
          <el-icon class="top-icon"><Moon /></el-icon>

          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <div class="avatar">{{ username.charAt(0).toUpperCase() }}</div>
              <span class="name">{{ username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="chat">进入对话</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 标签页栏 -->
      <div class="tabs-bar">
        <div class="tab active">
          <span class="tab-dot"></span>
          <span>{{ currentTitle }}</span>
        </div>
        <div class="tabs-actions" @click="router.go(0)">
          <el-icon><RefreshRight /></el-icon>
        </div>
      </div>

      <!-- 主内容 -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Service, Fold, Expand, Search, Bell, FullScreen, Moon,
  ArrowDown, ArrowRight, RefreshRight,
  HomeFilled, Document, ChatDotRound, ChatLineRound,
  Setting, Monitor, Tools, Collection, Cpu,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const collapsed = ref(false)
const openGroups = ref<string[]>(['记忆 Agent'])
const username = computed(() => userStore.username || 'Admin')

// ============ 菜单配置 ============
interface MenuItem {
  title: string
  icon: any
  path?: string
  children?: MenuItem[]
}

const menus: MenuItem[] = [
  { title: '首页', path: '/dashboard', icon: HomeFilled },
  {
    title: '系统管理',
    icon: Setting,
    children: [
      { title: '系统监控', path: '/monitor', icon: Monitor },
      { title: '系统工具', path: '/tools', icon: Tools },
    ],
  },
  {
    title: '记忆 Agent',
    icon: ChatDotRound,
    children: [
      { title: '智能对话', path: '/chat', icon: ChatLineRound },
      { title: '记忆库', path: '/knowledge', icon: Collection },
      { title: '模型配置', path: '/models', icon: Cpu },
      { title: 'Agent 参数', path: '/agent-config', icon: Setting },
      { title: '运行日志', path: '/logs', icon: Document },
      { title: '运行监控', path: '/monitor-agent', icon: Monitor },
    ],
  },
]

const currentTitle = computed(() => {
  for (const m of menus) {
    if (m.path === route.path) return m.title
    if (m.children) {
      const sub = m.children.find((s) => s.path === route.path)
      if (sub) return sub.title
    }
  }
  return '数据大屏'
})

function isActive(path: string) {
  return route.path === path
}

function toggleGroup(title: string) {
  const i = openGroups.value.indexOf(title)
  if (i >= 0) openGroups.value.splice(i, 1)
  else openGroups.value.push(title)
}

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (cmd === 'chat') {
    router.push('/chat')
  }
}
</script>

<style scoped lang="scss">
.main-layout {
  display: flex;
  height: 100vh;
  background: #f0f2f5;
}

// ========== 左侧边栏 ==========
.sidebar {
  width: 220px;
  background: #1e293b;
  color: #cbd5e1;
  display: flex;
  flex-direction: column;
  transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;

  &.collapsed {
    width: 64px;

    .sidebar-logo {
      justify-content: center;
      padding: 0;
    }

    .menu-item,
    .menu-group-header {
      justify-content: center;
      padding: 12px 0;
    }
  }

  .sidebar-logo {
    height: 60px;
    padding: 0 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);

    .logo-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      flex-shrink: 0;
    }

    .logo-text {
      font-size: 15px;
      font-weight: 600;
      color: #fff;
      white-space: nowrap;
    }
  }

  .sidebar-menu {
    flex: 1;
    padding: 12px 10px;
    overflow-y: auto;
  }

  .menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 14px;
    margin-bottom: 4px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    color: #cbd5e1;
    transition: all 0.2s ease;
    white-space: nowrap;

    &:hover {
      background: rgba(255, 255, 255, 0.06);
      color: #fff;
    }

    &.active {
      background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
      color: #fff;
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
  }

  .menu-group-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 14px;
    margin-bottom: 4px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    color: #cbd5e1;
    transition: all 0.2s ease;
    white-space: nowrap;

    &:hover {
      background: rgba(255, 255, 255, 0.06);
      color: #fff;
    }

    .arrow {
      margin-left: auto;
      transition: transform 0.2s ease;

      &.open {
        transform: rotate(90deg);
      }
    }
  }

  .submenu {
    padding-left: 8px;

    .sub-item {
      padding-left: 22px;
      font-size: 13.5px;
    }
  }

  .sidebar-footer {
    padding: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }
}

// ========== 右侧主体 ==========
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

// ---------- 顶部栏 ----------
.topbar {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;

  .left {
    display: flex;
    align-items: center;
    gap: 16px;

    .collapse-icon {
      cursor: pointer;
      color: #64748b;
      padding: 4px;
      border-radius: 6px;

      &:hover {
        background: #f1f5f9;
      }
    }
  }

  .right {
    display: flex;
    align-items: center;
    gap: 4px;

    .top-icon {
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #64748b;
      cursor: pointer;
      border-radius: 8px;
      transition: all 0.2s ease;

      &:hover {
        background: #f1f5f9;
        color: #3b82f6;
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 8px;
      border-radius: 8px;
      cursor: pointer;
      margin-left: 8px;
      transition: background 0.2s;

      &:hover {
        background: #f1f5f9;
      }

      .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 600;
      }

      .name {
        font-size: 14px;
        color: #1e293b;
        font-weight: 500;
      }
    }
  }
}

// ---------- 标签页栏 ----------
.tabs-bar {
  height: 40px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;

  .tab {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 16px;
    height: 28px;
    border-radius: 6px;
    background: #eff6ff;
    color: #1e40af;
    font-size: 13px;
    font-weight: 500;

    .tab-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #3b82f6;
    }
  }

  .tabs-actions {
    color: #64748b;
    cursor: pointer;
    padding: 6px;
    border-radius: 6px;

    &:hover {
      background: #f1f5f9;
    }
  }
}

// ---------- 主内容区 ----------
.content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
</style>

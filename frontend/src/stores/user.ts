/**
 * 用户状态
 * 管理登录信息、token、用户资料
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  // ===== 状态 =====
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const userId = ref<number | null>(null)
  const username = ref<string>('')

  // ===== 计算属性 =====
  const isLoggedIn = computed(() => !!token.value)

  // ===== 方法 =====

  /** 登录 */
  async function login(user: string, password: string) {
    const res = await loginApi({ username: user, password })
    token.value = res.access_token
    userId.value = res.user_id
    username.value = res.username
    localStorage.setItem('access_token', res.access_token)
    localStorage.setItem('user_id', String(res.user_id))
    localStorage.setItem('username', res.username)
  }

  /** 注册 */
  async function register(user: string, password: string) {
    const res = await registerApi({ username: user, password })
    token.value = res.access_token
    userId.value = res.user_id
    username.value = res.username
    localStorage.setItem('access_token', res.access_token)
  }

  /** 登出 */
  function logout() {
    token.value = ''
    userId.value = null
    username.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
  }

  return { token, userId, username, isLoggedIn, login, register, logout }
})
/**
 * Axios 实例封装
 * 统一处理 baseURL、请求拦截（带 token）、响应拦截（401 跳登录）
 */
import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// 创建 Axios 实例
const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器：自动带上 JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error) => {
    const status = error.response?.status
    if (status === 401) {
      // 未登录或 token 失效
      localStorage.removeItem('access_token')
      ElMessage.error('登录已过期，请重新登录')
      window.location.href = '/login'
    } else if (status === 429) {
      ElMessage.warning('请求过于频繁，请稍后再试')
    } else {
      const msg = error.response?.data?.detail || error.message || '请求失败'
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  },
)

export default api
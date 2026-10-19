<template>
  <div class="login-page">
    <!-- 背景几何纹理 -->
    <div class="bg-pattern"></div>

    <!-- 居中卡片 -->
    <div class="login-card fade-in">
      <!-- 左侧品牌区 -->
      <div class="brand-panel">
        <div class="brand-logo">
          <el-icon :size="28"><Service /></el-icon>
        </div>

        <h1>电商智能客服</h1>
        <p class="slogan">基于 LLM + RAG 的智能客服 Agent</p>

        <ul class="features">
          <li>
            <el-icon><ChatDotRound /></el-icon>
            <div>
              <div class="feature-title">智能问答</div>
              <div class="feature-desc">基于知识库的精准回答</div>
            </div>
          </li>
          <li>
            <el-icon><Cpu /></el-icon>
            <div>
              <div class="feature-title">多工具调用</div>
              <div class="feature-desc">订单、物流、退款一站式处理</div>
            </div>
          </li>
          <li>
            <el-icon><DataAnalysis /></el-icon>
            <div>
              <div class="feature-title">数据分析</div>
              <div class="feature-desc">会话、意图、情感全维度统计</div>
            </div>
          </li>
        </ul>

        <div class="brand-footer">FastAPI · Vue3 · LangGraph · RAG</div>
      </div>

      <!-- 右侧表单区 -->
      <div class="form-panel">
        <h2>欢迎回来</h2>
        <p class="subtitle">登录后即可开始您的智能客服体验</p>

        <el-form :model="form" @submit.prevent>
          <!-- 用户名 -->
          <el-form-item>
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>

          <!-- 密码 -->
          <el-form-item>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <!-- 验证码 -->
          <el-form-item>
            <div class="captcha-row">
              <el-input
                v-model="form.captcha"
                placeholder="请输入验证码"
                size="large"
                :prefix-icon="Key"
                @keyup.enter="handleLogin"
              />
              <div class="captcha-img" @click="refreshCaptcha">
                {{ captchaText }}
              </div>
            </div>
          </el-form-item>

          <!-- 记住密码 -->
          <el-form-item>
            <el-checkbox v-model="form.remember">记住密码</el-checkbox>
          </el-form-item>

          <!-- 登录按钮 -->
          <el-button
            type="primary"
            size="large"
            class="submit-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>

          <!-- 注册 -->
          <div class="switch">
            还没有账号？
            <a @click="handleRegister">立即注册</a>
          </div>
        </el-form>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="page-footer">
      Copyright © 2026 电商智能客服 · All Rights Reserved
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User, Lock, Key,
  Service, ChatDotRound, Cpu, DataAnalysis,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const form = ref({
  username: '',
  password: '',
  captcha: '',
  remember: false,
})

const loading = ref(false)
const captchaText = ref('')

/** 生成 4 位随机验证码 */
function generateCaptcha(): string {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let result = ''
  for (let i = 0; i < 4; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

/** 刷新验证码 */
function refreshCaptcha() {
  captchaText.value = generateCaptcha()
  form.value.captcha = ''
}

/** 校验验证码 */
function validateCaptcha(): boolean {
  if (!form.value.captcha) {
    ElMessage.warning('请输入验证码')
    return false
  }
  if (form.value.captcha.toUpperCase() !== captchaText.value) {
    ElMessage.error('验证码错误')
    refreshCaptcha()
    return false
  }
  return true
}

/** 登录 */
async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  if (!validateCaptcha()) return

  loading.value = true
  try {
    await userStore.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    router.push((route.query.redirect as string) || '/dashboard')
  } catch (e) {
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

/** 注册 */
async function handleRegister() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  if (!validateCaptcha()) return

  loading.value = true
  try {
    await userStore.register(form.value.username, form.value.password)
    ElMessage.success('注册成功')
    router.push('/dashboard')
  } catch (e) {
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshCaptcha()
  // 从 localStorage 读取记住的用户名
  const remembered = localStorage.getItem('remembered_username')
  if (remembered) {
    form.value.username = remembered
    form.value.remember = true
  }
})
</script>

<style scoped lang="scss">
// ============ 整体页面 ============
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 40%, #d1fae5 100%);
  overflow: hidden;
}

// 背景几何纹理（纯 CSS 模拟）
.bg-pattern {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.15) 0%, transparent 40%),
    radial-gradient(circle at 80% 70%, rgba(16, 185, 129, 0.12) 0%, transparent 40%),
    radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
  pointer-events: none;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(102, 126, 234, 0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(102, 126, 234, 0.04) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(ellipse at center, black 30%, transparent 80%);
    -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 80%);
  }
}

// ============ 居中卡片 ============
.login-card {
  position: relative;
  display: flex;
  width: 880px;
  max-width: 92vw;
  min-height: 520px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow:
    0 20px 60px rgba(102, 126, 234, 0.18),
    0 4px 16px rgba(0, 0, 0, 0.06);
  z-index: 1;
}

// ============ 左侧品牌区 ============
.brand-panel {
  width: 400px;
  padding: 48px 40px;
  background: linear-gradient(135deg, #bfdbfe 0%, #c7d2fe 50%, #a5b4fc 100%);
  display: flex;
  flex-direction: column;
  color: #1e293b;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.4) 0%, transparent 60%);
    pointer-events: none;
  }

  > * {
    position: relative;
    z-index: 1;
  }

  .brand-logo {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 28px;
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
  }

  h1 {
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 10px;
    color: #1e3a8a;
    letter-spacing: 0.5px;
  }

  .slogan {
    font-size: 13.5px;
    color: #475569;
    margin: 0 0 36px;
    line-height: 1.6;
  }

  .features {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 20px;

    li {
      display: flex;
      gap: 14px;
      align-items: flex-start;

      .el-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.6);
        color: #3b82f6;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 16px;
      }

      .feature-title {
        font-size: 14px;
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 2px;
      }

      .feature-desc {
        font-size: 12.5px;
        color: #64748b;
        line-height: 1.5;
      }
    }
  }

  .brand-footer {
    margin-top: auto;
    padding-top: 32px;
    font-size: 12px;
    color: #64748b;
    letter-spacing: 0.5px;
  }
}

// ============ 右侧表单区 ============
.form-panel {
  flex: 1;
  padding: 48px 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #fff;

  h2 {
    font-size: 24px;
    font-weight: 600;
    margin: 0 0 8px;
    color: #1e293b;
  }

  .subtitle {
    font-size: 13.5px;
    color: #94a3b8;
    margin: 0 0 32px;
  }

  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  :deep(.el-input__wrapper) {
    border-radius: 8px;
    box-shadow: 0 0 0 1px #e2e8f0 inset;
    transition: all 0.2s ease;
    padding: 4px 12px;

    &:hover {
      box-shadow: 0 0 0 1px #cbd5e1 inset;
    }

    &.is-focus {
      box-shadow: 0 0 0 1px #3b82f6 inset, 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
  }

  :deep(.el-input__inner) {
    height: 36px;
    font-size: 14px;
  }

  // 验证码行
  .captcha-row {
    display: flex;
    gap: 12px;
    width: 100%;

    .el-input {
      flex: 1;
    }

    .captcha-img {
      width: 100px;
      height: 44px;
      border-radius: 8px;
      background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
      color: #1e40af;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      user-select: none;
      font-family: 'Georgia', serif;
      font-style: italic;
      border: 1px solid #dbeafe;
      transition: all 0.2s ease;
      flex-shrink: 0;

      &:hover {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
      }
    }
  }

  :deep(.el-checkbox__label) {
    font-size: 13px;
    color: #64748b;
  }

  .submit-btn {
    width: 100%;
    height: 44px;
    border-radius: 8px;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 4px;
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
    border: none;
    margin-top: 4px;
    transition: all 0.25s ease;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
    }

    &:active {
      transform: translateY(0);
    }
  }

  .switch {
    text-align: center;
    margin-top: 20px;
    font-size: 13px;
    color: #94a3b8;

    a {
      color: #3b82f6;
      cursor: pointer;
      font-weight: 500;
      margin-left: 4px;

      &:hover {
        text-decoration: underline;
      }
    }
  }
}

// ============ 页脚 ============
.page-footer {
  position: absolute;
  bottom: 24px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 12.5px;
  color: #64748b;
  z-index: 1;
}

// ============ 响应式 ============
@media (max-width: 768px) {
  .login-card {
    flex-direction: column;
    width: 92vw;
    min-height: auto;
  }

  .brand-panel {
    width: 100%;
    padding: 32px 28px;

    h1 { font-size: 22px; }
    .slogan { margin-bottom: 20px; }
    .features { gap: 12px; }
    .features li .feature-desc { display: none; }
    .brand-footer { display: none; }
  }

  .form-panel {
    padding: 32px 28px;
  }
}
</style>
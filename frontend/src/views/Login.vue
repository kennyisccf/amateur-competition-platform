<template>
  <div class="login-container">
    <!-- 左侧品牌区域 -->
    <div class="login-left">
      <h1 class="login-title">乐赛</h1>
      <p class="login-desc">一站式赛事服务平台 · 精彩有你</p>
      <div class="tag-group">
        <el-tag>多元赛事</el-tag>
        <el-tag>全民参与</el-tag>
        <el-tag>智能成长</el-tag>
      </div>
    </div>

    <!-- 右侧登录卡片 -->
    <div class="login-card">
      <h2 class="card-title">欢迎登录</h2>
      <p class="card-sub">请选择您的系统角色并输入凭证</p>

      <!-- 角色切换标签 -->
      <el-radio-group v-model="userRole" class="role-tabs">
        <el-radio-button label="选手" />
        <el-radio-button label="主办方" />
        <el-radio-button label="管理员" />
      </el-radio-group>

      <!-- 原生 form，完全匹配后端接口 -->
      <form method="post" action="/login" class="login-form" @submit="beforeSubmit">
        <!-- 手动添加 CSRF token 隐藏字段（从 Cookie 读取） -->
        <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken" />

        <el-form-item>
          <el-input
            type="text"
            name="username"
            v-model="loginForm.username"
            placeholder="请输入用户名"
            required
          />
        </el-form-item>

        <el-form-item>
          <el-input
            type="password"
            name="password"
            v-model="loginForm.password"
            placeholder="请输入密码"
            required
          />
        </el-form-item>

        <!-- 验证码行（前端模拟） -->
        <div class="code-row">
          <el-input v-model="loginForm.code" placeholder="图形验证码" />
          <div class="code-box" @click="getCaptcha">{{ captcha }}</div>
        </div>

        <el-form-item>
          <el-button type="primary" class="login-btn" native-type="submit">登录</el-button>
        </el-form-item>
      </form>

      <!-- 后端错误信息：从 window.__ERROR_MSG__ 读取 -->
      <div class="error-tip" v-if="backendError">{{ backendError }}</div>

      <!-- 底部链接 -->
      <div class="login-footer">
        <a href="#">忘记密码？</a>
        <span>还没有账户？</span>
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const userRole = ref('选手')
const loginForm = ref({
  username: '',
  password: '',
  code: ''
})
const captcha = ref('')
const backendError = ref('')
const csrfToken = ref('')

// 生成验证码
const getCaptcha = () => {
  const str = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  let res = ''
  for (let i = 0; i < 4; i++) {
    res += str[Math.floor(Math.random() * 36)]
  }
  captcha.value = res
}

// 获取 CSRF Token（从 Cookie 中读取）
const getCookie = (name) => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return ''
}

// 表单提交前校验
const beforeSubmit = (e) => {
  const uname = loginForm.value.username.trim()
  const pwd = loginForm.value.password.trim()
  const code = loginForm.value.code.trim()

  if (!uname || !pwd) {
    ElMessage.warning('请输入账号密码')
    e.preventDefault()
    return
  }
  if (code.toUpperCase() !== captcha.value) {
    ElMessage.error('验证码错误')
    getCaptcha()
    e.preventDefault()
    return
  }
  // 校验通过，表单自然提交（POST /login），页面会刷新
}

onMounted(() => {
  getCaptcha()
  csrfToken.value = getCookie('csrftoken')   // 根据后端实际 Cookie 名称调整
  // 从后端注入的全局变量中读取错误信息
  if (window.__ERROR_MSG__) {
    backendError.value = window.__ERROR_MSG__
  }
})
</script>

<style scoped>
/* 你的原有样式，完全不变 */
.login-container {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #1a3a4a, #244757);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 120px;
}

.login-left {
  color: #fff;
}
.login-title {
  font-size: 46px;
  font-weight: 600;
  margin-bottom: 16px;
}
.login-desc {
  font-size: 18px;
  opacity: 0.8;
  margin-bottom: 30px;
}
.tag-group {
  display: flex;
  gap: 12px;
}

.login-card {
  width: 420px;
  padding: 40px 30px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  margin-right: 300px;
}
.card-title {
  font-size: 24px;
  margin: 0 0 8px;
}
.card-sub {
  color: #666;
  font-size: 14px;
  margin-bottom: 24px;
}

.role-tabs {
  margin-bottom: 20px;
  width: 100%;
}
.login-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.code-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}
.code-row .el-input {
  flex: 1;
}
.code-box {
  width: 120px;
  height: 40px;
  background: #f0f2f5;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 4px;
  user-select: none;
  cursor: pointer;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.error-tip {
  color: #ff4d4f;
  text-align: center;
  margin-top: 8px;
}

.login-footer {
  text-align: center;
  font-size: 13px;
  color: #666;
  margin-top: 16px;
}
.login-footer a {
  color: #4080ff;
  text-decoration: none;
}
</style>
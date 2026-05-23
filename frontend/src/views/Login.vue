<template>
  <div class="login-container">
    <div class="login-left">
      <h1>乐赛</h1>
      <p>一站式服务平台 · 精彩有你</p>
      <div class="tags">
        <span>多元赛事</span>
        <span>全民参与</span>
        <span>智能成长</span>
      </div>
    </div>
    <div class="login-form-card">
      <h2>欢迎登录</h2>
      <p>请选择您的系统角色并输入凭证</p>
      
      <!-- 角色选择 -->
      <div class="role-tabs">
        <button 
          v-for="role in roleList" 
          :key="role.value"
          :class="{ active: selectedRole === role.value }"
          @click="selectedRole = role.value"
        >
          {{ role.label }}
        </button>
      </div>

      <form @submit.prevent="handleLogin">
        <el-input
          v-model="form.username"
          placeholder="请输入用户名"
          clearable
          style="margin-bottom: 16px"
        />
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          clearable
          style="margin-bottom: 16px"
        />
        <div class="captcha-row">
          <el-input
            v-model="form.captcha"
            placeholder="图形验证码"
            style="flex: 1; margin-right: 12px"
          />
          <div class="captcha-code">8A3F</div>
        </div>

        <el-button type="primary" style="width: 100%; margin-top: 24px" native-type="submit">
          立即登录
        </el-button>

        <div class="form-footer">
          <a href="#">忘记密码?</a>
          <span>还没有账户? <router-link to="/register">立即注册</router-link></span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 角色列表，对应接口要求的中文role
const roleList = [
  { label: '参赛选手', value: '选手' },
  { label: '赛事主办方', value: '主办方' },
  { label: '平台管理员', value: '管理员' }
]
const selectedRole = ref('选手')

const form = ref({
  username: '',
  password: '',
  captcha: ''
})

// 登录处理
const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  try {
    // 1. 获取CSRF Token
    const csrfRes = await axios.get('http://localhost:8000/csrf/')
    const csrfToken = csrfRes.data.csrfToken

    // 2. 调用登录接口
    const res = await axios.post(
      'http://localhost:8000/api/login/',
      {
        username: form.value.username,
        password: form.value.password,
        role: selectedRole.value
      },
      {
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json'
        }
      }
    )

    if (res.data.success) {
      ElMessage.success('登录成功')
      // 保存用户ID，后续报名接口需要
      localStorage.setItem('user_id', res.data.user_id)
      router.push('/home')
    } else {
      ElMessage.error(res.data.msg || '登录失败')
    }
  } catch (err) {
    ElMessage.error('请求失败，请检查后端服务是否启动')
    console.error(err)
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  align-items: center;
  justify-content: space-around;
  padding: 0 10%;
}
.login-left {
  color: white;
}
.login-left h1 {
  font-size: 48px;
  margin: 0 0 12px;
}
.login-left p {
  font-size: 20px;
  opacity: 0.9;
  margin: 0 0 24px;
}
.tags {
  display: flex;
  gap: 12px;
}
.tags span {
  padding: 6px 16px;
  background: rgba(255,255,255,0.15);
  border-radius: 20px;
  font-size: 14px;
}
.login-form-card {
  background: white;
  padding: 32px;
  border-radius: 12px;
  width: 360px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}
.login-form-card h2 {
  margin: 0 0 8px;
  font-size: 24px;
}
.login-form-card p {
  color: #666;
  margin: 0 0 24px;
  font-size: 14px;
}
.role-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}
.role-tabs button {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  background: #f0f2f5;
  cursor: pointer;
  transition: all 0.3s;
}
.role-tabs button.active {
  background: #1677ff;
  color: white;
}
.captcha-row {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}
.captcha-code {
  padding: 10px 16px;
  background: #e5e7eb;
  border-radius: 6px;
  font-weight: bold;
  letter-spacing: 2px;
}
.form-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  font-size: 13px;
}
.form-footer a, .form-footer span a {
  color: #1677ff;
  text-decoration: none;
}
</style>
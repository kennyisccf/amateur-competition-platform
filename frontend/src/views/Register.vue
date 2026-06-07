<template>
  <div class="register-container">
    <div class="register-left">
      <h1>乐赛</h1>
      <p>一站式服务平台 · 精彩有你</p>
      <div class="tags">
        <span>多元赛事</span>
        <span>全民参与</span>
        <span>智能成长</span>
      </div>
    </div>
    <div class="register-form-card">
      <h2>欢迎注册</h2>
      <p>创建您的账户，开启赛事之旅</p>
      
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

      <form @submit.prevent="handleRegister">
        <el-input
          v-model="form.username"
          placeholder="请输入用户名"
          clearable
          style="margin-bottom: 16px"
        />
        <el-input
          v-model="form.nickname"
          placeholder="请输入昵称（选填，默认同用户名）"
          clearable
          style="margin-bottom: 16px"
        />
        <el-input
          v-model="form.email"
          placeholder="请输入邮箱（选填）"
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
        <el-input
          v-model="form.password2"
          type="password"
          placeholder="请确认密码"
          clearable
          style="margin-bottom: 16px"
        />

        <el-button type="primary" style="width: 100%; margin-top: 24px" native-type="submit">
          立即注册
        </el-button>

        <div class="form-footer">
          <span>已有账户? <router-link to="/login">立即登录</router-link></span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()

// 角色列表，对应接口要求的英文role
const roleList = [
  { label: '参赛选手', value: 'PLAYER' },
  { label: '赛事主办方', value: 'ORGANIZER' },
  { label: '平台管理员', value: 'ADMIN' }
]
const selectedRole = ref('PLAYER')

const form = ref({
  username: '',
  nickname: '',
  email: '',
  password: '',
  password2: ''
})

// 注册处理
const handleRegister = async () => {
  if (!form.value.username || !form.value.password || !form.value.password2) {
    ElMessage.warning('请填写必填项')
    return
  }
  if (form.value.password !== form.value.password2) {
    ElMessage.warning('两次密码输入不一致')
    return
  }

  try {
    // 1. 获取CSRF Token
    const csrfRes = await request.get('/csrf/')
    const csrfToken = csrfRes.data.csrfToken

    // 2. 构造FormData（接口要求form-data格式，不支持JSON）
    const formData = new FormData()
    formData.append('username', form.value.username)
    formData.append('password', form.value.password)
    formData.append('password2', form.value.password2)
    formData.append('role', selectedRole.value)
    if (form.value.nickname) formData.append('nickname', form.value.nickname)
    if (form.value.email) formData.append('email', form.value.email)

    // 3. 调用注册接口
    const res = await request.post(
      '/api/register/',
      formData,
      {
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    if (res.data.success) {
      ElMessage.success('注册成功，即将跳转到登录页')
      router.push('/login')
    } else {
      ElMessage.error(res.data.msg || '注册失败')
    }
  } catch (err) {
    ElMessage.error('请求失败，请检查后端服务是否启动')
    console.error(err)
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  align-items: center;
  justify-content: space-around;
  padding: 0 10%;
}
.register-left {
  color: white;
}
.register-left h1 {
  font-size: 48px;
  margin: 0 0 12px;
}
.register-left p {
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
.register-form-card {
  background: white;
  padding: 32px;
  border-radius: 12px;
  width: 360px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}
.register-form-card h2 {
  margin: 0 0 8px;
  font-size: 24px;
}
.register-form-card p {
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
.form-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  font-size: 13px;
}
.form-footer span a {
  color: #1677ff;
  text-decoration: none;
}
</style>

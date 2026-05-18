<template>
  <div class="login-container">
    <div class="login-left">
      <h1 class="login-title">乐赛</h1>
      <p class="login-desc">一站式赛事服务平台 · 精彩有你</p>
      <div class="tag-group">
        <el-tag>多元赛事</el-tag>
        <el-tag>全民参与</el-tag>
        <el-tag>智能成长</el-tag>
      </div>
    </div>

    <div class="login-card">
      <h2 class="card-title">用户注册</h2>
      <p class="card-sub">填写信息，注册赛事平台账号</p>

      <el-form :model="registerForm" class="login-form">
        <el-form-item>
          <el-input v-model="registerForm.username" placeholder="请设置用户名" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="registerForm.password" type="password" placeholder="请设置密码" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="registerForm.repwd" type="password" placeholder="请再次确认密码" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="registerForm.role" placeholder="请选择您的角色">
            <el-option label="参赛选手" value="选手" />
            <el-option label="赛事主办方" value="主办方" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" class="login-btn" @click="handleRegister">立即注册</el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        已有账户？
        <router-link to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const registerForm = ref({
  username: '',
  password: '',
  repwd: '',
  role: ''
})

const handleRegister = () => {
  if (registerForm.password !== registerForm.repwd) {
    ElMessage.warning('两次密码输入不一致')
    return
  }
  ElMessage.success('注册成功，请前往登录')
  router.push('/login')
}
</script>

<style scoped>
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
  font-size: 60px;
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
  margin-right:300px;
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
.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}
.login-footer {
  text-align: center;
  font-size: 13px;
  color: #666;
}
.login-footer a {
  color: #4080ff;
  text-decoration: none;
}
</style>
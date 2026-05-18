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

      <!-- 登录表单 -->
      <el-form :model="loginForm" class="login-form">
        <el-form-item>
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>

        <!-- 验证码行 -->
        <div class="code-row">
          <el-input v-model="loginForm.code" placeholder="图形验证码" />
          <div class="code-box">{{ captcha }}</div>
        </div>

        <el-form-item>
          <el-button type="primary" class="login-btn" @click="handleLogin">立即登录</el-button>
        </el-form-item>
      </el-form>

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

// 选中角色
const userRole = ref('选手')
// 登录表单数据
const loginForm = ref({
  username: '',
  password: '',
  code: ''
})
// 随机验证码
const captcha = ref('')

// 生成随机4位验证码
const getCaptcha = () => {
  const str = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  let res = ''
  for (let i = 0; i < 4; i++) {
    res += str[Math.floor(Math.random() * 36)]
  }
  captcha.value = res
}

// 登录提交
const handleLogin = () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入账号密码')
    return
  }
  if (loginForm.code.toUpperCase() !== captcha.value) {
    ElMessage.error('验证码错误')
    getCaptcha()
    return
  }
  // 后续这里对接登录接口 + 路由跳转首页
  ElMessage.success('登录成功')
}

onMounted(() => {
  getCaptcha()
})
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

/* 左侧品牌 */
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

/* 右侧登录卡片 */
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

.role-tabs {
  margin-bottom: 20px;
  width: 100%;
}
.login-form {
  gap: 12px;
}

/* 验证码行 */
.code-row {
  display: flex;
  gap: 12px;
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
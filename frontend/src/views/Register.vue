<template>
  <div class="register-container">
    <!-- 左侧品牌区域 -->
    <div class="register-left">
      <h1 class="register-title">乐赛</h1>
      <p class="register-desc">一站式赛事服务平台 · 精彩有你</p>
      <div class="tag-group">
        <el-tag>多元赛事</el-tag>
        <el-tag>全民参与</el-tag>
        <el-tag>智能成长</el-tag>
      </div>
    </div>

    <!-- 右侧注册卡片 -->
    <div class="register-card">
      <h2 class="card-title">欢迎注册</h2>
      <p class="card-sub">请填写信息完成注册</p>

      <!-- 原生form表单 -->
      <form class="register-form" @submit.prevent="beforeSubmit">
        <el-form-item>
          <el-input
            type="text"
            name="username"
            v-model="registerForm.username"
            placeholder="请输入用户名"
            required
          />
        </el-form-item>
        <el-form-item>
          <el-input
            type="password"
            name="password"
            v-model="registerForm.password"
            placeholder="请输入密码"
            required
          />
        </el-form-item>
        <el-form-item>
          <el-input
            type="password"
            name="password2"
            v-model="registerForm.password2"
            placeholder="请再次输入密码"
            required
          />
        </el-form-item>

        <!-- 验证码行 -->
        <div class="code-row">
          <el-input v-model="registerForm.code" placeholder="图形验证码" />
          <div class="code-box" @click="getCaptcha">{{ captcha }}</div>
        </div>

        <el-form-item>
          <el-button type="primary" class="register-btn" native-type="submit">注册</el-button>
        </el-form-item>
      </form>

      <!-- 后端错误/成功信息 -->
      <div class="tip" :class="tipClass" v-if="tipMsg">{{ tipMsg }}</div>

      <!-- 底部链接 -->
      <div class="register-footer">
        <span>已有账户？</span>
        <router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const registerForm = ref({
  username: '',
  password: '',
  password2: '',
  code: ''
})
const captcha = ref('')
const tipMsg = ref('')
const tipClass = ref('')

// 生成验证码
const getCaptcha = () => {
  const str = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  let res = ''
  for (let i = 0; i < 4; i++) {
    res += str[Math.floor(Math.random() * 36)]
  }
  captcha.value = res
}

// 注册函数
const register = async () => {
  const { username, password, password2, code } = registerForm.value

  if (!username || !password || !password2) {
    ElMessage.warning('请输入完整信息')
    return
  }
  if (password !== password2) {
    ElMessage.error('两次密码不一致')
    getCaptcha()
    return
  }
  if (code.toUpperCase() !== captcha.value) {
    ElMessage.error('验证码错误')
    getCaptcha()
    return
  }

  try {
    // 调用注册接口
    const res = await axios.post('/api/register/', {
      username,
      password,
      password2,
      role: '选手' // 可以根据实际选择
    })
    if (res.data.success) {
      ElMessage.success(res.data.msg)

      // 注册成功后自动登录
      const loginRes = await axios.post('/api/login/', {
        username,
        password,
        role: '选手'
      })

      if (loginRes.data.success) {
        ElMessage.success('注册并登录成功')
        router.push('/home')
      } else {
        ElMessage.error('注册成功，但自动登录失败，请手动登录')
        router.push('/login')
      }
    } else {
      ElMessage.error(res.data.msg)
      getCaptcha()
    }
  } catch (err) {
    console.error(err)
    ElMessage.error('请求失败，请稍后重试')
    getCaptcha()
  }
}

// 表单提交
const beforeSubmit = (e) => {
  e.preventDefault()
  register()
}

onMounted(() => {
  getCaptcha()
})
</script>

<style scoped>
.register-container {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #1a3a4a, #244757);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 120px;
}

/* 左侧品牌 */
.register-left {
  color: #fff;
}
.register-title {
  font-size: 46px;
  font-weight: 600;
  margin-bottom: 16px;
}
.register-desc {
  font-size: 18px;
  opacity: 0.8;
  margin-bottom: 30px;
}
.tag-group {
  display: flex;
  gap: 12px;
}

/* 右侧注册卡片 */
.register-card {
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

.register-form {
  gap: 12px;
}

/* 验证码行 */
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

.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.tip {
  text-align: center;
  margin-top: 8px;
}
.tip.error {
  color: #ff4d4f;
}
.tip.success {
  color: #52c41a;
}

.register-footer {
  text-align: center;
  font-size: 13px;
  color: #666;
  margin-top: 16px;
}
.register-footer a {
  color: #4080ff;
  text-decoration: none;
}
</style>
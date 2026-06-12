<template>
  <div class="login-container">
    <div
      v-for="(image, index) in backgroundImages"
      :key="image"
      class="login-bg"
      :class="{ active: index === activeBgIndex }"
      :style="{
        backgroundImage: `url(${image})`
      }"
    />
    <div class="login-scrim" />
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
            placeholder="请输入验证码"
            maxlength="4"
            clearable
          />
          <button
            class="captcha-code"
            type="button"
            title="点击刷新验证码"
            :disabled="captchaLoading"
            @click="loadCaptcha"
          >
            {{ captchaLoading ? '刷新中' : captchaCode }}
          </button>
        </div>
        <el-button type="primary" style="width: 100%; margin-top: 24px" native-type="submit">
          立即登录
        </el-button>

        <div class="form-footer">
          <span>还没有账户? <router-link to="/register">立即注册</router-link></span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
const router = useRouter()

const form = ref({
  username: '',
  password: '',
  captcha: '',
})
const captchaCode = ref('')
const captchaLoading = ref(false)
let backgroundTimer = null
const backgroundImages = [
  '/login-backgrounds/badminton-login.png',
  '/login-backgrounds/football-login.png',
  '/login-backgrounds/esports-login.png',
  '/login-backgrounds/basketball-login.png',
  '/login-backgrounds/tennis-login.png',
  '/login-backgrounds/tabletennis-login.png',
  '/login-backgrounds/track-login.png',
  '/login-backgrounds/volleyball-login.png',
  '/login-backgrounds/swimming-login.png'
]
const activeBgIndex = ref(Math.floor(Math.random() * backgroundImages.length))

const preloadBackgrounds = () => {
  backgroundImages.forEach((src) => {
    const image = new Image()
    image.src = src
  })
}

const pickNextBackgroundIndex = () => {
  if (backgroundImages.length <= 1) return 0
  let nextIndex = activeBgIndex.value
  while (nextIndex === activeBgIndex.value) {
    nextIndex = Math.floor(Math.random() * backgroundImages.length)
  }
  return nextIndex
}

const startBackgroundLoop = () => {
  if (backgroundTimer) return
  backgroundTimer = window.setInterval(() => {
    activeBgIndex.value = pickNextBackgroundIndex()
  }, 6000)
}

const loadCaptcha = async () => {
  captchaLoading.value = true
  try {
    const res = await request.get('/api/login-captcha/')
    captchaCode.value = res.data.captcha || ''
    form.value.captcha = ''
  } catch (err) {
    captchaCode.value = '重试'
  } finally {
    captchaLoading.value = false
  }
}

const handleLogin = async () => {
  if (!form.value.username) {
    ElMessage.warning('请输入用户名')
    return
  }
  const isTryingAutoLogin = !form.value.password && !form.value.captcha
  if (!isTryingAutoLogin && (!form.value.password || !form.value.captcha)) {
    ElMessage.warning('普通账号请输入密码和验证码；批量测试账号可只填用户名')
    return
  }
  try {
    const csrfRes = await request.get('/csrf/')
    const csrfToken = csrfRes.data.csrfToken
    const res = await request.post(
      '/api/login/',
      {
        username: form.value.username,
        password: form.value.password,
        captcha: form.value.captcha,
      },
      {
        headers: {
          'X-CSRFToken': csrfToken
        }
      }
    )
    if (res.data.success) {
      ElMessage.success('登录成功')
      // 保存用户ID、Token、角色，用于后续鉴权和菜单权限
      localStorage.setItem('user_id', res.data.user_id)
      localStorage.setItem('username', res.data.username)
      localStorage.setItem('role', res.data.role)
      localStorage.setItem('is_super_admin', res.data.is_super_admin ? '1' : '0')
      
      router.push('/home')
      // if (res.data.role === 'PLAYER') {
        // router.push('/home')
      // } else if (res.data.role === 'ORGANIZER') {
        // router.push('/workbench')
      // } else if (res.data.role === 'ADMIN') {
        // router.push('/admin-review')
      // }
    } else {
      ElMessage.error(res.data.msg || '登录失败')
      loadCaptcha()
    }
  }
  catch (err) {
    ElMessage.error(err.response?.data?.msg || '请求失败，请检查后端服务')
    loadCaptcha()
  }
}

onMounted(() => {
  preloadBackgrounds()
  loadCaptcha()
  startBackgroundLoop()
})

onBeforeUnmount(() => {
  if (backgroundTimer) {
    window.clearInterval(backgroundTimer)
    backgroundTimer = null
  }
})
</script>

<style scoped>
.login-container {
  position: relative;
  display: flex;
  min-height: 100dvh;
  align-items: center;
  justify-content: space-around;
  gap: clamp(32px, 6vw, 92px);
  padding: clamp(32px, 7vw, 96px) clamp(24px, 8vw, 128px);
  overflow: hidden;
  background: #081c3a;
}
.login-bg,
.login-scrim {
  position: absolute;
  inset: 0;
}
.login-bg {
  background-size: cover;
  background-position: center;
  opacity: 0;
  transform: scale(1.03);
  transition: opacity 1.2s ease, transform 6s ease;
  will-change: opacity, transform;
}
.login-bg.active {
  opacity: 1;
  transform: scale(1.06);
}
.login-scrim {
  background:
    radial-gradient(circle at 18% 25%, rgba(22, 119, 255, 0.42), transparent 32%),
    linear-gradient(90deg, rgba(5, 16, 38, 0.86) 0%, rgba(5, 16, 38, 0.54) 48%, rgba(5, 16, 38, 0.78) 100%);
  backdrop-filter: saturate(1.08);
}
.login-left {
  position: relative;
  z-index: 1;
  color: white;
  max-width: 480px;
}
.login-left h1 {
  font-size: clamp(42px, 5vw, 68px);
  margin: 0 0 12px;
  color: #fff;
  font-weight: 800;
}
.login-left p {
  font-size: clamp(18px, 2vw, 24px);
  opacity: 0.9;
  margin: 0 0 24px;
}
.tags {
  display: flex;
  gap: 12px;
}
.tags span {
  padding: 6px 16px;
  background: rgba(255,255,255,0.16);
  border: 1px solid rgba(255,255,255,0.22);
  border-radius: 999px;
  font-size: 14px;
  backdrop-filter: blur(10px);
}
.login-form-card {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.92);
  padding: clamp(26px, 3vw, 36px);
  border: 1px solid rgba(255,255,255,0.58);
  border-radius: 14px;
  width: min(380px, 100%);
  box-shadow: 0 24px 70px rgba(0,0,0,0.24);
  backdrop-filter: blur(18px);
}
.login-form-card h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 800;
  color: #10233f;
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
  display: grid;
  grid-template-columns: 1fr 96px;
  gap: 12px;
  align-items: stretch;
}
.captcha-code {
  min-height: 40px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #f2f5f9;
  color: #1e3c72;
  cursor: pointer;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0;
}
.captcha-code:disabled {
  cursor: wait;
  opacity: 0.7;
}
.form-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  font-size: 13px;
}
.form-footer a, .form-footer span a {
  color: #1677ff;
  text-decoration: none;
}

@media (max-width: 860px) {
  .login-container {
    flex-direction: column;
    justify-content: center;
    align-items: stretch;
  }

  .login-left {
    max-width: none;
    text-align: center;
  }

  .tags {
    justify-content: center;
    flex-wrap: wrap;
  }

  .login-form-card {
    margin: 0 auto;
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-bg {
    transition: opacity 0.2s linear;
  }
}
</style>

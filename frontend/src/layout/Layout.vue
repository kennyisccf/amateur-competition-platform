<template>
  <el-container class="app-shell">
    <el-aside width="220px" class="sidebar">
      <div class="logo-area">
        <h1>乐赛</h1>
        <p>多元赛事 · 全民参与</p>
      </div>

      <div class="menu-scroll">
        <div class="menu-group">
          <div class="menu-title">核心大厅</div>
          <el-menu
            :default-active="activeMenu"
            background-color="#1677ff"
            text-color="#fff"
            active-text-color="#fff"
            router
          >
            <el-menu-item index="/home">
              <el-icon><Trophy /></el-icon>
              <span>探索赛事大厅</span>
            </el-menu-item>
            <el-menu-item index="/profile">
              <el-icon><User /></el-icon>
              <span>我的运动档案</span>
            </el-menu-item>
            <el-menu-item index="/notifications">
              <el-icon><Bell /></el-icon>
              <el-badge
                :value="notificationBadge"
                :max="99"
                :hidden="notificationBadge === 0"
                class="menu-badge"
              >
                <span>消息通知</span>
              </el-badge>
            </el-menu-item>
            <el-menu-item index="/friends">
              <el-icon><ChatDotRound /></el-icon>
              <span>好友系统</span>
            </el-menu-item>
          </el-menu>
        </div>

        <div class="menu-group" v-if="['PLAYER', 'ORGANIZER', 'ADMIN'].includes(userRole)">
          <div class="menu-title">赛事创建与管理</div>
          <el-menu
            :default-active="activeMenu"
            background-color="#1677ff"
            text-color="#fff"
            active-text-color="#fff"
            router
          >
            <el-menu-item index="/create">
              <el-icon><Plus /></el-icon>
              <span>{{ userRole === 'PLAYER' ? '发起私人赛事' : '发起全新赛事' }}</span>
            </el-menu-item>
            <el-menu-item index="/workbench">
              <el-icon><Tools /></el-icon>
              <span>赛事工作台</span>
            </el-menu-item>
            <el-menu-item index="/registration-manage">
              <el-icon><List /></el-icon>
              <span>报名管理</span>
            </el-menu-item>
          </el-menu>
        </div>

        <div class="menu-group" v-if="userRole === 'ADMIN'">
          <div class="menu-title">管理员专区</div>
          <el-menu
            :default-active="activeMenu"
            background-color="#1677ff"
            text-color="#fff"
            active-text-color="#fff"
            router
          >
            <el-menu-item index="/admin-review">
              <el-icon><Setting /></el-icon>
              <span>审核与风控</span>
            </el-menu-item>
          </el-menu>
        </div>
      </div>

      <div class="logout-area">
        <el-button type="danger" plain @click="handleLogout">
          退出登录
        </el-button>
      </div>
    </el-aside>

    <el-container class="content-shell">
      <el-main class="content-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell, ChatDotRound, List, Plus, Setting, Tools, Trophy, User } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import {
  getUnreadNotificationCount,
  NOTIFICATION_REFRESH_EVENT,
  NOTIFICATION_SYNC_EVENT
} from '@/utils/notificationEvents'

const route = useRoute()
const router = useRouter()
const userRole = ref('')
const notificationBadge = ref(0)
let badgeTimer = null

const activeMenu = computed(() => {
  if (route.path.startsWith('/event-detail')) return '/home'
  if (route.path.startsWith('/event-register')) return '/home'
  if (route.path.startsWith('/competition-edit')) return '/workbench'
  return route.path
})

const refreshNotificationBadge = async () => {
  if (!localStorage.getItem('user_id')) {
    notificationBadge.value = 0
    return
  }
  try {
    const res = await request.get('/api/notifications/')
    if (res.data.success) {
      notificationBadge.value = getUnreadNotificationCount(res.data.messages || [])
    }
  } catch (err) {
    notificationBadge.value = 0
  }
}

const syncNotificationBadge = (event) => {
  const count = event?.detail?.count
  if (Number.isFinite(count)) {
    notificationBadge.value = count
  }
}

const refreshWhenVisible = () => {
  if (!document.hidden) refreshNotificationBadge()
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出当前账号吗？', '退出登录', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        const res = await request.post('/api/logout/', {})
        if (res.data.success) {
          localStorage.removeItem('user_id')
          localStorage.removeItem('role')
          localStorage.removeItem('username')
          localStorage.removeItem('is_super_admin')
          localStorage.removeItem('token')
          notificationBadge.value = 0
          ElMessage.success('已退出登录')
          router.replace('/login')
        }
      } catch (error) {
        ElMessage.error('退出失败')
      }
    })
    .catch(() => {})
}

onMounted(() => {
  userRole.value = localStorage.getItem('role') || ''
  refreshNotificationBadge()
  window.addEventListener(NOTIFICATION_REFRESH_EVENT, refreshNotificationBadge)
  window.addEventListener(NOTIFICATION_SYNC_EVENT, syncNotificationBadge)
  window.addEventListener('focus', refreshNotificationBadge)
  document.addEventListener('visibilitychange', refreshWhenVisible)
  badgeTimer = window.setInterval(refreshNotificationBadge, 3000)
})

onUnmounted(() => {
  if (badgeTimer) window.clearInterval(badgeTimer)
  window.removeEventListener(NOTIFICATION_REFRESH_EVENT, refreshNotificationBadge)
  window.removeEventListener(NOTIFICATION_SYNC_EVENT, syncNotificationBadge)
  window.removeEventListener('focus', refreshNotificationBadge)
  document.removeEventListener('visibilitychange', refreshWhenVisible)
})

watch(
  () => route.fullPath,
  () => refreshNotificationBadge()
)
</script>

<style scoped>
.app-shell {
  height: 100dvh;
  width: 100%;
  overflow: hidden;
}
.sidebar {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: #1677ff;
  overflow: hidden;
}
.logo-area {
  flex: 0 0 auto;
  padding: 26px 22px 18px;
  color: white;
}
.logo-area h1 {
  margin: 0;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: 0;
}
.logo-area p {
  margin: 8px 0 0;
  font-size: 13px;
  opacity: 0.86;
}
.menu-scroll {
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden auto;
  padding-bottom: 18px;
}
.menu-group {
  margin-top: 18px;
}
.menu-title {
  padding: 0 24px 8px;
  color: rgba(255,255,255,0.72);
  font-size: 12px;
}
.menu-group :deep(.el-menu) {
  border-right: 0;
}
.menu-group :deep(.el-menu-item) {
  margin: 0 10px 4px;
  border-radius: 8px;
}
.menu-group :deep(.el-menu-item.is-active) {
  background: rgba(255,255,255,0.18);
  font-weight: 700;
}
.menu-badge {
  line-height: 1;
}
.menu-badge :deep(.el-badge__content) {
  border: 0;
}
.logout-area {
  flex: 0 0 auto;
  padding: 14px 20px 22px;
}
.logout-area :deep(.el-button) {
  width: 100%;
}
.content-shell {
  min-width: 0;
  height: 100dvh;
  overflow: hidden;
}
.content-main {
  padding: 0;
  background: #f5f7fa;
  height: 100dvh;
  overflow-y: auto;
  overflow-x: hidden;
  min-width: 0;
  scrollbar-width: thin;
}
.content-main::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.content-main::-webkit-scrollbar-thumb {
  background: #c9d4e4;
  border-radius: 999px;
}
@media (max-width: 900px) {
  .app-shell {
    flex-direction: column;
  }
  .sidebar {
    width: 100% !important;
    height: auto;
    max-height: 38vh;
    display: flex;
    flex-direction: row;
    align-items: stretch;
    gap: 10px;
    padding: 10px 12px;
    overflow-x: auto;
    overflow-y: hidden;
  }
  .logo-area {
    flex: 0 0 auto;
    padding: 8px 10px 8px 0;
  }
  .logo-area h1 {
    font-size: 22px;
  }
  .logo-area p,
  .menu-title {
    display: none;
  }
  .menu-scroll {
    display: flex;
    flex: 1 1 auto;
    gap: 10px;
    overflow-x: auto;
    overflow-y: hidden;
    padding-bottom: 0;
  }
  .menu-group {
    flex: 0 0 auto;
    margin-top: 0;
  }
  .menu-group :deep(.el-menu) {
    display: flex;
    border-right: 0;
  }
  .menu-group :deep(.el-menu-item) {
    height: 44px;
    margin: 0 2px;
    padding: 0 12px;
    border-radius: 8px;
  }
  .logout-area {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    padding: 0;
    margin-left: auto;
  }
  .logout-area :deep(.el-button) {
    width: auto;
  }
  .content-shell,
  .content-main {
    height: auto;
    min-height: 0;
    flex: 1 1 auto;
  }
}
@media (max-width: 560px) {
  .sidebar {
    padding: 8px;
  }
  .menu-group :deep(.el-menu-item span) {
    display: none;
  }
  .menu-badge :deep(.el-badge__content) {
    display: inline-flex;
  }
}
</style>

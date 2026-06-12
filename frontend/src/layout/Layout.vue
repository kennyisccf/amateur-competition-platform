<template>
  <el-container class="app-shell">
    <!-- 左侧导航栏 -->
    <el-aside width="200px" class="sidebar">
      <!-- 顶部品牌 -->
      <div class="logo-area">
        <h1>乐赛</h1>
        <p>多元赛事·全民参与</p>
      </div>

      <!-- 核心大厅菜单 -->
      <div class="menu-group">
        <div class="menu-title">核心大厅</div>
        <el-menu
          default-active="1"
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
            <span>消息通知</span>
          </el-menu-item>
          <el-menu-item index="/friends">
            <el-icon><ChatDotRound /></el-icon>
            <span>好友系统</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 赛事管理：参赛者可管理私人赛事，管理员拥有全部赛事权限 -->
      <div class="menu-group" v-if="['PLAYER', 'ORGANIZER', 'ADMIN'].includes(userRole)">
        <div class="menu-title">赛事创建与管理</div>
        <el-menu
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

      <!-- 管理员专区：仅管理员可见 -->
      <div class="menu-group" v-if="userRole === 'ADMIN'">
        <div class="menu-title">管理员专区</div>
        <el-menu
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
      <div class="logout-area">
        <el-button type="danger" plain style="width: 160px" @click="handleLogout"> 退出登录 </el-button>
      </div>
    </el-aside>

    <!-- 右侧内容区 -->
    <el-container class="content-shell">
      <el-main class="content-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Bell, Trophy, User, Plus, Tools, List, Setting, ChatDotRound } from '@element-plus/icons-vue'
const userRole = ref('')
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
onMounted(() => {
  // 从本地获取用户角色，用于菜单权限
  userRole.value = localStorage.getItem('role') || ''
})

const handleLogout = () => {
  ElMessageBox.confirm(
    '确定退出当前账号吗？',
    '退出登录',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
  .then(async () => {
    try {
      const res = await request.post('/api/logout/', {})
      if (res.data.success) {
        localStorage.removeItem('user_id')
        localStorage.removeItem('role')
        localStorage.removeItem('username')
        localStorage.removeItem('is_super_admin')
        localStorage.removeItem('token')
        ElMessage.success('已退出登录')
        router.replace('/login')
      }
    } catch (error) {
      ElMessage.error('退出失败')
      console.error(error)
    }
  })
  .catch(() => {})
}
</script>

<style scoped>
.logo-area {
  padding: 24px;
  color: white;
}
.logo-area h1 {
  margin: 0;
  font-size: 28px;
  font-weight: bold;
}
.logo-area p {
  margin: 8px 0 0;
  font-size: 13px;
  opacity: 0.8;
}
.menu-group {
  margin-top: 20px;
}
.menu-title {
  padding: 0 24px 8px;
  color: rgba(255,255,255,0.7);
  font-size: 12px;
}
.logout-area {
  position: absolute;
  bottom: 30px;
  left: 20px;
  right: 20px;
  text-align: center;
}
.el-aside {
  position: relative;
}
.sidebar {
  background: #1677ff;
  position: relative;
  height: 100vh;
  overflow: hidden;
}
.app-shell {
  height: 100vh;
  width: 100%;
  overflow: hidden;
}
.content-shell {
  min-width: 0;
  height: 100vh;
  overflow: hidden;
}
.content-main {
  padding: 0;
  background: #f5f7fa;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  min-width: 0;
  scrollbar-width: none;
}
.content-main::-webkit-scrollbar {
  width: 0;
  height: 0;
}
</style>

<template>
  <el-container style="height: 100vh">
    <!-- 左侧导航栏 -->
    <el-aside width="200px" style="background: #1677ff">
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
        </el-menu>
      </div>

      <!-- 主办方专区：仅主办方/管理员可见 -->
      <div class="menu-group" v-if="userRole === '主办方' || userRole === '管理员'">
        <div class="menu-title">主办方专区</div>
        <el-menu
          background-color="#1677ff"
          text-color="#fff"
          active-text-color="#fff"
          router
        >
          <el-menu-item index="/create">
            <el-icon><Plus /></el-icon>
            <span>发起全新赛事</span>
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
      <div class="menu-group" v-if="userRole === '管理员'">
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
    </el-aside>

    <!-- 右侧内容区 -->
    <el-container>
      <el-main style="padding: 0; background: #f5f7fa">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Trophy, User, Plus, Tools, List, Setting } from '@element-plus/icons-vue'

const userRole = ref('')

onMounted(() => {
  // 从本地获取用户角色，用于菜单权限
  userRole.value = localStorage.getItem('role') || ''
})
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
</style>
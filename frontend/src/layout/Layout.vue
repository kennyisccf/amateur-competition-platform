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
          <el-menu-item index="/event-detail">
            <el-icon><InfoFilled /></el-icon>
            <span>赛事详情</span>
          </el-menu-item>
          <el-menu-item index="/event-register">
            <el-icon><Edit /></el-icon>
            <span>赛事报名</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 主办方专区 -->
      <div class="menu-group">
        <div class="menu-title">主办方专区</div>
        <el-menu
          background-color="#1677ff"
          text-color="#fff"
          active-text-color="#fff"
        >
          <el-menu-item index="/create">
            <el-icon><Plus /></el-icon>
            <span>发起全新赛事</span>
          </el-menu-item>
          <el-menu-item index="/workbench">
            <el-icon><Tools /></el-icon>
            <span>赛事工作台</span>
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
import { Trophy, User, Plus, Tools, InfoFilled, Edit } from '@element-plus/icons-vue'
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
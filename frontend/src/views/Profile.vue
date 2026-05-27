<template>
  <div class="profile-container">
    <a href="javascript:;" @click="router.push('/home')">← 返回赛事大厅</a>
    <div style="text-align: right; color: #666; font-size: 14px;">当前角色: 参赛选手</div>
    
    <div class="profile-content">
      <!-- 左侧个人信息卡 -->
      <div class="info-card">
        <div class="avatar">
          <el-icon><User /></el-icon>
        </div>
        <h2>{{ userInfo.nickname }}</h2>
        <p>全栈运动爱好者 | 专注{{ userInfo.skills || '篮球与MOBA' }}</p>
        
        <div class="stats-row">
          <div class="stat-item">
            <div class="stat-value">{{ userInfo.points || 1250 }}</div>
            <div class="stat-label">天梯积分</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userInfo.rank || 89 }}</div>
            <div class="stat-label">全站排名</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userInfo.winRate || 68 }}%</div>
            <div class="stat-label">总胜率</div>
          </div>
        </div>

        <div class="badges-row">
          <span class="badge">🏀 街球中流砥柱</span>
          <span class="badge">🎮 零失误控场</span>
          <span class="badge">✨ 活跃达人</span>
        </div>
      </div>

      <!-- 右侧参赛痕迹 -->
      <div class="history-card">
        <h3>参赛痕迹时间轴</h3>
        <div class="timeline">
          <div class="timeline-item" v-for="item in historyList" :key="item.id">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-title">
                {{ item.title }}
                <span class="timeline-status" :class="item.status">{{ item.statusText }}</span>
              </div>
              <div class="timeline-time">{{ item.time }}</div>
              <div class="timeline-desc">{{ item.desc }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 基础资料管理 -->
      <div class="edit-card">
        <h3>基础资料管理</h3>
        <form @submit.prevent="handleUpdateInfo" class="edit-form">
          <div class="form-row">
            <div class="form-item">
              <label>选手昵称</label>
              <el-input v-model="form.nickname" />
            </div>
            <div class="form-item">
              <label>绑定邮箱</label>
              <el-input v-model="form.email" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-item">
              <label>擅长项目</label>
              <el-input v-model="form.skills" />
            </div>
            <div class="form-item">
              <label>所属常驻战队</label>
              <el-input v-model="form.team" />
            </div>
          </div>
          <el-button type="primary" native-type="submit">保存资料修改</el-button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()

const userInfo = ref({})
const historyList = ref([
  {
    id: 1,
    title: '"乐赛杯"年度MOBA电竞社群巅峰邀请赛',
    time: '2026年5月(当前)',
    status: 'processing',
    statusText: '进行中',
    desc: '战队状态: 已成功晋级16强淘汰赛。下一场对局将于本周六进行。'
  },
  {
    id: 2,
    title: '第三届社区三人篮球赛（市中心公园站）',
    time: '2026年4月',
    status: 'finished',
    statusText: '已完赛',
    desc: '最终战绩: 荣获本届赛事【公开组·亚军】。'
  }
])

const form = ref({
  nickname: '',
  email: '',
  skills: '',
  team: ''
})

// 等后端个人接口写完，把这里填上
const loadUserInfo = async () => {
  // const userId = localStorage.getItem('user_id')
  // const res = await axios.get(`http://localhost:8000/api/user/info/${userId}/`)
  // userInfo.value = res.data.data
  // form.value = { ...res.data.data }
  // historyList.value = res.data.registrations
}

const handleUpdateInfo = async () => {
  // 等后端更新接口写完，把这里填上
  ElMessage.success('资料修改成功！')
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile-container {
  padding: 24px;
}
.profile-content {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  margin-top: 24px;
}
.info-card {
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  text-align: center;
  height: fit-content;
}
.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #e6f4ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}
.avatar .el-icon {
  font-size: 40px;
  color: #1677ff;
}
.info-card h2 {
  margin: 0 0 8px;
  font-size: 22px;
}
.info-card p {
  color: #666;
  margin: 0 0 24px;
  font-size: 14px;
}
.stats-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}
.stat-item {
  text-align: center;
}
.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #1677ff;
}
.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
.badges-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.badge {
  padding: 4px 10px;
  background: #fff7e6;
  color: #fa8c16;
  border-radius: 12px;
  font-size: 12px;
}
.history-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  margin-bottom: 24px;
}
.history-card h3 {
  margin: 0 0 20px;
  font-size: 16px;
  color: #333;
  border-left: 3px solid #1677ff;
  padding-left: 12px;
}
.timeline-item {
  position: relative;
  padding-left: 24px;
  margin-bottom: 24px;
  border-left: 1px solid #e8e8e8;
}
.timeline-item:last-child {
  border-left: none;
}
.timeline-dot {
  position: absolute;
  left: -6px;
  top: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #1677ff;
}
.timeline-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.timeline-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}
.timeline-status.processing {
  background: #e6f7ff;
  color: #1677ff;
}
.timeline-status.finished {
  background: #f6ffed;
  color: #52c41a;
}
.timeline-time {
  font-size: 14px;
  color: #666;
  margin: 4px 0;
}
.timeline-desc {
  font-size: 14px;
  color: #333;
}
.edit-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.edit-card h3 {
  margin: 0 0 20px;
  font-size: 16px;
  color: #333;
  border-left: 3px solid #1677ff;
  padding-left: 12px;
}
.form-row {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}
.form-item {
  flex: 1;
}
.form-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}
</style>
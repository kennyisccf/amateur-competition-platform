<template>
  <div class="profile-container">
    <a href="javascript:;" @click="router.push('/home')">← 返回赛事大厅</a>
    <div style="text-align: right; color: #666; font-size: 14px;">当前角色: {{ userRole }}</div>
    
    <div class="profile-content">
      <div class="info-card">
        <div class="avatar">
          <el-icon><User /></el-icon>
        </div>
        <h2>{{ userInfo.nickname || userInfo.username }}</h2>
        <p>全栈运动爱好者 | 专注{{ userInfo.skills || '篮球与MOBA' }}</p>
        
        <div class="stats-row">
          <div class="stat-item">
            <div class="stat-value">{{ userInfo.total_points || 1250 }}</div>
            <div class="stat-label">天梯积分</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userRank || 89 }}</div>
            <div class="stat-label">全站排名</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ winRate || 68 }}%</div>
            <div class="stat-label">总胜率</div>
          </div>
        </div>

        <div class="badges-row">
          <span class="badge">🏀 街球中流砥柱</span>
          <span class="badge">🎮 零失误控场</span>
          <span class="badge">✨ 活跃达人</span>
        </div>
      </div>

      <div class="history-card">
        <h3>参赛痕迹时间轴</h3>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else class="timeline">
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
const loading = ref(false)
const userRole = ref(localStorage.getItem('role') || '参赛选手')
const userInfo = ref({})
const historyList = ref([])
const form = ref({})

// 获取请求头
const getHeaders = async () => {
  const token = localStorage.getItem('token')
  return { 'Authorization': `Bearer ${token}` }
}

const loadUserInfo = async () => {
  loading.value = true
  try {
    const headers = await getHeaders()
    // 拉取个人信息
    const res = await axios.get('http://localhost:8000/api/profile/', { headers })
    if (res.data.success) {
      userInfo.value = res.data.data
      form.value = { ...res.data.data }
    }

    // 拉取报名记录
    const userId = localStorage.getItem('user_id')
    const regRes = await axios.get(`http://localhost:8000/api/my_registrations/?player_id=${userId}`, { headers })
    if (regRes.data.success) {
      historyList.value = regRes.data.data
    }
  } catch (err) {
    ElMessage.error('加载信息失败')
  } finally { loading.value = false }
}

const handleUpdateInfo = async () => {
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
.loading {
  text-align: center;
  padding: 50px;
  color: #666;
}
</style>
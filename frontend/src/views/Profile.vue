<template>
  <div class="profile-container">
    <a href="javascript:;" @click="router.push('/home')">← 返回赛事大厅</a>
    <div style="text-align: right; color: #666; font-size: 14px;"></div>
    
    <div class="profile-content">
      <div class="info-card">
        <div class="avatar">
          <el-icon><User /></el-icon>
        </div>
        <h2>{{ userInfo.nickname || userInfo.username }}</h2>
        <p>当前积分：{{ userInfo.points || 0 }}</p>
        <!-- <p>全栈运动爱好者 | 专注{{ userInfo.skills || '篮球与MOBA' }}</p> -->
        
        <!-- <div class="stats-row"> -->
          <!-- <div class="stat-item"> -->
            <!-- <div class="stat-value">{{ userInfo.total_points}}</div> -->
            <!-- <div class="stat-label">天梯积分</div> -->
          <!-- </div> -->
          <!-- <div class="stat-item"> -->
            <!-- <div class="stat-value">{{ userRank}}</div> -->
            <!-- <div class="stat-label">全站排名</div> -->
          <!-- </div> -->
          <!-- <div class="stat-item"> -->
            <!-- <div class="stat-value">{{ winRate}}%</div> -->
            <!-- <div class="stat-label">总胜率</div> -->
          <!-- </div> -->
        <!-- </div> -->

        <!-- <div class="badges-row"> -->
          <!-- <span class="badge">🏀 街球中流砥柱</span> -->
          <!-- <span class="badge">🎮 零失误控场</span> -->
          <!-- <span class="badge">✨ 活跃达人</span> -->
        <!-- </div> -->
      </div>

      <div class="history-card">
        <h3>参赛痕迹时间轴</h3>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else class="timeline">
          <div class="timeline-item" :class="{ hidden: !item.showInProfile }" v-for="item in historyList" :key="item.id">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-title">
                <span>
                  {{ item.title }}
                  <el-tag size="small" :type="item.competitionType === 'PRIVATE' ? 'warning' : 'success'" class="type-tag">
                    {{ item.competitionTypeText }}
                  </el-tag>
                </span>
                <div class="action-area">              
                  <span
                    class="timeline-status"
                    :class="item.status"
                  >
                    {{ item.statusText }}
                  </span>
                  <el-switch
                    v-model="item.showInProfile"
                    size="small"
                    active-text="展示"
                    inactive-text="隐藏"
                    @change="updateTraceVisibility(item)"
                  />
                  <el-button
                    size="small"
                    type="primary"
                    link
                    @click="router.push(`/event-detail/${item.competitionId}`)"
                  >查看详情</el-button>
                  <el-button
                    v-if="item.canCancel"
                    size="small"
                    type="danger"
                    link
                    @click="cancelRegistration(item.id)"
                  > 取消报名</el-button>            
                </div>   
              </div>
              <div class="timeline-time">{{ item.time }}</div>
              <div class="timeline-desc">
                <span>人数：{{ item.participantCount }}/{{ item.maxParticipants }}</span>
                <template v-if="item.isFinished">
                  <span>成绩：{{ item.finalScore || '-' }}</span>
                  <span>排名：{{ item.finalRank || '-' }}</span>
                  <span v-if="item.competitionType !== 'PRIVATE'">获得积分：{{ item.earnedPoints || 0 }}</span>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

       <div class="edit-card">
          <h3>个人资料</h3>
          <el-form :model="form" label-width="90px">
          <el-form-item label="用户名">
            <el-input :value="userInfo.username" disabled/>
          </el-form-item>
          <el-form-item label="昵称">
            <el-input v-model="form.nickname"/>
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="form.email"/>
          </el-form-item>
          <el-form-item label="身份">
            <el-tag> {{ userRole }}</el-tag>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleUpdateInfo">
              保存修改
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User } from '@element-plus/icons-vue'
import { ElMessage , ElMessageBox} from 'element-plus'
import request from '@/utils/request'
const router = useRouter()
const loading = ref(false)
const userRole = ref(localStorage.getItem('role') || '参赛选手')
const userInfo = ref({})
const historyList = ref([])
const form = ref({})


// 获取请求
const loadUserInfo = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/user/')
    if (res.data.success) {
      userInfo.value = res.data.data
      form.value = {
        nickname: res.data.data.nickname,
        email: res.data.data.email
      }
      userRole.value = res.data.data.role
    }
    const regRes = await request.get('/api/my_registrations/')
    if (regRes.data.success) {
      historyList.value = regRes.data.data
    }
  } catch (error) {
    ElMessage.error('加载用户信息失败')
  } finally {
    loading.value = false
  }
}
const handleUpdateInfo = async () => {
  try {
    const res = await request.post(
      '/api/update_user/',
      {
        nickname: form.value.nickname,
        email: form.value.email
      }
    )
    if (res.data.success) {
      ElMessage.success('资料修改成功')
      loadUserInfo()
    }
  } catch (error) {
    ElMessage.error('修改失败')
  }
}
const cancelRegistration = async (registrationId) => {
  try {
    await ElMessageBox.confirm(
      '确定取消该赛事报名吗？',
      '提示',
      {
        type: 'warning'
      }
    )
    const res = await request.post(
      '/api/cancel_registration/',
      {
        registration_id: registrationId
      }
    )
    if(res.data.success){
      ElMessage.success('已取消报名')
      loadUserInfo()
    }else{
      ElMessage.error(res.data.msg)
    }
  } catch(err){
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('取消报名失败')
    }
  }
}

const updateTraceVisibility = async (item) => {
  try {
    const res = await request.post('/api/registrations/visibility/', {
      registration_id: item.id,
      show_in_profile: item.showInProfile
    })
    if (res.data.success) {
      ElMessage.success(item.showInProfile ? '已展示该参赛痕迹' : '已隐藏该参赛痕迹')
    } else {
      ElMessage.error(res.data.msg || '设置失败')
      item.showInProfile = !item.showInProfile
    }
  } catch (err) {
    ElMessage.error('设置失败')
    item.showInProfile = !item.showInProfile
  }
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
.timeline-item.hidden {
  opacity: 0.5;
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
.timeline-status.ongoing {
  background: #f6ffed;
  color: #52c41a;
}
.timeline-status.rejected {
  background: #fff2f0;
  color: #f5222d;
}
.timeline-time {
  font-size: 14px;
  color: #666;
  margin: 4px 0;
}
.timeline-desc {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 14px;
  color: #333;
}
.type-tag {
  margin-left: 8px;
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
.action-area {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>

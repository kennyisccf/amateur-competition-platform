<template>
  <div class="profile-container">
    <header class="profile-header">
      <div>
        <p class="eyebrow">个人中心</p>
        <h2>我的运动档案</h2>
        <p>管理公开展示信息、报名记录和个人参赛轨迹。</p>
      </div>
      <el-button plain @click="router.push('/home')">返回赛事大厅</el-button>
    </header>

    <div class="profile-layout">
      <aside class="profile-sidebar">
        <section class="info-card">
          <div class="avatar">
            <el-icon><User /></el-icon>
          </div>
          <h3>{{ userInfo.nickname || userInfo.username || '未命名用户' }}</h3>
          <p>{{ roleLabel }} · {{ userInfo.points || 0 }} 积分</p>
          <div class="code-box">
            <span>{{ userCode }}</span>
            <el-button size="small" text type="primary" :icon="CopyDocument" @click="copyUserCode">
              复制
            </el-button>
          </div>
        </section>

        <section class="completion-card">
          <div class="card-title">
            <h3>资料完整度</h3>
            <strong>{{ profileCompletion }}%</strong>
          </div>
          <el-progress :percentage="profileCompletion" :show-text="false" :stroke-width="8" />
          <p>{{ completionTip }}</p>
        </section>

        <section class="edit-card">
          <h3>账号资料</h3>
          <el-form :model="form" label-position="top">
            <el-form-item label="用户名">
              <el-input :value="userInfo.username" disabled />
            </el-form-item>
            <el-form-item label="账号编号">
              <el-input :value="userCode" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="form.nickname" maxlength="50" show-word-limit />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="form.email" maxlength="100" show-word-limit />
            </el-form-item>
            <el-form-item label="角色">
              <el-tag>{{ roleLabel }}</el-tag>
            </el-form-item>
            <el-button type="primary" :loading="saving" @click="handleUpdateInfo">
              保存资料
            </el-button>
          </el-form>
        </section>
      </aside>

      <main class="profile-main">
        <section class="stats-grid">
          <div class="stat-card">
            <span>报名记录</span>
            <strong>{{ registrationStats.total }}</strong>
          </div>
          <div class="stat-card">
            <span>审核中</span>
            <strong>{{ registrationStats.processing }}</strong>
          </div>
          <div class="stat-card">
            <span>参赛中</span>
            <strong>{{ registrationStats.ongoing }}</strong>
          </div>
          <div class="stat-card">
            <span>已完赛</span>
            <strong>{{ registrationStats.finished }}</strong>
          </div>
        </section>

        <section class="history-card">
          <div class="history-head">
            <div>
              <h3>参赛时间线</h3>
              <p>隐藏的记录不会出现在公开档案里，但仍会保存在个人中心。</p>
            </div>
            <el-select v-model="historyFilter" class="filter-select">
              <el-option label="全部记录" value="all" />
              <el-option label="审核中" value="processing" />
              <el-option label="参赛中" value="ongoing" />
              <el-option label="已完赛" value="finished" />
              <el-option label="已隐藏" value="hidden" />
            </el-select>
          </div>

          <el-skeleton v-if="loading" :rows="8" animated />

          <el-empty
            v-else-if="filteredHistory.length === 0"
            description="暂无符合条件的参赛记录"
          >
            <el-button v-if="historyFilter !== 'all'" @click="historyFilter = 'all'">
              查看全部
            </el-button>
            <el-button v-else type="primary" @click="router.push('/home')">
              去报名赛事
            </el-button>
          </el-empty>

          <div v-else class="timeline">
            <article
              v-for="item in filteredHistory"
              :key="item.id"
              class="timeline-item"
              :class="{ hidden: !item.showInProfile }"
            >
              <div class="timeline-dot" :class="item.status" />
              <div class="timeline-content">
                <div class="timeline-title">
                  <div>
                    <h4>{{ item.title }}</h4>
                    <div class="timeline-tags">
                      <el-tag size="small" :type="item.competitionType === 'PRIVATE' ? 'warning' : 'success'">
                        {{ item.competitionType === 'PRIVATE' ? '私人赛' : '公开赛' }}
                      </el-tag>
                      <el-tag size="small" :type="statusTagType(item.status)">
                        {{ statusText(item) }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="action-area">
                    <el-switch
                      v-model="item.showInProfile"
                      size="small"
                      active-text="公开"
                      inactive-text="隐藏"
                      @change="updateTraceVisibility(item)"
                    />
                    <el-button size="small" type="primary" link @click="router.push(`/event-detail/${item.competitionId}`)">
                      详情
                    </el-button>
                    <el-button
                      v-if="item.canCancel"
                      size="small"
                      type="danger"
                      link
                      @click="cancelRegistration(item.id)"
                    >
                      取消报名
                    </el-button>
                  </div>
                </div>

                <div class="timeline-time">
                  <el-icon><Clock /></el-icon>
                  <span>{{ item.time }}</span>
                </div>

                <div class="timeline-desc">
                  <span>人数 {{ item.participantCount }}/{{ item.maxParticipants }}</span>
                  <template v-if="item.isFinished">
                    <span>成绩 {{ item.finalScore || '-' }}</span>
                    <span>排名 {{ item.finalRank || '-' }}</span>
                    <span v-if="item.competitionType !== 'PRIVATE'">获得 {{ item.earnedPoints || 0 }} 积分</span>
                  </template>
                  <span v-if="item.desc">{{ item.desc }}</span>
                </div>
              </div>
            </article>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Clock, CopyDocument, User } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const userInfo = ref({})
const historyList = ref([])
const historyFilter = ref('all')
const form = ref({
  nickname: '',
  email: ''
})

const roleMap = {
  PLAYER: '参赛选手',
  ORGANIZER: '主办方',
  ADMIN: '管理员'
}

const roleLabel = computed(() => roleMap[userInfo.value.role] || userInfo.value.role || '用户')
const userCode = computed(() => userInfo.value.user_code || `U${String(userInfo.value.id || 0).padStart(6, '0')}`)

const profileCompletion = computed(() => {
  const items = [
    userInfo.value.username,
    userCode.value,
    form.value.nickname,
    form.value.email
  ]
  return Math.round(items.filter(Boolean).length / items.length * 100)
})

const completionTip = computed(() => {
  if (profileCompletion.value >= 100) return '资料已经完整，好友和主办方更容易识别你。'
  if (!form.value.nickname) return '补充昵称后，报名和好友系统里的展示会更自然。'
  if (!form.value.email) return '补充邮箱后，账号资料会更完整。'
  return '继续完善资料可以提升账号可信度。'
})

const registrationStats = computed(() => ({
  total: historyList.value.length,
  processing: historyList.value.filter(item => item.status === 'processing').length,
  ongoing: historyList.value.filter(item => item.status === 'ongoing').length,
  finished: historyList.value.filter(item => item.status === 'finished').length,
  hidden: historyList.value.filter(item => !item.showInProfile).length
}))

const filteredHistory = computed(() => {
  if (historyFilter.value === 'all') return historyList.value
  if (historyFilter.value === 'hidden') return historyList.value.filter(item => !item.showInProfile)
  return historyList.value.filter(item => item.status === historyFilter.value)
})

const statusText = (item) => ({
  processing: '审核中',
  ongoing: '参赛中',
  rejected: '未通过',
  finished: '已完赛'
}[item.status] || item.statusText || '未知状态')

const statusTagType = (status) => ({
  processing: 'warning',
  ongoing: 'success',
  rejected: 'danger',
  finished: 'info'
}[status] || 'info')

const copyUserCode = async () => {
  try {
    await navigator.clipboard.writeText(userCode.value)
    ElMessage.success('账号编号已复制')
  } catch (err) {
    ElMessage.warning('复制失败，请手动复制')
  }
}

const loadUserInfo = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/user/')
    if (res.data.success) {
      userInfo.value = res.data.data
      form.value = {
        nickname: res.data.data.nickname || '',
        email: res.data.data.email || ''
      }
    }
    const regRes = await request.get('/api/my_registrations/')
    if (regRes.data.success) {
      historyList.value = regRes.data.data || []
    }
  } catch (error) {
    ElMessage.error('用户信息加载失败')
  } finally {
    loading.value = false
  }
}

const handleUpdateInfo = async () => {
  saving.value = true
  try {
    const res = await request.post('/api/update_user/', {
      nickname: form.value.nickname,
      email: form.value.email
    })
    if (res.data.success) {
      ElMessage.success('资料已保存')
      await loadUserInfo()
    } else {
      ElMessage.warning(res.data.msg || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const cancelRegistration = async (registrationId) => {
  try {
    await ElMessageBox.confirm('确定取消这条报名记录吗？', '取消报名', {
      confirmButtonText: '确定取消',
      cancelButtonText: '保留报名',
      type: 'warning'
    })
    const res = await request.post('/api/cancel_registration/', {
      registration_id: registrationId
    })
    if (res.data.success) {
      ElMessage.success('已取消报名')
      await loadUserInfo()
    } else {
      ElMessage.error(res.data.msg || '取消失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('取消失败')
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
      ElMessage.success(item.showInProfile ? '记录已公开' : '记录已隐藏')
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
  width: 100%;
  max-width: var(--page-max-width);
  margin: 0 auto;
  padding: var(--page-padding);
}
.profile-header,
.info-card,
.completion-card,
.edit-card,
.history-card,
.stat-card {
  background: #fff;
  border: 1px solid #e5edf7;
  border-radius: 8px;
  box-shadow: 0 8px 22px rgba(34, 84, 137, 0.08);
}
.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: clamp(20px, 2vw, 28px);
  margin-bottom: 18px;
}
.eyebrow {
  margin: 0 0 6px;
  color: #1677ff;
  font-size: 13px;
  font-weight: 700;
}
.profile-header h2 {
  margin: 0;
  color: #12355b;
  font-size: clamp(24px, 2.4vw, 32px);
}
.profile-header p {
  margin: 8px 0 0;
  color: #61738a;
}
.profile-layout {
  display: grid;
  grid-template-columns: minmax(280px, 340px) minmax(0, 1fr);
  gap: 18px;
}
.profile-sidebar {
  display: grid;
  align-content: start;
  gap: 16px;
}
.info-card,
.completion-card,
.edit-card,
.history-card {
  padding: 22px;
}
.info-card {
  text-align: center;
}
.avatar {
  width: 82px;
  height: 82px;
  margin: 0 auto 16px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: #e6f4ff;
}
.avatar .el-icon {
  color: #1677ff;
  font-size: 40px;
}
.info-card h3,
.completion-card h3,
.edit-card h3,
.history-card h3 {
  margin: 0;
  color: #12355b;
}
.info-card p {
  margin: 8px 0 16px;
  color: #667085;
}
.code-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid #d8e7fb;
  border-radius: 8px;
  background: #f5f9ff;
  color: #1f4f89;
  font-weight: 700;
}
.card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
.card-title strong {
  color: #1677ff;
}
.completion-card p {
  margin: 12px 0 0;
  color: #667085;
  font-size: 13px;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.stat-card {
  padding: 16px;
}
.stat-card span {
  color: #66758a;
  font-size: 13px;
}
.stat-card strong {
  display: block;
  margin-top: 6px;
  color: #12355b;
  font-size: 28px;
}
.history-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}
.history-head p {
  margin: 6px 0 0;
  color: #667085;
}
.filter-select {
  width: 150px;
}
.timeline {
  display: grid;
  gap: 16px;
}
.timeline-item {
  position: relative;
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  gap: 12px;
}
.timeline-item.hidden {
  opacity: 0.58;
}
.timeline-dot {
  width: 12px;
  height: 12px;
  margin-top: 5px;
  border-radius: 50%;
  background: #1677ff;
  box-shadow: 0 0 0 4px #e6f4ff;
}
.timeline-dot.processing { background: #f59e0b; }
.timeline-dot.ongoing { background: #34a853; }
.timeline-dot.rejected { background: #ef4444; }
.timeline-dot.finished { background: #8c8c8c; }
.timeline-content {
  min-width: 0;
  padding: 14px;
  border: 1px solid #e8eef6;
  border-radius: 8px;
  background: #fbfdff;
}
.timeline-title {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}
.timeline-title h4 {
  margin: 0 0 8px;
  color: #1f2d3d;
}
.timeline-tags,
.action-area,
.timeline-time,
.timeline-desc {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.timeline-time {
  margin: 10px 0;
  color: #667085;
  font-size: 13px;
}
.timeline-desc {
  color: #394a5f;
  font-size: 13px;
}
.action-area {
  justify-content: flex-end;
}
@media (max-width: 980px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 760px) {
  .profile-header,
  .history-head,
  .timeline-title {
    align-items: flex-start;
    flex-direction: column;
  }
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .filter-select {
    width: 100%;
  }
}
@media (max-width: 520px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .action-area {
    justify-content: flex-start;
  }
}
</style>

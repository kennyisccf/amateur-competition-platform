<template>
  <div class="event-detail-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else class="detail-content">
      <div class="detail-card">
        <div v-if="competitionData.thumbnail_url" class="detail-cover">
          <img :src="competitionData.thumbnail_url" alt="赛事缩图" />
        </div>
        <div class="category-tag">
          <span>{{ competitionData.category }}</span>
          <span>{{ competitionData.type === 'PRIVATE' ? '私人赛' : '公开赛' }}</span>
        </div>
        <h1>{{ competitionData.title }}</h1>
        <div class="info-row">
          <el-icon><Tickets /></el-icon>
          <span>赛事编号: {{ competitionData.competition_no }}</span>
        </div>
        
        <div class="info-row">
          <el-icon><Clock /></el-icon>
          <span>报名时间: {{ formatDate(competitionData.start_time) }} - {{ formatDate(competitionData.end_time) }}</span>
        </div>
        <div class="info-row">
          <el-icon><Location /></el-icon>
          <span>比赛地点: {{ competitionData.location }}</span>
        </div>
        <div class="info-row">
          <el-icon><User /></el-icon>
          <span>主办方: {{ competitionData.organizer?.nickname || competitionData.organizer?.username }}</span>
        </div>
        <div class="info-row">
          <el-icon><UserFilled /></el-icon>
          <span>报名人数: {{ competitionData.current_participants }} / {{ competitionData.max_participants }}</span>
        </div>
        <div class="info-row">
          <el-icon><Medal /></el-icon>
          <span>赛制规则: {{ formatRule(competitionData) }}</span>
        </div>
        <div class="info-row invite-row" v-if="competitionData.type === 'PRIVATE' && competitionData.invite_code">
          <el-icon><Tickets /></el-icon>
          <span>私人邀请码: <strong>{{ competitionData.invite_code }}</strong></span>
        </div>

        <div class="section">
          <h3>赛事规则</h3>
          <div class="rule-content">
            <p>{{ competitionData.description }}</p>
          </div>
        </div>

        <div class="section">
          <h3>赛事奖励</h3>
          <div class="rule-content">
            <p>{{ competitionData.type === 'PRIVATE' ? '私人赛事不设置积分。' : competitionData.reward }}</p>
          </div>
        </div>

        <CompetitionBracket
          :competition="competitionData"
          :registrations="bracketRegistrations"
          :bracket-state="bracketState"
          readonly
        />
      </div>

      <div class="register-card">
        <h3>报名状态</h3>
        <el-tag :type="registrationPanel.type" effect="light">
          {{ registrationPanel.title }}
        </el-tag>
        <p class="register-tip">{{ registrationPanel.desc }}</p>
        <el-button v-if="showRegisterButton" type="primary" style="width: 100%" @click="goToRegister">
          我要报名
        </el-button>
        <el-button v-else-if="!isLoggedIn" type="primary" style="width: 100%" @click="router.push('/login')">
          登录后报名
        </el-button>
        <el-button
          v-if="currentRegistration?.canCancel"
          type="danger"
          plain
          style="width: 100%; margin-top: 10px; margin-left: 0"
          @click="cancelMyRegistration"
        >
          取消报名
        </el-button>
        <el-button
          v-if="currentRegistration"
          plain
          style="width: 100%; margin-top: 10px; margin-left: 0"
          @click="router.push('/profile')"
        >
          查看我的报名
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, Location, Medal, Tickets, User, UserFilled } from '@element-plus/icons-vue'
import request from '@/utils/request'
import CompetitionBracket from '@/components/CompetitionBracket.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const competitionData = ref({})
const bracketRegistrations = ref([])
const bracketState = ref({ drawSeed: Date.now(), winners: {} })
const currentRegistration = ref(null)
const userRole = localStorage.getItem('role')
const isLoggedIn = computed(() => Boolean(localStorage.getItem('user_id')))
const isFull = computed(() =>
  Number(competitionData.value.current_participants || 0) >= Number(competitionData.value.max_participants || 0)
)
const canCurrentRoleRegister = computed(() =>
  userRole === 'PLAYER' ||
  (
    userRole === 'ORGANIZER' &&
    competitionData.value.type === 'PRIVATE' &&
    competitionData.value.can_manage
  )
)
const showRegisterButton = computed(() =>
  isLoggedIn.value &&
  !currentRegistration.value &&
  competitionData.value.status === 1 &&
  !isFull.value &&
  canCurrentRoleRegister.value
)

const registrationPanel = computed(() => {
  if (currentRegistration.value) {
    return {
      title: currentRegistration.value.statusText,
      desc: currentRegistration.value.desc || getRegistrationDesc(currentRegistration.value.status),
      type: getRegistrationTagType(currentRegistration.value.status)
    }
  }
  if (!isLoggedIn.value) {
    return { title: '未登录', desc: '登录后可以提交报名申请，并在个人档案查看审核进度。', type: 'info' }
  }
  if (!canCurrentRoleRegister.value) {
    return { title: '不可报名', desc: '当前身份不能直接报名该赛事，可在管理端维护报名名单。', type: 'info' }
  }
  if (competitionData.value.status !== 1) {
    return { title: getCompetitionStatusText(competitionData.value.status), desc: '该赛事当前不接受新的报名申请。', type: 'info' }
  }
  if (isFull.value) {
    return { title: '名额已满', desc: '报名人数已达到上限，可联系主办方确认是否扩容。', type: 'warning' }
  }
  return { title: '可以报名', desc: '提交后由主办方或管理员审核，通过后会进入赛程名单。', type: 'success' }
})

const getRegistrationDesc = (status) => ({
  processing: '报名申请已提交，等待主办方审核。',
  ongoing: '报名已通过，请留意赛程安排。',
  rejected: '报名未通过，可查看审核备注或联系主办方。',
  finished: '赛事已完赛，成绩会展示在个人档案。'
}[status] || '报名记录已生成。')

const getRegistrationTagType = (status) => ({
  processing: 'warning',
  ongoing: 'success',
  rejected: 'danger',
  finished: 'info'
}[status] || 'info')

const getCompetitionStatusText = (status) => ({
  0: '待审核',
  1: '报名中',
  2: '进行中',
  3: '已结束',
  4: '已驳回'
}[status] || '状态未知')

// 日期格式化
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const formatRule = (item) => {
  if (!item) return '单淘汰'
  return item.competition_format_text || '单淘汰'
}

// 加载赛事详情
const loadCompetitionDetail = async () => {
  const competitionId = route.params.id || 1
  try {
    const res = await request.get(`/api/competition/${competitionId}/`)
    if (res.data.success) {
      competitionData.value = res.data.data
      await loadCompetitionBracket(competitionId)
      await loadMyRegistrationStatus(competitionId)
      loading.value = false
    } else {
      ElMessage.error('获取赛事详情失败')
    }
  } catch (err) {
    ElMessage.error('请求失败，请检查后端服务')
  }
}

const loadCompetitionBracket = async (competitionId) => {
  try {
    const res = await request.get(`/api/competitions/${competitionId}/bracket/`)
    if (res.data.success) {
      bracketRegistrations.value = res.data.registrations
      bracketState.value = res.data.bracket_state || { drawSeed: Date.now(), winners: {} }
    }
  } catch (err) {
    bracketRegistrations.value = []
  }
}

const loadMyRegistrationStatus = async (competitionId) => {
  currentRegistration.value = null
  if (!isLoggedIn.value) return
  try {
    const res = await request.get('/api/my_registrations/')
    if (res.data.success) {
      currentRegistration.value = (res.data.data || []).find(
        item => String(item.competitionId) === String(competitionId)
      ) || null
    }
  } catch (err) {
    currentRegistration.value = null
  }
}

// 跳转到报名页
const goToRegister = () => {
  router.push(`/event-register/${competitionData.value.id}`)
}

const cancelMyRegistration = async () => {
  if (!currentRegistration.value) return
  try {
    await ElMessageBox.confirm('确定取消该赛事报名吗？', '取消报名', {
      confirmButtonText: '确定取消',
      cancelButtonText: '再想想',
      type: 'warning'
    })
    const csrfRes = await request.get('/csrf/')
    const res = await request.post(
      '/api/cancel_registration/',
      { registration_id: currentRegistration.value.id },
      { headers: { 'X-CSRFToken': csrfRes.data.csrfToken } }
    )
    if (res.data.success) {
      ElMessage.success('已取消报名')
      await loadCompetitionDetail()
    } else {
      ElMessage.error(res.data.msg || '取消报名失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('取消报名失败')
    }
  }
}

onMounted(() => {
  loadCompetitionDetail()
})
</script>

<style scoped>
.event-detail-container {
  min-height: 100%;
  padding: var(--page-padding);
  background: #f5f7fa;
}
.loading {
  text-align: center;
  padding: 100px;
  font-size: 16px;
  color: #666;
}
.detail-content {
  width: 100%;
  max-width: min(1500px, 100%);
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1fr) clamp(280px, 23vw, 360px);
  gap: clamp(16px, 1.8vw, 24px);
  align-items: start;
}
.detail-card {
  min-width: 0;
  background: white;
  padding: clamp(18px, 1.8vw, 26px);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  overflow: hidden;
}
.detail-cover {
  width: 100%;
  height: clamp(160px, 20vw, 260px);
  margin: 0 0 18px;
  border-radius: 8px;
  overflow: hidden;
  background: #f3f7fb;
}
.detail-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center center;
}
.category-tag {
  margin-bottom: 12px;
}
.category-tag span {
  padding: 4px 10px;
  background: #e6f4ff;
  color: #1677ff;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
}
.detail-card h1 {
  margin: 0 0 20px;
  font-size: 24px;
}
.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #666;
}
.invite-row {
  color: #1f4f89;
}
.invite-row strong {
  padding: 2px 8px;
  background: #eef5ff;
  border: 1px solid #cfe0f5;
  border-radius: 6px;
  letter-spacing: 0.5px;
}
.section {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}
.section h3 {
  margin: 0 0 12px;
  font-size: 16px;
  color: #1677ff;
  border-left: 3px solid #1677ff;
  padding-left: 12px;
}
.rule-content p {
  margin: 8px 0;
  color: #333;
  line-height: 1.6;
}
.reward-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
  color: #333;
}
.reward-item .el-icon {
  color: #faad14;
}
.register-card {
  position: sticky;
  top: var(--page-padding);
  min-width: 0;
  background: white;
  padding: clamp(18px, 1.8vw, 24px);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  height: fit-content;
}
.register-card h3 {
  margin: 0 0 16px;
  font-size: 16px;
  border-left: 3px solid #1677ff;
  padding-left: 12px;
}
.register-tip {
  margin: 14px 0 18px;
  color: #667085;
  line-height: 1.6;
}

@media (max-width: 1100px) {
  .detail-content {
    grid-template-columns: 1fr;
  }

  .register-card {
    position: static;
    width: auto;
  }
}

@media (max-width: 768px) {
  .event-detail-container {
    padding: 16px;
  }

  .detail-card h1 {
    font-size: 22px;
  }
}
</style>

<template>
  <div class="event-detail-container">
    <div v-if="loading" class="loading-card">
      <el-skeleton :rows="9" animated />
    </div>

    <el-result
      v-else-if="loadError"
      class="error-card"
      icon="warning"
      title="赛事加载失败"
      :sub-title="loadError"
    >
      <template #extra>
        <el-button type="primary" @click="loadCompetitionDetail">重试</el-button>
        <el-button @click="router.push('/home')">返回赛事大厅</el-button>
      </template>
    </el-result>

    <div v-else class="detail-content">
      <main class="detail-card">
        <div class="detail-cover">
          <img :src="coverUrl" alt="赛事缩图" @error="handleCoverError" />
          <div class="cover-actions">
            <el-button
              circle
              :type="isFavorite ? 'warning' : 'default'"
              :icon="isFavorite ? StarFilled : Star"
              :title="isFavorite ? '取消收藏' : '收藏赛事'"
              @click="toggleFavorite"
            />
            <el-button circle :icon="CopyDocument" title="复制链接" @click="copyEventLink" />
          </div>
        </div>

        <div class="title-block">
          <div>
            <div class="category-tag">
              <span>{{ competitionData.category || '其他' }}</span>
              <span>{{ competitionData.type === 'PRIVATE' ? '私人赛' : '公开赛' }}</span>
              <span :class="['status-chip', getCompetitionStatusClass(competitionData.status)]">
                {{ getCompetitionStatusText(competitionData.status) }}
              </span>
            </div>
            <h1>{{ competitionData.title }}</h1>
          </div>
        </div>

        <section class="info-grid">
          <div class="info-row">
            <el-icon><Tickets /></el-icon>
            <div>
              <span>赛事编号</span>
              <strong>{{ competitionData.competition_no || '未编号' }}</strong>
            </div>
          </div>
          <div class="info-row">
            <el-icon><Clock /></el-icon>
            <div>
              <span>报名时间</span>
              <strong>{{ formatDate(competitionData.start_time) }} - {{ formatDate(competitionData.end_time) }}</strong>
            </div>
          </div>
          <div class="info-row">
            <el-icon><Location /></el-icon>
            <div>
              <span>比赛地点</span>
              <strong>{{ competitionData.location || '地点待定' }}</strong>
            </div>
          </div>
          <div class="info-row">
            <el-icon><User /></el-icon>
            <div>
              <span>主办方</span>
              <strong>{{ competitionData.organizer?.nickname || competitionData.organizer?.username || '-' }}</strong>
            </div>
          </div>
          <div class="info-row">
            <el-icon><UserFilled /></el-icon>
            <div>
              <span>报名人数</span>
              <strong>{{ competitionData.current_participants || 0 }} / {{ competitionData.max_participants || 0 }}</strong>
            </div>
          </div>
          <div class="info-row">
            <el-icon><Medal /></el-icon>
            <div>
              <span>赛制规则</span>
              <strong>{{ formatRule(competitionData) }}</strong>
            </div>
          </div>
        </section>

        <div class="invite-row" v-if="competitionData.type === 'PRIVATE' && competitionData.invite_code">
          <span>私人邀请码</span>
          <strong>{{ competitionData.invite_code }}</strong>
          <el-button size="small" text type="primary" :icon="CopyDocument" @click="copyInviteCode">
            复制
          </el-button>
        </div>

        <section class="section">
          <h3>赛事规则</h3>
          <div class="rule-content">
            <p>{{ competitionData.description || '主办方暂未填写详细规则。' }}</p>
          </div>
        </section>

        <section class="section">
          <h3>赛事奖励</h3>
          <div class="rule-content">
            <p>{{ rewardText }}</p>
          </div>
        </section>

        <CompetitionBracket
          :competition="competitionData"
          :registrations="bracketRegistrations"
          :bracket-state="bracketState"
          readonly
        />
      </main>

      <aside class="register-card">
        <h3>报名状态</h3>
        <el-tag :type="registrationPanel.type" effect="light">
          {{ registrationPanel.title }}
        </el-tag>
        <p class="register-tip">{{ registrationPanel.desc }}</p>

        <div class="capacity-box">
          <div class="capacity-line">
            <span>报名进度</span>
            <strong>{{ competitionData.current_participants || 0 }}/{{ competitionData.max_participants || 0 }}</strong>
          </div>
          <div class="capacity-track">
            <div class="capacity-fill" :style="{ width: `${participantPercent}%` }" />
          </div>
        </div>

        <el-button v-if="showRegisterButton" type="primary" class="full-action" @click="goToRegister">
          立即报名
        </el-button>
        <el-button v-else-if="!isLoggedIn" type="primary" class="full-action" @click="goToLogin">
          登录后报名
        </el-button>
        <el-button
          v-if="currentRegistration?.canCancel"
          type="danger"
          plain
          class="full-action secondary-action"
          @click="cancelMyRegistration"
        >
          取消报名
        </el-button>
        <el-button
          v-if="currentRegistration"
          plain
          class="full-action secondary-action"
          @click="router.push('/profile')"
        >
          查看我的报名
        </el-button>

        <div class="side-tools">
          <button type="button" @click="toggleFavorite">
            <el-icon>
              <StarFilled v-if="isFavorite" />
              <Star v-else />
            </el-icon>
            {{ isFavorite ? '已收藏' : '收藏赛事' }}
          </button>
          <button type="button" @click="copyEventLink">
            <el-icon><CopyDocument /></el-icon>
            复制链接
          </button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Clock,
  CopyDocument,
  Location,
  Medal,
  Star,
  StarFilled,
  Tickets,
  User,
  UserFilled
} from '@element-plus/icons-vue'
import request from '@/utils/request'
import CompetitionBracket from '@/components/CompetitionBracket.vue'

const FAVORITE_STORAGE_KEY = 'lesai_favorite_competitions'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const loadError = ref('')
const coverFailed = ref(false)
const competitionData = ref({})
const bracketRegistrations = ref([])
const bracketState = ref({ drawSeed: Date.now(), winners: {} })
const currentRegistration = ref(null)
const favoriteIds = ref([])
const userRole = localStorage.getItem('role')

const defaultThumbnails = {
  篮球: '/default-thumbnails/basketball.png',
  足球: '/default-thumbnails/football.png',
  羽毛球: '/default-thumbnails/badminton.png',
  网球: '/default-thumbnails/tennis.png',
  电竞: '/default-thumbnails/esports.png',
  棋牌桌游: '/default-thumbnails/boardgame.png'
}

const isLoggedIn = computed(() => Boolean(localStorage.getItem('user_id')))
const competitionId = computed(() => Number(competitionData.value.id || route.params.id || 0))
const isFavorite = computed(() => favoriteIds.value.includes(competitionId.value))
const isFull = computed(() =>
  Number(competitionData.value.current_participants || 0) >= Number(competitionData.value.max_participants || 0)
)
const participantPercent = computed(() => {
  const max = Number(competitionData.value.max_participants || 0)
  if (!max) return 0
  return Math.min(100, Math.round((Number(competitionData.value.current_participants || 0) / max) * 100))
})
const coverUrl = computed(() => {
  if (!coverFailed.value && competitionData.value.thumbnail_url) {
    return competitionData.value.thumbnail_url
  }
  return defaultThumbnails[competitionData.value.category] || '/default-thumbnails/badminton.png'
})
const rewardText = computed(() => {
  if (competitionData.value.type === 'PRIVATE') return '私人赛事不计入积分奖励。'
  return competitionData.value.reward || `完成赛事后可按排名获得积分奖励，最高 ${competitionData.value.reward_points || 0} 分。`
})
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
  Number(competitionData.value.status) === 1 &&
  !isFull.value &&
  canCurrentRoleRegister.value
)

const registrationPanel = computed(() => {
  if (currentRegistration.value) {
    return {
      title: currentRegistration.value.statusText || getRegistrationStatusText(currentRegistration.value.status),
      desc: currentRegistration.value.desc || getRegistrationDesc(currentRegistration.value.status),
      type: getRegistrationTagType(currentRegistration.value.status)
    }
  }
  if (!isLoggedIn.value) {
    return { title: '未登录', desc: '登录后可以提交报名，并在消息通知中查看审核结果。', type: 'info' }
  }
  if (!canCurrentRoleRegister.value) {
    return { title: '当前角色不可报名', desc: '管理员或无参赛权限的账号不能直接报名该赛事。', type: 'info' }
  }
  if (Number(competitionData.value.status) !== 1) {
    return { title: getCompetitionStatusText(competitionData.value.status), desc: '该赛事当前不在报名阶段。', type: 'info' }
  }
  if (isFull.value) {
    return { title: '名额已满', desc: '报名人数已达到上限，可以收藏赛事后等待主办方调整名额。', type: 'warning' }
  }
  return { title: '可报名', desc: '名额仍可用，点击下方按钮即可进入报名页面。', type: 'success' }
})

const loadFavorites = () => {
  try {
    favoriteIds.value = JSON.parse(localStorage.getItem(FAVORITE_STORAGE_KEY) || '[]')
      .map(item => Number(item))
      .filter(Boolean)
  } catch (err) {
    favoriteIds.value = []
  }
}

const saveFavorites = () => {
  localStorage.setItem(FAVORITE_STORAGE_KEY, JSON.stringify(favoriteIds.value))
}

const toggleFavorite = () => {
  const id = competitionId.value
  if (!id) return
  if (isFavorite.value) {
    favoriteIds.value = favoriteIds.value.filter(item => item !== id)
    ElMessage.success('已取消收藏')
  } else {
    favoriteIds.value = [id, ...favoriteIds.value]
    ElMessage.success('已收藏赛事')
  }
  saveFavorites()
}

const copyEventLink = async () => {
  const url = `${window.location.origin}/event-detail/${route.params.id}`
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('赛事链接已复制')
  } catch (err) {
    ElMessage.warning('复制失败，请手动复制链接')
  }
}

const copyInviteCode = async () => {
  try {
    await navigator.clipboard.writeText(competitionData.value.invite_code)
    ElMessage.success('邀请码已复制')
  } catch (err) {
    ElMessage.warning('复制失败，请手动复制邀请码')
  }
}

const getRegistrationDesc = (status) => ({
  processing: '报名已提交，等待主办方审核。',
  ongoing: '报名已通过，可以在赛事页面查看赛程。',
  rejected: '报名未通过，可查看审核备注后重新选择赛事。',
  finished: '赛事已完成，成绩会保留在个人档案中。'
}[status] || '报名状态已更新。')

const getRegistrationStatusText = (status) => ({
  processing: '审核中',
  ongoing: '已通过',
  rejected: '未通过',
  finished: '已完赛'
}[status] || '已报名')

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
  4: '未通过'
}[Number(status)] || '未知状态')

const getCompetitionStatusClass = (status) => ({
  0: 'status-pending',
  1: 'status-open',
  2: 'status-running',
  3: 'status-ended',
  4: 'status-rejected'
}[Number(status)] || 'status-pending')

const formatDate = (dateStr) => {
  if (!dateStr) return '待定'
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return '待定'
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const formatRule = (item) => item?.competition_format_text || '单淘汰'

const loadCompetitionDetail = async () => {
  const id = route.params.id || 1
  loading.value = true
  loadError.value = ''
  coverFailed.value = false
  try {
    const res = await request.get(`/api/competition/${id}/`)
    if (res.data.success) {
      competitionData.value = res.data.data
      await loadCompetitionBracket(id)
      await loadMyRegistrationStatus(id)
    } else {
      loadError.value = res.data.msg || '未能获取赛事详情。'
    }
  } catch (err) {
    loadError.value = '网络异常，请稍后重试。'
  } finally {
    loading.value = false
  }
}

const loadCompetitionBracket = async (id) => {
  try {
    const res = await request.get(`/api/competitions/${id}/bracket/`)
    if (res.data.success) {
      bracketRegistrations.value = res.data.registrations || []
      bracketState.value = res.data.bracket_state || { drawSeed: Date.now(), winners: {} }
    }
  } catch (err) {
    bracketRegistrations.value = []
  }
}

const loadMyRegistrationStatus = async (id) => {
  currentRegistration.value = null
  if (!isLoggedIn.value) return
  try {
    const res = await request.get('/api/my_registrations/')
    if (res.data.success) {
      currentRegistration.value = (res.data.data || []).find(
        item => String(item.competitionId) === String(id)
      ) || null
    }
  } catch (err) {
    currentRegistration.value = null
  }
}

const goToRegister = () => {
  router.push(`/event-register/${competitionData.value.id}`)
}

const goToLogin = () => {
  router.push({ path: '/login', query: { redirect: route.fullPath } })
}

const handleCoverError = () => {
  coverFailed.value = true
}

const cancelMyRegistration = async () => {
  if (!currentRegistration.value) return
  try {
    await ElMessageBox.confirm('确定取消这次报名吗？', '取消报名', {
      confirmButtonText: '确定取消',
      cancelButtonText: '保留报名',
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
      ElMessage.error(res.data.msg || '取消失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('取消失败')
    }
  }
}

onMounted(() => {
  loadFavorites()
  loadCompetitionDetail()
})
</script>

<style scoped>
.event-detail-container {
  min-height: 100%;
  padding: var(--page-padding);
  background: #f5f7fa;
}
.loading-card,
.error-card {
  max-width: min(900px, 100%);
  margin: 0 auto;
  padding: clamp(18px, 2vw, 28px);
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 22px rgba(34, 84, 137, 0.08);
}
.detail-content {
  width: 100%;
  max-width: min(1500px, 100%);
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1fr) clamp(290px, 23vw, 360px);
  gap: clamp(16px, 1.8vw, 24px);
  align-items: start;
}
.detail-card,
.register-card {
  min-width: 0;
  background: white;
  border: 1px solid #e5edf7;
  border-radius: 8px;
  box-shadow: 0 8px 22px rgba(34, 84, 137, 0.08);
}
.detail-card {
  padding: clamp(18px, 1.8vw, 26px);
  overflow: hidden;
}
.detail-cover {
  position: relative;
  width: 100%;
  height: clamp(170px, 22vw, 300px);
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
.cover-actions {
  position: absolute;
  top: 14px;
  right: 14px;
  display: flex;
  gap: 8px;
}
.title-block {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}
.category-tag {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}
.category-tag span {
  padding: 4px 10px;
  background: #e6f4ff;
  color: #1677ff;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 700;
}
.status-chip.status-open {
  background: #f0f9eb;
  color: #389e0d;
}
.status-chip.status-running {
  background: #e8f0ff;
  color: #1d4ed8;
}
.status-chip.status-ended {
  background: #f2f4f7;
  color: #667085;
}
.status-chip.status-rejected {
  background: #fff2f0;
  color: #cf1322;
}
.status-chip.status-pending {
  background: #fff7e6;
  color: #d46b08;
}
.detail-card h1 {
  margin: 0;
  color: #12355b;
  font-size: clamp(24px, 2.4vw, 34px);
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}
.info-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  border: 1px solid #e8eef6;
  border-radius: 8px;
  background: #fbfdff;
}
.info-row .el-icon {
  margin-top: 2px;
  color: #1677ff;
}
.info-row span {
  display: block;
  margin-bottom: 3px;
  color: #667085;
  font-size: 12px;
}
.info-row strong {
  color: #24364f;
  font-weight: 700;
}
.invite-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px;
  border: 1px solid #cfe0f5;
  border-radius: 8px;
  background: #eef5ff;
  color: #1f4f89;
}
.invite-row strong {
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
  line-height: 1.7;
}
.register-card {
  position: sticky;
  top: var(--page-padding);
  padding: clamp(18px, 1.8vw, 24px);
  height: fit-content;
}
.register-card h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #12355b;
  border-left: 3px solid #1677ff;
  padding-left: 12px;
}
.register-tip {
  margin: 14px 0 18px;
  color: #667085;
  line-height: 1.6;
}
.capacity-box {
  margin-bottom: 18px;
}
.capacity-line {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #667085;
  font-size: 13px;
  margin-bottom: 8px;
}
.capacity-line strong {
  color: #10233f;
}
.capacity-track {
  height: 8px;
  border-radius: 999px;
  background: #edf2f7;
  overflow: hidden;
}
.capacity-fill {
  height: 100%;
  border-radius: inherit;
  background: #1677ff;
  transition: width 0.25s ease;
}
.full-action {
  width: 100%;
}
.secondary-action {
  margin-top: 10px;
  margin-left: 0;
}
.side-tools {
  display: grid;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eef2f7;
}
.side-tools button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 36px;
  border: 1px solid #d8e7fb;
  border-radius: 8px;
  color: #1f4f89;
  background: #f5f9ff;
  cursor: pointer;
}
@media (max-width: 1100px) {
  .detail-content {
    grid-template-columns: 1fr;
  }
  .register-card {
    position: static;
  }
}
@media (max-width: 820px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 768px) {
  .event-detail-container {
    padding: 16px;
  }
}
</style>

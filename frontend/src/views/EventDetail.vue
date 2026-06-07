<template>
  <div class="event-detail-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else class="detail-content">
      <div class="detail-card">
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

      <div class="register-card" v-if="canRegister">
        <h3>立即报名</h3>
        <el-button type="primary" style="width: 100%" @click="goToRegister">
          我要报名
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Clock, Location, Medal, Tickets, User, UserFilled } from '@element-plus/icons-vue'
import request from '@/utils/request'
import CompetitionBracket from '@/components/CompetitionBracket.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const competitionData = ref({})
const bracketRegistrations = ref([])
const bracketState = ref({ drawSeed: Date.now(), winners: {} })
const userRole = localStorage.getItem('role')
const canRegister = computed(() =>
  competitionData.value.status === 1 && (
    ['PLAYER', 'ADMIN'].includes(userRole) ||
    (
      userRole === 'ORGANIZER' &&
      competitionData.value.type === 'PRIVATE' &&
      competitionData.value.can_manage
    )
  )
)

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
      loading.value = false
    } else {
      ElMessage.error('获取赛事详情失败')
    }
  } catch (err) {
    ElMessage.error('请求失败，请检查后端服务')
    console.error(err)
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

// 跳转到报名页
const goToRegister = () => {
  router.push(`/event-register/${competitionData.value.id}`)
}

onMounted(() => {
  loadCompetitionDetail()
})
</script>

<style scoped>
.event-detail-container {
  padding: 24px;
}
.loading {
  text-align: center;
  padding: 100px;
  font-size: 16px;
  color: #666;
}
.detail-content {
  display: flex;
  gap: 24px;
}
.detail-card {
  flex: 2;
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
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
  flex: 1;
  background: white;
  padding: 24px;
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
</style>

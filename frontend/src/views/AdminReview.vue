<template>
  <div class="admin-container">
    <div style="text-align: right; color: #666; font-size: 14px; margin-bottom: 24px;">权限角色: 管理员</div>
    
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">全站注册用户</div>
        <div class="stat-value">514</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">进行中赛事总量</div>
        <div class="stat-value">5</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">待审核主办方资质</div>
        <div class="stat-value" style="color: #faad14">1</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">风控被举报内容</div>
        <div class="stat-value" style="color: #f5222d">1</div>
      </div>
    </div>

    <!-- 待审核赛事 -->
    <div class="review-card">
      <h3>主办方资质准入终审</h3>
      <el-table :data="pendingList" border>
        <el-table-column prop="title" label="申请主体名称" />
        <el-table-column prop="type" label="主体类型" />
        <el-table-column prop="file" label="证明附件材料" />
        <el-table-column label="操作">
          <template #default="scope">
            <el-button size="small" type="success" @click="handleReview(scope.row.id, 1)">批准入驻</el-button>
            <el-button size="small" type="danger" @click="handleReview(scope.row.id, 4)">拒绝</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 风控 -->
    <div class="risk-card">
      <h3>全站赛事违规内容突击风控</h3>
      <el-table :data="riskList" border>
        <el-table-column prop="eventName" label="被举报赛事名称" />
        <el-table-column prop="organizer" label="所属主办方" />
        <el-table-column prop="reason" label="触发违规风控原因" />
        <el-table-column label="操作">
          <template #default>
            <el-button size="small" type="danger">强制下架并封禁</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const pendingList = ref([])
const riskList = ref([
  {
    eventName: '恶意炸房测试娱乐赛',
    organizer: '非实名匿名个体',
    reason: '涉嫌虚假奖金宣传与外挂滋生'
  }
])

const loadPendingCompetitions = async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/admin/pending_competitions/')
    if (res.data.success) {
      pendingList.value = res.data.competitions
    }
  } catch (err) {
    ElMessage.error('加载审核列表失败')
    console.error(err)
  }
}

const handleReview = async (id, status) => {
  try {
    const csrfRes = await axios.get('http://localhost:8000/csrf/')
    const csrfToken = csrfRes.data.csrfToken

    await axios.post(
      'http://localhost:8000/api/admin/review_competition/',
      { competition_id: id, status },
      { headers: { 'X-CSRFToken': csrfToken } }
    )

    ElMessage.success('审核完成')
    loadPendingCompetitions()
  } catch (err) {
    ElMessage.error('审核失败')
    console.error(err)
  }
}

onMounted(() => {
  loadPendingCompetitions()
})
</script>

<style scoped>
.admin-container {
  padding: 24px;
}
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}
.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}
.review-card, .risk-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  margin-bottom: 24px;
}
.review-card h3, .risk-card h3 {
  margin: 0 0 20px;
  font-size: 16px;
  color: #333;
  border-left: 3px solid #1677ff;
  padding-left: 12px;
}
</style>
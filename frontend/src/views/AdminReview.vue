<template>
  <div class="admin-container">
    <div style="text-align: right; color: #666; font-size: 14px; margin-bottom: 24px;">权限角色: 平台管理员</div>
    
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">全站注册用户</div>
        <div class="stat-value">{{ stats.totalUsers }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">进行中赛事总量</div>
        <div class="stat-value">{{ stats.runningEvents }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">待审核赛事</div>
        <div class="stat-value" style="color: #faad14">{{ stats.pendingCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">风控被举报内容</div>
        <div class="stat-value" style="color: #f5222d">{{ stats.riskCount }}</div>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <!-- 赛事审核 -->
      <el-tab-pane label="赛事审核" name="review">
        <div class="review-card">
          <h3>主办方资质准入终审</h3>
          <el-table :data="pendingList" border v-loading="loading">
            <el-table-column prop="id" label="赛事ID" width="80" />
            <el-table-column prop="title" label="赛事名称" min-width="180" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="organizer.nickname" label="主办方" width="120" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" type="success" @click="handleApprove(scope.row)">批准</el-button>
                <el-button size="small" type="danger" @click="handleReject(scope.row)">驳回</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <div class="user-card">
          <h3>全站用户管理</h3>
          <el-table :data="userList" border v-loading="loading">
            <el-table-column prop="user_id" label="用户ID" width="80" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="role" label="角色" width="100" />
            <el-table-column prop="is_active" label="状态" width="100" :formatter="formatUserStatus" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button 
                  size="small" 
                  :type="scope.row.is_active ? 'danger' : 'success'"
                  @click="handleToggleUser(scope.row)"
                >
                  {{ scope.row.is_active ? '封禁' : '解封' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 审核记录 -->
      <el-tab-pane label="审核记录" name="records">
        <div class="record-card">
          <h3>历史审核记录</h3>
          <el-table :data="recordList" border v-loading="loading">
            <el-table-column prop="record_id" label="记录ID" width="100" />
            <el-table-column prop="competition_id" label="赛事ID" width="100" />
            <el-table-column prop="action" label="操作" width="120" />
            <el-table-column prop="created_at" label="时间" min-width="180" :formatter="formatTime" />
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElInput } from 'element-plus'

const loading = ref(false)
const activeTab = ref('review')
const stats = ref({
  totalUsers: 0,
  runningEvents: 0,
  pendingCount: 0,
  riskCount: 1
})
const pendingList = ref([])
const userList = ref([])
const recordList = ref([])

// 获取请求头
const getHeaders = async () => {
  const token = localStorage.getItem('token')
  const csrfRes = await axios.get('http://localhost:8000/csrf/')
  return {
    'Authorization': `Bearer ${token}`,
    'X-CSRFToken': csrfRes.data.csrfToken
  }
}

// 格式化状态
const formatUserStatus = (row) => row.is_active ? '正常' : '已封禁'
const formatTime = (row) => new Date(row.created_at).toLocaleString()

// 加载待审核赛事
const loadPending = async () => {
  loading.value = true
  try {
    const headers = await getHeaders()
    const res = await axios.get('http://localhost:8000/api/admin/pending_competitions/', { headers })
    if (res.data.success) {
      pendingList.value = res.data.competitions
      stats.value.pendingCount = res.data.competitions.length
    }
  } catch (err) {
    ElMessage.error('加载失败')
  } finally { loading.value = false }
}

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    const headers = await getHeaders()
    const res = await axios.get('http://localhost:8000/api/admin/users/', { headers })
    if (res.data.success) {
      userList.value = res.data.users
      stats.value.totalUsers = res.data.users.length
    }
  } catch (err) {
    ElMessage.error('加载失败')
  } finally { loading.value = false }
}

// 加载审核记录
const loadRecords = async () => {
  loading.value = true
  try {
    const headers = await getHeaders()
    const res = await axios.get('http://localhost:8000/api/admin/audit_records/', { headers })
    if (res.data.success) {
      recordList.value = res.data.records
    }
  } catch (err) {
    ElMessage.error('加载失败')
  } finally { loading.value = false }
}

// 审核操作
const handleApprove = async (row) => {
  try {
    const headers = await getHeaders()
    const res = await axios.post(
      'http://localhost:8000/api/admin/review_competition/',
      { competition_id: row.id, status: 1 },
      { headers }
    )
    ElMessage.success('审核通过')
    loadPending()
  } catch (err) { ElMessage.error('操作失败') }
}
const handleReject = async (row) => {
  const reason = await ElInput.prompt('请输入驳回原因')
  if (!reason) return
  try {
    const headers = await getHeaders()
    const res = await axios.post(
      'http://localhost:8000/api/admin/review_competition/',
      { competition_id: row.id, status: 4, reason },
      { headers }
    )
    ElMessage.success('已驳回')
    loadPending()
  } catch (err) { ElMessage.error('操作失败') }
}

// 封禁/解封用户
const handleToggleUser = async (row) => {
  try {
    const headers = await getHeaders()
    const res = await axios.put(
      `http://localhost:8000/api/admin/users/${row.user_id}/status/`,
      { is_active: !row.is_active },
      { headers }
    )
    ElMessage.success('操作成功')
    loadUsers()
  } catch (err) { ElMessage.error('操作失败') }
}

onMounted(() => {
  loadPending()
  loadUsers()
  loadRecords()
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
.review-card, .user-card, .record-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.review-card h3, .user-card h3, .record-card h3 {
  margin: 0 0 20px;
  font-size: 16px;
  color: #333;
  border-left: 3px solid #1677ff;
  padding-left: 12px;
}
</style>
<template>
  <div class="registration-manage-container">
    <h2>赛事报名管理</h2>
    <div class="filter-bar">
      <el-select 
        v-model="selectedCompetitionId" 
        placeholder="请选择要查看的赛事" 
        style="width: 300px;"
        @change="fetchRegistrations"
      >
        <el-option 
          v-for="comp in myCompetitions" 
          :key="comp.id" 
          :label="comp.title" 
          :value="comp.id"
        />
      </el-select>
    </div>

    <div v-if="loading" class="loading">加载报名数据中...</div>
    <div v-else-if="registrations.length === 0 && selectedCompetitionId" class="empty-tip">
      该赛事暂无报名信息
    </div>
    <el-table 
      v-else 
      :data="registrations" 
      border 
      style="width: 100%; margin-top: 20px;"
    >
      <el-table-column prop="registration_id" label="报名ID" width="100" />
      <el-table-column prop="player_id" label="选手ID" width="100" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="nickname" label="选手昵称" min-width="120" />
      <el-table-column 
        prop="status" 
        label="报名状态" 
        width="120"
        :formatter="formatStatus"
      />
      <el-table-column 
        prop="registration_time" 
        label="报名时间" 
        min-width="180"
        :formatter="formatTime"
      />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const myCompetitions = ref([])
const selectedCompetitionId = ref('')
const registrations = ref([])

// 获取请求头
const getHeaders = async () => {
  const token = localStorage.getItem('token')
  const csrfRes = await axios.get('http://localhost:8000/csrf/')
  return {
    'Authorization': `Bearer ${token}`,
    'X-CSRFToken': csrfRes.data.csrfToken
  }
}

const formatStatus = (row) => {
  const statusMap = {
    1: '待审核',
    2: '报名成功',
    3: '报名驳回'
  }
  return statusMap[row.status] || '未知状态'
}
const formatTime = (row) => {
  if (!row.registration_time) return '-'
  return new Date(row.registration_time).toLocaleString()
}

// 拉取主办方自己的赛事列表
const fetchMyCompetitions = async () => {
  const organizerId = localStorage.getItem('user_id')
  if (!organizerId) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const headers = await getHeaders()
    const res = await axios.get(`http://localhost:8000/api/my_competitions/?organizer_id=${organizerId}`, { headers })
    if (res.data.success) {
      myCompetitions.value = res.data.competitions
    }
  } catch (err) {
    ElMessage.error('网络请求失败')
  }
}

// 拉取报名列表
const fetchRegistrations = async () => {
  if (!selectedCompetitionId.value) return
  loading.value = true
  try {
    const headers = await getHeaders()
    const res = await axios.get(`http://localhost:8000/api/competitions/${selectedCompetitionId.value}/registrations/`, { headers })
    if (res.data.success) {
      registrations.value = res.registrations
    }
  } catch (err) {
    ElMessage.error('网络请求失败')
  } finally { loading.value = false }
}

onMounted(() => {
  fetchMyCompetitions()
})
</script>

<style scoped>
.registration-manage-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}
.registration-manage-container h2 {
  margin: 0 0 20px;
  font-size: 20px;
}
.filter-bar {
  margin-bottom: 20px;
}
.loading {
  text-align: center;
  padding: 50px;
  color: #666;
}
.empty-tip {
  text-align: center;
  padding: 50px;
  color: #999;
  font-size: 14px;
}
</style>
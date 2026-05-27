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
import { get } from '@/utils/request' // 复用之前的请求封装
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const myCompetitions = ref([]) // 主办方自己创建的赛事列表
const selectedCompetitionId = ref('') // 选中的赛事ID
const registrations = ref([]) // 报名列表数据

// 格式化报名状态
const formatStatus = (row) => {
  const statusMap = {
    1: '待审核',
    2: '报名成功',
    3: '报名驳回'
  }
  return statusMap[row.status] || '未知状态'
}

// 格式化时间
const formatTime = (row) => {
  if (!row.registration_time) return '-'
  return new Date(row.registration_time).toLocaleString()
}

// 拉取主办方自己的赛事列表（对接 /api/my_competitions/）
const fetchMyCompetitions = async () => {
  const organizerId = localStorage.getItem('user_id')
  if (!organizerId) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const res = await get(`/api/my_competitions/`, { organizer_id: organizerId })
    if (res.success) {
      myCompetitions.value = res.competitions
    } else {
      ElMessage.error(res.msg || '获取赛事列表失败')
    }
  } catch (err) {
    ElMessage.error('网络请求失败')
    console.error(err)
  }
}

// 拉取选中赛事的报名列表（对接 /api/competitions/<id>/registrations/）
const fetchRegistrations = async () => {
  if (!selectedCompetitionId.value) return

  loading.value = true
  try {
    const res = await get(`/api/competitions/${selectedCompetitionId.value}/registrations/`)
    if (res.success) {
      registrations.value = res.registrations
    } else {
      ElMessage.error(res.msg || '获取报名信息失败')
      registrations.value = []
    }
  } catch (err) {
    ElMessage.error('网络请求失败')
    registrations.value = []
  } finally {
    loading.value = false
  }
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
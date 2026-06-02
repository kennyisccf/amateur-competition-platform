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
    <el-table  v-else  :data="registrations"  border  style="width: 100%; margin-top: 20px;">
      <el-table-column prop="registration_id" label="报名ID" width="100" />
      <el-table-column prop="player_id" label="选手ID" width="100" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="nickname" label="选手昵称" min-width="120" />
      <el-table-column label="报名状态" width="120">
        <template #default="scope">
          <el-tag type="warning" v-if="scope.row.review_status===0">待审核</el-tag>
          <el-tag type="success" v-else-if="scope.row.review_status===1">已通过</el-tag>
          <el-tag type="danger" v-else>已驳回</el-tag>
        
        </template>
      </el-table-column>
      <el-table-column  prop="registration_time"  label="报名时间"  min-width="180" :formatter="formatTime"/>

      <el-table-column label="操作" width="260">
        <template #default="scope">
          <el-button v-if="scope.row.review_status===0" size="small" type="success" @click="approveRegistration(scope.row.registration_id)">
            通过
          </el-button>
          <el-button v-if="scope.row.review_status===0" size="small" type="danger" @click="rejectRegistration(scope.row)">
            驳回
          </el-button>
          <el-button size="small" @click="showDetail(scope.row)">
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
  <el-dialog v-model="detailDialogVisible" title="报名详情" width="500px">
    <el-descriptions :column="1" border>
      <el-descriptions-item label="报名ID">
        {{ currentRegistration.registration_id }}
      </el-descriptions-item>
      <el-descriptions-item label="用户名">
        {{ currentRegistration.username }}
      </el-descriptions-item>
      <el-descriptions-item label="昵称">
        {{ currentRegistration.nickname }}
      </el-descriptions-item>
      <el-descriptions-item label="选手ID">
        {{ currentRegistration.player_id }}
      </el-descriptions-item>
      <el-descriptions-item label="报名状态">
        <el-tag v-if="currentRegistration.review_status===0" type="warning">待审核</el-tag>
        <el-tag v-else-if="currentRegistration.review_status===1" type="success">已通过</el-tag>
        <el-tag v-else type="danger">已驳回</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="报名时间">
        {{ formatTime(currentRegistration) }}
      </el-descriptions-item>
      <el-descriptions-item label="审核备注">
        {{ currentRegistration.audit_remark || '暂无' }}
      </el-descriptions-item>
    </el-descriptions>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const myCompetitions = ref([])
const selectedCompetitionId = ref('')
const registrations = ref([])

const detailDialogVisible = ref(false)
const currentRegistration = ref({})

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
    0: '待审核',
    1: '报名成功',
    2: '报名驳回'
  }
  return statusMap[row.review_status] || '未知状态'
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
      registrations.value = res.data.registrations
    }
  } catch (err) {
    ElMessage.error('网络请求失败')
  } finally { loading.value = false }
}
const approveRegistration = async (id)=>{
  try{
    const res = await axios.post(
      'http://localhost:8000/api/approve_registration/',
      {
        registration_id:id
      },
      {
        withCredentials:true
      }
    )
    if(res.data.success){
      ElMessage.success('审核通过')
      fetchRegistrations()
    }
  }catch(err){
    ElMessage.error('审核失败')
  }
}
const rejectRegistration = async(row)=>{
  try{
    const remark = await ElMessageBox.prompt(
      '请输入驳回原因',
      '报名驳回'
    )
    const res = await axios.post(
      'http://localhost:8000/api/reject_registration/',
      {
        registration_id:row.registration_id,
        remark:remark.value
      },
      {
        withCredentials:true
      }
    )
    if(res.data.success){
      ElMessage.success('已驳回')
      fetchRegistrations()
    }

  }catch(err){

  }
}
const showDetail = (row) => {
  currentRegistration.value = row
  detailDialogVisible.value = true
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
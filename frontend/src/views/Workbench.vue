<template>
  <div class="workbench-container">
    <h2>赛事工作台</h2>
    
    <!-- <el-table :data="competitions" border> -->
      <!-- <el-table-column prop="title" label="赛事名称" /> -->
      <!-- <el-table-column prop="category" label="分类" /> -->
      <!-- <el-table-column prop="location" label="地点" /> -->
      <!-- <el-table-column prop="current_participants" label="报名人数" /> -->
      <!-- <el-table-column prop="status" label="状态" /> -->
      <!-- <el-table-column label="操作"> -->
        <!-- <template #default="scope"> -->
          <!-- <el-button size="small" @click="goToDetail(scope.row.id)">查看</el-button> -->
          <!-- <el-button size="small" @click="goToEdit(scope.row.id)">修改</el-button> -->
          <!-- <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button> -->
          <!-- <el-button size="small" @click="goToRegistration(scope.row.id)">报名管理</el-button> -->
        <!-- </template> -->
      <!-- </el-table-column> -->
    <!-- </el-table> -->
    <el-table :data="competitions" border stripe style="width: 100%"> 
      <el-table-column prop="title" label="赛事名称" min-width="220"/>
      <el-table-column prop="category" label="分类" width="100"/>
      <el-table-column prop="location" label="地点" width="160"/>
      <el-table-column label="状态" width="90">
        <template #default="scope">
          <el-tag :type="statusMap[scope.row.status]?.type">{{ statusMap[scope.row.status]?.text }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="报名人数" width="120">
        <template #default="scope">{{ scope.row.current_participants }}/{{ scope.row.max_participants }}</template>
      </el-table-column>
      <el-table-column label="比赛时间" width="180">
        <template #default="scope">
          {{new Date(scope.row.start_time) .toLocaleDateString()}}
        </template>
      </el-table-column><el-table-column label="驳回原因" min-width="190">
        <template #default="scope">
          <span v-if="scope.row.status === 4" style="color:#f56c6c">{{ scope.row.reject_reason }}</span>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" min-width="300" fixed="right">
        <template #default="scope">
          <el-space wrap>
            <el-button size="small" type="primary" @click="goToDetail(scope.row.id)">查看</el-button>
            <el-button size="small" type="primary" @click="goToEdit(scope.row.id)">修改</el-button>         
            <el-button size="small" type="primary" @click="goToRegistration(scope.row.id)">报名管理</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </el-space>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
const statusMap = {
  0: {text: '待审核', type: 'warning'},
  1: {text: '报名中', type: 'success'},
  2: {text: '进行中', type: 'primary'},
  3: {text: '已结束', type: 'info'},
  4: {text: '已驳回', type: 'danger'}
}
const router = useRouter()
const competitions = ref([])

// 获取请求头
const getHeaders = async () => {
  const token = localStorage.getItem('token')
  const csrfRes = await axios.get('http://localhost:8000/csrf/')
  return {
    'Authorization': `Bearer ${token}`,
    'X-CSRFToken': csrfRes.data.csrfToken
  }
}

const loadMyCompetitions = async () => {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    router.push('/login')
    return
  }

  try {
    const headers = await getHeaders()
    const res = await axios.get(`http://localhost:8000/api/my_competitions/?organizer_id=${userId}`, { headers })
    if (res.data.success) {
      competitions.value = res.data.competitions
    }
  } catch (err) {
    ElMessage.error('加载赛事失败')
    console.error(err)
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个赛事吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const headers = await getHeaders()
    await axios.delete(`http://localhost:8000/api/competitions/${id}/delete/`, { headers })

    ElMessage.success('删除成功')
    loadMyCompetitions()
  } catch (err) {
    console.error(err)
  }
}

const goToDetail = (id) => router.push(`/event-detail/${id}`)
const goToEdit = (id) => router.push(`/competition-edit/${id}`)
const goToRegistration = (id) => {
  router.push('/registration-manage')
  // 可以把选中的赛事ID存下来，让报名管理页自动选中
  localStorage.setItem('selected_competition', id)
}

onMounted(() => {
  loadMyCompetitions()
})
</script>

<style scoped>
.workbench-container {
  padding: 24px;
}

.workbench-container h2 {
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.el-table {
  border-radius: 8px;
  overflow: hidden;
}
</style>
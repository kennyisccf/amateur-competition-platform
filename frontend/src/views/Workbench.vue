<template>
  <div class="workbench-container">
    <h2>赛事工作台</h2>
    
    <el-table :data="competitions" border>
      <el-table-column prop="title" label="赛事名称" />
      <el-table-column prop="category" label="分类" />
      <el-table-column prop="location" label="地点" />
      <el-table-column prop="current_participants" label="报名人数" />
      <el-table-column prop="status" label="状态" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="goToDetail(scope.row.id)">查看</el-button>
          <el-button size="small" @click="goToEdit(scope.row.id)">修改</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          <el-button size="small" @click="goToRegistration(scope.row.id)">报名管理</el-button>
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
  margin: 0 0 24px;
}
</style>
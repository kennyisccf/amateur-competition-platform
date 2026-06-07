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
      <el-table-column prop="competition_no" label="编号" width="130"/>
      <el-table-column prop="title" label="赛事名称" min-width="220"/>
      <el-table-column prop="category" label="分类" width="100"/>
      <el-table-column prop="location" label="地点" width="160"/>
      <el-table-column label="赛制" min-width="150">
        <template #default="scope">{{ formatRule(scope.row) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="scope">
          <el-tag :type="statusMap[scope.row.status]?.type">{{ statusMap[scope.row.status]?.text }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="报名人数" width="120">
        <template #default="scope">{{ scope.row.current_participants }}/{{ scope.row.max_participants }}</template>
      </el-table-column>
      <el-table-column label="邀请码" width="130">
        <template #default="scope">
          <el-tag v-if="scope.row.type === 'PRIVATE'">{{ scope.row.invite_code }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="比赛时间" width="180">
        <template #default="scope">
          {{new Date(scope.row.start_time) .toLocaleDateString()}}
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="驳回原因" min-width="200">
        <template #default="scope">
          <span v-if="scope.row.status === 4" style="color:#f56c6c">{{ scope.row.reject_reason }}</span>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" min-width="430" fixed="right">
        <template #default="scope">
          <el-space wrap>
            <el-button size="small" type="primary" @click="goToDetail(scope.row.id)">查看</el-button>
            <el-button size="small" type="primary" @click="goToEdit(scope.row.id)">修改</el-button>         
            <el-button size="small" type="primary" @click="goToRegistration(scope.row.id)">报名管理</el-button>
            <el-button v-if="scope.row.status === 1" size="small" type="success" @click="handleStatusChange(scope.row, 2)">开始赛事</el-button>
            <el-button v-if="[1, 2].includes(scope.row.status)" size="small" type="warning" @click="handleStatusChange(scope.row, 3)">结束赛事</el-button>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
const statusMap = {
  0: {text: '待审核', type: 'warning'},
  1: {text: '报名中', type: 'success'},
  2: {text: '进行中', type: 'primary'},
  3: {text: '已结束', type: 'info'},
  4: {text: '已驳回', type: 'danger'}
}
const router = useRouter()
const competitions = ref([])

const formatRule = (item) => {
  return item.competition_format_text || '单淘汰'
}

const formatDateTime = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

// 获取请求头
const getHeaders = async () => {
  const csrfRes = await request.get('/csrf/')
  return {
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
    const res = await request.get('/api/my_competitions/?scope=managed', { headers })
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
    const res = await request.delete(`/api/competitions/${id}/delete/`, { headers })
    if (res.data.success) {
      ElMessage.success('删除成功')
      loadMyCompetitions()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (err) {
    console.error(err)
  }
}

const handleStatusChange = async (competition, status) => {
  const action = status === 2 ? '开始' : '结束'
  try {
    await ElMessageBox.confirm(`确定要${action}“${competition.title}”吗？`, `${action}赛事`, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const headers = await getHeaders()
    const res = await request.post(
      `/api/competitions/${competition.id}/status/`,
      { status },
      { headers }
    )
    if (res.data.success) {
      ElMessage.success(res.data.msg)
      loadMyCompetitions()
    } else {
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('操作失败')
    }
  }
}

const goToDetail = (id) => router.push(`/event-detail/${id}`)
const goToEdit = (id) => router.push(`/competition-edit/${id}`)
const goToRegistration = (id) => {
  localStorage.setItem('selected_competition', id)
  router.push('/registration-manage')
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

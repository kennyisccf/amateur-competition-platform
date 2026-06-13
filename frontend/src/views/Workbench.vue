<template>
  <div class="workbench-container">
    <div class="page-head">
      <div>
        <h2>赛事工作台</h2>
        <p>集中管理赛事审核状态、报名名单和赛程进度。</p>
      </div>
      <el-button type="primary" @click="router.push('/create')">发起新赛事</el-button>
    </div>

    <div class="summary-grid">
      <div class="summary-card">
        <span>全部赛事</span>
        <strong>{{ workbenchStats.total }}</strong>
      </div>
      <div class="summary-card">
        <span>报名中</span>
        <strong>{{ workbenchStats.open }}</strong>
      </div>
      <div class="summary-card">
        <span>进行中</span>
        <strong>{{ workbenchStats.running }}</strong>
      </div>
      <div class="summary-card">
        <span>已结束</span>
        <strong>{{ workbenchStats.finished }}</strong>
      </div>
    </div>

    <div class="toolbar">
      <el-input
        v-model="searchKeyword"
        class="toolbar-search"
        clearable
        placeholder="搜索赛事名称、编号或地点"
        @input="tablePage = 1"
      />
      <el-select v-model="statusFilter" clearable placeholder="赛事状态" @change="tablePage = 1">
        <el-option
          v-for="item in statusOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-select v-model="categoryFilter" clearable placeholder="赛事分类" @change="tablePage = 1">
        <el-option
          v-for="item in categoryOptions"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <el-button plain @click="resetFilters">清空筛选</el-button>
      <span class="toolbar-count">共 {{ filteredCompetitions.length }} 场</span>
    </div>

    <el-table
      v-loading="loading"
      :data="pagedCompetitions"
      row-key="id"
      border
      stripe
      style="width: 100%"
    >
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
          <el-button
            v-if="scope.row.type === 'PRIVATE' && scope.row.invite_code"
            size="small"
            plain
            :icon="CopyDocument"
            @click="copyInviteCode(scope.row.invite_code)"
          >
            复制
          </el-button>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="比赛时间" width="180">
        <template #default="scope">
          {{ new Date(scope.row.start_time).toLocaleDateString() }}
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

      <el-table-column label="操作" min-width="360" fixed="right">
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
    <el-empty
      v-if="!loading && competitions.length > 0 && filteredCompetitions.length === 0"
      description="没有符合筛选条件的赛事"
    />
    <el-empty
      v-if="!loading && competitions.length === 0"
      description="还没有创建或可管理的赛事"
    >
      <el-button type="primary" @click="router.push('/create')">发起新赛事</el-button>
    </el-empty>
    <el-pagination
      v-if="filteredCompetitions.length > tablePageSize"
      v-model:current-page="tablePage"
      v-model:page-size="tablePageSize"
      class="table-pagination"
      background
      layout="total, sizes, prev, pager, next"
      :page-sizes="[10, 20, 50]"
      :total="filteredCompetitions.length"
      @size-change="tablePage = 1"
    />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CopyDocument } from '@element-plus/icons-vue'
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
const loading = ref(false)
const searchKeyword = ref('')
const statusFilter = ref('')
const categoryFilter = ref('')
const tablePage = ref(1)
const tablePageSize = ref(10)

const statusOptions = [
  { label: '待审核', value: 0 },
  { label: '报名中', value: 1 },
  { label: '进行中', value: 2 },
  { label: '已结束', value: 3 },
  { label: '已驳回', value: 4 }
]

const categoryOptions = computed(() => {
  return [...new Set(competitions.value.map(item => item.category).filter(Boolean))]
})

const workbenchStats = computed(() => ({
  total: competitions.value.length,
  open: competitions.value.filter(item => item.status === 1).length,
  running: competitions.value.filter(item => item.status === 2).length,
  finished: competitions.value.filter(item => item.status === 3).length
}))

const filteredCompetitions = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  return competitions.value.filter(item => {
    const matchesKeyword = !keyword || [
      item.title,
      item.competition_no,
      item.location
    ].some(value => String(value || '').toLowerCase().includes(keyword))
    const matchesStatus = statusFilter.value === '' || statusFilter.value == null || item.status === statusFilter.value
    const matchesCategory = !categoryFilter.value || item.category === categoryFilter.value
    return matchesKeyword && matchesStatus && matchesCategory
  })
})
const pagedCompetitions = computed(() => {
  const start = (tablePage.value - 1) * tablePageSize.value
  return filteredCompetitions.value.slice(start, start + tablePageSize.value)
})

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
    loading.value = true
    const headers = await getHeaders()
    const res = await request.get('/api/my_competitions/?scope=managed', { headers })
    if (res.data.success) {
      competitions.value = res.data.competitions
      tablePage.value = 1
    }
  } catch (err) {
    ElMessage.error('加载赛事失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchKeyword.value = ''
  statusFilter.value = ''
  categoryFilter.value = ''
  tablePage.value = 1
}

const copyInviteCode = async (inviteCode) => {
  try {
    await navigator.clipboard.writeText(inviteCode)
    ElMessage.success('邀请码已复制')
  } catch (err) {
    ElMessage.warning('复制失败，请手动复制')
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
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('删除失败')
    }
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
  width: 100%;
  max-width: min(1440px, 100%);
  margin: 0 auto;
  padding: var(--page-padding);
}

.page-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 20px;
}

.page-head h2 {
  margin: 0 0 6px;
}

.page-head p {
  margin: 0;
  color: #667085;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}

.summary-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
}

.summary-card span {
  display: block;
  color: #667085;
  font-size: 13px;
  margin-bottom: 8px;
}

.summary-card strong {
  color: #1f2937;
  font-size: 26px;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.toolbar-search {
  width: 300px;
}

.toolbar-count {
  color: #667085;
  font-size: 13px;
}

.el-table {
  border-radius: 8px;
  overflow: hidden;
}

.table-pagination {
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 900px) {
  .page-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .toolbar-search,
  .toolbar :deep(.el-select) {
    width: 100%;
  }
}
</style>

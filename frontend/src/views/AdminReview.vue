<template>
  <div class="admin-container">
    <div class="role-strip">
      <span>权限角色: {{ isSuperAdmin ? '超级测试管理员 test_admin' : '平台管理员 admin' }}</span>
      <el-tag v-if="isSuperAdmin" type="danger" effect="dark">测试最高权限</el-tag>
    </div>

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
        <div class="stat-value warning-value">{{ stats.pendingCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">已驳回赛事</div>
        <div class="stat-value danger-value">{{ stats.rejectedCount }}</div>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="赛事审核" name="review">
        <div class="review-card">
          <h3>主办方资质准入终审</h3>
          <el-table :data="pendingList" border v-loading="loading">
            <el-table-column prop="id" label="赛事ID" width="80" />
            <el-table-column prop="competition_no" label="编号" width="140" />
            <el-table-column prop="title" label="赛事名称" min-width="180" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="organizer.nickname" label="主办方" width="140" />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="scope">
                <el-button size="small" type="success" @click="handleApprove(scope.row)">批准</el-button>
                <el-button size="small" type="danger" @click="handleReject(scope.row)">驳回</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="用户管理" name="users">
        <div class="user-card">
          <div class="card-header">
            <h3>全站用户管理</h3>
            <div class="header-actions">
              <el-button type="primary" @click="openUserDialog">新建用户</el-button>
              <el-button v-if="isSuperAdmin" type="success" @click="openBulkUserDialog">批量新增</el-button>
              <el-button
                v-if="isSuperAdmin"
                type="warning"
                :disabled="selectedUserIds.length === 0"
                @click="openBulkJoinDialog"
              >
                批量加入赛事
              </el-button>
              <el-button
                v-if="isSuperAdmin"
                type="danger"
                :disabled="selectedUserIds.length === 0"
                @click="handleBulkDeleteUsers"
              >
                批量删除用户
              </el-button>
            </div>
          </div>

          <div class="table-tools">
            <el-input
              v-model="userKeyword"
              clearable
              placeholder="搜索编号 / 用户名 / 昵称"
              class="tool-input"
              @input="userPage = 1"
            />
            <el-select
              v-model="userRoleFilter"
              clearable
              placeholder="角色"
              class="tool-select"
              @change="userPage = 1"
            >
              <el-option label="参赛者" value="PLAYER" />
              <el-option label="主办方" value="ORGANIZER" />
              <el-option label="管理员" value="ADMIN" />
            </el-select>
            <el-select
              v-model="userStatusFilter"
              clearable
              placeholder="状态"
              class="tool-select"
              @change="userPage = 1"
            >
              <el-option label="正常" value="active" />
              <el-option label="已封禁" value="blocked" />
            </el-select>
            <span class="table-count">
              已选 {{ selectedUserIds.length }} 人 / 筛选 {{ filteredUserList.length }} 人
            </span>
          </div>

          <el-table
            :data="pagedUserList"
            row-key="user_id"
            border
            v-loading="loading"
            @selection-change="handleUserSelectionChange"
          >
            <el-table-column
              v-if="isSuperAdmin"
              type="selection"
              width="48"
              reserve-selection
              :selectable="canSelectUserForJoin"
            />
            <el-table-column prop="user_id" label="用户ID" width="80" />
            <el-table-column prop="user_code" label="编号" width="110" />
            <el-table-column prop="username" label="用户名" width="140" />
            <el-table-column prop="nickname" label="昵称" min-width="150" />
            <el-table-column prop="points" label="积分" width="100" sortable />
            <el-table-column label="角色" width="150">
              <template #default="scope">
                <el-tag :type="getRoleTagType(scope.row.role_code)">
                  {{ scope.row.role }}
                </el-tag>
                <el-tag v-if="scope.row.is_super_admin" class="super-user-tag" type="danger" size="small">
                  test_admin
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100" :formatter="formatUserStatus" />
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="scope">
                <el-button
                  size="small"
                  :type="scope.row.is_active ? 'danger' : 'success'"
                  @click="handleToggleUser(scope.row)"
                >
                  {{ scope.row.is_active ? '封禁' : '解封' }}
                </el-button>
                <el-button
                  v-if="isSuperAdmin"
                  size="small"
                  type="danger"
                  plain
                  @click="handleDeleteUser(scope.row)"
                >
                  彻底删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-if="filteredUserList.length > userPageSize"
            v-model:current-page="userPage"
            v-model:page-size="userPageSize"
            class="table-pagination"
            background
            layout="total, sizes, prev, pager, next"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredUserList.length"
            @size-change="userPage = 1"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane v-if="isSuperAdmin" label="赛事测试数据" name="competition-tools">
        <div class="competition-card">
          <div class="card-header">
            <h3>批量赛事测试数据</h3>
            <div class="header-actions">
              <el-button type="success" @click="openBulkCompetitionDialog">批量随机新增赛事</el-button>
              <el-button
                type="danger"
                :disabled="selectedCompetitionIds.length === 0"
                @click="handleBulkDeleteCompetitions"
              >
                批量删除赛事
              </el-button>
            </div>
          </div>
          <el-table
            :data="competitionList"
            border
            v-loading="loading"
            @selection-change="handleCompetitionSelectionChange"
          >
            <el-table-column type="selection" width="48" />
            <el-table-column prop="competition_no" label="编号" width="140" />
            <el-table-column prop="title" label="赛事名称" min-width="180" />
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column label="类型" width="100">
              <template #default="scope">{{ scope.row.type === 'PRIVATE' ? '私人赛' : '公开赛' }}</template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="scope">{{ getStatusText(scope.row.status) }}</template>
            </el-table-column>
            <el-table-column label="人数" width="110">
              <template #default="scope">{{ scope.row.current_participants }}/{{ scope.row.max_participants }}</template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" min-width="170" :formatter="formatTime" />
          </el-table>
        </div>
      </el-tab-pane>

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

    <el-dialog v-model="userDialogVisible" title="新建测试用户" width="460px">
      <el-form :model="userForm" label-width="90px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" placeholder="例如 player_new" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="userForm.password" placeholder="默认 123456" show-password />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="userForm.nickname" placeholder="显示名称" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="userForm.role">
            <el-option label="参赛者" value="PLAYER" />
            <el-option label="主办方" value="ORGANIZER" />
            <el-option v-if="isSuperAdmin" label="管理员" value="ADMIN" />
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" placeholder="可不填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateUser">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="bulkUserDialogVisible" title="批量新增测试用户" width="500px">
      <el-form :model="bulkUserForm" label-width="110px">
        <el-form-item label="账号前缀">
          <el-input v-model="bulkUserForm.prefix" placeholder="例如 player_auto_" />
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="bulkUserForm.count" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="bulkUserForm.role">
            <el-option label="参赛者" value="PLAYER" />
            <el-option label="主办方" value="ORGANIZER" />
          </el-select>
        </el-form-item>
        <el-form-item label="昵称前缀">
          <el-input v-model="bulkUserForm.nickname_prefix" placeholder="例如 测试用户" />
        </el-form-item>
        <el-form-item label="随机积分">
          <el-switch v-model="bulkUserForm.random_points" active-text="开启" inactive-text="关闭" />
        </el-form-item>
        <div class="dialog-tip">
          批量生成的是测试账号，登录时只输用户名，不需要密码和验证码。开启随机积分后会生成 0-2000 分，方便测试种子选手排序。
        </div>
      </el-form>
      <template #footer>
        <el-button @click="bulkUserDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBulkCreateUsers">批量创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="bulkJoinDialogVisible" title="批量加入赛事" width="540px">
      <el-form :model="bulkJoinForm" label-width="100px">
        <el-form-item label="已选用户">
          <el-tag type="info">{{ selectedUserIds.length }} 人</el-tag>
        </el-form-item>
        <el-form-item label="目标赛事">
          <el-select
            v-model="bulkJoinForm.competition_id"
            placeholder="选择要加入的赛事"
            filterable
            class="full-select"
          >
            <el-option
              v-for="competition in competitionList"
              :key="competition.id"
              :label="formatCompetitionOption(competition)"
              :value="competition.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bulkJoinDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBulkJoinUsers">加入赛事</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="bulkCompetitionDialogVisible" title="批量随机新增赛事" width="520px">
      <el-form :model="bulkCompetitionForm" label-width="120px">
        <el-form-item label="新增数量">
          <el-input-number v-model="bulkCompetitionForm.count" :min="1" :max="30" />
        </el-form-item>
        <el-form-item label="赛事类型">
          <el-select v-model="bulkCompetitionForm.type">
            <el-option label="公开赛" value="PUBLIC" />
            <el-option label="私人赛" value="PRIVATE" />
            <el-option label="随机混合" value="MIXED" />
          </el-select>
        </el-form-item>
        <el-form-item label="每场人数">
          <el-input-number v-model="bulkCompetitionForm.max_participants" :min="2" :max="64" />
        </el-form-item>
        <el-form-item label="随机填满人">
          <el-switch v-model="bulkCompetitionForm.auto_fill" active-text="是" inactive-text="否" />
        </el-form-item>
        <el-form-item label="人员随机积分">
          <el-switch
            v-model="bulkCompetitionForm.random_points"
            :disabled="!bulkCompetitionForm.auto_fill"
            active-text="开启"
            inactive-text="关闭"
          />
        </el-form-item>
        <div class="dialog-tip">
          所有批量赛事都会使用单淘汰赛制；选择填满人时会自动生成测试选手并直接通过报名。开启随机积分后，树图种子推荐会更接近真实比赛。
        </div>
      </el-form>
      <template #footer>
        <el-button @click="bulkCompetitionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBulkCreateCompetitions">批量新增</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const activeTab = ref('review')
const isSuperAdmin = ref(localStorage.getItem('is_super_admin') === '1')
const stats = ref({
  totalUsers: 0,
  runningEvents: 0,
  pendingCount: 0,
  rejectedCount: 0
})
const pendingList = ref([])
const userList = ref([])
const recordList = ref([])
const competitionList = ref([])
const selectedUserIds = ref([])
const selectedCompetitionIds = ref([])
const userKeyword = ref('')
const userRoleFilter = ref('')
const userStatusFilter = ref('')
const userPage = ref(1)
const userPageSize = ref(20)
const userDialogVisible = ref(false)
const bulkUserDialogVisible = ref(false)
const bulkJoinDialogVisible = ref(false)
const bulkCompetitionDialogVisible = ref(false)
const userForm = ref({
  username: '',
  password: '123456',
  nickname: '',
  role: 'PLAYER',
  email: ''
})
const bulkUserForm = ref({
  prefix: 'player_auto_',
  count: 5,
  role: 'PLAYER',
  nickname_prefix: '测试用户',
  random_points: true
})
const bulkJoinForm = ref({
  competition_id: ''
})
const bulkCompetitionForm = ref({
  count: 3,
  type: 'PUBLIC',
  max_participants: 8,
  auto_fill: true,
  random_points: true
})

const filteredUserList = computed(() => {
  const keyword = userKeyword.value.trim().toLowerCase()
  return userList.value.filter((item) => {
    const matchesKeyword = !keyword || [
      item.user_code,
      item.username,
      item.nickname,
      item.email
    ].some(value => String(value || '').toLowerCase().includes(keyword))
    const matchesRole = !userRoleFilter.value || item.role_code === userRoleFilter.value
    const matchesStatus = !userStatusFilter.value ||
      (userStatusFilter.value === 'active' ? item.is_active : !item.is_active)
    return matchesKeyword && matchesRole && matchesStatus
  })
})
const pagedUserList = computed(() => {
  const start = (userPage.value - 1) * userPageSize.value
  return filteredUserList.value.slice(start, start + userPageSize.value)
})

const getHeaders = async () => {
  const csrfRes = await request.get('/csrf/')
  return {
    'X-CSRFToken': csrfRes.data.csrfToken
  }
}

const formatUserStatus = (row) => row.is_active ? '正常' : '已封禁'
const formatTime = (row) => new Date(row.created_at).toLocaleString()
const getRoleTagType = (role) => {
  if (role === 'ADMIN') return 'danger'
  if (role === 'ORGANIZER') return 'warning'
  return 'success'
}
const getStatusText = (status) => {
  const map = {
    0: '待审核',
    1: '报名中',
    2: '进行中',
    3: '已结束',
    4: '已驳回'
  }
  return map[Number(status)] || '未知'
}
const formatCompetitionOption = (competition) => {
  const no = competition.competition_no || `ID.${competition.id}`
  return `${no} ${competition.title} (${competition.current_participants}/${competition.max_participants}, ${getStatusText(competition.status)})`
}
const canSelectUserForJoin = (row) => !row.is_super_admin

const loadCurrentUser = async () => {
  try {
    const res = await request.get('/api/user/')
    if (res.data.success) {
      isSuperAdmin.value = !!res.data.data.is_super_admin
      localStorage.setItem('username', res.data.data.username)
      localStorage.setItem('is_super_admin', isSuperAdmin.value ? '1' : '0')
    }
  } catch (err) {
    isSuperAdmin.value = false
  }
}

const openUserDialog = () => {
  userForm.value = {
    username: '',
    password: '123456',
    nickname: '',
    role: 'PLAYER',
    email: ''
  }
  userDialogVisible.value = true
}

const openBulkUserDialog = () => {
  bulkUserForm.value = {
    prefix: 'player_auto_',
    count: 5,
    role: 'PLAYER',
    nickname_prefix: '测试用户',
    random_points: true
  }
  bulkUserDialogVisible.value = true
}

const openBulkJoinDialog = () => {
  if (selectedUserIds.value.length === 0) {
    ElMessage.warning('请先勾选要加入赛事的用户')
    return
  }
  bulkJoinForm.value = { competition_id: '' }
  loadCompetitions()
  bulkJoinDialogVisible.value = true
}

const handleUserSelectionChange = (selection) => {
  selectedUserIds.value = selection.map(item => item.user_id)
}

const openBulkCompetitionDialog = () => {
  bulkCompetitionForm.value = {
    count: 3,
    type: 'PUBLIC',
    max_participants: 8,
    auto_fill: true,
    random_points: true
  }
  bulkCompetitionDialogVisible.value = true
}

const handleCompetitionSelectionChange = (selection) => {
  selectedCompetitionIds.value = selection.map(item => item.id)
}

const loadPending = async () => {
  loading.value = true
  try {
    const headers = await getHeaders()
    const res = await request.get('/api/admin/pending_competitions/', { headers })
    if (res.data.success) {
      pendingList.value = res.data.data
      stats.value.pendingCount = res.data.data.length
    }
  } catch (err) {
    ElMessage.error('待审核赛事加载失败')
  } finally { loading.value = false }
}

const loadUsers = async () => {
  loading.value = true
  try {
    const headers = await getHeaders()
    const res = await request.get('/api/admin/users/', { headers })
    if (res.data.success) {
      userList.value = res.data.users
      stats.value.totalUsers = res.data.users.length
    }
  } catch (err) {
    ElMessage.error('用户列表加载失败')
  } finally { loading.value = false }
}

const loadRecords = async () => {
  loading.value = true
  try {
    const headers = await getHeaders()
    const res = await request.get('/api/admin/audit_records/', { headers })
    if (res.data.success) {
      recordList.value = res.data.records
    }
  } catch (err) {
    ElMessage.error('审核记录加载失败')
  } finally { loading.value = false }
}

const loadCompetitions = async () => {
  try {
    const headers = await getHeaders()
    const res = await request.get('/api/my_competitions/?scope=managed', { headers })
    if (res.data.success) {
      competitionList.value = res.data.competitions
    }
  } catch (err) {
    ElMessage.error('赛事列表加载失败')
  }
}

const handleApprove = async (row) => {
  try {
    const headers = await getHeaders()
    const res = await request.post(
      '/api/admin/review_competition/',
      { competition_id: row.id, status: 1 },
      { headers }
    )
    if (res.data.success) {
      ElMessage.success('审核通过')
      loadPending()
      loadStats()
      loadCompetitions()
    } else {
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (err) { ElMessage.error('操作失败') }
}

const handleReject = async (row) => {
  try {
    const { value: reason } = await ElMessageBox.prompt('请输入驳回原因', '驳回赛事')
    if (!reason) return
    const headers = await getHeaders()
    const res = await request.post(
      '/api/admin/review_competition/',
      { competition_id: row.id, status: 4, reason },
      { headers }
    )
    if (res.data.success) {
      ElMessage.success('已驳回')
      loadPending()
      loadStats()
      loadCompetitions()
    } else {
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('操作失败')
    }
  }
}

const handleToggleUser = async (row) => {
  try {
    const headers = await getHeaders()
    const res = await request.put(
      `/api/admin/users/${row.user_id}/status/`,
      { is_active: !row.is_active },
      { headers }
    )
    if (res.data.success) {
      ElMessage.success('操作成功')
      loadUsers()
    } else {
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (err) { ElMessage.error('操作失败') }
}

const handleCreateUser = async () => {
  if (!userForm.value.username || !userForm.value.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  try {
    const headers = await getHeaders()
    const res = await request.post('/api/admin/users/create/', userForm.value, { headers })
    if (res.data.success) {
      ElMessage.success('用户创建成功')
      userDialogVisible.value = false
      loadUsers()
      loadStats()
    } else {
      ElMessage.error(res.data.msg || '创建失败')
    }
  } catch (err) {
    ElMessage.error('创建失败')
  }
}

const handleBulkCreateUsers = async () => {
  if (!bulkUserForm.value.prefix) {
    ElMessage.warning('请填写账号前缀')
    return
  }
  try {
    const headers = await getHeaders()
    const res = await request.post('/api/admin/users/bulk_create/', {
      ...bulkUserForm.value,
      password: ''
    }, { headers })
    if (res.data.success) {
      ElMessage.success(res.data.msg || '批量创建成功')
      if (res.data.skipped?.length) {
        ElMessage.warning(`已跳过 ${res.data.skipped.length} 个已有账号`)
      }
      bulkUserDialogVisible.value = false
      loadUsers()
      loadStats()
    } else {
      ElMessage.error(res.data.msg || '批量创建失败')
    }
  } catch (err) {
    ElMessage.error('批量创建失败')
  }
}

const handleBulkJoinUsers = async () => {
  if (!bulkJoinForm.value.competition_id) {
    ElMessage.warning('请选择目标赛事')
    return
  }
  try {
    const headers = await getHeaders()
    const res = await request.post(
      '/api/admin/competitions/bulk_add_users/',
      {
        competition_id: bulkJoinForm.value.competition_id,
        user_ids: selectedUserIds.value
      },
      { headers }
    )
    if (res.data.success) {
      ElMessage.success(res.data.msg || '批量加入成功')
      if (res.data.skipped?.length) {
        ElMessage.warning(`有 ${res.data.skipped.length} 个用户被跳过`)
      }
      bulkJoinDialogVisible.value = false
      loadCompetitions()
    } else {
      ElMessage.error(res.data.msg || '批量加入失败')
    }
  } catch (err) {
    ElMessage.error('批量加入失败')
  }
}

const handleBulkCreateCompetitions = async () => {
  try {
    const headers = await getHeaders()
    const res = await request.post('/api/admin/competitions/bulk_create/', bulkCompetitionForm.value, { headers })
    if (res.data.success) {
      ElMessage.success(res.data.msg || '批量新增赛事成功')
      bulkCompetitionDialogVisible.value = false
      loadCompetitions()
      loadStats()
    } else {
      ElMessage.error(res.data.msg || '批量新增赛事失败')
    }
  } catch (err) {
    ElMessage.error('批量新增赛事失败')
  }
}

const handleBulkDeleteCompetitions = async () => {
  if (!selectedCompetitionIds.value.length) return
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedCompetitionIds.value.length} 个赛事吗？相关报名和审核记录会一起删除。`,
      '批量删除赛事',
      { type: 'warning' }
    )
    const headers = await getHeaders()
    const res = await request.post(
      '/api/admin/competitions/bulk_delete/',
      { competition_ids: selectedCompetitionIds.value },
      { headers }
    )
    if (res.data.success) {
      ElMessage.success(res.data.msg)
      selectedCompetitionIds.value = []
      loadCompetitions()
      loadStats()
    } else {
      ElMessage.error(res.data.msg || '批量删除失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleBulkDeleteUsers = async () => {
  if (!selectedUserIds.value.length) return
  try {
    await ElMessageBox.confirm(
      `确定彻底删除选中的 ${selectedUserIds.value.length} 个用户吗？相关报名和他们创建的赛事也会一起删除。`,
      '批量删除用户',
      { type: 'warning' }
    )
    const headers = await getHeaders()
    const res = await request.post(
      '/api/admin/users/bulk_delete/',
      { user_ids: selectedUserIds.value },
      { headers }
    )
    if (res.data.success) {
      ElMessage.success(res.data.msg)
      selectedUserIds.value = []
      loadUsers()
      loadCompetitions()
      loadStats()
    } else {
      ElMessage.error(res.data.msg || '批量删除失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleDeleteUser = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定彻底删除账号“${row.username}”吗？相关报名和该账号创建的赛事也会一起删除，不能通过解封恢复。`,
      '彻底删除账号',
      { type: 'warning' }
    )
    const headers = await getHeaders()
    const res = await request.delete(`/api/admin/users/${row.user_id}/delete/`, { headers })
    if (res.data.success) {
      ElMessage.success(res.data.msg)
      loadUsers()
      loadStats()
      loadCompetitions()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('删除失败')
    }
  }
}

const loadStats = async () => {
  try {
    const headers = await getHeaders()
    const res = await request.get('/api/admin/stats/', { headers })
    if (res.data.success) {
      stats.value = res.data.data
    }
  } catch (err) {
    ElMessage.error('统计信息加载失败')
  }
}

onMounted(async () => {
  await loadCurrentUser()
  loadStats()
  loadPending()
  loadUsers()
  loadRecords()
  loadCompetitions()
})
</script>

<style scoped>
.admin-container {
  width: 100%;
  max-width: min(1440px, 100%);
  margin: 0 auto;
  padding: var(--page-padding);
}
.role-strip {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  color: #666;
  font-size: 14px;
  margin-bottom: 24px;
}
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(160px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}
.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
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
.warning-value {
  color: #faad14;
}
.danger-value {
  color: #f5222d;
}
.review-card,
.user-card,
.competition-card,
.record-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.review-card h3,
.user-card h3,
.competition-card h3,
.record-card h3 {
  margin: 0 0 20px;
  font-size: 16px;
  color: #333;
  border-left: 3px solid #1677ff;
  padding-left: 12px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.card-header h3 {
  margin-bottom: 0;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.super-user-tag {
  margin-left: 6px;
}
.table-tools {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}
.tool-input {
  width: min(280px, 100%);
}
.tool-select {
  width: 140px;
}
.table-count {
  color: #667085;
  font-size: 13px;
}
.table-pagination {
  justify-content: flex-end;
  margin-top: 16px;
}
.dialog-tip {
  margin-bottom: 12px;
  padding: 10px 12px;
  color: #5f6f86;
  background: #f6f9fd;
  border: 1px solid #e5edf7;
  border-radius: 8px;
  font-size: 13px;
}
.full-select {
  width: 100%;
}
@media (max-width: 900px) {
  .stats-row {
    grid-template-columns: repeat(2, minmax(140px, 1fr));
  }
}
@media (max-width: 560px) {
  .admin-container {
    padding: 16px;
  }
  .stats-row {
    grid-template-columns: 1fr;
    gap: 14px;
  }
}
</style>

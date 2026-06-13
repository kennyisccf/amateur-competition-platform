<template>
  <div class="registration-manage-container">
    <h2>赛事报名与赛程</h2>
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
      <el-button v-if="userRole === 'ADMIN' && canManageSelected" type="primary" :disabled="!selectedCompetitionId" @click="openForceDialog">
        手动加入选手
      </el-button>
      <el-button
        v-if="isSuperAdmin && canManageSelected"
        type="success"
        :disabled="!selectedCompetitionId"
        @click="openBulkCreateDialog"
      >
        批量新增测试用户
      </el-button>
      <el-button
        v-if="isSuperAdmin && canManageSelected"
        type="warning"
        :disabled="!selectedCompetitionId"
        @click="openBulkJoinDialog"
      >
        用户表批量加入
      </el-button>
      <el-button
        v-if="userRole === 'ADMIN' && canManageSelected"
        type="danger"
        plain
        :disabled="selectedRegistrationIds.length === 0"
        @click="bulkDeleteRegistrations"
      >
        批量删除报名
      </el-button>
      <el-button
        v-if="canManageSelected"
        type="info"
        plain
        :disabled="!selectedCompetitionId || approvedRegistrations.length === 0"
        @click="openSeedDialog"
      >
        设置种子选手
      </el-button>
      <el-button
        v-if="canManageSelected && selectedCompetition?.status === 1"
        type="success"
        @click="handleCompetitionStatusChange(2)"
      >
        开始赛事
      </el-button>
      <el-button
        v-if="canManageSelected && [1, 2].includes(selectedCompetition?.status)"
        type="danger"
        plain
        @click="handleCompetitionStatusChange(3)"
      >
        结束赛事
      </el-button>
    </div>

    <CompetitionBracket
      v-if="selectedCompetition"
      :competition="selectedCompetition"
      :registrations="registrations"
      :bracket-state="bracketState"
      :readonly="!canManageSelected"
      :allow-ban="userRole === 'ADMIN'"
      @state-change="saveBracketState"
      @registration-action="handleBracketAction"
    />

    <div v-if="loading" class="loading">加载报名数据中...</div>
    <div v-else-if="registrations.length === 0 && selectedCompetitionId" class="empty-tip">
      该赛事暂无报名信息
    </div>
    <template v-else>
      <div class="table-tools">
        <el-input
          v-model="registrationKeyword"
          clearable
          placeholder="搜索报名ID / 编号 / 用户名 / 昵称 / 战队"
          class="tool-input"
          @input="registrationPage = 1"
        />
        <el-select
          v-model="registrationStatusFilter"
          clearable
          placeholder="选手状态"
          class="tool-select"
          @change="registrationPage = 1"
        >
          <el-option
            v-for="item in registrationStatusOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <span class="table-count">
          已选 {{ selectedRegistrationIds.length }} 人 / 筛选 {{ filteredRegistrations.length }} 人
        </span>
      </div>
      <el-table
        :data="pagedRegistrations"
        row-key="registration_id"
        border
        stripe
        class="registration-table"
        style="width: 100%; margin-top: 14px;"
        @selection-change="handleRegistrationSelectionChange"
      >
        <el-table-column
          v-if="userRole === 'ADMIN' && canManageSelected"
          type="selection"
          width="48"
          reserve-selection
        />
        <el-table-column prop="registration_id" label="报名ID" width="100" />
        <el-table-column prop="player_id" label="选手ID" width="100" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="nickname" label="选手昵称" min-width="120" />
        <el-table-column prop="player_points" label="当前积分" width="100" sortable />
        <el-table-column prop="team_name" label="战队名" min-width="140" />
        <el-table-column prop="team_members" label="选手账号" min-width="180" />
        <el-table-column label="选手状态" width="150">
          <template #default="scope">
            <el-dropdown v-if="canManageSelected" trigger="click" @command="(state) => changeRegistrationStatus(scope.row, state)">
              <el-tag
                :type="getRegistrationState(scope.row).type"
                effect="light"
                class="status-tag"
              >
                {{ getRegistrationState(scope.row).text }}
              </el-tag>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-for="item in registrationStatusOptions"
                    :key="item.value"
                    :command="item.value"
                  >
                    {{ item.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-tag v-else :type="getRegistrationState(scope.row).type" effect="light">
              {{ getRegistrationState(scope.row).text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="final_score" label="成绩" width="100" />
        <el-table-column prop="final_rank" label="排名" width="80" />
        <el-table-column prop="earned_points" label="获得积分" width="100" />
        <el-table-column  prop="registration_time"  label="报名时间"  min-width="180" :formatter="formatTime"/>

        <el-table-column label="操作" width="340">
          <template #default="scope">
            <el-button v-if="canManageSelected && scope.row.review_status===0" size="small" type="success" @click="approveRegistration(scope.row.registration_id)">
              通过
            </el-button>
            <el-button v-if="canManageSelected && scope.row.review_status===0" size="small" type="danger" @click="rejectRegistration(scope.row)">
              驳回
            </el-button>
            <el-button
              v-if="canManageSelected && scope.row.review_status===1 && scope.row.status !== 'finished' && [2, 3].includes(selectedCompetition?.status)"
              size="small"
              type="primary"
              @click="openResultDialog(scope.row)"
            >
              录入成绩
            </el-button>
            <el-button size="small" @click="showDetail(scope.row)">
              详情
            </el-button>
            <el-button v-if="userRole === 'ADMIN' && canManageSelected" size="small" type="danger" @click="deleteRegistration(scope.row)">
              删除报名
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="filteredRegistrations.length > registrationPageSize"
        v-model:current-page="registrationPage"
        v-model:page-size="registrationPageSize"
        class="table-pagination"
        background
        layout="total, sizes, prev, pager, next"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredRegistrations.length"
        @size-change="registrationPage = 1"
      />
    </template>
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
      <el-descriptions-item label="报名类型">
        {{ currentRegistration.register_type === 'team' ? '战队报名' : '个人报名' }}
      </el-descriptions-item>
      <el-descriptions-item label="战队/选手名称">
        {{ currentRegistration.team_name || '暂无' }}
      </el-descriptions-item>
      <el-descriptions-item label="选手账号">
        {{ currentRegistration.team_members || '暂无' }}
      </el-descriptions-item>
      <el-descriptions-item label="联系人">
        {{ currentRegistration.contact_name || '暂无' }}
      </el-descriptions-item>
      <el-descriptions-item label="联系方式">
        {{ currentRegistration.phone || '暂无' }}
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
      <el-descriptions-item label="比赛成绩">
        {{ currentRegistration.final_score || '暂无' }}
      </el-descriptions-item>
      <el-descriptions-item label="最终排名">
        {{ currentRegistration.final_rank || '暂无' }}
      </el-descriptions-item>
      <el-descriptions-item label="获得积分">
        {{ currentRegistration.earned_points || 0 }}
      </el-descriptions-item>
    </el-descriptions>
  </el-dialog>
  <el-dialog v-model="resultDialogVisible" title="录入比赛成绩" width="460px">
    <el-form label-width="90px">
      <el-form-item label="选手">
        {{ resultRegistration.nickname || resultRegistration.username }}
      </el-form-item>
      <el-form-item label="成绩">
        <el-input v-model="resultForm.final_score" placeholder="例如：100分、2:0" />
      </el-form-item>
      <el-form-item label="最终排名">
        <el-input-number v-model="resultForm.final_rank" :min="1" />
      </el-form-item>
      <el-form-item v-if="selectedCompetition?.type !== 'PRIVATE'" label="奖励积分">
        <el-input-number v-model="resultForm.earned_points" :min="0" />
      </el-form-item>
      <el-form-item v-else label="奖励积分">
        <el-input value="私人赛事不设置积分" disabled />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="resultDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitResult">保存成绩</el-button>
    </template>
  </el-dialog>
  <el-dialog v-model="forceDialogVisible" title="手动加入选手" width="520px">
    <el-form :model="forceForm" label-width="100px">
      <el-form-item label="加入账号">
        <el-input v-model="forceForm.username" placeholder="必须是已有用户名，例如 player_mike" />
      </el-form-item>
      <el-form-item label="报名类型">
        <el-select v-model="forceForm.register_type">
          <el-option label="个人报名" value="single" />
          <el-option label="战队报名" value="team" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="forceForm.register_type === 'team'" label="战队名">
        <el-input v-model="forceForm.team_name" placeholder="例如 测试战队" />
      </el-form-item>
      <el-form-item label="选手账号">
        <el-input
          v-model="forceForm.team_members"
          type="textarea"
          :rows="3"
          placeholder="多个账号用逗号或换行分隔；会自动包含加入账号"
        />
      </el-form-item>
      <el-form-item label="联系人">
        <el-input v-model="forceForm.contact_name" placeholder="可不填，默认使用账号昵称" />
      </el-form-item>
      <el-form-item label="联系方式">
        <el-input v-model="forceForm.phone" placeholder="可不填" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="forceDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="forceAddRegistration">加入赛事</el-button>
    </template>
  </el-dialog>
  <el-dialog v-model="bulkCreateDialogVisible" title="批量新增测试用户" width="500px">
    <el-form :model="bulkCreateForm" label-width="110px">
      <el-form-item label="账号前缀">
        <el-input v-model="bulkCreateForm.prefix" placeholder="例如 player_auto_" />
      </el-form-item>
      <el-form-item label="数量">
        <el-input-number v-model="bulkCreateForm.count" :min="1" :max="100" />
      </el-form-item>
      <el-form-item label="角色">
        <el-select v-model="bulkCreateForm.role">
          <el-option label="参赛者" value="PLAYER" />
          <el-option label="主办方" value="ORGANIZER" />
        </el-select>
      </el-form-item>
      <el-form-item label="昵称前缀">
        <el-input v-model="bulkCreateForm.nickname_prefix" placeholder="例如 测试用户" />
      </el-form-item>
      <el-form-item label="随机积分">
        <el-switch v-model="bulkCreateForm.random_points" active-text="开启" inactive-text="关闭" />
      </el-form-item>
      <div class="dialog-tip">
        这里生成的是测试用户，登录时只需要输入用户名，不需要密码和验证码。开启随机积分后会生成 0-2000 分，方便测试种子选手。
      </div>
    </el-form>
    <template #footer>
      <el-button @click="bulkCreateDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="bulkCreateUsers">批量新增</el-button>
    </template>
  </el-dialog>
  <el-dialog v-model="bulkJoinDialogVisible" title="从用户表批量加入赛事" width="920px">
    <div class="dialog-tip">
      当前赛事：{{ selectedCompetition?.competition_no || selectedCompetition?.id }} {{ selectedCompetition?.title }}；已报名用户会自动隐藏。
    </div>
    <div class="table-tools compact-tools">
      <el-input
        v-model="bulkJoinKeyword"
        clearable
        placeholder="搜索编号 / 用户名 / 昵称"
        class="tool-input"
        @input="bulkJoinPage = 1"
      />
      <el-select
        v-model="bulkJoinRoleFilter"
        clearable
        placeholder="角色"
        class="tool-select"
        @change="bulkJoinPage = 1"
      >
        <el-option label="参赛者" value="PLAYER" />
        <el-option label="主办方" value="ORGANIZER" />
      </el-select>
      <span class="table-count">
        已选 {{ bulkSelectedUserIds.length }} 人 / 可加入 {{ filteredJoinableUsers.length }} 人
      </span>
    </div>
    <el-table
      :data="pagedJoinableUsers"
      row-key="user_id"
      border
      height="360"
      @selection-change="handleBulkUserSelectionChange"
    >
      <el-table-column type="selection" width="48" reserve-selection />
      <el-table-column prop="user_id" label="ID" width="80" />
      <el-table-column prop="user_code" label="编号" width="110" />
      <el-table-column prop="username" label="用户名" min-width="140" />
      <el-table-column prop="nickname" label="昵称" min-width="140" />
      <el-table-column prop="role" label="角色" width="120" />
      <el-table-column prop="points" label="积分" width="100" sortable />
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
            {{ scope.row.is_active ? '正常' : '已封禁' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-if="filteredJoinableUsers.length > bulkJoinPageSize"
      v-model:current-page="bulkJoinPage"
      v-model:page-size="bulkJoinPageSize"
      class="table-pagination"
      background
      layout="total, sizes, prev, pager, next"
      :page-sizes="[10, 20, 50, 100]"
      :total="filteredJoinableUsers.length"
      @size-change="bulkJoinPage = 1"
    />
    <template #footer>
      <el-button @click="bulkJoinDialogVisible = false">取消</el-button>
      <el-button type="primary" :disabled="bulkSelectedUserIds.length === 0" @click="bulkJoinUsers">
        加入选中的 {{ bulkSelectedUserIds.length }} 人
      </el-button>
    </template>
  </el-dialog>
  <el-dialog v-model="seedDialogVisible" title="设置种子选手" width="560px">
    <div class="dialog-tip">
      种子选手表示首轮保送。系统只会在人数不规则、存在保送位时按积分推荐；你也可以手动指定，最多 {{ recommendedSeedLimit }} 位。
    </div>
    <el-radio-group v-model="selectedSeedMode" class="seed-mode">
      <el-radio-button value="AUTO">系统自动推荐</el-radio-button>
      <el-radio-button value="MANUAL">手动设置</el-radio-button>
    </el-radio-group>
    <el-select
      v-model="selectedSeedIds"
      multiple
      filterable
      collapse-tags
      collapse-tags-tooltip
      placeholder="选择已通过报名的选手或战队"
      style="width: 100%;"
      :disabled="selectedSeedMode === 'AUTO' || recommendedSeedLimit === 0"
    >
      <el-option
        v-for="row in approvedRegistrations"
        :key="row.registration_id"
      :label="seedOptionLabel(row)"
      :value="String(row.registration_id)"
    />
  </el-select>
    <div v-if="selectedSeedMode === 'MANUAL' && recommendedSeedLimit === 0" class="seed-preview">
      当前人数刚好进入标准单淘汰赛，没有首轮保送位，因此不设置种子。
    </div>
    <div v-if="selectedSeedMode === 'AUTO'" class="seed-preview">
      自动推荐：{{ autoSeedPreview || '当前没有保送位，暂不设置种子' }}
    </div>
    <template #footer>
      <el-button @click="seedDialogVisible = false">取消</el-button>
      <el-button type="warning" plain @click="clearSeedSettings">手动清空种子</el-button>
      <el-button type="primary" @click="saveSeedSettings">保存设置</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import CompetitionBracket from '@/components/CompetitionBracket.vue'

const router = useRouter()
const loading = ref(false)
const myCompetitions = ref([])
const selectedCompetitionId = ref('')
const registrations = ref([])
const userRole = localStorage.getItem('role') || ''
const isSuperAdmin = ref(localStorage.getItem('is_super_admin') === '1')
const bracketState = ref({ drawSeed: Date.now(), winners: {}, seedIds: [], seedMode: 'AUTO' })
const userList = ref([])
const bulkSelectedUserIds = ref([])
const selectedRegistrationIds = ref([])
const registrationKeyword = ref('')
const registrationStatusFilter = ref('')
const registrationPage = ref(1)
const registrationPageSize = ref(20)
const bulkJoinKeyword = ref('')
const bulkJoinRoleFilter = ref('')
const bulkJoinPage = ref(1)
const bulkJoinPageSize = ref(20)

const detailDialogVisible = ref(false)
const currentRegistration = ref({})
const resultDialogVisible = ref(false)
const resultRegistration = ref({})
const forceDialogVisible = ref(false)
const bulkCreateDialogVisible = ref(false)
const bulkJoinDialogVisible = ref(false)
const seedDialogVisible = ref(false)
const selectedSeedIds = ref([])
const selectedSeedMode = ref('AUTO')
const forceForm = ref({
  username: '',
  register_type: 'single',
  team_name: '',
  team_members: '',
  contact_name: '',
  phone: ''
})
const resultForm = ref({
  final_score: '',
  final_rank: 1,
  earned_points: 0
})
const bulkCreateForm = ref({
  prefix: 'player_auto_',
  count: 8,
  role: 'PLAYER',
  nickname_prefix: '测试用户',
  random_points: true
})
const selectedCompetition = computed(() =>
  myCompetitions.value.find(item => item.id === selectedCompetitionId.value)
)
const canManageSelected = computed(() => Boolean(selectedCompetition.value?.can_manage))
const approvedRegistrations = computed(() =>
  registrations.value.filter(item => item.review_status === 1)
)
const floorPowerOfTwo = (value) => {
  let size = 1
  while (size * 2 <= value) size *= 2
  return size
}
const getSeedLimit = (playerCount) => {
  if (playerCount < 4) return 0
  const mainSize = floorPowerOfTwo(playerCount)
  const prelimMatchCount = playerCount - mainSize
  if (prelimMatchCount <= 0) return 0
  const prelimPlayerCount = prelimMatchCount * 2
  const byeCount = playerCount - prelimPlayerCount
  return Math.min(byeCount, prelimMatchCount, 4, Math.ceil(playerCount / 4))
}
const recommendedSeedLimit = computed(() => getSeedLimit(approvedRegistrations.value.length))
const recommendedSeedIds = computed(() => {
  const seedCount = recommendedSeedLimit.value
  if (!seedCount) return []
  return approvedRegistrations.value
    .slice()
    .sort((a, b) => Number(b.player_points || 0) - Number(a.player_points || 0) || String(a.username).localeCompare(String(b.username)))
    .slice(0, seedCount)
    .map(item => String(item.registration_id))
})
const autoSeedPreview = computed(() =>
  recommendedSeedIds.value
    .map(id => approvedRegistrations.value.find(item => String(item.registration_id) === id))
    .filter(Boolean)
    .map((item, index) => `S${index + 1} ${item.team_name || item.nickname || item.username}`)
    .join('，')
)
const registeredPlayerIds = computed(() =>
  new Set(registrations.value.map(item => Number(item.player_id)))
)
const joinableUsers = computed(() =>
  userList.value.filter(item =>
    item.is_active &&
    item.role_code !== 'ADMIN' &&
    !registeredPlayerIds.value.has(Number(item.user_id))
  )
)
const filterUserByKeyword = (item, keyword) => {
  if (!keyword) return true
  return [
    item.user_code,
    item.username,
    item.nickname,
    item.email,
    item.team_name,
    item.team_members,
    item.registration_id,
    item.player_id
  ].some(value => String(value || '').toLowerCase().includes(keyword))
}
const filteredJoinableUsers = computed(() => {
  const keyword = bulkJoinKeyword.value.trim().toLowerCase()
  return joinableUsers.value.filter(item =>
    filterUserByKeyword(item, keyword) &&
    (!bulkJoinRoleFilter.value || item.role_code === bulkJoinRoleFilter.value)
  )
})
const pagedJoinableUsers = computed(() => {
  const start = (bulkJoinPage.value - 1) * bulkJoinPageSize.value
  return filteredJoinableUsers.value.slice(start, start + bulkJoinPageSize.value)
})
const filteredRegistrations = computed(() => {
  const keyword = registrationKeyword.value.trim().toLowerCase()
  return registrations.value.filter(item =>
    filterUserByKeyword(item, keyword) &&
    (!registrationStatusFilter.value || getRegistrationState(item).value === registrationStatusFilter.value)
  )
})
const pagedRegistrations = computed(() => {
  const start = (registrationPage.value - 1) * registrationPageSize.value
  return filteredRegistrations.value.slice(start, start + registrationPageSize.value)
})
const registrationStatusOptions = [
  { value: 'pending', label: '待审核', type: 'warning' },
  { value: 'approved', label: '已通过', type: 'success' },
  { value: 'rejected', label: '已驳回', type: 'danger' },
  { value: 'ongoing', label: '进行中', type: 'primary' },
  { value: 'finished', label: '已完赛', type: 'info' }
]

// 获取请求头
const getHeaders = async () => {
  const csrfRes = await request.get('/csrf/')
  return {
    'X-CSRFToken': csrfRes.data.csrfToken
  }
}

const fetchCurrentUser = async () => {
  try {
    const res = await request.get('/api/user/')
    if (res.data.success) {
      isSuperAdmin.value = !!res.data.data.is_super_admin
      localStorage.setItem('is_super_admin', isSuperAdmin.value ? '1' : '0')
    }
  } catch (err) {
    isSuperAdmin.value = false
  }
}

const fetchUsers = async () => {
  if (!isSuperAdmin.value) return
  try {
    const headers = await getHeaders()
    const res = await request.get('/api/admin/users/', { headers })
    if (res.data.success) {
      userList.value = res.data.users
    }
  } catch (err) {
    ElMessage.error('用户列表加载失败')
  }
}

const getRegistrationState = (row) => {
  if (row.status === 'finished') {
    return { value: 'finished', text: '已完赛', type: 'info' }
  }
  if (row.review_status === 2 || row.status === 'rejected') {
    return { value: 'rejected', text: '已驳回', type: 'danger' }
  }
  if (row.review_status === 0 || row.status === 'pending') {
    return { value: 'pending', text: '待审核', type: 'warning' }
  }
  if (row.status === 'ongoing' && selectedCompetition.value?.status === 2) {
    return { value: 'ongoing', text: '进行中', type: 'primary' }
  }
  return { value: 'approved', text: '已通过', type: 'success' }
}
const formatTime = (row) => {
  if (!row.registration_time) return '-'
  return new Date(row.registration_time).toLocaleString()
}
const saveBracketState = async (state) => {
  if (!selectedCompetitionId.value || !canManageSelected.value) return
  bracketState.value = state
  try {
    const res = await request.post(`/api/competitions/${selectedCompetitionId.value}/bracket/`, {
      bracket_state: state
    })
    if (res.data.success) {
      bracketState.value = res.data.bracket_state
      fetchRegistrations()
    } else {
      ElMessage.error(res.data.msg || '赛程保存失败')
    }
  } catch (err) {
    ElMessage.error('赛程保存失败')
  }
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
    const res = await request.get('/api/my_competitions/', { headers })
    if (res.data.success) {
      myCompetitions.value = res.data.competitions
      const savedId = Number(localStorage.getItem('selected_competition'))
      if (savedId && myCompetitions.value.some(item => item.id === savedId)) {
        selectedCompetitionId.value = savedId
        localStorage.removeItem('selected_competition')
        await fetchRegistrations()
      }
    }
  } catch (err) {
    ElMessage.error('网络请求失败')
  }
}

// 拉取报名列表
const fetchRegistrations = async () => {
  if (!selectedCompetitionId.value) return
  registrations.value = []
  selectedRegistrationIds.value = []
  registrationPage.value = 1
  bracketState.value = { drawSeed: Date.now(), winners: {}, seedIds: [], seedMode: 'AUTO' }
  loading.value = true
  try {
    const headers = await getHeaders()
    const res = await request.get(`/api/competitions/${selectedCompetitionId.value}/registrations/`, { headers })
    if (res.data.success) {
      registrations.value = res.data.registrations
      bracketState.value = res.data.bracket_state || { drawSeed: Date.now(), winners: {}, seedIds: [], seedMode: 'AUTO' }
    }
  } catch (err) {
    ElMessage.error('网络请求失败')
  } finally { loading.value = false }
}
const approveRegistration = async (id)=>{
  try{
    const res = await request.post(
      '/api/approve_registration/',
      {
        registration_id:id
      }
    )
    if(res.data.success){
      ElMessage.success('审核通过')
      fetchRegistrations()
    } else {
      ElMessage.error(res.data.msg || '审核失败')
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
    const res = await request.post(
      '/api/reject_registration/',
      {
        registration_id:row.registration_id,
        remark:remark.value
      }
    )
    if(res.data.success){
      ElMessage.success('已驳回')
      fetchRegistrations()
    } else {
      ElMessage.error(res.data.msg || '审核失败')
    }

  }catch(err){

  }
}
const changeRegistrationStatus = async (row, state) => {
  const current = getRegistrationState(row).value
  if (current === state) return
  const option = registrationStatusOptions.find(item => item.value === state)
  try {
    await ElMessageBox.confirm(
      `确定把“${row.nickname || row.username}”改为「${option?.label || state}」吗？`,
      '修改选手状态',
      { type: 'warning' }
    )
    const res = await request.post('/api/registrations/status/', {
      registration_id: row.registration_id,
      status: state
    })
    if (res.data.success) {
      ElMessage.success(res.data.msg || '选手状态已更新')
      fetchRegistrations()
      fetchMyCompetitions()
    } else {
      ElMessage.error(res.data.msg || '状态更新失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('状态更新失败')
    }
  }
}
const handleBracketAction = async ({ action, registrationId, playerId, name, username }) => {
  if (!canManageSelected.value) return
  if (action === 'drop') {
    try {
      await ElMessageBox.confirm(
        `确定把“${name || username}”标记为退赛吗？该队伍会从赛程树中移除。`,
        '标记退赛',
        { type: 'warning' }
      )
      const res = await request.post('/api/registrations/status/', {
        registration_id: registrationId,
        status: 'rejected'
      })
      if (res.data.success) {
        ElMessage.success('已标记退赛')
        fetchRegistrations()
        fetchMyCompetitions()
      } else {
        ElMessage.error(res.data.msg || '退赛操作失败')
      }
    } catch (err) {
      if (!['cancel', 'close'].includes(err)) {
        ElMessage.error('退赛操作失败')
      }
    }
    return
  }
  if (action === 'ban') {
    if (userRole !== 'ADMIN') {
      ElMessage.warning('只有平台管理员可以封禁账号')
      return
    }
    try {
      await ElMessageBox.confirm(
        `确定封禁账号“${username}”吗？封禁后该账号不能登录。`,
        '封禁账号',
        { type: 'warning' }
      )
      const headers = await getHeaders()
      const res = await request.put(
        `/api/admin/users/${playerId}/status/`,
        { is_active: false },
        { headers }
      )
      if (res.data.success) {
        await request.post('/api/registrations/status/', {
          registration_id: registrationId,
          status: 'rejected'
        })
        ElMessage.success('账号已封禁并移出赛程')
        fetchRegistrations()
        fetchMyCompetitions()
      } else {
        ElMessage.error(res.data.msg || '封禁失败')
      }
    } catch (err) {
      if (!['cancel', 'close'].includes(err)) {
        ElMessage.error('封禁失败')
      }
    }
  }
}
const showDetail = (row) => {
  currentRegistration.value = row
  detailDialogVisible.value = true
}

const openForceDialog = () => {
  forceForm.value = {
    username: '',
    register_type: 'single',
    team_name: '',
    team_members: '',
    contact_name: '',
    phone: ''
  }
  forceDialogVisible.value = true
}
const openBulkCreateDialog = () => {
  bulkCreateForm.value = {
    prefix: 'player_auto_',
    count: 8,
    role: 'PLAYER',
    nickname_prefix: '测试用户',
    random_points: true
  }
  bulkCreateDialogVisible.value = true
}
const openBulkJoinDialog = async () => {
  if (!selectedCompetitionId.value) {
    ElMessage.warning('请先选择赛事')
    return
  }
  await fetchUsers()
  bulkSelectedUserIds.value = []
  bulkJoinKeyword.value = ''
  bulkJoinRoleFilter.value = ''
  bulkJoinPage.value = 1
  bulkJoinDialogVisible.value = true
}
const seedOptionLabel = (row) => {
  const name = row.team_name || row.nickname || row.username
  return `${name} / ${row.username} / ${Number(row.player_points || 0)}分`
}
const openSeedDialog = () => {
  selectedSeedMode.value = bracketState.value?.seedMode === 'MANUAL' ? 'MANUAL' : 'AUTO'
  selectedSeedIds.value = Array.isArray(bracketState.value?.seedIds)
    ? bracketState.value.seedIds.map(String).slice(0, recommendedSeedLimit.value)
    : recommendedSeedIds.value
  seedDialogVisible.value = true
}
const saveSeedSettings = async () => {
  const validIds = new Set(approvedRegistrations.value.map(item => String(item.registration_id)))
  const seedIds = selectedSeedMode.value === 'MANUAL'
    ? selectedSeedIds.value
        .map(String)
        .filter((id, index, arr) => validIds.has(id) && arr.indexOf(id) === index)
        .slice(0, recommendedSeedLimit.value)
    : []
  seedDialogVisible.value = false
  await saveBracketState({
    ...bracketState.value,
    seedIds,
    seedMode: selectedSeedMode.value,
    winners: {}
  })
  ElMessage.success(selectedSeedMode.value === 'AUTO' ? '已恢复系统自动推荐保送种子，抽签树已重置' : (seedIds.length ? '保送种子已更新，抽签树已重置' : '已手动清空保送种子'))
}
const clearSeedSettings = async () => {
  selectedSeedMode.value = 'MANUAL'
  selectedSeedIds.value = []
  await saveSeedSettings()
}
const handleBulkUserSelectionChange = (selection) => {
  bulkSelectedUserIds.value = selection.map(item => item.user_id)
}
const handleRegistrationSelectionChange = (selection) => {
  selectedRegistrationIds.value = selection.map(item => item.registration_id)
}
const openResultDialog = (row) => {
  resultRegistration.value = row
  resultForm.value = {
    final_score: row.final_score || '',
    final_rank: row.final_rank || 1,
    earned_points: selectedCompetition.value?.type === 'PRIVATE' ? 0 : (row.earned_points || 0)
  }
  resultDialogVisible.value = true
}
const submitResult = async () => {
  try {
    const res = await request.post('/api/record_result/', {
      registration_id: resultRegistration.value.registration_id,
      ...resultForm.value,
      earned_points: selectedCompetition.value?.type === 'PRIVATE' ? 0 : resultForm.value.earned_points
    })
    if (res.data.success) {
      ElMessage.success(res.data.msg)
      resultDialogVisible.value = false
      fetchRegistrations()
    } else {
      ElMessage.error(res.data.msg || '成绩保存失败')
    }
  } catch (err) {
    ElMessage.error('成绩保存失败')
  }
}

const forceAddRegistration = async () => {
  if (!selectedCompetitionId.value || !forceForm.value.username) {
    ElMessage.warning('请选择赛事并填写账号')
    return
  }
  try {
    const res = await request.post('/api/admin/force_registration/', {
      competition_id: selectedCompetitionId.value,
      ...forceForm.value
    })
    if (res.data.success) {
      ElMessage.success(res.data.msg)
      forceDialogVisible.value = false
      fetchRegistrations()
      fetchMyCompetitions()
    } else {
      ElMessage.error(res.data.msg || '加入失败')
    }
  } catch (err) {
    ElMessage.error('加入失败')
  }
}

const handleCompetitionStatusChange = async (status) => {
  if (!selectedCompetitionId.value) return
  const action = status === 2 ? '开始' : '结束'
  try {
    await ElMessageBox.confirm(
      status === 2
        ? `确定开始“${selectedCompetition.value?.title}”吗？待审核报名会自动驳回，赛事大厅仍可查看但不能再报名。`
        : `确定结束“${selectedCompetition.value?.title}”吗？`,
      `${action}赛事`,
      { type: 'warning' }
    )
    const headers = await getHeaders()
    const res = await request.post(
      `/api/competitions/${selectedCompetitionId.value}/status/`,
      { status },
      { headers }
    )
    if (res.data.success) {
      ElMessage.success(res.data.msg)
      await fetchMyCompetitions()
      await fetchRegistrations()
    } else {
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('操作失败')
    }
  }
}

const bulkCreateUsers = async () => {
  if (!bulkCreateForm.value.prefix || !bulkCreateForm.value.count) {
    ElMessage.warning('请填写账号前缀和数量')
    return
  }
  try {
    const headers = await getHeaders()
    const res = await request.post('/api/admin/users/bulk_create/', {
      ...bulkCreateForm.value,
      password: ''
    }, { headers })
    if (res.data.success) {
      ElMessage.success(`${res.data.msg}，这些账号可免密码验证码登录`)
      bulkCreateDialogVisible.value = false
      await fetchUsers()
    } else {
      ElMessage.error(res.data.msg || '批量新增失败')
    }
  } catch (err) {
    ElMessage.error('批量新增失败')
  }
}

const bulkJoinUsers = async () => {
  if (!selectedCompetitionId.value || bulkSelectedUserIds.value.length === 0) {
    ElMessage.warning('请选择赛事和用户')
    return
  }
  try {
    const headers = await getHeaders()
    const res = await request.post('/api/admin/competitions/bulk_add_users/', {
      competition_id: selectedCompetitionId.value,
      user_ids: bulkSelectedUserIds.value
    }, { headers })
    if (res.data.success) {
      ElMessage.success(res.data.msg || '批量加入成功')
      if (res.data.skipped?.length) {
        ElMessage.warning(`已跳过 ${res.data.skipped.length} 个用户`)
      }
      bulkJoinDialogVisible.value = false
      fetchRegistrations()
      fetchMyCompetitions()
    } else {
      ElMessage.error(res.data.msg || '批量加入失败')
    }
  } catch (err) {
    ElMessage.error('批量加入失败')
  }
}

const bulkDeleteRegistrations = async () => {
  if (!selectedRegistrationIds.value.length) {
    ElMessage.warning('请先勾选要删除的报名记录')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedRegistrationIds.value.length} 条报名记录吗？已通过报名会同步扣减赛事人数。`,
      '批量删除报名',
      { type: 'warning' }
    )
    const headers = await getHeaders()
    const res = await request.post('/api/admin/registrations/bulk_delete/', {
      registration_ids: selectedRegistrationIds.value
    }, { headers })
    if (res.data.success) {
      ElMessage.success(res.data.msg || '批量删除成功')
      selectedRegistrationIds.value = []
      fetchRegistrations()
      fetchMyCompetitions()
    } else {
      ElMessage.error(res.data.msg || '批量删除失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('批量删除失败')
    }
  }
}

const deleteRegistration = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定删除“${row.nickname || row.username}”的报名记录吗？`,
      '删除报名',
      { type: 'warning' }
    )
    const res = await request.delete(`/api/admin/registrations/${row.registration_id}/delete/`)
    if (res.data.success) {
      ElMessage.success(res.data.msg)
      selectedRegistrationIds.value = []
      fetchRegistrations()
      fetchMyCompetitions()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(async () => {
  await fetchCurrentUser()
  fetchMyCompetitions()
})
</script>

<style scoped>
.registration-manage-container {
  padding: var(--page-padding);
  max-width: min(1440px, 100%);
  margin: 0 auto;
}
.registration-manage-container h2 {
  margin: 0 0 20px;
  font-size: 20px;
  color: #1f2d3d;
}
.filter-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.registration-table {
  border-radius: 8px;
  overflow: hidden;
}
.table-tools {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 16px;
}
.compact-tools {
  margin-top: 0;
  margin-bottom: 12px;
}
.tool-input {
  width: min(320px, 100%);
}
.tool-select {
  width: 150px;
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
.seed-mode {
  margin-bottom: 14px;
}
.seed-preview {
  margin-top: 10px;
  color: #5f6f86;
  font-size: 13px;
}
.status-tag {
  cursor: pointer;
  min-width: 72px;
  justify-content: center;
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
@media (max-width: 960px) {
  .filter-bar {
    align-items: stretch;
  }
}
</style>

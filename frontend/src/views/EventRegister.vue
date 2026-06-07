<template>
  <div class="event-register-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else class="register-content">
      <div class="competition-info">
        <a href="javascript:;" @click="router.push('/home')">← 返回赛事大厅</a>
        <h2>{{ competitionData.title }}</h2>
        <p>请填写报名信息，提交参赛申请</p>
        <div style="color: #666; font-size: 14px;">赛事状态: <span style="color: #52c41a">报名进行中</span></div>
      </div>

      <form @submit.prevent="handleSubmitRegister" class="register-form">
        <div class="form-item">
          <label>报名身份</label>
          <el-select v-model="form.registerType" placeholder="请选择">
            <el-option label="个人报名" value="single" />
            <el-option label="作为战队队长发起报名" value="team" />
          </el-select>
        </div>

        <div class="form-item">
          <label>{{ form.registerType === 'team' ? '战队名' : '队伍/显示名称' }}</label>
          <el-input v-model="form.teamName" :placeholder="form.registerType === 'team' ? '例如：乐赛羽毛球队' : '可不填，默认使用昵称'" />
        </div>

        <div class="form-item">
          <label>选手账号</label>
          <div class="member-row" v-for="(member, index) in form.memberNames" :key="index">
            <el-input
              v-model="form.memberNames[index]"
              placeholder="请输入已有账号用户名，例如 player_mike"
            />
            <el-button
              v-if="form.registerType === 'team'"
              type="primary"
              plain
              @click="addMember"
            >
              +
            </el-button>
            <el-button
              v-if="form.registerType === 'team' && form.memberNames.length > 1"
              type="danger"
              plain
              @click="removeMember(index)"
            >
              -
            </el-button>
          </div>
        </div>

        <div class="form-item">
          <label>队长/联系人</label>
          <el-input v-model="form.contactName" placeholder="可不填，默认使用账号昵称" />
        </div>

        <div class="form-item">
          <label>联系方式(手机/微信)</label>
          <el-input v-model="form.phone" placeholder="可不填，报名结果可在消息通知查看" />
        </div>

        <div class="form-item" v-if="competitionData.type === 'PRIVATE'">
          <label>私人赛事邀请码</label>
          <el-input v-model="form.inviteCode" placeholder="请输入私人赛事邀请码" />
        </div>

        <div class="progress-info">
          <div class="progress-label">报名进度</div>
          <el-progress :percentage="Math.round(competitionData.current_participants / competitionData.max_participants * 100)" :text-inside="true" />
          <div class="progress-text">{{ competitionData.current_participants }} / {{ competitionData.max_participants }} 战队</div>
        </div>

        <el-button type="primary" native-type="submit" style="width: 100%; margin-top: 24px">
          提交报名申请
        </el-button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const competitionData = ref({})
const form = ref({
  registerType: 'single',
  teamName: '',
  memberNames: [''],
  contactName: '',
  phone: '',
  inviteCode: ''
})
const currentUsername = ref('')

// 加载赛事信息
const loadCompetitionDetail = async () => {
  const competitionId = route.params.id || 1
  try {
    const res = await request.get(`/api/competition/${competitionId}/`)
    if (res.data.success) {
      competitionData.value = res.data.data
      loading.value = false
    }
    const userRes = await request.get('/api/user/')
    if (userRes.data.success) {
      currentUsername.value = userRes.data.data.username
      if (!form.value.memberNames[0]) {
        form.value.memberNames = [userRes.data.data.username]
      }
      form.value.contactName = userRes.data.data.nickname || userRes.data.data.username
    }
  } catch (err) {
    ElMessage.error('加载赛事信息失败')
    console.error(err)
  }
}

// 提交报名，适配新接口地址
const handleSubmitRegister = async () => {
  if (form.value.registerType === 'team' && !form.value.teamName) {
    ElMessage.warning(form.value.registerType === 'team' ? '请填写战队名' : '请填写队伍/显示名称')
    return
  }
  const memberNames = form.value.memberNames
    .map(item => String(item || '').trim())
    .filter(Boolean)
  const submittedMemberNames = form.value.registerType === 'single'
    ? memberNames.slice(0, 1)
    : memberNames
  if (!submittedMemberNames.length) {
    ElMessage.warning('请填写参赛选手账号')
    return
  }
  if (currentUsername.value && !submittedMemberNames.includes(currentUsername.value)) {
    ElMessage.warning('选手账号列表必须包含当前登录账号')
    return
  }
  if (competitionData.value.type === 'PRIVATE' && !form.value.inviteCode) {
    ElMessage.warning('私人赛事需要填写邀请码')
    return
  }

  const userId = localStorage.getItem('user_id')
  if (!userId) {
    ElMessage.warning('请先登录后再报名')
    router.push('/login')
    return
  }

  try {
    // 1. 获取CSRF Token
    const csrfRes = await request.get('/csrf/')
    const csrfToken = csrfRes.data.csrfToken

    // 2. 调用新的报名接口
    const res = await request.post(
      '/api/register_competition/',
      {
        competition_id: competitionData.value.id,
        invite_code: competitionData.value.type === 'PRIVATE' ? form.value.inviteCode : '',
        register_type: form.value.registerType,
        team_name: form.value.teamName,
        team_members: submittedMemberNames.join(', '),
        contact_name: form.value.contactName,
        phone: form.value.phone
      },
      {
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        }
      }
    )
    if (res.data.success) {
      ElMessage.success('报名成功！')
      router.push('/home')
    } else {
      ElMessage.error(res.data.msg || '报名失败')
    }
  } catch (err) {
    ElMessage.error('报名请求失败，请检查后端服务')
    console.error(err)
  }
}

const addMember = () => {
  form.value.memberNames.push('')
}

const removeMember = (index) => {
  form.value.memberNames.splice(index, 1)
  if (!form.value.memberNames.length) {
    form.value.memberNames.push('')
  }
}

onMounted(() => {
  loadCompetitionDetail()
})
</script>

<style scoped>
.event-register-container {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}
.loading {
  text-align: center;
  padding: 100px;
  font-size: 16px;
  color: #666;
}
.competition-info {
  margin-bottom: 32px;
}
.competition-info a {
  color: #1677ff;
  text-decoration: none;
  font-size: 14px;
}
.competition-info h2 {
  margin: 12px 0 8px;
  font-size: 24px;
}
.competition-info p {
  color: #666;
  margin: 0 0 8px;
}
.register-form {
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.form-item {
  margin-bottom: 20px;
}
.form-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}
.member-row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 8px;
  margin-bottom: 8px;
}
.progress-info {
  margin-top: 16px;
}
.progress-label {
  font-size: 14px;
  margin-bottom: 8px;
}
.progress-text {
  text-align: right;
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}
</style>

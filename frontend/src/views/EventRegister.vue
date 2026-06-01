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
            <el-option label="作为战队队长发起报名" value="team" />
            <el-option label="个人报名" value="single" />
          </el-select>
        </div>

        <div class="form-item">
          <label>战队/选手名称</label>
          <el-input v-model="form.teamName" placeholder="请填写全称" />
        </div>

        <div class="form-item">
          <label>队长/联系人</label>
          <el-input v-model="form.contactName" placeholder="请填写联系人姓名" />
        </div>

        <div class="form-item">
          <label>联系方式(手机/微信)</label>
          <el-input v-model="form.phone" placeholder="用于接收赛事通知" />
        </div>

        <div class="form-item">
          <label>私人赛事邀请码</label>
          <el-input v-model="form.inviteCode" placeholder="私人赛事请填写，公开赛事留空" />
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
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const competitionData = ref({})
const form = ref({
  registerType: 'team',
  teamName: '',
  contactName: '',
  phone: '',
  inviteCode: ''
})

// 加载赛事信息
const loadCompetitionDetail = async () => {
  const competitionId = route.params.id || 1
  try {
    const res = await axios.get(`http://localhost:8000/api/competition/${competitionId}/`)
    if (res.data.success) {
      competitionData.value = res.data.data
      loading.value = false
    }
  } catch (err) {
    ElMessage.error('加载赛事信息失败')
    console.error(err)
  }
}

// 提交报名，适配新接口地址
const handleSubmitRegister = async () => {
  if (!form.value.teamName || !form.value.phone) {
    ElMessage.warning('请填写完整报名信息')
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
    const csrfRes = await axios.get('http://localhost:8000/csrf/')
    const csrfToken = csrfRes.data.csrfToken

    // 2. 调用新的报名接口
    const res = await axios.post(
      'http://localhost:8000/api/register_competition/',
      {
        player_id: parseInt(userId),
        competition_id: competitionData.value.id,
        invite_code: form.value.inviteCode || null
      },
      {
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
        withCredentials: true
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
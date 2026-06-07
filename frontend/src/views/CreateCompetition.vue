<template>
  <div class="create-competition-container">
    <h2>{{ userRole === 'PLAYER' ? '发起私人赛事' : '发起全新赛事' }}</h2>
    <form @submit.prevent="handleCreate" class="create-form">
      <div class="form-row">
        <div class="form-item">
          <label>赛事名称</label>
          <el-input v-model="form.title" placeholder="请输入赛事名称" />
        </div>
        <div class="form-item">
          <label>赛事分类</label>
          <el-select v-model="form.category" placeholder="请选择分类">
            <el-option label="篮球" value="篮球" />
            <el-option label="足球" value="足球" />
            <el-option label="羽毛球" value="羽毛球" />
            <el-option label="网球" value="网球" />
            <el-option label="电竞" value="电竞" />
            <el-option label="棋牌桌游" value="棋牌桌游" />
            <el-option label="其他" value="其他" />
          </el-select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-item">
          <label>比赛地点</label>
          <el-input v-model="form.location" placeholder="请输入比赛地点" />
        </div>
        <div class="form-item">
          <label>赛事类型</label>
          <el-select v-model="form.competition_type" placeholder="请选择">
            <el-option v-if="userRole !== 'PLAYER'" label="公开赛事" value="PUBLIC" />
            <el-option label="私人赛事" value="PRIVATE" />
          </el-select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-item">
          <label>开始时间</label>
          <el-date-picker v-model="form.start_time" type="datetime" placeholder="选择开始时间" />
        </div>
        <div class="form-item">
          <label>结束时间</label>
          <el-date-picker v-model="form.end_time" type="datetime" placeholder="选择结束时间" />
        </div>
      </div>

      <div class="form-row">
        <div class="form-item">
          <label>最大参与人数</label>
          <el-input v-model="form.max_participants" type="number" placeholder="请输入" />
        </div>
        <div class="form-item" v-if="form.competition_type !== 'PRIVATE'">
          <label>奖励积分</label>
          <el-input v-model="form.reward_points" type="number" placeholder="请输入" />
        </div>
        <div class="form-item" v-else>
          <label>奖励积分</label>
          <el-input value="私人赛事不设置积分" disabled />
        </div>
      </div>

      <div class="form-row">
        <div class="form-item">
          <label>赛制规则</label>
          <el-select v-model="form.competition_format" placeholder="请选择赛制" disabled>
            <el-option label="单淘汰" value="SINGLE_ELIMINATION" />
          </el-select>
        </div>
      </div>

      <div class="form-item">
        <label>赛事描述</label>
        <el-input v-model="form.description" type="textarea" :rows="5" placeholder="请输入赛事规则、说明等信息" />
      </div>
      <div class="form-item">
        <label>赛事奖励</label>
        <el-input v-model="form.reward" type="textarea" :rows="5" placeholder="请输入赛事奖励" />
      </div>
      <el-button type="primary" native-type="submit" style="width: 100%; margin-top: 24px">
        创建赛事
      </el-button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const userRole = localStorage.getItem('role') || ''
const defaultStartTime = new Date()
defaultStartTime.setSeconds(0, 0)
const defaultEndTime = new Date(defaultStartTime.getTime() + 24 * 60 * 60 * 1000)

const form = ref({
  title: '',
  category: '',
  location: '',
  competition_type: userRole === 'PLAYER' ? 'PRIVATE' : 'PUBLIC',
  max_participants: '',
  reward_points: userRole === 'PLAYER' ? 0 : '',
  competition_format: 'SINGLE_ELIMINATION',
  group_count: 0,
  start_time: defaultStartTime,
  end_time: defaultEndTime,
  description: '',
  reward: '',
  status: '0'
})

// 获取请求头
const getHeaders = async () => {
  const csrfRes = await request.get('/csrf/')
  return {
    'X-CSRFToken': csrfRes.data.csrfToken,
    'Content-Type': 'application/json'
  }
}

const handleCreate = async () => {
  if (!form.value.title || !form.value.category || !form.value.location || !form.value.competition_type || !form.value.start_time || !form.value.end_time || !form.value.max_participants) {
    ElMessage.warning('请填写必填项')
    return
  }
  if (form.value.competition_type !== 'PRIVATE' && form.value.reward_points === '') {
    ElMessage.warning('请填写奖励积分')
    return
  }
  if (form.value.competition_format === 'GROUP_KNOCKOUT' && !form.value.group_count) {
    ElMessage.warning('请填写分组数')
    return
  }
  if (new Date(form.value.end_time) <= new Date(form.value.start_time)) {
    ElMessage.warning('结束时间必须晚于开始时间')
    return
  }

  const userId = localStorage.getItem('user_id')
  if (!userId) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const headers = await getHeaders()
    const res = await request.post(
      '/api/create_competition/',
      {
        ...form.value
      },
      { headers }
    )

    if (res.data.success) {
      ElMessage.success(`赛事创建成功！编号：${res.data.competition_no}`)
      if (res.data.invite_code) {
        await ElMessageBox.alert(
          `私人赛事邀请码：${res.data.invite_code}`,
          '请保存邀请码'
        )
      }
      router.push('/workbench')
    } else {
      ElMessage.error(res.data.msg || '创建失败')
    }
  } catch (err) {
    ElMessage.error('请求失败，请检查后端服务')
    console.error(err)
  }
}

watch(
  () => form.value.competition_type,
  (type) => {
    if (type === 'PRIVATE') {
      form.value.reward_points = 0
    } else if (form.value.reward_points === 0) {
      form.value.reward_points = ''
    }
  }
)

watch(
  () => form.value.competition_format,
  (format) => {
    if (format !== 'GROUP_KNOCKOUT') {
      form.value.group_count = 0
    }
  }
)
</script>

<style scoped>
.create-competition-container {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}
.create-competition-container h2 {
  margin: 0 0 24px;
}
.create-form {
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.form-row {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}
.form-item {
  flex: 1;
}
.form-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}
</style>

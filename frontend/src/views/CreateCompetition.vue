<template>
  <div class="create-competition-container">
    <h2>发起全新赛事</h2>
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
            <el-option label="公开赛事" value="PUBLIC" />
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
        <div class="form-item">
          <label>奖励积分</label>
          <el-input v-model="form.reward_points" type="number" placeholder="请输入" />
        </div>
      </div>

      <div class="form-item">
        <label>赛事描述</label>
        <el-input v-model="form.description" type="textarea" :rows="5" placeholder="请输入赛事规则、说明等信息" />
      </div>

      <el-button type="primary" native-type="submit" style="width: 100%; margin-top: 24px">
        创建赛事
      </el-button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const form = ref({
  title: '',
  category: '',
  location: '',
  competition_type: 'PUBLIC',
  max_participants: '',
  reward_points: '',
  start_time: '',
  end_time: '',
  description: ''
})

// 获取请求头
const getHeaders = async () => {
  const token = localStorage.getItem('token')
  const csrfRes = await axios.get('http://localhost:8000/csrf/')
  return {
    'Authorization': `Bearer ${token}`,
    'X-CSRFToken': csrfRes.data.csrfToken,
    'Content-Type': 'application/json'
  }
}

const handleCreate = async () => {
  if (!form.value.title || !form.value.location) {
    ElMessage.warning('请填写必填项')
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
    const res = await axios.post(
      'http://localhost:8000/api/create_competition/',
      {
        ...form.value,
        organizer_id: parseInt(userId)
      },
      { headers }
    )

    if (res.data.success) {
      ElMessage.success('赛事创建成功！')
      router.push('/workbench')
    } else {
      ElMessage.error(res.data.msg || '创建失败')
    }
  } catch (err) {
    ElMessage.error('请求失败，请检查后端服务')
    console.error(err)
  }
}
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
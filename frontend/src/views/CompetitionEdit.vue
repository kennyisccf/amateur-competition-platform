<template>
  <div class="edit-container">
    <h2>修改赛事信息</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <form v-else @submit.prevent="handleUpdate" class="edit-form">
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
          <label>最大参与人数</label>
          <el-input v-model="form.max_participants" type="number" placeholder="请输入" />
        </div>
      </div>

      <div class="form-row">
        <div class="form-item" v-if="form.type !== 'PRIVATE'">
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
        保存修改
      </el-button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const form = ref({})

// 获取请求头
const getHeaders = async () => {
  const csrfRes = await request.get('/csrf/')
  return {
    'X-CSRFToken': csrfRes.data.csrfToken
  }
}

// 加载原有赛事信息
const loadCompetition = async () => {
  const id = route.params.id
  try {
    const headers = await getHeaders()
    const res = await request.get(`/api/competition/${id}/`, { headers })
    if (res.data.success) {
      form.value = {
        title: res.data.data.title,
        category: res.data.data.category,
        type: res.data.data.type,
        location: res.data.data.location,
        max_participants: res.data.data.max_participants,
        reward_points: res.data.data.reward_points,
        competition_format: 'SINGLE_ELIMINATION',
        group_count: 0,
        reward: res.data.data.reward,
        description: res.data.data.description
      }
      loading.value = false
    }
  } catch (err) {
    ElMessage.error('加载赛事信息失败')
    console.error(err)
  }
}

// 提交修改
const handleUpdate = async () => {
  const id = route.params.id
  if (!form.value.title) {
    ElMessage.warning('请填写赛事名称')
    return
  }
  if (form.value.competition_format === 'GROUP_KNOCKOUT' && !form.value.group_count) {
    ElMessage.warning('请填写分组数')
    return
  }

  try {
    const headers = await getHeaders()
    const res = await request.put(
      `/api/competitions/${id}/update/`,
      form.value,
      { headers }
    )
    if (res.data.success) {
      ElMessage.success('修改成功')
      router.push('/workbench')
    } else {
      ElMessage.error(res.data.msg || '修改失败')
    }
  } catch (err) {
    ElMessage.error('修改失败')
  }
}

onMounted(() => {
  loadCompetition()
})

watch(
  () => form.value.competition_format,
  (format) => {
    if (format && format !== 'GROUP_KNOCKOUT') {
      form.value.group_count = 0
    }
  }
)
</script>

<style scoped>
.edit-container {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}
.edit-container h2 {
  margin: 0 0 24px;
}
.edit-form {
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
.loading {
  text-align: center;
  padding: 50px;
  color: #666;
}
</style>

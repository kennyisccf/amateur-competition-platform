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
      <div class="form-item">
        <label>赛事缩图</label>
        <div class="thumbnail-picker">
          <button
            v-for="item in defaultThumbnails"
            :key="item.url"
            type="button"
            class="thumbnail-option"
            :class="{ active: form.thumbnail_url === item.url }"
            @click="selectThumbnail(item.url)"
          >
            <img :src="item.url" :alt="item.name" />
            <span>{{ item.name }}</span>
          </button>
        </div>
        <div class="thumbnail-tools">
          <el-upload
            :show-file-list="false"
            accept="image/*"
            :http-request="uploadThumbnail"
          >
            <el-button>上传本地图片</el-button>
          </el-upload>
          <el-button v-if="form.thumbnail_url" text @click="form.thumbnail_url = ''">清空缩图</el-button>
        </div>
        <div v-if="form.thumbnail_url" class="thumbnail-preview">
          <img :src="form.thumbnail_url" alt="赛事缩图预览" />
        </div>
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
const defaultThumbnails = [
  { name: '羽毛球', url: '/default-thumbnails/badminton.png' },
  { name: '篮球', url: '/default-thumbnails/basketball.png' },
  { name: '足球', url: '/default-thumbnails/football.png' },
  { name: '网球', url: '/default-thumbnails/tennis.png' },
  { name: '电竞', url: '/default-thumbnails/esports.png' },
  { name: '棋牌桌游', url: '/default-thumbnails/boardgame.png' }
]

const selectThumbnail = (url) => {
  form.value.thumbnail_url = url
}

const uploadThumbnail = async ({ file, onSuccess, onError }) => {
  const payload = new FormData()
  payload.append('file', file)
  try {
    const res = await request.post('/api/upload/competition_thumbnail/', payload, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (res.data.success) {
      form.value.thumbnail_url = res.data.url
      ElMessage.success(res.data.msg || '缩图上传成功')
      onSuccess?.(res.data)
    } else {
      ElMessage.warning(res.data.msg || '缩图上传失败')
      onError?.(new Error(res.data.msg || 'upload failed'))
    }
  } catch (err) {
    ElMessage.error('缩图上传失败，请检查后端服务')
    onError?.(err)
  }
}

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
        description: res.data.data.description,
        thumbnail_url: res.data.data.thumbnail_url || ''
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
  if (form.value.thumbnail_url && form.value.thumbnail_url.length > 500) {
    ElMessage.warning('缩图地址不能超过500个字符')
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
  padding: var(--page-padding);
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
.thumbnail-picker {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(126px, 1fr));
  gap: 10px;
}
.thumbnail-option {
  position: relative;
  height: 78px;
  padding: 0;
  overflow: hidden;
  border: 2px solid transparent;
  border-radius: 8px;
  background: #f6f9fd;
  cursor: pointer;
}
.thumbnail-option.active {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.14);
}
.thumbnail-option img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.thumbnail-option span {
  position: absolute;
  left: 8px;
  bottom: 7px;
  padding: 2px 8px;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  background: rgba(8, 28, 54, 0.68);
  border-radius: 999px;
}
.thumbnail-tools {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
}
.thumbnail-preview {
  margin-top: 10px;
  width: 280px;
  height: 156px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5edf7;
  background: #f6f9fd;
}
.thumbnail-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.loading {
  text-align: center;
  padding: 50px;
  color: #666;
}
</style>

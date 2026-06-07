<template>
  <div class="notice-container">
    <div class="page-header">
      <h2>消息通知</h2>
      <el-button @click="loadMessages">刷新</el-button>
    </div>

    <div v-if="loading" class="loading">加载消息中...</div>
    <el-empty v-else-if="messages.length === 0" description="暂无系统消息" />
    <div v-else class="notice-list">
      <div v-for="item in messages" :key="item.id" class="notice-item" @click="goToCompetition(item)">
        <div class="notice-icon">{{ item.type === '报名结果' ? '报' : '赛' }}</div>
        <div class="notice-body">
          <div class="notice-title">
            <span>{{ item.title }}</span>
            <el-tag size="small" :type="item.type === '报名结果' ? 'warning' : 'danger'">
              {{ item.type }}
            </el-tag>
          </div>
          <p>{{ item.content }}</p>
          <div class="notice-time">{{ item.created_at }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const messages = ref([])

const loadMessages = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/notifications/')
    if (res.data.success) {
      messages.value = res.data.messages
    } else {
      ElMessage.error(res.data.msg || '消息加载失败')
    }
  } catch (err) {
    ElMessage.error('消息加载失败')
  } finally {
    loading.value = false
  }
}

const goToCompetition = (item) => {
  if (item.competition_id) {
    router.push(`/event-detail/${item.competition_id}`)
  }
}

onMounted(loadMessages)
</script>

<style scoped>
.notice-container {
  padding: 24px;
  max-width: 960px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.page-header h2 {
  margin: 0;
  font-size: 22px;
  color: #1f2d3d;
}
.notice-list {
  display: grid;
  gap: 12px;
}
.notice-item {
  display: flex;
  gap: 14px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e8eef6;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  cursor: pointer;
}
.notice-item:hover {
  border-color: #9ec5ff;
  background: #f8fbff;
}
.notice-icon {
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  color: #fff;
  background: #1677ff;
  border-radius: 8px;
  font-weight: 700;
}
.notice-body {
  min-width: 0;
  flex: 1;
}
.notice-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #1f2d3d;
  font-weight: 700;
}
.notice-body p {
  margin: 8px 0;
  color: #4f5f73;
  font-size: 14px;
}
.notice-time {
  color: #8a97a8;
  font-size: 12px;
}
.loading {
  padding: 60px;
  text-align: center;
  color: #666;
}
</style>

<template>
  <div class="notice-container">
    <div class="page-header">
      <div>
        <p class="eyebrow">系统消息</p>
        <h2>消息通知</h2>
      </div>
      <el-button @click="loadMessages">刷新</el-button>
    </div>

    <div v-if="loading" class="loading">加载消息中...</div>
    <el-empty v-else-if="messages.length === 0" description="暂无消息通知" />
    <div v-else class="notice-list">
      <div
        v-for="item in messages"
        :key="item.id"
        class="notice-item"
        @click="goToTarget(item)"
      >
        <div class="notice-icon" :class="iconClass(item)">{{ iconText(item) }}</div>
        <div class="notice-body">
          <div class="notice-title">
            <span>{{ item.title }}</span>
            <el-tag size="small" :type="tagType(item)">{{ item.type }}</el-tag>
          </div>
          <p>{{ item.content }}</p>
          <div class="notice-footer">
            <span class="notice-time">{{ item.created_at }}</span>
            <div v-if="item.action_required && item.friend_relation_id" class="notice-actions">
              <el-button size="small" type="primary" @click.stop="respondFriend(item, 'accept')">
                通过
              </el-button>
              <el-button size="small" plain @click.stop="respondFriend(item, 'reject')">
                拒绝
              </el-button>
            </div>
          </div>
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
      messages.value = res.data.messages || []
    } else {
      ElMessage.error(res.data.msg || '消息加载失败')
    }
  } catch (err) {
    ElMessage.error('消息加载失败')
  } finally {
    loading.value = false
  }
}

const tagType = (item) => {
  if (item.type === '好友申请') return 'success'
  if (item.type === '好友消息') return 'primary'
  if (item.type === '报名结果') return 'warning'
  if (item.type === '赛事审核') return 'danger'
  return 'info'
}

const iconText = (item) => {
  if (item.type === '好友申请' || item.type === '好友通知' || item.type === '好友消息') return '友'
  if (item.type === '报名结果') return '报'
  return '赛'
}

const iconClass = (item) => ({
  friend: item.type === '好友申请' || item.type === '好友通知' || item.type === '好友消息',
  warning: item.type === '报名结果',
  danger: item.type === '赛事审核'
})

const respondFriend = async (item, action) => {
  try {
    const res = await request.post('/api/friends/respond/', {
      relation_id: item.friend_relation_id,
      action
    })
    if (res.data.success) {
      ElMessage.success(res.data.msg)
      await loadMessages()
    } else {
      ElMessage.warning(res.data.msg || '处理失败')
    }
  } catch (err) {
    ElMessage.error('处理失败')
  }
}

const goToTarget = (item) => {
  if (item.competition_id) {
    router.push(`/event-detail/${item.competition_id}`)
    return
  }
  if (item.friend_relation_id || item.friend_user_id) {
    router.push('/friends')
  }
}

onMounted(loadMessages)
</script>

<style scoped>
.notice-container {
  padding: var(--page-padding);
  max-width: 960px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.eyebrow {
  margin: 0 0 6px;
  color: #1677ff;
  font-size: 13px;
  font-weight: 700;
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
.notice-icon.friend {
  background: #34a853;
}
.notice-icon.warning {
  background: #f59e0b;
}
.notice-icon.danger {
  background: #ef4444;
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
.notice-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.notice-time {
  color: #8a97a8;
  font-size: 12px;
}
.notice-actions {
  display: flex;
  gap: 8px;
}
.loading {
  padding: 60px;
  text-align: center;
  color: #666;
}
</style>

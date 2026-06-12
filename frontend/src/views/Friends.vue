<template>
  <div class="friends-page">
    <div class="friends-hero">
      <div>
        <p class="eyebrow">社交与协作</p>
        <h2>好友系统</h2>
        <p>添加同学为好友，和好友聊天，后续组队报名会更自然。</p>
      </div>
      <div class="hero-actions">
        <span>允许别人添加我</span>
        <el-switch v-model="allowFriendRequests" @change="saveFriendSettings" />
        <el-button type="primary" @click="loadFriends">刷新</el-button>
      </div>
    </div>

    <div class="main-grid">
      <section class="panel friends-panel">
        <div class="panel-title">
          <h3>我的好友</h3>
          <el-tag>{{ friends.length }} 人</el-tag>
        </div>
        <el-empty v-if="!loading && friends.length === 0" description="暂无好友" />
        <div v-else class="user-list">
          <div
            v-for="item in friends"
            :key="item.user_id"
            class="user-card"
            :class="{ active: activeFriend?.user_id === item.user_id }"
            @click="openChat(item)"
          >
            <div class="avatar">{{ getInitial(item) }}</div>
            <div class="user-main">
              <strong>{{ item.nickname || item.username }}</strong>
              <span>{{ item.last_message || `${displayUserCode(item)} · ${item.username} · ${roleText(item.role)} · ${item.points || 0} 分` }}</span>
            </div>
            <el-badge v-if="item.unread_count" :value="item.unread_count" />
            <el-button size="small" type="danger" plain @click.stop="deleteFriend(item)">删除</el-button>
          </div>
        </div>

        <div class="panel-title request-title">
          <h3>收到的申请</h3>
          <el-tag type="warning">{{ incoming.length }} 条</el-tag>
        </div>
        <el-empty v-if="!loading && incoming.length === 0" description="暂无好友申请" />
        <div v-else class="user-list">
          <div v-for="item in incoming" :key="item.relation_id" class="user-card">
            <div class="avatar warm">{{ getInitial(item) }}</div>
            <div class="user-main">
              <strong>{{ item.nickname || item.username }}</strong>
              <span>{{ displayUserCode(item) }} · {{ item.username }} · {{ roleText(item.role) }}</span>
            </div>
            <div class="card-actions">
              <el-button size="small" type="primary" @click="respondRequest(item, 'accept')">通过</el-button>
              <el-button size="small" plain @click="respondRequest(item, 'reject')">拒绝</el-button>
            </div>
          </div>
        </div>
      </section>

      <section class="panel chat-panel">
        <div v-if="!activeFriend" class="chat-empty">
          <h3>选择一个好友开始聊天</h3>
          <p>聊天消息会同步到消息通知里的未读提醒。</p>
        </div>
        <template v-else>
          <div class="chat-header">
            <div class="avatar">{{ getInitial(activeFriend) }}</div>
            <div>
              <h3>{{ activeFriend.nickname || activeFriend.username }}</h3>
              <span>{{ displayUserCode(activeFriend) }} · {{ activeFriend.username }} · {{ roleText(activeFriend.role) }}</span>
            </div>
          </div>
          <div class="message-list">
            <div
              v-for="message in chatMessages"
              :key="message.id"
              class="message-row"
              :class="{ mine: message.mine }"
            >
              <div class="message-bubble">
                <p>{{ message.content }}</p>
                <span>{{ message.created_at }}</span>
              </div>
            </div>
          </div>
          <div class="chat-input">
            <el-input
              v-model="chatInput"
              type="textarea"
              :rows="2"
              maxlength="500"
              show-word-limit
              placeholder="输入聊天内容"
              @keydown.ctrl.enter.prevent="sendMessage"
            />
            <el-button type="primary" :disabled="!chatInput.trim()" @click="sendMessage">
              发送
            </el-button>
          </div>
        </template>
      </section>
    </div>

    <section class="panel search-panel">
      <div class="panel-title">
        <h3>查找用户</h3>
        <span>如果对方关闭“允许别人添加我”，这里会显示但不能发送申请。</span>
      </div>
      <div class="search-row">
        <el-input
          v-model="keyword"
          clearable
          placeholder="搜索用户名、昵称或编号，例如 U000003"
          @keyup.enter="searchUsers"
        />
        <el-button type="primary" @click="searchUsers">搜索</el-button>
      </div>
      <el-empty v-if="searched && searchResults.length === 0" description="没有找到用户" />
      <div v-else class="user-list search-results">
        <div v-for="item in searchResults" :key="item.user_id" class="user-card">
          <div class="avatar blue">{{ getInitial(item) }}</div>
          <div class="user-main">
            <strong>{{ item.nickname || item.username }}</strong>
            <span>{{ displayUserCode(item) }} · {{ item.username }} · {{ roleText(item.role) }} · {{ item.points || 0 }} 分</span>
          </div>
          <el-button
            size="small"
            type="primary"
            :disabled="!canSendRequest(item)"
            @click="sendRequest(item)"
          >
            {{ relationText(item) }}
          </el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const friends = ref([])
const incoming = ref([])
const outgoing = ref([])
const keyword = ref('')
const searchResults = ref([])
const searched = ref(false)
const allowFriendRequests = ref(true)
const activeFriend = ref(null)
const chatMessages = ref([])
const chatInput = ref('')

const roleText = (role) => ({
  PLAYER: '参赛者',
  ORGANIZER: '主办方',
  ADMIN: '管理员'
}[role] || role || '用户')

const getInitial = (item) => String(item.nickname || item.username || '?').slice(0, 1).toUpperCase()
const displayUserCode = (item) => item.user_code || `U${String(item.user_id || 0).padStart(6, '0')}`

const relationText = (item) => {
  if (item.relation_status === 'accepted') return '已是好友'
  if (item.relation_status === 'pending' && item.relation_direction === 'incoming') return '待你通过'
  if (item.relation_status === 'pending') return '已申请'
  if (!item.allow_friend_requests) return '对方已关闭'
  return '加好友'
}

const canSendRequest = (item) => !item.relation_status && item.allow_friend_requests

const loadFriends = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/friends/')
    if (res.data.success) {
      friends.value = res.data.friends || []
      incoming.value = res.data.incoming || []
      outgoing.value = res.data.outgoing || []
      allowFriendRequests.value = Boolean(res.data.allow_friend_requests)
      if (activeFriend.value) {
        const updated = friends.value.find(item => item.user_id === activeFriend.value.user_id)
        activeFriend.value = updated || null
      }
    } else {
      ElMessage.error(res.data.msg || '好友列表加载失败')
    }
  } catch (err) {
    ElMessage.error('好友列表加载失败')
  } finally {
    loading.value = false
  }
}

const saveFriendSettings = async () => {
  try {
    const res = await request.post('/api/friends/settings/', {
      allow_friend_requests: allowFriendRequests.value
    })
    if (res.data.success) {
      ElMessage.success(res.data.msg || '设置已保存')
    } else {
      ElMessage.warning(res.data.msg || '设置保存失败')
    }
  } catch (err) {
    ElMessage.error('设置保存失败')
  }
}

const searchUsers = async () => {
  searched.value = true
  try {
    const res = await request.get('/api/friends/search/', {
      params: { keyword: keyword.value }
    })
    if (res.data.success) {
      searchResults.value = res.data.users || []
    } else {
      ElMessage.error(res.data.msg || '搜索失败')
    }
  } catch (err) {
    ElMessage.error('搜索失败')
  }
}

const sendRequest = async (item) => {
  try {
    const res = await request.post('/api/friends/request/', { user_id: item.user_id })
    if (res.data.success) {
      ElMessage.success(res.data.msg || '好友申请已发送')
      await loadFriends()
      await searchUsers()
    } else {
      ElMessage.warning(res.data.msg || '发送失败')
    }
  } catch (err) {
    ElMessage.error('发送失败')
  }
}

const respondRequest = async (item, action) => {
  try {
    const res = await request.post('/api/friends/respond/', {
      relation_id: item.relation_id,
      action
    })
    if (res.data.success) {
      ElMessage.success(res.data.msg)
      await loadFriends()
      if (searched.value) await searchUsers()
    } else {
      ElMessage.warning(res.data.msg || '处理失败')
    }
  } catch (err) {
    ElMessage.error('处理失败')
  }
}

const openChat = async (item) => {
  activeFriend.value = item
  chatInput.value = ''
  try {
    const res = await request.get(`/api/friends/${item.user_id}/messages/`)
    if (res.data.success) {
      chatMessages.value = res.data.messages || []
      await loadFriends()
    } else {
      ElMessage.warning(res.data.msg || '聊天记录加载失败')
    }
  } catch (err) {
    ElMessage.error('聊天记录加载失败')
  }
}

const sendMessage = async () => {
  if (!activeFriend.value || !chatInput.value.trim()) return
  try {
    const res = await request.post(`/api/friends/${activeFriend.value.user_id}/messages/`, {
      content: chatInput.value.trim()
    })
    if (res.data.success) {
      chatInput.value = ''
      await openChat(activeFriend.value)
    } else {
      ElMessage.warning(res.data.msg || '发送失败')
    }
  } catch (err) {
    ElMessage.error('发送失败')
  }
}

const deleteFriend = async (item) => {
  try {
    await ElMessageBox.confirm(`确定删除好友“${item.nickname || item.username}”吗？`, '删除好友', { type: 'warning' })
    const res = await request.delete(`/api/friends/${item.user_id}/delete/`)
    if (res.data.success) {
      ElMessage.success(res.data.msg)
      if (activeFriend.value?.user_id === item.user_id) {
        activeFriend.value = null
        chatMessages.value = []
      }
      await loadFriends()
      if (searched.value) await searchUsers()
    } else {
      ElMessage.warning(res.data.msg || '删除失败')
    }
  } catch (err) {
    if (!['cancel', 'close'].includes(err)) {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(async () => {
  await loadFriends()
  await searchUsers()
})
</script>

<style scoped>
.friends-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px;
}
.friends-hero,
.panel {
  background: #fff;
  border: 1px solid #e5edf7;
  border-radius: 10px;
  box-shadow: 0 8px 22px rgba(34, 84, 137, 0.08);
}
.friends-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 24px;
  margin-bottom: 18px;
}
.friends-hero h2,
.panel-title h3,
.chat-header h3 {
  margin: 0;
  color: #12355b;
}
.friends-hero p {
  margin: 8px 0 0;
  color: #5d6f86;
}
.eyebrow {
  margin: 0 0 6px;
  color: #1677ff;
  font-weight: 700;
  font-size: 13px;
}
.hero-actions,
.card-actions,
.search-row,
.chat-input {
  display: flex;
  align-items: center;
  gap: 10px;
}
.hero-actions span {
  color: #5d6f86;
  font-size: 13px;
}
.main-grid {
  display: grid;
  grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
  gap: 18px;
  margin-bottom: 18px;
}
.panel {
  padding: 18px;
}
.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.panel-title span {
  color: #6a7b90;
  font-size: 13px;
}
.request-title {
  margin-top: 20px;
}
.user-list {
  display: grid;
  gap: 10px;
}
.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e8eef6;
  border-radius: 8px;
  background: #fbfdff;
  cursor: pointer;
}
.user-card.active,
.user-card:hover {
  border-color: #9ec5ff;
  background: #f3f8ff;
}
.avatar {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  flex: 0 0 38px;
  border-radius: 50%;
  color: #fff;
  background: #34a853;
  font-weight: 800;
}
.avatar.warm {
  background: #f59e0b;
}
.avatar.blue {
  background: #1677ff;
}
.user-main {
  min-width: 0;
  flex: 1;
  display: grid;
  gap: 4px;
}
.user-main strong {
  color: #1f2d3d;
}
.user-main span,
.chat-header span {
  color: #718096;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.chat-panel {
  min-height: 520px;
  display: flex;
  flex-direction: column;
}
.chat-empty {
  height: 100%;
  display: grid;
  place-content: center;
  text-align: center;
  color: #6a7b90;
}
.chat-empty h3 {
  margin: 0 0 8px;
  color: #12355b;
}
.chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 14px;
  border-bottom: 1px solid #e8eef6;
}
.message-list {
  flex: 1;
  min-height: 320px;
  max-height: 420px;
  overflow-y: auto;
  padding: 16px 4px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.message-row {
  display: flex;
}
.message-row.mine {
  justify-content: flex-end;
}
.message-bubble {
  max-width: 70%;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f1f5fb;
  color: #24364f;
}
.message-row.mine .message-bubble {
  background: #1677ff;
  color: #fff;
}
.message-bubble p {
  margin: 0 0 6px;
  white-space: pre-wrap;
  word-break: break-word;
}
.message-bubble span {
  font-size: 11px;
  opacity: 0.72;
}
.chat-input {
  align-items: flex-end;
  padding-top: 12px;
  border-top: 1px solid #e8eef6;
}
.search-row {
  margin-bottom: 14px;
}
.search-results {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
@media (max-width: 980px) {
  .main-grid,
  .search-results {
    grid-template-columns: 1fr;
  }
  .friends-hero {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>

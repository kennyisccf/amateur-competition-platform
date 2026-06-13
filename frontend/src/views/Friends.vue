<template>
  <div class="friends-page">
    <header class="friends-hero">
      <div>
        <p class="eyebrow">社交协作</p>
        <h2>好友与私信</h2>
        <p>管理好友申请、查看未读消息，也可以按账号编号快速找到同学。</p>
      </div>
      <div class="hero-actions">
        <span>允许别人添加我</span>
        <el-switch
          v-model="allowFriendRequests"
          :loading="settingsSaving"
          @change="saveFriendSettings"
        />
        <el-button :loading="loading" type="primary" plain @click="refreshAll">
          刷新
        </el-button>
      </div>
    </header>

    <section class="stats-grid">
      <div class="stat-card">
        <span>好友</span>
        <strong>{{ friends.length }}</strong>
      </div>
      <div class="stat-card">
        <span>待处理申请</span>
        <strong>{{ incoming.length }}</strong>
      </div>
      <div class="stat-card">
        <span>我发出的申请</span>
        <strong>{{ outgoing.length }}</strong>
      </div>
      <div class="stat-card">
        <span>未读消息</span>
        <strong>{{ unreadTotal }}</strong>
      </div>
    </section>

    <div class="main-grid">
      <section class="panel contacts-panel">
        <div class="panel-title">
          <h3>好友列表</h3>
          <el-tag>{{ filteredFriends.length }} 人</el-tag>
        </div>

        <el-input
          v-model="contactKeyword"
          clearable
          class="contact-search"
          placeholder="筛选昵称、用户名或编号"
        />

        <div v-loading="loading" class="user-list">
          <el-empty v-if="!loading && filteredFriends.length === 0" description="暂无匹配好友" />
          <div
            v-for="item in filteredFriends"
            v-else
            :key="item.user_id"
            class="user-card"
            :class="{ active: activeFriend?.user_id === item.user_id }"
            @click="openChat(item)"
          >
            <div class="avatar">{{ getInitial(item) }}</div>
            <div class="user-main">
              <div class="user-line">
                <strong>{{ item.nickname || item.username }}</strong>
                <el-badge v-if="item.unread_count" :value="item.unread_count" :max="99" />
              </div>
              <span>{{ friendSubtitle(item) }}</span>
              <small v-if="item.last_message_time">{{ item.last_message_time }}</small>
            </div>
            <el-button size="small" type="danger" plain @click.stop="deleteFriend(item)">
              删除
            </el-button>
          </div>
        </div>

        <div class="panel-title request-title">
          <h3>收到的申请</h3>
          <el-tag type="warning">{{ incoming.length }} 条</el-tag>
        </div>
        <el-empty v-if="!loading && incoming.length === 0" description="暂无好友申请" />
        <div v-else class="user-list compact-list">
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

        <div class="panel-title request-title">
          <h3>发出的申请</h3>
          <el-tag type="info">{{ outgoing.length }} 条</el-tag>
        </div>
        <el-empty v-if="!loading && outgoing.length === 0" description="暂无等待中的申请" />
        <div v-else class="user-list compact-list">
          <div v-for="item in outgoing" :key="item.relation_id" class="user-card muted">
            <div class="avatar blue">{{ getInitial(item) }}</div>
            <div class="user-main">
              <strong>{{ item.nickname || item.username }}</strong>
              <span>{{ displayUserCode(item) }} · {{ roleText(item.role) }}</span>
            </div>
            <el-tag size="small">等待对方处理</el-tag>
          </div>
        </div>
      </section>

      <section class="panel chat-panel">
        <div v-if="!activeFriend" class="chat-empty">
          <h3>选择一个好友开始聊天</h3>
          <p>好友消息会同步显示到消息通知，进入聊天后会自动标记为已读。</p>
        </div>
        <template v-else>
          <div class="chat-header">
            <div class="avatar">{{ getInitial(activeFriend) }}</div>
            <div>
              <h3>{{ activeFriend.nickname || activeFriend.username }}</h3>
              <span>{{ displayUserCode(activeFriend) }} · {{ activeFriend.username }} · {{ roleText(activeFriend.role) }} · {{ activeFriend.points || 0 }} 分</span>
            </div>
          </div>

          <div ref="messageListRef" v-loading="chatLoading" class="message-list">
            <el-empty v-if="!chatLoading && chatMessages.length === 0" description="还没有聊天记录" />
            <div
              v-for="message in chatMessages"
              v-else
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
              placeholder="输入消息，Ctrl + Enter 发送"
              @keydown.ctrl.enter.prevent="sendMessage"
            />
            <el-button
              type="primary"
              :loading="sending"
              :disabled="!chatInput.trim()"
              @click="sendMessage"
            >
              发送
            </el-button>
          </div>
        </template>
      </section>
    </div>

    <section class="panel search-panel">
      <div class="panel-title">
        <div>
          <h3>查找用户</h3>
          <span>支持用户名、昵称和账号编号，例如 U000003。</span>
        </div>
      </div>
      <div class="search-row">
        <el-input
          v-model="keyword"
          clearable
          placeholder="输入用户编号、昵称或用户名"
          @keyup.enter="searchUsers"
        />
        <el-button type="primary" :loading="searchLoading" @click="searchUsers">
          搜索
        </el-button>
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
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const loading = ref(false)
const searchLoading = ref(false)
const chatLoading = ref(false)
const sending = ref(false)
const settingsSaving = ref(false)
const friends = ref([])
const incoming = ref([])
const outgoing = ref([])
const keyword = ref('')
const contactKeyword = ref('')
const searchResults = ref([])
const searched = ref(false)
const allowFriendRequests = ref(true)
const activeFriend = ref(null)
const chatMessages = ref([])
const chatInput = ref('')
const messageListRef = ref(null)

const roleText = (role) => ({
  PLAYER: '参赛选手',
  ORGANIZER: '主办方',
  ADMIN: '管理员'
}[role] || role || '用户')

const unreadTotal = computed(() =>
  friends.value.reduce((total, item) => total + Number(item.unread_count || 0), 0)
)

const filteredFriends = computed(() => {
  const term = contactKeyword.value.trim().toLowerCase()
  if (!term) return friends.value
  return friends.value.filter(item =>
    [item.nickname, item.username, item.user_code, displayUserCode(item)]
      .some(value => String(value || '').toLowerCase().includes(term))
  )
})

const getInitial = (item) => String(item.nickname || item.username || '?').slice(0, 1).toUpperCase()
const displayUserCode = (item) => item.user_code || `U${String(item.user_id || 0).padStart(6, '0')}`

const friendSubtitle = (item) => {
  if (item.last_message) return item.last_message
  return `${displayUserCode(item)} · ${item.username} · ${roleText(item.role)} · ${item.points || 0} 分`
}

const relationText = (item) => {
  if (item.relation_status === 'accepted') return '已是好友'
  if (item.relation_status === 'pending' && item.relation_direction === 'incoming') return '等待你处理'
  if (item.relation_status === 'pending') return '已申请'
  if (!item.allow_friend_requests) return '对方已关闭'
  return '加好友'
}

const canSendRequest = (item) => !item.relation_status && item.allow_friend_requests

const scrollMessagesToBottom = async () => {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

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

const refreshAll = async () => {
  await loadFriends()
  if (activeFriend.value) await openChat(activeFriend.value)
  if (searched.value) await searchUsers()
}

const saveFriendSettings = async () => {
  settingsSaving.value = true
  try {
    const res = await request.post('/api/friends/settings/', {
      allow_friend_requests: allowFriendRequests.value
    })
    if (res.data.success) {
      ElMessage.success(res.data.msg || '好友申请设置已更新')
    } else {
      ElMessage.warning(res.data.msg || '设置保存失败')
    }
  } catch (err) {
    ElMessage.error('设置保存失败')
  } finally {
    settingsSaving.value = false
  }
}

const searchUsers = async () => {
  searched.value = true
  searchLoading.value = true
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
  } finally {
    searchLoading.value = false
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
  chatLoading.value = true
  try {
    const res = await request.get(`/api/friends/${item.user_id}/messages/`)
    if (res.data.success) {
      chatMessages.value = res.data.messages || []
      await loadFriends()
      await scrollMessagesToBottom()
    } else {
      ElMessage.warning(res.data.msg || '聊天记录加载失败')
    }
  } catch (err) {
    ElMessage.error('聊天记录加载失败')
  } finally {
    chatLoading.value = false
  }
}

const sendMessage = async () => {
  if (!activeFriend.value || !chatInput.value.trim()) return
  sending.value = true
  try {
    const res = await request.post(`/api/friends/${activeFriend.value.user_id}/messages/`, {
      content: chatInput.value.trim()
    })
    if (res.data.success) {
      chatMessages.value.push(res.data.message)
      chatInput.value = ''
      await scrollMessagesToBottom()
      await loadFriends()
    } else {
      ElMessage.warning(res.data.msg || '发送失败')
    }
  } catch (err) {
    ElMessage.error('发送失败')
  } finally {
    sending.value = false
  }
}

const deleteFriend = async (item) => {
  try {
    await ElMessageBox.confirm(`确定删除好友“${item.nickname || item.username}”吗？`, '删除好友', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
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
  const targetUserId = Number(route.query.user || 0)
  if (targetUserId) {
    const matched = friends.value.find(item => item.user_id === targetUserId)
    if (matched) await openChat(matched)
  }
})
</script>

<style scoped>
.friends-page {
  width: 100%;
  max-width: min(1280px, 100%);
  margin: 0 auto;
  padding: var(--page-padding);
}
.friends-hero,
.panel,
.stat-card {
  background: #fff;
  border: 1px solid #e5edf7;
  border-radius: 8px;
  box-shadow: 0 8px 22px rgba(34, 84, 137, 0.08);
}
.friends-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: clamp(18px, 2vw, 24px);
  margin-bottom: 16px;
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
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.stat-card {
  padding: 16px;
}
.stat-card span {
  display: block;
  color: #66758a;
  font-size: 13px;
}
.stat-card strong {
  display: block;
  margin-top: 6px;
  color: #12355b;
  font-size: 26px;
}
.main-grid {
  display: grid;
  grid-template-columns: minmax(320px, 430px) minmax(0, 1fr);
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
.contact-search {
  margin-bottom: 12px;
}
.request-title {
  margin-top: 22px;
}
.user-list {
  display: grid;
  gap: 10px;
}
.compact-list {
  max-height: 260px;
  overflow: auto;
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
.user-card.muted {
  cursor: default;
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
.user-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.user-main strong {
  min-width: 0;
  color: #1f2d3d;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-main span,
.user-main small,
.chat-header span {
  color: #718096;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-main small {
  color: #98a2b3;
  font-size: 12px;
}
.chat-panel {
  min-height: 560px;
  display: flex;
  flex-direction: column;
}
.chat-empty {
  height: 100%;
  min-height: 420px;
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
  min-height: 340px;
  max-height: 460px;
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
  max-width: min(70%, 520px);
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
@media (max-width: 1080px) {
  .main-grid,
  .search-results {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 860px) {
  .friends-hero {
    align-items: flex-start;
    flex-direction: column;
  }
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 560px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .hero-actions,
  .search-row,
  .chat-input {
    align-items: stretch;
    flex-direction: column;
    width: 100%;
  }
  .user-card {
    align-items: flex-start;
  }
  .card-actions {
    flex-direction: column;
  }
}
</style>

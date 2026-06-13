<template>
  <div class="notice-container">
    <header class="page-header">
      <div>
        <p class="eyebrow">消息中心</p>
        <h2>通知与待办</h2>
        <p>报名审核、赛事状态、好友申请和聊天未读都集中在这里处理。</p>
      </div>
      <el-button :loading="loading" type="primary" plain @click="loadMessages">
        刷新
      </el-button>
    </header>

    <section class="summary-grid">
      <button
        v-for="item in summaryItems"
        :key="item.key"
        class="summary-card"
        :class="{ active: activeFilter === item.key }"
        type="button"
        @click="activeFilter = item.key"
      >
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </button>
    </section>

    <section class="notice-toolbar">
      <el-radio-group v-model="activeFilter" size="large">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="todo">待处理</el-radio-button>
        <el-radio-button label="friend">好友</el-radio-button>
        <el-radio-button label="event">赛事/报名</el-radio-button>
      </el-radio-group>
      <el-input
        v-model="keyword"
        clearable
        class="search-input"
        placeholder="搜索标题、内容或类型"
      />
    </section>

    <el-skeleton v-if="loading" :rows="7" animated class="notice-loading" />

    <el-empty
      v-else-if="filteredMessages.length === 0"
      :description="emptyDescription"
      class="empty-state"
    >
      <el-button v-if="keyword || activeFilter !== 'all'" @click="resetFilters">
        清空筛选
      </el-button>
      <el-button v-else type="primary" plain @click="loadMessages">
        再检查一次
      </el-button>
    </el-empty>

    <div v-else class="notice-list">
      <article
        v-for="item in filteredMessages"
        :key="item.id"
        class="notice-item"
        :class="{ unread: isUnread(item), actionable: item.action_required }"
        @click="goToTarget(item)"
      >
        <div class="notice-icon" :class="iconClass(item)">
          {{ iconText(item) }}
        </div>
        <div class="notice-body">
          <div class="notice-title">
            <div>
              <span class="unread-dot" v-if="isUnread(item)" />
              <strong>{{ item.title }}</strong>
            </div>
            <el-tag size="small" :type="tagType(item)">
              {{ item.type }}
            </el-tag>
          </div>
          <p>{{ item.content }}</p>
          <div class="notice-footer">
            <span class="notice-time">{{ item.created_at }}</span>
            <div class="notice-actions">
              <el-button
                v-if="item.action_required && item.friend_relation_id"
                size="small"
                type="primary"
                @click.stop="respondFriend(item, 'accept')"
              >
                通过
              </el-button>
              <el-button
                v-if="item.action_required && item.friend_relation_id"
                size="small"
                plain
                @click.stop="respondFriend(item, 'reject')"
              >
                拒绝
              </el-button>
              <el-button
                v-if="hasTarget(item)"
                size="small"
                text
                type="primary"
                @click.stop="goToTarget(item)"
              >
                {{ targetText(item) }}
              </el-button>
            </div>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const messages = ref([])
const keyword = ref('')
const activeFilter = ref('all')

const isFriendNotice = (item) => String(item.type || '').includes('好友') || Boolean(item.friend_relation_id || item.friend_user_id)
const isEventNotice = (item) => Boolean(item.competition_id) || ['赛事', '报名'].some(text => String(item.type || '').includes(text))
const isUnread = (item) => Boolean(item.action_required) || String(item.type || '') === '好友消息'

const summaryItems = computed(() => [
  { key: 'all', label: '全部消息', value: messages.value.length },
  { key: 'todo', label: '待处理', value: messages.value.filter(item => item.action_required).length },
  { key: 'friend', label: '好友相关', value: messages.value.filter(isFriendNotice).length },
  { key: 'event', label: '赛事报名', value: messages.value.filter(isEventNotice).length }
])

const filteredMessages = computed(() => {
  const term = keyword.value.trim().toLowerCase()
  return messages.value.filter((item) => {
    const matchesFilter =
      activeFilter.value === 'all' ||
      (activeFilter.value === 'todo' && item.action_required) ||
      (activeFilter.value === 'friend' && isFriendNotice(item)) ||
      (activeFilter.value === 'event' && isEventNotice(item))
    if (!matchesFilter) return false
    if (!term) return true
    return [item.title, item.content, item.type, item.created_at]
      .some(value => String(value || '').toLowerCase().includes(term))
  })
})

const emptyDescription = computed(() => {
  if (keyword.value || activeFilter.value !== 'all') return '没有符合条件的消息'
  return '暂无消息通知'
})

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
  if (item.action_required) return 'warning'
  if (String(item.type || '').includes('好友')) return 'success'
  if (String(item.type || '').includes('报名')) return 'primary'
  if (String(item.type || '').includes('拒')) return 'danger'
  return 'info'
}

const iconText = (item) => {
  if (isFriendNotice(item)) return '友'
  if (String(item.type || '').includes('报名')) return '报'
  if (String(item.type || '').includes('拒')) return '审'
  return '赛'
}

const iconClass = (item) => ({
  friend: isFriendNotice(item),
  warning: item.action_required,
  danger: String(item.type || '').includes('拒')
})

const hasTarget = (item) => Boolean(item.competition_id || item.friend_relation_id || item.friend_user_id)

const targetText = (item) => {
  if (item.competition_id) return '查看赛事'
  if (item.friend_user_id) return '打开聊天'
  return '进入好友'
}

const resetFilters = () => {
  keyword.value = ''
  activeFilter.value = 'all'
}

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
  if (item.friend_user_id) {
    router.push({ path: '/friends', query: { user: item.friend_user_id } })
    return
  }
  if (item.friend_relation_id) {
    router.push('/friends')
  }
}

onMounted(loadMessages)
</script>

<style scoped>
.notice-container {
  width: 100%;
  max-width: min(1100px, 100%);
  margin: 0 auto;
  padding: var(--page-padding);
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}
.eyebrow {
  margin: 0 0 6px;
  color: #1677ff;
  font-size: 13px;
  font-weight: 700;
}
.page-header h2 {
  margin: 0;
  font-size: clamp(22px, 2.2vw, 28px);
  color: #132f4c;
}
.page-header p {
  margin: 8px 0 0;
  color: #61738a;
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.summary-card {
  min-height: 86px;
  padding: 16px;
  border: 1px solid #e4edf7;
  border-radius: 8px;
  background: #fff;
  text-align: left;
  cursor: pointer;
  box-shadow: 0 8px 22px rgba(34, 84, 137, 0.06);
}
.summary-card span {
  display: block;
  color: #66758a;
  font-size: 13px;
}
.summary-card strong {
  display: block;
  margin-top: 8px;
  color: #12355b;
  font-size: 28px;
}
.summary-card.active {
  border-color: #1677ff;
  background: #f2f7ff;
}
.notice-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.search-input {
  max-width: 320px;
}
.notice-loading,
.empty-state {
  padding: 28px;
  background: #fff;
  border: 1px solid #e4edf7;
  border-radius: 8px;
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
.notice-item.unread {
  border-left: 4px solid #1677ff;
}
.notice-item.actionable {
  background: #fffdf8;
}
.notice-icon {
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
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
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  color: #1f2d3d;
}
.notice-title > div {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.notice-title strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.unread-dot {
  width: 8px;
  height: 8px;
  flex: 0 0 8px;
  border-radius: 50%;
  background: #1677ff;
}
.notice-body p {
  margin: 8px 0;
  color: #4f5f73;
  font-size: 14px;
  line-height: 1.6;
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
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}
@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .notice-toolbar {
    align-items: stretch;
    flex-direction: column;
  }
  .search-input {
    max-width: none;
  }
}
@media (max-width: 560px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }
  .summary-grid {
    grid-template-columns: 1fr;
  }
  .notice-item {
    padding: 14px;
  }
  .notice-footer,
  .notice-title {
    align-items: flex-start;
    flex-direction: column;
  }
  .notice-actions {
    justify-content: flex-start;
  }
}
</style>

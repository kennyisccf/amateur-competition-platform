<template>
  <div class="home-page">
    <section class="hall-hero">
      <div class="hero-copy">
        <p class="eyebrow">赛事大厅</p>
        <h2>发现、报名和收藏校园赛事</h2>
        <p>按运动类型、报名状态和热度筛选赛事，收藏感兴趣的比赛，演示时也能快速回到重点赛事。</p>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="router.push('/create')">发起赛事</el-button>
        <el-button plain @click="getCompetitionData">刷新</el-button>
      </div>
    </section>

    <section class="stats-grid">
      <button class="stat-card" type="button" @click="resetFilters">
        <span>赛事总数</span>
        <strong>{{ hallStats.total }}</strong>
      </button>
      <button class="stat-card" type="button" @click="statusFilter = '1'">
        <span>正在报名</span>
        <strong>{{ hallStats.open }}</strong>
      </button>
      <button class="stat-card" type="button" @click="statusFilter = '2'">
        <span>进行中</span>
        <strong>{{ hallStats.running }}</strong>
      </button>
      <button class="stat-card" type="button" @click="favoriteOnly = true">
        <span>我的收藏</span>
        <strong>{{ favoriteCount }}</strong>
      </button>
    </section>

    <section class="filter-panel">
      <div class="search-line">
        <el-input
          v-model="searchKeyword"
          clearable
          placeholder="搜索赛事名称、编号或地点，例如 NO.00000001"
          @keyup.enter="searchEvent"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="searchEvent">搜索</el-button>
      </div>

      <div class="filter-row">
        <div class="filter-group category-filter">
          <span>品类</span>
          <el-radio-group v-model="category">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button
              v-for="item in categories"
              :key="item"
              :value="item"
            >
              {{ item }}
            </el-radio-button>
          </el-radio-group>
        </div>

        <div class="filter-group">
          <span>状态</span>
          <el-select v-model="statusFilter" class="compact-select">
            <el-option label="全部状态" value="all" />
            <el-option label="待审核" value="0" />
            <el-option label="报名中" value="1" />
            <el-option label="进行中" value="2" />
            <el-option label="已结束" value="3" />
            <el-option label="未通过" value="4" />
          </el-select>
        </div>

        <div class="filter-group">
          <span>类型</span>
          <el-select v-model="typeFilter" class="compact-select">
            <el-option label="全部类型" value="all" />
            <el-option label="公开赛" value="PUBLIC" />
            <el-option label="私人赛" value="PRIVATE" />
          </el-select>
        </div>

        <div class="filter-group">
          <span>排序</span>
          <el-select v-model="sortMode" class="compact-select">
            <el-option label="最新发布" value="latest" />
            <el-option label="报名人数最多" value="popular" />
            <el-option label="即将满员" value="filling" />
            <el-option label="积分奖励最高" value="reward" />
          </el-select>
        </div>

        <el-checkbox v-model="favoriteOnly" class="favorite-toggle">
          只看收藏
        </el-checkbox>
      </div>
    </section>

    <section class="event-section">
      <div class="section-head">
        <div>
          <h3>赛事列表</h3>
          <p>当前显示 {{ visibleCompetitionList.length }} 场赛事</p>
        </div>
        <el-button v-if="hasActiveFilter" text type="primary" @click="resetFilters">
          清空筛选
        </el-button>
      </div>

      <div v-if="loading" class="event-grid">
        <div v-for="item in 6" :key="item" class="event-card skeleton-card">
          <el-skeleton animated :rows="5" />
        </div>
      </div>

      <el-empty
        v-else-if="visibleCompetitionList.length === 0"
        class="empty-card"
        :description="favoriteOnly ? '暂无收藏赛事' : '没有找到符合条件的赛事'"
      >
        <el-button type="primary" @click="resetFilters">清空筛选</el-button>
      </el-empty>

      <div v-else class="event-grid">
        <article
          v-for="item in visibleCompetitionList"
          :key="item.id"
          class="event-card"
          @click="goToDetail(item.id)"
        >
          <div class="card-image" :style="eventImageStyle(item)">
            <button
              class="favorite-button"
              :class="{ active: isFavorite(item.id) }"
              type="button"
              :title="isFavorite(item.id) ? '取消收藏' : '收藏赛事'"
              @click.stop="toggleFavorite(item)"
            >
              <el-icon>
                <StarFilled v-if="isFavorite(item.id)" />
                <Star v-else />
              </el-icon>
            </button>

            <div class="tag-row">
              <span class="tag category-tag">{{ item.category || '其他' }}</span>
              <span class="tag" :class="item.type === 'PRIVATE' ? 'orange' : 'green'">
                {{ item.type === 'PRIVATE' ? '私人赛' : '公开赛' }}
              </span>
            </div>
            <span class="tag status-tag" :class="getStatusClass(item.status)">
              {{ getStatusText(item.status) }}
            </span>
            <div class="card-overlay">
              <p class="event-no">{{ item.competition_no || '未编号' }}</p>
              <h3>{{ displayTitle(item) }}</h3>
              <div class="meta-line">
                <span><el-icon><Location /></el-icon>{{ item.location || '地点待定' }}</span>
                <span><el-icon><Tickets /></el-icon>{{ formatRule(item) }}</span>
              </div>
            </div>
          </div>

          <div class="card-body">
            <div class="time-line">
              <el-icon><Calendar /></el-icon>
              <span>{{ getDateRange(item) }}</span>
            </div>
            <div class="participant-block">
              <div class="capacity-line">
                <span>报名进度</span>
                <strong>{{ item.current_participants || 0 }}/{{ item.max_participants || 0 }}</strong>
              </div>
              <el-progress
                :percentage="getFillPercent(item)"
                :show-text="false"
                :stroke-width="7"
              />
            </div>
            <div class="card-footer">
              <span class="reward-text">{{ getRewardText(item) }}</span>
              <div class="card-actions">
                <el-button text @click.stop="copyEventLink(item.id)">复制链接</el-button>
                <el-button type="primary" text @click.stop="goToDetail(item.id)">
                  {{ getActionText(item) }}
                </el-button>
              </div>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Calendar, Location, Search, Star, StarFilled, Tickets } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const searchKeyword = ref('')
const category = ref('')
const statusFilter = ref('all')
const typeFilter = ref('all')
const sortMode = ref('latest')
const favoriteOnly = ref(false)
const competitionList = ref([])
const favoriteIds = ref([])

const FAVORITE_STORAGE_KEY = 'lesai_favorite_competitions'
const categories = ['篮球', '足球', '羽毛球', '网球', '电竞', '棋牌桌游']

const defaultThumbnails = {
  篮球: '/default-thumbnails/basketball.png',
  足球: '/default-thumbnails/football.png',
  羽毛球: '/default-thumbnails/badminton.png',
  网球: '/default-thumbnails/tennis.png',
  电竞: '/default-thumbnails/esports.png',
  棋牌桌游: '/default-thumbnails/boardgame.png'
}

const hallStats = computed(() => ({
  total: competitionList.value.length,
  open: competitionList.value.filter(item => Number(item.status) === 1).length,
  running: competitionList.value.filter(item => Number(item.status) === 2).length
}))

const favoriteCount = computed(() => favoriteIds.value.length)

const visibleCompetitionList = computed(() => {
  const list = competitionList.value.filter((item) => {
    const matchesStatus = statusFilter.value === 'all' || String(item.status) === statusFilter.value
    const matchesType = typeFilter.value === 'all' || item.type === typeFilter.value
    const matchesFavorite = !favoriteOnly.value || isFavorite(item.id)
    return matchesStatus && matchesType && matchesFavorite
  })

  if (sortMode.value === 'popular') {
    return [...list].sort((a, b) => Number(b.current_participants || 0) - Number(a.current_participants || 0))
  }
  if (sortMode.value === 'filling') {
    return [...list].sort((a, b) => getFillPercent(b) - getFillPercent(a))
  }
  if (sortMode.value === 'reward') {
    return [...list].sort((a, b) => Number(b.reward_points || 0) - Number(a.reward_points || 0))
  }
  return [...list].sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
})

const hasActiveFilter = computed(() =>
  Boolean(
    searchKeyword.value ||
    category.value ||
    statusFilter.value !== 'all' ||
    typeFilter.value !== 'all' ||
    sortMode.value !== 'latest' ||
    favoriteOnly.value
  )
)

const loadFavorites = () => {
  try {
    favoriteIds.value = JSON.parse(localStorage.getItem(FAVORITE_STORAGE_KEY) || '[]')
      .map(item => Number(item))
      .filter(Boolean)
  } catch (err) {
    favoriteIds.value = []
  }
}

const saveFavorites = () => {
  localStorage.setItem(FAVORITE_STORAGE_KEY, JSON.stringify(favoriteIds.value))
}

const isFavorite = (id) => favoriteIds.value.includes(Number(id))

const toggleFavorite = (item) => {
  const id = Number(item.id)
  if (!id) return
  if (isFavorite(id)) {
    favoriteIds.value = favoriteIds.value.filter(itemId => itemId !== id)
    ElMessage.success('已取消收藏')
  } else {
    favoriteIds.value = [id, ...favoriteIds.value]
    ElMessage.success('已收藏赛事')
  }
  saveFavorites()
}

const copyEventLink = async (id) => {
  const url = `${window.location.origin}/event-detail/${id}`
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('赛事链接已复制')
  } catch (err) {
    ElMessage.warning('复制失败，请手动复制链接')
  }
}

const goToDetail = (id) => {
  router.push(`/event-detail/${id}`)
}

const formatRule = (item) => item.competition_format_text || '单淘汰'
const displayTitle = (item) => String(item.title || '').trim() || '未命名赛事'

const getStatusText = (status) => ({
  0: '待审核',
  1: '报名中',
  2: '进行中',
  3: '已结束',
  4: '未通过'
}[Number(status)] || '待审核')

const getStatusClass = (status) => ({
  0: 'orange',
  1: 'green',
  2: 'primary',
  3: 'gray',
  4: 'red'
}[Number(status)] || 'orange')

const getActionText = (item) => {
  if (Number(item.status) === 1) return '查看报名'
  if (Number(item.status) === 2) return '查看赛程'
  return '查看详情'
}

const getFillPercent = (item) => {
  const max = Number(item.max_participants || 0)
  if (!max) return 0
  return Math.min(100, Math.round(Number(item.current_participants || 0) / max * 100))
}

const getRewardText = (item) => {
  if (item.type === 'PRIVATE') return '私人赛不计积分'
  return `奖励 ${item.reward_points || 0} 积分`
}

const getDateRange = (item) => {
  const start = formatDate(item.start_time)
  const end = formatDate(item.end_time)
  if (!start && !end) return '时间待定'
  return `${start || '待定'} - ${end || '待定'}`
}

const formatDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const eventImageStyle = (item) => {
  const url = item.thumbnail_url || defaultThumbnails[item.category] || '/default-thumbnails/badminton.png'
  return {
    backgroundImage: `linear-gradient(to top, rgba(5, 23, 47, 0.82), rgba(5, 23, 47, 0.12)), url("${url}")`
  }
}

const getCompetitionData = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/competitions/', {
      params: {
        keyword: searchKeyword.value,
        category: category.value
      }
    })
    if (res.data.success) {
      competitionList.value = res.data.competitions || []
    } else {
      ElMessage.error(res.data.msg || '赛事加载失败')
    }
  } catch (error) {
    ElMessage.error('网络异常，赛事加载失败')
  } finally {
    loading.value = false
  }
}

const searchEvent = () => {
  getCompetitionData()
}

const resetFilters = () => {
  searchKeyword.value = ''
  category.value = ''
  statusFilter.value = 'all'
  typeFilter.value = 'all'
  sortMode.value = 'latest'
  favoriteOnly.value = false
  getCompetitionData()
}

watch(category, () => {
  getCompetitionData()
})

onMounted(() => {
  loadFavorites()
  getCompetitionData()
})
</script>

<style scoped>
.home-page {
  min-height: 100%;
  padding: var(--page-padding);
  background: linear-gradient(to bottom, #eaf4ff, #f5f7fa 360px);
}
.hall-hero,
.filter-panel,
.stat-card,
.event-card,
.empty-card {
  background: #fff;
  border: 1px solid #e5edf7;
  border-radius: 8px;
  box-shadow: 0 8px 22px rgba(34, 84, 137, 0.08);
}
.hall-hero {
  max-width: var(--page-max-width);
  margin: 0 auto 16px;
  padding: clamp(20px, 2.4vw, 32px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}
.eyebrow {
  margin: 0 0 6px;
  color: #1677ff;
  font-size: 13px;
  font-weight: 700;
}
.hero-copy h2 {
  margin: 0;
  color: #12355b;
  font-size: clamp(24px, 3vw, 36px);
}
.hero-copy p {
  margin: 10px 0 0;
  color: #61738a;
}
.hero-actions {
  display: flex;
  gap: 10px;
  flex: 0 0 auto;
}
.stats-grid,
.filter-panel,
.event-section {
  max-width: var(--page-max-width);
  margin-left: auto;
  margin-right: auto;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.stat-card {
  min-height: 86px;
  padding: 16px;
  text-align: left;
  cursor: pointer;
}
.stat-card:hover {
  border-color: #9ec5ff;
  background: #f8fbff;
}
.stat-card span {
  color: #66758a;
  font-size: 13px;
}
.stat-card strong {
  display: block;
  margin-top: 6px;
  color: #12355b;
  font-size: 28px;
}
.filter-panel {
  padding: 16px;
  margin-bottom: 20px;
}
.search-line {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  margin-bottom: 14px;
}
.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14px 18px;
  align-items: center;
}
.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.filter-group > span {
  color: #66758a;
  font-size: 13px;
  white-space: nowrap;
}
.category-filter {
  flex: 1 1 520px;
}
.compact-select {
  width: 150px;
}
.favorite-toggle {
  margin-left: auto;
}
.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}
.section-head h3 {
  margin: 0;
  color: #12355b;
  font-size: 20px;
}
.section-head p {
  margin: 6px 0 0;
  color: #667085;
}
.event-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 310px), 1fr));
  gap: 18px;
}
.event-card {
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.event-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(34, 84, 137, 0.16);
}
.skeleton-card {
  min-height: 330px;
  padding: 18px;
  cursor: default;
}
.card-image {
  position: relative;
  aspect-ratio: 16 / 9;
  min-height: 190px;
  background-size: cover;
  background-position: center;
}
.favorite-button {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 50%;
  color: #fff;
  background: rgba(8, 28, 54, 0.64);
  cursor: pointer;
}
.favorite-button.active {
  color: #facc15;
  background: rgba(8, 28, 54, 0.82);
}
.tag-row {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 92px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tag {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 3px 9px;
  color: #fff;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 700;
}
.category-tag {
  background: #1677ff;
}
.status-tag {
  position: absolute;
  top: 54px;
  right: 12px;
}
.green { background: #52c41a; }
.orange { background: #fa8c16; }
.primary { background: #1d4ed8; }
.gray { background: #8c8c8c; }
.red { background: #f56c6c; }
.card-overlay {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 18px;
  color: #fff;
}
.event-no {
  margin: 0 0 4px;
  font-size: 12px;
  opacity: 0.86;
}
.card-overlay h3 {
  margin: 0 0 10px;
  font-size: 22px;
}
.meta-line {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  opacity: 0.92;
}
.meta-line span,
.time-line {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.card-body {
  padding: 16px;
}
.time-line {
  color: #61738a;
  margin-bottom: 14px;
}
.capacity-line,
.card-footer,
.card-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.capacity-line,
.card-footer {
  justify-content: space-between;
}
.capacity-line {
  color: #667085;
  font-size: 13px;
  margin-bottom: 8px;
}
.capacity-line strong {
  color: #12355b;
}
.card-footer {
  margin-top: 14px;
}
.card-actions {
  flex: 0 0 auto;
}
.reward-text {
  color: #475467;
  font-weight: 700;
}
.empty-card {
  padding: 48px 18px;
}
@media (max-width: 900px) {
  .hall-hero {
    align-items: flex-start;
    flex-direction: column;
  }
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 680px) {
  .search-line,
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .hero-actions,
  .filter-group,
  .filter-group :deep(.el-radio-group),
  .compact-select,
  .favorite-toggle {
    width: 100%;
  }
  .filter-group {
    align-items: stretch;
    flex-direction: column;
  }
  .filter-group :deep(.el-radio-group) {
    overflow-x: auto;
    flex-wrap: nowrap;
  }
  .card-footer {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>

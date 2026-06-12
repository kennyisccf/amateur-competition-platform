<template>
  <div class="home-page">

    <!-- 顶部区域 -->
    <div class="header-section">
      <h2>
        找 <span>精彩赛事</span>，上乐赛
      </h2>

      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜赛事名称、项目或编号，例如 NO.00000001"
          @keyup.enter="searchEvent"
        />

        <el-button
          type="primary"
          @click="searchEvent"
        >
          搜索
        </el-button>
        <el-select v-model="sortMode" class="sort-select" placeholder="排序">
          <el-option label="最新发布" value="latest" />
          <el-option label="报名最多" value="popular" />
          <el-option label="名额紧张" value="filling" />
        </el-select>
      </div>

      <div class="category-tabs">
        <el-radio-group v-model="category">

          <el-radio-button value="">全部品类</el-radio-button>

          <el-radio-button value="篮球">篮球</el-radio-button>

          <el-radio-button value="足球">足球</el-radio-button>

          <el-radio-button value="羽毛球">羽毛球</el-radio-button>

          <el-radio-button value="网球">网球</el-radio-button>

          <el-radio-button value="电竞">电竞</el-radio-button>

          <el-radio-button value="棋牌桌游">棋牌桌游</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div class="event-section">

      <div class="section-head">
        <div>
          <div class="section-title">赛事大厅</div>
          <div class="section-subtitle">
            共 {{ hallStats.total }} 场赛事，{{ hallStats.open }} 场正在报名，{{ hallStats.running }} 场进行中
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">
        加载赛事中...
      </div>
      <el-empty v-else-if="competitionList.length === 0" description="暂无赛事"/>

      <div v-else class="event-grid">

        <div
          class="event-card"
          v-for="item in visibleCompetitionList"
          :key="item.id"
          @click="goToDetail(item.id)"
        >

          <div class="card-image" :class="{ 'has-image': item.thumbnail_url }" :style="eventImageStyle(item)">
            <span
              class="tag category-tag"
              :class="String(item.category || '').includes('电竞') ? 'purple' : 'blue'"
            >
              {{ item.category || '其他' }}
            </span>
            <span
              class="tag type-tag"
              :class="item.type === 'PRIVATE' ? 'orange' : 'green'"
            >
              {{ item.type === 'PRIVATE' ? '私人赛' : '公开赛' }}
            </span>
            <span class="tag status-tag" :class="getStatusClass(item.status)">
              {{ getStatusText(item.status) }}
            </span>

            <div class="card-overlay">
              <p class="event-no">{{ item.competition_no }}</p>
              <h3>{{ displayTitle(item) }}</h3>
              <p>地点：{{ item.location || '待公布' }}</p>
              <p>赛制：{{ formatRule(item) }}</p>
            </div>
          </div>
          <div class="card-footer">
            <div class="participant-block">
              <span>已报名：{{ item.current_participants }}/{{ item.max_participants }}</span>
              <el-progress
                :percentage="getFillPercent(item)"
                :show-text="false"
                :stroke-width="6"
              />
            </div>
            <div class="reward-text">
              {{ getRewardText(item) }}
            </div>
          </div>

        </div>

      </div>

    </div>

  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()

const loading = ref(false)

const searchKeyword = ref('')

const category = ref('')

const competitionList = ref([])

const sortMode = ref('latest')

const hallStats = computed(() => ({
  total: competitionList.value.length,
  open: competitionList.value.filter(item => item.status === 1).length,
  running: competitionList.value.filter(item => item.status === 2).length
}))

const visibleCompetitionList = computed(() => {
  const list = [...competitionList.value]
  if (sortMode.value === 'popular') {
    return list.sort((a, b) => Number(b.current_participants || 0) - Number(a.current_participants || 0))
  }
  if (sortMode.value === 'filling') {
    return list.sort((a, b) => getFillPercent(b) - getFillPercent(a))
  }
  return list.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
})

const goToDetail = (id) => {
  router.push(`/event-detail/${id}`)
}

const formatRule = (item) => {
  return item.competition_format_text || '单淘汰'
}

const displayTitle = (item) => String(item.title || '').trim() || '未命名赛事'

const getStatusText = (status) => ({
  1: '报名中',
  2: '进行中',
  3: '已结束',
  4: '已驳回'
}[status] || '待审核')

const getStatusClass = (status) => ({
  1: 'green',
  2: 'primary',
  3: 'gray',
  4: 'red'
}[status] || 'orange')

const getFillPercent = (item) => {
  const max = Number(item.max_participants || 0)
  if (!max) return 0
  return Math.min(100, Math.round(Number(item.current_participants || 0) / max * 100))
}

const getRewardText = (item) => {
  if (item.type === 'PRIVATE') return '私人赛无积分'
  return `奖励积分：${item.reward_points || 0}`
}

const eventImageStyle = (item) => {
  if (!item.thumbnail_url) return {}
  return {
    backgroundImage: `linear-gradient(to top, rgba(5, 23, 47, 0.78), rgba(5, 23, 47, 0.18)), url("${item.thumbnail_url}")`
  }
}

const getCompetitionData = async () => {

  loading.value = true

  try {

    const res = await request.get(
      '/api/competitions/',
      {
        params: {
          keyword: searchKeyword.value,
          category: category.value
        }
      }
    )

    if (res.data.success) {

      competitionList.value =
        res.data.competitions

    } else {

      ElMessage.error(
        res.data.msg || '加载失败'
      )

    }

  } catch (error) {

    ElMessage.error('无法连接服务器')

  } finally {

    loading.value = false

  }
}

const searchEvent = () => {
  getCompetitionData()
}

watch(category, () => {
  getCompetitionData()
})

onMounted(() => {
  getCompetitionData()
})
</script>

<style scoped>

.home-page {
  min-height: 100%;
  padding: clamp(22px, 3vw, 36px) clamp(16px, 4vw, 60px);
  background: linear-gradient(
    to bottom,
    #eaf4ff,
    #f5f7fa
  );
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
}

.header-section h2 {
  font-size: 32px;
  margin-bottom: 20px;
}

.header-section span {
  color: #1677ff;
}

.search-bar {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.search-bar .el-input {
  width: 420px;
}

.sort-select {
  width: 132px;
}

.category-tabs {
  display: flex;
  justify-content: center;
}

.event-section {
  max-width: min(1360px, 100%);
  margin: 0 auto;
}

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
}

.section-subtitle {
  margin-top: 6px;
  color: #667085;
  font-size: 14px;
}

.event-grid {
  display: grid;
  grid-template-columns:
    repeat(auto-fill, minmax(min(100%, 290px), 1fr));
  gap: 24px;
}

.event-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all .2s;
  box-shadow:
    0 4px 12px rgba(0,0,0,.08);
}

.event-card:hover {
  transform: translateY(-5px);
  box-shadow:
    0 8px 20px rgba(0,0,0,.15);
}

.card-image {
  position: relative;
  aspect-ratio: 16 / 9;
  min-height: 180px;
  height: auto;
  background:
    linear-gradient(
      135deg,
      #4facfe,
      #00f2fe
    );
  background-size: cover;
  background-position: center;
}
.card-image.has-image {
  background-size: cover;
  background-position: center;
}

.tag {
  position: absolute;
  top: 12px;
  left: 12px;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
}
.type-tag {
  left: 92px;
}
.category-tag{
  left: 12px;
}
.status-tag {
  left: auto;
  right: 12px;
}
.green {
  background: #52c41a;
}
.orange {
  background: #fa8c16;
}
.blue {
  background: #1677ff;
}
.primary {
  background: #1d4ed8;
}

.gray {
  background: #8c8c8c;
}

.red {
  background: #f56c6c;
}

.purple {
  background: #722ed1;
}

.card-overlay {

  position: absolute;

  bottom: 0;

  left: 0;

  right: 0;

  padding: 20px;

  color: white;

  background:
    linear-gradient(
      to top,
      rgba(0,0,0,.7),
      transparent
    );
}

.card-overlay h3 {

  margin: 0 0 8px;

  font-size: 22px;
}
.event-no {
  font-size: 13px;
  opacity: 0.9;
  margin: 0 0 4px;
}

.card-footer {

  padding: 16px;

  display: flex;

  justify-content: space-between;
  gap: 14px;

  font-size: 14px;

  color: #666;
}

.participant-block {
  flex: 1;
  min-width: 0;
}

.participant-block span {
  display: block;
  margin-bottom: 8px;
}

.reward-text {
  color: #475467;
  white-space: nowrap;
}

.loading {

  text-align: center;

  padding: 80px;

  font-size: 18px;

  color: #666;
}

@media (max-width: 768px) {
  .home-page {
    padding: 22px 16px;
  }

  .header-section h2 {
    font-size: 26px;
  }

  .search-bar .el-input,
  .sort-select {
    width: 100%;
  }

  .event-grid {
    grid-template-columns: 1fr;
  }

  .category-tabs {
    justify-content: flex-start;
    overflow-x: auto;
    padding-bottom: 2px;
  }
}

</style>

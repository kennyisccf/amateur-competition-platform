<template>
  <div class="home-page">

    <!-- 顶部区域 -->
    <div class="header-section">
      <h2>
        找 <span>精彩赛事</span>，上乐赛
      </h2>

      <!-- 搜索框 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜赛事、找运动项目..."
          @keyup.enter="searchEvent"
        />
        <el-button
          type="primary"
          @click="searchEvent"
        >
          搜索
        </el-button>
      </div>

      <!-- 分类 -->
      <div class="category-tabs">
        <el-radio-group v-model="category">

          <el-radio-button label="">全部品类</el-radio-button>

          <el-radio-button label="篮球">篮球</el-radio-button>

          <el-radio-button label="足球">足球</el-radio-button>

          <el-radio-button label="羽毛球">羽毛球</el-radio-button>

          <el-radio-button label="网球">网球</el-radio-button>

          <el-radio-button label="电竞">电竞</el-radio-button>

          <el-radio-button label="棋牌桌游">棋牌桌游</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 赛事列表 -->
    <div class="event-section">

      <div class="section-title">🔥 正在火热报名中</div>

      <!-- 加载 -->
      <div v-if="loading" class="loading">
        加载赛事中...
      </div>
      <!-- 空数据 -->
      <el-empty v-else-if="competitionList.length === 0" description="暂无赛事"/>

      <!-- 数据 -->
      <div v-else class="event-grid">

        <div
          class="event-card"
          v-for="item in competitionList"
          :key="item.id"
          @click="goToDetail(item.id)"
        >

          <div class="card-image">
            <span
              class="tag category-tag"
              :class="item.category.includes('电竞') ? 'purple' : 'blue'"
            >
              {{ item.category }}
            </span>
            <span
              class="tag type-tag"
              :class="item.type === 'PRIVATE' ? 'orange' : 'green'"
            >
              {{ item.type === 'PRIVATE' ? '私人赛' : '公开赛' }}
            </span>

            <div class="card-overlay">
              <h3>{{ item.title }}</h3>
              <p>📍地点：{{ item.location }}</p>
            </div>
          </div>
          <div class="card-footer">
            <div>已报名：{{ item.current_participants }}/{{ item.max_participants }}</div>
            <div>奖励积分：{{ item.reward_points }}</div>
          </div>

        </div>

      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()

const loading = ref(false)

const searchKeyword = ref('')

const category = ref('')

const competitionList = ref([])

const goToDetail = (id) => {
  router.push(`/event-detail/${id}`)
}

const getCompetitionData = async () => {

  loading.value = true

  try {

    const res = await axios.get(
      'http://localhost:8000/api/competitions/',
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

    console.error(error)

    ElMessage.error('无法连接服务器')

  } finally {

    loading.value = false

  }
}

const searchEvent = () => {
  getCompetitionData()
}
// 
// const searchEvent = async () => {
  // if (inviteCode.value.trim()) {
    // try {
      // const res = await axios.get(
        // `http://localhost:8000/api/competition_by_invite/`,
        // { params: { invite_code: inviteCode.value.trim() } }
      // )
      // if (res.data.success && res.data.competition) {
        // router.push(`/event-detail/${res.data.competition.id}`)
        // return
      // } else {
        // ElMessage.error(res.data.msg || '未找到该私人赛事')
        // return
      // }
    // } catch (err) {
      // console.error(err)
      // ElMessage.error('查询私人赛事失败')
      // return
    // }
  // }
// 
  // 否则按关键字搜索公开赛事
  // getCompetitionData()
// }
watch(category, () => {
  getCompetitionData()
})

onMounted(() => {
  getCompetitionData()
})
</script>

<style scoped>

.home-page {
  min-height: 100vh;
  padding: 30px 60px;
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
}

.search-bar .el-input {
  width: 420px;
}

.category-tabs {
  display: flex;
  justify-content: center;
}

.event-section {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 25px;
}

.event-grid {
  display: grid;
  grid-template-columns:
    repeat(auto-fill, minmax(320px, 1fr));
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
  height: 220px;
  background:
    linear-gradient(
      135deg,
      #4facfe,
      #00f2fe
    );
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
  position: relative;
}
.category-tag{
  position: relative;
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

.card-footer {

  padding: 16px;

  display: flex;

  justify-content: space-between;

  font-size: 14px;

  color: #666;
}

.loading {

  text-align: center;

  padding: 80px;

  font-size: 18px;

  color: #666;
}

</style>
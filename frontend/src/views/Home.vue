<template>
  <div class="home-page">
    <div class="header-section">
      <h2>找 <span>精彩赛事</span>，上乐赛</h2>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜赛事、找战队、查运动项目..." />
        <el-button type="primary" @click="searchEvent">搜索</el-button>
      </div>

      <div class="category-tabs">
        <el-radio-group v-model="category">
          <el-radio-button label="全部品类" />
          <el-radio-button label="篮球/足球" />
          <el-radio-button label="羽毛球/网球" />
          <el-radio-button label="MOBA电竞" />
          <el-radio-button label="射击/FPS" />
          <el-radio-button label="棋牌桌游" />
          <el-radio-button label="同城赛事" />
        </el-radio-group>
      </div>
    </div>

    <div class="event-section">
      <div class="section-title">🔥 正在火热报名中</div>
      <div v-if="loading" class="loading">加载赛事中...</div>
      <div v-else class="event-grid">
        <div class="event-card" v-for="item in competitionList" :key="item.id" @click="goToDetail(item.id)">
          <div class="card-image">
            <span class="tag" :class="item.category.includes('电竞') ? 'purple' : 'blue'">
              {{ item.category }}
            </span>
            <div class="card-overlay">
              <h3>{{ item.title }}</h3>
              <p>{{ item.location }}</p>
            </div>
          </div>
          <div class="card-footer">
            <span>{{ item.current_participants }} / {{ item.max_participants }} 队已报</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const category = ref('全部品类')
const searchKeyword = ref('')
const loading = ref(false)
const competitionList = ref([])

const goToDetail = (id) => router.push(`/event-detail/${id}`)

// 拉取赛事列表
const getCompetitionData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const headers = { 'Authorization': `Bearer ${token}` }
    const res = await axios.get('http://localhost:8000/api/competitions/', { headers })
    if (res.data.success) {
      competitionList.value = res.data.competitions
    }
  } catch (err) {
    ElMessage.error('加载赛事失败')
  } finally { loading.value = false }
}

const searchEvent = () => {
  // 后续可以加搜索逻辑
  getCompetitionData()
}

onMounted(() => {
  getCompetitionData()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  padding: 30px 60px;
  background: linear-gradient(to bottom, #eaf4ff, #f5f7fa);
}
.header-section {
  text-align: center;
  margin-bottom: 40px;
}
.header-section h2 {
  font-size: 26px;
  color: #1a1a1a;
}
.header-section h2 span {
  color: #1677ff;
}
.search-bar {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}
.search-bar .el-input {
  width: 400px;
}
.category-tabs {
  display: flex;
  justify-content: center;
  gap: 8px;
}
.event-section {
  max-width: 1200px;
  margin: 0 auto;
}
.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
}
.event-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.event-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: transform 0.2s;
}
.event-card:hover {
  transform: translateY(-4px);
}
.card-image {
  position: relative;
  height: 200px;
  background: #f0f5ff;
}
.tag {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 8px;
  color: white;
  font-size: 12px;
  border-radius: 4px;
}
.tag.blue { background: #1677ff; }
.tag.purple { background: #722ed1; }
.card-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  color: white;
}
.card-overlay h3 {
  margin: 0 0 8px;
  font-size: 22px;
}
.card-overlay p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}
.card-footer {
  padding: 16px;
  font-size: 14px;
}
.loading {
  text-align: center;
  padding: 50px;
  color: #666;
}
</style>
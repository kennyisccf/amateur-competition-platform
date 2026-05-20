<template>
  <div class="home-page">
    <!-- 顶部标题和搜索 -->
    <div class="header-section">
      <h2>找 <span>精彩赛事</span>，上乐赛</h2>
      <div class="search-bar">
        <el-input placeholder="搜赛事、找战队、查运动项目..." />
        <el-button type="primary">搜索</el-button>
      </div>

      <!-- 分类标签 -->
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

    <!-- 赛事列表区 -->
    <div class="event-section">
      <div class="section-title">🔥 正在火热报名中</div>
      <div class="event-grid">
        <!-- 赛事卡片1 -->
        <div class="event-card">
          <div class="card-image">
           
            <span class="tag blue">传统体育</span>
            <div class="card-overlay">
              <h3>街球狂飙</h3>
              <p>第三届社区三人篮球赛（市中心公园站）</p>
            </div>
          </div>
          <div class="card-footer">
            <span>{{ race1.joinNum }} / {{ race1.totalNum }} 队已报</span>
          </div>
        </div>

        <!-- 赛事卡片2 -->
        <div class="event-card">
          <div class="card-image">
            
            <span class="tag purple">电子竞技</span>
            <div class="card-overlay">
              <h3>暗黑突围</h3>
              <p>“乐赛杯”年度MOBA电竞社群巅峰邀请赛</p>
            </div>
          </div>
          <div class="card-footer">
            <span>{{ race2.joinNum }} / {{ race2.totalNum }} 战队已报</span>
          </div>
        </div>

        <!-- 赛事卡片3 -->
        <div class="event-card">
          <div class="card-image">
            
            <span class="tag blue">传统体育</span>
            <div class="card-overlay">
              <h3>飞羽争锋</h3>
              <p>金秋双打羽毛球大奖赛（公开组）</p>
            </div>
          </div>
          <div class="card-footer">
            <span>{{ race3.joinNum }} / {{ race3.totalNum }} 组已报</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const category = ref('全部品类')

// 空数据 纯等后端接口赋值，无任何固定数字
const race1 = ref({})
const race2 = ref({})
const race3 = ref({})

// 接口请求位置
const getCompetitionData = async () => {
  // const res = await 后端赛事列表接口
  // race1.value = res[0]
  // race2.value = res[1]
  // race3.value = res[2]
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
}
.card-image {
  position: relative;
  height: 200px;
}
.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
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
.tag.blue {
  background: #1677ff;
}
.tag.purple {
  background: #722ed1;
}
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
</style>
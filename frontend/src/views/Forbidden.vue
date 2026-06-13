<template>
  <div class="forbidden-page">
    <section class="forbidden-card">
      <el-result
        icon="warning"
        title="暂无访问权限"
        :sub-title="description"
      >
        <template #extra>
          <el-button type="primary" @click="router.push('/home')">
            返回赛事大厅
          </el-button>
          <el-button @click="router.back()">
            返回上一页
          </el-button>
        </template>
      </el-result>
    </section>

    <section class="role-panel">
      <div class="role-head">
        <p class="eyebrow">权限说明</p>
        <h3>当前账号: {{ currentRoleLabel }}</h3>
      </div>
      <div class="role-grid">
        <div
          v-for="item in roles"
          :key="item.code"
          class="role-card"
          :class="{ active: item.code === currentRole }"
        >
          <div class="role-title">
            <strong>{{ item.label }}</strong>
            <el-tag v-if="item.code === currentRole" size="small" type="success">当前</el-tag>
          </div>
          <p>{{ item.desc }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const currentRole = localStorage.getItem('role') || ''

const roleLabels = {
  PLAYER: '参赛选手',
  ORGANIZER: '主办方',
  ADMIN: '管理员'
}

const roles = [
  {
    code: 'PLAYER',
    label: '参赛选手',
    desc: '可以浏览赛事、报名参赛、查看个人档案、创建私人赛事并和好友沟通。'
  },
  {
    code: 'ORGANIZER',
    label: '主办方',
    desc: '可以创建和维护赛事、管理报名、查看赛程，并处理自己负责的赛事数据。'
  },
  {
    code: 'ADMIN',
    label: '管理员',
    desc: '可以审核赛事、管理平台数据、批量生成测试数据，并执行风控操作。'
  }
]

const currentRoleLabel = computed(() => roleLabels[currentRole] || '未识别角色')

const requiredRoleLabels = computed(() => {
  const raw = String(route.query.need || '')
  if (!raw) return []
  return raw.split(',').map(item => roleLabels[item] || item).filter(Boolean)
})

const description = computed(() => {
  if (!requiredRoleLabels.value.length) {
    return '当前账号不能进入这个页面，请返回赛事大厅或切换合适的账号。'
  }
  return `该页面需要 ${requiredRoleLabels.value.join(' / ')} 权限，当前账号是 ${currentRoleLabel.value}。`
})
</script>

<style scoped>
.forbidden-page {
  width: 100%;
  max-width: min(980px, 100%);
  margin: 0 auto;
  padding: var(--page-padding);
}
.forbidden-card,
.role-panel {
  background: #fff;
  border: 1px solid #e5edf7;
  border-radius: 8px;
  box-shadow: 0 8px 22px rgba(34, 84, 137, 0.08);
}
.forbidden-card {
  margin-bottom: 18px;
}
.role-panel {
  padding: 22px;
}
.role-head {
  margin-bottom: 16px;
}
.eyebrow {
  margin: 0 0 6px;
  color: #1677ff;
  font-weight: 700;
  font-size: 13px;
}
.role-head h3 {
  margin: 0;
  color: #12355b;
}
.role-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
.role-card {
  min-height: 130px;
  padding: 16px;
  border: 1px solid #e8eef6;
  border-radius: 8px;
  background: #fbfdff;
}
.role-card.active {
  border-color: #34a853;
  background: #f4fbf7;
}
.role-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}
.role-title strong {
  color: #132f4c;
}
.role-card p {
  margin: 0;
  color: #61738a;
  line-height: 1.6;
}
@media (max-width: 760px) {
  .role-grid {
    grid-template-columns: 1fr;
  }
}
</style>

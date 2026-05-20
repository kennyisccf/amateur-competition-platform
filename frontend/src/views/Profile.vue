<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人资料</span>
          <el-button type="primary" link @click="editMode = !editMode">
            {{ editMode ? '取消' : '编辑' }}
          </el-button>
        </div>
      </template>

      <el-form :model="profile" label-width="100px" :disabled="!editMode">
        <el-form-item label="头像">
          <div class="avatar-wrapper">
            <el-avatar :size="80" :src="profile.avatar" />
            <el-button v-if="editMode" type="primary" link @click="uploadAvatar">更换头像</el-button>
          </div>
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="profile.username" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="profile.nickname" />
        </el-form-item>
        <el-form-item label="个人总积分">
          <el-input-number v-model="profile.totalPoints" :min="0" :disabled="!editMode" />
        </el-form-item>
        <el-form-item v-if="editMode">
          <el-button type="primary" @click="saveProfile">保存修改</el-button>
          <el-button @click="editMode = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="my-events-card">
      <template #header>
        <span>我的参赛记录</span>
      </template>
      <el-table :data="myEvents" style="width: 100%">
        <el-table-column prop="name" label="赛事名称" />
        <el-table-column prop="date" label="比赛时间" />
        <el-table-column prop="points" label="获得积分" sortable />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === '已结束' ? 'info' : 'success'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewEvent(row.id)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const editMode = ref(false)

const profile = ref({
  avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
  username: 'player123',
  nickname: '篮球小子',
  totalPoints: 1250
})

const myEvents = ref([
  { id: 1, name: '街球狂飙', date: '2025-07-15', points: 350, status: '已结束' },
  { id: 2, name: '暗黑突围', date: '2025-08-20', points: 480, status: '已结束' },
  { id: 3, name: '飞羽争锋', date: '2025-09-10', points: null, status: '报名中' }
])

const saveProfile = () => {
  ElMessage.success('保存成功（演示）')
  editMode.value = false
}

const uploadAvatar = () => {
  ElMessage.info('头像上传功能待集成')
}

const viewEvent = (id) => {
  router.push(`/event/${id}`)
}
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 0 20px;
}
.profile-card {
  margin-bottom: 24px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.avatar-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}
.my-events-card {
  margin-bottom: 24px;
}
</style>
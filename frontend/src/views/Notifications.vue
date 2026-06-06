<template>
  <div class="notification-container">
    <h2>我的通知</h2>

    <el-table
      :data="notificationList"
      border
      v-loading="loading"
    >
      <el-table-column
        prop="content"
        label="通知内容"
      />

      <el-table-column
        prop="is_read"
        label="状态"
        width="100"
      >
        <template #default="scope">
          <el-tag
            :type="scope.row.is_read ? 'success' : 'danger'"
          >
            {{ scope.row.is_read ? '已读' : '未读' }}
          </el-tag>
        </template>


      </el-table-column>

      <el-table-column
        prop="created_at"
        label="时间"
        width="180"
      />

      <el-table-column
        label="操作"
        width="120"
        fixed="right"
      >
        <template #default="scope">
          <el-button size="small" type="danger" @click="deleteNotification(scope.row.id)">删除</el-button>
          
          
        </template>  
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref,onMounted } from 'vue'
import axios from 'axios'
import { ElMessage , ElMessageBox} from 'element-plus'
import { useRouter } from 'vue-router'
const router = useRouter()
const loading = ref(false)
const notificationList = ref([])

const loadNotifications = async () => {
  loading.value = true

  try {
    const res = await axios.get(
      'http://localhost:8000/api/notifications/',
      {
        withCredentials:true
      }
    )

    if(res.data.success){
      notificationList.value = res.data.notifications
    }

  } catch(err){
    ElMessage.error('加载通知失败')
  } finally{
    loading.value = false
  }
}

const readAll = async () => {
  await axios.post(
    'http://localhost:8000/api/read_all_notifications/',
    {},
    {
      withCredentials:true
    }
  )
}
const deleteNotification = async(id)=>{
  try{
    await ElMessageBox.confirm(
      '确定删除该通知吗？',
      '提示',
      {
        type:'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      }
    )
    const res = await axios.post(
      'http://localhost:8000/api/delete_notification/',
      {
        notification_id:id
      },
      {
        withCredentials:true
      }
    )
    if(res.data.success){
      ElMessage.success('删除成功')
      loadNotifications()
    }

  }catch(err){
    console.log(err)
  }
}
onMounted(async()=>{
  await readAll()
  await loadNotifications()
})
</script>

<style scoped>
.notification-container {
  padding: 24px;
}
.header-bar{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:20px;
}
.competition-link {
  color: #1677ff;
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;
  margin: 0 4px;
}

.competition-link:hover {
  color: #409eff;
  text-decoration: underline;
}
</style>
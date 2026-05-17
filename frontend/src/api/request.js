import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api', 
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 可以在这里统一加 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    // 这里可以根据后端约定的 code 处理
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  error => {
    ElMessage.error(error.message || '网络异常')
    return Promise.reject(error)
  }
)

export default request
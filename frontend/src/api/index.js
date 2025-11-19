import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    const data = response.data
    // 确保返回的数据格式正确
    // 如果后端返回的是对象但应该是数组，进行转换
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      // 检查是否是类似 {0: {...}, 1: {...}} 的格式
      const keys = Object.keys(data)
      if (keys.length > 0 && keys.every(key => /^\d+$/.test(key))) {
        // 转换为数组
        return Object.values(data)
      }
    }
    return data
  },
  error => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default api


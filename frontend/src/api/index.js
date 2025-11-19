import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5分钟超时（UI测试可能需要更长时间）
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
    
    // 只处理明显错误的数据格式（数字键对象转数组）
    // 不进行深度清理，避免破坏正常数据结构
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      const keys = Object.keys(data)
      // 只有当所有键都是数字且至少有一个键时，才进行转换
      if (keys.length > 0 && keys.every(key => /^\d+$/.test(key))) {
        // 转换为数组，按数字键排序
        const sortedKeys = keys.map(Number).sort((a, b) => a - b)
        const converted = sortedKeys.map(key => data[String(key)])
        console.warn('API响应数据格式已转换（数字键对象 -> 数组）:', response.config.url, converted)
        return converted
      }
    }
    
    // 确保数组数据确实是数组
    if (Array.isArray(data)) {
      // 验证数组中的每个元素都是对象（不是数字键对象）
      const hasNumericKeys = data.some(item => 
        item && typeof item === 'object' && 
        Object.keys(item).some(key => /^\d+$/.test(key))
      )
      if (hasNumericKeys) {
        console.warn('检测到数组中的对象包含数字键:', response.config.url)
      }
    }
    
    // 直接返回数据，不进行深度处理
    return data
  },
  error => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default api


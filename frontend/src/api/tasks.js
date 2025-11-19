import api from './index'

export const taskApi = {
  getTaskStatus(taskId) {
    return api.get(`/tasks/${taskId}`, {
      timeout: 30000 // 30秒超时（查询状态不需要太长时间）
    })
  }
}


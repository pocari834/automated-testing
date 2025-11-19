import api from './index'

export const taskApi = {
  getTaskStatus(taskId) {
    return api.get(`/tasks/${taskId}`)
  }
}


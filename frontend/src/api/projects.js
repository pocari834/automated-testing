import api from './index'

export const projectApi = {
  // 获取项目列表
  getProjects(params) {
    return api.get('/projects', { params })
  },
  // 获取项目详情
  getProject(id) {
    return api.get(`/projects/${id}`)
  },
  // 创建项目
  createProject(data) {
    return api.post('/projects', data)
  },
  // 更新项目
  updateProject(id, data) {
    return api.put(`/projects/${id}`, data)
  },
  // 删除项目
  deleteProject(id) {
    return api.delete(`/projects/${id}`)
  }
}


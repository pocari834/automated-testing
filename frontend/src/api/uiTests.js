import api from './index'

export const uiTestApi = {
  getCases(params) {
    return api.get('/ui_tests/cases', { params })
  },
  getCase(id) {
    return api.get(`/ui_tests/cases/${id}`)
  },
  createCase(data) {
    return api.post('/ui_tests/cases', data)
  },
  updateCase(id, data) {
    return api.put(`/ui_tests/cases/${id}`, data)
  },
  deleteCase(id) {
    return api.delete(`/ui_tests/cases/${id}`)
  },
  runCase(id) {
    return api.post(`/ui_tests/run/${id}`)
  }
}


import api from './index'

export const reportApi = {
  getReports(params) {
    return api.get('/reports', { params })
  },
  getReport(id) {
    return api.get(`/reports/${id}`)
  }
}


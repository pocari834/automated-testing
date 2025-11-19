import api from './index'

export const performanceTestApi = {
  getTests(params) {
    return api.get('/performance_tests', { params })
  },
  getTest(id) {
    return api.get(`/performance_tests/${id}`)
  },
  createTest(data) {
    return api.post('/performance_tests', data)
  },
  updateTest(id, data) {
    return api.put(`/performance_tests/${id}`, data)
  },
  deleteTest(id) {
    return api.delete(`/performance_tests/${id}`)
  },
  uploadJmx(id, file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/performance_tests/upload/${id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  runTest(id) {
    return api.post(`/performance_tests/run/${id}`)
  }
}


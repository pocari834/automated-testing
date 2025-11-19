import api from './index'

export const apiTestApi = {
  // 用例
  getCases(params) {
    return api.get('/api_tests/cases', { params })
  },
  getCase(id) {
    return api.get(`/api_tests/cases/${id}`)
  },
  createCase(data) {
    return api.post('/api_tests/cases', data)
  },
  updateCase(id, data) {
    return api.put(`/api_tests/cases/${id}`, data)
  },
  deleteCase(id) {
    return api.delete(`/api_tests/cases/${id}`)
  },
  // 套件
  getSuites(params) {
    return api.get('/api_tests/suites', { params })
  },
  getSuite(id) {
    return api.get(`/api_tests/suites/${id}`)
  },
  createSuite(data) {
    return api.post('/api_tests/suites', data)
  },
  updateSuite(id, data) {
    return api.put(`/api_tests/suites/${id}`, data)
  },
  deleteSuite(id) {
    return api.delete(`/api_tests/suites/${id}`)
  },
  // 执行
  runCase(id) {
    return api.post(`/api_tests/run/${id}`)
  },
  runSuite(id) {
    return api.post(`/api_tests/run_suite/${id}`)
  }
}


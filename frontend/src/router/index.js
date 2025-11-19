import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/projects',
    children: [
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/Projects.vue'),
        meta: { title: '项目管理', icon: 'Folder' }
      },
      {
        path: 'api-tests',
        name: 'APITests',
        component: () => import('@/views/APITests.vue'),
        meta: { title: 'API测试', icon: 'Connection' }
      },
      {
        path: 'ui-tests',
        name: 'UITests',
        component: () => import('@/views/UITests.vue'),
        meta: { title: 'UI测试', icon: 'Monitor' }
      },
      {
        path: 'performance-tests',
        name: 'PerformanceTests',
        component: () => import('@/views/PerformanceTests.vue'),
        meta: { title: '性能测试', icon: 'DataAnalysis' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/Reports.vue'),
        meta: { title: '测试报告', icon: 'Document' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router


import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/equipment' },
  { path: '/equipment', component: () => import('../views/Equipment.vue') },
  { path: '/borrow', component: () => import('../views/BorrowRecords.vue') },
  { path: '/scores', component: () => import('../views/Scores.vue') },
  { path: '/exams', component: () => import('../views/Exams.vue') },
  { path: '/statistics', component: () => import('../views/Statistics.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

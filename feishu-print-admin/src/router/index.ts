import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/',
      component: () => import('@/views/Layout.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: { title: '仪表盘' }
        },
        {
          path: 'users',
          name: 'users',
          component: () => import('@/views/UserManage.vue'),
          meta: { title: '用户管理' }
        },
        {
          path: 'feedbacks',
          name: 'feedbacks',
          component: () => import('@/views/FeedbackManage.vue'),
          meta: { title: '反馈管理' }
        },
        {
          path: 'orders',
          name: 'orders',
          component: () => import('@/views/OrderManage.vue'),
          meta: { title: '订单管理' }
        },
        {
          path: 'promos',
          name: 'promos',
          component: () => import('@/views/PromoManage.vue'),
          meta: { title: '邀请码管理' }
        },
        {
          path: 'plans',
          name: 'plans',
          component: () => import('@/views/PlanManage.vue'),
          meta: { title: '会员价格管理' }
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router

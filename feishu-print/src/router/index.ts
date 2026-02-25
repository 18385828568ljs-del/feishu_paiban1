import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/library',
      name: 'library',
      component: () => import('@/views/TemplateLibrary.vue')
    },
    {
      path: '/editor',
      name: 'editor',
      component: () => import('@/views/EditorPage.vue')
    },
    {
      path: '/ai-generate',
      name: 'ai-generate',
      component: () => import('@/views/AIGenerate.vue')
    },
    {
      path: '/templates',
      name: 'templates',
      redirect: '/library'
    },
    {
      path: '/sign/:token',
      name: 'signature',
      component: () => import('@/views/SignaturePage.vue')
    },
    {
      path: '/team',
      name: 'team',
      component: () => import('@/views/TeamPage.vue')
    },
    {
      path: '/pricing',
      name: 'pricing',
      component: () => import('@/views/PricingPage.vue')
    },
    {
      path: '/debug-auth',
      name: 'debug-auth',
      component: () => import('@/views/DebugAuth.vue')
    }
  ]
});

export default router;

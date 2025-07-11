import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/pages/Home.vue';
import Road from '@/pages/Road.vue';
import Face from '@/pages/Face.vue';
import Log from '@/pages/Log.vue';
import Traffic from '@/pages/Traffic.vue';
import UserManagement from '@/pages/UserManagement.vue';
import ChangePassword from '@/pages/ChangePassword.vue';
import Approval from '@/pages/Approval.vue';
import AllViews from '@/pages/AllViews.vue';
import { ElNotification } from 'element-plus'; // Import ElNotification

const routes = [
  {
    path: '/',
    name: 'AllViews',
    component: AllViews,
    meta: { guest: true } // Mark this as a guest-only route
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/road',
    name: 'Road',
    component: Road,
    meta: { requiresAuth: true }
  },
  {
    path: '/face',
    name: 'Face',
    component: Face,
    meta: { requiresAuth: true },
    beforeEnter: (to, from, next) => {
      const userClass = localStorage.getItem('user-class');
      // Corrected the condition to check for Chinese role names
      if (userClass && (userClass.trim() === '认证用户' || userClass.trim() === '管理员')) {
        ElNotification({
          title: '访问限制',
          message: '您已是认证用户，无需再次进入认证页面。',
          type: 'info',
        });
        // Redirect to home page
        return next({ name: 'Home' });
      }
      // Allow navigation
      next();
    }
  },
  {
    path: '/log',
    name: 'Log',
    component: Log,
    meta: { requiresAuth: true }
  },
  {
    path: '/traffic',
    name: 'Traffic',
    component: Traffic,
    meta: { requiresAuth: true }
  },
  {
    path: '/user-management',
    name: 'UserManagement',
    component: UserManagement,
    meta: { requiresAuth: true }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: ChangePassword,
    meta: { requiresAuth: true }
  },
  {
    path: '/approval',
    name: 'Approval',
    component: Approval,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userClass = localStorage.getItem('user-class'); 
  const isAuthenticated = !!token;

  if (to.meta.requiresAuth && !isAuthenticated) {
    ElNotification({
      title: '访问受限',
      message: '此页面需要登录，请先登录。',
      type: 'warning'
    });
    return next('/');
  }

  if (to.meta.requiresAdmin && userClass?.trim() !== '管理员') {
    ElNotification({
      title: '权限不足',
      message: '您没有权限访问此页面。',
      type: 'error'
    });
    return next('/home');
  }
  
  // 如果用户已登录，但尝试访问访客页面（如登录页），则重定向到主页
  if (isAuthenticated && to.meta.guest) {
      return next('/home');
  }

  next();
});

export default router; 
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
import { ElNotification, ElMessage, ElMessageBox } from 'element-plus'; // 引入所需组件
import { getUserStatus } from '@/api/user'; // 引入API
import { cleanupFaceData } from '@/api/face'; // 引入清理API
import { useMainStore } from '@/store'; // 引入store

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
    beforeEnter: async (to, from, next) => {
      const userClass = localStorage.getItem('user-class')?.trim();
      const store = useMainStore(); // 获取store实例
      
      // 逻辑1: 已认证用户禁止访问 - 此段逻辑将被移除或修改
      // if (userClass === '认证用户') {
      //   ElNotification({
      //     title: '访问限制',
      //     message: '您已是认证用户，无需再次进入认证页面。',
      //     type: 'info',
      //   });
      //   return next({ name: 'Home' });
      // }

      // 逻辑2: 普通用户根据状态进行不同处理
      if (userClass === '普通用户') {
        try {
          const status = await getUserStatus();
          const faceStatus = status.face_registration_status;

          if (faceStatus === 'approved') {
            store.setFaceAuthNotificationStatus('none');
            ElMessageBox.alert('恭喜！您的认证已通过审核。为了使新权限生效，系统将自动为您退出登录。', '认证成功', {
              confirmButtonText: '好的',
              callback: () => {
                store.logout();
              },
            });
            return next(false);
          }

          if (faceStatus === 'rejected') {
            store.setFaceAuthNotificationStatus('none');
            ElMessageBox.confirm(
              '您的认证申请已被拒绝。是否立即删除旧的认证数据并重新尝试？',
              '认证失败',
              {
                confirmButtonText: '删除并重试',
                cancelButtonText: '取消',
                type: 'warning',
              }
            ).then(async () => {
              await cleanupFaceData();
              next();
            }).catch(() => {
              next(false);
            });
            return;
          }

          if (faceStatus === 'pending') {
            ElMessage.info('您的认证申请正在审核中，请耐心等待。');
            return next(false);
          }

          // 对于'not_registered'等其他情况，允许进入
          return next();

        } catch (error) {
          console.error("在路由守卫中获取用户状态失败:", error);
          // 如果API调用失败，为避免卡住用户，也允许导航
          return next();
        }
      }

      // 逻辑3: 其他情况（如管理员）允许访问
      store.setFaceAuthNotificationStatus('none');
      return next();
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
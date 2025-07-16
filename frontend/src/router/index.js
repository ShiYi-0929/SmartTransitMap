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
import AdminRoad from '@/pages/AdminRoad.vue'; // 保留新增的AdminRoad路由
import { ElNotification, ElMessage, ElMessageBox } from 'element-plus'; // 整合所有需要的组件
import { getUserProfile } from '@/api/user'; // 保留你的getUserProfile API
import { getUserStatus } from '@/api/user'; // 新增第一个版本的getUserStatus API
import { cleanupFaceData } from '@/api/face'; // 新增清理API
import { useMainStore } from '@/store'; // 新增store引入

const routes = [
  {
    path: '/',
    name: 'AllViews',
    component: AllViews,
    meta: { guest: true } // 访客页标记
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
    path: '/admin-road',
    name: 'AdminRoad',
    component: AdminRoad,
    meta: { requiresAuth: true, requiresAdmin: true } // 保留管理员路由
  },
  {
    path: '/face',
    name: 'Face',
    component: Face,
    meta: { requiresAuth: true },
    // 整合第一个版本的beforeEnter逻辑，保留更详细的认证状态处理
    beforeEnter: async (to, from, next) => {
      const userClass = localStorage.getItem('user-class')?.trim();
      const store = useMainStore(); // 获取store实例
      
      // 逻辑1: 已认证用户禁止访问
      if (userClass === '认证用户') {
        ElNotification({
          title: '访问限制',
          message: '您已是认证用户，无需再次进入认证页面。',
          type: 'info',
        });
        return next({ name: 'Home' });
      }

      // 逻辑2: 普通用户根据状态进行不同处理
      if (userClass === '普通用户') {
        try {
          const status = await getUserStatus(); // 使用getUserStatus获取认证状态
          const faceStatus = status.face_registration_status;

          if (faceStatus === 'approved') {
            store.setFaceAuthNotificationStatus('none');
            ElMessageBox.alert('恭喜！您的认证已通过审核。为了使新权限生效，系统将自动为您退出登录。', '认证成功', {
              confirmButtonText: '好的',
              callback: () => {
                store.logout(); // 调用store的登出方法
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
              await cleanupFaceData(); // 调用清理API
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
          // 如果API调用失败，允许导航（避免卡住用户）
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

// 整合全局导航守卫，保留第二个版本的动态用户类型判断和road/admin-road跳转逻辑
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token');
  let userClass = localStorage.getItem('user-class');
  const isAuthenticated = !!token;

  // 需要登录但未登录
  if (to.meta.requiresAuth && !isAuthenticated) {
    ElNotification({
      title: '访问受限',
      message: '此页面需要登录，请先登录。',
      type: 'warning'
    });
    return next('/');
  }

  // 动态判断用户类型，处理road和admin-road跳转
  if (isAuthenticated && (!userClass || to.path === '/road' || to.path === '/admin-road')) {
    try {
      // 优先用缓存，没有就请求
      if (!userClass) {
        const res = await getUserProfile(); // 使用你的getUserProfile获取用户信息
        userClass = res.data.user_class;
        localStorage.setItem('user-class', userClass);
      }
      // 认证用户访问 /road，管理员访问 /admin-road
      if (to.path === '/road' && userClass === '管理员') {
        return next('/admin-road');
      }
      if (to.path === '/admin-road' && userClass !== '管理员') {
        return next('/road');
      }
    } catch (e) {
      // 获取用户信息失败，强制退出
      localStorage.removeItem('token');
      localStorage.removeItem('user-class');
      ElNotification({
        title: '登录失效',
        message: '请重新登录。',
        type: 'error'
      });
      return next('/');
    }
  }

  // 管理员权限校验
  if (to.meta.requiresAdmin && userClass?.trim() !== '管理员') {
    ElNotification({
      title: '权限不足',
      message: '您没有权限访问此页面。',
      type: 'error'
    });
    return next('/home');
  }

  // 已登录用户访问访客页
  if (isAuthenticated && to.meta.guest) {
    return next('/home');
  }

  next();
});

export default router;

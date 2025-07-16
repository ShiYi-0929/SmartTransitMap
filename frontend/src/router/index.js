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
    // 使用返回值方式实现导航守卫，避免 async+next 的组合导致 "Invalid navigation guard" 错误
    beforeEnter: async (to, from) => {
      const userClass = localStorage.getItem('user-class')?.trim();
      const store = useMainStore();

      // 1) 已认证用户直接放行
      if (userClass === '认证用户') {
        return true;
      }

      // 2) 普通用户根据后端状态决定
      if (userClass === '普通用户') {
        try {
          const status = await getUserStatus();
          const faceStatus = status.face_registration_status;

          // 2-A 审核通过 → 通知后登出，中止导航
          if (faceStatus === 'approved') {
            await ElMessageBox.alert(
              '恭喜！您的认证已通过审核。为了使新权限生效，系统将自动为您退出登录。',
              '认证成功',
              { confirmButtonText: '好的' }
            );
            store.logout();
            return false; // 取消当前导航
          }

          // 2-B 被拒绝 → 询问是否删除后重试
          if (faceStatus === 'rejected') {
            const confirm = await ElMessageBox.confirm(
              '您的认证申请已被拒绝。是否立即删除旧的认证数据并重新尝试？',
              '认证失败',
              {
                confirmButtonText: '删除并重试',
                cancelButtonText: '取消',
                type: 'warning',
              }
            ).catch(() => false);

            if (confirm) {
              await cleanupFaceData();
              store.setFaceAuthNotificationStatus('none');
              return true; // 允许进入重新认证
            }
            return false; // 用户取消
          }

          // 2-C 待审核 → 提示并阻止进入
          if (faceStatus === 'pending') {
            ElMessage.info('您的认证申请正在审核中，请耐心等待。');
            return false;
          }

          // 其他状态（如 not_registered）允许进入
          return true;

        } catch (error) {
          console.error('在路由守卫中获取用户状态失败:', error);
          return true; // 避免因异常阻止导航
        }
      }

      // 3) 其他用户类型（如管理员）
      return true;
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

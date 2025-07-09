import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Face from '../pages/Face.vue'
import Road from '../pages/Road.vue'
import Log from '../pages/Log.vue'
import Traffic from '../pages/Traffic.vue'
import AllViews from '../pages/AllViews.vue'
import UserManagement from '../pages/UserManagement.vue'

const routes = [
  { path: '/', component: AllViews },
  { path: '/home', component: Home },
  { path: '/face', component: Face },
  { path: '/road', component: Road },
  { path: '/log', component: Log },
  { path: '/traffic', component: Traffic },
  { path: '/user-management', component: UserManagement }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('user-token');

  if (to.path === '/' && isAuthenticated) {
    return next('/home');
  }

  const publicPages = ['/'];
  const authRequired = !publicPages.includes(to.path);

  if (authRequired && !isAuthenticated) {
    if (to.path === '/home') {
      return next(false); // 对首页静默取消导航
    }
    alert('请先登录');
    return next(false); // 对其他页面提示并取消导航
  }

  next();
});

export default router 
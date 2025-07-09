import { createRouter, createWebHistory } from "vue-router";
import Detection from "../views/Detection.vue";
import History from "../views/History.vue";
import Settings from "../views/Settings.vue";

const routes = [
  {
    path: "/",
    name: "Detection",
    component: Detection,
    meta: {
      title: "路面病害检测系统",
    },
  },
  {
    path: "/detection",
    redirect: "/",
  },
  {
    path: "/history",
    name: "History",
    component: History,
    meta: {
      title: "检测历史 - 路面病害检测系统",
    },
  },
  {
    path: "/settings",
    name: "Settings",
    component: Settings,
    meta: {
      title: "系统设置 - 路面病害检测系统",
    },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title;
  }
  next();
});

export default router;

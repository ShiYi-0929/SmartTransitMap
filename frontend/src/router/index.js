import { createRouter, createWebHistory } from "vue-router"
import Home from "../pages/Home.vue"
import Face from "../pages/Face.vue"
import Road from "../pages/Road.vue"
import Log from "../pages/Log.vue"
import AllViews from "../pages/AllViews.vue"
import UserManagement from "../pages/UserManagement.vue"
// 交通数据相关子页面
import Traffic from "../modules/trafficVisualization/Traffic.vue"
import TrafficOverview from "../modules/trafficVisualization/TrafficOverview.vue"
import TrafficTrack from "../modules/trafficVisualization/TrafficTrack.vue"
import TrafficHeatmap from "../modules/trafficVisualization/TrafficHeatmap.vue"
import TrafficAnomaly from "../modules/trafficVisualization/TrafficAnomaly.vue"
import SpatioTemporalAnalysis from "../modules/trafficVisualization/SpatioTemporalAnalysis.vue"
import TrafficStatistics from "../modules/trafficVisualization/TrafficStatistics.vue"
import TrafficRoadSimple from "../modules/trafficVisualization/TrafficRoadSimple.vue"
import TrafficRoadAdvanced from "../modules/trafficVisualization/TrafficRoadAdvanced.vue"
import SmartPassengerAnalysis from "../modules/trafficVisualization/SmartPassengerAnalysis.vue"
import TrafficLog from "../modules/trafficVisualization/TrafficLog.vue"

const routes = [
  { path: "/", component: AllViews },
  { path: "/home", component: Home },
  { path: "/face", component: Face },
  { path: "/road", component: Road },
  { path: "/log", component: Log },
  { path: "/user-management", component: UserManagement },
  {
    path: "/traffic",
    component: Traffic,
    redirect: "/traffic/overview", // 添加默认重定向
    children: [
      { path: "", redirect: "/traffic/overview" }, // 空路径重定向到overview
      { path: "overview", component: TrafficOverview },
      { path: "track", component: TrafficTrack },
      { path: "heatmap", component: TrafficHeatmap },
      { path: "anomaly", component: TrafficAnomaly },
      { path: "spatiotemporal", component: SpatioTemporalAnalysis },
      { path: "statistics", component: TrafficStatistics },
      { path: "road", component: TrafficRoadSimple },
      { path: "road-advanced", component: TrafficRoadAdvanced },
      { path: "smart-passenger", component: SmartPassengerAnalysis },
      { path: "log", component: TrafficLog }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  // const isAuthenticated = !!localStorage.getItem("user-token")
  // if (to.path === "/" && isAuthenticated) {
  //   return next("/home")
  // }
  // const publicPages = ["/"]
  // const authRequired = !publicPages.includes(to.path)
  // if (authRequired && !isAuthenticated) {
  //   if (to.path === "/home") {
  //     return next(false) // 对首页静默取消导航
  //   }
  //   alert("请先登录")
  //   return next(false) // 对其他页面提示并取消导航
  // }
  next()
})

export default router

// import { createRouter, createWebHistory } from "vue-router"
// import Home from "../pages/Home.vue"
// import Face from "../pages/Face.vue"
// import Road from "../pages/Road.vue"
// import Log from "../pages/Log.vue"
// import Traffic from "../pages/Traffic.vue"
// import AllViews from "../pages/AllViews.vue"
// import UserManagement from "../pages/UserManagement.vue"
//
// const routes = [
//   { path: "/", component: AllViews },
//   { path: "/home", component: Home },
//   { path: "/face", component: Face },
//   { path: "/road", component: Road },
//   { path: "/log", component: Log },
//   { path: "/traffic", component: Traffic },
//   { path: "/user-management", component: UserManagement },
// ]
//
// const router = createRouter({
//   history: createWebHistory(),
//   routes,
// })
//
// router.beforeEach((to, from, next) => {
//   const isAuthenticated = !!localStorage.getItem("user-token")
//   if (to.path === "/" && isAuthenticated) {
//     return next("/home")
//   }
//   const publicPages = ["/"]
//   const authRequired = !publicPages.includes(to.path)
//   if (authRequired && !isAuthenticated) {
//     if (to.path === "/home") {
//       return next(false) // 对首页静默取消导航
//     }
//     alert("请先登录")
//     return next(false) // 对其他页面提示并取消导航
//   }
//   next()
// })
//
// export default router


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
import TrafficRoad from "../modules/trafficVisualization/TrafficRoad.vue"
import TrafficPattern from "../modules/trafficVisualization/TrafficPattern.vue"

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
    children: [
      { path: "overview", component: TrafficOverview },
      { path: "track", component: TrafficTrack },
      { path: "heatmap", component: TrafficHeatmap },
      { path: "anomaly", component: TrafficAnomaly },
      { path: "spatiotemporal", component: SpatioTemporalAnalysis },
      { path: "statistics", component: TrafficStatistics },
      { path: "road", component: TrafficRoad },
      { path: "pattern", component: TrafficPattern }
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

import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Face from '../pages/Face.vue'
import Road from '../pages/Road.vue'
import Log from '../pages/Log.vue'
import Traffic from '../pages/Traffic.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/face', component: Face },
  { path: '/road', component: Road },
  { path: '/log', component: Log },
  { path: '/traffic', component: Traffic }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 
<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900">
    <!-- 顶部导航栏 -->
    <nav class="bg-black/20 backdrop-blur-md border-b border-white/10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <MapPin class="h-8 w-8 text-cyan-400 mr-3" />
            <h1 class="text-xl font-bold text-white">智慧交通时空分析系统</h1>
          </div>
          <div class="flex space-x-4">
            <button 
              v-for="nav in navigation"
              :key="nav.name"
              @click="activeTab = nav.key"
              :class="[
                'px-4 py-2 rounded-lg transition-all duration-300',
                activeTab === nav.key 
                  ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/25'
                  : 'text-gray-300 hover:text-white hover:bg-white/10'
              ]"
            >
              <component :is="nav.icon" class="h-5 w-5 inline mr-2" />
              {{ nav.name }}
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主要内容区域 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 系统概览卡片 -->
      <div v-if="activeTab === 'overview'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div 
          v-for="stat in stats"
          :key="stat.title"
          class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300"
        >
          <div class="flex items-center">
            <component :is="stat.icon" :class="['h-8 w-8 mr-4', stat.color]" />
            <div>
              <p class="text-gray-300 text-sm">{{ stat.title }}</p>
              <p class="text-2xl font-bold text-white">{{ stat.value }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 功能模块网格 -->
      <div v-if="activeTab === 'overview'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="module in modules"
          :key="module.title"
          @click="navigateToModule(module.route)"
          class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/15 hover:scale-105 transition-all duration-300 cursor-pointer group"
        >
          <component :is="module.icon" :class="['h-12 w-12 mb-4 group-hover:scale-110 transition-transform', module.color]" />
          <h3 class="text-xl font-semibold text-white mb-2">{{ module.title }}</h3>
          <p class="text-gray-300 text-sm">{{ module.description }}</p>
        </div>
      </div>

      <!-- 交通可视化模块 -->
      <div v-if="activeTab === 'traffic'">
        <TrafficVisualization />
      </div>

      <!-- 数据分析模块 -->
      <div v-if="activeTab === 'analysis'">
        <DataAnalysis />
      </div>

      <!-- 异常检测模块 -->
      <div v-if="activeTab === 'anomaly'">
        <AnomalyDetection />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { MapPin, Activity, BarChart3, AlertTriangle, Map, TrendingUp, Users, Car } from 'lucide-vue-next'
import DataAnalysis from '@/components/DataAnalysis.vue'
import AnomalyDetection from '@/components/AnomalyDetection.vue'

const activeTab = ref('overview')

const navigation = [
  { name: '系统概览', key: 'overview', icon: BarChart3 },
  { name: '交通可视化', key: 'traffic', icon: Map },
  { name: '数据分析', key: 'analysis', icon: TrendingUp },
  { name: '异常检测', key: 'anomaly', icon: AlertTriangle }
]

const stats = [
  { title: '实时车辆数', value: '12,847', icon: Car, color: 'text-green-400' },
  { title: '今日订单', value: '45,231', icon: Activity, color: 'text-blue-400' },
  { title: '异常事件', value: '23', icon: AlertTriangle, color: 'text-red-400' },
  { title: '在线用户', value: '8,934', icon: Users, color: 'text-purple-400' }
]

const modules = [
  {
    title: '地图查询与轨迹',
    description: '实时查询车辆位置，展示行驶轨迹',
    icon: Map,
    color: 'text-cyan-400',
    route: '/traffic'
  },
  {
    title: '热力图分析',
    description: '展示交通热点区域分布',
    icon: TrendingUp,
    color: 'text-orange-400',
    route: '/analysis'
  },
  {
    title: '异常检测',
    description: '智能识别交通异常事件',
    icon: AlertTriangle,
    color: 'text-red-400',
    route: '/anomaly'
  },
  {
    title: '时空分析',
    description: '分析交通时空分布特征',
    icon: BarChart3,
    color: 'text-green-400',
    route: '/statistics'
  },
  {
    title: '人口分布',
    description: '展示区域人口与客流关系',
    icon: Users,
    color: 'text-purple-400',
    route: '/population'
  },
  {
    title: '交通模式',
    description: '识别典型交通出行模式',
    icon: Activity,
    color: 'text-pink-400',
    route: '/patterns'
  }
]

const navigateToModule = (route) => {
  console.log('导航到:', route)
}

onMounted(() => {
  console.log('系统初始化完成')
})
</script>

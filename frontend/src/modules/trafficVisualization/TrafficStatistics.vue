<template>
  <div class="space-y-6 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 p-6">
    <!-- 数据分析标题 -->
    <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <TrendingUp class="h-8 w-8 text-blue-400 mr-3" />
          <div>
            <h2 class="text-2xl font-bold text-white">数据分析中心</h2>
            <p class="text-blue-200">深度分析交通数据趋势</p>
          </div>
        </div>
        
        <!-- 分析模块选择 -->
        <div class="flex space-x-2">
          <button 
            @click="activeModule = 'overview'"
            :class="[
              'px-4 py-2 rounded-lg transition-all',
              activeModule === 'overview' 
                ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg' 
                : 'bg-blue-700/30 text-blue-200 hover:bg-blue-600/40 hover:text-white'
            ]"
          >
            总览分析
          </button>
          <button 
            @click="activeModule = 'weekly'"
            :class="[
              'px-4 py-2 rounded-lg transition-all',
              activeModule === 'weekly' 
                ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg' 
                : 'bg-blue-700/30 text-blue-200 hover:bg-blue-600/40 hover:text-white'
            ]"
          >
            周客流量分析
          </button>
        </div>
      </div>
    </div>

    <!-- 总览分析模块 -->
    <div v-if="activeModule === 'overview'">
      <!-- 时间周期选择 -->
      <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-4 border border-blue-500/30 mb-6">
        <div class="flex justify-center space-x-2">
          <button 
            v-for="period in timePeriods" 
            :key="period.key"
            @click="selectedPeriod = period.key"
            :class="[
              'px-4 py-2 rounded-lg transition-all',
              selectedPeriod === period.key 
                ? 'bg-gradient-to-r from-blue-500 to-sky-500 text-white shadow-lg' 
                : 'bg-blue-700/30 text-blue-200 hover:bg-blue-600/40 hover:text-white'
            ]"
          >
            {{ period.label }}
          </button>
        </div>
      </div>

      <!-- 关键指标卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div 
          v-for="metric in keyMetrics" 
          :key="metric.title"
          class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-blue-200 text-sm">{{ metric.title }}</p>
              <p class="text-2xl font-bold text-white">{{ metric.value }}</p>
              <div class="flex items-center mt-2">
                <component 
                  :is="metric.trend > 0 ? TrendingUp : TrendingDown" 
                  :class="['h-4 w-4 mr-1', metric.trend > 0 ? 'text-green-400' : 'text-red-400']" 
                />
                <span :class="['text-sm', metric.trend > 0 ? 'text-green-400' : 'text-red-400']">
                  {{ Math.abs(metric.trend) }}%
                </span>
              </div>
            </div>
            <component :is="metric.icon" :class="['h-8 w-8', metric.color]" />
          </div>
        </div>
      </div>

      <!-- 图表展示区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-1 gap-6">
        <!-- 时间流量趋势 -->
        <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-white">24小时流量趋势</h3>
            <TrendingUp class="h-5 w-5 text-blue-400" />
          </div>
          <div class="h-64 flex items-end space-x-1">
            <div 
              v-for="(value, index) in trafficData" 
              :key="index"
              class="bg-gradient-to-t from-blue-600 to-blue-400 rounded-t flex-1 transition-all hover:scale-105 hover:from-blue-500 hover:to-blue-300"
              :style="{ height: `${(value / Math.max(...trafficData)) * 100}%` }"
              :title="`${index}:00 - ${value} 车辆`"
            ></div>
          </div>
          <div class="flex justify-between text-xs text-blue-300 mt-2">
            <span>00:00</span>
            <span>06:00</span>
            <span>12:00</span>
            <span>18:00</span>
            <span>23:59</span>
          </div>
        </div>
      </div>

      <!-- 区域统计排行 -->
      <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">区域流量排行</h3>
          <div class="flex space-x-2">
            <button 
              @click="sortBy = 'vehicles'"
              :class="['px-3 py-1 text-xs rounded transition-all', sortBy === 'vehicles' ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg' : 'bg-blue-700/30 text-blue-200 hover:bg-blue-600/40']"
            >
              按流量
            </button>
            <button 
              @click="sortBy = 'speed'"
              :class="['px-3 py-1 text-xs rounded transition-all', sortBy === 'speed' ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg' : 'bg-blue-700/30 text-blue-200 hover:bg-blue-600/40']"
            >
              按速度
            </button>
            <button class="px-3 py-1 bg-gradient-to-r from-sky-500 to-blue-500 text-white text-xs rounded shadow-lg hover:from-sky-600 hover:to-blue-600 transition-all">导出</button>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-blue-500/30">
                <th class="text-left py-3 px-4 text-blue-200">排名</th>
                <th class="text-left py-3 px-4 text-blue-200">区域名称</th>
                <th class="text-left py-3 px-4 text-blue-200">总车辆数</th>
                <th class="text-left py-3 px-4 text-blue-200">平均速度</th>
                <th class="text-left py-3 px-4 text-blue-200">拥堵率</th>
                <th class="text-left py-3 px-4 text-blue-200">流量等级</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(area, index) in sortedAreaData" :key="area.id" class="border-b border-blue-500/20 hover:bg-blue-700/20">
                <td class="py-3 px-4 text-white">
                  <div class="flex items-center">
                    <span :class="['w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mr-2', getRankColor(index)]">
                      {{ index + 1 }}
                    </span>
                  </div>
                </td>
                <td class="py-3 px-4 text-white font-medium">{{ area.name }}</td>
                <td class="py-3 px-4 text-white">{{ area.totalVehicles.toLocaleString() }}</td>
                <td class="py-3 px-4 text-white">{{ area.avgSpeed }} km/h</td>
                <td class="py-3 px-4">
                  <div class="flex items-center">
                    <div class="w-20 bg-blue-900/50 rounded-full h-2 mr-2">
                      <div 
                        class="h-full rounded-full" 
                        :class="getCongestionColor(area.congestionRate)"
                        :style="{ width: `${area.congestionRate}%` }"
                      ></div>
                    </div>
                    <span class="text-white text-xs">{{ area.congestionRate }}%</span>
                  </div>
                </td>
                <td class="py-3 px-4">
                  <span :class="['px-2 py-1 rounded text-xs', getTrafficLevelColor(area.trafficLevel)]">
                    {{ area.trafficLevel }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 时间段统计 -->
      <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">高峰时段分析</h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="period in timePeriodStats" :key="period.name" class="bg-blue-700/30 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-white font-medium">{{ period.name }}</h4>
              <span :class="['px-2 py-1 rounded text-xs', period.statusClass]">{{ period.status }}</span>
            </div>
            <div class="space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-blue-200">时间段:</span>
                <span class="text-white">{{ period.timeRange }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-blue-200">平均车流:</span>
                <span class="text-white">{{ period.avgVehicles }} 辆/小时</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-blue-200">平均速度:</span>
                <span class="text-white">{{ period.avgSpeed }} km/h</span>
              </div>
              <div class="w-full bg-blue-900/50 rounded-full h-2 mt-3">
                <div 
                  class="h-full rounded-full bg-gradient-to-r from-blue-500 to-sky-400" 
                  :style="{ width: `${(period.avgVehicles / 2000) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 周客流量分析模块 -->
    <div v-if="activeModule === 'weekly'">
      <WeeklyPassengerFlow />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { TrendingUp, TrendingDown, Car, Clock, Users } from 'lucide-vue-next'
import WeeklyPassengerFlow from '../../components/WeeklyPassengerFlow.vue'

// 响应式数据
const selectedPeriod = ref('today')
const activeModule = ref('overview')

// 删除了'month'选项，只保留今日和本周
const timePeriods = [
  { key: 'today', label: '今日' },
  { key: 'week', label: '本周' }
]

const keyMetrics = ref([
  { title: '总流量', value: '45,231', trend: 12.5, icon: Car, color: 'text-blue-400' },
  { title: '平均速度', value: '42.8km/h', trend: -3.2, icon: TrendingUp, color: 'text-sky-400' },
  { title: '高峰时长', value: '3.2h', trend: 8.1, icon: Clock, color: 'text-indigo-400' },
  { title: '活跃用户', value: '12,847', trend: 15.3, icon: Users, color: 'text-purple-400' }
])

const trafficData = ref([20, 25, 30, 45, 60, 80, 95, 85, 70, 55, 40, 35, 30, 45, 65, 85, 90, 75, 60, 45, 35, 30, 25, 20])

// 排序方式
const sortBy = ref('vehicles')

// 区域统计数据
const areaStatsData = ref([
  { id: 1, name: '市中心核心区', totalVehicles: 45230, avgSpeed: 35.2, congestionRate: 78, trafficLevel: '重度拥堵' },
  { id: 2, name: '商业购物区', totalVehicles: 38750, avgSpeed: 42.8, congestionRate: 65, trafficLevel: '中度拥堵' },
  { id: 3, name: '住宅居民区', totalVehicles: 28650, avgSpeed: 55.1, congestionRate: 35, trafficLevel: '轻度拥堵' },
  { id: 4, name: '工业开发区', totalVehicles: 19430, avgSpeed: 62.3, congestionRate: 25, trafficLevel: '基本畅通' },
  { id: 5, name: '文教科研区', totalVehicles: 15820, avgSpeed: 58.7, congestionRate: 30, trafficLevel: '基本畅通' },
  { id: 6, name: '交通枢纽区', totalVehicles: 52100, avgSpeed: 28.5, congestionRate: 85, trafficLevel: '严重拥堵' },
  { id: 7, name: '休闲娱乐区', totalVehicles: 22340, avgSpeed: 48.9, congestionRate: 45, trafficLevel: '轻度拥堵' }
])

// 时间段统计数据
const timePeriodStats = ref([
  {
    name: '早高峰',
    timeRange: '07:00-09:00',
    avgVehicles: 1850,
    avgSpeed: 32.5,
    status: '拥堵',
    statusClass: 'bg-red-500/20 text-red-400'
  },
  {
    name: '晚高峰', 
    timeRange: '17:00-19:00',
    avgVehicles: 1920,
    avgSpeed: 30.8,
    status: '严重拥堵',
    statusClass: 'bg-purple-500/20 text-purple-400'
  },
  {
    name: '平峰时段',
    timeRange: '10:00-16:00', 
    avgVehicles: 980,
    avgSpeed: 52.3,
    status: '畅通',
    statusClass: 'bg-green-500/20 text-green-400'
  }
])

// 计算属性
const trafficDataPoints = computed(() => {
  return trafficData.value.map((value, index) => `${index * 10},${200 - (value * 2)}`).join(' ')
})

// 排序后的区域数据
const sortedAreaData = computed(() => {
  const data = [...areaStatsData.value]
  if (sortBy.value === 'vehicles') {
    return data.sort((a, b) => b.totalVehicles - a.totalVehicles)
  } else if (sortBy.value === 'speed') {
    return data.sort((a, b) => b.avgSpeed - a.avgSpeed)
  }
  return data
})

// 方法
const generateTrendLine = () => {
  return trafficDataPoints.value
}

const getRankColor = (index) => {
  if (index === 0) return 'bg-yellow-500 text-yellow-900'
  if (index === 1) return 'bg-gray-300 text-gray-800'
  if (index === 2) return 'bg-orange-400 text-orange-900'
  return 'bg-blue-500 text-white'
}

const getCongestionColor = (rate) => {
  if (rate >= 80) return 'bg-red-500'
  if (rate >= 60) return 'bg-orange-500'
  if (rate >= 40) return 'bg-yellow-500'
  return 'bg-green-500'
}

const getTrafficLevelColor = (level) => {
  switch (level) {
    case '基本畅通': return 'bg-green-500/20 text-green-400'
    case '轻度拥堵': return 'bg-yellow-500/20 text-yellow-400'
    case '中度拥堵': return 'bg-orange-500/20 text-orange-400'
    case '重度拥堵': return 'bg-red-500/20 text-red-400'
    case '严重拥堵': return 'bg-purple-500/20 text-purple-400'
    default: return 'bg-slate-500/20 text-slate-400'
  }
}

onMounted(() => {
  console.log('统计分析模块已加载')
})
</script>

<style scoped>
/* 科技感样式 */
.grid-cols-20 {
  grid-template-columns: repeat(20, minmax(0, 1fr));
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.space-y-6 > * {
  animation: fadeInUp 0.6s ease-out;
}

/* 悬停效果 */
.hover\:scale-105:hover {
  transform: scale(1.05);
}

.hover\:scale-110:hover {
  transform: scale(1.1);
}

/* 渐变效果 */
.bg-gradient-to-t {
  background: linear-gradient(to top, var(--tw-gradient-stops));
}

/* 响应式表格 */
.overflow-x-auto {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
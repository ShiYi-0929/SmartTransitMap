<template>
  <div class="space-y-6">
    <!-- 数据分析标题 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <TrendingUp class="h-8 w-8 text-blue-400 mr-3" />
          <div>
            <h2 class="text-2xl font-bold text-white">数据分析中心</h2>
            <p class="text-gray-300">深度分析交通数据趋势</p>
          </div>
        </div>
        <div class="flex space-x-2">
          <button 
            v-for="period in timePeriods" 
            :key="period.key"
            @click="selectedPeriod = period.key"
            :class="[
              'px-4 py-2 rounded-lg transition-all',
              selectedPeriod === period.key 
                ? 'bg-blue-500 text-white' 
                : 'bg-white/10 text-gray-300 hover:bg-white/20'
            ]"
          >
            {{ period.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- 关键指标卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div 
        v-for="metric in keyMetrics" 
        :key="metric.title"
        class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-300 text-sm">{{ metric.title }}</p>
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

    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 流量趋势图 -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <h3 class="text-xl font-semibold text-white mb-4">交通流量趋势</h3>
        <div class="h-64">
          <svg class="w-full h-full" viewBox="0 0 400 200">
            <!-- 网格线 -->
            <defs>
              <pattern id="grid" width="40" height="20" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
            
            <!-- 流量曲线 -->
            <polyline
              :points="generateTrendLine(trafficData)"
              fill="none"
              stroke="rgb(34, 197, 94)"
              stroke-width="2"
              class="drop-shadow-lg"
            />
            
            <!-- 数据点 -->
            <circle
              v-for="(point, index) in trafficDataPoints"
              :key="index"
              :cx="point.x"
              :cy="point.y"
              r="4"
              fill="rgb(34, 197, 94)"
              class="animate-pulse"
            />
          </svg>
        </div>
        <div class="flex justify-between text-xs text-gray-400 mt-2">
          <span>00:00</span>
          <span>06:00</span>
          <span>12:00</span>
          <span>18:00</span>
          <span>24:00</span>
        </div>
      </div>

      <!-- 区域分布饼图 -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <h3 class="text-xl font-semibold text-white mb-4">区域流量分布</h3>
        <div class="h-64 flex items-center justify-center">
          <div class="relative w-48 h-48">
            <!-- 饼图 -->
            <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle
                v-for="(segment, index) in pieChartData"
                :key="index"
                cx="50"
                cy="50"
                r="40"
                fill="none"
                :stroke="segment.color"
                stroke-width="8"
                :stroke-dasharray="`${segment.percentage} ${100 - segment.percentage}`"
                :stroke-dashoffset="segment.offset"
                class="transition-all duration-500"
              />
            </svg>
            <!-- 中心文字 -->
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="text-center">
                <div class="text-2xl font-bold text-white">100%</div>
                <div class="text-sm text-gray-300">总流量</div>
              </div>
            </div>
          </div>
        </div>
        <!-- 图例 -->
        <div class="grid grid-cols-2 gap-2 mt-4">
          <div 
            v-for="area in areaData" 
            :key="area.name"
            class="flex items-center"
          >
            <div :class="['w-3 h-3 rounded-full mr-2', area.colorClass]"></div>
            <span class="text-sm text-gray-300">{{ area.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 热力图分析 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
      <h3 class="text-xl font-semibold text-white mb-4">交通热力图分析</h3>
      <div class="grid grid-cols-7 gap-1 mb-4">
        <div 
          v-for="(day, index) in heatmapData" 
          :key="index"
          class="space-y-1"
        >
          <div class="text-xs text-gray-400 text-center">{{ day.name }}</div>
          <div 
            v-for="(hour, hourIndex) in day.hours" 
            :key="hourIndex"
            :class="['h-4 rounded', getHeatmapColor(hour)]"
            :title="`${day.name} ${hourIndex}:00 - 流量: ${hour}`"
          ></div>
        </div>
      </div>
      <div class="flex items-center justify-between text-xs text-gray-400">
        <span>低流量</span>
        <div class="flex space-x-1">
          <div class="w-3 h-3 bg-green-900 rounded"></div>
          <div class="w-3 h-3 bg-green-700 rounded"></div>
          <div class="w-3 h-3 bg-green-500 rounded"></div>
          <div class="w-3 h-3 bg-yellow-500 rounded"></div>
          <div class="w-3 h-3 bg-red-500 rounded"></div>
        </div>
        <span>高流量</span>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
      <div class="p-6 border-b border-white/10">
        <h3 class="text-xl font-semibold text-white">详细数据报告</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-white/5">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">时间段</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">总流量</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">平均速度</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">拥堵指数</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">状态</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/10">
            <tr 
              v-for="row in tableData" 
              :key="row.time"
              class="hover:bg-white/5 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm text-white">{{ row.time }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-white">{{ row.traffic }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-white">{{ row.speed }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-white">{{ row.congestion }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 py-1 rounded text-xs font-medium', getStatusColor(row.status)]">
                  {{ row.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { TrendingUp, TrendingDown, Car, Clock, Users, BarChart3 } from 'lucide-vue-next'

// 响应式数据
const selectedPeriod = ref('today')

const timePeriods = [
  { key: 'today', label: '今日' },
  { key: 'week', label: '本周' },
  { key: 'month', label: '本月' }
]

const keyMetrics = ref([
  { title: '总流量', value: '45,231', trend: 12.5, icon: Car, color: 'text-blue-400' },
  { title: '平均速度', value: '42.8km/h', trend: -3.2, icon: TrendingUp, color: 'text-green-400' },
  { title: '高峰时长', value: '3.2h', trend: 8.1, icon: Clock, color: 'text-yellow-400' },
  { title: '活跃用户', value: '12,847', trend: 15.3, icon: Users, color: 'text-purple-400' }
])

const trafficData = ref([20, 25, 30, 45, 60, 80, 95, 85, 70, 55, 40, 35, 30, 45, 65, 85, 90, 75, 60, 45, 35, 30, 25, 20])

const areaData = ref([
  { name: '市中心', percentage: 35, color: '#ef4444', colorClass: 'bg-red-500' },
  { name: '商业区', percentage: 25, color: '#f59e0b', colorClass: 'bg-yellow-500' },
  { name: '住宅区', percentage: 20, color: '#10b981', colorClass: 'bg-green-500' },
  { name: '工业区', percentage: 20, color: '#3b82f6', colorClass: 'bg-blue-500' }
])

const tableData = ref([
  { time: '08:00-09:00', traffic: '2,847', speed: '35.2km/h', congestion: '0.75', status: '拥堵' },
  { time: '09:00-10:00', traffic: '2,156', speed: '42.8km/h', congestion: '0.45', status: '正常' },
  { time: '10:00-11:00', traffic: '1,923', speed: '48.5km/h', congestion: '0.32', status: '畅通' },
  { time: '11:00-12:00', traffic: '2,234', speed: '41.2km/h', congestion: '0.52', status: '正常' },
  { time: '12:00-13:00', traffic: '2,567', speed: '38.9km/h', congestion: '0.68', status: '缓慢' }
])

// 计算属性
const trafficDataPoints = computed(() => {
  return trafficData.value.map((value, index) => ({
    x: (index / (trafficData.value.length - 1)) * 380 + 10,
    y: 180 - (value / 100) * 160
  }))
})

const pieChartData = computed(() => {
  let offset = 0
  return areaData.value.map(area => {
    const segment = {
      percentage: area.percentage,
      color: area.color,
      offset: -offset
    }
    offset += area.percentage
    return segment
  })
})

const heatmapData = ref([
  { name: '周一', hours: Array.from({length: 24}, () => Math.floor(Math.random() * 100)) },
  { name: '周二', hours: Array.from({length: 24}, () => Math.floor(Math.random() * 100)) },
  { name: '周三', hours: Array.from({length: 24}, () => Math.floor(Math.random() * 100)) },
  { name: '周四', hours: Array.from({length: 24}, () => Math.floor(Math.random() * 100)) },
  { name: '周五', hours: Array.from({length: 24}, () => Math.floor(Math.random() * 100)) },
  { name: '周六', hours: Array.from({length: 24}, () => Math.floor(Math.random() * 100)) },
  { name: '周日', hours: Array.from({length: 24}, () => Math.floor(Math.random() * 100)) }
])

// 方法
const generateTrendLine = (data) => {
  return data.map((value, index) => {
    const x = (index / (data.length - 1)) * 380 + 10
    const y = 180 - (value / 100) * 160
    return `${x},${y}`
  }).join(' ')
}

const getHeatmapColor = (value) => {
  if (value < 20) return 'bg-green-900'
  if (value < 40) return 'bg-green-700'
  if (value < 60) return 'bg-green-500'
  if (value < 80) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getStatusColor = (status) => {
  switch (status) {
    case '畅通': return 'bg-green-500/20 text-green-400'
    case '正常': return 'bg-blue-500/20 text-blue-400'
    case '缓慢': return 'bg-yellow-500/20 text-yellow-400'
    case '拥堵': return 'bg-red-500/20 text-red-400'
    default: return 'bg-gray-500/20 text-gray-400'
  }
}

onMounted(() => {
  console.log('数据分析模块初始化完成')
})
</script>

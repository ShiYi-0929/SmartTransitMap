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
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
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

        <!-- 区域分布饼图 -->
        <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30">
                     <div class="flex items-center justify-between mb-4">
             <h3 class="text-lg font-semibold text-white">区域分布</h3>
             <BarChart3 class="h-5 w-5 text-sky-400" />
           </div>
          <div class="h-64 flex items-center justify-center">
            <div class="relative w-48 h-48">
              <svg class="w-full h-full" viewBox="0 0 200 200">
                <circle cx="100" cy="100" r="80" fill="none" stroke="#374151" stroke-width="2"/>
                <g v-for="(area, index) in areaData" :key="area.name">
                  <path 
                    :d="generatePieSlice(index, area.percentage)"
                    :fill="area.color"
                    class="transition-all hover:opacity-80"
                  />
                </g>
              </svg>
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="text-center text-white">
                  <div class="text-lg font-bold">总计</div>
                  <div class="text-sm">100%</div>
                </div>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 mt-4">
                         <div v-for="area in areaData" :key="area.name" class="flex items-center">
               <div :class="['w-3 h-3 rounded mr-2', area.colorClass]"></div>
               <span class="text-xs text-blue-200">{{ area.name }} {{ area.percentage }}%</span>
             </div>
          </div>
        </div>
      </div>

      <!-- 热力图分析 -->
      <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">热力图分析</h3>
                     <div class="flex space-x-2">
             <button class="px-3 py-1 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-xs rounded shadow-lg">实时</button>
             <button class="px-3 py-1 bg-blue-700/30 text-blue-200 text-xs rounded hover:bg-blue-600/40 hover:text-white transition-all">历史</button>
           </div>
        </div>
        <div class="grid grid-cols-20 gap-1 h-40">
          <div 
            v-for="(value, index) in heatmapData" 
            :key="index"
            :class="['rounded transition-all hover:scale-110', getHeatmapColor(value)]"
            :title="`强度: ${value}`"
          ></div>
        </div>
        <div class="flex justify-between items-center mt-4">
          <div class="flex items-center space-x-4">
                         <span class="text-xs text-blue-300">低</span>
                         <div class="flex space-x-1">
               <div class="w-4 h-4 bg-blue-900 rounded"></div>
               <div class="w-4 h-4 bg-blue-700 rounded"></div>
               <div class="w-4 h-4 bg-blue-500 rounded"></div>
               <div class="w-4 h-4 bg-sky-500 rounded"></div>
               <div class="w-4 h-4 bg-indigo-500 rounded"></div>
             </div>
                         <span class="text-xs text-blue-300">高</span>
          </div>
                     <span class="text-xs text-blue-300">最后更新: {{ new Date().toLocaleTimeString() }}</span>
        </div>
      </div>

      <!-- 详细数据表格 -->
      <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">详细数据</h3>
                     <div class="flex space-x-2">
             <button class="px-3 py-1 bg-gradient-to-r from-sky-500 to-blue-500 text-white text-xs rounded shadow-lg hover:from-sky-600 hover:to-blue-600 transition-all">导出</button>
             <button class="px-3 py-1 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-xs rounded shadow-lg hover:from-blue-600 hover:to-indigo-600 transition-all">刷新</button>
           </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
                             <tr class="border-b border-blue-500/30">
                                 <th class="text-left py-3 px-4 text-blue-200">时间</th>
                 <th class="text-left py-3 px-4 text-blue-200">区域</th>
                 <th class="text-left py-3 px-4 text-blue-200">车辆数</th>
                 <th class="text-left py-3 px-4 text-blue-200">平均速度</th>
                 <th class="text-left py-3 px-4 text-blue-200">状态</th>
              </tr>
            </thead>
                         <tbody>
               <tr v-for="row in tableData" :key="row.id" class="border-b border-blue-500/20 hover:bg-blue-700/20">
                <td class="py-3 px-4 text-white">{{ row.time }}</td>
                <td class="py-3 px-4 text-white">{{ row.area }}</td>
                <td class="py-3 px-4 text-white">{{ row.vehicles }}</td>
                <td class="py-3 px-4 text-white">{{ row.speed }}</td>
                <td class="py-3 px-4">
                  <span :class="['px-2 py-1 rounded text-xs', getStatusColor(row.status)]">
                    {{ row.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
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
import { TrendingUp, TrendingDown, Car, Clock, Users, BarChart3 } from 'lucide-vue-next'
import WeeklyPassengerFlow from '../../components/WeeklyPassengerFlow.vue'

// 响应式数据
const selectedPeriod = ref('today')
const activeModule = ref('overview')

const timePeriods = [
  { key: 'today', label: '今日' },
  { key: 'week', label: '本周' },
  { key: 'month', label: '本月' }
]

const keyMetrics = ref([
  { title: '总流量', value: '45,231', trend: 12.5, icon: Car, color: 'text-blue-400' },
  { title: '平均速度', value: '42.8km/h', trend: -3.2, icon: TrendingUp, color: 'text-sky-400' },
  { title: '高峰时长', value: '3.2h', trend: 8.1, icon: Clock, color: 'text-indigo-400' },
  { title: '活跃用户', value: '12,847', trend: 15.3, icon: Users, color: 'text-purple-400' }
])

const trafficData = ref([20, 25, 30, 45, 60, 80, 95, 85, 70, 55, 40, 35, 30, 45, 65, 85, 90, 75, 60, 45, 35, 30, 25, 20])

const areaData = ref([
  { name: '市中心', percentage: 35, color: '#3b82f6', colorClass: 'bg-blue-500' },
  { name: '商业区', percentage: 25, color: '#0ea5e9', colorClass: 'bg-sky-500' },
  { name: '住宅区', percentage: 20, color: '#6366f1', colorClass: 'bg-indigo-500' },
  { name: '工业区', percentage: 20, color: '#8b5cf6', colorClass: 'bg-purple-500' }
])

const tableData = ref([
  { id: 1, time: '08:00', area: '市中心', vehicles: 1250, speed: '35.2 km/h', status: '拥堵' },
  { id: 2, time: '08:15', area: '商业区', vehicles: 890, speed: '42.8 km/h', status: '缓慢' },
  { id: 3, time: '08:30', area: '住宅区', vehicles: 654, speed: '55.1 km/h', status: '正常' },
  { id: 4, time: '08:45', area: '工业区', vehicles: 432, speed: '62.3 km/h', status: '畅通' },
  { id: 5, time: '09:00', area: '市中心', vehicles: 1180, speed: '38.7 km/h', status: '拥堵' }
])

// 生成热力图数据
const heatmapData = ref(Array.from({ length: 400 }, () => Math.floor(Math.random() * 100)))

// 计算属性
const trafficDataPoints = computed(() => {
  return trafficData.value.map((value, index) => `${index * 10},${200 - (value * 2)}`).join(' ')
})

const pieChartData = computed(() => {
  return areaData.value.map((area, index) => {
    const startAngle = areaData.value.slice(0, index).reduce((sum, a) => sum + (a.percentage * 3.6), 0)
    const endAngle = startAngle + (area.percentage * 3.6)
    return { ...area, startAngle, endAngle }
  })
})

// 方法
const generateTrendLine = () => {
  return trafficDataPoints.value
}

const generatePieSlice = (index, percentage) => {
  const radius = 80
  const centerX = 100
  const centerY = 100
  
  const startAngle = pieChartData.value.slice(0, index).reduce((sum, area) => sum + area.percentage, 0) * 3.6 - 90
  const endAngle = startAngle + (percentage * 3.6)
  
  const startX = centerX + radius * Math.cos(startAngle * Math.PI / 180)
  const startY = centerY + radius * Math.sin(startAngle * Math.PI / 180)
  const endX = centerX + radius * Math.cos(endAngle * Math.PI / 180)
  const endY = centerY + radius * Math.sin(endAngle * Math.PI / 180)
  
  const largeArcFlag = percentage > 27.78 ? 1 : 0
  
  return `M ${centerX} ${centerY} L ${startX} ${startY} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${endX} ${endY} Z`
}

const getHeatmapColor = (value) => {
  if (value < 20) return 'bg-blue-900'
  if (value < 40) return 'bg-blue-700'
  if (value < 60) return 'bg-blue-500'
  if (value < 80) return 'bg-sky-500'
  return 'bg-indigo-500'
}

const getStatusColor = (status) => {
  switch (status) {
    case '畅通': return 'bg-sky-500/20 text-sky-400'
    case '正常': return 'bg-blue-500/20 text-blue-400'
    case '缓慢': return 'bg-indigo-500/20 text-indigo-400'
    case '拥堵': return 'bg-purple-500/20 text-purple-400'
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
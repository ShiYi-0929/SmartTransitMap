<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 p-6">
    <!-- 页面标题 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <Users class="h-8 w-8 text-blue-400 mr-3" />
          <div>
            <h1 class="text-3xl font-bold text-white">载客车辆分析</h1>
            <p class="text-blue-200 mt-1">Loaded Vehicles Analysis</p>
          </div>
        </div>
        
        <!-- 状态指示器 -->
        <div class="flex items-center space-x-4">
          <div class="flex items-center">
            <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></div>
            <span class="text-green-400 text-sm">数据分析中</span>
          </div>
          <div class="text-white/60 text-sm">
            {{ currentTime }}
          </div>
        </div>
      </div>
    </div>

    <!-- 控制面板 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- 日期选择 -->
        <div>
          <label class="block text-white text-sm font-medium mb-2">选择日期</label>
          <select 
            v-model="selectedDate" 
            @change="loadTimelineData"
            class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="2013-09-12">2013-09-12 (周四)</option>
            <option value="2013-09-13">2013-09-13 (周五)</option>
            <option value="2013-09-14">2013-09-14 (周六)</option>
            <option value="2013-09-15">2013-09-15 (周日)</option>
            <option value="2013-09-16">2013-09-16 (周一)</option>
            <option value="2013-09-17">2013-09-17 (周二)</option>
            <option value="2013-09-18">2013-09-18 (周三)</option>
          </select>
        </div>

        <!-- 时间分辨率 -->
        <div>
          <label class="block text-white text-sm font-medium mb-2">时间分辨率</label>
          <select 
            v-model="timeResolution" 
            @change="loadTimelineData"
            class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="15">15分钟</option>
            <option value="30">30分钟</option>
            <option value="60">1小时</option>
          </select>
        </div>

        <!-- 刷新按钮 -->
        <div class="flex items-end">
          <button 
            @click="loadTimelineData"
            :disabled="loading"
            class="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-all disabled:opacity-50 flex items-center justify-center"
          >
            <RefreshCw class="h-4 w-4 mr-2" :class="{ 'animate-spin': loading }" />
            {{ loading ? '加载中...' : '刷新数据' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-white/60 text-sm">载客车辆</p>
            <p class="text-2xl font-bold text-blue-400">{{ currentStats.loadedVehicles }}</p>
          </div>
          <Car class="h-8 w-8 text-blue-400" />
        </div>
      </div>

      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-white/60 text-sm">总车辆</p>
            <p class="text-2xl font-bold text-green-400">{{ currentStats.totalVehicles }}</p>
          </div>
          <Truck class="h-8 w-8 text-green-400" />
        </div>
      </div>

      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-white/60 text-sm">载客率</p>
            <p class="text-2xl font-bold text-purple-400">{{ currentStats.occupancyRate }}%</p>
          </div>
          <Percent class="h-8 w-8 text-purple-400" />
        </div>
      </div>
      <!-- 当前时间卡片已移除 -->
    </div>

    <!-- 主要内容区域 -->
    <div class="grid grid-cols-1 gap-6">
      <!-- 载客率动态折线图 -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
        <div class="p-6 border-b border-white/10 flex items-center justify-between">
          <h3 class="text-xl font-semibold text-white flex items-center">
            <TrendingUp class="h-5 w-5 mr-2" />
            载客率动态折线图
          </h3>
          <div class="flex items-center space-x-2">
            <button @click="togglePlay" class="px-3 py-1 rounded bg-blue-500 text-white hover:bg-blue-600 transition-all">
              <span v-if="isPlaying">⏸ 暂停</span>
              <span v-else>▶️ 播放</span>
            </button>
            <span class="text-white/60 text-sm">当前: {{ timelineData[activeIndex]?.time_window || '--:--' }}</span>
          </div>
        </div>
        <div class="p-6">
          <div v-if="loading" class="flex items-center justify-center h-64">
            <div class="text-white">加载中...</div>
          </div>
          <div v-else-if="timelineData.length === 0" class="flex items-center justify-center h-64">
            <div class="text-white/60">暂无数据</div>
          </div>
          <div v-else>
            <div ref="chartRef" style="width: 100%; height: 400px;"></div>
          </div>
        </div>
      </div>
      <!-- 载客车辆时间线（Element Plus 时间轴） -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
        <div class="p-6 border-b border-white/10 flex items-center justify-between">
          <h3 class="text-xl font-semibold text-white flex items-center">
            <TrendingUp class="h-5 w-5 mr-2" />
            载客车辆时间线
          </h3>
          <div class="flex items-center space-x-2">
            <button @click="togglePlay" class="px-3 py-1 rounded bg-blue-500 text-white hover:bg-blue-600 transition-all">
              <span v-if="isPlaying">⏸ 暂停</span>
              <span v-else>▶️ 播放</span>
            </button>
            <span class="text-white/60 text-sm">当前: {{ timelineData[activeIndex]?.time_window || '--:--' }}</span>
          </div>
        </div>
        <div class="p-6">
          <div v-if="loading" class="flex items-center justify-center h-64">
            <div class="text-white">加载中...</div>
          </div>
          <div v-else-if="timelineData.length === 0" class="flex items-center justify-center h-64">
            <div class="text-white/60">暂无数据</div>
          </div>
          <div v-else>
            <el-timeline>
              <el-timeline-item
                v-for="(item, idx) in timelineData"
                :key="item.time_window"
                :timestamp="item.time_window"
                :color="activeIndex === idx ? '#e6a23c' : getOccupancyColor(item.occupancy_rate)"
                :class="{ 'animate-pulse': activeIndex === idx }"
              >
                <div class="flex items-center justify-between">
                  <span class="font-bold text-blue-300">{{ item.loaded_vehicles }} 辆载客</span>
                  <span class="font-bold text-yellow-400">载客率 {{ item.occupancy_rate }}%</span>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细统计 -->
    <div class="mt-6 bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
      <div class="p-6 border-b border-white/10">
        <h3 class="text-xl font-semibold text-white flex items-center">
          <BarChart3 class="h-5 w-5 mr-2" />
          详细统计
        </h3>
      </div>
      <div class="p-6">
        <div v-if="timelineData.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center">
            <div class="text-3xl font-bold text-blue-400">{{ summary.maxLoadedVehicles }}</div>
            <div class="text-white/60 mt-1">最大载客车辆数</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold text-green-400">{{ summary.avgOccupancyRate }}%</div>
            <div class="text-white/60 mt-1">平均载客率</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold text-purple-400">{{ summary.totalTimeWindows }}</div>
            <div class="text-white/60 mt-1">时间段总数</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { 
  Users, Car, Truck, Percent, Clock, TrendingUp, Map, BarChart3, RefreshCw
} from 'lucide-vue-next'
import { smartPassengerAPI } from '@/api/smartPassenger'
import { ElTimeline, ElTimelineItem } from 'element-plus'
import * as echarts from 'echarts'
const chartRef = ref(null)
let chartInstance = null

// 响应式数据
const loading = ref(false)
const currentTime = ref('')
const selectedDate = ref('2013-09-13')
const timeResolution = ref(15)
const timelineData = ref([])
const selectedTimeWindow = ref(null)

// 计算属性
const currentStats = computed(() => {
  if (selectedTimeWindow.value) {
    return {
      loadedVehicles: selectedTimeWindow.value.loaded_vehicles,
      totalVehicles: selectedTimeWindow.value.total_vehicles,
      occupancyRate: selectedTimeWindow.value.occupancy_rate,
      currentTime: selectedTimeWindow.value.time_window
    }
  }
  return {
    loadedVehicles: 0,
    totalVehicles: 0,
    occupancyRate: 0,
    currentTime: '--:--'
  }
})

const summary = computed(() => {
  if (timelineData.value.length === 0) {
    return {
      maxLoadedVehicles: 0,
      avgOccupancyRate: 0,
      totalTimeWindows: 0
    }
  }
  
  const maxLoaded = Math.max(...timelineData.value.map(d => d.loaded_vehicles))
  const avgOccupancy = timelineData.value.reduce((sum, d) => sum + d.occupancy_rate, 0) / timelineData.value.length
  
  return {
    maxLoadedVehicles: maxLoaded,
    avgOccupancyRate: Math.round(avgOccupancy),
    totalTimeWindows: timelineData.value.length
  }
})

// 方法
const updateCurrentTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const loadTimelineData = async () => {
  try {
    loading.value = true
    console.log('🚕 加载载客车辆时间线数据...', selectedDate.value)

    // 这里res就是后端返回的对象
    const res = await smartPassengerAPI.getLoadedVehiclesTimeline(selectedDate.value, timeResolution.value)

    if (Array.isArray(res)) {
      // 直接就是数据数组
      timelineData.value = res
      console.log('✅ 载客车辆时间线数据加载成功', res.length, '个时间段')
      if (res.length > 0) {
        selectedTimeWindow.value = res[0]
      } else {
        selectedTimeWindow.value = null
      }
    } else if (res && res.success && Array.isArray(res.data)) {
      // 标准对象结构
      timelineData.value = res.data
      console.log('✅ 载客车辆时间线数据加载成功', res.data.length, '个时间段')
      if (res.data.length > 0) {
        selectedTimeWindow.value = res.data[0]
      } else {
        selectedTimeWindow.value = null
      }
    } else {
      console.error('❌ 载客车辆时间线数据加载失败:', res)
      timelineData.value = []
      selectedTimeWindow.value = null
    }
  } catch (error) {
    console.error('❌ 加载载客车辆时间线数据异常:', error)
    timelineData.value = []
    selectedTimeWindow.value = null
  } finally {
    loading.value = false
  }
}

const selectTimeWindow = (timeWindow) => {
  selectedTimeWindow.value = timeWindow
}

const activeIndex = ref(0)
const isPlaying = ref(false)
let timer = null

function startPlay() {
  if (timer) clearInterval(timer)
  isPlaying.value = true
  timer = setInterval(() => {
    if (timelineData.value.length > 0) {
      activeIndex.value = (activeIndex.value + 1) % timelineData.value.length
    }
  }, 70) // 0.7秒切换
}

function stopPlay() {
  isPlaying.value = false
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function togglePlay() {
  if (isPlaying.value) {
    stopPlay()
  } else {
    startPlay()
  }
}

function getOccupancyColor(rate) {
  if (rate >= 70) return '#f59e42'   // 橙色
  if (rate >= 50) return '#67c23a'   // 绿色
  if (rate >= 30) return '#409eff'   // 蓝色
  return '#909399'                   // 灰色
}

function renderChart() {
  if (!chartInstance && chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
  }
  if (!chartInstance) return
  // 只展示到当前activeIndex
  const times = timelineData.value.slice(0, activeIndex.value + 1).map(d => d.time_window)
  const rates = timelineData.value.slice(0, activeIndex.value + 1).map(d => d.occupancy_rate)
  const loaded = timelineData.value.slice(0, activeIndex.value + 1).map(d => d.loaded_vehicles)
  chartInstance.setOption({
    xAxis: { type: 'category', data: times, name: '时间' },
    yAxis: [
      { type: 'value', min: 0, max: 100, name: '载客率(%)' },
      { type: 'value', min: 0, name: '载客车辆数', position: 'right' }
    ],
    series: [
      {
        data: rates,
        type: 'line',
        smooth: true,
        areaStyle: {},
        showSymbol: false,
        lineStyle: { width: 3 },
        name: '载客率',
        yAxisIndex: 0
      },
      {
        data: loaded,
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, type: 'dashed' },
        name: '载客车辆数',
        yAxisIndex: 1
      }
    ],
    tooltip: { trigger: 'axis' },
    legend: { data: ['载客率', '载客车辆数'] },
    animation: true
  })
}

watch([timelineData, activeIndex], () => {
  renderChart()
})

// 定时器
let timeTimer = null

// 组件挂载
onMounted(() => {
  console.log('🚀 载客车辆分析模块初始化...')
  
  // 更新时间
  updateCurrentTime()
  timeTimer = setInterval(updateCurrentTime, 1000)
  
  // 加载初始数据
  loadTimelineData()
  
  // 清理定时器
  onUnmounted(() => {
    if (timeTimer) {
      clearInterval(timeTimer)
    }
    stopPlay() // 组件卸载时停止播放
    if (chartInstance) chartInstance.dispose()
  })
})

// 当数据变化时，重置高亮和播放状态
watch(() => timelineData.value, (newVal) => {
  activeIndex.value = 0
  stopPlay()
})
</script>

<style scoped>
/* 自定义动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* 渐变背景 */
.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}
</style> 
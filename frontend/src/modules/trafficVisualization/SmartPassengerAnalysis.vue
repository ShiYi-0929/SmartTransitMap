<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 p-6">
    <!-- 页面标题 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <Users class="h-8 w-8 text-blue-400 mr-3" />
          <div>
            <h1 class="text-3xl font-bold text-white">智能客流分析</h1>
            <p class="text-blue-200 mt-1">Intelligent Passenger Flow Analysis</p>
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

    <!-- 功能选择卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <!-- 天气影响分析 -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all cursor-pointer"
           @click="activeModule = 'weather'" 
           :class="{ 'ring-2 ring-blue-400': activeModule === 'weather' }">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center">
            <Cloud class="h-6 w-6 text-blue-400 mr-3" />
            <h2 class="text-xl font-semibold text-white">天气影响分析</h2>
          </div>
          <div class="text-blue-400">
            <ChevronRight class="h-5 w-5" />
          </div>
        </div>
        <p class="text-blue-200 text-sm mb-3">分析天气变化对客流量的影响程度</p>
        <div class="flex items-center space-x-4 text-sm">
          <div class="flex items-center">
            <div class="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
            <span class="text-blue-300">真实天气数据</span>
          </div>
          <div class="flex items-center">
            <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
            <span class="text-green-300">关联性分析</span>
          </div>
        </div>
      </div>

      <!-- 载客出租车分析 -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all cursor-pointer"
           @click="activeModule = 'taxi'" 
           :class="{ 'ring-2 ring-purple-400': activeModule === 'taxi' }">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center">
            <Car class="h-6 w-6 text-purple-400 mr-3" />
            <h2 class="text-xl font-semibold text-white">载客出租车分析</h2>
          </div>
          <div class="text-purple-400">
            <ChevronRight class="h-5 w-5" />
          </div>
        </div>
        <p class="text-purple-200 text-sm mb-3">分析载客出租车数量和需求分布</p>
        <div class="flex items-center space-x-4 text-sm">
          <div class="flex items-center">
            <div class="w-2 h-2 bg-purple-400 rounded-full mr-2"></div>
            <span class="text-purple-300">历史分析</span>
          </div>
          <div class="flex items-center">
            <div class="w-2 h-2 bg-yellow-400 rounded-full mr-2"></div>
            <span class="text-yellow-300">供需分析</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="space-y-6">
      <!-- 天气影响分析模块 -->
      <div v-if="activeModule === 'weather'" class="space-y-6">
        <WeatherImpactTimeline
          :daily-impacts="dailyImpacts"
          :selected-date="selectedDate"
          @date-change="selectedDate = $event"
          @hour-hover="selectedHour = $event"
        />
        <WeatherImpactMechanism :hourly-impact="currentHourlyImpact" />
        <WeatherImpactAnalysis 
          :weather-data="weatherData" 
          :passenger-data="passengerData"
          :loading="loading"
          @refresh="loadWeatherData"
        />
      </div>

      <!-- 载客出租车分析模块 -->
      <div v-if="activeModule === 'taxi'" class="space-y-6">
        <TaxiDemandAnalysis 
          :taxi-data="taxiData"
          :real-time-data="realTimeData"
          :loading="loading"
          @refresh="loadTaxiData"
        />
      </div>

      <!-- 综合分析视图 -->
      <div v-if="activeModule === 'comprehensive'" class="space-y-6">
        <!-- 数据分析面板 -->
        <div class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
          <div class="p-6 border-b border-white/10">
            <h3 class="text-xl font-semibold text-white flex items-center">
              <Activity class="h-5 w-5 mr-2" />
              数据分析面板
            </h3>
          </div>
          <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="text-center p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <div class="text-2xl font-bold text-blue-400">{{ realTimeStats.activePassengers }}</div>
                <div class="text-sm text-gray-300">活跃乘客</div>
              </div>
              <div class="text-center p-4 bg-green-500/10 rounded-lg border border-green-500/20">
                <div class="text-2xl font-bold text-green-400">{{ realTimeStats.loadedTaxis }}</div>
                <div class="text-sm text-gray-300">载客车辆</div>
              </div>
              <div class="text-center p-4 bg-purple-500/10 rounded-lg border border-purple-500/20">
                <div class="text-2xl font-bold text-purple-400">{{ realTimeStats.demandIndex }}</div>
                <div class="text-sm text-gray-300">需求指数</div>
              </div>
              <div class="text-center p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                <div class="text-2xl font-bold text-yellow-400">{{ realTimeStats.weatherImpact }}</div>
                <div class="text-sm text-gray-300">天气影响</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 综合分析图表 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <WeatherImpactAnalysis 
            :weather-data="weatherData" 
            :passenger-data="passengerData"
            :loading="loading"
            :compact="true"
            @refresh="loadWeatherData"
          />
          <TaxiDemandAnalysis 
            :taxi-data="taxiData"
            :real-time-data="realTimeData"
            :loading="loading"
            :compact="true"
            @refresh="loadTaxiData"
          />
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="fixed bottom-6 right-6 flex space-x-3">
      <button 
        @click="activeModule = 'comprehensive'"
        :class="[
          'px-4 py-2 rounded-lg transition-all',
          activeModule === 'comprehensive' 
            ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg' 
            : 'bg-white/10 text-white/70 hover:bg-white/20'
        ]"
      >
        <Grid class="h-4 w-4 mr-2 inline" />
        综合视图
      </button>
      <button 
        @click="refreshAllData"
        :disabled="loading"
        class="px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-all disabled:opacity-50"
      >
        <RefreshCw class="h-4 w-4 mr-2 inline" :class="{ 'animate-spin': loading }" />
        刷新数据
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { 
  Users, Cloud, Car, ChevronRight, Activity, Grid, RefreshCw
} from 'lucide-vue-next'
import { smartPassengerAPI } from '@/api/smartPassenger'
import WeatherImpactAnalysis from './components/WeatherImpactAnalysis.vue'
import TaxiDemandAnalysis from './components/TaxiDemandAnalysis.vue'
import WeatherImpactTimeline from './components/WeatherImpactTimeline.vue'
import WeatherImpactMechanism from './components/WeatherImpactMechanism.vue'

// 响应式数据
const activeModule = ref('comprehensive')
const loading = ref(false)
const currentTime = ref('')
const weatherData = ref(null)
const passengerData = ref(null)
const taxiData = ref(null)
const realTimeData = ref(null)

// 实时统计数据
const realTimeStats = ref({
  activePassengers: 0,
  loadedTaxis: 0,
  demandIndex: 0,
  weatherImpact: 0
})

// 新增：每日天气影响数据
const dailyImpacts = ref([])
const selectedDate = ref('')
const selectedHour = ref(null)

const currentHourlyImpact = computed(() => {
  const day = dailyImpacts.value.find(d => d.date === selectedDate.value)
  if (!day || selectedHour.value === null) return null
  return day.hourly_impacts.find(h => h.hour === selectedHour.value) || null
})

// 定时器
let refreshTimer = null

// 更新当前时间
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

// 加载天气影响数据
const loadWeatherData = async () => {
  try {
    loading.value = true
    console.log('🌤️ 加载天气影响数据...')
    
    const response = await smartPassengerAPI.analyzeWeatherImpact({
      time_window: '7d',
      correlation_threshold: 0.3
    })
    
    if (response.success) {
      weatherData.value = response
      console.log('✅ 天气影响数据加载成功')
    } else {
      console.error('❌ 天气影响数据加载失败:', response.message)
    }
  } catch (error) {
    console.error('❌ 加载天气影响数据异常:', error)
  } finally {
    loading.value = false
  }
}

// 加载出租车需求数据
const loadTaxiData = async () => {
  try {
    loading.value = true
    console.log('🚕 加载出租车需求数据...')
    
    const response = await smartPassengerAPI.analyzeTaxiDemand({
      historical_analysis: true,
      hotspot_analysis: true,
      time_window: '1h'
    })
    
    if (response.success) {
      taxiData.value = response
      console.log('✅ 出租车需求数据加载成功')
    } else {
      console.error('❌ 出租车需求数据加载失败:', response.message)
    }
  } catch (error) {
    console.error('❌ 加载出租车需求数据异常:', error)
  } finally {
    loading.value = false
  }
}

// 加载历史分析数据
const loadHistoricalData = async () => {
  try {
    console.log('📊 加载历史分析数据...')
    
    const response = await smartPassengerAPI.getHistoricalAnalysis()
    
    if (response.success) {
      realTimeData.value = response.historical_data
      
      // 更新历史统计
      if (response.historical_data) {
        realTimeStats.value = {
          activePassengers: response.historical_data.passenger_stats?.active_passengers || 0,
          loadedTaxis: response.historical_data.taxi_stats?.loaded_taxis || 0,
          demandIndex: (response.historical_data.taxi_stats?.avg_demand_index * 100).toFixed(1) || 0,
          weatherImpact: '晴天'
        }
      }
      
      console.log('✅ 历史分析数据加载成功')
    } else {
      console.error('❌ 历史分析数据加载失败:', response.message)
    }
  } catch (error) {
    console.error('❌ 加载历史分析数据异常:', error)
  }
}

// 刷新所有数据
const refreshAllData = async () => {
  await Promise.all([
    loadWeatherData(),
    loadTaxiData(),
    loadHistoricalData()
  ])
}

// 新增：加载每日天气影响数据
const loadDailyWeatherImpact = async () => {
  try {
    loading.value = true
    const now = Date.now() / 1000
    // 取近7天数据
    const start = now - 7 * 24 * 3600
    const end = now
    const res = await smartPassengerAPI.analyzeDailyWeatherImpact({ start_time: start, end_time: end })
    if (res.success && res.daily_impacts.length > 0) {
      dailyImpacts.value = res.daily_impacts
      selectedDate.value = res.daily_impacts[0].date
    }
  } catch (e) {
    console.error('加载每日天气影响失败', e)
  } finally {
    loading.value = false
  }
}

// 组件挂载
onMounted(() => {
  console.log('🚀 智能客流分析模块初始化...')
  
  // 更新时间
  updateCurrentTime()
  const timeTimer = setInterval(updateCurrentTime, 1000)
  
  // 初始化数据
  refreshAllData()
  loadDailyWeatherImpact() // 初始化每日天气影响数据
  
  // 设置定时刷新（每30秒）
  refreshTimer = setInterval(() => {
    loadHistoricalData()
  }, 30000)
  
  // 清理定时器
  onUnmounted(() => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
    }
    if (timeTimer) {
      clearInterval(timeTimer)
    }
  })
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

/* 卡片悬停效果 */
.hover\:bg-white\/15:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

/* 渐变背景 */
.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}
</style> 
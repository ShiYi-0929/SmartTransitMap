<template>
  <div class="space-y-6">
    <!-- 查询控制面板 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
      <h2 class="text-xl font-semibold text-white mb-4 flex items-center">
        <Search class="h-5 w-5 mr-2 text-cyan-400" />
        交通数据查询
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- 时间查询 -->
        <div class="space-y-2">
          <label class="text-sm text-gray-300">起始时间</label>
          <input 
            v-model="queryParams.startTime"
            type="datetime-local" 
            class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
          />
        </div>
        
        <div class="space-y-2">
          <label class="text-sm text-gray-300">结束时间</label>
          <input 
            v-model="queryParams.endTime"
            type="datetime-local" 
            class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
          />
        </div>
        
        <!-- 车辆ID查询 -->
        <div class="space-y-2">
          <label class="text-sm text-gray-300">车辆标识 (可选)</label>
          <input 
            v-model="queryParams.vehicleId"
            type="text" 
            placeholder="输入车辆ID查看轨迹"
            class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
          />
        </div>
      </div>
      
      <div class="flex space-x-4 mt-4">
        <button 
          @click="queryTrafficData"
          :disabled="loading"
          class="px-6 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-500 text-white rounded-lg transition-colors duration-300 flex items-center"
        >
          <Search class="h-4 w-4 mr-2" />
          {{ loading ? '查询中...' : '查询数据' }}
        </button>
        
        <button 
          @click="clearResults"
          class="px-6 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors duration-300 flex items-center"
        >
          <X class="h-4 w-4 mr-2" />
          清除结果
        </button>
      </div>
    </div>

    <!-- 地图显示区域 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-white flex items-center">
          <MapPin class="h-5 w-5 mr-2 text-cyan-400" />
          交通分布地图
        </h2>
        
        <div class="flex space-x-2">
          <button 
            v-for="view in mapViews" 
            :key="view.key"
            @click="currentMapView = view.key"
            :class="[
              'px-3 py-1 rounded-lg text-sm transition-colors duration-300',
              currentMapView === view.key 
                ? 'bg-cyan-500 text-white' 
                : 'bg-white/10 text-gray-300 hover:bg-white/20'
            ]"
          >
            {{ view.name }}
          </button>
        </div>
      </div>
      
      <!-- 地图容器 -->
      <div class="h-96 bg-gray-800 rounded-lg relative overflow-hidden">
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="text-center">
            <MapPin class="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <p class="text-gray-400">地图组件将在这里显示</p>
            <p class="text-sm text-gray-500 mt-2">集成百度地图或高德地图API</p>
          </div>
        </div>
        
        <!-- 数据点显示 -->
        <div v-if="trafficData.length > 0" class="absolute top-4 left-4 bg-black/50 rounded-lg p-3">
          <p class="text-white text-sm">找到 {{ trafficData.length }} 条数据</p>
          <p class="text-gray-300 text-xs">{{ queryParams.vehicleId ? '车辆轨迹模式' : '区域分布模式' }}</p>
        </div>
      </div>
    </div>

    <!-- 数据统计面板 -->
    <div v-if="trafficData.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <h3 class="text-lg font-semibold text-white mb-3 flex items-center">
          <Activity class="h-5 w-5 mr-2 text-green-400" />
          数据概览
        </h3>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-gray-300">总数据点:</span>
            <span class="text-white font-semibold">{{ trafficData.length }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">时间跨度:</span>
            <span class="text-white font-semibold">{{ timeSpan }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">覆盖区域:</span>
            <span class="text-white font-semibold">{{ coverageArea }}</span>
          </div>
        </div>
      </div>
      
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <h3 class="text-lg font-semibold text-white mb-3 flex items-center">
          <Car class="h-5 w-5 mr-2 text-blue-400" />
          车辆信息
        </h3>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-gray-300">活跃车辆:</span>
            <span class="text-white font-semibold">{{ activeVehicles }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">平均速度:</span>
            <span class="text-white font-semibold">{{ averageSpeed }} km/h</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">总里程:</span>
            <span class="text-white font-semibold">{{ totalDistance }} km</span>
          </div>
        </div>
      </div>
      
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <h3 class="text-lg font-semibold text-white mb-3 flex items-center">
          <TrendingUp class="h-5 w-5 mr-2 text-purple-400" />
          实时状态
        </h3>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-gray-300">更新时间:</span>
            <span class="text-white font-semibold">{{ lastUpdate }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">数据状态:</span>
            <span class="text-green-400 font-semibold">● 正常</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">连接状态:</span>
            <span class="text-green-400 font-semibold">● 在线</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, MapPin, X, Activity, Car, TrendingUp } from 'lucide-vue-next'

// 响应式数据
const loading = ref(false)
const trafficData = ref([])
const currentMapView = ref('distribution')

const queryParams = ref({
  startTime: '',
  endTime: '',
  vehicleId: ''
})

const mapViews = [
  { key: 'distribution', name: '分布视图' },
  { key: 'trajectory', name: '轨迹视图' },
  { key: 'heatmap', name: '热力图' }
]

// 计算属性
const timeSpan = computed(() => {
  if (!queryParams.value.startTime || !queryParams.value.endTime) return '-'
  const start = new Date(queryParams.value.startTime)
  const end = new Date(queryParams.value.endTime)
  const hours = Math.round((end - start) / (1000 * 60 * 60))
  return `${hours} 小时`
})

const coverageArea = computed(() => {
  return trafficData.value.length > 0 ? '济南市区' : '-'
})

const activeVehicles = computed(() => {
  const uniqueVehicles = new Set(trafficData.value.map(item => item.vehicleId))
  return uniqueVehicles.size
})

const averageSpeed = computed(() => {
  if (trafficData.value.length === 0) return 0
  const totalSpeed = trafficData.value.reduce((sum, item) => sum + (item.speed || 0), 0)
  return Math.round(totalSpeed / trafficData.value.length)
})

const totalDistance = computed(() => {
  return Math.round(trafficData.value.length * 0.5) // 模拟计算
})

const lastUpdate = computed(() => {
  return new Date().toLocaleTimeString()
})

// 方法
const queryTrafficData = async () => {
  if (!queryParams.value.startTime || !queryParams.value.endTime) {
    alert('请选择查询时间范围')
    return
  }
  
  loading.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 生成模拟数据
    const mockData = []
    const dataCount = Math.floor(Math.random() * 500) + 100
    
    for (let i = 0; i < dataCount; i++) {
      mockData.push({
        id: i,
        vehicleId: queryParams.value.vehicleId || `V${Math.floor(Math.random() * 1000)}`,
        latitude: 36.651 + (Math.random() - 0.5) * 0.1,
        longitude: 117.120 + (Math.random() - 0.5) * 0.1,
        timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
        speed: Math.floor(Math.random() * 60) + 10,
        status: Math.random() > 0.8 ? 'occupied' : 'available'
      })
    }
    
    trafficData.value = mockData
    
  } catch (error) {
    console.error('查询失败:', error)
    alert('查询失败，请重试')
  } finally {
    loading.value = false
  }
}

const clearResults = () => {
  trafficData.value = []
  queryParams.value = {
    startTime: '',
    endTime: '',
    vehicleId: ''
  }
}

onMounted(() => {
  // 设置默认时间范围（最近1小时）
  const now = new Date()
  const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000)
  
  queryParams.value.endTime = now.toISOString().slice(0, 16)
  queryParams.value.startTime = oneHourAgo.toISOString().slice(0, 16)
})
</script>
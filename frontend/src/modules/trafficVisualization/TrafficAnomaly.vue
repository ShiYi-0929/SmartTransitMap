<template>
  <div class="anomaly-detection-container">
    <!-- 页面标题和总览 -->
    <div class="mb-6">
      <div class="bg-gradient-to-r from-red-900/50 via-orange-900/50 to-yellow-900/50 rounded-xl p-6 border border-red-500/30">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div class="bg-red-500/20 p-3 rounded-lg mr-4">
              <AlertTriangleIcon class="w-8 h-8 text-red-400" />
            </div>
            <div>
              <h2 class="text-2xl font-bold text-white mb-1">交通异常检测与可视化</h2>
              <p class="text-gray-300">基于真实GPS数据的智能异常事件识别与分析</p>
            </div>
          </div>
          <div class="flex items-center space-x-6">
            <div class="text-center">
              <div class="text-3xl font-bold text-red-400">{{ statistics.total_count || 0 }}</div>
              <div class="text-sm text-gray-300">异常事件</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-orange-400">{{ statistics.by_severity?.high || 0 }}</div>
              <div class="text-sm text-gray-300">高危异常</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-green-400">{{ isRealTimeMode ? '历史' : '历史' }}</div>
              <div class="text-sm text-gray-300">检测模式</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 控制面板 -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
      <!-- 检测配置 -->
      <div class="lg:col-span-1 space-y-4">
        <!-- 模式切换 -->
        <div class="bg-blue-900/30 rounded-xl p-4 border border-blue-500/30">
          <h3 class="text-lg font-semibold text-white mb-3 flex items-center">
            <SettingsIcon class="w-5 h-5 mr-2" />
            检测模式
          </h3>
          <div class="space-y-2">
            <label class="flex items-center">
              <input 
                v-model="isRealTimeMode" 
                type="checkbox" 
                class="mr-2 rounded bg-blue-900/50 border-blue-500/50 text-blue-500"
              />
              <span class="text-white">历史监控模式</span>
            </label>
          </div>
        </div>

        <!-- 时间范围 -->
        <div class="bg-blue-900/30 rounded-xl p-4 border border-blue-500/30" v-if="!isRealTimeMode">
          <h3 class="text-lg font-semibold text-white mb-3 flex items-center">
            <ClockIcon class="w-5 h-5 mr-2" />
            时间范围
          </h3>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-gray-300 mb-1">开始时间</label>
              <input 
                v-model="detectionParams.startTime"
                type="datetime-local" 
                class="w-full p-2 bg-blue-900/50 border border-blue-500/50 rounded text-white text-sm"
                :min="minDate"
                :max="maxDate"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">结束时间</label>
              <input 
                v-model="detectionParams.endTime"
                type="datetime-local" 
                class="w-full p-2 bg-blue-900/50 border border-blue-500/50 rounded text-white text-sm"
                :min="minDate"
                :max="maxDate"
              />
            </div>
          </div>
        </div>

        <!-- 检测类型 -->
        <div class="bg-blue-900/30 rounded-xl p-4 border border-blue-500/30">
          <h3 class="text-lg font-semibold text-white mb-3 flex items-center">
            <ScanIcon class="w-5 h-5 mr-2" />
            异常类型
          </h3>
          <div class="space-y-2">
            <label class="flex items-center">
              <input 
                v-model="detectionParams.detectAll" 
                type="checkbox" 
                class="mr-2 rounded bg-blue-900/50 border-blue-500/50 text-blue-500"
                @change="toggleDetectAll"
              />
              <span class="text-white font-medium">全部检测</span>
            </label>
            <div v-for="type in anomalyTypes" :key="type.type" class="ml-4">
              <label class="flex items-center">
                <input 
                  v-model="detectionParams.selectedTypes" 
                  :value="type.type"
                  type="checkbox" 
                  class="mr-2 rounded bg-blue-900/50 border-blue-500/50 text-blue-500"
                  :disabled="detectionParams.detectAll"
                />
                <span class="text-sm text-gray-300">{{ type.name }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- 阈值配置 -->
        <div class="bg-blue-900/30 rounded-xl p-4 border border-blue-500/30">
          <h3 class="text-lg font-semibold text-white mb-3 flex items-center">
            <SlidersHorizontalIcon class="w-5 h-5 mr-2" />
            检测阈值
          </h3>
          <div class="space-y-3 text-sm">
            <div>
              <label class="block text-gray-300 mb-1">停车时长 (分钟)</label>
              <input 
                v-model.number="thresholds.long_stop_duration_minutes"
                type="number" 
                min="1" 
                max="60"
                class="w-full p-2 bg-blue-900/50 border border-blue-500/50 rounded text-white text-sm"
              />
            </div>
            <div>
              <label class="block text-gray-300 mb-1">低速阈值 (km/h)</label>
              <input 
                v-model.number="thresholds.speed_threshold_low"
                type="number" 
                min="1" 
                max="20"
                class="w-full p-2 bg-blue-900/50 border border-blue-500/50 rounded text-white text-sm"
              />
            </div>
            <div>
              <label class="block text-gray-300 mb-1">高速阈值 (km/h)</label>
              <input 
                v-model.number="thresholds.speed_threshold_high"
                type="number" 
                min="40" 
                max="150"
                class="w-full p-2 bg-blue-900/50 border border-blue-500/50 rounded text-white text-sm"
              />
            </div>
            <div>
              <label class="block text-gray-300 mb-1">聚集密度</label>
              <input 
                v-model.number="thresholds.cluster_density"
                type="number" 
                min="10" 
                max="200"
                class="w-full p-2 bg-blue-900/50 border border-blue-500/50 rounded text-white text-sm"
              />
            </div>
          </div>
        </div>

        <!-- 控制按钮 -->
        <div class="space-y-2">
          <button 
            @click="startDetection"
            :disabled="isDetecting"
            class="w-full btn-tech flex items-center justify-center"
          >
            <LoaderIcon v-if="isDetecting" class="w-4 h-4 mr-2 animate-spin" />
            <PlayIcon v-else class="w-4 h-4 mr-2" />
            {{ isDetecting ? '检测中...' : '开始检测' }}
          </button>
          <button 
            @click="clearResults"
            class="w-full btn-tech-secondary flex items-center justify-center"
          >
            <RefreshCwIcon class="w-4 h-4 mr-2" />
            清除结果
          </button>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="lg:col-span-3 space-y-6">
        <!-- 统计卡片 -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-red-900/30 rounded-xl p-4 border border-red-500/30">
            <div class="flex items-center">
              <AlertTriangleIcon class="w-6 h-6 text-red-400 mr-3" />
              <div>
                <div class="text-2xl font-bold text-white">{{ statistics.by_severity?.high || 0 }}</div>
                <div class="text-sm text-gray-300">高危异常</div>
              </div>
            </div>
          </div>
          <div class="bg-orange-900/30 rounded-xl p-4 border border-orange-500/30">
            <div class="flex items-center">
              <AlertCircleIcon class="w-6 h-6 text-orange-400 mr-3" />
              <div>
                <div class="text-2xl font-bold text-white">{{ statistics.by_severity?.medium || 0 }}</div>
                <div class="text-sm text-gray-300">中危异常</div>
              </div>
            </div>
          </div>
          <div class="bg-yellow-900/30 rounded-xl p-4 border border-yellow-500/30">
            <div class="flex items-center">
              <InfoIcon class="w-6 h-6 text-yellow-400 mr-3" />
              <div>
                <div class="text-2xl font-bold text-white">{{ statistics.by_severity?.low || 0 }}</div>
                <div class="text-sm text-gray-300">低危异常</div>
              </div>
            </div>
          </div>
          <div class="bg-blue-900/30 rounded-xl p-4 border border-blue-500/30">
            <div class="flex items-center">
              <BarChart3Icon class="w-6 h-6 text-blue-400 mr-3" />
              <div>
                <div class="text-2xl font-bold text-white">{{ Object.keys(statistics.by_type || {}).length }}</div>
                <div class="text-sm text-gray-300">异常类型</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 地图可视化 -->
        <div class="bg-blue-900/30 rounded-xl border border-blue-500/30 overflow-hidden">
          <div class="p-4 border-b border-blue-500/30 flex items-center justify-between">
            <h3 class="text-xl font-semibold text-white flex items-center">
              <MapIcon class="w-6 h-6 mr-2" />
              异常事件地图
            </h3>
            <div class="flex items-center space-x-2">
              <select 
                v-model="selectedAnomalyTypeFilter"
                class="px-3 py-1 bg-blue-900/50 border border-blue-500/50 rounded text-white text-sm"
                @change="filterAnomaliesByType"
              >
                <option value="all">全部类型</option>
                <option v-for="type in anomalyTypes" :key="type.type" :value="type.type">
                  {{ type.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="relative">
            <div :id="mapContainerId" class="w-full h-96"></div>
            <div v-if="!mapInitialized" class="absolute inset-0 flex items-center justify-center bg-blue-900/50">
              <div class="text-white">地图加载中...</div>
            </div>
          </div>
        </div>

        <!-- 异常事件列表 -->
        <div class="bg-blue-900/30 rounded-xl border border-blue-500/30">
          <div class="p-4 border-b border-blue-500/30 flex items-center justify-between">
            <h3 class="text-xl font-semibold text-white flex items-center">
              <ListIcon class="w-6 h-6 mr-2" />
              异常事件列表
              <span class="ml-2 px-2 py-1 bg-red-500/20 text-red-400 text-sm rounded">
                {{ filteredAnomalies.length }}
              </span>
            </h3>
            <div class="flex items-center space-x-2">
              <select 
                v-model="sortBy"
                class="px-3 py-1 bg-blue-900/50 border border-blue-500/50 rounded text-white text-sm"
                @change="sortAnomalies"
              >
                <option value="timestamp">按时间排序</option>
                <option value="severity">按严重程度</option>
                <option value="type">按类型排序</option>
              </select>
              <button 
                @click="exportAnomalies"
                class="px-3 py-1 bg-green-600/50 hover:bg-green-600/70 border border-green-500/50 rounded text-white text-sm flex items-center"
              >
                <DownloadIcon class="w-4 h-4 mr-1" />
                导出
              </button>
            </div>
          </div>
          <div class="max-h-96 overflow-y-auto">
            <div v-if="filteredAnomalies.length === 0" class="p-8 text-center text-gray-400">
              <ScanIcon class="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>暂无异常事件</p>
              <p class="text-sm mt-1">点击"开始检测"来搜索异常事件</p>
            </div>
            <div v-else class="divide-y divide-blue-500/20">
              <div 
                v-for="anomaly in filteredAnomalies.slice(0, 50)" 
                :key="anomaly.id"
                class="p-4 hover:bg-blue-800/30 cursor-pointer transition-colors"
                @click="selectAnomaly(anomaly)"
              >
                <div class="flex items-start justify-between">
                  <div class="flex items-start">
                    <div :class="getSeverityIndicator(anomaly.severity)" class="w-3 h-3 rounded-full mt-1 mr-3 flex-shrink-0"></div>
                    <div class="flex-1">
                      <div class="flex items-center space-x-2">
                        <h4 class="text-white font-medium">{{ anomaly.name }}</h4>
                        <span :class="getSeverityBadge(anomaly.severity)" class="px-2 py-1 rounded text-xs font-medium">
                          {{ getSeverityText(anomaly.severity) }}
                        </span>
                        <span class="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
                          {{ getTypeText(anomaly.type) }}
                        </span>
                      </div>
                      <p class="text-gray-300 text-sm mt-1">{{ anomaly.description }}</p>
                      <div class="flex items-center space-x-4 mt-2 text-xs text-gray-400">
                        <span class="flex items-center">
                          <ClockIcon class="w-3 h-3 mr-1" />
                          {{ formatTime(anomaly.timestamp) }}
                        </span>
                        <span class="flex items-center" v-if="anomaly.vehicle_id">
                          <CarIcon class="w-3 h-3 mr-1" />
                          车辆: {{ anomaly.vehicle_id }}
                        </span>
                        <span class="flex items-center">
                          <MapPinIcon class="w-3 h-3 mr-1" />
                          {{ anomaly.latitude?.toFixed(4) }}, {{ anomaly.longitude?.toFixed(4) }}
                        </span>
                      </div>
                    </div>
                  </div>
                  <button 
                    @click.stop="locateOnMap(anomaly)"
                    class="px-2 py-1 bg-cyan-600/50 hover:bg-cyan-600/70 border border-cyan-500/50 rounded text-white text-xs flex items-center"
                  >
                    <EyeIcon class="w-3 h-3 mr-1" />
                    定位
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情模态框 -->
    <div v-if="selectedAnomaly" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click="closeAnomalyDetail">
      <div class="bg-blue-900 rounded-xl border border-blue-500/50 max-w-2xl w-full m-4 max-h-[80vh] overflow-y-auto" @click.stop>
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-bold text-white flex items-center">
              <AlertTriangleIcon class="w-6 h-6 mr-2 text-red-400" />
              异常事件详情
            </h3>
            <button @click="closeAnomalyDetail" class="text-gray-400 hover:text-white">
              <XIcon class="w-6 h-6" />
            </button>
          </div>
          
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm text-gray-300 mb-1">异常类型</label>
                <div class="text-white font-medium">{{ selectedAnomaly.name }}</div>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">严重程度</label>
                <span :class="getSeverityBadge(selectedAnomaly.severity)" class="px-3 py-1 rounded font-medium">
                  {{ getSeverityText(selectedAnomaly.severity) }}
                </span>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">发生时间</label>
                <div class="text-white">{{ formatTime(selectedAnomaly.timestamp) }}</div>
              </div>
              <div v-if="selectedAnomaly.vehicle_id">
                <label class="block text-sm text-gray-300 mb-1">车辆ID</label>
                <div class="text-white font-mono">{{ selectedAnomaly.vehicle_id }}</div>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">位置坐标</label>
                <div class="text-white font-mono text-sm">
                  {{ selectedAnomaly.latitude?.toFixed(6) }}, {{ selectedAnomaly.longitude?.toFixed(6) }}
                </div>
              </div>
            </div>
            
            <div>
              <label class="block text-sm text-gray-300 mb-1">详细描述</label>
              <div class="text-white bg-blue-800/30 p-3 rounded">{{ selectedAnomaly.description }}</div>
            </div>
            
            <div v-if="selectedAnomaly.details">
              <label class="block text-sm text-gray-300 mb-2">技术详情</label>
              <div class="bg-blue-800/30 p-3 rounded">
                <pre class="text-sm text-gray-300 whitespace-pre-wrap">{{ JSON.stringify(selectedAnomaly.details, null, 2) }}</pre>
              </div>
            </div>
            
            <div class="flex space-x-2 pt-4">
              <button 
                @click="locateOnMap(selectedAnomaly)"
                class="flex-1 btn-tech flex items-center justify-center"
              >
                <MapPinIcon class="w-4 h-4 mr-2" />
                在地图上定位
              </button>
              <button 
                @click="exportSingleAnomaly(selectedAnomaly)"
                class="flex-1 btn-tech-secondary flex items-center justify-center"
              >
                <DownloadIcon class="w-4 h-4 mr-2" />
                导出详情
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { 
  AlertTriangleIcon, 
  SettingsIcon, 
  ClockIcon, 
  ScanIcon, 
  SlidersHorizontalIcon,
  PlayIcon,
  LoaderIcon,
  RefreshCwIcon,
  BarChart3Icon,
  MapIcon,
  ListIcon,
  DownloadIcon,
  EyeIcon,
  XIcon,
  MapPinIcon,
  AlertCircleIcon,
  InfoIcon,
  CarIcon
} from 'lucide-vue-next'
import { 
  detectAnomalies, 
  getRealtimeAnomalies, 
  getAnomalyTypes, 
  getAnomalyHeatmap 
} from '@/api/traffic'

// 地图相关
const mapContainerId = 'anomaly-map-' + Date.now()
let map = null
let markers = []
let heatmapLayer = null
const mapInitialized = ref(false)

// 基础状态
const isRealTimeMode = ref(false)
const isDetecting = ref(false)
const showHeatmap = ref(false)
const selectedAnomalyTypeFilter = ref('all')
const sortBy = ref('timestamp')

// 时间限制 - 基于真实数据的时间范围
const minDate = "2013-09-12T00:00"
const maxDate = "2013-09-18T23:59"

// 检测参数
const detectionParams = ref({
  startTime: "2013-09-13T08:00",
  endTime: "2013-09-13T12:00",
  detectAll: true,
  selectedTypes: []
})

// 阈值配置
const thresholds = ref({
  long_stop_duration_minutes: 5,
  speed_threshold_low: 0,
  speed_threshold_high: 80,
  cluster_density: 50
})

// 数据状态
const anomalyTypes = ref([])
const anomalies = ref([])
const statistics = ref({})
const selectedAnomaly = ref(null)

// 计算属性
const filteredAnomalies = computed(() => {
  if (selectedAnomalyTypeFilter.value === 'all') {
    return anomalies.value
  }
  return anomalies.value.filter(anomaly => anomaly.type === selectedAnomalyTypeFilter.value)
})

// 实时监控定时器
let realtimeTimer = null

// 方法
async function initMap() {
  if (!window.AMap) {
    await loadAMapAPI()
  }
  
  map = new window.AMap.Map(mapContainerId, {
    center: [117.120, 36.651], // 济南市中心
    zoom: 11,
    mapStyle: 'amap://styles/dark'
  })
  
  map.plugin(['AMap.ToolBar', 'AMap.Scale'], function() {
    map.addControl(new window.AMap.ToolBar())
    map.addControl(new window.AMap.Scale())
  })
  
  mapInitialized.value = true
}

function loadAMapAPI() {
  return new Promise((resolve, reject) => {
    if (window.AMap) {
      resolve()
      return
    }
    
    const script = document.createElement('script')
    script.src = 'https://webapi.amap.com/maps?v=2.0&key=ac9b745946df9aee02cf0515319407df&callback=initAMap'
    
    window.initAMap = () => {
      resolve()
      delete window.initAMap
    }
    
    script.onerror = reject
    document.head.appendChild(script)
  })
}

async function loadAnomalyTypes() {
  try {
    const response = await getAnomalyTypes()
    if (response.data.success) {
      anomalyTypes.value = response.data.anomaly_types
    }
  } catch (error) {
    console.error('加载异常类型失败:', error)
    // 使用默认异常类型
    anomalyTypes.value = [
      { type: 'long_stop', name: '长时间停车' },
      { type: 'speed_anomaly', name: '速度异常' },
      { type: 'cluster_anomaly', name: '异常聚集' },
      { type: 'abnormal_route', name: '异常绕路' }
    ]
  }
}

function toggleDetectAll() {
  if (detectionParams.value.detectAll) {
    detectionParams.value.selectedTypes = []
  }
}

async function startDetection() {
  if (isDetecting.value) return
  
  isDetecting.value = true
  
  try {
    if (isRealTimeMode.value) {
      await detectRealtimeAnomalies()
      startRealtimeMonitoring()
    } else {
      await detectHistoricalAnomalies()
    }
  } catch (error) {
    console.error('异常检测失败:', error)
    alert('异常检测失败，请检查参数后重试')
  } finally {
    isDetecting.value = false
  }
}

async function detectRealtimeAnomalies() {
  try {
    const response = await getRealtimeAnomalies(3600, 100)
    
    if (response.data.success) {
      anomalies.value = response.data.anomalies
      updateStatistics()
      displayAnomaliesOnMap()
    }
  } catch (error) {
    console.error('历史异常检测失败:', error)
  }
}

async function detectHistoricalAnomalies() {
  try {
    // 转换时间为时间戳
    const startTimestamp = new Date(detectionParams.value.startTime).getTime() / 1000
    const endTimestamp = new Date(detectionParams.value.endTime).getTime() / 1000
    
    // 确定检测类型
    let detectionTypes = 'all'
    if (!detectionParams.value.detectAll && detectionParams.value.selectedTypes.length > 0) {
      detectionTypes = detectionParams.value.selectedTypes.join(',')
    }
    
    // 准备阈值参数
    const thresholdParams = {
      long_stop_duration: thresholds.value.long_stop_duration_minutes * 60,
      speed_threshold_low: thresholds.value.speed_threshold_low,
      speed_threshold_high: thresholds.value.speed_threshold_high,
      cluster_density: thresholds.value.cluster_density
    }
    
    console.log('开始异常检测:', {
      startTimestamp,
      endTimestamp,
      detectionTypes,
      thresholdParams
    })
    
    const response = await detectAnomalies(startTimestamp, endTimestamp, detectionTypes, thresholdParams)
    
    if (response.data.success) {
      anomalies.value = response.data.anomalies
      statistics.value = response.data.statistics
      displayAnomaliesOnMap()
      console.log('异常检测完成:', response.data)
    } else {
      alert(response.data.message || '检测失败')
    }
  } catch (error) {
    console.error('历史异常检测失败:', error)
    alert('检测失败: ' + error.message)
  }
}

function startRealtimeMonitoring() {
  if (realtimeTimer) {
    clearInterval(realtimeTimer)
  }
  
  if (isRealTimeMode.value) {
    realtimeTimer = setInterval(() => {
      detectRealtimeAnomalies()
    }, 30000) // 30秒刷新一次
  }
}

function updateStatistics() {
  const stats = {
    total_count: anomalies.value.length,
    by_type: {},
    by_severity: { high: 0, medium: 0, low: 0 }
  }
  
  anomalies.value.forEach(anomaly => {
    // 按类型统计
    const type = anomaly.type || 'unknown'
    stats.by_type[type] = (stats.by_type[type] || 0) + 1
    
    // 按严重程度统计
    const severity = anomaly.severity || 'low'
    if (stats.by_severity[severity] !== undefined) {
      stats.by_severity[severity]++
    }
  })
  
  statistics.value = stats
}

function displayAnomaliesOnMap() {
  if (!map) return
  
  clearMapMarkers()
  
  if (showHeatmap.value) {
    displayHeatmap()
  } else {
    displayMarkers()
  }
}

function displayMarkers() {
  const colorMap = {
    'high': '#ff4444',
    'medium': '#ffa726',
    'low': '#ffeb3b'
  }
  
  filteredAnomalies.value.forEach(anomaly => {
    const color = colorMap[anomaly.severity] || '#666666'
    
    const marker = new window.AMap.Marker({
      position: [anomaly.longitude, anomaly.latitude],
      icon: new window.AMap.Icon({
        size: new window.AMap.Size(24, 24),
        image: `data:image/svg+xml;base64,${btoa(`
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" fill="${color}" stroke="#fff" stroke-width="2"/>
            <path d="M12 8v4l3 3" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
          </svg>
        `)}`
      }),
      title: anomaly.name,
      extData: anomaly
    })
    
    marker.on('click', () => {
      selectAnomaly(anomaly)
    })
    
    map.add(marker)
    markers.push(marker)
  })
  
  // 自适应视野
  if (markers.length > 0) {
    map.setFitView(markers, false, [50, 50, 50, 50])
  }
}

async function displayHeatmap() {
  if (!map || filteredAnomalies.value.length === 0) return
  
  try {
    // 获取热力图数据
    const startTimestamp = new Date(detectionParams.value.startTime).getTime() / 1000
    const endTimestamp = new Date(detectionParams.value.endTime).getTime() / 1000
    
    const response = await getAnomalyHeatmap(
      startTimestamp, 
      endTimestamp, 
      selectedAnomalyTypeFilter.value
    )
    
    if (response.data.success && response.data.heatmap_points.length > 0) {
      const heatmapData = response.data.heatmap_points.map(point => ({
        lng: point.lng,
        lat: point.lat,
        count: point.intensity || point.count
      }))
      
      // 移除旧的热力图
      if (heatmapLayer) {
        map.remove(heatmapLayer)
      }
      
      // 创建新的热力图
      map.plugin(['AMap.Heatmap'], () => {
        heatmapLayer = new window.AMap.Heatmap(map, {
          radius: 25,
          opacity: [0, 0.8],
          gradient: {
            0.4: '#00ff00',
            0.6: '#ffff00',
            0.8: '#ff8800',
            1.0: '#ff0000'
          }
        })
        
        heatmapLayer.setDataSet({
          data: heatmapData,
          max: Math.max(...heatmapData.map(d => d.count))
        })
      })
    }
  } catch (error) {
    console.error('显示热力图失败:', error)
  }
}

function clearMapMarkers() {
  markers.forEach(marker => map.remove(marker))
  markers = []
  
  if (heatmapLayer) {
    map.remove(heatmapLayer)
    heatmapLayer = null
  }
}

function clearResults() {
  anomalies.value = []
  statistics.value = {}
  selectedAnomaly.value = null
  clearMapMarkers()
  
  if (realtimeTimer) {
    clearInterval(realtimeTimer)
    realtimeTimer = null
  }
}

function filterAnomaliesByType() {
  displayAnomaliesOnMap()
}

function sortAnomalies() {
  switch (sortBy.value) {
    case 'timestamp':
      anomalies.value.sort((a, b) => b.timestamp - a.timestamp)
      break
    case 'severity':
      const severityOrder = { high: 3, medium: 2, low: 1 }
      anomalies.value.sort((a, b) => severityOrder[b.severity] - severityOrder[a.severity])
      break
    case 'type':
      anomalies.value.sort((a, b) => a.type.localeCompare(b.type))
      break
  }
}

function selectAnomaly(anomaly) {
  selectedAnomaly.value = anomaly
}

function closeAnomalyDetail() {
  selectedAnomaly.value = null
}

function locateOnMap(anomaly) {
  if (!map) return
  
  map.setCenter([anomaly.longitude, anomaly.latitude])
  map.setZoom(15)
  
  // 高亮标记
  const marker = markers.find(m => m.getExtData()?.id === anomaly.id)
  if (marker) {
    marker.setAnimation('AMAP_ANIMATION_BOUNCE')
    setTimeout(() => {
      marker.setAnimation('AMAP_ANIMATION_NONE')
    }, 3000)
  }
  
  closeAnomalyDetail()
}

function exportAnomalies() {
  if (anomalies.value.length === 0) return
  
  const dataStr = JSON.stringify(anomalies.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `anomalies_${Date.now()}.json`
  link.click()
  
  URL.revokeObjectURL(url)
}

function exportSingleAnomaly(anomaly) {
  const dataStr = JSON.stringify(anomaly, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `anomaly_${anomaly.id}.json`
  link.click()
  
  URL.revokeObjectURL(url)
}

// 辅助函数
function getSeverityIndicator(severity) {
  const classes = {
    'high': 'bg-red-500',
    'medium': 'bg-orange-500',
    'low': 'bg-yellow-500'
  }
  return classes[severity] || 'bg-gray-500'
}

function getSeverityBadge(severity) {
  const classes = {
    'high': 'bg-red-500/20 text-red-400 border border-red-500/30',
    'medium': 'bg-orange-500/20 text-orange-400 border border-orange-500/30',
    'low': 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
  }
  return classes[severity] || 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
}

function getSeverityText(severity) {
  const texts = {
    'high': '高危',
    'medium': '中危',
    'low': '低危'
  }
  return texts[severity] || '未知'
}

function getTypeText(type) {
  const typeMap = anomalyTypes.value.reduce((map, t) => {
    map[t.type] = t.name
    return map
  }, {})
  return typeMap[type] || type
}

function formatTime(timestamp) {
  return new Date(timestamp * 1000).toLocaleString('zh-CN')
}

// 监听模式变化
watch(isRealTimeMode, (newVal) => {
  if (!newVal && realtimeTimer) {
    clearInterval(realtimeTimer)
    realtimeTimer = null
  }
})

watch(showHeatmap, () => {
  displayAnomaliesOnMap()
})

// 生命周期
onMounted(async () => {
  await loadAnomalyTypes()
  
  setTimeout(() => {
    initMap()
  }, 500)
})

onUnmounted(() => {
  if (realtimeTimer) {
    clearInterval(realtimeTimer)
  }
  
  if (map) {
    map.destroy()
  }
})
</script>

<style scoped>
.anomaly-detection-container {
  padding: 20px;
  min-height: 100vh;
}

.btn-tech {
  padding: 8px 16px;
  background: linear-gradient(135deg, #dc2626, #ef4444);
  border: none;
  border-radius: 6px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-tech:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
}

.btn-tech:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-tech-secondary {
  padding: 8px 16px;
  background: rgba(75, 85, 99, 0.8);
  border: 1px solid rgba(156, 163, 175, 0.3);
  border-radius: 6px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-tech-secondary:hover {
  background: rgba(107, 114, 128, 0.8);
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style> 
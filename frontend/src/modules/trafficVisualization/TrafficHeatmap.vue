<template>
  <div class="heatmap-analysis-container">
    <!-- 控制面板 -->
    <div class="card-tech p-6 mb-6">
      <h2 class="text-xl font-semibold text-white mb-4 flex items-center">
        <Thermometer class="h-5 w-5 mr-2 text-cyan-400" />
        热力图分析
      </h2>
      
      <!-- 分析参数配置 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <div class="space-y-2">
          <label class="text-sm text-blue-200">分析日期</label>
          <input 
            v-model="analysisParams.date"
            type="date" 
            class="input-tech"
            :min="minDate"
            :max="maxDate"
          />
        </div>
        <div class="space-y-2">
          <label class="text-sm text-blue-200">时间聚合间隔</label>
          <select v-model="analysisParams.timeInterval" class="input-tech">
            <option value="15">15分钟</option>
            <option value="30">30分钟</option>
            <option value="60">1小时</option>
            <option value="120">2小时</option>
            <option value="360">6小时</option>
            <option value="1440">全天</option>
          </select>
        </div>
        <div class="space-y-2">
          <label class="text-sm text-blue-200">热力图分辨率</label>
          <select v-model="analysisParams.resolution" class="input-tech">
            <option value="0.0005">高精度 (0.5m)</option>
            <option value="0.001">标准 (1m)</option>
            <option value="0.005">中等 (5m)</option>
            <option value="0.01">粗糙 (10m)</option>
          </select>
        </div>
        <div class="space-y-2">
          <label class="text-sm text-blue-200">分析类型</label>
          <select v-model="analysisParams.analysisType" class="input-tech">
            <option value="density">车辆密度</option>
            <option value="pickup">上车热点</option>
            <option value="dropoff">下车热点</option>
            <option value="speed">平均速度</option>
          </select>
        </div>
      </div>
      
      <!-- 时间段选择器 -->
      <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
          <label class="text-sm text-blue-200">分析时间段</label>
          <div class="flex space-x-2">
            <button @click="selectPeakHours('morning')" class="btn-tech-small">早高峰</button>
            <button @click="selectPeakHours('evening')" class="btn-tech-small">晚高峰</button>
            <button @click="selectPeakHours('night')" class="btn-tech-small">夜间</button>
            <button @click="selectPeakHours('all')" class="btn-tech-small">全天</button>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <input 
              v-model="analysisParams.startTime"
              type="time" 
              class="input-tech"
            />
          </div>
          <div>
            <input 
              v-model="analysisParams.endTime"
              type="time" 
              class="input-tech"
            />
          </div>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="flex space-x-4">
        <button 
          @click="generateHeatmap"
          :disabled="loading"
          class="btn-tech flex items-center text-white"
        >
          <Activity class="h-4 w-4 mr-2" />
          {{ loading ? '生成中...' : '生成热力图' }}
        </button>
        <button 
          @click="playTimeAnimation"
          :disabled="!heatmapData.length || playing"
          class="btn-tech flex items-center text-white"
        >
          <Play class="h-4 w-4 mr-2" />
          {{ playing ? '播放中...' : '时间轴播放' }}
        </button>
        <button 
          @click="exportHeatmapData"
          :disabled="!heatmapData.length"
          class="btn-tech-secondary flex items-center text-white"
        >
          <Download class="h-4 w-4 mr-2" />
          导出数据
        </button>
        <button 
          @click="clearHeatmap"
          class="btn-tech-secondary flex items-center text-white"
        >
          <X class="h-4 w-4 mr-2" />
          清除图层
        </button>
      </div>
    </div>

    <!-- 热力图显示和统计信息 -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
      <!-- 热力图地图 -->
      <div class="lg:col-span-3 card-tech p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">热力图可视化</h3>
          <div class="flex space-x-2">
            <select v-model="mapParams.style" @change="changeMapStyle" class="input-tech text-xs">
              <option value="dark">暗色主题</option>
              <option value="light">亮色主题</option>
              <option value="satellite">卫星图</option>
            </select>
            <button @click="toggleHeatmapLayer" class="btn-tech-small">
              {{ heatmapVisible ? '隐藏热力图' : '显示热力图' }}
            </button>
          </div>
        </div>
        
        <div 
          :id="mapContainerId" 
          class="w-full h-96 bg-gray-800 rounded-lg border border-blue-800"
        ></div>
        
        <!-- 时间轴控制器 -->
        <div v-if="timeSlices.length > 1" class="mt-4">
          <div class="flex items-center space-x-4">
            <button @click="prevTimeSlice" :disabled="currentTimeIndex === 0" class="btn-tech-small">
              <ChevronLeft class="h-4 w-4" />
            </button>
            <div class="flex-1">
              <input 
                type="range" 
                :min="0" 
                :max="timeSlices.length - 1"
                v-model="currentTimeIndex"
                @input="updateTimeSlice"
                class="w-full"
              />
              <div class="text-center text-sm text-blue-200 mt-1">
                {{ formatTimeSlice(timeSlices[currentTimeIndex]) }}
              </div>
            </div>
            <button @click="nextTimeSlice" :disabled="currentTimeIndex === timeSlices.length - 1" class="btn-tech-small">
              <ChevronRight class="h-4 w-4" />
            </button>
          </div>
        </div>
        
        <!-- 图例 -->
        <div class="mt-4 flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <span class="text-sm text-blue-200">密度梯度:</span>
            <div class="flex items-center space-x-1">
              <div class="w-4 h-4 bg-blue-500"></div>
              <span class="text-xs text-gray-400">低</span>
              <div class="w-4 h-4 bg-green-500"></div>
              <div class="w-4 h-4 bg-yellow-500"></div>
              <div class="w-4 h-4 bg-red-500"></div>
              <span class="text-xs text-gray-400">高</span>
            </div>
          </div>
          <div class="text-sm text-blue-200">
            数据点: {{ currentHeatmapStats.totalPoints }} | 
            最大密度: {{ currentHeatmapStats.maxDensity }}
          </div>
        </div>
      </div>
      
      <!-- 统计面板 -->
      <div class="card-tech p-6">
        <h3 class="text-lg font-semibold text-white mb-4">分析统计</h3>
        
        <!-- 整体统计 -->
        <div class="space-y-4 mb-6">
          <div v-for="stat in overallStats" :key="stat.label" class="flex justify-between">
            <span class="text-blue-200 text-sm">{{ stat.label }}</span>
            <span class="text-white font-semibold text-sm">{{ stat.value }}</span>
          </div>
        </div>
        
        <!-- 热点区域排行 -->
        <div class="mb-6">
          <h4 class="text-sm font-semibold text-blue-200 mb-3">热点区域 TOP5</h4>
          <div class="space-y-2">
            <div 
              v-for="(hotspot, index) in topHotspots" 
              :key="index"
              @click="zoomToHotspot(hotspot)"
              class="p-2 bg-gray-700 rounded cursor-pointer hover:bg-gray-600 transition-colors"
            >
              <div class="flex justify-between items-center">
                <span class="text-white text-xs">区域 {{ index + 1 }}</span>
                <span class="text-cyan-400 text-xs">{{ hotspot.density }}</span>
              </div>
              <div class="text-xs text-gray-400">
                {{ hotspot.coordinates }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- 时间分布图表 -->
        <div>
          <h4 class="text-sm font-semibold text-blue-200 mb-3">时间分布</h4>
          <div class="h-32 bg-gray-700 rounded p-2">
            <!-- 简单的时间分布条形图 -->
            <div class="flex items-end justify-between h-full">
              <div 
                v-for="(bar, index) in timeDistributionBars" 
                :key="index"
                :style="{ height: bar.height + '%' }"
                class="bg-cyan-500 w-1 rounded-t"
                :title="bar.label"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细数据表格 -->
    <div class="card-tech p-6" v-if="detailedData.length > 0">
      <h3 class="text-lg font-semibold text-white mb-4">详细数据</h3>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-600">
              <th class="text-left py-2 text-blue-200">时间段</th>
              <th class="text-left py-2 text-blue-200">区域</th>
              <th class="text-left py-2 text-blue-200">密度值</th>
              <th class="text-left py-2 text-blue-200">数据点数</th>
              <th class="text-left py-2 text-blue-200">平均速度</th>
              <th class="text-left py-2 text-blue-200">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(row, index) in detailedData.slice(0, 50)" 
              :key="index"
              class="border-b border-gray-700 hover:bg-gray-700"
            >
              <td class="py-2 text-white">{{ formatTime(row.time) }}</td>
              <td class="py-2 text-white">{{ row.region }}</td>
              <td class="py-2 text-white">{{ row.density }}</td>
              <td class="py-2 text-white">{{ row.count }}</td>
              <td class="py-2 text-white">{{ row.avgSpeed || 'N/A' }}</td>
              <td class="py-2">
                <button @click="zoomToRegion(row)" class="text-cyan-400 hover:text-cyan-300 text-xs">
                  定位
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-blue-900 p-6 rounded-lg text-white">
        <div class="flex items-center">
          <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-cyan-400 mr-3"></div>
          <span>{{ loadingMessage }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Thermometer, Activity, Play, Download, X, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { getHeatmapData, getTrafficVisualization } from '@/api/traffic'

// 响应式数据
const loading = ref(false)
const loadingMessage = ref('')
const playing = ref(false)
const heatmapData = ref([])
const timeSlices = ref([])
const currentTimeIndex = ref(0)
const heatmapVisible = ref(true)
const detailedData = ref([])

// 分析参数
const analysisParams = ref({
  date: '2013-09-13',
  timeInterval: 60, // 分钟
  resolution: 0.001,
  analysisType: 'density',
  startTime: '06:00',
  endTime: '22:00'
})

// 地图参数
const mapParams = ref({
  style: 'dark'
})

// 地图相关
const mapContainerId = `heatmap-map-${Date.now()}`
let map = null
let heatmap = null

// 时间限制
const minDate = "2013-09-12"
const maxDate = "2013-09-18"

// 计算属性
const currentHeatmapStats = computed(() => {
  if (!heatmapData.value.length || !timeSlices.value.length) {
    return { totalPoints: 0, maxDensity: 0 }
  }
  
  const currentSlice = timeSlices.value[currentTimeIndex.value]
  if (!currentSlice || !currentSlice.data) {
    return { totalPoints: 0, maxDensity: 0 }
  }
  
  const points = currentSlice.data
  return {
    totalPoints: points.length,
    maxDensity: points.length > 0 ? Math.max(...points.map(p => p.count)) : 0
  }
})

const overallStats = computed(() => {
  const data = heatmapData.value
  if (!data || data.length === 0) {
    return []
  }
  
  const totalPoints = data.length
  const counts = data.map(p => p.count || 0)
  const avgDensity = counts.reduce((sum, count) => sum + count, 0) / totalPoints
  const maxDensity = Math.max(...counts)
  
  return [
    { label: '总数据点', value: totalPoints },
    { label: '平均密度', value: avgDensity.toFixed(1) },
    { label: '最大密度', value: maxDensity },
    { label: '覆盖区域', value: `${(totalPoints * 0.001).toFixed(2)} km²` },
    { label: '时间切片', value: timeSlices.value.length }
  ]
})

const topHotspots = computed(() => {
  const data = heatmapData.value
  if (!data || data.length === 0) {
    return []
  }
  
  return [...data]
    .sort((a, b) => (b.count || 0) - (a.count || 0))
    .slice(0, 5)
    .map(point => ({
      density: point.count || 0,
      coordinates: `${point.lat.toFixed(4)}, ${point.lng.toFixed(4)}`,
      lat: point.lat,
      lng: point.lng
    }))
})

const timeDistributionBars = computed(() => {
  const slices = timeSlices.value
  if (!slices || slices.length === 0) {
    return []
  }
  
  const counts = slices.map(slice => (slice.data || []).length)
  const maxCount = Math.max(...counts, 1) // 避免除以0
  
  return slices.map((slice, index) => ({
    height: ((slice.data || []).length / maxCount) * 100,
    label: slice.label
  }))
})

// 地图初始化
async function initMap() {
  if (!window.AMap) {
    await loadAMapAPI()
  }
  
  map = new window.AMap.Map(mapContainerId, {
    center: [117.120, 36.651],
    zoom: 10,
    mapStyle: `amap://styles/${mapParams.value.style}`
  })
  
  map.plugin(['AMap.ToolBar', 'AMap.Scale'], function() {
    map.addControl(new window.AMap.ToolBar())
    map.addControl(new window.AMap.Scale())
  })
}

// 加载高德地图API
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

// 生成热力图
async function generateHeatmap() {
  loading.value = true
  loadingMessage.value = '正在生成热力图数据...'
  
  try {
    // 构建时间范围
    const startDateTime = new Date(`${analysisParams.value.date}T${analysisParams.value.startTime}:00`)
    const endDateTime = new Date(`${analysisParams.value.date}T${analysisParams.value.endTime}:00`)
    
    const startTimeStamp = startDateTime.getTime() / 1000
    const endTimeStamp = endDateTime.getTime() / 1000
    
    console.log('生成热力图参数:', {
      start: startTimeStamp,
      end: endTimeStamp,
      interval: analysisParams.value.timeInterval,
      resolution: analysisParams.value.resolution
    })
    
    // 根据时间间隔生成时间切片
    await generateTimeSlices(startTimeStamp, endTimeStamp)
    
    // 生成热力图可视化
    renderHeatmap()
    
  } catch (error) {
    console.error('生成热力图失败:', error)
    alert('生成热力图失败，请检查参数设置')
  } finally {
    loading.value = false
  }
}

// 生成时间切片
async function generateTimeSlices(startTime, endTime) {
  const intervalSeconds = analysisParams.value.timeInterval * 60
  const slices = []
  
  let currentTime = startTime
  while (currentTime < endTime) {
    const sliceEndTime = Math.min(currentTime + intervalSeconds, endTime)
    
    loadingMessage.value = `正在处理时间段: ${formatTimestamp(currentTime)} - ${formatTimestamp(sliceEndTime)}`
    
    try {
      const response = await getTrafficVisualization(
        currentTime, 
        sliceEndTime, 
        'heatmap',
        null,
        mapParams.value.style
      )
      
      if (response.data.success && response.data.data) {
        slices.push({
          startTime: currentTime,
          endTime: sliceEndTime,
          label: `${formatTimestamp(currentTime)} - ${formatTimestamp(sliceEndTime)}`,
          data: response.data.data
        })
        
        // 累积所有数据用于整体分析
        heatmapData.value.push(...response.data.data)
      }
    } catch (error) {
      console.error(`获取时间段 ${currentTime}-${sliceEndTime} 数据失败:`, error)
    }
    
    currentTime = sliceEndTime
  }
  
  timeSlices.value = slices
  currentTimeIndex.value = 0
  
  console.log(`生成了 ${slices.length} 个时间切片`)
}

// 渲染热力图
function renderHeatmap() {
  if (!map) return
  
  // 清除现有热力图
  if (heatmap) {
    heatmap.setMap(null)
  }
  
  const currentSlice = timeSlices.value[currentTimeIndex.value]
  if (!currentSlice || !currentSlice.data.length) return
  
  // 创建热力图
  map.plugin(['AMap.HeatMap'], function() {
    heatmap = new window.AMap.HeatMap(map, {
      radius: 25,
      opacity: [0, 0.8],
      gradient: {
        0.5: 'blue',
        0.65: 'rgb(117,211,248)',
        0.7: 'rgb(0,255,0)',
        0.9: 'yellow',
        1.0: 'red'
      }
    })
    
    heatmap.setDataSet({
      data: currentSlice.data,
      max: Math.max(...currentSlice.data.map(p => p.count))
    })
  })
}

// 时间段快速选择
function selectPeakHours(period) {
  switch (period) {
    case 'morning':
      analysisParams.value.startTime = '07:00'
      analysisParams.value.endTime = '09:00'
      break
    case 'evening':
      analysisParams.value.startTime = '17:00'
      analysisParams.value.endTime = '19:00'
      break
    case 'night':
      analysisParams.value.startTime = '22:00'
      analysisParams.value.endTime = '06:00'
      break
    case 'all':
      analysisParams.value.startTime = '00:00'
      analysisParams.value.endTime = '23:59'
      break
  }
}

// 时间轴控制
function prevTimeSlice() {
  if (currentTimeIndex.value > 0) {
    currentTimeIndex.value--
    updateTimeSlice()
  }
}

function nextTimeSlice() {
  if (currentTimeIndex.value < timeSlices.value.length - 1) {
    currentTimeIndex.value++
    updateTimeSlice()
  }
}

function updateTimeSlice() {
  renderHeatmap()
}

// 时间轴播放
async function playTimeAnimation() {
  if (playing.value || !timeSlices.value.length) return
  
  playing.value = true
  currentTimeIndex.value = 0
  
  const playInterval = setInterval(() => {
    updateTimeSlice()
    currentTimeIndex.value++
    
    if (currentTimeIndex.value >= timeSlices.value.length) {
      currentTimeIndex.value = 0 // 循环播放
    }
  }, 1000) // 每秒切换一个时间段
  
  // 10秒后停止播放
  setTimeout(() => {
    clearInterval(playInterval)
    playing.value = false
  }, 10000)
}

// 地图样式控制
function changeMapStyle() {
  if (map) {
    map.setMapStyle(`amap://styles/${mapParams.value.style}`)
  }
}

function toggleHeatmapLayer() {
  if (heatmap) {
    if (heatmapVisible.value) {
      heatmap.hide()
    } else {
      heatmap.show()
    }
    heatmapVisible.value = !heatmapVisible.value
  }
}

// 清除热力图
function clearHeatmap() {
  if (heatmap) {
    heatmap.setMap(null)
    heatmap = null
  }
  heatmapData.value = []
  timeSlices.value = []
  detailedData.value = []
  currentTimeIndex.value = 0
}

// 导出数据
function exportHeatmapData() {
  if (!heatmapData.value.length) return
  
  const exportData = {
    analysisParams: analysisParams.value,
    timeSlices: timeSlices.value.map(slice => ({
      ...slice,
      dataCount: slice.data.length
    })),
    overallStats: overallStats.value,
    topHotspots: topHotspots.value
  }
  
  const dataStr = JSON.stringify(exportData, null, 2)
  const dataBlob = new Blob([dataStr], {type: 'application/json'})
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `heatmap_analysis_${analysisParams.value.date}_${Date.now()}.json`
  link.click()
  
  URL.revokeObjectURL(url)
}

// 区域定位
function zoomToHotspot(hotspot) {
  if (map) {
    map.setZoomAndCenter(15, [hotspot.lng, hotspot.lat])
  }
}

function zoomToRegion(row) {
  console.log('定位到区域:', row)
}

// 工具函数
function formatTimestamp(timestamp) {
  return new Date(timestamp * 1000).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function formatTimeSlice(slice) {
  if (!slice) return ''
  return `${formatTimestamp(slice.startTime)} - ${formatTimestamp(slice.endTime)}`
}

function formatTime(timestamp) {
  return new Date(timestamp * 1000).toLocaleTimeString('zh-CN')
}

// 生命周期
onMounted(() => {
  setTimeout(() => {
    initMap()
  }, 500)
})

onUnmounted(() => {
  if (map) {
    map.destroy()
  }
})

// 监听时间索引变化
watch(currentTimeIndex, () => {
  updateTimeSlice()
})
</script> 

<style scoped>
.heatmap-analysis-container {
  padding: 20px;
}

.input-tech {
  width: 100%;
  padding: 8px 12px;
  background: rgba(30, 58, 138, 0.3);
  border: 1px solid rgba(59, 130, 246, 0.5);
  border-radius: 6px;
  color: white;
  font-size: 14px;
}

.input-tech:focus {
  outline: none;
  border-color: #06b6d4;
  box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
}

.btn-tech {
  padding: 8px 16px;
  background: linear-gradient(135deg, #0ea5e9, #06b6d4);
  border: none;
  border-radius: 6px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-tech:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4);
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

.btn-tech-small {
  padding: 4px 8px;
  font-size: 12px;
  background: rgba(30, 58, 138, 0.8);
  border: 1px solid rgba(59, 130, 246, 0.5);
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-tech-small:hover {
  background: rgba(37, 99, 235, 0.8);
}

.btn-tech-small:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.card-tech {
  background: linear-gradient(135deg, rgba(30, 58, 138, 0.8), rgba(29, 78, 216, 0.6));
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* 时间轴滑块样式 */
input[type="range"] {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: rgba(59, 130, 246, 0.3);
  outline: none;
}

input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #06b6d4;
  cursor: pointer;
}

input[type="range"]::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #06b6d4;
  cursor: pointer;
  border: none;
}
</style> 
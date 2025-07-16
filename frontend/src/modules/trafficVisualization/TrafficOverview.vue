<template>
  <div class="space-y-6 tech-bg">
    <div class="container mx-auto px-4">
      <!-- 查询控制面板 -->
      <TrafficQueryPanel
        v-model="queryParams"
        :loading="loading"
        @query="submitQuery"
        @clear="resetQuery"
      />
      
      <!-- 错误提示 -->
      <div v-if="showError" class="alert alert-danger mt-3">
        {{ errorMessage }}
      </div>
      
      <!-- 地图显示区域 -->
      <TrafficMapPanel
        :data="trafficData"
        :view-type="queryParams.viewType"
        :map-style="queryParams.mapStyle"
        :loading="loading"
        :vehicle-id="queryParams.vehicleId"
      />
      
      <!-- 数据统计面板 -->
      <TrafficStatsPanel
        v-if="trafficData.length > 0"
        :totalCount="trafficData.length"
        :timeSpan="timeSpan"
        :coverageArea="coverageArea"
        :activeVehicles="activeVehicles"
        :averageSpeed="averageSpeed"
        :totalDistance="totalDistance"
        :lastUpdate="lastUpdate"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TrafficQueryPanel from './TrafficQueryPanel.vue'
import TrafficMapPanel from './TrafficMapPanel.vue'
import TrafficStatsPanel from './TrafficStatsPanel.vue'
import { getTrafficVisualization } from '@/api/traffic'
import axios from 'axios'

const loading = ref(false)
const trafficData = ref([])
const currentMapView = ref('distribution')
const queryParams = ref({
  startTime: '2013-09-13T08:00',
  endTime: '2013-09-13T12:00',
  vehicleId: '',
  viewType: 'distribution',
  mapStyle: 'blue'
})
const mapViews = [
  { key: 'distribution', name: '分布视图' },
  { key: 'trajectory', name: '轨迹视图' },
  { key: 'heatmap', name: '热力图' }
]
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

// 错误提示状态
const errorMessage = ref('')
const showError = ref(false)

// 地图相关
let map = null

const submitQuery = async () => {
  // 清除之前的错误
  errorMessage.value = ''
  showError.value = false
  
  // 检查必填字段
  if (!queryParams.value.startTime || !queryParams.value.endTime) {
    errorMessage.value = '请选择查询时间范围'
    showError.value = true
    return
  }
  
  // 转换为UTC时间戳
  const startTimeUTC = convertToUTC(queryParams.value.startTime)
  const endTimeUTC = convertToUTC(queryParams.value.endTime)
  
  // 定义数据集的有效时间范围
  const minValidTime = 1378944000  // 2013-09-12 00:00:00 UTC
  const maxValidTime = 1379548799  // 2013-09-18 23:59:59 UTC
  
  // 验证时间范围
  if (startTimeUTC < minValidTime || startTimeUTC > maxValidTime || 
      endTimeUTC < minValidTime || endTimeUTC > maxValidTime) {
    // 时间超出范围，显示错误
    errorMessage.value = '查询时间超出数据集范围（2013年9月12日至9月18日）'
    showError.value = true
    return // 阻止查询继续
  }
  
  // 时间范围有效，继续查询
  loading.value = true
  try {
    // 使用更新后的API函数
    const response = await getTrafficVisualization(
      startTimeUTC,
      endTimeUTC,
      queryParams.value.viewType,
      queryParams.value.vehicleId || null,
      queryParams.value.mapStyle
    )
    
    if (response.data.success) {
      trafficData.value = response.data.data
    } else {
      errorMessage.value = response.data.message || '查询失败'
      showError.value = true
    }
  } catch (error) {
    errorMessage.value = `查询失败: ${error.message}`
    showError.value = true
    console.error('API请求错误:', error)
  } finally {
    loading.value = false
  }
}

const resetQuery = () => {
  queryParams.value.startTime = "2013-09-13T08:00"
  queryParams.value.endTime = "2013-09-13T12:00"
  queryParams.value.vehicleId = ""
  queryParams.value.viewType = 'distribution'
  queryParams.value.mapStyle = 'blue'
  
  errorMessage.value = ''
  showError.value = false
  trafficData.value = []
}

// 初始化地图
function initMap() {
  if (window.AMap) {
    map = new window.AMap.Map('traffic-map', {
      zoom: 13,
      center: [117.000923, 36.675807], // 济南市中心坐标
      mapStyle: 'amap://styles/blue'
    })
  } else {
    console.error('AMap is not loaded')
  }
}

// 更新地图
function updateMap() {
  if (!map || !trafficData.value) return
  
  // 清除之前的标记
  map.clearMap()
  
  // 根据视图类型更新地图
  if (queryParams.value.viewType === 'distribution') {
    renderDistributionView()
  } else if (queryParams.value.viewType === 'trajectory') {
    renderTrajectoryView()
  } else if (queryParams.value.viewType === 'heatmap') {
    renderHeatmapView()
  }
}

// 渲染分布视图
function renderDistributionView() {
  if (!map || !trafficData.value) return
  
  const markers = []
  
  trafficData.value.forEach(point => {
    const marker = new window.AMap.Marker({
      position: [point.lng, point.lat],
      title: `车辆ID: ${point.vehicle_id}`
    })
    markers.push(marker)
  })
  
  map.add(markers)
  
  // 调整视图以包含所有标记
  if (markers.length > 0) {
    map.setFitView(markers)
  }
}

// 渲染轨迹视图
function renderTrajectoryView() {
  if (!map || !trafficData.value) return
  
  trafficData.value.forEach(track => {
    if (!track.points || track.points.length < 2) return
    
    const path = track.points.map(point => [point.lng, point.lat])
    
    const polyline = new window.AMap.Polyline({
      path: path,
      strokeColor: '#3366FF',
      strokeWeight: 5,
      strokeOpacity: 0.8
    })
    
    map.add(polyline)
    
    // 添加起点和终点标记
    const startMarker = new window.AMap.Marker({
      position: path[0],
      title: '起点',
      icon: 'https://webapi.amap.com/theme/v1.3/markers/n/start.png'
    })
    
    const endMarker = new window.AMap.Marker({
      position: path[path.length - 1],
      title: '终点',
      icon: 'https://webapi.amap.com/theme/v1.3/markers/n/end.png'
    })
    
    map.add([startMarker, endMarker])
  })
  
  // 调整视图
  map.setFitView()
}

// 渲染热力图
function renderHeatmapView() {
  if (!map || !trafficData.value || !window.AMap.HeatMap) return
  
  const heatmap = new window.AMap.HeatMap(map, {
    radius: 25,
    opacity: [0, 0.8]
  })
  
  const points = trafficData.value.map(point => {
    return {
      lng: point.lng,
      lat: point.lat,
      count: point.count || 1
    }
  })
  
  heatmap.setDataSet({
    data: points,
    max: 100
  })
}

// 地图控制
function zoomIn() {
  if (map) map.zoomIn()
}

function zoomOut() {
  if (map) map.zoomOut()
}

function resetMap() {
  if (map) {
    map.setZoom(13)
    map.setCenter([117.000923, 36.675807])
  }
}

// 前端时间转换函数
function convertToUTC(dateString) {
  if (!dateString) return 0
  try {
    const date = new Date(dateString)
    return Math.floor(date.getTime() / 1000) // 转换为秒级时间戳
  } catch (error) {
    console.error('时间转换错误:', error)
    return 0
  }
}

// 设置日期选择器的最小和最大值
const minDate = "2013-09-12T00:00"
const maxDate = "2013-09-18T23:59"

onMounted(() => {
  // 设置默认值为数据集范围内的时间（优化后的4小时范围）
  queryParams.value.startTime = "2013-09-13T08:00"
  queryParams.value.endTime = "2013-09-13T12:00"
  
  // 初始化地图
  initMap()
  
  // 加载高德地图API
  if (!window.AMap) {
    const script = document.createElement('script')
    script.src = 'https://webapi.amap.com/maps?v=2.0&key=ac9b745946df9aee02cf0515319407df&plugin=AMap.HeatMap'
    script.async = true
    script.onload = () => {
      initMap()
    }
    document.head.appendChild(script)
  }
})
</script>

<style scoped>
.tech-bg {
  background: linear-gradient(135deg, #0a2342 0%, #183b6b 100%);
  min-height: 100vh;
  padding: 32px 0;
}
.container {
  max-width: 1280px;
}
.card-tech {
  background: rgba(10, 35, 66, 0.95);
  border: 1.5px solid #183b6b;
  border-radius: 18px;
  box-shadow: 0 4px 32px 0 rgba(0, 207, 255, 0.08);
}
.input-tech {
  background: #122b45;
  color: #fff;
  border: 1px solid #00cfff;
  border-radius: 8px;
  padding: 8px 12px;
  outline: none;
  transition: border 0.2s, box-shadow 0.2s;
}
.input-tech:focus {
  border: 1.5px solid #00cfff;
  box-shadow: 0 0 0 2px #00cfff33;
}
.btn-tech {
  background: linear-gradient(90deg, #00cfff 0%, #1e90ff 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  padding: 8px 24px;
  box-shadow: 0 2px 8px 0 #00cfff33;
  transition: background 0.2s, box-shadow 0.2s;
}
.btn-tech:hover {
  background: linear-gradient(90deg, #1e90ff 0%, #00cfff 100%);
  box-shadow: 0 4px 16px 0 #00cfff44;
}
.btn-tech-secondary {
  background: #183b6b;
  color: #fff;
  border: 1px solid #00cfff;
  border-radius: 8px;
  font-weight: 600;
  padding: 8px 24px;
  transition: background 0.2s, box-shadow 0.2s;
}
.btn-tech-secondary:hover {
  background: #122b45;
  color: #00cfff;
}

.alert {
  margin-bottom: 20px;
  padding: 12px 16px;
  border-radius: 4px;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style> 
<template>
  <div class="track-query-container">
    <!-- 查询控制面板 -->
    <div class="card-tech p-6 mb-6">
      <h2 class="text-xl font-semibold text-white mb-4 flex items-center">
        <Route class="h-5 w-5 mr-2 text-cyan-400" />
        车辆轨迹查询
      </h2>
      
      <!-- 查询表单 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div class="space-y-2">
          <label class="text-sm text-blue-200">起始时间</label>
          <input 
            v-model="queryParams.startTime"
            type="datetime-local" 
            class="input-tech"
            :min="minDate"
            :max="maxDate"
          />
        </div>
        <div class="space-y-2">
          <label class="text-sm text-blue-200">结束时间</label>
          <input 
            v-model="queryParams.endTime"
            type="datetime-local" 
            class="input-tech"
            :min="minDate"
            :max="maxDate"
          />
        </div>
        <div class="space-y-2">
          <label class="text-sm text-blue-200">车辆ID（精确查询）</label>
          <div class="flex space-x-2">
            <input 
              v-model="queryParams.vehicleId"
              type="text" 
              placeholder="输入具体车辆ID，如: 粤A12345"
              class="input-tech placeholder:text-blue-300 flex-1"
            />
            <button 
              @click="loadSampleVehicles"
              :disabled="loadingSamples"
              class="btn-tech-small whitespace-nowrap"
            >
              {{ loadingSamples ? '加载中...' : '获取示例' }}
            </button>
          </div>
          <!-- 示例车辆下拉列表 -->
          <div v-if="sampleVehicles.length > 0" class="mt-2">
            <select 
              @change="selectSampleVehicle($event.target.value)"
              class="input-tech text-sm"
            >
              <option value="">选择示例车辆...</option>
              <option 
                v-for="vehicle in sampleVehicles" 
                :key="vehicle.vehicle_id"
                :value="vehicle.vehicle_id"
              >
                {{ vehicle.description }}
              </option>
            </select>
          </div>
        </div>
      </div>
      
      <!-- 查询选项 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <div class="space-y-2">
          <label class="text-sm text-blue-200">查询模式</label>
          <select v-model="queryParams.mode" class="input-tech">
            <option value="single">单车辆轨迹</option>
            <option value="multiple">多车辆对比</option>
            <option value="area">区域内所有车辆</option>
          </select>
        </div>
        <div class="space-y-2">
          <label class="text-sm text-blue-200">显示详细度</label>
          <select v-model="queryParams.detail" class="input-tech">
            <option value="full">完整轨迹</option>
            <option value="key">关键节点</option>
            <option value="simplified">简化路径</option>
          </select>
        </div>
        <div class="space-y-2">
          <label class="text-sm text-blue-200">速度阈值</label>
          <input 
            v-model="queryParams.speedFilter"
            type="number" 
            placeholder="最低速度(km/h)"
            class="input-tech placeholder:text-blue-300"
          />
        </div>
        <div class="space-y-2">
          <label class="text-sm text-blue-200">显示选项</label>
          <div class="flex space-x-2">
            <label class="flex items-center text-xs text-blue-200">
              <input type="checkbox" v-model="displayOptions.showSpeed" class="mr-1">
              速度
            </label>
            <label class="flex items-center text-xs text-blue-200">
              <input type="checkbox" v-model="displayOptions.showTime" class="mr-1">
              时间
            </label>
            <label class="flex items-center text-xs text-blue-200">
              <input type="checkbox" v-model="displayOptions.showStops" class="mr-1">
              停留点
            </label>
          </div>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="flex space-x-4">
        <button 
          @click="queryTracks"
          :disabled="loading"
          class="btn-tech flex items-center text-white"
        >
          <Search class="h-4 w-4 mr-2" />
          {{ loading ? '查询中...' : '查询轨迹' }}
        </button>
        <button 
          @click="clearMap"
          class="btn-tech-secondary flex items-center text-white"
        >
          <X class="h-4 w-4 mr-2" />
          清除地图
        </button>
        <button 
          @click="playAnimation"
          :disabled="!trackData.length"
          class="btn-tech flex items-center text-white"
        >
          <Play class="h-4 w-4 mr-2" />
          动画播放
        </button>
        <button 
          @click="exportTrack"
          :disabled="!trackData.length"
          class="btn-tech-secondary flex items-center text-white"
        >
          <Download class="h-4 w-4 mr-2" />
          导出数据
        </button>
      </div>
    </div>

    <!-- 轨迹分析结果 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- 地图显示 -->
      <div class="lg:col-span-2 card-tech p-6">
        <h3 class="text-lg font-semibold text-white mb-4">轨迹地图</h3>
        <div 
          :id="mapContainerId" 
          class="w-full h-96 bg-gray-800 rounded-lg border border-blue-800"
        ></div>
        
        <!-- 地图控制 -->
        <div class="flex justify-between items-center mt-4">
          <div class="flex space-x-2">
            <button @click="zoomIn" class="btn-tech-small">放大</button>
            <button @click="zoomOut" class="btn-tech-small">缩小</button>
            <button @click="resetView" class="btn-tech-small">重置视图</button>
          </div>
          <div class="text-sm text-blue-200">
            显示 {{ trackData.length }} 条轨迹，共 {{ totalPoints }} 个点
          </div>
        </div>
      </div>
      
      <!-- 轨迹统计 -->
      <div class="card-tech p-6">
        <h3 class="text-lg font-semibold text-white mb-4">轨迹分析</h3>
        <div class="space-y-4">
          <div v-for="stat in trackStats" :key="stat.label" class="flex justify-between">
            <span class="text-blue-200">{{ stat.label }}</span>
            <span class="text-white font-semibold">{{ stat.value }}</span>
          </div>
        </div>
        
        <!-- 车辆列表 -->
        <div class="mt-6" v-if="trackData.length > 0">
          <h4 class="text-sm font-semibold text-blue-200 mb-2">车辆列表</h4>
          <div class="max-h-48 overflow-y-auto space-y-2">
            <div 
              v-for="track in trackData" 
              :key="track.vehicle_id"
              @click="highlightTrack(track.vehicle_id)"
              class="p-2 bg-gray-700 rounded cursor-pointer hover:bg-gray-600 transition-colors"
            >
              <div class="flex justify-between items-center">
                <span class="text-white text-sm">{{ track.vehicle_id }}</span>
                <span class="text-xs text-blue-300">{{ formatDistance(track.distance) }}</span>
              </div>
              <div class="text-xs text-gray-400">
                {{ formatDuration(track.duration) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 轨迹详情表格 -->
    <div class="card-tech p-6" v-if="selectedTrackDetails">
      <h3 class="text-lg font-semibold text-white mb-4">轨迹详情 - {{ selectedTrackDetails.vehicle_id }}</h3>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-600">
              <th class="text-left py-2 text-blue-200">时间</th>
              <th class="text-left py-2 text-blue-200">经度</th>
              <th class="text-left py-2 text-blue-200">纬度</th>
              <th class="text-left py-2 text-blue-200">速度</th>
              <th class="text-left py-2 text-blue-200">方向</th>
              <th class="text-left py-2 text-blue-200">状态</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(point, index) in selectedTrackDetails.points" 
              :key="index"
              class="border-b border-gray-700 hover:bg-gray-700"
            >
              <td class="py-2 text-white">{{ formatTime(point.timestamp) }}</td>
              <td class="py-2 text-white">{{ point.lng.toFixed(6) }}</td>
              <td class="py-2 text-white">{{ point.lat.toFixed(6) }}</td>
              <td class="py-2 text-white">{{ point.speed || 'N/A' }}</td>
              <td class="py-2 text-white">{{ point.direction || 'N/A' }}</td>
              <td class="py-2 text-white">{{ point.status || 'N/A' }}</td>
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
          <span>正在查询轨迹数据...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Route, Search, X, Play, Download } from 'lucide-vue-next'
import { getTrackData, getSampleVehicles } from '@/api/traffic'

// 响应式数据
const loading = ref(false)
const loadingSamples = ref(false)
const trackData = ref([])
const selectedTrackDetails = ref(null)
const sampleVehicles = ref([])

const queryParams = ref({
  startTime: '2013-09-13T08:00',
  endTime: '2013-09-13T12:00',
  vehicleId: '',
  mode: 'single',
  detail: 'full',
  speedFilter: ''
})

const displayOptions = ref({
  showSpeed: true,
  showTime: true,
  showStops: false
})

// 地图相关
const mapContainerId = `track-map-${Date.now()}`
let map = null
let polylines = []
let markers = []

// 时间限制
const minDate = "2013-09-12T00:00"
const maxDate = "2013-09-18T23:59"

// 计算属性
const totalPoints = computed(() => {
  return trackData.value.reduce((total, track) => {
    return total + (track.points ? track.points.length : 0)
  }, 0)
})

const trackStats = computed(() => {
  if (trackData.value.length === 0) return []
  
  // 计算总距离和总时长
  const totalDistance = trackData.value.reduce((sum, track) => {
    // 使用后端计算的距离（单位：公里）
    const distance = track.distance || 0
    return sum + distance
  }, 0)
  
  const totalDuration = trackData.value.reduce((sum, track) => {
    // 使用后端计算的时长（单位：秒）
    const duration = track.duration || 0
    return sum + duration
  }, 0)
  
  // 计算平均速度 (km/h)
  const avgSpeed = totalDuration > 0 ? (totalDistance / (totalDuration / 3600)) : 0
  
  return [
    { label: '轨迹数量', value: trackData.value.length },
    { label: '总距离', value: formatDistance(totalDistance) },
    { label: '总时长', value: formatDuration(totalDuration) },
    { label: '平均速度', value: isNaN(avgSpeed) ? '0 km/h' : `${avgSpeed.toFixed(1)} km/h` },
    { label: '数据点数', value: totalPoints.value }
  ]
})

// 地图初始化
async function initMap() {
  if (!window.AMap) {
    await loadAMapAPI()
  }
  
  map = new window.AMap.Map(mapContainerId, {
    center: [117.120, 36.651],
    zoom: 10,
    mapStyle: 'amap://styles/dark'
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

// 查询轨迹
async function queryTracks() {
  if (!queryParams.value.vehicleId.trim()) {
    alert('请输入车辆ID进行查询')
    return
  }
  
  loading.value = true
  
  try {
    // 将ISO时间字符串转换为UTC时间戳
    const startTimeStamp = new Date(queryParams.value.startTime).getTime() / 1000
    const endTimeStamp = new Date(queryParams.value.endTime).getTime() / 1000
    
    const params = {
      start_time: startTimeStamp,
      end_time: endTimeStamp,
      vehicle_id: queryParams.value.vehicleId.trim(),
      view_type: 'trajectory'
    }
    
    console.log('查询参数:', params)
    console.log('转换前时间:', queryParams.value.startTime, queryParams.value.endTime)
    console.log('转换后时间戳:', startTimeStamp, endTimeStamp)
    
    const response = await getTrackData(params)
    
    if (response.data.success && response.data.data) {
      // 处理轨迹数据
      processTrackData(response.data.data)
      // 在地图上显示轨迹
      displayTracksOnMap()
    } else {
      alert(response.data.message || '查询失败')
    }
  } catch (error) {
    console.error('查询轨迹失败:', error)
    alert('查询失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

// 处理轨迹数据
function processTrackData(data) {
  if (!data || data.length === 0) {
    trackData.value = []
    return
  }
  
  console.log('原始轨迹数据:', data)
  
  // 检查数据结构 - 后端返回的是VehicleTrack对象数组
  if (data[0] && data[0].vehicle_id && data[0].points) {
    // 如果是VehicleTrack对象数组，直接使用
    trackData.value = data.map(track => ({
      vehicle_id: track.vehicle_id,
      points: track.points || [],
      distance: track.distance || 0,
      duration: track.end_time && track.start_time ? track.end_time - track.start_time : 0,
      start_time: track.start_time,
      end_time: track.end_time
    }))
  } else {
    // 如果是原始数据点数组，按车辆ID分组处理
    const vehicleGroups = {}
    data.forEach(point => {
      const vehicleId = point.vehicle_id
      if (!vehicleGroups[vehicleId]) {
        vehicleGroups[vehicleId] = []
      }
      vehicleGroups[vehicleId].push({
        lng: point.longitude,
        lat: point.latitude,
        timestamp: point.UTC,
        speed: point.speed || 0
      })
    })
    
    // 计算每个车辆的轨迹统计
    trackData.value = Object.keys(vehicleGroups).map(vehicleId => {
      const points = vehicleGroups[vehicleId].sort((a, b) => a.timestamp - b.timestamp)
      
      // 计算距离和时长
      let distance = 0
      for (let i = 1; i < points.length; i++) {
        distance += calculateDistance(points[i-1], points[i])
      }
      
      const duration = points.length > 0 ? points[points.length - 1].timestamp - points[0].timestamp : 0
      
      return {
        vehicle_id: vehicleId,
        points: points,
        distance: distance,
        duration: duration,
        start_time: points[0]?.timestamp,
        end_time: points[points.length - 1]?.timestamp
      }
    })
  }
  
  console.log('处理后的轨迹数据:', trackData.value)
  
  // 确保数据格式正确
  trackData.value.forEach(track => {
    if (track.points && track.points.length > 0) {
      console.log(`车辆 ${track.vehicle_id}: ${track.points.length} 个点, 距离: ${track.distance}km, 时长: ${track.duration}s`)
    }
  })
}

// 在地图上显示轨迹
function displayTracksOnMap() {
  if (!map || trackData.value.length === 0) return
  
  // 清除现有轨迹
  clearMap()
  
  const colors = ['#ff4444', '#44ff44', '#4444ff', '#ffff44', '#ff44ff', '#44ffff']
  
  trackData.value.forEach((track, index) => {
    if (!track.points || track.points.length < 2) {
      console.log(`车辆 ${track.vehicle_id} 轨迹点不足，跳过显示`)
      return
    }
    
    const color = colors[index % colors.length]
    
    // 构建轨迹路径，确保坐标格式正确
    const path = track.points.map(point => {
      // 适配不同的坐标格式
      const lng = point.lng || point.longitude
      const lat = point.lat || point.latitude
      
      if (lng === undefined || lat === undefined) {
        console.error('轨迹点缺少坐标信息:', point)
        return null
      }
      
      return [lng, lat]
    }).filter(p => p !== null)  // 过滤掉无效点
    
    if (path.length < 2) {
      console.log(`车辆 ${track.vehicle_id} 有效轨迹点不足，跳过显示`)
      return
    }
    
    console.log(`绘制车辆 ${track.vehicle_id} 轨迹，共 ${path.length} 个点`)
    console.log('轨迹路径:', path.slice(0, 3), '...', path.slice(-3))  // 显示前3个和后3个点
    
    // 创建轨迹线
    const polyline = new window.AMap.Polyline({
      path: path,
      strokeColor: color,
      strokeWeight: 4,
      strokeOpacity: 0.8,
      showDir: true,
      lineJoin: 'round',
      lineCap: 'round'
    })
    
    map.add(polyline)
    polylines.push(polyline)
    
    // 添加起点标记（绿色）
    const startMarker = new window.AMap.Marker({
      position: path[0],
      icon: new window.AMap.Icon({
        size: new window.AMap.Size(16, 16),
        image: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iOCIgY3k9IjgiIHI9IjYiIGZpbGw9IiMwMGZmMDAiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIyIi8+Cjwvc3ZnPgo='
      }),
      title: `起点 - ${track.vehicle_id}`,
      zIndex: 100
    })
    
    map.add(startMarker)
    markers.push(startMarker)
    
    // 添加终点标记（红色）
    const endMarker = new window.AMap.Marker({
      position: path[path.length - 1],
      icon: new window.AMap.Icon({
        size: new window.AMap.Size(16, 16),
        image: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iOCIgY3k9IjgiIHI9IjYiIGZpbGw9IiNmZjAwMDAiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIyIi8+Cjwvc3ZnPgo='
      }),
      title: `终点 - ${track.vehicle_id}`,
      zIndex: 100
    })
    
    map.add(endMarker)
    markers.push(endMarker)
  })
  
  // 自动调整地图视野以显示所有轨迹
  if (polylines.length > 0) {
    try {
      const bounds = new window.AMap.Bounds()
      
      trackData.value.forEach(track => {
        if (track.points && track.points.length > 0) {
          track.points.forEach(point => {
            const lng = point.lng || point.longitude
            const lat = point.lat || point.latitude
            if (lng !== undefined && lat !== undefined) {
              bounds.extend([lng, lat])
            }
          })
        }
      })
      
      if (!bounds.isEmpty()) {
        map.setBounds(bounds, false, [50, 50, 50, 50])  // 添加边距
      }
    } catch (error) {
      console.error('设置地图边界失败:', error)
    }
  }
}

// 清除地图
function clearMap() {
  if (!map) return
  
  polylines.forEach(polyline => map.remove(polyline))
  markers.forEach(marker => map.remove(marker))
  polylines = []
  markers = []
}

// 地图控制功能
function zoomIn() {
  if (map) map.zoomIn()
}

function zoomOut() {
  if (map) map.zoomOut()
}

function resetView() {
  if (map && polylines.length > 0) {
    map.setFitView([...polylines, ...markers])
  }
}

// 高亮轨迹
function highlightTrack(vehicleId) {
  selectedTrackDetails.value = trackData.value.find(track => track.vehicle_id === vehicleId)
}

// 动画播放
function playAnimation() {
  alert('动画播放功能开发中...')
}

// 导出轨迹
function exportTrack() {
  if (trackData.value.length === 0) return
  
  const dataStr = JSON.stringify(trackData.value, null, 2)
  const dataBlob = new Blob([dataStr], {type: 'application/json'})
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `track_data_${queryParams.value.vehicleId}_${Date.now()}.json`
  link.click()
  
  URL.revokeObjectURL(url)
}

// 加载示例车辆
async function loadSampleVehicles() {
  loadingSamples.value = true
  
  try {
    // 将当前时间范围转换为时间戳
    const startTimeStamp = new Date(queryParams.value.startTime).getTime() / 1000
    const endTimeStamp = new Date(queryParams.value.endTime).getTime() / 1000
    
    console.log('获取示例车辆，时间范围:', startTimeStamp, endTimeStamp)
    
    const response = await getSampleVehicles(startTimeStamp, endTimeStamp, 20)
    
    if (response.data.success && response.data.vehicles) {
      sampleVehicles.value = response.data.vehicles
      console.log('获取到示例车辆:', sampleVehicles.value)
    } else {
      alert(response.data.message || '获取示例车辆失败')
      sampleVehicles.value = []
    }
  } catch (error) {
    console.error('获取示例车辆失败:', error)
    alert('获取示例车辆失败，请检查网络连接')
    sampleVehicles.value = []
  } finally {
    loadingSamples.value = false
  }
}

// 选择示例车辆
function selectSampleVehicle(vehicleId) {
  if (vehicleId) {
    queryParams.value.vehicleId = vehicleId
    console.log('选择了车辆:', vehicleId)
  }
}

// 工具函数
function calculateDistance(point1, point2) {
  const R = 6371 // 地球半径 km
  const dLat = (point2.lat - point1.lat) * Math.PI / 180
  const dLon = (point2.lng - point1.lng) * Math.PI / 180
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) + 
            Math.cos(point1.lat * Math.PI / 180) * Math.cos(point2.lat * Math.PI / 180) * 
            Math.sin(dLon/2) * Math.sin(dLon/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  return R * c
}

function formatDistance(distance) {
  if (distance < 1) {
    return `${(distance * 1000).toFixed(0)} m`
  }
  return `${distance.toFixed(2)} km`
}

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  } else {
    return `${secs}s`
  }
}

function formatTime(timestamp) {
  return new Date(timestamp * 1000).toLocaleString('zh-CN')
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
</script> 

<style scoped>
.track-query-container {
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

.card-tech {
  background: linear-gradient(135deg, rgba(30, 58, 138, 0.8), rgba(29, 78, 216, 0.6));
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
</style> 
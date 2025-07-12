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
              placeholder="输入具体车辆ID"
              class="input-tech placeholder:text-blue-300 flex-1"
            />
            <button 
              @click="loadSampleVehicles"
              :disabled="loadingVehicles"
              class="btn-tech-small whitespace-nowrap"
            >
              {{ loadingVehicles ? '加载中...' : '获取示例' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 示例车辆列表 -->
      <div v-if="sampleVehicles.length > 0" class="mb-4">
        <label class="text-sm text-blue-200 mb-2 block">示例车辆（点击选择）</label>
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
          <button 
            v-for="vehicle in sampleVehicles" 
            :key="vehicle.id"
            @click="selectVehicle(vehicle)"
            :class="queryParams.vehicleId === vehicle.id ? 'bg-blue-500 text-white' : 'bg-gray-700 text-blue-200 hover:bg-gray-600'"
            class="p-2 rounded text-sm transition-colors"
          >
            {{ vehicle.id }}
            <div class="text-xs opacity-75">{{ vehicle.points }}点</div>
          </button>
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
        <div id="track-map" class="w-full h-96 bg-gray-800 rounded-lg"></div>
        
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
                {{ formatDuration(track.end_time - track.start_time) }}
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Route, Search, X, Play, Download } from 'lucide-vue-next'
import { getTrafficVisualization, getSampleVehicles } from '@/api/traffic'

// 响应式数据
const loading = ref(false)
const loadingVehicles = ref(false)
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
  
  const totalDistance = trackData.value.reduce((sum, track) => sum + (track.distance || 0), 0)
  const avgSpeed = totalDistance > 0 ? (totalDistance / trackData.value.length) : 0
  
  return [
    { label: '轨迹数量', value: trackData.value.length },
    { label: '总距离', value: formatDistance(totalDistance) },
    { label: '平均速度', value: `${avgSpeed.toFixed(1)} km/h` },
    { label: '数据点数', value: totalPoints.value },
    { label: '时间跨度', value: formatDuration(getTimeSpan()) }
  ]
})

// 方法
const initMap = () => {
  if (window.AMap) {
    map = new window.AMap.Map('track-map', {
      zoom: 13,
      center: [117.000923, 36.675807],
      mapStyle: 'amap://styles/blue'
    })
  }
}

// 获取示例车辆
const loadSampleVehicles = async () => {
  loadingVehicles.value = true
  
  try {
    const startTime = Math.floor(new Date(queryParams.value.startTime).getTime() / 1000)
    const endTime = Math.floor(new Date(queryParams.value.endTime).getTime() / 1000)
    
    const response = await getSampleVehicles(startTime, endTime, 20)
    
    if (response.data.success) {
      sampleVehicles.value = response.data.vehicles.map(v => ({
        id: v.vehicle_id,
        points: v.point_count,
        firstTime: v.first_time,
        lastTime: v.last_time
      }))
      console.log('🚗 获取示例车辆成功:', sampleVehicles.value)
    } else {
      console.warn('获取示例车辆失败:', response.data.message)
    }
  } catch (error) {
    console.error('获取示例车辆失败:', error)
  } finally {
    loadingVehicles.value = false
  }
}

// 选择车辆
const selectVehicle = (vehicle) => {
  queryParams.value.vehicleId = vehicle.id
  console.log('🚗 选择车辆:', vehicle.id)
}

// 处理轨迹数据
const processTrajectoryData = (rawData) => {
  if (!rawData || rawData.length === 0) {
    return []
  }
  
  // 按车辆ID分组
  const vehicleGroups = {}
  rawData.forEach(point => {
    const vehicleId = point.vehicle_id || point.vehicleId
    if (!vehicleGroups[vehicleId]) {
      vehicleGroups[vehicleId] = []
    }
    vehicleGroups[vehicleId].push(point)
  })
  
  // 转换为轨迹格式
  const tracks = []
  for (const [vehicleId, points] of Object.entries(vehicleGroups)) {
    if (points.length < 2) continue
    
    // 按时间排序
    points.sort((a, b) => (a.timestamp || a.UTC) - (b.timestamp || b.UTC))
    
    // 计算轨迹距离
    let totalDistance = 0
    for (let i = 1; i < points.length; i++) {
      const prev = points[i - 1]
      const curr = points[i]
      const distance = calculateDistance(prev.lat, prev.lng, curr.lat, curr.lng)
      totalDistance += distance
    }
    
    const track = {
      vehicle_id: vehicleId,
      points: points.map(p => ({
        lng: p.lng || p.lon,
        lat: p.lat,
        timestamp: p.timestamp || p.UTC,
        speed: p.speed || 0
      })),
      start_time: points[0].timestamp || points[0].UTC,
      end_time: points[points.length - 1].timestamp || points[points.length - 1].UTC,
      distance: totalDistance
    }
    
    tracks.push(track)
  }
  
  return tracks
}

// 计算两点间距离（公里）
const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371 // 地球半径（公里）
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLng/2) * Math.sin(dLng/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  return R * c
}

const queryTracks = async () => {
  if (!queryParams.value.startTime || !queryParams.value.endTime) {
    alert('请选择查询时间范围')
    return
  }
  
  if (!queryParams.value.vehicleId) {
    alert('请输入车辆ID或选择示例车辆')
    return
  }
    
  loading.value = true
  
  try {
    const startTime = Math.floor(new Date(queryParams.value.startTime).getTime() / 1000)
    const endTime = Math.floor(new Date(queryParams.value.endTime).getTime() / 1000)
    
    console.log('🚗 查询轨迹参数:', {
      startTime,
      endTime,
      vehicleId: queryParams.value.vehicleId,
      startDate: new Date(startTime * 1000).toISOString(),
      endDate: new Date(endTime * 1000).toISOString()
    })
    
    // 使用可视化API获取特定车辆的轨迹数据
    const response = await getTrafficVisualization(
      startTime,
      endTime,
      'trajectory',  // 轨迹视图
      queryParams.value.vehicleId,
      'normal'
    )
    
    if (response.data.success) {
      const rawData = response.data.data || []
      console.log('🚗 轨迹原始数据:', rawData)
      
      // 将原始数据转换为轨迹格式
      const processedTracks = processTrajectoryData(rawData)
      trackData.value = processedTracks
      
      console.log('🚗 处理后的轨迹数据:', processedTracks)
      renderTracks()
    } else {
      alert('查询失败：' + response.data.message)
    }
  } catch (error) {
    console.error('查询轨迹失败:', error)
    alert('查询失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

const renderTracks = () => {
  clearMap()
  
  if (!map || trackData.value.length === 0) return
  
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#00CFFF', '#FF6B6B']
  
  trackData.value.forEach((track, index) => {
    if (!track.points || track.points.length < 2) return
    
    const color = colors[index % colors.length]
    const path = track.points.map(point => [point.lng, point.lat])
    
    // 绘制轨迹线
    const polyline = new window.AMap.Polyline({
      path: path,
      strokeColor: color,
      strokeWeight: 3,
      strokeOpacity: 0.8
    })
    
    map.add(polyline)
    polylines.push(polyline)
    
    // 添加起点和终点标记
    if (track.points.length > 0) {
      const startPoint = track.points[0]
      const endPoint = track.points[track.points.length - 1]
      
      // 起点
      const startMarker = new window.AMap.Marker({
        position: [startPoint.lng, startPoint.lat],
        title: `车辆${track.vehicle_id} - 起点\n时间: ${formatTime(startPoint.timestamp)}`,
        icon: new window.AMap.Icon({
          size: new window.AMap.Size(24, 24),
          image: `data:image/svg+xml;base64,${btoa(`
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" fill="#00ff00" stroke="#fff" stroke-width="2"/>
              <text x="12" y="16" text-anchor="middle" fill="#fff" font-size="12" font-weight="bold">S</text>
            </svg>
          `)}`,
          imageSize: new window.AMap.Size(24, 24)
        })
      })
      
      // 终点
      const endMarker = new window.AMap.Marker({
        position: [endPoint.lng, endPoint.lat],
        title: `车辆${track.vehicle_id} - 终点\n时间: ${formatTime(endPoint.timestamp)}`,
        icon: new window.AMap.Icon({
          size: new window.AMap.Size(24, 24),
          image: `data:image/svg+xml;base64,${btoa(`
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" fill="#ff4444" stroke="#fff" stroke-width="2"/>
              <text x="12" y="16" text-anchor="middle" fill="#fff" font-size="12" font-weight="bold">E</text>
            </svg>
          `)}`,
          imageSize: new window.AMap.Size(24, 24)
        })
      })
      
      map.add([startMarker, endMarker])
      markers.push(startMarker, endMarker)
      
      // 添加轨迹上的一些关键点标记
      if (displayOptions.value.showSpeed && track.points.length > 4) {
        const keyPoints = track.points.filter((_, index) => index % Math.floor(track.points.length / 4) === 0)
        keyPoints.forEach(point => {
          const speedColor = point.speed > 30 ? '#ff6b6b' : point.speed > 15 ? '#ffa500' : '#4ecdc4'
          const speedMarker = new window.AMap.Marker({
            position: [point.lng, point.lat],
            title: `速度: ${point.speed.toFixed(1)} km/h\n时间: ${formatTime(point.timestamp)}`,
            icon: new window.AMap.Icon({
              size: new window.AMap.Size(12, 12),
              image: `data:image/svg+xml;base64,${btoa(`
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="6" cy="6" r="5" fill="${speedColor}" stroke="#fff" stroke-width="1"/>
                </svg>
              `)}`,
              imageSize: new window.AMap.Size(12, 12)
            })
          })
          map.add(speedMarker)
          markers.push(speedMarker)
        })
      }
    }
  })
  
  // 自适应视图
  if (polylines.length > 0) {
    map.setFitView(polylines)
  }
}

const clearMap = () => {
  polylines.forEach(line => map.remove(line))
  polylines = []
  markers.forEach(marker => map.remove(marker))
  markers = []
  selectedTrackDetails.value = null
}

const highlightTrack = (vehicleId) => {
  const track = trackData.value.find(t => t.vehicle_id === vehicleId)
  if (track) {
    selectedTrackDetails.value = track
    
    // 高亮显示选中的轨迹
    // 这里可以添加高亮逻辑
  }
}

const playAnimation = () => {
  if (trackData.value.length === 0) {
    alert('没有轨迹数据可播放')
    return
  }
  
  // 选择第一条轨迹进行动画播放
  const track = trackData.value[0]
  if (!track.points || track.points.length < 2) {
    alert('轨迹数据不足，无法播放动画')
    return
  }
  
  // 清除现有的动画标记
  const existingAnimationMarkers = markers.filter(m => m.getTitle && m.getTitle().includes('动画'))
  existingAnimationMarkers.forEach(marker => map.remove(marker))
  
  // 创建动画标记
  const animationMarker = new window.AMap.Marker({
    position: [track.points[0].lng, track.points[0].lat],
    title: `车辆${track.vehicle_id} - 动画播放`,
    icon: new window.AMap.Icon({
      size: new window.AMap.Size(16, 16),
      image: `data:image/svg+xml;base64,${btoa(`
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="8" cy="8" r="6" fill="#00cfff" stroke="#fff" stroke-width="2"/>
          <circle cx="8" cy="8" r="3" fill="#fff"/>
        </svg>
      `)}`,
      imageSize: new window.AMap.Size(16, 16)
    })
  })
  
  map.add(animationMarker)
  markers.push(animationMarker)
  
  // 播放动画
  let currentIndex = 0
  const animationInterval = setInterval(() => {
    if (currentIndex >= track.points.length) {
      clearInterval(animationInterval)
      return
    }
    
    const point = track.points[currentIndex]
    animationMarker.setPosition([point.lng, point.lat])
    animationMarker.setTitle(`车辆${track.vehicle_id} - 动画播放\n时间: ${formatTime(point.timestamp)}\n速度: ${point.speed.toFixed(1)} km/h`)
    
    // 地图跟随
    map.setCenter([point.lng, point.lat])
    
    currentIndex++
  }, 500) // 每500ms移动一次
  
  alert('轨迹动画开始播放，地图将跟随车辆移动')
}

const exportTrack = () => {
  // 导出轨迹数据
  const dataStr = JSON.stringify(trackData.value, null, 2)
  const dataBlob = new Blob([dataStr], {type: 'application/json'})
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `tracks_${new Date().getTime()}.json`
  link.click()
}

// 工具函数
const formatDistance = (distance) => {
  if (distance == null) return 'N/A'
  return distance > 1 ? `${distance.toFixed(2)} km` : `${(distance * 1000).toFixed(0)} m`
}

const formatDuration = (seconds) => {
  if (!seconds) return 'N/A'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`
}

const formatTime = (timestamp) => {
  return new Date(timestamp * 1000).toLocaleString()
}

const getTimeSpan = () => {
  if (trackData.value.length === 0) return 0
  const times = trackData.value.flatMap(track => track.points?.map(p => p.timestamp) || [])
  return Math.max(...times) - Math.min(...times)
}

const zoomIn = () => map?.zoomIn()
const zoomOut = () => map?.zoomOut()
const resetView = () => {
  if (polylines.length > 0) {
    map.setFitView(polylines)
  } else {
    map.setZoom(13)
    map.setCenter([117.000923, 36.675807])
  }
}

onMounted(() => {
  initMap()
  // 自动加载示例车辆
  setTimeout(() => {
    loadSampleVehicles()
  }, 1000)
})
</script>

<style scoped>
.track-query-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a2342 0%, #183b6b 100%);
  padding: 32px;
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
  width: 100%;
}

.input-tech:focus {
  border: 1.5px solid #00cfff;
  box-shadow: 0 0 0 2px #00cfff33;
}

.btn-tech, .btn-tech-secondary {
  background: linear-gradient(90deg, #00cfff 0%, #1e90ff 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  padding: 8px 24px;
  box-shadow: 0 2px 8px 0 #00cfff33;
  transition: background 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.btn-tech-secondary {
  background: linear-gradient(90deg, #4a5568 0%, #2d3748 100%);
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.2);
}

.btn-tech-small {
  background: #183b6b;
  color: #00cfff;
  border: 1px solid #00cfff;
  border-radius: 6px;
  padding: 4px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-tech-small:hover {
  background: #00cfff;
  color: #183b6b;
}

.btn-tech:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px 0 #00cfff44;
}

.btn-tech:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
</style>
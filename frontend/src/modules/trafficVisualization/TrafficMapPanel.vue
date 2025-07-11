<template>
  <div class="card-tech p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold text-white flex items-center">
        <MapPin class="h-5 w-5 mr-2 text-cyan-400" />
        交通分布地图
      </h2>
      <div class="flex space-x-2">
        <button 
          v-for="view in mapViews" 
          :key="view.key"
          @click="changeMapView(view.key)"
          :class="[
            'px-3 py-1 rounded-lg text-sm transition-colors duration-300',
            currentMapView === view.key 
              ? 'bg-cyan-500 text-white' 
              : 'bg-blue-900 text-blue-200 hover:bg-blue-800'
          ]"
        >
          {{ view.name }}
        </button>
      </div>
    </div>
    
    <!-- 地图风格选择器 -->
    <div class="mb-4 flex flex-wrap gap-2">
      <button 
        v-for="style in mapStyles" 
        :key="style.key"
        @click="changeMapStyle(style.key)"
        :class="[
          'px-2 py-1 rounded text-xs transition-colors duration-300',
          currentMapStyle === style.key 
            ? 'bg-cyan-500 text-white' 
            : 'bg-blue-900 text-blue-200 hover:bg-blue-800'
        ]"
      >
        {{ style.name }}
      </button>
    </div>
    
    <!-- 地图容器 -->
    <div class="relative">
      <div 
        :id="mapContainerId" 
        ref="mapContainer"
        class="rounded-lg overflow-hidden border border-blue-800"
        style="min-height: 600px; width: 100%; height: 600px;"
      ></div>
      
      <!-- 地图状态信息 -->
      <div v-if="mapLoaded" class="absolute top-4 left-4 bg-blue-900/80 rounded-lg p-3 text-white text-sm">
        <div class="flex items-center mb-1">
          <div class="w-2 h-2 rounded-full bg-green-400 mr-2"></div>
          <span>地图已加载</span>
        </div>
        <div v-if="data && data.length > 0">
          <p>找到 {{ data.length }} 条数据</p>
          <p class="text-blue-200 text-xs">{{ vehicleId ? '车辆轨迹模式' : '区域分布模式' }}</p>
        </div>
      </div>
      
      <!-- 地图控制按钮 -->
      <div class="absolute top-4 right-4 flex flex-col space-y-2">
        <button 
          @click="centerToShandong"
          class="bg-blue-900/80 hover:bg-blue-800 text-white text-sm py-1 px-3 rounded-lg"
        >
          查看山东省
        </button>
        <button 
          @click="centerToJinan"
          class="bg-blue-900/80 hover:bg-blue-800 text-white text-sm py-1 px-3 rounded-lg"
        >
          查看济南市
        </button>
      </div>
      
      <!-- 加载中状态 -->
      <div v-if="loading || !mapLoaded" class="absolute inset-0 flex items-center justify-center bg-blue-950/50">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-cyan-500 mb-4"></div>
          <p class="text-cyan-400">{{ loadingMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { MapPin } from 'lucide-vue-next'
import mapAPIManager from '@/utils/mapManager.js'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  viewType: {
    type: String,
    default: 'distribution'
  },
  mapStyle: {
    type: String,
    default: 'blue'
  },
  loading: {
    type: Boolean,
    default: false
  },
  vehicleId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:viewType', 'update:mapStyle'])

// 生成唯一的地图容器ID
const mapContainerId = ref(`amap-container-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`)
const mapContainer = ref(null)
// 地图实例
let mapInstance = null
let currentHeatmap = null // 存储当前热力图实例
const mapLoaded = ref(false)
const loadingMessage = ref('正在加载高德地图API...')

// 地图风格
const mapStyleOptions = {
  normal: 'amap://styles/normal',
  dark: 'amap://styles/dark',
  light: 'amap://styles/light',
  whitesmoke: 'amap://styles/whitesmoke',
  fresh: 'amap://styles/fresh',
  blue: 'amap://styles/blue',
  darkblue: 'amap://styles/darkblue'
}

// 地图风格选项
const mapStyles = [
  { key: 'normal', name: '标准地图' },
  { key: 'dark', name: '暗色地图' },
  { key: 'light', name: '亮色地图' },
  { key: 'whitesmoke', name: '浅灰地图' },
  { key: 'fresh', name: '清新地图' },
  { key: 'blue', name: '蓝色地图' },
  { key: 'darkblue', name: '深蓝地图' }
]

// 当前地图风格
const currentMapStyle = ref(props.mapStyle || 'blue')

// 当前地图视图
const currentMapView = ref(props.viewType || 'distribution')

// 地图视图选项
const mapViews = [
  { key: 'distribution', name: '分布视图' },
  { key: 'trajectory', name: '轨迹视图' },
  { key: 'heatmap', name: '热力图' }
]

// 视图对应的默认风格
const viewStyleMap = {
  distribution: 'blue',
  trajectory: 'dark',
  heatmap: 'darkblue'
}

// 使用全局地图API管理器
async function loadAMapScript() {
  try {
    return await mapAPIManager.loadAPI()
  } catch (error) {
    console.error('地图API加载失败:', error)
    loadingMessage.value = `地图API加载失败: ${error.message}`
    throw error
  }
}

// 初始化地图 (优化版本)
async function initMap() {
  try {
    // 检查组件是否已经卸载
    if (!mapContainer.value) {
      console.warn('地图容器不存在，可能组件已卸载')
      return
    }
    
    // 如果地图实例已存在，先销毁
    if (mapInstance) {
      console.log('清理现有地图实例')
      await cleanupMap()
    }
    
    // 确保高德地图API已加载
    loadingMessage.value = '正在加载高德地图API...'
    await loadAMapScript()
    
    // 再次检查组件是否已卸载（API加载过程中可能组件已经切换）
    if (!mapContainer.value) {
      console.warn('API加载期间组件已卸载')
      return
    }
    
    loadingMessage.value = '正在初始化地图...'
    console.log(`正在初始化地图，容器ID: ${mapContainerId.value}`)
    
    // 等待下一个tick确保DOM完全渲染
    await nextTick()
    
    // 等待容器准备就绪（带重试机制）
    let containerElement = null
    let attempts = 0
    const maxAttempts = 10
    
    while (!containerElement && attempts < maxAttempts) {
      containerElement = document.getElementById(mapContainerId.value)
      if (!containerElement) {
        attempts++
        console.log(`等待地图容器准备就绪... (${attempts}/${maxAttempts})`)
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    }
    
    if (!containerElement) {
      console.error(`找不到地图容器: ${mapContainerId.value}，已重试 ${maxAttempts} 次`)
      loadingMessage.value = '地图容器初始化失败，请刷新页面重试'
      return
    }
    
    console.log('地图容器已找到:', containerElement)
    
    // 创建地图实例
    mapInstance = new window.AMap.Map(mapContainerId.value, {
      center: [117.120, 36.651], // 济南市中心
      zoom: 8,                   // 缩放级别
      viewMode: '2D',            // 2D模式
      mapStyle: mapStyleOptions[currentMapStyle.value],
      features: ['bg', 'road', 'building', 'point'],
      doubleClickZoom: false,
      renderMode: 'canvas'
    })
    
    // 添加地图控件
    mapInstance.plugin(['AMap.ToolBar', 'AMap.Scale'], function() {
      if (mapInstance) { // 确保地图实例仍然存在
        mapInstance.addControl(new window.AMap.ToolBar())
        mapInstance.addControl(new window.AMap.Scale())
      }
    })
    
    // 监听地图加载完成事件
    mapInstance.on('complete', function() {
      console.log('地图加载完成')
      mapLoaded.value = true
      loadingMessage.value = ''
      // 根据当前视图类型更新地图
      updateMapByViewType(currentMapView.value)
    })
    
    // 监听地图错误事件
    mapInstance.on('error', function(error) {
      console.error('地图加载错误:', error)
      loadingMessage.value = '地图加载错误，请刷新重试'
    })
    
  } catch (error) {
    console.error('地图初始化失败:', error)
    loadingMessage.value = '地图初始化失败，请刷新重试'
  }
}

// 清理地图资源 (新增函数)
async function cleanupMap() {
  return new Promise((resolve) => {
    try {
      // 清理热力图实例
      if (currentHeatmap) {
        currentHeatmap.setMap(null)
        currentHeatmap = null
      }
      
      // 清理地图实例
      if (mapInstance) {
        mapInstance.clearMap()
        mapInstance.destroy()
        mapInstance = null
      }
      
      // 重置状态
      mapLoaded.value = false
      loadingMessage.value = '正在加载高德地图API...'
      
      console.log('地图资源清理完成')
      resolve()
    } catch (error) {
      console.warn('清理地图资源时出错:', error)
      resolve() // 即使出错也要继续
    }
  })
}

// 根据视图类型更新地图
function updateMapByViewType(viewType) {
  if (!mapInstance) return
  
  // 根据视图类型设置默认风格
  if (viewStyleMap[viewType]) {
    currentMapStyle.value = viewStyleMap[viewType]
    mapInstance.setMapStyle(mapStyleOptions[currentMapStyle.value])
  }
  
  // 根据不同视图类型执行不同操作
  switch (viewType) {
    case 'distribution':
      // 分布视图逻辑
      renderDistributionView()
      break
    case 'trajectory':
      // 轨迹视图逻辑
      renderTrajectoryView()
      break
    case 'heatmap':
      // 热力图视图逻辑
      renderHeatmapView()
      break
  }
}

// 切换地图风格
function changeMapStyle(styleKey) {
  if (!mapInstance) return
  
  currentMapStyle.value = styleKey
  mapInstance.setMapStyle(mapStyleOptions[styleKey])
  emit('update:mapStyle', styleKey)
}

// 分布视图渲染
function renderDistributionView() {
  if (!mapInstance || !props.data || !props.data.length) return
  
  // 清除已有标记
  mapInstance.clearMap()
  
  // 添加点标记
  props.data.forEach(item => {
    const lat = item.lat || item.latitude
    const lng = item.lng || item.longitude
    
    if (lat && lng) {
      new window.AMap.Marker({
        position: [lng, lat],
        map: mapInstance,
        icon: new window.AMap.Icon({
          size: new window.AMap.Size(6, 6),
          image: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNiIgaGVpZ2h0PSI2IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxjaXJjbGUgY3g9IjMiIGN5PSIzIiByPSIzIiBmaWxsPSIjMDBjZmZmIi8+PC9zdmc+',
          imageSize: new window.AMap.Size(6, 6)
        })
      })
    }
  })
}

// 轨迹视图渲染
function renderTrajectoryView() {
  if (!mapInstance || !props.data || !props.data.length) return
  
  // 清除已有标记
  mapInstance.clearMap()
  
  // 如果有指定车辆ID，绘制该车辆轨迹
  if (props.vehicleId) {
    const vehicleData = props.data
      .filter(item => item.vehicleId === props.vehicleId || item.vehicle_id === props.vehicleId)
      .sort((a, b) => {
        const timeA = a.timestamp || a.UTC || 0
        const timeB = b.timestamp || b.UTC || 0
        return timeA - timeB
      })
    
    if (vehicleData.length > 1) {
      // 创建轨迹路径
      const path = vehicleData.map(item => {
        const lng = item.lng || item.longitude
        const lat = item.lat || item.latitude
        return [lng, lat]
      })
      
      // 绘制轨迹线
      const polyline = new window.AMap.Polyline({
        path: path,
        strokeColor: '#00cfff',
        strokeWeight: 4,
        strokeOpacity: 0.8,
        showDir: true
      })
      
      mapInstance.add(polyline)
      
      // 添加起点和终点标记
      const startMarker = new window.AMap.Marker({
        position: path[0],
        map: mapInstance,
        icon: new window.AMap.Icon({
          size: new window.AMap.Size(25, 34),
          imageSize: new window.AMap.Size(25, 34),
          image: '//a.amap.com/jsapi_demos/static/demo-center/icons/dir-marker.png'
        })
      })
      
      const endMarker = new window.AMap.Marker({
        position: path[path.length - 1],
        map: mapInstance,
        icon: new window.AMap.Icon({
          size: new window.AMap.Size(25, 34),
          imageSize: new window.AMap.Size(25, 34),
          image: '//a.amap.com/jsapi_demos/static/demo-center/icons/dir-spot.png'
        })
      })
      
      // 自适应缩放级别
      mapInstance.setFitView([polyline, startMarker, endMarker])
    }
  }
}

// 热力图视图渲染
function renderHeatmapView() {
  if (!mapInstance || !props.data || !props.data.length) return
  
  // 清除已有标记和热力图
  mapInstance.clearMap()
  if (currentHeatmap) {
    currentHeatmap.setMap(null)
    currentHeatmap = null
  }
  
  // 准备热力图数据
  const heatmapData = props.data.map(item => {
    const lng = item.lng || item.longitude
    const lat = item.lat || item.latitude
    const count = item.count || item.speed || 1
    
    return {
      lng: lng,
      lat: lat,
      count: count
    }
  }).filter(item => item.lng && item.lat) // 过滤掉无效数据
  
  if (heatmapData.length === 0) {
    console.warn('没有有效的热力图数据')
    return
  }
  
  // 加载热力图插件
  mapInstance.plugin(['AMap.HeatMap'], function() {
    try {
      // 创建热力图实例
      currentHeatmap = new window.AMap.HeatMap(mapInstance, {
        radius: 25,
        opacity: [0, 0.8],
        gradient: {
          0.5: 'blue',
          0.65: 'rgb(117,211,248)',
          0.7: 'rgb(0,255,0)',
          0.9: 'yellow',
          1.0: 'red'
        },
        // 添加配置减少Canvas警告
        blur: 0.85,
        zooms: [3, 18]
      })
      
      // 设置热力图数据
      currentHeatmap.setDataSet({
        data: heatmapData,
        max: Math.max(...heatmapData.map(item => item.count))
      })
      
      console.log(`热力图渲染完成，共 ${heatmapData.length} 个点`)
    } catch (error) {
      console.error('热力图渲染失败:', error)
    }
  })
}

// 切换地图视图
function changeMapView(viewType) {
  currentMapView.value = viewType
  emit('update:viewType', viewType)
  updateMapByViewType(viewType)
}

// 定位到山东省
function centerToShandong() {
  if (mapInstance) {
    mapInstance.setZoomAndCenter(7, [118.000, 36.400])
  }
}

// 定位到济南市
function centerToJinan() {
  if (mapInstance) {
    mapInstance.setZoomAndCenter(11, [117.120, 36.651])
  }
}

// 监听视图类型变化
watch(() => props.viewType, (newView) => {
  if (mapInstance && newView) {
    currentMapView.value = newView
    updateMapByViewType(newView)
  }
})

// 监听地图风格变化
watch(() => props.mapStyle, (newStyle) => {
  if (mapInstance && newStyle) {
    currentMapStyle.value = newStyle
    mapInstance.setMapStyle(mapStyleOptions[newStyle])
  }
})

// 监听交通数据变化
watch(() => props.data, (newData) => {
  if (mapInstance && newData && newData.length > 0) {
    updateMapByViewType(currentMapView.value)
  }
}, { deep: true })

// 组件挂载时初始化地图 (优化版本)
onMounted(async () => {
  console.log('TrafficMapPanel 组件已挂载')
  
  // 等待DOM完全渲染
  await nextTick()
  
  // 延迟初始化，确保组件稳定
  setTimeout(async () => {
    if (mapContainer.value) { // 确保组件仍然挂载
      console.log('开始初始化地图')
      await initMap()
    }
  }, 200) // 稍微增加延迟确保组件稳定
})

// 组件卸载时销毁地图 (优化版本)
onUnmounted(async () => {
  console.log('TrafficMapPanel 组件开始卸载')
  
  // 异步清理避免阻塞
  setTimeout(async () => {
    await cleanupMap()
    console.log('TrafficMapPanel 组件卸载完成')
  }, 0)
})
</script>

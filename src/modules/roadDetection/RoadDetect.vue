<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">路面病害检测系统</h1>
        <p class="text-gray-600 mt-2">智能识别路面病害，提供精准检测与分析</p>
      </div>

      <!-- 告警面板 -->
      <div v-if="alarms.length > 0" class="mb-6">
        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="flex items-center">
            <AlertTriangle class="h-5 w-5 text-red-500 mr-2" />
            <h3 class="text-red-800 font-medium">系统告警</h3>
          </div>
          <div class="mt-2 space-y-1">
            <div v-for="alarm in alarms" :key="alarm.id" class="text-red-700 text-sm">
              {{ alarm.message }} - {{ alarm.level }}
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧：上传和检测区域 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 文件上传区域 -->
          <div class="bg-white rounded-lg shadow-sm border p-6">
            <h2 class="text-xl font-semibold mb-4 flex items-center">
              <Upload class="h-5 w-5 mr-2" />
              图像上传
            </h2>
            
            <div 
              @drop="handleDrop"
              @dragover.prevent
              @dragenter.prevent
              class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors"
              :class="{ 'border-blue-400 bg-blue-50': isDragging }"
            >
              <div v-if="!selectedFile">
                <ImageIcon class="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p class="text-gray-600 mb-2">拖拽图片到此处或点击上传</p>
                <input 
                  type="file" 
                  ref="fileInput"
                  @change="handleFileSelect"
                  accept="image/*,video/*"
                  class="hidden"
                />
                <button 
                  @click="$refs.fileInput.click()"
                  class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  选择文件
                </button>
              </div>
              
              <div v-else class="space-y-4">
                <img 
                  v-if="previewUrl" 
                  :src="previewUrl" 
                  alt="预览图片"
                  class="max-h-64 mx-auto rounded-lg"
                />
                <div class="flex items-center justify-center space-x-4">
                  <span class="text-gray-700">{{ selectedFile.name }}</span>
                  <button 
                    @click="detectDamage"
                    :disabled="isDetecting"
                    class="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
                  >
                    <div v-if="isDetecting" class="flex items-center">
                      <Loader2 class="h-4 w-4 mr-2 animate-spin" />
                      检测中...
                    </div>
                    <div v-else class="flex items-center">
                      <Search class="h-4 w-4 mr-2" />
                      开始检测
                    </div>
                  </button>
                  <button 
                    @click="clearFile"
                    class="text-gray-500 hover:text-gray-700"
                  >
                    <X class="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 检测结果展示 -->
          <div v-if="detectionResult" class="bg-white rounded-lg shadow-sm border p-6">
            <h2 class="text-xl font-semibold mb-4 flex items-center">
              <Eye class="h-5 w-5 mr-2" />
              检测结果
            </h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 结果图像 -->
              <div>
                <div class="relative">
                  <img 
                    :src="detectionResult.imageUrl" 
                    alt="检测结果"
                    class="w-full rounded-lg border"
                  />
                  <!-- 病害标注叠加 -->
                  <div 
                    v-for="damage in detectionResult.damages" 
                    :key="damage.id"
                    class="absolute border-2 border-red-500 bg-red-500 bg-opacity-20"
                    :style="{
                      left: damage.bbox.x + 'px',
                      top: damage.bbox.y + 'px',
                      width: damage.bbox.width + 'px',
                      height: damage.bbox.height + 'px'
                    }"
                  >
                    <div class="bg-red-500 text-white text-xs px-1 py-0.5 rounded">
                      {{ damage.type }}
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 检测详情 -->
              <div class="space-y-4">
                <div class="bg-gray-50 rounded-lg p-4">
                  <h3 class="font-medium mb-2">检测统计</h3>
                  <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span class="text-gray-600">病害数量:</span>
                      <span class="font-medium ml-2">{{ detectionResult.totalCount }}</span>
                    </div>
                    <div>
                      <span class="text-gray-600">总面积:</span>
                      <span class="font-medium ml-2">{{ detectionResult.totalArea }}m²</span>
                    </div>
                  </div>
                </div>
                
                <div class="space-y-2">
                  <h3 class="font-medium">病害详情</h3>
                  <div class="max-h-48 overflow-y-auto space-y-2">
                    <div 
                      v-for="damage in detectionResult.damages" 
                      :key="damage.id"
                      class="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-sm"
                    >
                      <div>
                        <div class="font-medium">{{ damage.type }}</div>
                        <div class="text-gray-600">置信度: {{ (damage.confidence * 100).toFixed(1) }}%</div>
                      </div>
                      <div class="text-right">
                        <div class="font-medium">{{ damage.area }}m²</div>
                        <div class="text-gray-600">严重程度: {{ damage.severity }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：统计和日志 -->
        <div class="space-y-6">
          <!-- 实时统计 -->
          <div class="bg-white rounded-lg shadow-sm border p-6">
            <h2 class="text-xl font-semibold mb-4 flex items-center">
              <BarChart3 class="h-5 w-5 mr-2" />
              实时统计
            </h2>
            
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div class="text-center p-3 bg-blue-50 rounded-lg">
                  <div class="text-2xl font-bold text-blue-600">{{ stats.todayDetections }}</div>
                  <div class="text-sm text-gray-600">今日检测</div>
                </div>
                <div class="text-center p-3 bg-red-50 rounded-lg">
                  <div class="text-2xl font-bold text-red-600">{{ stats.totalDamages }}</div>
                  <div class="text-sm text-gray-600">发现病害</div>
                </div>
              </div>
              
              <!-- 病害类型分布 -->
              <div>
                <h3 class="font-medium mb-2">病害类型分布</h3>
                <div class="space-y-2">
                  <div v-for="type in stats.damageTypes" :key="type.name" class="flex items-center justify-between">
                    <span class="text-sm">{{ type.name }}</span>
                    <div class="flex items-center">
                      <div class="w-16 h-2 bg-gray-200 rounded-full mr-2">
                        <div 
                          class="h-2 bg-blue-500 rounded-full"
                          :style="{ width: (type.count / stats.totalDamages * 100) + '%' }"
                        ></div>
                      </div>
                      <span class="text-sm font-medium">{{ type.count }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作日志 -->
          <div class="bg-white rounded-lg shadow-sm border p-6">
            <h2 class="text-xl font-semibold mb-4 flex items-center">
              <FileText class="h-5 w-5 mr-2" />
              操作日志
            </h2>
            
            <div class="max-h-64 overflow-y-auto space-y-2">
              <div 
                v-for="log in logs" 
                :key="log.id"
                class="flex items-center justify-between p-2 hover:bg-gray-50 rounded text-sm"
              >
                <div>
                  <div class="font-medium">{{ log.action }}</div>
                  <div class="text-gray-600">{{ log.operator }}</div>
                </div>
                <div class="text-gray-500 text-xs">
                  {{ formatTime(log.timestamp) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 趋势分析 -->
      <div class="mt-8 bg-white rounded-lg shadow-sm border p-6">
        <h2 class="text-xl font-semibold mb-4 flex items-center">
          <TrendingUp class="h-5 w-5 mr-2" />
          趋势分析
        </h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- 时间趋势图 -->
          <div>
            <h3 class="font-medium mb-2">病害检测趋势</h3>
            <div class="h-48 bg-gray-50 rounded-lg flex items-center justify-center">
              <div class="text-gray-500">趋势图表区域</div>
            </div>
          </div>
          
          <!-- 类型分布饼图 -->
          <div>
            <h3 class="font-medium mb-2">病害类型分布</h3>
            <div class="h-48 bg-gray-50 rounded-lg flex items-center justify-center">
              <div class="text-gray-500">饼图区域</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  Upload, 
  Search, 
  Eye, 
  BarChart3, 
  FileText, 
  TrendingUp, 
  AlertTriangle,
  Loader2,
  X,
  ImageIcon
} from 'lucide-vue-next'

// 响应式数据
const selectedFile = ref(null)
const previewUrl = ref('')
const isDragging = ref(false)
const isDetecting = ref(false)
const detectionResult = ref(null)
const alarms = ref([])
const stats = ref({
  todayDetections: 0,
  totalDamages: 0,
  damageTypes: []
})
const logs = ref([])
const fileInput = ref(null)

// API 基础URL
const API_BASE = '/api'

// 文件处理
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file && (file.type.startsWith('image/') || file.type.startsWith('video/'))) {
    selectedFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

const clearFile = () => {
  selectedFile.value = null
  previewUrl.value = ''
  detectionResult.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 上传图片
const uploadImage = async (file) => {
  const formData = new FormData()
  formData.append('image', file)
  
  try {
    const response = await fetch(`${API_BASE}/upload/image`, {
      method: 'POST',
      body: formData
    })
    return await response.json()
  } catch (error) {
    console.error('上传失败:', error)
    throw error
  }
}

// 检测病害
const detectDamage = async () => {
  if (!selectedFile.value) return
  
  isDetecting.value = true
  
  try {
    // 1. 上传图片
    const uploadResult = await uploadImage(selectedFile.value)
    
    // 2. 触发检测
    const detectResponse = await fetch(`${API_BASE}/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        imageId: uploadResult.id,
        imagePath: uploadResult.path
      })
    })
    
    const detectResult = await detectResponse.json()
    
    // 3. 获取检测结果详情
    const resultResponse = await fetch(`${API_BASE}/results/${detectResult.id}`)
    const result = await resultResponse.json()
    
    detectionResult.value = {
      imageUrl: result.processedImageUrl || previewUrl.value,
      totalCount: result.damages?.length || 0,
      totalArea: result.damages?.reduce((sum, d) => sum + d.area, 0) || 0,
      damages: result.damages || []
    }
    
    // 刷新统计数据
    await fetchStats()
    await fetchLogs()
    
  } catch (error) {
    console.error('检测失败:', error)
    alert('检测失败，请重试')
  } finally {
    isDetecting.value = false
  }
}

// 获取告警数据
const fetchAlarms = async () => {
  try {
    const response = await fetch(`${API_BASE}/alarm`)
    const data = await response.json()
    alarms.value = data.alarms || []
  } catch (error) {
    console.error('获取告警数据失败:', error)
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await fetch(`${API_BASE}/trend`)
    const data = await response.json()
    stats.value = {
      todayDetections: data.todayDetections || 0,
      totalDamages: data.totalDamages || 0,
      damageTypes: data.damageTypes || [
        { name: '裂缝', count: 15 },
        { name: '坑洞', count: 8 },
        { name: '破损', count: 12 },
        { name: '其他', count: 5 }
      ]
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    // 使用模拟数据
    stats.value = {
      todayDetections: 23,
      totalDamages: 40,
      damageTypes: [
        { name: '裂缝', count: 15 },
        { name: '坑洞', count: 8 },
        { name: '破损', count: 12 },
        { name: '其他', count: 5 }
      ]
    }
  }
}

// 获取操作日志
const fetchLogs = async () => {
  try {
    const response = await fetch(`${API_BASE}/logs`)
    const data = await response.json()
    logs.value = data.logs || []
  } catch (error) {
    console.error('获取日志失败:', error)
    // 使用模拟数据
    logs.value = [
      { id: 1, action: '图像检测完成', operator: '系统', timestamp: new Date() },
      { id: 2, action: '上传图像文件', operator: '用户', timestamp: new Date(Date.now() - 300000) },
      { id: 3, action: '病害识别', operator: '系统', timestamp: new Date(Date.now() - 600000) }
    ]
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchAlarms()
  fetchStats()
  fetchLogs()
  
  // 定时刷新告警数据
  setInterval(fetchAlarms, 30000)
})
</script>

<style scoped>
/* 自定义样式 */
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

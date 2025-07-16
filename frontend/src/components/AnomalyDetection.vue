<template>
  <div class="space-y-6">
    <!-- 异常检测标题 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <AlertTriangle class="h-8 w-8 text-red-400 mr-3" />
          <div>
            <h2 class="text-2xl font-bold text-white">异常检测系统</h2>
            <p class="text-gray-300">实时监控交通异常事件</p>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-red-400">{{ anomalyCount }}</div>
            <div class="text-sm text-gray-300">异常事件</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-400">{{ normalCount }}</div>
            <div class="text-sm text-gray-300">正常状态</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 异常类型统计 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div 
        v-for="type in anomalyTypes" 
        :key="type.name"
        class="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20"
      >
        <div class="flex items-center">
          <component :is="type.icon" :class="['h-6 w-6 mr-3', type.color]" />
          <div>
            <div class="text-lg font-bold text-white">{{ type.count }}</div>
            <div class="text-sm text-gray-300">{{ type.name }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 实时异常列表 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
      <div class="p-6 border-b border-white/10">
        <h3 class="text-xl font-semibold text-white">实时异常事件</h3>
      </div>
      <div class="p-6">
        <div class="space-y-4">
          <div 
            v-for="anomaly in realtimeAnomalies" 
            :key="anomaly.id"
            class="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10"
          >
            <div class="flex items-center">
              <div :class="['w-3 h-3 rounded-full mr-3', getSeverityColor(anomaly.severity)]"></div>
              <div>
                <div class="text-white font-medium">{{ anomaly.title }}</div>
                <div class="text-gray-300 text-sm">{{ anomaly.location }} • {{ anomaly.time }}</div>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <span :class="['px-2 py-1 rounded text-xs font-medium', getSeverityBadge(anomaly.severity)]">
                {{ anomaly.severity }}
              </span>
              <button class="text-cyan-400 hover:text-cyan-300 transition-colors">
                <Eye class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 异常趋势图表 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 24小时异常趋势 -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <h3 class="text-xl font-semibold text-white mb-4">24小时异常趋势</h3>
        <div class="h-64 flex items-end justify-between space-x-2">
          <div 
            v-for="(hour, index) in hourlyData" 
            :key="index"
            class="flex-1 bg-gradient-to-t from-red-500/20 to-red-400/40 rounded-t"
            :style="{ height: `${(hour / Math.max(...hourlyData)) * 100}%` }"
            :title="`${index}:00 - ${hour}个异常`"
          ></div>
        </div>
        <div class="flex justify-between text-xs text-gray-400 mt-2">
          <span>00:00</span>
          <span>06:00</span>
          <span>12:00</span>
          <span>18:00</span>
          <span>24:00</span>
        </div>
      </div>

      <!-- 异常分布地图 -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <h3 class="text-xl font-semibold text-white mb-4">异常分布热力图</h3>
        <div class="h-64 bg-gray-800/50 rounded-lg flex items-center justify-center relative overflow-hidden">
          <!-- 模拟地图背景 -->
          <div class="absolute inset-0 opacity-20">
            <div class="w-full h-full bg-gradient-to-br from-blue-500 via-green-500 to-yellow-500"></div>
          </div>
          <!-- 异常点标记 -->
          <div 
            v-for="point in anomalyPoints" 
            :key="point.id"
            class="absolute w-4 h-4 bg-red-500 rounded-full animate-pulse"
            :style="{ left: `${point.x}%`, top: `${point.y}%` }"
            :title="point.description"
          ></div>
          <div class="text-gray-400 text-center">
            <Map class="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>异常事件分布图</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 异常处理状态 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
      <div class="p-6 border-b border-white/10">
        <h3 class="text-xl font-semibold text-white">异常处理状态</h3>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="text-center p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
            <div class="text-2xl font-bold text-yellow-400">{{ processingStatus.pending }}</div>
            <div class="text-sm text-gray-300">待处理</div>
          </div>
          <div class="text-center p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
            <div class="text-2xl font-bold text-blue-400">{{ processingStatus.processing }}</div>
            <div class="text-sm text-gray-300">处理中</div>
          </div>
          <div class="text-center p-4 bg-green-500/10 rounded-lg border border-green-500/20">
            <div class="text-2xl font-bold text-green-400">{{ processingStatus.resolved }}</div>
            <div class="text-sm text-gray-300">已解决</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { AlertTriangle, Car, Users, Zap, Eye, Map } from 'lucide-vue-next'

// 响应式数据
const anomalyCount = ref(23)
const normalCount = ref(1247)

const anomalyTypes = ref([
  { name: '交通拥堵', count: 8, icon: Car, color: 'text-red-400' },
  { name: '设备故障', count: 5, icon: Zap, color: 'text-yellow-400' },
  { name: '异常聚集', count: 7, icon: Users, color: 'text-orange-400' },
  { name: '其他异常', count: 3, icon: AlertTriangle, color: 'text-purple-400' }
])

const realtimeAnomalies = ref([
  {
    id: 1,
    title: '严重交通拥堵',
    location: '中山路与解放路交叉口',
    time: '2分钟前',
    severity: '高'
  },
  {
    id: 2,
    title: '信号灯故障',
    location: '人民大道123号',
    time: '5分钟前',
    severity: '中'
  },
  {
    id: 3,
    title: '异常车流聚集',
    location: '火车站广场',
    time: '8分钟前',
    severity: '低'
  },
  {
    id: 4,
    title: '道路施工影响',
    location: '建设路段',
    time: '12分钟前',
    severity: '中'
  }
])

const hourlyData = ref([2, 1, 0, 1, 3, 5, 8, 12, 15, 18, 22, 25, 20, 18, 16, 14, 19, 23, 21, 18, 15, 12, 8, 5])

const anomalyPoints = ref([
  { id: 1, x: 25, y: 30, description: '交通拥堵' },
  { id: 2, x: 60, y: 45, description: '设备故障' },
  { id: 3, x: 80, y: 20, description: '异常聚集' },
  { id: 4, x: 40, y: 70, description: '道路施工' },
  { id: 5, x: 70, y: 60, description: '信号异常' }
])

const processingStatus = ref({
  pending: 8,
  processing: 12,
  resolved: 156
})

// 方法
const getSeverityColor = (severity) => {
  switch (severity) {
    case '高': return 'bg-red-500'
    case '中': return 'bg-yellow-500'
    case '低': return 'bg-green-500'
    default: return 'bg-gray-500'
  }
}

const getSeverityBadge = (severity) => {
  switch (severity) {
    case '高': return 'bg-red-500/20 text-red-400 border border-red-500/30'
    case '中': return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
    case '低': return 'bg-green-500/20 text-green-400 border border-green-500/30'
    default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
  }
}

onMounted(() => {
  // 模拟实时数据更新
  setInterval(() => {
    // 随机更新异常数量
    anomalyCount.value = Math.floor(Math.random() * 50) + 10
    normalCount.value = Math.floor(Math.random() * 500) + 1000
  }, 5000)
})
</script>

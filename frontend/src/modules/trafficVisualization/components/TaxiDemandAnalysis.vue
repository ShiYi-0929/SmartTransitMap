<template>
  <div class="space-y-6">
    <!-- 组件标题 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <Car class="h-6 w-6 text-purple-400 mr-3" />
          <div>
            <h2 class="text-xl font-semibold text-white">载客出租车数量动态展示</h2>
            <p class="text-purple-200 text-sm mt-1">实时监控载客出租车分布与需求匹配</p>
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <div class="flex items-center">
            <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></div>
            <span class="text-green-300 text-sm">实时监控</span>
          </div>
          <button 
            @click="$emit('refresh')"
            :disabled="loading"
            class="px-3 py-1 bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 rounded-lg transition-all disabled:opacity-50"
          >
            <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': loading }" />
          </button>
        </div>
      </div>
    </div>

    <!-- 实时状态面板 -->
    <div v-if="realTimeData" class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold text-green-400">{{ realTimeData.taxi_stats?.loaded_taxis || 0 }}</div>
            <div class="text-sm text-gray-300">载客车辆</div>
          </div>
          <Users class="h-8 w-8 text-green-400" />
        </div>
        <div class="mt-2 text-xs text-green-200">
          占比: {{ getLoadedTaxiRatio() }}%
        </div>
      </div>

      <div class="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold text-blue-400">{{ realTimeData.taxi_stats?.empty_taxis || 0 }}</div>
            <div class="text-sm text-gray-300">空载车辆</div>
          </div>
          <Car class="h-8 w-8 text-blue-400" />
        </div>
        <div class="mt-2 text-xs text-blue-200">
          可用运力
        </div>
      </div>

      <div class="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold text-yellow-400">{{ realTimeData.taxi_stats?.total_demand || 0 }}</div>
            <div class="text-sm text-gray-300">总需求</div>
          </div>
          <TrendingUp class="h-8 w-8 text-yellow-400" />
        </div>
        <div class="mt-2 text-xs text-yellow-200">
          需求指数: {{ (realTimeData.taxi_stats?.avg_demand_index || 0).toFixed(2) }}
        </div>
      </div>

      <div class="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold" :class="getSupplyStatusColor()">
              {{ getSupplyStatus() }}
            </div>
            <div class="text-sm text-gray-300">供需状态</div>
          </div>
          <Activity class="h-8 w-8" :class="getSupplyStatusColor()" />
        </div>
        <div class="mt-2 text-xs text-gray-400">
          {{ getSupplyStatusText() }}
        </div>
      </div>
    </div>

    <!-- 供需分析图表 -->
    <!-- 直接删除整个供需对比分析相关的div及其内容，不保留 -->

    <!-- 供应不足区域 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
      <div class="p-4 border-b border-white/10">
        <h3 class="text-lg font-semibold text-white flex items-center">
          <AlertTriangle class="h-5 w-5 mr-2" />
          供应不足区域预警
        </h3>
      </div>
      <div class="p-4">
        <div v-if="loading" class="flex items-center justify-center h-32">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-400"></div>
        </div>
        <div v-else-if="getShortageAreas().length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="(shortage, index) in getShortageAreas()" 
            :key="index"
            class="p-3 bg-orange-500/10 rounded-lg border border-orange-500/20"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center">
                <AlertTriangle class="h-4 w-4 text-orange-400 mr-2" />
                <span class="text-white font-medium">区域 {{ index + 1 }}</span>
              </div>
              <div class="text-orange-400 font-bold">
                {{ shortage.supply_ratio.toFixed(2) }}
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>
                <div class="text-gray-400">位置</div>
                <div class="text-blue-400 font-mono text-xs">
                  {{ shortage.location.lat.toFixed(4) }}, {{ shortage.location.lng.toFixed(4) }}
                </div>
              </div>
              <div>
                <div class="text-gray-400">等待订单</div>
                <div class="text-red-400 font-mono">{{ shortage.waiting_orders }}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="flex items-center justify-center h-32 text-gray-400">
          <div class="text-center">
            <CheckCircle class="h-8 w-8 mx-auto mb-2 text-green-400" />
            <p class="text-green-400">所有区域供应充足</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细分析报告 -->
    <div v-if="!compact" class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
      <div class="p-4 border-b border-white/10">
        <h3 class="text-lg font-semibold text-white flex items-center">
          <FileText class="h-5 w-5 mr-2" />
          载客车辆分析报告
        </h3>
      </div>
      <div class="p-4">
        <div class="space-y-4 text-sm">
          <div class="p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
            <h4 class="text-purple-400 font-medium mb-2">🚕 载客车辆概况</h4>
            <ul class="text-purple-200 space-y-1">
              <li>• 当前载客车辆：{{ realTimeData?.taxi_stats?.loaded_taxis || 0 }} 辆</li>
              <li>• 空载车辆：{{ realTimeData?.taxi_stats?.empty_taxis || 0 }} 辆</li>
              <li>• 载客率：{{ getLoadedTaxiRatio() }}%</li>
              <li>• 平均需求指数：{{ (realTimeData?.taxi_stats?.avg_demand_index || 0).toFixed(3) }}</li>
            </ul>
          </div>

          <div class="p-3 bg-green-500/10 rounded-lg border border-green-500/20">
            <h4 class="text-green-400 font-medium mb-2">📊 供需分析结果</h4>
            <ul class="text-green-200 space-y-1">
              <li>• 总需求量：{{ realTimeData?.taxi_stats?.total_demand || 0 }} 单</li>
              <li>• 供需状态：{{ getSupplyStatusText() }}</li>
              <li>• 热点区域：{{ getHotspotAreas().length }} 个</li>
              <li>• 供应不足区域：{{ getShortageAreas().length }} 个</li>
            </ul>
          </div>

          <div class="p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
            <h4 class="text-blue-400 font-medium mb-2">🎯 运营建议</h4>
            <ul class="text-blue-200 space-y-1">
              <li>• 向热点区域增派空载车辆，提高服务效率</li>
              <li>• 对供应不足区域实施动态调度</li>
              <li>• 优化车辆分布，平衡各区域供需</li>
              <li>• 建立实时调度系统，快速响应需求变化</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  Car, Users, Activity, MapPin, FileText, RefreshCw
} from 'lucide-vue-next'

// Props
const props = defineProps({
  taxiData: {
    type: Object,
    default: null
  },
  realTimeData: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['refresh'])

// 计算载客车辆比例
const getLoadedTaxiRatio = () => {
  if (!props.realTimeData?.taxi_stats) return '0.0'
  const loaded = props.realTimeData.taxi_stats.loaded_taxis || 0
  const empty = props.realTimeData.taxi_stats.empty_taxis || 0
  const total = loaded + empty
  return total > 0 ? ((loaded / total) * 100).toFixed(1) : '0.0'
}

// 计算总车辆数
const getTotalVehicles = () => {
  if (!props.realTimeData?.taxi_stats) return 0
  const loaded = props.realTimeData.taxi_stats.loaded_taxis || 0
  const empty = props.realTimeData.taxi_stats.empty_taxis || 0
  return loaded + empty
}

// 车辆分布分析（示例：按区域聚合，实际可根据后端返回结构调整）
const getVehicleDistribution = () => {
  // 这里假设 taxiData 里有 vehicle_distribution 字段，实际可根据后端返回结构调整
  if (!props.taxiData?.vehicle_distribution) return []
  return props.taxiData.vehicle_distribution
}

// 平均载客率
const getAverageLoadedRatio = () => {
  const dist = getVehicleDistribution()
  if (!dist.length) return '0.0'
  const avg = dist.reduce((sum, area) => sum + (area.loaded_ratio || 0), 0) / dist.length
  return (avg * 100).toFixed(1)
}

// 获取供应状态
const getSupplyStatus = () => {
  if (!props.realTimeData?.status_indicators) return '正常'
  const status = props.realTimeData.status_indicators.supply_status
  const statusMap = {
    'adequate': '充足',
    'shortage': '不足',
    'surplus': '过剩'
  }
  return statusMap[status] || '正常'
}

// 获取供应状态颜色
const getSupplyStatusColor = () => {
  const status = getSupplyStatus()
  if (status === '充足') return 'text-green-400'
  if (status === '不足') return 'text-red-400'
  if (status === '过剩') return 'text-blue-400'
  return 'text-gray-400'
}

// 获取供应状态文本
const getSupplyStatusText = () => {
  const status = getSupplyStatus()
  if (status === '充足') return '供需平衡'
  if (status === '不足') return '需增加运力'
  if (status === '过剩') return '运力过剩'
  return '状态正常'
}

// 获取供需比例颜色
const getSupplyDemandColor = (ratio) => {
  if (ratio >= 0.8) return 'bg-green-500'
  if (ratio >= 0.6) return 'bg-yellow-500'
  if (ratio >= 0.4) return 'bg-orange-500'
  return 'bg-red-500'
}

// 格式化时间段
const formatTimePeriod = (period) => {
  // 假设period是时间戳或时间字符串
  if (typeof period === 'string') {
    return period
  }
  return new Date(period * 1000).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取热点区域
const getHotspotAreas = () => {
  if (!props.taxiData?.supply_demand_analysis) return []
  
  const allHotspots = []
  props.taxiData.supply_demand_analysis.forEach(analysis => {
    if (analysis.hotspot_areas) {
      allHotspots.push(...analysis.hotspot_areas)
    }
  })
  
  // 按需求指数排序，取前5个
  return allHotspots
    .sort((a, b) => b.demand_index - a.demand_index)
    .slice(0, 5)
}

// 获取供应不足区域
const getShortageAreas = () => {
  if (!props.taxiData?.supply_demand_analysis) return []
  
  const allShortages = []
  props.taxiData.supply_demand_analysis.forEach(analysis => {
    if (analysis.shortage_areas) {
      allShortages.push(...analysis.shortage_areas)
    }
  })
  
  // 按供应比例排序，供应比例越低越紧急
  return allShortages
    .sort((a, b) => a.supply_ratio - b.supply_ratio)
    .slice(0, 6)
}
</script>

<style scoped>
/* 动画效果 */
.animate-spin {
  animation: spin 1s linear infinite;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 进度条动画 */
.transition-all {
  transition: all 0.3s ease;
}
</style> 
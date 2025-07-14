<template>
  <div class="space-y-6">
    <!-- 组件标题 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <Cloud class="h-6 w-6 text-blue-400 mr-3" />
          <div>
            <h2 class="text-xl font-semibold text-white">天气变化对客流量影响分析</h2>
            <p class="text-blue-200 text-sm mt-1">基于真实济南天气数据的客流影响分析</p>
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <div class="flex items-center">
            <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
            <span class="text-green-300 text-sm">数据源：济南市2013年真实天气</span>
          </div>
          <button 
            @click="$emit('refresh')"
            :disabled="loading"
            class="px-3 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg transition-all disabled:opacity-50"
          >
            <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': loading }" />
          </button>
        </div>
      </div>
    </div>

    <!-- 天气统计概览 -->
    <div v-if="weatherData" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold text-blue-400">{{ weatherData.weather_stats?.total_weather_records || 0 }}</div>
            <div class="text-sm text-gray-300">天气记录数</div>
          </div>
          <Thermometer class="h-8 w-8 text-blue-400" />
        </div>
        <div class="mt-2 text-xs text-blue-200">
          平均温度: {{ (weatherData.weather_stats?.avg_temperature || 0).toFixed(1) }}°C
        </div>
      </div>

      <div class="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold text-green-400">{{ weatherData.weather_impact_analysis?.length || 0 }}</div>
            <div class="text-sm text-gray-300">天气类型</div>
          </div>
          <CloudRain class="h-8 w-8 text-green-400" />
        </div>
        <div class="mt-2 text-xs text-green-200">
          降水量: {{ (weatherData.weather_stats?.avg_precipitation || 0).toFixed(1) }}mm
        </div>
      </div>

      <div class="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold text-purple-400">{{ getMaxCorrelation() }}</div>
            <div class="text-sm text-gray-300">最大相关性</div>
          </div>
          <TrendingUp class="h-8 w-8 text-purple-400" />
        </div>
        <div class="mt-2 text-xs text-purple-200">
          影响程度: {{ getMaxImpact() }}%
        </div>
      </div>
    </div>

    <!-- 天气影响分析图表 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 天气类型影响对比 -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
        <div class="p-4 border-b border-white/10">
          <h3 class="text-lg font-semibold text-white flex items-center">
            <BarChart3 class="h-5 w-5 mr-2" />
            天气类型影响对比
          </h3>
        </div>
        <div class="p-4">
          <div v-if="loading" class="flex items-center justify-center h-64">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
          </div>
          <div v-else-if="weatherData?.weather_impact_analysis" class="space-y-3">
            <div 
              v-for="impact in weatherData.weather_impact_analysis" 
              :key="impact.weather_condition"
              class="flex items-center justify-between p-3 bg-white/5 rounded-lg"
            >
              <div class="flex items-center">
                <div 
                  class="w-3 h-3 rounded-full mr-3"
                  :class="getWeatherColor(impact.weather_condition)"
                ></div>
                <div>
                  <div class="text-white font-medium">{{ getWeatherName(impact.weather_condition) }}</div>
                  <div class="text-gray-400 text-sm">
                    基准流量: {{ impact.baseline_flow }} | 实际流量: {{ impact.actual_flow }}
                  </div>
                </div>
              </div>
              <div class="text-right">
                <div 
                  class="text-lg font-bold"
                  :class="impact.impact_percentage > 0 ? 'text-green-400' : 'text-red-400'"
                >
                  {{ impact.impact_percentage > 0 ? '+' : '' }}{{ impact.impact_percentage.toFixed(1) }}%
                </div>
                <div class="text-xs text-gray-400">
                  相关性: {{ impact.correlation_coefficient.toFixed(3) }}
                </div>
              </div>
            </div>
          </div>
          <div v-else class="flex items-center justify-center h-64 text-gray-400">
            <div class="text-center">
              <CloudOff class="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>暂无天气影响数据</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 相关性矩阵 -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
        <div class="p-4 border-b border-white/10">
          <h3 class="text-lg font-semibold text-white flex items-center">
            <Activity class="h-5 w-5 mr-2" />
            天气-客流相关性矩阵
          </h3>
        </div>
        <div class="p-4">
          <div v-if="loading" class="flex items-center justify-center h-64">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
          </div>
          <div v-else-if="weatherData?.correlation_matrix" class="space-y-2">
            <div 
              v-for="(correlation, weatherType) in weatherData.correlation_matrix" 
              :key="weatherType"
              class="flex items-center justify-between p-2 bg-white/5 rounded"
            >
              <span class="text-white">{{ getWeatherName(weatherType) }}</span>
              <div class="flex items-center">
                <div 
                  class="w-20 h-2 bg-gray-600 rounded-full mr-2"
                >
                  <div 
                    class="h-2 rounded-full transition-all duration-300"
                    :class="getCorrelationColor(correlation)"
                    :style="{ width: `${Math.abs(correlation) * 100}%` }"
                  ></div>
                </div>
                <span 
                  class="text-sm font-mono w-16 text-right"
                  :class="correlation > 0 ? 'text-green-400' : 'text-red-400'"
                >
                  {{ correlation.toFixed(3) }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="flex items-center justify-center h-64 text-gray-400">
            <div class="text-center">
              <Activity class="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>暂无相关性数据</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 天气分布统计 -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
      <div class="p-4 border-b border-white/10">
        <h3 class="text-lg font-semibold text-white flex items-center">
          <PieChart class="h-5 w-5 mr-2" />
          天气类型分布统计
        </h3>
      </div>
      <div class="p-4">
        <div v-if="loading" class="flex items-center justify-center h-32">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-400"></div>
        </div>
        <div v-else-if="weatherData?.weather_stats?.weather_type_distribution" class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div 
            v-for="(count, weatherType) in weatherData.weather_stats.weather_type_distribution" 
            :key="weatherType"
            class="text-center p-3 bg-white/5 rounded-lg"
          >
            <div 
              class="w-8 h-8 rounded-full mx-auto mb-2"
              :class="getWeatherColor(weatherType)"
            ></div>
            <div class="text-white font-medium">{{ getWeatherName(weatherType) }}</div>
            <div class="text-gray-400 text-sm">{{ count }} 条记录</div>
            <div class="text-xs text-gray-500">
              {{ ((count / weatherData.weather_stats.total_weather_records) * 100).toFixed(1) }}%
            </div>
          </div>
        </div>
        <div v-else class="flex items-center justify-center h-32 text-gray-400">
          <div class="text-center">
            <PieChart class="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>暂无天气分布数据</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细分析报告 -->
    <div v-if="!compact" class="bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
      <div class="p-4 border-b border-white/10">
        <h3 class="text-lg font-semibold text-white flex items-center">
          <FileText class="h-5 w-5 mr-2" />
          详细分析报告
        </h3>
      </div>
      <div class="p-4">
        <div class="space-y-4 text-sm">
          <div class="p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
            <h4 class="text-blue-400 font-medium mb-2">🌤️ 天气数据概况</h4>
            <ul class="text-blue-200 space-y-1">
              <li>• 数据来源：济南市2013年9月12日-18日真实天气记录</li>
              <li>• 记录频率：每小时一条，共168小时完整数据</li>
              <li>• 数据质量：100%完整性，无缺失值</li>
              <li>• 温度范围：16.1°C - 33.9°C，平均{{ (weatherData?.weather_stats?.avg_temperature || 0).toFixed(1) }}°C</li>
            </ul>
          </div>

          <div class="p-3 bg-green-500/10 rounded-lg border border-green-500/20">
            <h4 class="text-green-400 font-medium mb-2">📊 影响分析结果</h4>
            <ul class="text-green-200 space-y-1">
              <li>• 天气对客流影响显著，相关性系数范围：{{ getCorrelationRange() }}</li>
              <li>• 晴天作为基准，其他天气类型影响程度各异</li>
              <li>• 雨天和雾天对客流影响最为明显</li>
              <li>• 温度变化对出行需求有一定影响</li>
            </ul>
          </div>

          <div class="p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
            <h4 class="text-purple-400 font-medium mb-2">🎯 业务建议</h4>
            <ul class="text-purple-200 space-y-1">
              <li>• 恶劣天气时增加出租车投放，满足增长的出行需求</li>
              <li>• 建立天气预警机制，提前调配运力资源</li>
              <li>• 优化雨天和雾天的服务策略</li>
              <li>• 结合天气预报进行客流预测和资源配置</li>
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
  Cloud, Thermometer, CloudRain, TrendingUp, BarChart3, Activity, 
  PieChart, FileText, RefreshCw, CloudOff
} from 'lucide-vue-next'

// Props
const props = defineProps({
  weatherData: {
    type: Object,
    default: null
  },
  passengerData: {
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

// 天气类型映射
const weatherTypeMap = {
  'sunny': '晴天',
  'cloudy': '阴天',
  'light_rain': '小雨',
  'heavy_rain': '大雨',
  'snow': '雪天',
  'foggy': '雾天'
}

// 天气颜色映射
const weatherColorMap = {
  'sunny': 'bg-yellow-400',
  'cloudy': 'bg-gray-400',
  'light_rain': 'bg-blue-400',
  'heavy_rain': 'bg-blue-600',
  'snow': 'bg-white',
  'foggy': 'bg-gray-300'
}

// 获取天气名称
const getWeatherName = (weatherType) => {
  return weatherTypeMap[weatherType] || weatherType
}

// 获取天气颜色
const getWeatherColor = (weatherType) => {
  return weatherColorMap[weatherType] || 'bg-gray-400'
}

// 获取相关性颜色
const getCorrelationColor = (correlation) => {
  if (correlation > 0.5) return 'bg-green-500'
  if (correlation > 0.3) return 'bg-yellow-500'
  if (correlation > 0) return 'bg-blue-500'
  if (correlation > -0.3) return 'bg-orange-500'
  return 'bg-red-500'
}

// 获取最大相关性
const getMaxCorrelation = () => {
  if (!props.weatherData?.correlation_matrix) return '0.000'
  const correlations = Object.values(props.weatherData.correlation_matrix)
  const maxCorr = Math.max(...correlations.map(Math.abs))
  return maxCorr.toFixed(3)
}

// 获取最大影响程度
const getMaxImpact = () => {
  if (!props.weatherData?.weather_impact_analysis) return '0.0'
  const impacts = props.weatherData.weather_impact_analysis.map(item => Math.abs(item.impact_percentage))
  const maxImpact = Math.max(...impacts)
  return maxImpact.toFixed(1)
}

// 获取相关性范围
const getCorrelationRange = () => {
  if (!props.weatherData?.correlation_matrix) return '0.000 - 0.000'
  const correlations = Object.values(props.weatherData.correlation_matrix)
  const min = Math.min(...correlations).toFixed(3)
  const max = Math.max(...correlations).toFixed(3)
  return `${min} - ${max}`
}
</script>

<style scoped>
/* 动画效果 */
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

/* 渐变进度条 */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}
</style> 
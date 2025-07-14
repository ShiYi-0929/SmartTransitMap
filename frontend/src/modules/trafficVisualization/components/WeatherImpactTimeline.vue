<template>
  <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center">
        <BarChart3 class="h-6 w-6 text-blue-400 mr-2" />
        <h2 class="text-lg font-semibold text-white">天气影响时间轴</h2>
      </div>
      <div class="flex items-center space-x-2">
        <button v-for="(item, idx) in dailyImpacts" :key="item.date"
                @click="$emit('date-change', item.date)"
                :class="['px-3 py-1 rounded', selectedDate === item.date ? 'bg-blue-500 text-white' : 'bg-white/10 text-blue-300']">
          {{ item.date }}
        </button>
      </div>
    </div>
    <div v-if="currentDay" class="w-full">
      <ECharts :option="chartOption" style="height:320px;width:100%" @mouseover="onChartHover" />
      <div v-if="hoverHour !== null" class="mt-4 p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
        <div class="text-blue-400 font-bold mb-1">{{ hoverHour }}:00 - {{ hoverHour+1 }}:00 详情</div>
        <div class="text-sm text-white">载客率：{{ getHourData(hoverHour).impact_factor | percent }}，温度：{{ getHourData(hoverHour).temperature }}°C，降水：{{ getHourData(hoverHour).precipitation }}mm</div>
        <div class="text-xs text-blue-200 mt-1">{{ getHourData(hoverHour).impact_description }}</div>
      </div>
    </div>
    <div v-else class="text-gray-400 text-center py-12">请选择日期查看详细时间轴</div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { BarChart3 } from 'lucide-vue-next'
import * as echarts from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import ECharts from 'vue-echarts'

// 注册echarts组件
if (!echarts.hasInit) {
  echarts.use([LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])
  echarts.hasInit = true
}

const props = defineProps({
  dailyImpacts: { type: Array, required: true },
  selectedDate: { type: String, required: false, default: '' }
})
const emit = defineEmits(['date-change', 'hour-hover'])

const hoverHour = ref(null)

const currentDay = computed(() => props.dailyImpacts.find(d => d.date === props.selectedDate))

const chartOption = computed(() => {
  if (!currentDay.value) return {}
  const hours = currentDay.value.hourly_impacts.map(h => h.hour)
  const impact = currentDay.value.hourly_impacts.map(h => h.impact_factor)
  const temp = currentDay.value.hourly_impacts.map(h => h.temperature)
  const precip = currentDay.value.hourly_impacts.map(h => h.precipitation)
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['载客率', '温度', '降水'] },
    grid: { left: 40, right: 20, bottom: 40, top: 40 },
    xAxis: { type: 'category', data: hours.map(h => `${h}:00`) },
    yAxis: [
      { type: 'value', name: '载客率', min: 0, max: 1, axisLabel: { formatter: v => `${(v*100).toFixed(0)}%` } },
      { type: 'value', name: '温度/降水', min: 0, max: Math.max(...temp, ...precip, 30) }
    ],
    series: [
      { name: '载客率', type: 'line', yAxisIndex: 0, data: impact, smooth: true, symbol: 'circle', lineStyle: { width: 3 } },
      { name: '温度', type: 'bar', yAxisIndex: 1, data: temp, barGap: 0, itemStyle: { color: '#60a5fa' } },
      { name: '降水', type: 'bar', yAxisIndex: 1, data: precip, barGap: '-100%', itemStyle: { color: '#38bdf8' } }
    ]
  }
})

function onChartHover(params) {
  if (params && params.dataIndex !== undefined) {
    hoverHour.value = currentDay.value.hourly_impacts[params.dataIndex].hour
    emit('hour-hover', hoverHour.value)
  }
}

function getHourData(hour) {
  if (!currentDay.value) return {}
  return currentDay.value.hourly_impacts.find(h => h.hour === hour) || {}
}

// 百分比过滤器
function percent(val) {
  return `${(val * 100).toFixed(1)}%`
}
</script>

<style scoped>
.echarts {
  width: 100%;
  height: 320px;
}
</style> 
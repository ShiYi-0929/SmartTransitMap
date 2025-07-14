<template>
  <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
    <div class="flex items-center mb-4">
      <Activity class="h-6 w-6 text-purple-400 mr-2" />
      <h2 class="text-lg font-semibold text-white">影响机制可视化</h2>
      <span v-if="hourlyImpact" class="ml-4 text-blue-300 text-sm">{{ hourlyImpact.hour }}:00 - {{ hourlyImpact.hour+1 }}:00</span>
    </div>
    <div v-if="hourlyImpact">
      <ECharts :option="radarOption" style="height:320px;width:100%" />
      <div class="mt-4 p-4 bg-purple-500/10 rounded-lg border border-purple-500/20">
        <div class="text-purple-400 font-bold mb-1">详细机制说明</div>
        <div class="text-sm text-white">温度：{{ hourlyImpact.temperature }}°C，降水：{{ hourlyImpact.precipitation }}mm，能见度：{{ hourlyImpact.visibility ?? '—' }}km</div>
        <div class="text-xs text-purple-200 mt-1">{{ hourlyImpact.impact_description }}</div>
      </div>
    </div>
    <div v-else class="text-gray-400 text-center py-12">请选择小时查看影响机制</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Activity } from 'lucide-vue-next'
import * as echarts from 'echarts/core'
import { RadarChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import ECharts from 'vue-echarts'

if (!echarts.hasRadarInit) {
  echarts.use([RadarChart, TooltipComponent, LegendComponent, CanvasRenderer])
  echarts.hasRadarInit = true
}

const props = defineProps({
  hourlyImpact: { type: Object, required: false, default: null }
})

const radarOption = computed(() => {
  if (!props.hourlyImpact) return {}
  // 能见度字段兼容
  const visibility = props.hourlyImpact.visibility ?? 10
  return {
    tooltip: {},
    legend: { data: ['当前时段'] },
    radar: {
      indicator: [
        { name: '温度(°C)', max: 40 },
        { name: '降水(mm)', max: 10 },
        { name: '能见度(km)', max: 20 },
        { name: '载客率(%)', max: 1 }
      ],
      radius: 90
    },
    series: [
      {
        name: '影响机制',
        type: 'radar',
        data: [
          {
            value: [props.hourlyImpact.temperature, props.hourlyImpact.precipitation, visibility, props.hourlyImpact.impact_factor],
            name: '当前时段',
            areaStyle: { color: 'rgba(139,92,246,0.3)' },
            lineStyle: { color: '#8b5cf6' },
            symbol: 'circle',
            itemStyle: { color: '#a78bfa' }
          }
        ]
      }
    ]
  }
})
</script>

<style scoped>
.echarts {
  width: 100%;
  height: 320px;
}
</style> 
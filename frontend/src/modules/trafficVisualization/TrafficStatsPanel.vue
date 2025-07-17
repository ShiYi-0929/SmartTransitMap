<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div class="card-tech p-6">
      <h3 class="text-lg font-semibold text-white mb-3 flex items-center">
        <Activity class="h-5 w-5 mr-2 text-green-400" />
        数据概览
      </h3>
      <div class="space-y-2">
        <div class="flex justify-between">
          <span class="text-blue-200">总数据点:</span>
          <span class="text-white font-semibold">{{ totalCount }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-blue-200">时间跨度:</span>
          <span class="text-white font-semibold">{{ timeSpan }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-blue-200">覆盖区域:</span>
          <span class="text-white font-semibold">{{ coverageArea }}</span>
        </div>
      </div>
    </div>
    <div class="card-tech p-6">
      <h3 class="text-lg font-semibold text-white mb-3 flex items-center">
        <Car class="h-5 w-5 mr-2 text-blue-400" />
        车辆信息
      </h3>
      <div class="space-y-2">
        <div class="flex justify-between">
          <span class="text-blue-200">活跃车辆:</span>
          <span class="text-white font-semibold">{{ activeVehicles }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-blue-200">平均速度:</span>
          <span class="text-white font-semibold">{{ averageSpeed }} km/h</span>
        </div>
        <div class="flex justify-between">
          <span class="text-blue-200">总里程:</span>
          <span class="text-white font-semibold">{{ totalDistance }} km</span>
        </div>
      </div>
    </div>
    <div class="card-tech p-6">
      <h3 class="text-lg font-semibold text-white mb-3 flex items-center">
        <TrendingUp class="h-5 w-5 mr-2 text-purple-400" />
        实时状态
      </h3>
      <div class="space-y-2">
        <div class="flex justify-between">
          <span class="text-blue-200">更新时间:</span>
          <span class="text-white font-semibold">{{ lastUpdate }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-blue-200">数据状态:</span>
          <span class="text-green-400 font-semibold">● 正常</span>
        </div>
        <div class="flex justify-between">
          <span class="text-blue-200">连接状态:</span>
          <span class="text-green-400 font-semibold">● 在线</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { Activity, Car, TrendingUp } from 'lucide-vue-next'
const props = defineProps({
  totalCount: Number,
  timeSpan: String,
  coverageArea: String,
  activeVehicles: Number,
  averageSpeed: Number,
  totalDistance: Number,
  lastUpdate: String
})
</script> 
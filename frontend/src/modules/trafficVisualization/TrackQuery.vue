<template>
  <div class="track-query-container">
    <el-card class="track-query-card">
      <div style="margin-bottom: 16px;">
        <el-date-picker v-model="timeRange" type="datetimerange" range-separator="至" start-placeholder="开始时间" end-placeholder="结束时间" />
        <el-input v-model="carId" placeholder="请输入车辆ID" style="width: 200px; margin-left: 12px;"></el-input> <el-button type="primary" @click="queryTrafficDistribution" style="margin-left: 12px;">查询交通分布</el-button>
        <el-button type="primary" @click="queryTrack" style="margin-left: 12px;">查询车辆轨迹</el-button>
      </div>
      <div id="amap" class="map-container"></div>
    </el-card>
  </div>
</template>
<script setup>
import {ref, onMounted} from 'vue'
import axios from 'axios'

const timeRange = ref([])
const carId = ref('') // 新增车辆ID的ref
let map = null
let polylines = []
let markers = []

const initMap = () => {
  map = new window.AMap.Map('amap', {
    center: [117.12, 36.65],
    zoom: 12
  })
}

const clearOverlays = () => {
  polylines.forEach(line => map.remove(line))
  polylines = []
  markers.forEach(marker => map.remove(marker))
  markers = []
}

const queryTrafficDistribution = async () => {
  if (!timeRange.value || timeRange.value.length !== 2) return
  const [start, end] = timeRange.value.map(t => Math.floor(new Date(t).getTime() / 1000))

  // 构造请求参数，如果carId有值则添加
  const params = {start_time: start, end_time: end};
  if (carId.value) {
    params.car_id = carId.value;
  }

  const res = await axios.get('/api/traffic/track', {params: params})

  clearOverlays()

  res.data.forEach(car => {
    car.track.forEach(p => {
      const marker = new window.AMap.Marker({
        position: [p.LON / 1e5, p.LAT / 1e5],
        map: map,
        icon: new window.AMap.Icon({
          size: new window.AMap.Size(12, 12),
          image: '//vdata.amap.com/icons/b18/1.png',
          imageOffset: new window.AMap.Pixel(-9, -3)
        })
      });
      markers.push(marker);
    });
  });
  if (markers.length > 0) {
    map.setFitView();
  }
}

const queryTrack = async () => {
  if (!timeRange.value || timeRange.value.length !== 2) return
  const [start, end] = timeRange.value.map(t => Math.floor(new Date(t).getTime() / 1000))

  // 构造请求参数，如果carId有值则添加
  const params = {start_time: start, end_time: end};
  if (carId.value) {
    params.car_id = carId.value;
  }

  const res = await axios.get('/api/traffic/track', {params: params})

  clearOverlays()

  res.data.forEach(car => {
    if (car.track.length > 1) {
      const path = car.track.map(p => [p.LON / 1e5, p.LAT / 1e5])
      const polyline = new window.AMap.Polyline({
        path,
        strokeColor: randomColor(),
        strokeWeight: 4,
        strokeOpacity: 0.7
      })
      map.add(polyline)
      polylines.push(polyline)

      // 如果只查询一辆车，可以设置中心点和缩放级别
      if (res.data.length === 1) {
        map.setFitView(polyline);
      }
    }
  })
  if (polylines.length > 0 && res.data.length > 1) { // 如果查询多辆车，适应所有轨迹
    map.setFitView();
  }
}

function randomColor() {
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  return colors[Math.floor(Math.random() * colors.length)]
}

onMounted(() => {
  initMap()
})
</script>
<style scoped>
.track-query-container {
  padding: 24px;
}

.track-query-card {
  max-width: 1200px;
  margin: 0 auto;
}

.map-container {
  width: 100%;
  height: 600px;
  margin-top: 16px;
  border-radius: 8px;
  overflow: hidden;
}
</style>
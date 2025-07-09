<template>
  <el-card>
    <h3>交通数据可视化 - 热力图</h3>
    <div style="margin-bottom: 16px;">
      <el-input v-model="selectedDate" placeholder="请输入日期（如0912）" style="width: 200px; margin-right: 12px;"></el-input>
      <el-button type="primary" @click="loadHeatmap">加载某天热力图</el-button>

      <el-divider direction="vertical"></el-divider>

      <el-date-picker
        v-model="selectedTimePoint"
        type="datetime"
        placeholder="选择时间点"
        style="width: 220px; margin-left: 12px;"
      />
      <el-button type="primary" @click="loadHeatmapByTimePoint" style="margin-left: 12px;">搜索15分钟内上客热力图</el-button>
    </div>
    <div id="heatmap-map" class="map-container"></div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { getTrafficVisualization } from '../api/traffic' // 从 traffic.js 导入API

const selectedDate = ref('0912') // 默认显示日期
const selectedTimePoint = ref(null) // 新增时间点选择器
let map = null
let heatmap = null // 热力图层

const initMap = () => {
  map = new window.AMap.Map('heatmap-map', {
    center: [117.12, 36.65], // 济南市中心示例坐标
    zoom: 12
  });

  // 加载热力图插件
  window.AMap.plugin(['AMap.Heatmap'], function(){
      heatmap = new window.AMap.Heatmap(map, {
          radius: 25, // 热力图半径
          opacity: [0, 0.8] // 透明度范围
      });
  });
}

const loadHeatmap = async () => {
  if (!selectedDate.value) return;

  try {
    // 调用后端接口获取某天的热力图数据
    const res = await axios.get('/api/traffic/visualization', { params: { date: selectedDate.value } });
    const data = res.data.heatmap_data;
    updateHeatmap(data);
  } catch (error) {
    console.error('加载某天热力图数据失败:', error);
  }
}

const loadHeatmapByTimePoint = async () => {
  if (!selectedTimePoint.value) {
    alert('请选择一个时间点！');
    return;
  }

  // 计算15分钟的时间范围
  const timeMs = new Date(selectedTimePoint.value).getTime();
  const startMs = timeMs - (15 * 60 * 1000) / 2; // 15分钟的一半，即前后7.5分钟
  const endMs = timeMs + (15 * 60 * 1000) / 2;

  // 将毫秒转换为秒（UTC时间戳）
  const start_utc = Math.floor(startMs / 1000);
  const end_utc = Math.floor(endMs / 1000);

  try {
    // 调用后端接口获取指定时间段内的热力图数据
    const res = await axios.get('/api/traffic/visualization', { params: { start_time: start_utc, end_time: end_utc } });
    const data = res.data.heatmap_data;
    updateHeatmap(data);
  } catch (error) {
    console.error('加载15分钟内上客热力图数据失败:', error);
  }
}

const updateHeatmap = (data) => {
    if (heatmap && data) {
      heatmap.setDataSet({
          data: data,
          max: getMaxWeight(data) // 计算最大权重，用于热力图颜色渲染
      });
      if (data.length > 0) {
        map.setFitView(); // 适应数据点
      } else {
        alert('该时间段内无数据。');
      }
    }
}

// 辅助函数：计算数据中的最大权重
const getMaxWeight = (data) => {
    let max = 0;
    data.forEach(item => {
        if (item.count > max) {
            max = item.count;
        }
    });
    return max === 0 ? 1 : max; // 避免max为0导致热力图不显示
}

onMounted(() => {
  initMap();
  loadHeatmap(); // 页面加载后自动显示某天热力图
})
</script>

<style scoped>
.map-container { width: 100%; height: 600px; margin-top: 16px; border-radius: 8px; overflow: hidden; }
</style>
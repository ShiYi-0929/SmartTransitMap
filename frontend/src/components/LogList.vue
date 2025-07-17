<template>
  <el-card class="main-card">
    <template v-if="currentView === 'monitor'">
      <el-list>
        <el-list-item v-for="(log, idx) in logs" :key="idx">{{ log }}</el-list-item>
      </el-list>

      <div class="monitor-cards-container">
        <div class="monitor-section">
          <h3>人脸识别监控概览</h3>
          <FaceRecognitionMonitor />
        </div>

        <div class="monitor-section">
          <h3>路面监测监控概览</h3>
          <RoadDamageDetectionMonitor @view-detailed-logs="setCurrentView('roadLogList')" />
        </div>
      </div>
    </template>

    <template v-else-if="currentView === 'roadLogList'">
      <RoadLogList @close-road-log-list="setCurrentView('monitor')" />
    </template>
  </el-card>
</template>

<script setup>
import { ref } from 'vue';
import { getLogs } from '../api/log'; // 确保路径正确

import FaceRecognitionMonitor from '../modules/Log/FaceLog/FaceRecognitionMonitor.vue';
import RoadDamageDetectionMonitor from '../modules/Log/RoadLog/RoadDamageDetectionMonitor.vue';
import RoadLogList from '../modules/Log/RoadLog/RoadLogList.vue'; // Correct path to RoadLogList

const logs = ref([]);
const currentView = ref('monitor'); // 'monitor' for the default view, 'roadLogList' for the detailed list

function setCurrentView(view) {
  currentView.value = view;
}

async function loadLogs() {
  try {
    const res = await getLogs();
    logs.value = res.data.logs;
  } catch (error) {
    console.error('Failed to load logs:', error);
  }
}

loadLogs();
</script>

<style scoped>
/* 调整最外层el-card的宽度和内边距，减少整体留白 */
.main-card {
  width: fit-content; /* 让卡片宽度刚好适应内容，从而减少多余的横向留白 */
  height: fit-content;
  min-height: 2000px;
  max-height: 2000px;
  min-width: 2000px; /* 最小宽度确保两张卡片和间距能够排开 */
  max-width: 2000px; /* 限制最大宽度，防止在超宽屏幕上拉伸过大 */
  margin: 10px auto; /* 居中显示，并提供少量上下外边距 */
  padding: 10px; /* 适当的内边距 */
  box-sizing: border-box; /* 确保内边距和边框不会增加总宽度 */
  background-color: #052146;
}

/* 新增的 Flex 容器样式 */
.monitor-cards-container {
  display: flex; /* 启用 Flexbox */
  justify-content: center; /* 使内部两个卡片整体居中 */
  align-items: flex-start; /* 使所有项目顶部对齐 */
  gap: 120px; /* **增加两个子组件卡片之间的间距，从20px调整为30px** */
  margin-top: 30px; /* 给整个监控区域留出一些顶部间距 */
  flex-wrap: wrap; /* 允许项目换行，以防屏幕宽度不足时溢出 */
  /* padding: 0 20px; /* **可选：增加横向内边距，将卡片从容器边缘稍微推开** */
}

.monitor-section {
  flex: 0 0 auto; /* 阻止flex项目伸缩，让其保持内容宽度 */
  width: 700px; /* 固定每个监控组件的宽度，与截图中的卡片宽度保持一致 */
  /* 调整上边距，减少与上方标题的距离 */
  margin-top: 0;
  padding-top: 0; /* 移除内边距，因为子组件自身有padding */
  border-top: none; /* 移除分隔线，如果不需要 */
}

.monitor-section h3 {
  margin-bottom: 15px; /* 调整标题与下方组件的间距 */
  color: #367c9d;
  text-align: center; /* 标题居中 */
}

/* 针对el-list的样式，使其看起来更像日志列表 */
.el-list {
  background-color: #406ba2;
  border-radius: 4px;
  padding: 10px;
  margin-top: 15px;
  max-height: 500px; /* 限制日志列表的高度，出现滚动条 */
  overflow-y: auto;
  border: 1px solid #455d90;
}

.el-list-item {
  padding: 8px 0;
  border-bottom: 1px dashed #8fa3d2;
  font-size: 14px;
  color: #040b19;
}
.el-list-item:last-child {
  border-bottom: none;
}
</style>
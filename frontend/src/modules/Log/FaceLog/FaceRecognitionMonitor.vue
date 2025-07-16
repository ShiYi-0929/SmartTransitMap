<template>
  <div class="face-recognition-monitor-card">
    <div class="header">
      <el-icon class="header-icon"><UserFilled /></el-icon>
      <h2 class="title">人脸识别监控</h2>
    </div>

    <div class="metrics-panel">
      <div class="metric-item">
        <div class="value">{{ todayRecognitionCount }}</div>
        <div class="label">今日识别</div>
      </div>
      <div class="metric-item accuracy">
        <div class="value">{{ recognitionAccuracy }}%</div>
        <div class="label">识别准确率</div>
      </div>
      <div class="metric-item anomaly">
        <div class="value">{{ anomalyDetectionCount }}</div>
        <div class="label">异常检测</div>
      </div>
    </div>

    <div class="message-list">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message-item', `level-${message.level}`]"
      >
        <span class="time">{{ message.time }}</span>
        <span class="description">{{ message.description }}</span>
        <el-tag :type="getTagType(message.level)" size="small">{{
          getLevelText(message.level)
        }}</el-tag>
      </div>
    </div>

    <div class="actions">
      <el-button type="primary" @click="handleAlarmPlayback"
        >告警回放</el-button
      >
      <el-button @click="handleViewDetailedLogs">详细日志</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { UserFilled } from '@element-plus/icons-vue'; // 引入Element Plus图标

// 响应式数据
const todayRecognitionCount = ref(143);
const recognitionAccuracy = ref(98.6);
const anomalyDetectionCount = ref(3);

const messages = ref([
  { id: 1, time: '14:32', description: '检测到未授权人员尝试进入', level: 'high' },
  { id: 2, time: '13:45', description: '识别质量较低，建议重新录入', level: 'medium' },
  { id: 3, time: '12:15', description: '用户 A001 成功通过验证', level: 'low' },
]);

// 根据告警级别返回 Element Plus Tag 的类型
const getTagType = (level) => {
  switch (level) {
    case 'high':
      return 'danger';
    case 'medium':
      return 'warning';
    case 'low':
      return 'success';
    default:
      return 'info';
  }
};

// 根据告警级别返回对应的文字
const getLevelText = (level) => {
  switch (level) {
    case 'high':
      return '高';
    case 'medium':
      return '中';
    case 'low':
      return '低';
    default:
      return '未知';
  }
};

// 按钮点击事件处理
const handleAlarmPlayback = () => {
  console.log('点击了告警回放');
  // 实际应用中会跳转到告警回放页面或打开相关模态框
  // 例如：router.push('/alarm-playback');
};

const handleViewDetailedLogs = () => {
  console.log('点击了详细日志');
  // 实际应用中会跳转到详细日志页面
  // 例如：router.push('/log');
};

// 模拟数据更新（可选，用于演示实时性）
onMounted(() => {
  // setInterval(() => {
  //   todayRecognitionCount.value = Math.floor(Math.random() * 200) + 100;
  //   recognitionAccuracy.value = (Math.random() * (99.9 - 90) + 90).toFixed(1);
  //   anomalyDetectionCount.value = Math.floor(Math.random() * 5) + 1;

  //   const newMessages = [
  //     { id: Date.now(), time: '此刻', description: '模拟新事件', level: ['high', 'medium', 'low'][Math.floor(Math.random() * 3)] },
  //     ...messages.value.slice(0, 2)
  //   ];
  //   messages.value = newMessages;
  // }, 5000);
});
</script>

<style lang="scss" scoped>
.face-recognition-monitor-card {
  background-color: #1a1a2e; /* 深色背景 */
  border-radius: 8px;
  padding: 20px;
  color: #e0e0e0; /* 浅色文字 */
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  width: 100%; // 可以根据需要调整宽度
  max-width: 900px; // 限制最大宽度以符合截图布局
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);

  .header {
    display: flex;
    align-items: center;
    margin-bottom: 25px;

    .header-icon {
      font-size: 28px;
      color: #00bcd4; /* 蓝色系图标 */
      margin-right: 10px;
    }

    .title {
      font-size: 22px;
      font-weight: bold;
      color: #ffffff;
      margin: 0;
    }
  }

  .metrics-panel {
    display: flex;
    justify-content: space-around;
    margin-bottom: 25px;
    background-color: #2a2a4a; /* 比主背景稍浅 */
    border-radius: 6px;
    padding: 15px 10px;

    .metric-item {
      text-align: center;
      flex: 1; /* 均匀分配空间 */

      .value {
        font-size: 32px;
        font-weight: bold;
        color: #f0f0f0; /* 默认值颜色 */
        margin-bottom: 5px;
      }

      .label {
        font-size: 14px;
        color: #aaaaaa;
      }

      &.accuracy .value {
        color: #4caf50; /* 绿色 */
      }

      &.anomaly .value {
        color: #ff5722; /* 橙红色 */
      }
    }
  }

  .message-list {
    margin-bottom: 25px;

    .message-item {
      display: flex;
      align-items: center;
      padding: 12px 15px;
      margin-bottom: 8px;
      border-radius: 5px;
      background-color: #2a2a4a; /* 消息背景 */
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);

      &.level-high {
        border-left: 5px solid #ff5722; /* 高级别告警条颜色 */
      }
      &.level-medium {
        border-left: 5px solid #ffc107; /* 中级别告警条颜色 */
      }
      &.level-low {
        border-left: 5px solid #4caf50; /* 低级别告警条颜色 */
      }

      .time {
        font-size: 14px;
        color: #b0b0b0;
        margin-right: 15px;
        min-width: 50px; /* 固定时间宽度 */
      }

      .description {
        flex-grow: 1;
        font-size: 15px;
        color: #e0e0e0;
        margin-right: 10px;
      }

      .el-tag {
        font-weight: bold;
      }
    }
  }

  .actions {
    display: flex;
    justify-content: center;
    gap: 20px; /* 按钮之间的间距 */

    .el-button {
      padding: 10px 25px;
      border-radius: 5px;
      font-size: 16px;
      // 自定义按钮颜色以匹配截图风格
      &.el-button--primary {
        background-color: #007bff; /* 蓝色主按钮 */
        border-color: #007bff;
        &:hover {
          background-color: #0056b3;
          border-color: #0056b3;
        }
      }
      &:not(.el-button--primary) {
        background-color: #4a4a6e; /* 次要按钮 */
        border-color: #4a4a6e;
        color: #ffffff;
        &:hover {
          background-color: #5a5a7e;
          border-color: #5a5a7e;
        }
      }
    }
  }
}
</style>
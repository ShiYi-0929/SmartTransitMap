<template>
  <div class="road-damage-monitor-card">
    <div class="header">
      <el-icon class="header-icon"><RoadMap /></el-icon>
      <h2 class="title">路面病害检测</h2>
    </div>

    <div class="metrics-panel">
      <div class="metric-item">
        <div class="value">{{ todayDetectionCount }}</div>
        <div class="label">今日检测</div>
      </div>
      <div class="metric-item discovered">
        <div class="value">{{ discoveredDamageCount }}</div>
        <div class="label">发现病害</div>
      </div>
      <div class="metric-item pending">
        <div class="value">{{ pendingCount }}</div>
        <div class="label">待处理</div>
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
import { ref } from 'vue';
// import { RoadMap } from '@element-plus/icons-vue'; // 确保已安装并注册 Element Plus icons

// 声明组件可以触发的自定义事件
const emit = defineEmits(['view-detailed-logs']);

// 响应式数据
const todayDetectionCount = ref(28);
const discoveredDamageCount = ref(6);
const pendingCount = ref(7);

const messages = ref([
  { id: 1, time: '11:01', description: '性能监控告警', level: 'medium' },
  { id: 2, time: '15:20', description: '检测到严重坑洼，影响行车安全', level: 'high' },
  { id: 3, time: '14:55', description: '发现纵向裂缝，长度约15米', level: 'medium' },
  { id: 4, time: '13:30', description: '路面龟裂面积超过阈值', level: 'medium' },
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

// 根据告警级别返回对应文本
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
};

const handleViewDetailedLogs = () => {
  console.log('点击了详细日志');
  // 触发自定义事件，通知父组件切换视图
  emit('view-detailed-logs');
};
</script>

<style lang="scss" scoped>
/* 保持原有的样式 */
.road-damage-monitor-card {
  background-color: #1a1a2e;
  border-radius: 8px;
  padding: 20px;
  color: #e0e0e0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  width: 100%;
  max-width: 1000px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);

  .header {
    display: flex;
    align-items: center;
    margin-bottom: 25px;

    .header-icon {
      font-size: 28px;
      color: #7b68ee;
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
    background-color: #2a2a4a;
    border-radius: 6px;
    padding: 15px 10px;

    .metric-item {
      text-align: center;
      flex: 1;

      .value {
        font-size: 32px;
        font-weight: bold;
        color: #f0f0f0;
        margin-bottom: 5px;
      }

      .label {
        font-size: 14px;
        color: #aaaaaa;
      }

      &.discovered .value {
        color: #ffa500;
      }

      &.pending .value {
        color: #1e90ff;
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
      background-color: #2a2a4a;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);

      &.level-high {
        border-left: 5px solid #ff5722;
      }
      &.level-medium {
        border-left: 5px solid #ffc107;
      }
      &.level-low {
        border-left: 5px solid #4caf50;
      }

      .time {
        font-size: 14px;
        color: #b0b0b0;
        margin-right: 15px;
        min-width: 50px;
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
    gap: 20px;

    .el-button {
      padding: 10px 25px;
      border-radius: 5px;
      font-size: 16px;
      &.el-button--primary {
        background-color: #007bff;
        border-color: #007bff;
        &:hover {
          background-color: #0056b3;
          border-color: #0056b3;
        }
      }
      &:not(.el-button--primary) {
        background-color: #4a4a6e;
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
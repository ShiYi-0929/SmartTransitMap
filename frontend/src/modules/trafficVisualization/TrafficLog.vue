<template>
  <div class="traffic-log-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">交通监控日志</h2>
      <p class="page-description">详细完善的监控日志功能，实时记录交通系统运行状态、关键事件和异常情况</p>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="logLevel" placeholder="日志级别" @change="filterLogs">
            <el-option label="全部级别" value="all" />
            <el-option label="错误" value="error" />
            <el-option label="警告" value="warning" />
            <el-option label="信息" value="info" />
            <el-option label="调试" value="debug" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="logType" placeholder="日志类型" @change="filterLogs">
            <el-option label="全部类型" value="all" />
            <el-option label="系统日志" value="system" />
            <el-option label="交通日志" value="traffic" />
            <el-option label="异常日志" value="anomaly" />
            <el-option label="性能日志" value="performance" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            @change="filterLogs"
          />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="refreshLogs" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon error">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.errorCount }}</div>
                <div class="stat-label">错误日志</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon warning">
                <el-icon><InfoFilled /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.warningCount }}</div>
                <div class="stat-label">警告日志</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon info">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.infoCount }}</div>
                <div class="stat-label">信息日志</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <el-icon><List /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.totalCount }}</div>
                <div class="stat-label">总日志数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 日志表格 -->
    <div class="log-table-container">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>日志详情</span>
            <div class="header-actions">
              <el-button size="small" @click="exportLogs">
                <el-icon><Download /></el-icon>
                导出日志
              </el-button>
              <el-button size="small" @click="clearLogs" type="danger">
                <el-icon><Delete /></el-icon>
                清空日志
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table
          :data="logs"
          style="width: 100%"
          :loading="loading"
          stripe
          @row-click="showLogDetail"
        >
          <el-table-column prop="timestamp" label="时间" width="180" sortable>
            <template #default="{ row }">
              <span class="timestamp">{{ formatTime(row.timestamp) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="level" label="级别" width="100">
            <template #default="{ row }">
              <el-tag :type="getLevelType(row.level)" size="small">
                {{ row.level.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="type" label="类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getTypeType(row.type)" size="small">
                {{ getLogTypeDisplay(row) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="module" label="模块" width="150" />
          
          <el-table-column prop="message" label="消息" min-width="300">
            <template #default="{ row }">
              <div class="log-message">
                <span class="message-text">{{ row.message }}</span>
                <el-button 
                  v-if="row.details" 
                  type="text" 
                  size="small"
                  @click.stop="showLogDetail(row)"
                >
                  详情
                </el-button>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="source" label="来源" width="120" />
          
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="text" size="small" @click.stop="showLogDetail(row)">
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalLogs"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="日志详情"
      width="60%"
      :before-close="closeDetailDialog"
    >
      <div v-if="selectedLog" class="log-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="时间">
            {{ formatTime(selectedLog.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="级别">
            <el-tag :type="getLevelType(selectedLog.level)">
              {{ selectedLog.level.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="getTypeType(selectedLog.type)">
              {{ getLogTypeDisplay(selectedLog) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="模块">
            {{ selectedLog.module }}
          </el-descriptions-item>
          <el-descriptions-item label="来源">
            {{ selectedLog.source }}
          </el-descriptions-item>
          <el-descriptions-item label="用户">
            {{ selectedLog.user || '系统' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="detail-section">
          <h4>消息内容</h4>
          <div class="message-content">{{ selectedLog.message }}</div>
        </div>
        
        <div v-if="selectedLog.details" class="detail-section">
          <h4>详细信息</h4>
          <pre class="details-content">{{ JSON.stringify(selectedLog.details, null, 2) }}</pre>
        </div>
        
        <div v-if="selectedLog.stack" class="detail-section">
          <h4>堆栈信息</h4>
          <pre class="stack-content">{{ selectedLog.stack }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- 实时日志监控 -->
    <!-- 删除实时监控相关内容 -->
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  Warning, 
  InfoFilled, 
  Document, 
  List, 
  Download, 
  Delete 
} from '@element-plus/icons-vue'
import { getTrafficLogs, getTrafficLogStats, clearTrafficLogs, addTrafficLog, sendTrafficAlert } from '@/api/traffic'

// 响应式数据
const loading = ref(false)
const logLevel = ref('all')
const logType = ref('all')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const totalLogs = ref(0)
const detailDialogVisible = ref(false)
const selectedLog = ref(null)

// 日志数据
const logs = ref([])

// 统计数据
const stats = reactive({
  errorCount: 0,
  warningCount: 0,
  infoCount: 0,
  totalCount: 0
})

// 计算属性 - 已移除，改为后端过滤

// 方法
const fetchLogs = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (logLevel.value !== 'all') {
      params.level = logLevel.value
    }
    
    if (logType.value !== 'all') {
      params.log_type = logType.value
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_time = dateRange.value[0]
      params.end_time = dateRange.value[1]
    }
    
    const response = await getTrafficLogs(params)
    logs.value = response.data.logs || []
    totalLogs.value = response.data.total || 0
    updateStats()
    ElMessage.success('日志数据加载成功')
  } catch (error) {
    console.error('获取日志失败:', error)
    ElMessage.error('获取日志数据失败')
  } finally {
    loading.value = false
  }
}

const filterLogs = () => {
  currentPage.value = 1
  fetchLogs()
}

const updateStats = async () => {
  try {
    const response = await getTrafficLogStats()
    const data = response.data
    stats.errorCount = data.error_count || 0
    stats.warningCount = data.warning_count || 0
    stats.infoCount = data.info_count || 0
    stats.totalCount = data.total_count || 0
  } catch (error) {
    console.error('获取统计信息失败:', error)
    // 如果API失败，使用本地计算
    stats.errorCount = logs.value.filter(log => log.level === 'error').length
    stats.warningCount = logs.value.filter(log => log.level === 'warning').length
    stats.infoCount = logs.value.filter(log => log.level === 'info').length
    stats.totalCount = logs.value.length
  }
}

const refreshLogs = () => {
  fetchLogs()
}

const showLogDetail = (log) => {
  selectedLog.value = log
  detailDialogVisible.value = true
}

const closeDetailDialog = () => {
  detailDialogVisible.value = false
  selectedLog.value = null
}

const exportLogs = () => {
  const csvContent = generateCSV(logs.value)
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `traffic_logs_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
  ElMessage.success('交通日志导出成功')
}

const generateCSV = (logs) => {
  const headers = ['时间', '级别', '类型', '模块', '消息', '来源', '用户']
  const rows = logs.map(log => [
    formatTime(log.timestamp),
    log.level,
    getLogTypeDisplay(log),
    log.module,
    log.message,
    log.source,
    log.user || '系统'
  ])
  
  return [headers, ...rows]
    .map(row => row.map(cell => `"${cell}"`).join(','))
    .join('\n')
}

const clearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await clearTrafficLogs()
    logs.value = []
    await updateStats()
    ElMessage.success('交通日志已清空')
  } catch (error) {
    // 用户取消操作
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchLogs()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchLogs()
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

const getLevelType = (level) => {
  const types = {
    error: 'danger',
    warning: 'warning',
    info: 'info',
    debug: ''
  }
  return types[level] || ''
}

const getTypeType = (type) => {
  const types = {
    system: 'primary',
    traffic: 'success',
    anomaly: 'warning',
    performance: 'info'
  }
  return types[type] || ''
}

const getTypeLabel = (type) => {
  const labels = {
    system: '系统日志',
    traffic: '交通日志',
    anomaly: '异常日志',
    performance: '性能日志'
  }
  return labels[type] || type
}

// 辅助函数：根据 details.view_type 返回更友好的类型名称
function getLogTypeDisplay(log) {
  if (log.details && log.details.view_type === 'heatmap') return '热力图分析';
  if (log.details && log.details.view_type === 'distribution') return '分布分析';
  if (log.details && log.details.view_type === 'trajectory') return '轨迹分析';
  return getTypeLabel(log.type);
}

// 生命周期
onMounted(() => {
  fetchLogs()
})

onUnmounted(() => {
  // stopRealtimeMonitor() // 删除实时监控相关内容
})
</script>

<style scoped>
.traffic-log-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.page-description {
  color: #7f8c8d;
  margin: 0;
}

.control-panel {
  margin-bottom: 24px;
}

.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.stat-icon.error {
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
}

.stat-icon.warning {
  background: linear-gradient(135deg, #feca57, #ff9ff3);
}

.stat-icon.info {
  background: linear-gradient(135deg, #48dbfb, #0abde3);
}

.stat-icon.total {
  background: linear-gradient(135deg, #54a0ff, #2e86de);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-top: 4px;
}

.log-table-container {
  margin-bottom: 24px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.timestamp {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #7f8c8d;
}

.log-message {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.message-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.log-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-top: 20px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 16px;
}

.message-content {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  border-left: 4px solid #007bff;
}

.details-content,
.stack-content {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

/* 删除实时监控相关样式 */
/*
.realtime-monitor {
  margin-top: 24px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.monitor-content {
  max-height: 300px;
  overflow-y: auto;
}

.realtime-logs {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.realtime-log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 4px;
  background: #f8f9fa;
  border-left: 4px solid #007bff;
}

.realtime-log-item.level-error {
  background: #fff5f5;
  border-left-color: #ff6b6b;
}

.realtime-log-item.level-warning {
  background: #fffbf0;
  border-left-color: #feca57;
}

.realtime-log-item.level-info {
  background: #f0f9ff;
  border-left-color: #48dbfb;
}

.realtime-time {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #7f8c8d;
  min-width: 150px;
}

.realtime-message {
  flex: 1;
  font-size: 14px;
}

.monitor-disabled {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}
*/
</style> 
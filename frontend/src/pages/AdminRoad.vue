<template>
  <div class="admin-road-page">
    <el-card class="main-card">
      <el-tabs v-model="tab" type="border-card">
        <!-- 检测分析 -->
        <el-tab-pane label="检测分析" name="detect">
          <el-row :gutter="16" class="mb-4">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">今日检测</div>
                <div class="stat-value">{{ stats.today_records }}</div>
                <div class="stat-sub">较昨日 +2</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">待维修</div>
                <div class="stat-value">{{ stats.pending_tasks }}</div>
                <div class="stat-sub">需要处理</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">维修中</div>
                <div class="stat-value">{{ stats.repairing_tasks || 0 }}</div>
                <div class="stat-sub">进行中</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">已完成</div>
                <div class="stat-value">{{ stats.completed_tasks || 0 }}</div>
                <div class="stat-sub">本月完成</div>
              </el-card>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-card>
                <div class="chart-title">病害类型统计</div>
                <v-chart :option="pieOption" autoresize style="height:260px" />
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <div class="chart-title">每日检测趋势</div>
                <v-chart :option="lineOption" autoresize style="height:260px" />
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
        <!-- 历史记录 -->
        <el-tab-pane label="历史记录" name="history">
          <div class="section-title">操作日志</div>
          <el-table :data="logs" style="width: 100%">
            <el-table-column prop="operator" label="操作人员" />
            <el-table-column prop="action" label="操作类型" />
            <el-table-column prop="detail" label="操作对象" />
            <el-table-column prop="time" label="操作时间" />
          </el-table>
        </el-tab-pane>
        <!-- 维修任务管理 -->
        <el-tab-pane label="维修任务" name="tasks">
          <div class="section-title">维修任务管理</div>
          <el-table :data="tasks" style="width: 100%">
            <el-table-column prop="id" label="任务ID" />
            <el-table-column prop="damage_type" label="病害类型" />
            <el-table-column prop="severity" label="严重程度" />
            <el-table-column prop="location" label="位置" />
            <el-table-column prop="reporter" label="上报人" />
            <el-table-column prop="upload_time" label="上报时间" />
            <el-table-column prop="status" label="状态" />
            <el-table-column prop="assignee" label="负责人" />
            <el-table-column label="操作">
              <template #default="{ row }">
                <el-button v-if="row.status==='未维修'" type="primary" size="small" @click="openAssignDialog(row)">分配任务</el-button>
                <el-button v-else type="default" size="small" @click="viewTask(row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    <!-- 分配任务弹窗 -->
    <el-dialog v-model="assignDialogVisible" title="分配任务" width="400px">
      <el-form :model="assignForm">
        <el-form-item label="选择负责人">
          <el-select v-model="assignForm.assignee" placeholder="请选择认证用户">
            <el-option v-for="user in users" :key="user.userID" :label="user.username" :value="user.userID" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible=false">取消</el-button>
        <el-button type="primary" @click="assignTask">确定分配</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from '@/utils/request'
import { ElMessage } from 'element-plus'
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import { PieChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([PieChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const tab = ref('detect')
const stats = reactive({ today_records: 0, pending_tasks: 0, repairing_tasks: 0, completed_tasks: 0, damage_types: {}, trend_dates: [], trend_values: [] })
const logs = ref([])
const tasks = ref([])
const users = ref([])
const assignDialogVisible = ref(false)
const assignForm = reactive({ taskId: null, assignee: null })

// 图表数据
const pieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { top: 'bottom' },
  series: [{
    name: '病害类型',
    type: 'pie',
    radius: '60%',
    data: Object.entries(stats.damage_types).map(([name, value]) => ({ name, value })),
    label: { formatter: '{b} {d}%' }
  }]
}))
const lineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: stats.trend_dates || [] },
  yAxis: { type: 'value' },
  series: [{
    name: '检测数',
    type: 'line',
    data: stats.trend_values || [],
    smooth: true
  }]
}))

// 数据加载
async function fetchStats() {
  const res = await axios.get('/road/statistics')
  Object.assign(stats, res.data)
}
async function fetchLogs() {
  const res = await axios.get('/road/logs')
  logs.value = res.data.map(log => ({
    ...log,
    operator: getUserName(log.user_id)
  }))
}
async function fetchTasks() {
  const res = await axios.get('/road/repair-tasks')
  // 需要补充病害类型、严重程度、位置、上报人等信息
  const recordRes = await axios.get('/road/records')
  const recordMap = {}
  recordRes.data.forEach(r => { recordMap[r.id] = r })
  tasks.value = res.data.map(task => {
    const rec = recordMap[task.record_id] || {}
    let damage_type = '-', severity = '-', location = '-', reporter = '-', upload_time = '-'
    try {
      const arr = JSON.parse(rec.detect_result)
      if (arr && arr.length > 0) {
        damage_type = arr[0].class || '-'
        severity = arr[0].severity || '-'
        location = arr[0].location || '-'
      }
    } catch {}
    reporter = getUserName(rec.user_id)
    upload_time = rec.upload_time
    return {
      ...task,
      damage_type, severity, location, reporter, upload_time,
      assignee: getUserName(task.assigned_to)
    }
  })
}
async function fetchUsers() {
  // 获取所有认证用户
  const res = await axios.get('/user/list')
  users.value = res.data.filter(u => u.user_class === '认证用户')
}
function getUserName(userId) {
  const user = users.value.find(u => u.userID === userId)
  return user ? user.username : (userId === null ? '未分配' : '管理员')
}

// 分配任务
function openAssignDialog(row) {
  assignForm.taskId = row.id
  assignForm.assignee = null
  assignDialogVisible.value = true
}
async function assignTask() {
  if (!assignForm.assignee) {
    ElMessage.error('请选择负责人')
    return
  }
  await axios.post('/road/repair-tasks/assign', { record_id: tasks.value.find(t => t.id === assignForm.taskId).record_id, assigned_to: assignForm.assignee })
  ElMessage.success('分配成功')
  assignDialogVisible.value = false
  fetchTasks()
}
function viewTask(row) {
  ElMessage.info('查看详情功能可后续扩展')
}

onMounted(() => {
  fetchUsers()
  fetchStats()
  fetchLogs()
  fetchTasks()
})
</script>

<script>
export default {
  components: { VChart }
}
</script>

<style scoped>
.admin-road-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 32px 0 80px 0;
}
.main-card {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 24px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.section-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 16px;
}
.stat-card {
  text-align: center;
  padding: 16px 0;
  border-radius: 12px;
  background: #fafbfc;
}
.stat-title {
  color: #888;
  font-size: 15px;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}
.stat-sub {
  color: #aaa;
  font-size: 13px;
}
.chart-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
}
</style> 
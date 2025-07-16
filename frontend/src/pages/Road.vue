<template>
  <div class="road-page">
    <el-card class="main-card">
      <el-tabs v-model="tab" type="border-card">
        <el-tab-pane label="检测分析" name="detect">
          <div class="section-title">智能识别路面病害，提供精准检测与分析</div>
          <div class="section-sub">支持 JPG, PNG, MP4 (最大50MB)</div>
          <el-upload
            class="upload-block"
            drag
            :show-file-list="false"
            :before-upload="beforeUpload"
            :on-change="onFileChange"
            :auto-upload="false"
            ref="uploadRef"
          >
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">拖拽图片或视频到此处或点击上传</div>
            <el-button type="primary">选择图片/视频文件</el-button>
            <div slot="tip" class="el-upload__tip">未选择文件</div>
          </el-upload>
          <div v-if="selectedFile" class="mt-4">
            <el-button type="success" :loading="loading" @click="submitDetect">开始检测</el-button>
            <el-button type="text" @click="clearFile">移除</el-button>
            <div class="file-name">已选择: {{ selectedFile.name }}</div>
          </div>
          <el-card v-if="detectResult" class="mt-6">
            <div class="font-bold mb-2">检测结果</div>
            <div v-if="detectResult.length === 0" class="text-gray-500">未检测到病害</div>
            <div v-else>
              <el-table :data="detectResult" style="width: 100%">
                <el-table-column prop="class" label="类型" />
                <el-table-column prop="confidence" label="置信度" />
                <el-table-column prop="bbox" label="位置" />
              </el-table>
            </div>
          </el-card>
        </el-tab-pane>
        <el-tab-pane label="历史记录" name="history">
          <div class="section-title">检测历史记录</div>
          <el-input v-model="search" placeholder="搜索文件名或检测结果..." class="mb-4 search-input" />
          <el-table :data="filteredRecords" style="width: 100%">
            <el-table-column prop="file_path" label="文件名" :formatter="fileNameFormatter" />
            <el-table-column prop="upload_time" label="检测时间" />
            <el-table-column prop="detect_result" label="检测结果" :formatter="resultFormatter" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="维修任务" name="tasks">
          <div class="section-title">维修任务</div>
          <el-row :gutter="20">
            <el-col v-for="task in tasks" :key="task.id" :span="12">
              <el-card class="mb-4">
                <div class="flex justify-between items-center mb-2">
                  <div class="font-bold text-blue-600">{{ task.id }}</div>
                  <el-tag :type="task.status==='未维修'?'warning':task.status==='维修中'?'info':'success'">
                    {{ task.status }}
                  </el-tag>
                </div>
                <div class="text-gray-500 mb-1">指派时间: {{ task.start_time || '未开始' }}</div>
                <div class="text-gray-500 mb-1">识别病害数: {{ getTaskDamageCount(task) }}</div>
                <el-button v-if="task.status==='未维修'" type="primary" @click="startRepair(task)">维修</el-button>
                <el-button v-if="task.status==='维修中'" type="success" @click="finishRepair(task)">结束维修</el-button>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { detectRoadDamage } from '@/api/road'
import axios from '@/utils/request'
import { ElMessage } from 'element-plus'
import logoUrl from '@/assets/logo.png'

const tab = ref('detect')
const selectedFile = ref(null)
const loading = ref(false)
const detectResult = ref(null)
const search = ref('')
const records = ref([])
const tasks = ref([])
const uploadRef = ref(null)

function beforeUpload(file) {
  // 限制大小和类型
  const isValid = (file.type.startsWith('image/') || file.type.startsWith('video/')) && file.size < 50 * 1024 * 1024
  if (!isValid) {
    ElMessage.error('仅支持图片/视频且小于50MB')
  }
  return isValid
}
function onFileChange(file) {
  selectedFile.value = file.raw
  detectResult.value = null
}
function clearFile() {
  selectedFile.value = null
  detectResult.value = null
  if (uploadRef.value) uploadRef.value.clearFiles()
}
async function submitDetect() {
  if (!selectedFile.value) return
  loading.value = true
  try {
    const res = await detectRoadDamage(selectedFile.value)
    detectResult.value = Array.isArray(res.data.result) ? res.data.result : []
    ElMessage.success('检测完成')
  } catch (e) {
    ElMessage.error('检测失败')
  } finally {
    loading.value = false
  }
}
const filteredRecords = computed(() => {
  if (!search.value) return records.value
  return records.value.filter(r =>
    (r.file_path && r.file_path.includes(search.value)) ||
    (r.detect_result && r.detect_result.includes(search.value))
  )
})
function fileNameFormatter(row) {
  return row.file_path ? row.file_path.split('/').pop() : ''
}
function resultFormatter(row) {
  try {
    const arr = JSON.parse(row.detect_result)
    if (!arr || arr.length === 0) return '未检测到病害'
    return arr.map(d => d.class + ' (' + (d.confidence*100).toFixed(1) + '%)').join(', ')
  } catch {
    return row.detect_result
  }
}
function getTaskDamageCount(task) {
  const rec = records.value.find(r => r.id === task.record_id)
  if (!rec) return '-'
  try {
    const arr = JSON.parse(rec.detect_result)
    return arr.length
  } catch {
    return '-'
  }
}
async function startRepair(task) {
  await updateTaskStatus(task.id, '维修中')
  ElMessage.success('维修中')
  await fetchTasks()
}
async function finishRepair(task) {
  await updateTaskStatus(task.id, '已结束')
  ElMessage.success('维修已结束')
  await fetchTasks()
}
async function updateTaskStatus(taskId, status) {
  await axios.post(`/road/repair-tasks/${taskId}/update-status`, { status })
}
async function fetchRecords() {
  const res = await axios.get('/road/records')
  records.value = res.data
}
async function fetchTasks() {
  const res = await axios.get('/road/repair-tasks')
  tasks.value = res.data
}
onMounted(() => {
  fetchRecords()
  fetchTasks()
})
</script>

<style scoped>
.road-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 32px 0 80px 0;
}
.main-card {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px 24px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.section-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 8px;
}
.section-sub {
  color: #888;
  margin-bottom: 24px;
}
.upload-block {
  margin-bottom: 12px;
}
.file-name {
  color: #666;
  margin-top: 8px;
}
.search-input {
  max-width: 300px;
  margin-bottom: 16px;
}
.footer {
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100vw;
  text-align: center;
  color: #888;
  font-size: 14px;
  background: transparent;
  padding-bottom: 12px;
}
.footer-logo {
  height: 32px;
  vertical-align: middle;
  margin-right: 8px;
}
</style> 

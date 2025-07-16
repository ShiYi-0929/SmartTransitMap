<template>
  <el-card class="log-container">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="系统操作日志" name="system">
        <div class="header">
          <h3>系统操作日志</h3>
          <div class="header-right">
            <el-input
              v-model="searchQuery"
              placeholder="按用户/ID/类型搜索"
              clearable
              class="search-input"
            />
            <el-button 
              v-if="isAdmin"
              type="danger" 
              @click="handleBulkDelete" 
              :disabled="multipleSelection.length === 0"
            >
              批量删除
            </el-button>
            <el-button @click="() => loadSystemLogs()" :loading="loading">刷新</el-button>
          </div>
        </div>
        <el-table :data="systemLogs" stripe style="width: 100%" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="55" v-if="isAdmin" />
          <el-table-column prop="timestamp" label="时间" width="180"></el-table-column>
          <el-table-column prop="username" label="操作用户" width="120"></el-table-column>
          <el-table-column prop="userID" label="用户ID" width="100"></el-table-column>
          <el-table-column prop="logtype" label="日志类型" width="180"></el-table-column>
          <el-table-column prop="description" label="描述"></el-table-column>
          <el-table-column v-if="isAdmin" label="媒体证据" width="120">
            <template #default="scope">
              <img v-if="scope.row.screenshot_url" :src="scope.row.screenshot_url" class="thumb" @click="previewMedia(scope.row.screenshot_url, 'image')"/>
              <el-icon v-if="scope.row.video_url" @click="previewMedia(scope.row.video_url, 'video')" class="media-icon"><VideoCamera /></el-icon>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" v-if="isAdmin">
            <template #default="scope">
              <el-button size="small" @click="openEdit(scope.row)">编辑</el-button>
              <el-button type="danger" size="small" @click="handleDelete(scope.row.id)" style="margin-left:6px;">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="日志告警" name="alert">
        <p>此功能待开发...</p>
      </el-tab-pane>
    </el-tabs>

    <!-- 媒体预览对话框 -->
    <el-dialog v-model="dialogVisible" :title="previewType === 'image' ? '截图预览' : '录屏回放'" width="60%">
      <img v-if="previewType === 'image'" :src="mediaUrl" style="width: 100%;" />
      <video v-if="previewType === 'video'" :src="mediaUrl" controls autoplay style="width: 100%;"></video>
    </el-dialog>

    <!-- 编辑描述对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑日志描述" width="30%">
      <el-input type="textarea" v-model="editDescription" rows="4" placeholder="请输入描述" />
      <template #footer>
        <el-button @click="editDialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { getLogs, deleteLog, updateLog } from '../api/log';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Picture, VideoCamera } from '@element-plus/icons-vue';

const activeTab = ref('system');
const systemLogs = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
const mediaUrl = ref('');
const previewType = ref('image');
const multipleSelection = ref([]); // 新增：用于存储多选的行
const searchQuery = ref(''); // 新增：搜索查询
let debounceTimer = null; // 新增：防抖计时器

const userRole = computed(() => localStorage.getItem('user-class')?.trim() || '');
const isAdmin = computed(() => userRole.value === '管理员');

async function loadSystemLogs(query = '') {
  loading.value = true;
  try {
    const data = await getLogs(query);
    systemLogs.value = data;
  } catch (error) {
    ElMessage.error('加载系统日志失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
}

watch(searchQuery, (newQuery) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    loadSystemLogs(newQuery);
  }, 300);
});

function previewMedia(url, type) {
  mediaUrl.value = url;
  previewType.value = type;
  dialogVisible.value = true;
}

async function handleDelete(logId) {
  try {
    await ElMessageBox.confirm('此操作将永久删除该日志及其关联的媒体文件，是否继续？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });

    await deleteLog(logId);
    ElMessage.success('日志删除成功');
    loadSystemLogs();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
      console.error(error);
    }
  }
}

function handleSelectionChange(val) {
  multipleSelection.value = val;
}

async function handleBulkDelete() {
  if (multipleSelection.value.length === 0) {
    ElMessage.warning('请至少选择一条日志进行删除');
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${multipleSelection.value.length} 条日志吗？此操作不可恢复。`,
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    const deletePromises = multipleSelection.value.map(log => deleteLog(log.id));
    await Promise.all(deletePromises);

    ElMessage.success('批量删除成功');
    loadSystemLogs();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除时发生错误');
      console.error(error);
    }
  }
}

const editDialogVisible = ref(false);
const editDescription = ref('');
const editingId = ref(null);

function openEdit(row){
  editingId.value = row.id;
  editDescription.value = row.description || '';
  editDialogVisible.value = true;
}
async function submitEdit(){
  try{
     await updateLog(editingId.value, editDescription.value);
     ElMessage.success('更新成功');
     editDialogVisible.value=false;
     loadSystemLogs(searchQuery.value);
  }catch(e){
     ElMessage.error('更新失败');
  }
}

onMounted(() => {
  loadSystemLogs();
});
</script>

<style scoped>
.log-container {
  margin: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.search-input {
  width: 250px;
}
.media-icon {
  font-size: 20px;
  cursor: pointer;
  margin-right: 10px;
}
.media-icon:hover {
  color: #409EFF;
}
.thumb{width:60px;height:40px;object-fit:cover;cursor:pointer;margin-right:6px;}
</style>
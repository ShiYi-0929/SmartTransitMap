<template>
  <div class="approval-container-wrapper">
    <div class="approval-container">
      <h1 class="title">权限升级申请批复</h1>

      <div class="tab-header">
        <button
          :class="{ active: activeTab === 'pending' }"
          @click="activeTab = 'pending'"
        >
          待处理 ({{ filteredPending.length }})
        </button>
        <button
          :class="{ active: activeTab === 'processed' }"
          @click="activeTab = 'processed'"
        >
          已处理 ({{ filteredProcessed.length }})
        </button>
      </div>

      <div class="search-bar-wrapper">
        <div class="search-bar">
          <input type="text" v-model="searchTerm" placeholder="按用户ID或用户名搜索..." />
        </div>
        <button
          v-if="activeTab === 'processed' && filteredProcessed.length > 0"
          class="btn clear-all"
          @click="handleClearAll"
        >
          清空已处理列表
        </button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'pending'" class="application-list">
          <div v-if="isLoading" class="loading">加载中...</div>
          <div v-else-if="filteredPending.length === 0" class="empty-state">
            没有待处理的申请。
          </div>
          <div v-else class="list-item" v-for="app in filteredPending" :key="app.applyID">
            <div class="item-info">
              <p><strong>申请人:</strong> {{ app.username }}</p>
              <p><strong>用户ID:</strong> {{ app.userID }}</p>
            </div>
            <div class="item-actions">
              <button class="btn approve" @click="handleProcess(app.applyID, true)">
                批准
              </button>
              <button class="btn reject" @click="handleProcess(app.applyID, false)">
                拒绝
              </button>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'processed'" class="application-list">
          <div v-if="isLoading" class="loading">加载中...</div>
          <div v-else-if="filteredProcessed.length === 0" class="empty-state">
            没有已处理的申请。
          </div>
          <div
            v-else
            class="list-item"
            v-for="app in filteredProcessed"
            :key="app.applyID"
          >
            <div class="item-info">
              <p><strong>申请人:</strong> {{ app.username }}</p>
              <p><strong>用户ID:</strong> {{ app.userID }}</p>
            </div>
            <div class="item-status-actions">
              <span :class="getStatusClass(app.result)">{{
                getStatusText(app.result)
              }}</span>
              <button class="btn delete" @click="handleDeleteApplication(app.applyID)">
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import {
  getPendingApplications,
  getProcessedApplications,
  processApplication,
  deleteApplication,
  clearProcessedApplications,
} from "@/api/admin";
import { ElNotification, ElMessageBox } from "element-plus";
import { useMainStore } from '@/store';

const store = useMainStore();
const activeTab = ref("pending");
const searchTerm = ref("");
const pendingList = ref([]);
const processedList = ref([]);
const isLoading = ref(false);

const fetchApplications = async () => {
  isLoading.value = true;
  try {
    const [pendingRes, processedRes] = await Promise.all([
      getPendingApplications(),
      getProcessedApplications(),
    ]);
    pendingList.value = pendingRes; // Use the response directly
    processedList.value = processedRes; // Use the response directly
  } catch (error) {
    console.error("获取申请列表失败:", error);
    ElNotification({
      title: "错误",
      message: "加载申请列表失败，请稍后重试。",
      type: "error",
    });
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchApplications);

const filteredPending = computed(() =>
  pendingList.value.filter(
    (app) =>
      app.username.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      String(app.userID).includes(searchTerm.value)
  )
);

const filteredProcessed = computed(
  () =>
    processedList.value
      .filter(
        (app) =>
          app.username.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          String(app.userID).includes(searchTerm.value)
      )
      .sort((a, b) => b.applyID - a.applyID) // 按申请ID降序排序
);

const handleProcess = async (applyId, isApproved) => {
  try {
    await processApplication(applyId, isApproved);
    ElNotification({
      title: "成功",
      message: `申请 #${applyId} 已成功${isApproved ? "批准" : "拒绝"}。`,
      type: "success",
    });
    // Refresh lists and update badge count
    await fetchApplications();
    await store.fetchPendingApplicationsCount();
  } catch (error) {
    console.error("处理申请失败:", error);
    const errorMsg = error.response?.data?.detail || "操作失败，请稍后重试。";
    ElNotification({
      title: "错误",
      message: errorMsg,
      type: "error",
    });
  }
};

const getStatusText = (result) => {
  if (result === 1) return "已批准";
  if (result === 2) return "已拒绝";
  return "状态未知";
};

const getStatusClass = (result) => {
  if (result === 1) return "status-approved";
  if (result === 2) return "status-rejected";
  return "";
};

const handleDeleteApplication = async (applyId) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除申请 #${applyId} 吗？此操作无法撤销。`,
      "警告",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await deleteApplication(applyId);
    ElNotification({
      title: "成功",
      message: `申请 #${applyId} 已被删除。`,
      type: "success",
    });
    await fetchApplications();
    await store.fetchPendingApplicationsCount();
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除申请失败:", error);
      const errorMsg = error.response?.data?.detail || "删除失败，请稍后重试。";
      ElNotification({
        title: "错误",
        message: errorMsg,
        type: "error",
      });
    }
  }
};

const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm(
      "确定要清空所有已处理的申请记录吗？此操作无法撤销。",
      "警告",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    const response = await clearProcessedApplications();
    ElNotification({
      title: "成功",
      message: response.message || "已处理记录已清空。",
      type: "success",
    });
    await fetchApplications();
    await store.fetchPendingApplicationsCount();
  } catch (error) {
    if (error !== "cancel") {
      console.error("清空失败:", error);
      const errorMsg = error.response?.data?.detail || "操作失败，请稍后重试。";
      ElNotification({
        title: "错误",
        message: errorMsg,
        type: "error",
      });
    }
  }
};
</script>

<style scoped>
.approval-container-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5 url("@/assets/bg5.png") no-repeat center center;
  background-size: cover;
  position: relative;
}

.approval-container-wrapper::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.approval-container {
  max-width: 1200px;
  width: 100%; /* Ensure it expands to the max-width */
  margin: 2rem auto;
  padding: 2rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-family: "Helvetica Neue", Arial, sans-serif;
  z-index: 2;
  position: relative;
}

.title {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 1rem;
}

.tab-header button {
  padding: 10px 20px;
  border: none;
  background-color: transparent;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  position: relative;
  top: 1px;
}

.tab-header button.active {
  border-bottom: 3px solid #409eff;
  color: #409eff;
  font-weight: bold;
}

.search-bar-wrapper {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: center;
}

.search-bar {
  flex-grow: 1;
  margin-bottom: 0;
}

.search-bar input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}

.application-list {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 10px; /* for scrollbar */
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 6px;
  margin-bottom: 1rem;
  background-color: #f9fafb;
  transition: box-shadow 0.2s;
}

.list-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.item-info p {
  margin: 0;
  color: #555;
}

.item-info p strong {
  color: #333;
}

.item-actions .btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  margin-left: 10px;
}

.btn.approve {
  background-color: #67c23a;
}
.btn.approve:hover {
  background-color: #85d861;
}

.btn.reject {
  background-color: #f56c6c;
}
.btn.reject:hover {
  background-color: #f78989;
}

.item-status-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.item-status span {
  font-weight: bold;
  padding: 5px 10px;
  border-radius: 4px;
  color: #fff;
}

.status-approved {
  background-color: #67c23a;
  color: #fff;
}

.status-rejected {
  background-color: #f56c6c;
  color: #fff;
}

.btn.delete {
  background-color: #e6a23c;
  padding: 6px 12px;
  font-size: 13px;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn.delete:hover {
  background-color: #ebb563;
}

.btn.clear-all {
  padding: 12px 15px;
  background-color: #6c9ef5;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  white-space: nowrap;
}
.btn.clear-all:hover {
  background-color: #f78989;
}

.loading,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #888;
  font-size: 18px;
}
</style>

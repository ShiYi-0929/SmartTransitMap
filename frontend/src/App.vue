<template>
  <el-container style="height: 100vh">
    <!-- 根据路由判断是否显示侧边栏 -->
    <el-aside v-if="showSidebar" width="200px" :class="themeClass">
      <el-menu
        :default-active="$route.path"
        :background-color="themeColors.backgroundColor"
        :text-color="themeColors.textColor"
        :active-text-color="themeColors.activeTextColor"
        style="height: 100%; border-right: none"
        @select="handleSelect"
      >
        <el-menu-item index="/home">首页</el-menu-item>

        <!-- 用户管理对所有登录用户可见 -->
        <el-menu-item index="/user-management">用户管理</el-menu-item>

        <!-- 用户认证对非管理员用户可见 -->
        <el-menu-item v-if="!isAdmin" index="/face"> 用户认证 </el-menu-item>

        <!-- 人脸数据管理，仅管理员可见 -->
        <el-menu-item v-if="isAdmin" index="/face">人脸数据管理</el-menu-item>

        <!-- 以下菜单项仅对管理员和认证用户可见 -->
        <template v-if="!isNormalUser">
          <el-menu-item index="/road">路面检测</el-menu-item>
          <el-menu-item index="/traffic">交通数据</el-menu-item>
          <el-menu-item index="/log">日志告警</el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container direction="vertical">
      <el-main :style="mainStyle">
        <router-view />
      </el-main>
      <el-footer style="height: auto">
        <AuthFooter />
      </el-footer>
    </el-container>
  </el-container>

  <!-- 全局认证状态通知弹窗 -->
  <el-dialog
    v-model="statusModal.visible"
    :title="statusModal.title"
    width="30%"
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <span>{{ statusModal.content }}</span>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="handleModalConfirm">
          {{ statusModal.buttonText }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import bg6 from "@/assets/bg6.png"; // 引入 bg6 图片
import AuthFooter from "@/components/AuthFooter.vue";
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useMainStore } from "@/store";
import { getUserStatus } from "@/api/user"; // 引入获取状态的API
import { cleanupFaceData } from "@/api/face"; // 引入清理API

const router = useRouter();
const route = useRoute();
const store = useMainStore();

// --- 认证状态轮询 ---
const statusModal = ref({
  visible: false,
  title: "",
  content: "",
  buttonText: "确认",
  action: null, // 'logout' or 'close'
});
let pollInterval = null;
let demotionCheckInterval = null; // 新增：用于降级检测的独立轮询器

const pollStatus = async () => {
  // 注意：此函数现在假设调用它的逻辑是正确的，
  // 因此移除了顶部的检查，以简化代码。
  console.log("正在轮询用户认证状态...");

  try {
    const response = await getUserStatus();
    console.log("轮询API响应:", response);

    const { face_registration_status, user_class: remoteUserClass } = response;
    const localUserClass = localStorage.getItem("user-class")?.trim();

    // 场景1：检测到用户被降级
    // 条件：本地记录是认证用户，但远程已经是普通用户
    if (localUserClass === "认证用户" && remoteUserClass === "普通用户") {
      console.log("检测到用户降级！触发降级流程。");
      store.setDemotionStatus(true);
      stopPolling(); // 停止轮询
      store.setPollingState(false);
      return; // 优先处理降级，不再继续下面的逻辑
    }

    // 场景2：普通用户等待认证结果
    if (
      face_registration_status === "approved" ||
      face_registration_status === "rejected"
    ) {
      // 检测到最终状态，更新通知状态并停止轮询
      console.log(
        `检测到最终状态: '${face_registration_status}'，更新通知状态并停止轮询。`
      );
      store.setFaceAuthNotificationStatus(face_registration_status);
      stopPolling();
      store.setPollingState(false);
    }
  } catch (error) {
    console.error("轮询用户状态失败:", error);
  }
};

// 新增：专门用于检测认证用户是否被降级的函数
const checkDemotionStatus = async () => {
  console.log("正在轮询用户降级状态...");
  const localUserClass = localStorage.getItem("user-class")?.trim();

  // 如果本地不是认证用户了，或者没有token，就停止轮询
  if (localUserClass !== "认证用户" || !localStorage.getItem("token")) {
    if (demotionCheckInterval) {
      clearInterval(demotionCheckInterval);
      demotionCheckInterval = null;
      console.log("降级状态轮询停止（条件不满足）。");
    }
    return;
  }

  try {
    const response = await getUserStatus();
    if (response.user_class === "普通用户") {
      console.log("检测到用户降级！触发降级流程。");
      store.setDemotionStatus(true);
      if (demotionCheckInterval) {
        clearInterval(demotionCheckInterval);
        demotionCheckInterval = null; // 清理定时器
      }
    }
  } catch (error) {
    console.error("轮询用户降级状态失败:", error);
    // 出错时停止，避免无限循环错误请求
    if (demotionCheckInterval) {
      clearInterval(demotionCheckInterval);
      demotionCheckInterval = null;
    }
  }
};

const handleModalConfirm = async () => {
  // 此函数现在仅用于批准后的登出确认，保留以防万一，但主要逻辑已移至路由守卫
  const action = statusModal.value.action;
  statusModal.value.visible = false;

  if (action === "logout") {
    store.logout();
  }
};

// 停止轮询的函数
const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
    console.log("认证状态轮询已停止。");
  }
};

// 启动轮询的函数
const startPolling = () => {
  if (pollInterval) return; // 防止重复启动

  const token = localStorage.getItem("token");
  const userClass = localStorage.getItem("user-class")?.trim();

  // 双重检查，确保只在需要时轮询
  if (token && userClass === "普通用户" && store.isPollingActive) {
    console.log("启动认证状态轮询...");
    pollStatus(); // 立即执行一次
    pollInterval = setInterval(pollStatus, 10000); // 每10秒轮询一次
  }
};

// 监听 store 中的轮询开关
watch(
  () => store.isPollingActive,
  (isActive) => {
    if (isActive) {
      startPolling();
    } else {
      stopPolling();
    }
  },
  { immediate: true } // 立即执行，以处理刷新后或初始加载时的状态
);

onMounted(() => {
  // 启动降级状态轮询
  const currentUserClass = localStorage.getItem("user-class")?.trim();
  if (currentUserClass === "认证用户") {
    startDemotionCheck();
  }
});

onUnmounted(() => {
  stopPolling();
  if (demotionCheckInterval) {
    clearInterval(demotionCheckInterval);
    demotionCheckInterval = null;
  }
});

// 新增：启动降级轮询的函数
const startDemotionCheck = () => {
  if (demotionCheckInterval) return; // 防止重复启动
  console.log("启动认证用户降级状态轮询...");
  checkDemotionStatus(); // 立即检查一次
  demotionCheckInterval = setInterval(checkDemotionStatus, 30000); // 每30秒检查一次
};

// --- 布局和路由管理 ---
const showSidebar = computed(() => {
  // 在登录页 (路径为 '/') 不显示侧边栏
  return route.path !== "/";
});

// 为特定管理员页面应用特殊背景
const mainStyle = computed(() => {
  const isAdmin = userRole.value === "管理员";
  const adminRoutes = ["/user-management", "/approval"];
  if (isAdmin && adminRoutes.includes(route.path)) {
    return {
      backgroundImage: `url(${bg6})`,
      backgroundSize: "cover",
      backgroundPosition: "center center",
    };
  }
  return {};
});

// --- 角色和主题管理 ---
const userRole = computed(() => {
  // 通过引用 route.path，我们确保了在每次路由变化时，
  // 这个计算属性都会重新评估，从而读取最新的 localStorage 值。
  // eslint-disable-next-line no-unused-vars
  const _ = route.path;
  return localStorage.getItem("user-class")?.trim() || "普通用户";
});

// 监听用户角色变化，动态启停降级轮询
watch(userRole, (newRole, oldRole) => {
  if (newRole === "认证用户" && oldRole !== "认证用户") {
    startDemotionCheck();
  } else if (newRole !== "认证用户" && demotionCheckInterval) {
    clearInterval(demotionCheckInterval);
    demotionCheckInterval = null;
    console.log("用户不再是认证用户，停止降级轮询。");
  }
});

const isAdmin = computed(() => userRole.value === "管理员");
const isNormalUser = computed(() => userRole.value === "普通用户");

const themeClass = computed(() => (isAdmin.value ? "admin-theme" : "user-theme"));

const themeColors = computed(() => {
  if (isAdmin.value) {
    return {
      backgroundColor: "#4a0e0e", // 深红色背景
      textColor: "#ffffff",
      activeTextColor: "#f5c518", // 金色高亮
    };
  }
  return {
    backgroundColor: "#001f3f", // 默认深蓝色背景
    textColor: "#ffffff",
    activeTextColor: "#ffd04b",
  };
});

// --- 导航逻辑 ---
const handleSelect = (index) => {
  // el-menu 的 select 事件会传递 index，我们直接用它导航
  if (route.path !== index) {
    router.push(index);
  }
};

// 废弃旧的 handleNavigate，逻辑简化并移入 handleSelect
</script>

<style>
/* 移除 .restricted-menu-item 样式，因为菜单项已经通过 v-if 控制 */

/* 主题化样式 */
.el-aside.admin-theme .el-menu {
  /* 可以在这里添加更多管理员主题的特定样式，如果需要的话 */
  /* 例如，改变非激活状态下的菜单项悬浮颜色 */
}
.el-aside.admin-theme .el-menu-item:hover {
  background-color: #631212 !important; /* 深红色悬浮背景 */
}
</style>

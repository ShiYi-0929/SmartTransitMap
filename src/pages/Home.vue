<template>
  <div class="home-container">
    <div class="main-content">
      <h1 class="title">智能交通与路面病害检测平台系统 欢迎您的使用</h1>
      <div class="button-grid">
        <!-- 用户管理按钮 -->
        <div class="button-wrapper">
          <button class="styled-button" @click="$router.push('/user-management')">
            <font-awesome-icon icon="user-cog" class="icon" />
            用户管理
          </button>
          <span v-if="pendingCount > 0" class="badge">{{ pendingCount }}</span>
        </div>

        <!-- 用户认证按钮 -->
        <button class="styled-button" @click="handleAuthClick">
          <font-awesome-icon icon="user-shield" class="icon" />
          <span>用户认证</span>
        </button>

        <!-- 路面检测按钮 -->
        <button class="styled-button" @click="$router.push('/road')">
          <font-awesome-icon icon="road" />
          <span>路面检测</span>
        </button>

        <!-- 交通数据按钮 -->
        <button class="styled-button" @click="$router.push('/traffic')">
          <font-awesome-icon icon="chart-bar" />
          <span>交通数据</span>
        </button>

        <!-- 日志按钮 -->
        <button class="styled-button" @click="$router.push('/log')">
          <font-awesome-icon icon="list" />
          <span>日志记录</span>
        </button>

        <!-- 退出登录按钮 -->
        <button class="styled-button logout-btn" @click="logout">
          <font-awesome-icon icon="sign-out-alt" />
          <span>退出登录</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from "vue";
import { useMainStore } from "@/store";
import { useRouter } from "vue-router";
import { ElNotification } from "element-plus";

const store = useMainStore();
const router = useRouter();

const pendingCount = computed(() => store.pendingApplicationsCount);

onMounted(() => {
  store.fetchPendingApplicationsCount();
});

const handleAuthClick = () => {
  const userClass = localStorage.getItem("user-class");
  // 使用 trim() 移除潜在的空格, 并检查中文角色
  if (userClass && (userClass.trim() === "认证用户" || userClass.trim() === "管理员")) {
    ElNotification({
      title: "提示",
      message: "您已是认证用户，无需重复认证！",
      type: "info",
    });
  } else {
    router.push("/face");
  }
};

const logout = () => {
  localStorage.removeItem("user-token");
  localStorage.removeItem("user-class");
  store.setPendingApplicationsCount(0); // Clear badge on logout
  router.push("/");
};
</script>

<style scoped>
/* General Container Styling */
.home-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5 url("@/assets/bg5.png") no-repeat center center;
  background-size: cover;
  padding: 2rem;
  position: relative; /* 添加相对定位 */
}

/* 添加遮罩 */
.home-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.main-content {
  text-align: center;
  background-color: rgba(255, 255, 255, 0.95);
  padding: 40px 50px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 1000px;
  z-index: 2; /* 确保内容显示在遮罩之上 */
}

.title {
  font-size: 32px;
  color: #333;
  margin-bottom: 40px;
}

/* Grid layout for buttons */
.button-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 修改为一行三个按钮 */
  gap: 2rem;
}

/* Wrapper for buttons that need badges */
.button-wrapper {
  position: relative;
}

/* General button styling */
.styled-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 150px; /* Uniform height */
  padding: 20px;
  border-radius: 10px;
  background-color: white;
  color: #007bff;
  font-size: 18px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid #e0e0e0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.styled-button .icon,
.styled-button .fa-icon,
.styled-button svg {
  /* More specific selectors */
  font-size: 36px;
  margin-bottom: 15px;
}

.styled-button:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #007bff;
}

/* Badge styling */
.badge {
  position: absolute;
  top: -10px;
  right: -10px;
  background-color: #dc3545;
  color: white;
  border-radius: 50%;
  padding: 5px;
  font-size: 14px;
  font-weight: bold;
  border: 2px solid white;
  min-width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-sizing: border-box;
}

/* Logout button specific styling */
.logout-btn {
  color: #dc3545;
}

.logout-btn:hover {
  border-color: #dc3545;
  background-color: #f8d7da;
}
</style>

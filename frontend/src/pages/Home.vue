<template>
  <div class="home-container" :class="themeClass" :style="backgroundStyle">
    <div class="main-content">
      <h1 class="title">智能交通与路面病害检测平台系统 欢迎您的使用</h1>
      <div class="button-grid">
        <!-- 用户管理按钮 - 所有用户可见 -->
        <div class="button-wrapper">
          <button
            class="styled-button"
            @click="$router.push('/user-management')"
          >
            <font-awesome-icon icon="user-cog" class="icon" />
            用户管理
          </button>
          <span v-if="pendingCount > 0 && isAdmin" class="badge">{{ pendingCount }}</span>
        </div>

        <!-- 用户认证按钮 - 对非管理员用户可见 -->
        <button v-if="!isAdmin" class="styled-button" @click="handleAuthClick">
          <font-awesome-icon icon="user-shield" class="icon" />
          <span>用户认证</span>
        </button>
        
        <!-- 人脸数据管理按钮 - 仅对管理员可见 -->
        <button v-if="isAdmin" class="styled-button" @click="$router.push('/face')">
          <font-awesome-icon icon="database" class="icon" />
          <span>人脸数据管理</span>
        </button>

        <!-- 路面检测按钮 - 非普通用户可见 -->
        <button
          v-if="!isNormalUser"
          class="styled-button"
          @click="handleNavigation('/road')"
        >
          <font-awesome-icon icon="road" />
          <span>路面检测</span>
        </button>

        <!-- 交通数据按钮 - 非普通用户可见 -->
        <button
          v-if="!isNormalUser"
          class="styled-button"
          @click="handleNavigation('/traffic')"
        >
          <font-awesome-icon icon="chart-bar" />
          <span>交通数据</span>
        </button>

        <!-- 日志按钮 - 非普通用户可见 -->
        <button
          v-if="!isNormalUser"
          class="styled-button"
          @click="handleNavigation('/log')"
        >
          <font-awesome-icon icon="list" />
          <span>日志记录</span>
        </button>

        <!-- 退出登录按钮 - 所有用户可见 -->
        <button class="styled-button logout-btn" @click="logout">
          <font-awesome-icon icon="sign-out-alt" />
          <span>退出登录</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useMainStore } from "@/store";
import { ElNotification } from "element-plus";
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
// 引入背景图片
import bg5 from '@/assets/bg5.png';
import bg6 from '@/assets/bg6.png';

const store = useMainStore();
const router = useRouter();

const pendingCount = computed(() => store.pendingApplicationsCount);
const userRole = computed(() => localStorage.getItem('user-class')?.trim() || '普通用户');

const isAdmin = computed(() => userRole.value === '管理员');
const isAuthenticatedUser = computed(() => userRole.value === '认证用户');
const isNormalUser = computed(() => userRole.value === '普通用户');

const themeClass = computed(() => {
  if (isAdmin.value) return 'admin-theme';
  return 'user-theme'; // 认证和普通用户用蓝色系
});

// 动态背景样式
const backgroundStyle = computed(() => {
  const imageUrl = isAdmin.value ? bg6 : bg5;
  return {
    backgroundImage: `url(${imageUrl})`
  };
});

onMounted(() => {
  if (isAdmin.value) {
    store.fetchPendingApplicationsCount();
  }
});

const handleAuthClick = () => {
  if (isAuthenticatedUser.value || isAdmin.value) {
    ElNotification({
      title: "提示",
      message: "您已是认证用户或管理员，无需重复认证！",
      type: "info",
    });
  } else {
    router.push("/face");
  }
};

const handleNavigation = (path) => {
  // 由于普通用户看不到受限按钮，此处的权限检查逻辑可以简化或移除
  // 但为保险起见，暂时保留
  if (isNormalUser.value && ['/road', '/traffic', '/log'].includes(path)) {
    ElNotification({
      title: '权限不足',
      message: '此功能需要认证用户权限，请先完成用户认证。',
      type: 'warning',
    });
  } else {
    router.push(path);
  }
};

const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user-class");
  store.setUser(null);
  store.setPendingApplicationsCount(0);
  router.push("/");
  ElNotification({
    title: '已退出',
    message: '您已成功退出登录。',
    type: 'success'
  });
};
</script>

<style scoped>
/* General Container Styling */
.home-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  /* 移除静态背景图片设置，改为通过 :style 动态绑定 */
  background-color: #f0f2f5;
  background-repeat: no-repeat;
  background-position: center center;
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
  /* 根据按钮数量动态调整列数 */
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
  color: #007bff; /* 默认蓝色 */
  font-size: 18px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid #e0e0e0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

/* 移除 .restricted 相关的样式，因为按钮已通过 v-if 隐藏 */

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
  border-color: #007bff; /* 默认蓝色悬浮边框 */
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
  color: #dc3545; /* 登出按钮保持红色 */
}

.logout-btn:hover {
  border-color: #dc3545;
}

/* --- 主题样式 --- */

/* 管理员红色主题 */
.admin-theme .styled-button:not(.logout-btn) {
  color: #c72c41; /* 主要红色 */
}

.admin-theme .styled-button:not(.logout-btn):hover {
  border-color: #c72c41;
}

.admin-theme .badge {
  background-color: #007bff; /* 管理员界面的角标可以换成蓝色，以示区别 */
}

/* 用户蓝色主题 (基本是默认样式，但可以保留以备将来扩展) */
.user-theme .styled-button {
  /* 默认已经是蓝色系，无需额外规则 */
}
</style>

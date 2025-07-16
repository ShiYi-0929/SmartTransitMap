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
            :disabled="isInteractionLocked"
          >
            <font-awesome-icon icon="user-cog" class="icon" />
            用户管理
          </button>
          <span v-if="pendingCount > 0 && isAdmin" class="badge">{{ pendingCount }}</span>
        </div>

        <!-- 用户认证按钮 - 对非管理员、或被降级的用户可见 -->
        <el-badge v-if="!isAdmin" :is-dot="showAuthBadge" class="home-badge">
          <button class="styled-button" @click="handleAuthClick">
            <font-awesome-icon icon="user-shield" class="icon" />
            <span>用户认证</span>
          </button>
        </el-badge>
        
        <!-- 人脸数据管理按钮 - 仅对管理员可见 -->
        <div class="button-wrapper" v-if="isAdmin">
          <button class="styled-button" @click="$router.push('/face')" :disabled="isInteractionLocked">
            <font-awesome-icon icon="database" class="icon" />
            <span>人脸数据管理</span>
          </button>
          <span v-if="pendingFacesCount > 0" class="badge">{{ pendingFacesCount }}</span>
        </div>

        <!-- 路面检测按钮 - 非普通用户可见 -->
        <button
          v-if="!isNormalUser"
          class="styled-button"
          @click="handleNavigation('/road')"
          :disabled="isInteractionLocked"
        >
          <font-awesome-icon icon="road" />
          <span>路面检测</span>
        </button>

        <!-- 交通数据按钮 - 非普通用户可见 -->
        <button
          v-if="!isNormalUser"
          class="styled-button"
          @click="handleNavigation('/traffic')"
          :disabled="isInteractionLocked"
        >
          <font-awesome-icon icon="chart-bar" />
          <span>交通数据</span>
        </button>

        <!-- 日志按钮 - 非普通用户可见 -->
        <button
          v-if="!isNormalUser"
          class="styled-button"
          @click="handleNavigation('/log')"
          :disabled="isInteractionLocked"
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
import { ElNotification, ElMessageBox } from "element-plus"; // 引入 ElMessageBox
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
// 引入背景图片
import bg5 from '@/assets/bg5.png';
import bg6 from '@/assets/bg6.png';

const store = useMainStore();
const router = useRouter();

// --- 权限和状态计算 ---
const userRole = computed(() => localStorage.getItem('user-class')?.trim() || '普通用户');
const isAdmin = computed(() => userRole.value === '管理员');
const isAuthenticatedUser = computed(() => userRole.value === '认证用户');
const isNormalUser = computed(() => userRole.value === '普通用户');

// 新增：判断是否需要锁定交互
const isInteractionLocked = computed(() => {
  // 锁定条件1：用户被降级
  if (store.isDemoted) return true;
  // 锁定条件2：普通用户认证已批准，等待重新登录
  if (isNormalUser.value && store.faceAuthNotificationStatus === 'approved') return true;
  return false;
});

// "用户认证"按钮上的小红点
const showAuthBadge = computed(() => {
  if (store.isDemoted) return true; // 被降级时显示
  const status = store.faceAuthNotificationStatus;
  return status === 'approved' || status === 'rejected'; // 认证结果出来时显示
});

const pendingCount = computed(() => store.pendingApplicationsCount);
const pendingFacesCount = computed(() => store.pendingFacesCount);

// --- 视图和样式 ---
const themeClass = computed(() => {
  if (isAdmin.value) return 'admin-theme';
  return 'user-theme';
});

const backgroundStyle = computed(() => {
  const imageUrl = isAdmin.value ? bg6 : bg5;
  return {
    backgroundImage: `url(${imageUrl})`
  };
});

onMounted(() => {
  if (isAdmin.value) {
    store.fetchPendingApplicationsCount();
    store.fetchPendingFacesCount();
  }
  
  if (window.history.state.notification) {
    const { title, message, type } = window.history.state.notification;
    ElNotification({ title, message, type, duration: 7000 });
    window.history.replaceState({ ...window.history.state, notification: null }, '');
  }
});

// --- 事件处理 ---
const handleAuthClick = () => {
  // 场景1：处理被降级的情况
  if (store.isDemoted) {
    ElMessageBox.alert('您的人脸数据已被管理员移除，用户等级已降级。请重新登录后进行操作。', '权限变更通知', {
      confirmButtonText: '重新登录',
      type: 'warning',
      showClose: false,
      callback: () => {
        store.logout();
      },
    });
    return; // 终止后续操作
  }
  
  // 场景2：已认证用户（非降级状态）点击，直接跳转到人脸验证页面
  if (isAuthenticatedUser.value) {
    router.push("/face");
    return;
  }
  
  // 场景3：普通用户点击，跳转到认证页面 (此处的交互由路由守卫处理)
  router.push("/face");
};

const handleNavigation = (path) => {
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
  store.logout(); // 直接调用 store 的 action
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

.styled-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  background-color: #f0f0f0;
  color: #999;
  transform: none; /* 禁用时移除悬浮效果 */
}

.styled-button .icon,
.styled-button .fa-icon,
.styled-button svg {
  /* More specific selectors */
  font-size: 36px;
  margin-bottom: 15px;
}

.styled-button:not(:disabled):hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.2);
}

.logout-btn {
  color: #dc3545; /* 红色 */
}

.logout-btn:not(:disabled):hover {
  background-color: #dc3545;
  color: white;
  box-shadow: 0 6px 20px rgba(220, 53, 69, 0.3);
}

.badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #dc3545;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 14px;
  font-weight: bold;
  border: 2px solid white;
}

/* --- THEME OVERRIDES --- */

/* User Theme */
.user-theme .title {
  color: #0056b3;
}
.user-theme .styled-button {
  color: #007bff;
}

/* Admin Theme */
.admin-theme .title {
  color: #8b0000;
}
.admin-theme .styled-button {
  color: #8b0000;
}
.admin-theme .styled-button:not(:disabled):hover {
  background-color: #8b0000;
  color: white;
  box-shadow: 0 6px 20px rgba(139, 0, 0, 0.3);
}

.home-badge {
  width: 100%;
  height: 100%;
}

.home-badge .styled-button {
  width: 100%;
  height: 100%;
}
</style>

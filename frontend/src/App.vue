<template>
  <el-container style="height: 100vh">
    <!-- 根据路由判断是否显示侧边栏 -->
    <el-aside v-if="showSidebar" width="200px" :class="themeClass">
      <el-menu
        :default-active="$route.path"
        :background-color="themeColors.backgroundColor"
        :text-color="themeColors.textColor"
        :active-text-color="themeColors.activeTextColor"
        style="height: 100%; border-right: none;"
        @select="handleSelect"
      >
        <el-menu-item index="/home">首页</el-menu-item>

        <!-- 用户管理对所有登录用户可见 -->
        <el-menu-item index="/user-management">用户管理</el-menu-item>

        <!-- 用户认证对非认证/非管理员用户可见 -->
        <el-menu-item v-if="isNormalUser" index="/face">用户认证(人脸识别)</el-menu-item>
        
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
      <el-footer style="height: auto;">
        <AuthFooter />
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import bg6 from '@/assets/bg6.png'; // 引入 bg6 图片
import AuthFooter from '@/components/AuthFooter.vue';
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const router = useRouter();
const route = useRoute();

// --- 布局和路由管理 ---
const showSidebar = computed(() => {
  // 在登录页 (路径为 '/') 不显示侧边栏
  return route.path !== '/';
});

// 为特定管理员页面应用特殊背景
const mainStyle = computed(() => {
  const isAdmin = userRole.value === '管理员';
  const adminRoutes = ['/user-management', '/approval'];
  if (isAdmin && adminRoutes.includes(route.path)) {
    return {
      backgroundImage: `url(${bg6})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center center',
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
  return localStorage.getItem('user-class')?.trim() || '普通用户';
});
const isAdmin = computed(() => userRole.value === '管理员');
const isNormalUser = computed(() => userRole.value === '普通用户');

const themeClass = computed(() => (isAdmin.value ? 'admin-theme' : 'user-theme'));

const themeColors = computed(() => {
  if (isAdmin.value) {
    return {
      backgroundColor: '#4a0e0e', // 深红色背景
      textColor: '#ffffff',
      activeTextColor: '#f5c518' // 金色高亮
    };
  }
  return {
    backgroundColor: '#001f3f', // 默认深蓝色背景
    textColor: '#ffffff',
    activeTextColor: '#ffd04b'
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
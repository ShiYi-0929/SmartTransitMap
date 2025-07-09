<template>
  <div
    class="min-h-screen bg-gradient-to-br from-blue-100 via-blue-50 to-gray-100 flex"
  >
    <!-- 左侧导航栏 -->
    <div class="w-48 bg-slate-800 text-white flex-shrink-0">
      <div class="p-4">
        <h2
          class="text-lg font-semibold text-center border-b border-slate-600 pb-3 mb-4"
        >
          智能检测系统
        </h2>
        <nav class="space-y-2">
          <router-link
            to="/"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'home' }"
          >
            <HomeIcon class="w-4 h-4 mr-3" />
            首页
          </router-link>

          <router-link
            to="/auth"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'auth' }"
          >
            <UserIcon class="w-4 h-4 mr-3" />
            用户认证
          </router-link>

          <router-link
            to="/road-detection"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'roadDetection' }"
          >
            <ScanIcon class="w-4 h-4 mr-3" />
            路面识别
          </router-link>

          <router-link
            to="/traffic-data"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'trafficData' }"
          >
            <BarChart3Icon class="w-4 h-4 mr-3" />
            交通数据
          </router-link>

          <router-link
            to="/log-alarm"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'logAlarm' }"
          >
            <AlertTriangleIcon class="w-4 h-4 mr-3" />
            日志告警
          </router-link>
        </nav>
      </div>
    </div>

    <!-- 右侧主要内容区域 -->
    <div class="flex-1 flex flex-col">
      <!-- 顶部标题栏 -->
      <div class="bg-slate-800 text-white px-6 py-4">
        <div class="flex items-center justify-center">
          <component :is="currentPageIcon" class="w-6 h-6 mr-3" />
          <h1 class="text-xl font-semibold">{{ currentPageTitle }}</h1>
        </div>
      </div>

      <!-- 主要内容 -->
      <div class="flex-1 overflow-auto">
        <slot />
      </div>
    </div>
  </div>
</template>

<script>
import {
  Home as HomeIcon,
  User as UserIcon,
  ScanLine as ScanIcon,
  BarChart3 as BarChart3Icon,
  AlertTriangle as AlertTriangleIcon,
} from "lucide-vue-next";

export default {
  name: "AppLayout",
  components: {
    HomeIcon,
    UserIcon,
    ScanIcon,
    BarChart3Icon,
    AlertTriangleIcon,
  },
  computed: {
    currentPageTitle() {
      const titles = {
        home: "系统首页",
        auth: "用户认证",
        roadDetection: "路面病害识别系统",
        trafficData: "交通数据分析",
        logAlarm: "日志告警管理",
      };
      return titles[this.$route.name] || "智能检测系统";
    },
    currentPageIcon() {
      const icons = {
        home: "HomeIcon",
        auth: "UserIcon",
        roadDetection: "ScanIcon",
        trafficData: "BarChart3Icon",
        logAlarm: "AlertTriangleIcon",
      };
      return icons[this.$route.name] || "ScanIcon";
    },
  },
};
</script>

<style scoped>
.nav-link {
  @apply flex items-center px-3 py-2 rounded-md text-sm font-medium text-slate-300 hover:bg-slate-700 hover:text-white transition-colors;
}

.nav-link-active {
  @apply bg-slate-700 text-white;
}
</style>

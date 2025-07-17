<template>
  <AppLayout>
    <div class="p-6">
      <div class="max-w-7xl mx-auto">
        <div
          class="bg-white rounded-lg shadow-md border border-slate-200 p-8 text-center"
        >
          <h2 class="text-3xl font-bold text-slate-800 mb-4">
            欢迎使用智能检测系统
          </h2>
          <p class="text-slate-600 mb-8">
            集成多种智能检测功能，为您提供全方位的数据分析服务
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <router-link to="/road-detection" class="feature-card">
              <ScanIcon class="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <h3 class="text-lg font-semibold text-slate-800 mb-2">
                路面识别
              </h3>
              <p class="text-slate-600 text-sm">AI智能路面病害检测</p>
            </router-link>

            <router-link to="/traffic-data" class="feature-card">
              <BarChart3Icon class="w-12 h-12 text-green-600 mx-auto mb-4" />
              <h3 class="text-lg font-semibold text-slate-800 mb-2">
                交通数据
              </h3>
              <p class="text-slate-600 text-sm">交通流量数据分析</p>
            </router-link>

            <router-link to="/auth" class="feature-card">
              <UserIcon class="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <h3 class="text-lg font-semibold text-slate-800 mb-2">
                用户认证
              </h3>
              <p class="text-slate-600 text-sm">安全的用户身份验证</p>
            </router-link>

            <router-link to="/log-alarm" class="feature-card">
              <AlertTriangleIcon class="w-12 h-12 text-red-600 mx-auto mb-4" />
              <h3 class="text-lg font-semibold text-slate-800 mb-2">
                日志告警
              </h3>
              <p class="text-slate-600 text-sm">系统日志和告警管理</p>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import AppLayout from "@/components/AppLayout.vue";
import {
  ScanLine as ScanIcon,
  BarChart3 as BarChart3Icon,
  User as UserIcon,
  AlertTriangle as AlertTriangleIcon,
} from "lucide-vue-next";

export default {
  name: "HomePage",
  components: {
    AppLayout,
    ScanIcon,
    BarChart3Icon,
    UserIcon,
    AlertTriangleIcon,
  },
};
</script>

<style scoped>
.feature-card {
  @apply bg-slate-50 p-6 rounded-lg border border-slate-200 hover:bg-slate-100 hover:shadow-md transition-all duration-200 cursor-pointer;
}
</style>

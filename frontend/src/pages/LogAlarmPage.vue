<template>
  <AppLayout>
    <div class="p-6">
      <div class="max-w-4xl mx-auto">
        <div
          class="bg-white rounded-lg shadow-md border border-slate-200 p-8 text-center"
        >
          <AlertTriangleIcon class="w-16 h-16 text-slate-400 mx-auto mb-4" />
          <h2 class="text-2xl font-bold text-slate-800 mb-4">日志告警管理</h2>
          <p class="text-slate-600 mb-8">此模块由其他团队成员负责开发</p>
          <div class="bg-slate-100 rounded-lg p-6">
            <p class="text-slate-500">功能开发中...</p>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import AppLayout from "@/components/AppLayout.vue";
import { AlertTriangle as AlertTriangleIcon } from "lucide-vue-next";

export default {
  name: "LogAlarmPage",
  components: {
    AppLayout,
    AlertTriangleIcon,
  },
};
</script>

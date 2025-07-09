<template>
  <AppLayout>
    <div class="p-6">
      <div class="max-w-4xl mx-auto">
        <div
          class="bg-white rounded-lg shadow-md border border-slate-200 p-8 text-center"
        >
          <BarChart3Icon class="w-16 h-16 text-slate-400 mx-auto mb-4" />
          <h2 class="text-2xl font-bold text-slate-800 mb-4">交通数据分析</h2>
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
import { BarChart3 as BarChart3Icon } from "lucide-vue-next";

export default {
  name: "TrafficDataPage",
  components: {
    AppLayout,
    BarChart3Icon,
  },
};
</script>

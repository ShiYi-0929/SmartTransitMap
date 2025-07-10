<template>
  <div>
    <!-- 二级菜单Tab -->
    <el-menu
      :default-active="activeTab"
      mode="horizontal"
      @select="handleTabChange"
      background-color="#0a2342"
      text-color="#fff"
      active-text-color="#00cfff"
      style="border-radius: 12px; margin-bottom: 24px;"
    >
      <el-menu-item index="overview">数据总览</el-menu-item>
      <el-menu-item index="track">轨迹查询</el-menu-item>
      <el-menu-item index="heatmap">热力图分析</el-menu-item>
      <el-menu-item index="anomaly">异常检测</el-menu-item>
      <el-menu-item index="spatiotemporal">时空动态</el-menu-item>
      <el-menu-item index="statistics">统计分析</el-menu-item>
      <el-menu-item index="road">路段分析</el-menu-item>
      <el-menu-item index="pattern">模式识别</el-menu-item>
    </el-menu>
    <div style="margin-top: 24px;">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const router = useRouter()
const activeTab = computed(() => {
  return route.path.split('/')[2] || 'overview'
})
function handleTabChange(tab) {
  router.push(`/traffic/${tab}`)
}
</script>
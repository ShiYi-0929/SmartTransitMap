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
      <el-menu-item index="road-advanced">路段智能分析</el-menu-item>
      <el-menu-item index="pattern">模式识别</el-menu-item>
    </el-menu>
    
    <!-- 路由视图容器 -->
    <div style="margin-top: 24px; min-height: 500px;">
      <router-view :key="$route.fullPath" v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed, watch, nextTick } from 'vue'

const route = useRoute()
const router = useRouter()

// 计算当前激活的标签页
const activeTab = computed(() => {
  const pathSegments = route.path.split('/').filter(Boolean)
  return pathSegments[1] || 'overview' // traffic是第0个，子路由是第1个
})

// 处理标签页切换
async function handleTabChange(tab) {
  console.log(`🔀 导航切换: ${activeTab.value} -> ${tab}`)
  
  // 如果已经在当前页面，不需要导航
  if (activeTab.value === tab) {
    console.log('🚫 已在当前页面，跳过导航')
    return
  }
  
  try {
    // 确保导航完成
    await router.push(`/traffic/${tab}`)
    console.log(`✅ 导航成功: /traffic/${tab}`)
    
    // 等待DOM更新
    await nextTick()
  } catch (error) {
    console.error('❌ 导航失败:', error)
  }
}

// 监听路由变化进行调试
watch(() => route.fullPath, (newPath, oldPath) => {
  console.log(`🛣️ 路由变化: ${oldPath} -> ${newPath}`)
  console.log(`📍 当前激活标签: ${activeTab.value}`)
}, { immediate: true })

// 组件挂载时的调试信息
watch(() => activeTab.value, (newTab, oldTab) => {
  console.log(`🏷️ 激活标签变化: ${oldTab} -> ${newTab}`)
}, { immediate: true })
</script>

<style scoped>
/* 添加页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 确保路由视图容器有足够高度 */
.router-view-container {
  min-height: 500px;
}
</style>
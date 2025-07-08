<template>
  <el-card>
    <h3>交通数据统计</h3>
    <el-button @click="loadStats">刷新</el-button>
    <div v-if="stats">{{ stats }}</div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { getTrafficStats } from 'c:/Users/1/Documents/GitHub/SmartTransitMap/frontend/src/api/traffic'

const stats = ref('')

async function loadStats() {
  const res = await getTrafficStats()
  stats.value = res.data.stats
}

loadStats()
</script> 
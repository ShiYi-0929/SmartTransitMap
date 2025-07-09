<template>
  <el-card>
    <h3>交通数据统计</h3>
    <el-button @click="loadStats">刷新</el-button>
    <div v-if="stats && Object.keys(stats).length">
      <div v-for="(value, key) in stats" :key="key">
        {{ key }}：{{ value }}
      </div>
    </div>
    <pre>{{ stats }}</pre>
  </el-card>
</template>

<script setup>
import {ref} from 'vue'
import {getTrafficStats} from '../api/traffic'

const stats = ref({})

async function loadStats() {
  const res = await getTrafficStats()
  stats.value = res.data
}

loadStats()
</script> 
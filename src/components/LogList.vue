<template>
  <el-card>
    <h3>系统日志</h3>
    <el-button @click="loadLogs">刷新</el-button>
    <el-list>
      <el-list-item v-for="(log, idx) in logs" :key="idx">{{ log }}</el-list-item>
    </el-list>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { getLogs } from '../api/log'

const logs = ref([])

async function loadLogs() {
  const res = await getLogs()
  logs.value = res.data.logs
}

loadLogs()
</script> 
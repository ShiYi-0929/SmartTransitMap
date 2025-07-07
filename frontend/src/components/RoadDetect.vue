<template>
  <el-card>
    <h3>路面病害检测</h3>
    <input type="file" @change="onFileChange" />
    <el-button type="primary" @click="submit">检测</el-button>
    <div v-if="result">{{ result }}</div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { detectRoadDamage } from '../api/road'

const file = ref(null)
const result = ref('')

function onFileChange(e) {
  file.value = e.target.files[0]
}

async function submit() {
  if (!file.value) return
  const res = await detectRoadDamage(file.value)
  result.value = res.data.msg
}
</script> 
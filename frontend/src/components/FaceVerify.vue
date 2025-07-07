<template>
  <el-card>
    <h3>人脸识别</h3>
    <el-input v-model="userId" placeholder="请输入用户ID" />
    <input type="file" @change="onFileChange" />
    <el-button type="primary" @click="submit">识别</el-button>
    <div v-if="result">{{ result }}</div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { verifyFace } from '../api/face'

const userId = ref('')
const file = ref(null)
const result = ref('')

function onFileChange(e) {
  file.value = e.target.files[0]
}

async function submit() {
  if (!userId.value || !file.value) return
  const res = await verifyFace(userId.value, file.value)
  result.value = res.data.msg
}
</script> 
<template>
  <el-card>
    <h3>人脸录入</h3>
    <el-input v-model="userId" placeholder="请输入用户ID" />
    <input type="file" @change="onFileChange" />
    <el-button type="primary" @click="submit">上传</el-button>
    <div v-if="result">{{ result }}</div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { registerFace } from '../api/face'

const userId = ref('')
const file = ref(null)
const result = ref('')

function onFileChange(e) {
  file.value = e.target.files[0]
}

async function submit() {
  if (!userId.value || !file.value) return
  const res = await registerFace(userId.value, file.value)
  result.value = res.data.msg
}
</script> 
<template>
  <el-row :gutter="20">
    <el-col :span="12">
      <FaceRegister />
    </el-col>
    <el-col :span="12">
      <FaceVerify />
    </el-col>
  </el-row>
</template>

<script setup>
import FaceRegister from '../components/FaceRegister.vue'
import FaceVerify from '../components/FaceVerify.vue'
</script> 
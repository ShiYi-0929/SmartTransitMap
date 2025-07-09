<template>
  <el-container style="height: 100vh">
    <el-aside width="200px">
      <el-menu
        router
        background-color="#001f3f"
        text-color="#ffffff"
        active-text-color="#ffd04b"
        style="height: 100%;"
      >
        <el-menu-item index="/home">首页</el-menu-item>
        <el-menu-item index="/face">用户认证(人脸识别)</el-menu-item>
        <el-menu-item index="/road">路面检测</el-menu-item>
        <el-menu-item index="/traffic">交通数据</el-menu-item>
        <el-menu-item index="/log">日志告警</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container direction="vertical">
      <el-main>
        <router-view />
      </el-main>
      <el-footer style="height: auto;">
        <AuthFooter />
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import AuthFooter from '@/components/AuthFooter.vue'
</script> 
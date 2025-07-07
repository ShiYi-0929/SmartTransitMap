<template>
  <el-container style="height: 100vh">
    <el-aside width="200px">
      <el-menu router>
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/face">人脸识别</el-menu-item>
        <el-menu-item index="/road">路面检测</el-menu-item>
        <el-menu-item index="/traffic">交通数据</el-menu-item>
        <el-menu-item index="/log">日志告警</el-menu-item>
      </el-menu>
    </el-aside>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
</script> 
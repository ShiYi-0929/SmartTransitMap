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
        <!-- Modified for conditional navigation and added non-route index to fix warning -->
        <el-menu-item index="auth-action" @click="handleAuthMenuClick">用户认证(人脸识别)</el-menu-item>
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
import { useRouter } from 'vue-router';
import { ElNotification } from 'element-plus';

const router = useRouter();

const handleAuthMenuClick = () => {
  const userClass = localStorage.getItem('user-class');
  // Use trim() and check for Chinese role names
  if (userClass && (userClass.trim() === '认证用户' || userClass.trim() === '管理员')) {
    ElNotification({
      title: '提示',
      message: '您已是认证用户，无需重复认证！',
      type: 'info',
    });
    // Redirect to home page after showing notification
    router.push('/home');
  } else {
    router.push('/face');
  }
};
</script> 
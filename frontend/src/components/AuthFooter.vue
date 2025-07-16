<template>
  <div class="auth-footer">
    <!-- 添加图片标签 -->
    <img src="@/assets/logo2.png" alt="Logo" class="footer-logo">
    <p>◎ 2025 智能交通与路面病害检测平台系统 版权所有|北京交通大学|软件工程学院|妙妙妙代码全队出品</p>
  </div>
</template>

<script>
export default {
  name: 'AuthFooter'
};
</script>

<style scoped>
.auth-footer {
  text-align: center;
  padding: 10px;
  color: #999;
  margin-top: auto; /* 推至页面底部 */
  display: flex; /* 使用 flexbox 布局 */
  align-items: center; /* 垂直居中对齐 */
  justify-content: center; /* 水平居中对齐 */
}

.footer-logo {
  max-width: 50px; /* 设置 logo 的最大宽度 */
  max-height: 50px; /* 设置 logo 的最大高度 */
  margin-right: 10px; /* 右侧边距 */
}
</style>
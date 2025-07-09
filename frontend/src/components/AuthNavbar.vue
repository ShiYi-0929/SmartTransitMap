<template>
  <div class="auth-navbar">
    <img src="@/assets/logo.png" alt="Logo" class="logo">
    <h1>身份验证/注册页面</h1>
  </div>
</template>

<script>
export default {
  name: 'AuthNavbar'
};
</script>

<style scoped>
.auth-navbar {
  background-color: #001f3f;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo {
  height: 40px;
  margin-right: 20px;
}

h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}
</style>
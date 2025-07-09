<template>
  <div class="welcome-container">
    <div class="welcome-box">
      <h1>欢迎回来！</h1>
      <p>您已成功登录。</p>
      <div class="actions">
        <div class="square-btn" @click="goToManagement">
          <font-awesome-icon icon="user" />
          <span>用户管理</span>
        </div>
        <div class="square-btn" @click="showLogs">
          <font-awesome-icon icon="list" />
          <span>日志及告警记录</span>
        </div>
        <div class="square-btn logout-btn" @click="logout">
          <font-awesome-icon icon="sign-out-alt" />
          <span>退出登录</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  methods: {
    goToManagement() {
      this.$router.push('/user-management');
    },
    showLogs() {
      alert('（仅限管理员）\n\n此功能暂未开放，敬请期待！');
    },
    logout() {
      localStorage.removeItem('user-token');
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
.welcome-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5 url('@/assets/bg5.png') no-repeat center center;
  background-size: cover;
  position: relative;
}

.welcome-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.welcome-box {
  text-align: center;
  background-color: rgba(255, 255, 255, 0.95);
  padding: 50px 60px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  z-index: 2;
  position: relative;
  width: 80%;
  max-width: 900px;
}

h1 {
  font-size: 32px;
  color: #333;
  margin-bottom: 10px;
}

p {
  font-size: 18px;
  color: #666;
  margin-bottom: 40px;
}

.actions {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 30px;
  width: 100%;
  margin: 0 auto;
}

.square-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 25px;
  border-radius: 10px;
  background-color: white;
  color: #007BFF;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 180px;  /* Set a fixed width */
  height: 160px; /* Set a fixed height */
  border: 1px solid #e0e0e0;
}

.square-btn .fa-icon { /* Targeting FontAwesomeIcon */
  font-size: 32px;
  margin-bottom: 15px;
}

.square-btn:hover {
  background-color: #f8f9fa;
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.logout-btn {
  color: #dc3545;
}

.logout-btn:hover {
  background-color: #f8d7da;
}
</style> 
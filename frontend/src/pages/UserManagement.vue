<template>
  <div class="management-container">
    <div class="management-box">
      <button @click="$router.push('/home')" class="back-btn">&larr; 返回</button>
      <h2>用户个人信息管理</h2>
      <div class="avatar-section">
        <img :src="avatarPreview" alt="User Avatar" class="avatar-img">
        <input type="file" @change="onFileChange" accept="image/*" ref="fileInput" style="display: none;">
        <button @click="$refs.fileInput.click()">更换头像</button>
      </div>
      <div class="form-section">
        <div class="form-group">
          <label for="username">用户名</label>
          <input type="text" id="username" v-model="user.username">
        </div>
        <div class="form-group">
          <label for="phone">电话号码</label>
          <input type="text" id="phone" v-model="user.phone">
        </div>
        <div class="form-group">
          <label for="email">邮箱</label>
          <input type="email" id="email" v-model="user.email">
        </div>
        <div class="form-group">
          <label for="role">用户权限</label>
          <input type="text" id="role" :value="user.role" disabled>
        </div>
        <button @click="saveChanges" class="save-btn">保存更改</button>
      </div>
    </div>
  </div>
</template>

<script>
import defaultAvatar from '@/assets/head.jpg';

export default {
  name: 'UserManagement',
  data() {
    return {
      user: {
        username: '杨冕新（示例用户）',
        phone: '13811451419',
        email: 'ymx1919810@qq.com',
        role: '宇宙至尊威震天，但是普通用户',
        avatar: defaultAvatar
      },
      avatarPreview: defaultAvatar
    };
  },
  methods: {
    onFileChange(e) {
      const file = e.target.files[0];
      if (file) {
        // Create a URL for the selected file for preview
        this.avatarPreview = URL.createObjectURL(file);
        // Here you would typically upload the file to your server
        // For now, we'll just update the preview
        console.log('New avatar selected:', file);
      }
    },
    saveChanges() {
      // Here you would typically send the updated user data to your server
      console.log('Saving changes:', this.user);
      alert('用户信息已更新！');
    }
  }
};
</script>

<style scoped>
.management-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5 url('@/assets/bg5.png') no-repeat center center;
  background-size: cover;
  position: relative;
}

.management-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.management-box {
  width: 90%;
  max-width: 600px;
  background-color: rgba(255, 255, 255, 0.98);
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  z-index: 2;
  position: relative;
}

.back-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  background: none;
  border: 1px solid #ccc;
  color: #555;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}

h2 {
  text-align: center;
  font-size: 24px;
  margin-bottom: 30px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.avatar-img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid #fff;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  margin-bottom: 15px;
  object-fit: cover;
}

.avatar-section button {
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 14px;
}

.form-group input:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}

.save-btn {
  width: 100%;
  padding: 12px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
}
</style> 
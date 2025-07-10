<template>
  <div class="change-password-container">
    <!-- 添加遮罩层 -->
    <div class="background-mask"></div>
    <div class="change-password-box">
      <button @click="$router.back()" class="back-btn">&larr; 返回</button>
      <h2>修改密码</h2>

      <div class="form-group">
        <label for="oldPassword">旧密码</label>
        <div class="input-with-icon">
          <input
            :type="oldPasswordVisible ? 'text' : 'password'"
            id="oldPassword"
            v-model="passwords.oldPassword"
            placeholder="请输入您的旧密码"
          />
          <i
            class="fa"
            :class="oldPasswordVisible ? 'fa-eye-slash' : 'fa-eye'"
            @click="toggleVisibility('oldPasswordVisible')"
          ></i>
        </div>
      </div>

      <div class="form-group">
        <label for="newPassword">新密码</label>
        <div class="input-with-icon">
          <input
            :type="newPasswordVisible ? 'text' : 'password'"
            id="newPassword"
            v-model="passwords.newPassword"
            placeholder="请输入您的新密码"
          />
          <i
            class="fa"
            :class="newPasswordVisible ? 'fa-eye-slash' : 'fa-eye'"
            @click="toggleVisibility('newPasswordVisible')"
          ></i>
        </div>
      </div>

      <div class="form-group">
        <label for="confirmPassword">确认新密码</label>
        <div class="input-with-icon">
          <input
            :type="confirmPasswordVisible ? 'text' : 'password'"
            id="confirmPassword"
            v-model="passwords.confirmPassword"
            placeholder="请再次输入新密码"
          />
          <i
            class="fa"
            :class="confirmPasswordVisible ? 'fa-eye-slash' : 'fa-eye'"
            @click="toggleVisibility('confirmPasswordVisible')"
          ></i>
        </div>
      </div>

      <div class="form-group captcha-group">
        <input
          type="text"
          v-model="captcha"
          placeholder="请输入邮箱验证码"
          class="captcha-input"
        />
        <button @click="sendCode" :disabled="countdown > 0" class="captcha-btn">
          {{ countdown > 0 ? `${countdown}s 后重发` : "获取验证码" }}
        </button>
      </div>

      <button @click="submitChange" class="submit-btn">确认修改</button>
    </div>
  </div>
</template>

<script>
import { getUserProfile, sendVerificationCode, changePassword } from "@/api/user";

export default {
  name: "ChangePassword",
  data() {
    return {
      userEmail: "",
      passwords: {
        oldPassword: "",
        newPassword: "",
        confirmPassword: "",
      },
      captcha: "",
      countdown: 0,
      oldPasswordVisible: false,
      newPasswordVisible: false,
      confirmPasswordVisible: false,
    };
  },
  created() {
    this.fetchUserEmail();
  },
  methods: {
    fetchUserEmail() {
      getUserProfile()
        .then((response) => {
          this.userEmail = response.data.email;
        })
        .catch((error) => {
          console.error("获取用户邮箱失败:", error);
          alert("无法获取用户信息，请确保您已登录。");
          this.$router.push("/");
        });
    },
    sendCode() {
      if (!this.userEmail) {
        alert("用户邮箱未加载，无法发送验证码。");
        return;
      }
      sendVerificationCode(this.userEmail)
        .then(() => {
          alert("验证码已发送至您的邮箱，请注意查收。");
          this.countdown = 60;
          const interval = setInterval(() => {
            this.countdown--;
            if (this.countdown <= 0) {
              clearInterval(interval);
            }
          }, 1000);
        })
        .catch((error) => {
          console.error("发送验证码失败:", error);
          alert(error.response?.data?.detail || "发送验证码失败，请稍后重试。");
        });
    },
    toggleVisibility(field) {
      this[field] = !this[field];
    },
    submitChange() {
      if (this.passwords.newPassword !== this.passwords.confirmPassword) {
        alert("两次输入的新密码不一致！");
        return;
      }
      if (!this.passwords.oldPassword || !this.passwords.newPassword || !this.captcha) {
        alert("请填写所有字段！");
        return;
      }

      const payload = {
        old_password: this.passwords.oldPassword,
        new_password: this.passwords.newPassword,
        code: this.captcha,
      };

      changePassword(payload)
        .then(() => {
          alert("密码修改成功！为了您的账户安全，请使用新密码重新登录。");
          localStorage.removeItem("user-token");
          this.$router.push("/");
        })
        .catch((error) => {
          console.error("密码修改失败:", error);
          alert(error.response?.data?.detail || "密码修改失败，请检查您的输入。");
        });
    },
  },
};
</script>

<style scoped>
.change-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5 url("@/assets/bg5.png") no-repeat center center;
  background-size: cover;
  position: relative; /* 添加相对定位 */
}

/* 添加遮罩层样式 */
.background-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.change-password-box {
  width: 90%;
  max-width: 450px;
  background-color: rgba(255, 255, 255, 0.98);
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 2; /* 确保表单在遮罩层之上 */
}

.back-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  background: none;
  border: 1px solid #ccc;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
}

.input-with-icon {
  position: relative;
}

/* 修改输入框的宽度 */
.input-with-icon input {
  width: 80%; /* 可以根据需要调整这个值 */
  padding: 10px 40px 10px 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.input-with-icon i {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #888;
}

.captcha-group {
  display: flex;
  gap: 10px;
}

/* 修改验证码输入框的宽度 */
.captcha-input {
  width: 60%; /* 可以根据需要调整这个值 */
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.captcha-btn {
  padding: 10px 15px;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  white-space: nowrap;
}

.captcha-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 5px;
  background-color: #28a745;
  color: white;
  font-size: 16px;
  cursor: pointer;
}
</style>

<template>
  <div class="management-container" :style="containerStyle">
    <div class="management-box">
      <button @click="$router.push('/home')" class="back-btn">&larr; 返回</button>
      <h2>用户个人信息管理</h2>
      <div class="avatar-section">
        <img :src="avatarPreview" alt="User Avatar" class="avatar-img" />
        <input
          type="file"
          @change="onFileChange"
          accept="image/*"
          ref="fileInput"
          style="display: none"
        />
        <!-- 修改按钮点击事件 -->
        <button @click="showUnavailableAlert">更换头像</button>
      </div>
      <div class="form-section">
        <div class="form-group">
          <label for="userID">用户ID</label>
          <input type="text" id="userID" v-model="user.userID" disabled />
        </div>
        <div class="form-group">
          <label for="username">用户名</label>
          <input type="text" id="username" v-model="user.username" />
        </div>
        <div class="form-group">
          <label for="email">邮箱</label>
          <input type="email" id="email" v-model="user.email" />
        </div>
        <div class="form-group">
          <label for="role">用户权限</label>
          <input type="text" id="role" :value="user.role" disabled />
        </div>
        <div class="form-actions">
          <button @click="saveChanges" class="save-btn">保存更改</button>
          <!-- Wrap the upgrade button to position the badge -->
          <div class="button-wrapper">
            <button @click="upgradeRole" class="upgrade-btn">
              {{ user.role.trim() === "管理员" ? "权限升级申请批复" : "升级权限" }}
            </button>
            <!-- Badge display logic -->
            <span v-if="user.role.trim() === '管理员' && pendingCount > 0" class="badge">
              {{ pendingCount }}
            </span>
          </div>
          <button @click="goToChangePassword" class="change-password-btn">
            修改密码
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import defaultAvatar from "@/assets/head.jpg";
import bg5 from "@/assets/bg5.png"; // Import the background image
import { getUserProfile, updateUserProfile } from "@/api/user";
import { applyForAdmin } from "@/api/admin";
import { useMainStore } from "@/store";
import { mapState } from "pinia"; // Import mapState
import { ElMessage } from "element-plus";

export default {
  name: "UserManagement",
  data() {
    return {
      user: {
        userID: null,
        username: "",
        email: "",
        role: "", // This will be populated from API
        avatar: defaultAvatar,
      },
      // Store original values for comparison
      originalUsername: "",
      originalEmail: "",
      isEditing: false, // This seems unused, but we'll keep it for now
      isLoading: false,
      // 定义 avatarPreview 变量
      avatarPreview: defaultAvatar,
    };
  },
  computed: {
    // Map the store's state to computed properties
    ...mapState(useMainStore, {
      pendingCount: "pendingApplicationsCount",
    }),
    isAdmin() {
      return localStorage.getItem("user-class")?.trim() === "管理员";
    },
    containerStyle() {
      if (!this.isAdmin) {
        return {
          "background-image": `url(${bg5})`,
        };
      }
      return {};
    },
  },
  created() {
    this.fetchUserProfile();
  },
  methods: {
    async fetchUserProfile() {
      try {
        this.isLoading = true;
        const response = await getUserProfile();

        this.user.userID = response.userID;
        this.user.username = response.username;
        this.user.email = response.email;
        this.user.role = response.user_class.trim();

        // Store the original values
        this.originalUsername = response.username;
        this.originalEmail = response.email;
      } catch (error) {
        console.error("获取用户信息失败:", error);
        ElMessage.error("加载用户信息失败，请稍后重试。");
      } finally {
        this.isLoading = false;
      }
    },

    async saveChanges() {
      // 1. Check if there are any changes
      if (
        this.user.username === this.originalUsername &&
        this.user.email === this.originalEmail
      ) {
        ElMessage.info("用户信息未作任何修改。");
        return;
      }

      // 2. Validate username format
      const usernameRegex = /^[a-zA-Z0-9\u4e00-\u9fa5]+$/;
      if (!usernameRegex.test(this.user.username)) {
        ElMessage.error("用户名只能包含中文、字母和数字。");
        return;
      }

      // 3. Proceed with API call
      try {
        const dataToUpdate = {
          username: this.user.username,
          email: this.user.email,
        };
        const response = await updateUserProfile(dataToUpdate);

        // Update user object and original values with the new info from the response
        this.user.username = response.username;
        this.user.email = response.email;
        this.originalUsername = response.username;
        this.originalEmail = response.email;

        ElMessage.success("用户信息更新成功！");
      } catch (error) {
        console.error("更新用户信息失败:", error);
        const errorMsg = error.response?.data?.detail || "更新失败，请稍后重试。";
        ElMessage.error(errorMsg);
        // Optional: Revert changes to original if save fails
        this.user.username = this.originalUsername;
        this.user.email = this.originalEmail;
      }
    },

    goToChangePassword() {
      this.$router.push("/change-password");
    },

    upgradeRole() {
      const role = this.user.role;
      if (role === "普通用户") {
        ElMessage.info("权限升级需要进行人脸识别认证，即将跳转至认证页面。");
        this.$router.push("/face");
      } else if (role === "认证用户") {
        applyForAdmin()
          .then((response) => {
            ElMessage.success(response.message || "升级申请已发送，请等待管理员批复。");
          })
          .catch((error) => {
            const errorMsg = error.response?.data?.detail || "申请失败，请稍后重试。";
            ElMessage.error(errorMsg);
          });
      } else if (role === "管理员") {
        this.$router.push("/approval");
      }
    },

    // 新增方法用于显示提示信息
    showUnavailableAlert() {
      ElMessage.info("该功能暂不开放");
    },
  },
  mounted() {
    const store = useMainStore();
    this.fetchUserProfile();
    // Also fetch the count when the component is mounted
    store.fetchPendingApplicationsCount();
  },
};
</script>

<style scoped>
.management-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  /* background: #f0f2f5 url("@/assets/bg5.png") no-repeat center center; */ /* This will be handled by :style now */
  background-size: cover;
  position: relative;
}

.management-container::before {
  content: "";
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
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
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

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30px;
}

.form-actions button,
.button-wrapper {
  flex-basis: 32%; /* Distribute space */
}

.form-actions button {
  padding: 12px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
  width: 100%;
  box-sizing: border-box; /* Ensure padding doesn't affect width */
}

/* Styles for wrapper and badge, copied from Home.vue */
.button-wrapper {
  position: relative;
}

.badge {
  position: absolute;
  top: -10px;
  right: -5px;
  background-color: #dc3545;
  color: white;
  border-radius: 50%;
  padding: 5px;
  font-size: 14px;
  font-weight: bold;
  border: 2px solid white;
  min-width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-sizing: border-box;
}

.save-btn {
  background-color: #28a745;
  color: white;
}

.save-btn:hover {
  background-color: #218838;
}

.upgrade-btn {
  background-color: #007bff;
  color: white;
}

.upgrade-btn:hover {
  background-color: #0056b3;
}

.change-password-btn {
  background-color: #ffc107;
  color: #333;
}

.change-password-btn:hover {
  background-color: #e0a800;
}
</style>

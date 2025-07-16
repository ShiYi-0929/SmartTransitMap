import { getPendingApplicationsCount, getPendingFacesCount as apiGetPendingFacesCount } from '@/api/admin'; // 从 admin api 导入
import { getUserProfile } from '@/api/user';
import { defineStore } from 'pinia';
import router from '@/router'; // 使用默认导入

export const useMainStore = defineStore('main', {
  state: () => ({
    user: null,
    pendingApplicationsCount: 0,
    pendingFacesCount: 0, // 新增：待审批人脸数量
    // 从 localStorage 初始化轮询状态，确保刷新后不丢失
    isPollingActive: localStorage.getItem('isPollingActive') === 'true',
    // 新增：用于驱动通知徽章的状态
    faceAuthNotificationStatus: localStorage.getItem('faceAuthNotificationStatus') || 'none', // none, approved, rejected
    // 新增：用于标记用户是否被管理员降级
    isDemoted: false,
  }),
  actions: {
    setUser(user) {
      this.user = user;
    },
    setPendingApplicationsCount(count) {
        this.pendingApplicationsCount = count;
    },
    setPendingFacesCount(count) {
      this.pendingFacesCount = count;
    },
    setPollingState(isActive) {
      this.isPollingActive = isActive;
      // 将状态同步到 localStorage
      if (isActive) {
        localStorage.setItem('isPollingActive', 'true');
      } else {
        localStorage.removeItem('isPollingActive');
      }
    },
    setFaceAuthNotificationStatus(status) {
      this.faceAuthNotificationStatus = status;
      if (status === 'none') {
        localStorage.removeItem('faceAuthNotificationStatus');
      } else {
        localStorage.setItem('faceAuthNotificationStatus', status);
      }
    },
    setDemotionStatus(isDemoted) {
      this.isDemoted = isDemoted;
    },
    logout() {
      // 清除所有相关的本地存储
      localStorage.removeItem('token');
      localStorage.removeItem('user-class');
      localStorage.removeItem('user-id'); // 假设也存储了用户ID
      localStorage.removeItem('hasSeenRejection'); // 清除拒绝状态

      // 重置 Pinia store 中的状态
      this.setUser(null);
      this.setPendingApplicationsCount(0);
      this.setPendingFacesCount(0);
      this.setPollingState(false); // 登出时停止轮询 (这也会清理localStorage)
      this.setFaceAuthNotificationStatus('none'); // 登出时清除通知状态
      this.setDemotionStatus(false); // 登出时重置降级状态
      
      // 使用 router 实例进行跳转
      // 在action中直接使用引入的router实例
      if (router.currentRoute.value.path !== '/') {
        router.push('/');
      }
    },
    async fetchPendingApplicationsCount() {
        // 仅当用户是管理员时才获取
        const userClass = localStorage.getItem('user-class');
        const token = localStorage.getItem('token');
        
        // 如果没有token或者不是管理员，直接返回
        if (!token || userClass !== '管理员') {
            this.setPendingApplicationsCount(0);
            return;
        }
        
        try {
            const response = await getPendingApplicationsCount();
            this.setPendingApplicationsCount(response.pending_count);
        } catch (error) {
            console.error("获取待处理申请数量失败:", error);
            this.setPendingApplicationsCount(0);
            // 不显示错误通知，让全局错误处理器处理
        }
    },
    async fetchPendingFacesCount() {
      const userClass = localStorage.getItem('user-class');
      const token = localStorage.getItem('token');
      if (!token || userClass !== '管理员') {
          this.setPendingFacesCount(0);
          return;
      }
      try {
          const response = await apiGetPendingFacesCount();
          this.setPendingFacesCount(response.pending_count);
      } catch (error) {
          console.error("获取待审批人脸数量失败:", error);
          this.setPendingFacesCount(0);
      }
    },
    async fetchUserProfile() {
      try {
        const userData = await getUserProfile();
        this.setUser(userData);
        // 获取用户信息后，接着获取待处理数量
        await this.fetchPendingApplicationsCount();
        await this.fetchPendingFacesCount(); // 获取待审批人脸数量
      } catch (error) {
        console.error("获取用户信息失败:", error);
        this.setUser(null);
        // 不显示错误通知，让全局错误处理器处理
      }
    }
  }
}); 
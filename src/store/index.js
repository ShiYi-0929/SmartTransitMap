import { defineStore } from 'pinia';
import { getUserProfile, getPendingApplicationsCount } from '@/api/user'; // 假设API路径

export const useMainStore = defineStore('main', {
  state: () => ({
    user: null,
    pendingApplicationsCount: 0,
  }),
  actions: {
    setUser(user) {
      this.user = user;
    },
    setPendingApplicationsCount(count) {
        this.pendingApplicationsCount = count;
    },
    async fetchPendingApplicationsCount() {
        // 仅当用户是管理员时才获取
        const userClass = localStorage.getItem('user-class');
        if (userClass === '管理员') {
            try {
                const response = await getPendingApplicationsCount();
                this.setPendingApplicationsCount(response.pending_count);
            } catch (error) {
                console.error("获取待处理申请数量失败:", error);
                this.setPendingApplicationsCount(0); // Or handle error appropriately
            }
        }
    },
    async fetchUserProfile() {
      try {
        const userData = await getUserProfile();
        this.setUser(userData);
        // 获取用户信息后，接着获取待处理数量
        await this.fetchPendingApplicationsCount();
      } catch (error) {
        console.error("获取用户信息失败:", error);
        this.setUser(null);
      }
    }
  }
}); 
import { getPendingApplicationsCount, getUserProfile } from '@/api/user'; // 假设API路径
import { defineStore } from 'pinia';

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
    async fetchUserProfile() {
      try {
        const userData = await getUserProfile();
        this.setUser(userData);
        // 获取用户信息后，接着获取待处理数量
        await this.fetchPendingApplicationsCount();
      } catch (error) {
        console.error("获取用户信息失败:", error);
        this.setUser(null);
        // 不显示错误通知，让全局错误处理器处理
      }
    }
  }
}); 
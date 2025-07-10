// // store/index.js
// import { defineStore } from 'pinia'
//
// export const useMainStore = defineStore('main', {
//   state: () => ({
//     // 项目原有状态（用户信息）
//     user: null,
//
//     // 你的状态（从 Vuex 迁移）
//     settings: {
//       theme: "light",
//       language: "zh-CN",
//       autoRefresh: true,
//     },
//     statistics: {
//       todayDetections: 0,
//       totalDamages: 0,
//       todayGrowth: 0,
//     },
//     alarms: [],
//     detectionHistory: [],
//   }),
//
//   actions: {
//     // 项目原有 action（设置用户）
//     setUser(user) {
//       this.user = user
//     },
//
//     // 你的 action（从 Vuex mutations/actions 迁移）
//     // 更新系统设置
//     updateSettings(settings) {
//       this.settings = { ...this.settings, ...settings }
//     },
//
//     // 更新统计信息
//     async updateStatistics() {
//       try {
//         // 模拟 API 调用（替换为真实接口）
//         const mockStats = {
//           todayDetections: Math.floor(Math.random() * 50) + 10,
//           totalDamages: Math.floor(Math.random() * 100) + 20,
//           todayGrowth: Math.floor(Math.random() * 20) - 10,
//         }
//         this.statistics = { ...this.statistics, ...mockStats }
//       } catch (error) {
//         console.error("更新统计信息失败:", error)
//       }
//     },
//
//     // 添加告警
//     addAlarm(alarm) {
//       this.alarms.unshift({ id: Date.now(), ...alarm }) // 自动添加唯一id
//     },
//
//     // 移除告警
//     removeAlarm(alarmId) {
//       this.alarms = this.alarms.filter(alarm => alarm.id !== alarmId)
//     },
//
//     // 清空告警
//     clearAlarms() {
//       this.alarms = []
//     },
//
//     // 添加检测记录
//     addDetectionRecord(record) {
//       this.detectionHistory.unshift({
//         id: Date.now(),
//         timestamp: new Date(),
//         ...record
//       })
//     },
//   },
//
//   getters: {
//     // 你的 getters（从 Vuex getters 迁移）
//     getAlarmCount: (state) => state.alarms.length,
//     getSettings: (state) => state.settings,
//     getStatistics: (state) => state.statistics,
//     getDetectionHistory: (state) => state.detectionHistory,
//   }
// })



// store/index.js
import { defineStore } from 'pinia'
import { createPinia } from 'pinia'

export const useMainStore = defineStore('main', {
  state: () => ({
    // 项目原有状态（用户信息）
    user: null,

    // 你的状态（从 Vuex 迁移）
    settings: {
      theme: "light",
      language: "zh-CN",
      autoRefresh: true,
    },
    statistics: {
      todayDetections: 0,
      totalDamages: 0,
      todayGrowth: 0,
    },
    alarms: [],
    detectionHistory: [],
  }),

  actions: {
    // 项目原有 action（设置用户）
    setUser(user) {
      this.user = user
    },

    // 你的 action（从 Vuex mutations/actions 迁移）
    // 更新系统设置
    updateSettings(settings) {
      this.settings = { ...this.settings, ...settings }
    },

    // 更新统计信息
    async updateStatistics() {
      try {
        // 模拟 API 调用（替换为真实接口）
        const mockStats = {
          todayDetections: Math.floor(Math.random() * 50) + 10,
          totalDamages: Math.floor(Math.random() * 100) + 20,
          todayGrowth: Math.floor(Math.random() * 20) - 10,
        }
        this.statistics = { ...this.statistics, ...mockStats }
      } catch (error) {
        console.error("更新统计信息失败:", error)
      }
    },

    // 添加告警
    addAlarm(alarm) {
      this.alarms.unshift({ id: Date.now(), ...alarm }) // 自动添加唯一id
    },

    // 移除告警
    removeAlarm(alarmId) {
      this.alarms = this.alarms.filter(alarm => alarm.id !== alarmId)
    },

    // 清空告警
    clearAlarms() {
      this.alarms = []
    },

    // 添加检测记录
    addDetectionRecord(record) {
      this.detectionHistory.unshift({
        id: Date.now(),
        timestamp: new Date(),
        ...record
      })
    },
  },

  getters: {
    // 你的 getters（从 Vuex getters 迁移）
    getAlarmCount: (state) => state.alarms.length,
    getSettings: (state) => state.settings,
    getStatistics: (state) => state.statistics,
    getDetectionHistory: (state) => state.detectionHistory,
  }
})

// 创建pinia实例
const pinia = createPinia()

// 为了兼容Vue2的store格式，提供默认导出
export default {
  install(app) {
    app.use(pinia)
  },
  state: {
    user: null,
    settings: {
      theme: "light",
      language: "zh-CN",
      autoRefresh: true,
    },
    statistics: {
      todayDetections: 0,
      totalDamages: 0,
      todayGrowth: 0,
    },
    alarms: [],
    detectionHistory: [],
  }
}

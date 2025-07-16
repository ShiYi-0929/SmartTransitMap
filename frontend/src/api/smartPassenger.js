import request from './index'

// 智能客运分析API
export const smartPassengerAPI = {
  // 获取载客车辆时间线数据（新API，替换旧的出租车需求分析）
  async getLoadedVehiclesTimeline(date, timeResolution = 15) {
    try {
      const response = await request.get('/traffic/smart-passenger/loaded-vehicles-timeline', {
        params: {
          date: date, // 格式：YYYY-MM-DD
          time_resolution: timeResolution // 时间分辨率（分钟）
        }
      })
      return response.data
    } catch (error) {
      console.error('获取载客车辆时间线失败:', error)
      return {
        success: false,
        message: '获取载客车辆时间线失败',
        data: []
      }
    }
  },

  // 天气影响分析
  async analyzeWeatherImpact(params) {
    try {
      const response = await request.post('/traffic/smart-passenger/weather-impact', params)
      return response.data
    } catch (error) {
      console.error('天气影响分析失败:', error)
      return {
        success: false,
        message: '天气影响分析失败',
        weather_impact_analysis: []
      }
    }
  },

  // 获取历史分析数据
  async getHistoricalAnalysis() {
    try {
      const response = await request.get('/traffic/smart-passenger/historical')
      return response.data
    } catch (error) {
      console.error('获取历史分析数据失败:', error)
      return {
        success: false,
        message: '获取历史分析数据失败',
        historical_data: null
      }
    }
  },

  // 每日天气影响分析
  async analyzeDailyWeatherImpact(params) {
    try {
      const response = await request.post('/traffic/smart-passenger/daily-weather-impact', params)
      return response.data
    } catch (error) {
      console.error('每日天气影响分析失败:', error)
      return {
        success: false,
        message: '每日天气影响分析失败',
        daily_impacts: []
      }
    }
  }
} 
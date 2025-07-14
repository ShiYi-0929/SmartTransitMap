import axios from 'axios'

const API_BASE_URL = '/api'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 响应拦截器
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('智能客流API错误:', error)
    return Promise.reject(error)
  }
)

export const smartPassengerAPI = {
  // 智能客运监控分析
  async analyzeSmartPassenger(params = {}) {
    try {
      const requestData = {
        analysis_type: params.analysis_type || 'comprehensive',
        include_weather: params.include_weather !== false,
        include_taxi_analysis: params.include_taxi_analysis !== false,
        min_passenger_threshold: params.min_passenger_threshold || 1,
        weather_correlation: params.weather_correlation !== false,
        time_resolution: params.time_resolution || 15
      }
      
      console.log('🚀 发送智能客运分析请求:', requestData)
      const response = await apiClient.post('/smart-passenger/analysis', requestData)
      console.log('✅ 智能客运分析响应:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ 智能客运分析失败:', error)
      throw error
    }
  },

  // 天气影响分析
  async analyzeWeatherImpact(params = {}) {
    try {
      const requestData = {
        include_prediction: params.include_prediction || false,
        correlation_threshold: params.correlation_threshold || 0.3,
        time_window: params.time_window || '7d'
      }
      
      console.log('🌤️ 发送天气影响分析请求:', requestData)
      const response = await apiClient.post('/smart-passenger/weather-impact', requestData)
      console.log('✅ 天气影响分析响应:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ 天气影响分析失败:', error)
      throw error
    }
  },

  // 出租车需求分析
  async analyzeTaxiDemand(params = {}) {
    try {
      const requestData = {
        historical_analysis: params.historical_analysis !== false,
        include_prediction: params.include_prediction || false,
        hotspot_analysis: params.hotspot_analysis !== false,
        time_window: params.time_window || '1h'
      }
      
      console.log('🚕 发送出租车需求分析请求:', requestData)
      const response = await apiClient.post('/smart-passenger/taxi-demand', requestData)
      console.log('✅ 出租车需求分析响应:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ 出租车需求分析失败:', error)
      throw error
    }
  },

  // 获取客运可视化数据
  async getVisualizationData(params = {}) {
    try {
      const requestData = {
        visualization_type: params.visualization_type || 'comprehensive',
        time_range: params.time_range || {
          start: Date.now() / 1000 - 3600, // 1小时前
          end: Date.now() / 1000
        },
        include_heatmap: params.include_heatmap !== false,
        include_weather_correlation: params.include_weather_correlation !== false,
        include_taxi_demand_map: params.include_taxi_demand_map !== false
      }
      
      console.log('📊 发送可视化数据请求:', requestData)
      const response = await apiClient.post('/smart-passenger/visualization', requestData)
      console.log('✅ 可视化数据响应:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ 获取可视化数据失败:', error)
      throw error
    }
  },

  // 获取历史客运分析数据
  async getHistoricalAnalysis() {
    try {
      console.log('📊 获取历史客运分析数据')
      const response = await apiClient.get('/api/smart-passenger/historical')
      console.log('✅ 历史分析数据响应:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ 获取历史分析数据失败:', error)
      throw error
    }
  }
}

export default smartPassengerAPI 
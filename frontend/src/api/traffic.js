import axios from 'axios'

// 配置axios默认超时时间
axios.defaults.timeout = 60000; // 60秒超时，因为数据处理需要时间

// 配置后端服务器地址
const API_BASE_URL = 'http://localhost:8000';

export function getTrafficStats(startTime, endTime, groupBy) {
  return axios.get(`${API_BASE_URL}/api/traffic/stats`, { 
    params: { start_time: startTime, end_time: endTime, group_by: groupBy } 
  })
}

export function getTrafficVisualization(startTime, endTime, viewType, vehicleId, mapStyle, limit = 5000) {
  return axios.get(`${API_BASE_URL}/api/traffic/visualization`, { 
    params: { 
      start_time: startTime, 
      end_time: endTime, 
      view_type: viewType, 
      vehicle_id: vehicleId, 
      map_style: mapStyle,
      limit: limit
    } 
  })
}

// 新增：获取数据文件信息
export function getDataFilesInfo() {
  return axios.get(`${API_BASE_URL}/api/traffic/files/info`)
}

// 新增：获取交通数据概要统计
export function getTrafficSummary() {
  return axios.get(`${API_BASE_URL}/api/traffic/summary`)
}

export function getTrackData(params) {
  return axios.get(`${API_BASE_URL}/api/traffic/track`, { params })
}

export function getSampleVehicles(startTime, endTime, limit) {
  return axios.get(`${API_BASE_URL}/api/traffic/sample-vehicles`, { 
    params: { 
      start_time: startTime, 
      end_time: endTime, 
      limit: limit || 50 
    } 
  })
}

export function getHeatmapData(startTime, endTime, resolution) {
  return axios.get(`${API_BASE_URL}/api/traffic/heatmap`, { 
    params: { start_time: startTime, end_time: endTime, resolution } 
  })
}

export function detectAnomalies(startTime, endTime, detectionTypes, thresholdParams) {
  return axios.get(`${API_BASE_URL}/api/traffic/anomaly/detection`, { 
    params: { 
      start_time: startTime, 
      end_time: endTime, 
      detection_types: detectionTypes,
      threshold_params: JSON.stringify(thresholdParams)
    } 
  })
}

export function getRealtimeAnomalies(timeWindow, limit) {
  return axios.get(`${API_BASE_URL}/api/traffic/anomaly/realtime`, { 
    params: { time_window: timeWindow, limit } 
  })
}

export function getAnomalyTypes() {
  return axios.get(`${API_BASE_URL}/api/traffic/anomaly/types`)
}

export function getAnomalyHeatmap(startTime, endTime, anomalyType, resolution) {
  return axios.get(`${API_BASE_URL}/api/traffic/anomaly/heatmap`, { 
    params: { 
      start_time: startTime, 
      end_time: endTime, 
      anomaly_type: anomalyType, 
      resolution 
    } 
  })
}

export function getDynamicHeatmap(startTime, endTime, temporalResolution, spatialResolution, smoothing) {
  return axios.get(`${API_BASE_URL}/api/traffic/spatiotemporal/dynamic-heatmap`, { 
    params: { 
      start_time: startTime, 
      end_time: endTime, 
      temporal_resolution: temporalResolution, 
      spatial_resolution: spatialResolution, 
      smoothing 
    } 
  })
}

export function performClustering(startTime, endTime, request) {
  return axios.post(`${API_BASE_URL}/api/traffic/spatiotemporal/clustering`, request, { 
    params: { start_time: startTime, end_time: endTime } 
  })
}

export function performODAnalysis(startTime, endTime, request) {
  return axios.post(`${API_BASE_URL}/api/traffic/spatiotemporal/od-analysis`, request, { 
    params: { start_time: startTime, end_time: endTime } 
  })
}

export function performComprehensiveAnalysis(startTime, endTime, heatmapRequest) {
  return axios.post(`${API_BASE_URL}/api/traffic/spatiotemporal/comprehensive`, heatmapRequest, { 
    params: { start_time: startTime, end_time: endTime } 
  })
}

export function getAvailableAlgorithms() {
  return axios.get(`${API_BASE_URL}/api/traffic/spatiotemporal/algorithms`)
}

export function analyzeRoadSegments(request) {
  return axios.post(`${API_BASE_URL}/api/traffic/road/analysis`, request)
}

export function performRoadAnalysis(config) {
  return axios.post(`${API_BASE_URL}/api/traffic/road/analysis`, config)
}

export function getRoadSegments() {
  return axios.get(`${API_BASE_URL}/api/traffic/road/segments`)
}

export function getRoadTrafficData(timeRange) {
  return axios.post(`${API_BASE_URL}/api/traffic/road/traffic`, timeRange)
}

export function getRoadVisualizationData(request) {
  return axios.post(`${API_BASE_URL}/api/traffic/road/visualization`, request)
}

export function getRoadNetworkMetrics() {
  return axios.get(`${API_BASE_URL}/api/traffic/road/metrics`)
}

export function getWeeklyPassengerFlowAnalysis(startTime, endTime) {
  return axios.get(`${API_BASE_URL}/api/traffic/weekly-passenger-flow`, { 
    params: { start_time: startTime, end_time: endTime } 
  })
}

// 交通日志相关API
export function getTrafficLogs(params = {}) {
  return axios.get(`${API_BASE_URL}/api/traffic/logs`, { params })
}

export function getTrafficLogStats() {
  return axios.get(`${API_BASE_URL}/api/traffic/logs/stats`)
}

export function clearTrafficLogs() {
  return axios.delete(`${API_BASE_URL}/api/traffic/logs`)
}

export function addTrafficLog(logData) {
  return axios.post(`${API_BASE_URL}/api/traffic/logs`, logData)
}

export function sendTrafficAlert(message) {
  return axios.post(`${API_BASE_URL}/api/traffic/alert`, { message })
} 

// 路程分析API - 使用高级版API路径
export const roadAPI = {
  tripAnalysis(config) {
    // 根据选择的日期调整时间范围
    let startTime, endTime
    
    if (config.selected_date && config.selected_date !== 'all') {
      // 特定日期的时间戳映射
      const dateMap = {
        '2013-09-11': { start: 1378857600, end: 1378943999 },  // 2013-09-11 00:00:00 - 23:59:59 UTC
        '2013-09-12': { start: 1378944000, end: 1379030399 },  // 2013-09-12 00:00:00 - 23:59:59 UTC
        '2013-09-13': { start: 1379030400, end: 1379116799 },  // 2013-09-13 00:00:00 - 23:59:59 UTC
        '2013-09-14': { start: 1379116800, end: 1379203199 },  // 2013-09-14 00:00:00 - 23:59:59 UTC
        '2013-09-15': { start: 1379203200, end: 1379289599 },  // 2013-09-15 00:00:00 - 23:59:59 UTC
        '2013-09-16': { start: 1379289600, end: 1379375999 },  // 2013-09-16 00:00:00 - 23:59:59 UTC
        '2013-09-17': { start: 1379376000, end: 1379462399 },  // 2013-09-17 00:00:00 - 23:59:59 UTC
        '2013-09-18': { start: 1379462400, end: 1379548799 }   // 2013-09-18 00:00:00 - 23:59:59 UTC
      }
      
      const dateRange = dateMap[config.selected_date]
      if (dateRange) {
        startTime = dateRange.start
        endTime = dateRange.end
      } else {
        // 默认全部日期
        startTime = 1378857600  // 2013-09-11 00:00:00 UTC
        endTime = 1379548799    // 2013-09-18 23:59:59 UTC
      }
    } else {
      // 全部日期
      startTime = 1378857600  // 2013-09-11 00:00:00 UTC
      endTime = 1379548799    // 2013-09-18 23:59:59 UTC
    }
    
    return axios.post(`${API_BASE_URL}/api/traffic/road/trip-analysis?start_time=${startTime}&end_time=${endTime}`, config)
  },
  
  orderSpeedAnalysis(config) {
    // 使用高级版API路径，需要传递时间戳参数
    const startTime = 1378944000  // 2013-09-12 00:00:00 UTC
    const endTime = 1379548799    // 2013-09-18 23:59:59 UTC
    
    // 添加详细的调试信息
    console.log('=== API orderSpeedAnalysis 调用 ===')
    console.log('请求配置:', JSON.stringify(config, null, 2))
    console.log('时间范围:', { startTime, endTime })
    
    const url = `${API_BASE_URL}/api/traffic/road/order-speed-analysis?start_time=${startTime}&end_time=${endTime}`
    console.log('请求URL:', url)
    console.log('请求方法: POST')
    console.log('请求体:', JSON.stringify(config, null, 2))
    
    // 发送请求前的额外检查
    console.log('axios对象:', axios)
    console.log('当前时间:', new Date().toISOString())
    
    // 为此API设置更长的超时时间
    const requestConfig = {
      timeout: 120000, // 2分钟超时
      headers: {
        'Content-Type': 'application/json'
      }
    }
    
    return axios.post(url, config, requestConfig)
      .then(response => {
        console.log('=== API 响应成功 ===')
        console.log('响应状态:', response.status)
        console.log('响应头:', response.headers)
        console.log('响应数据:', response.data)
        console.log('响应数据类型:', typeof response.data)
        return response
      })
      .catch(error => {
        console.error('=== API 请求失败 ===')
        console.error('错误类型:', error.constructor.name)
        console.error('错误消息:', error.message)
        
        if (error.response) {
          console.error('HTTP错误响应:')
          console.error('  状态码:', error.response.status)
          console.error('  状态文本:', error.response.statusText)
          console.error('  响应头:', error.response.headers)
          console.error('  响应数据:', error.response.data)
        } else if (error.request) {
          console.error('网络请求错误:')
          console.error('  请求对象:', error.request)
          console.error('  请求状态:', error.request.readyState)
          console.error('  请求URL:', error.request.responseURL)
          console.error('  请求超时:', error.code === 'ECONNABORTED' ? '是' : '否')
        } else {
          console.error('配置错误:', error.message)
        }
        
        throw error
      })
  },
  
  comprehensiveAnalysis(config) {
    // 综合分析可以调用两个API
    return Promise.all([
      this.tripAnalysis(config),
      this.orderSpeedAnalysis(config)
    ])
  }
}
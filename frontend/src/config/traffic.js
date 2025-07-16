// 交通分析配置文件
export const trafficConfig = {
  // 地图配置
  map: {
    center: [117.02, 36.67], // 济南市中心坐标 [lng, lat]
    zoom: 12,
    style: 'amap://styles/blue',
    apiKey: process.env.VUE_APP_AMAP_KEY || 'ac9b745946df9aee02cf0515319407df',
    apiUrl: 'https://webapi.amap.com/maps?v=2.0'
  },
  
  // 时间配置
  time: {
    // 默认时间范围
    defaultStartTime: new Date(Date.now() - 24 * 60 * 60 * 1000), // 24小时前
    defaultEndTime: new Date(), // 当前时间
    
    // 数据有效时间范围（从后端获取）
    validTimeRange: {
      min: 1378944000, // 2013-09-12 00:00:00 UTC
      max: 1379548799  // 2013-09-18 23:59:59 UTC
    }
  },
  
  // 分析配置
  analysis: {
    analysis_type: 'comprehensive',
    segment_types: ['all'],
    aggregation_level: 'segment',
    include_patterns: true,
    min_vehicles: 1
  },
  
  // 分页配置
  pagination: {
    pageSize: 50
  },
  
  // API配置
  api: {
    baseUrl: '/api/traffic/road/analysis',
    timeout: 60000,
    configEndpoint: '/api/traffic/config/time-range'
  },
  
  // 可视化配置
  visualization: {
    defaultType: 'speed',
    colors: {
      free: '#27ae60',
      moderate: '#f39c12', 
      heavy: '#e74c3c',
      jam: '#c0392b'
    }
  }
}

// 环境特定配置
export const getConfig = () => {
  const env = process.env.NODE_ENV || 'development'
  
  const envConfig = {
    development: {
      api: {
        baseUrl: 'http://localhost:8000/api/traffic/road/analysis',
        timeout: 120000 // 开发环境增加超时时间
      }
    },
    production: {
      api: {
        baseUrl: '/api/traffic/road/analysis',
        timeout: 60000
      }
    }
  }
  
  return {
    ...trafficConfig,
    ...envConfig[env]
  }
}

// 动态配置加载器
export class ConfigLoader {
  static async load() {
    try {
      // 尝试从API加载配置
      const response = await fetch('/api/config/traffic')
      if (response.ok) {
        const apiConfig = await response.json()
        return { ...getConfig(), ...apiConfig }
      }
    } catch (error) {
      console.warn('无法从API加载配置，使用默认配置:', error)
    }
    
    return getConfig()
  }
  
  static async getValidTimeRange() {
    try {
      const config = getConfig()
      const response = await fetch(config.api.configEndpoint)
      if (response.ok) {
        const data = await response.json()
        return data.validTimeRange || config.time.validTimeRange
      }
    } catch (error) {
      console.warn('无法获取有效时间范围，使用默认值:', error)
    }
    
    return getConfig().time.validTimeRange
  }
} 
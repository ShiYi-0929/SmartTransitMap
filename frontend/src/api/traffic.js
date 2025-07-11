import axios from 'axios'

export function getTrafficStats(startTime, endTime, groupBy) {
  return axios.get('/api/traffic/stats', { 
    params: { start_time: startTime, end_time: endTime, group_by: groupBy } 
  })
}

export function getTrafficVisualization(startTime, endTime, viewType, vehicleId, mapStyle) {
  return axios.get('/api/traffic/visualization', { 
    params: { 
      start_time: startTime, 
      end_time: endTime, 
      view_type: viewType, 
      vehicle_id: vehicleId, 
      map_style: mapStyle 
    } 
  })
}

export function getTrackData(params) {
  return axios.get('/api/traffic/track', { params })
}

export function getSampleVehicles(startTime, endTime, limit) {
  return axios.get('/api/traffic/sample-vehicles', { 
    params: { 
      start_time: startTime, 
      end_time: endTime, 
      limit: limit || 50 
    } 
  })
}

export function getHeatmapData(startTime, endTime, resolution) {
  return axios.get('/api/traffic/heatmap', { 
    params: { start_time: startTime, end_time: endTime, resolution } 
  })
}

export function detectAnomalies(startTime, endTime, detectionTypes, thresholdParams) {
  return axios.get('/api/traffic/anomaly/detection', { 
    params: { 
      start_time: startTime, 
      end_time: endTime, 
      detection_types: detectionTypes,
      threshold_params: JSON.stringify(thresholdParams)
    } 
  })
}

export function getRealtimeAnomalies(timeWindow, limit) {
  return axios.get('/api/traffic/anomaly/realtime', { 
    params: { time_window: timeWindow, limit } 
  })
}

export function getAnomalyTypes() {
  return axios.get('/api/traffic/anomaly/types')
}

export function getAnomalyHeatmap(startTime, endTime, anomalyType, resolution) {
  return axios.get('/api/traffic/anomaly/heatmap', { 
    params: { 
      start_time: startTime, 
      end_time: endTime, 
      anomaly_type: anomalyType, 
      resolution 
    } 
  })
}

export function getDynamicHeatmap(startTime, endTime, temporalResolution, spatialResolution, smoothing) {
  return axios.get('/api/traffic/spatiotemporal/dynamic-heatmap', { 
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
  return axios.post('/api/traffic/spatiotemporal/clustering', request, { 
    params: { start_time: startTime, end_time: endTime } 
  })
}

export function performODAnalysis(startTime, endTime, request) {
  return axios.post('/api/traffic/spatiotemporal/od-analysis', request, { 
    params: { start_time: startTime, end_time: endTime } 
  })
}

export function performComprehensiveAnalysis(startTime, endTime, heatmapRequest) {
  return axios.post('/api/traffic/spatiotemporal/comprehensive', heatmapRequest, { 
    params: { start_time: startTime, end_time: endTime } 
  })
}

export function getAvailableAlgorithms() {
  return axios.get('/api/traffic/spatiotemporal/algorithms')
}

export function analyzeRoadSegments(request) {
  return axios.post('/api/traffic/api/road/analysis', request)
}

export function performRoadAnalysis(config) {
  return axios.post('/api/traffic/api/road/analysis', config)
}

export function getRoadSegments() {
  return axios.get('/api/traffic/api/road/segments')
}

export function getRoadTrafficData(timeRange) {
  return axios.post('/api/traffic/api/road/traffic', timeRange)
}

export function getRoadVisualizationData(request) {
  return axios.post('/api/traffic/api/road/visualization', request)
}

export function getRoadNetworkMetrics() {
  return axios.get('/api/traffic/api/road/metrics')
}

export function getWeeklyPassengerFlowAnalysis(startTime, endTime) {
  return axios.get('/api/traffic/weekly-passenger-flow', { 
    params: { start_time: startTime, end_time: endTime } 
  })
} 
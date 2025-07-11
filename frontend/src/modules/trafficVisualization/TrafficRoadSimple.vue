<template>
  <div class="road-segment-analysis">
    <!-- 标题栏 -->
    <div class="analysis-header">
      <h2>路段数据分析</h2>
      <p class="subtitle">展示不同路段的通行状况、速度、距离等指标</p>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <div class="panel-row">
        <!-- 分析类型选择 -->
        <div class="control-group">
          <label>分析类型:</label>
          <select v-model="analysisConfig.analysis_type" @change="onConfigChange">
            <option value="comprehensive">综合分析</option>
            <option value="speed">速度分析</option>
            <option value="flow">流量分析</option>
            <option value="congestion">拥堵分析</option>
          </select>
        </div>

        <!-- 路段类型筛选 -->
        <div class="control-group">
          <label>路段类型:</label>
          <select v-model="analysisConfig.segment_types[0]" @change="onConfigChange">
            <option value="all">全部路段</option>
            <option value="highway">高速公路</option>
            <option value="arterial">主干道</option>
            <option value="urban">城市道路</option>
            <option value="local">支路</option>
          </select>
        </div>

        <!-- 可视化类型 -->
        <div class="control-group">
          <label>可视化:</label>
          <select v-model="visualizationType" @change="onVisualizationChange">
            <option value="speed">速度分布</option>
            <option value="flow">流量分布</option>
            <option value="congestion">拥堵程度</option>
            <option value="efficiency">运行效率</option>
          </select>
        </div>

        <!-- 最小车辆数 -->
        <div class="control-group">
          <label>最小车辆数:</label>
          <input 
            type="number" 
            v-model.number="analysisConfig.min_vehicles" 
            min="1" 
            max="50"
            @change="onConfigChange"
          />
        </div>

        <!-- 分析按钮 -->
        <div class="control-group">
          <button 
            @click="performAnalysis" 
            :disabled="isLoading"
            class="analyze-btn"
          >
            {{ isLoading ? '分析中...' : '开始分析' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards" v-if="analysisData">
      <div class="stat-card">
        <div class="stat-value">{{ analysisData.analysis?.total_segments || 0 }}</div>
        <div class="stat-label">总路段数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ activeSegments }}</div>
        <div class="stat-label">活跃路段</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ avgSpeed }}</div>
        <div class="stat-label">平均速度 (km/h)</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ avgFlow }}</div>
        <div class="stat-label">平均流量 (veh/h)</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ bottleneckCount }}</div>
        <div class="stat-label">瓶颈路段</div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 地图可视化区域 -->
      <div class="map-section">
        <div class="map-header">
          <h3>路段可视化地图</h3>
          <div class="map-controls">
            <button @click="refreshVisualization" :disabled="isLoading">
              刷新可视化
            </button>
            <button @click="exportData" :disabled="!analysisData">
              导出数据
            </button>
          </div>
        </div>
        
        <!-- 地图容器 -->
        <div class="map-container">
          <div 
            id="road-analysis-map-simple" 
            class="map-canvas"
            v-show="mapLoaded"
          ></div>
          <div 
            v-show="!mapLoaded" 
            class="map-fallback"
          >
            <canvas 
              ref="fallbackCanvas"
              class="fallback-canvas"
              width="800"
              height="600"
            ></canvas>
            <div class="canvas-overlay">
              <p>{{ loadingMessage }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据分析面板 -->
      <div class="analysis-panel">
        <!-- 速度分布图表 -->
        <div class="chart-section" v-if="speedDistributions && speedDistributions.length > 0">
          <h3>速度分布</h3>
          <div class="speed-chart">
            <div 
              v-for="dist in speedDistributions" 
              :key="dist.speed_range"
              class="speed-bar"
            >
              <div class="bar-container">
                <div 
                  class="bar-fill"
                  :style="{ width: dist.percentage + '%' }"
                ></div>
                <span class="bar-label">{{ dist.speed_range }}</span>
              </div>
              <div class="bar-value">{{ dist.percentage.toFixed(1) }}%</div>
            </div>
          </div>
        </div>

        <!-- 路段详情列表 -->
        <div class="segments-list" v-if="segmentDetails && segmentDetails.length > 0">
          <h3>路段详情</h3>
          <div class="segments-table">
            <div class="table-header">
              <div class="col-id">路段ID</div>
              <div class="col-type">类型</div>
              <div class="col-length">长度(km)</div>
              <div class="col-speed">平均速度</div>
              <div class="col-flow">流量</div>
              <div class="col-congestion">拥堵状态</div>
            </div>
            <div class="table-body">
              <div 
                v-for="segment in paginatedSegments" 
                :key="segment.segment_id"
                class="table-row"
                @click="selectSegment(segment)"
                :class="{ active: selectedSegment?.segment_id === segment.segment_id }"
              >
                <div class="col-id">{{ segment.segment_id }}</div>
                <div class="col-type">{{ getRoadTypeLabel(segment.road_type) }}</div>
                <div class="col-length">{{ segment.segment_length?.toFixed(3) || 'N/A' }}</div>
                <div class="col-speed">{{ segment.avg_speed?.toFixed(1) || 'N/A' }}</div>
                <div class="col-flow">{{ segment.flow_rate?.toFixed(0) || 'N/A' }}</div>
                <div class="col-congestion">
                  <span :class="'congestion-' + segment.congestion_level">
                    {{ getCongestionLabel(segment.congestion_level) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 网络指标摘要 -->
        <div class="network-summary" v-if="networkMetrics">
          <h3>路网指标摘要</h3>
          <div class="metrics-grid">
            <div class="metric-item">
              <div class="metric-label">网络平均速度</div>
              <div class="metric-value">{{ networkMetrics.traffic_performance?.avg_speed?.toFixed(1) || 'N/A' }} km/h</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">网络利用率</div>
              <div class="metric-value">{{ networkMetrics.efficiency_indicators?.network_utilization?.toFixed(1) || 'N/A' }}%</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">畅通率</div>
              <div class="metric-value">{{ networkMetrics.efficiency_indicators?.free_flow_percentage?.toFixed(1) || 'N/A' }}%</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">瓶颈率</div>
              <div class="metric-value">{{ networkMetrics.efficiency_indicators?.bottleneck_rate?.toFixed(1) || 'N/A' }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载遮罩 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>正在分析路段数据，请稍候...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrafficRoadSimple',
  data() {
    return {
      isLoading: false,
      mapLoaded: false,
      map: null,
      loadingMessage: '地图加载中，使用Canvas降级显示',
      
      // 分析配置
      analysisConfig: {
        analysis_type: 'comprehensive',
        segment_types: ['all'],
        aggregation_level: 'segment',
        include_patterns: true,
        min_vehicles: 10
      },
      
      // 可视化配置
      visualizationType: 'speed',
      
      // 分析数据
      analysisData: null,
      visualizationData: null,
      networkMetrics: null,
      
      // 图表数据
      speedDistributions: [],
      flowPatterns: [],
      
      // 路段数据
      segmentDetails: [],
      selectedSegment: null,
      
      // 分页
      currentPage: 1,
      pageSize: 10
    }
  },
  
  computed: {
    activeSegments() {
      return this.analysisData?.analysis?.segments_data?.length || 0
    },
    
    avgSpeed() {
      const summary = this.analysisData?.analysis?.network_summary
      return summary?.network_avg_speed?.toFixed(1) || 'N/A'
    },
    
    avgFlow() {
      if (!this.segmentDetails || this.segmentDetails.length === 0) return 'N/A'
      const totalFlow = this.segmentDetails.reduce((sum, s) => sum + (s.flow_rate || 0), 0)
      return (totalFlow / this.segmentDetails.length).toFixed(0)
    },
    
    bottleneckCount() {
      return this.analysisData?.analysis?.bottleneck_segments?.length || 0
    },
    
    paginatedSegments() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.segmentDetails.slice(start, end)
    },
    
    totalPages() {
      return Math.ceil(this.segmentDetails.length / this.pageSize)
    }
  },
  
  mounted() {
    this.initializeComponent()
  },

  beforeUnmount() {
    this.cleanup()
  },
  
  methods: {
    async initializeComponent() {
      try {
        await this.initializeMap()
        await this.performAnalysis()
      } catch (error) {
        console.error('初始化路段分析组件失败:', error)
      }
    },
    
    async initializeMap() {
      try {
        this.loadingMessage = '正在初始化地图...'
        
        // 检查地图容器是否存在
        await this.$nextTick()
        const mapContainer = document.getElementById('road-analysis-map-simple')
        if (!mapContainer) {
          console.warn('地图容器不存在，使用Canvas降级模式')
          this.mapLoaded = false
          this.initializeFallbackCanvas()
          return
        }

        // 尝试加载地图API
        if (typeof window !== 'undefined' && window.AMap) {
          this.map = new window.AMap.Map('road-analysis-map-simple', {
            zoom: 11,
            center: [117.120, 36.651], // 济南市中心
            mapStyle: 'amap://styles/blue',
            viewMode: '2D'
          })
          
          this.map.on('complete', () => {
            console.log('路段分析地图加载完成')
            this.mapLoaded = true
          })
          
          this.map.on('error', (error) => {
            console.error('路段分析地图加载错误:', error)
            this.mapLoaded = false
            this.initializeFallbackCanvas()
          })
        } else {
          console.warn('地图API未加载，使用Canvas降级模式')
          this.mapLoaded = false
          this.initializeFallbackCanvas()
        }
        
      } catch (error) {
        console.warn('地图初始化失败，使用Canvas降级模式:', error)
        this.mapLoaded = false
        this.initializeFallbackCanvas()
      }
    },
    
    initializeFallbackCanvas() {
      this.loadingMessage = '地图API未加载，使用Canvas显示'
      this.$nextTick(() => {
        const canvas = this.$refs.fallbackCanvas
        if (canvas) {
          const ctx = canvas.getContext('2d')
          
          // 绘制背景
          ctx.fillStyle = '#f8f9fa'
          ctx.fillRect(0, 0, 800, 600)
          
          // 绘制标题
          ctx.fillStyle = '#333'
          ctx.font = 'bold 24px Arial'
          ctx.textAlign = 'center'
          ctx.fillText('路段分析地图', 400, 200)
          
          ctx.font = '16px Arial'
          ctx.fillText('(Canvas降级模式)', 400, 230)
          
          // 绘制模拟路段
          const roadSegments = [
            { x: 200, y: 300, width: 150, height: 20, color: '#4CAF50', label: '高速公路' },
            { x: 400, y: 350, width: 120, height: 15, color: '#2196F3', label: '主干道' },
            { x: 300, y: 400, width: 100, height: 12, color: '#FF9800', label: '城市道路' }
          ]
          
          roadSegments.forEach(segment => {
            ctx.fillStyle = segment.color
            ctx.fillRect(segment.x, segment.y, segment.width, segment.height)
            
            ctx.fillStyle = '#333'
            ctx.font = '12px Arial'
            ctx.textAlign = 'left'
            ctx.fillText(segment.label, segment.x, segment.y - 5)
          })
          
          // 绘制说明
          ctx.fillStyle = '#666'
          ctx.font = '14px Arial'
          ctx.textAlign = 'center'
          ctx.fillText('数据分析完成后将在此显示路段分布', 400, 500)
        }
      })
    },
    
    async performAnalysis() {
      this.isLoading = true
      try {
        console.log('开始执行路段分析，配置:', this.analysisConfig)
        
        // 模拟分析过程
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // 加载模拟数据
        this.loadMockData()
        
        console.log('路段分析完成，找到路段数:', this.segmentDetails.length)
        
      } catch (error) {
        console.error('路段分析失败:', error)
        // 仍然加载模拟数据
        this.loadMockData()
      } finally {
        this.isLoading = false
      }
    },

    // 加载模拟数据
    loadMockData() {
      console.log('加载模拟数据用于演示')
      this.analysisData = {
        success: true,
        analysis: {
          total_segments: 25,
          network_summary: {
            network_avg_speed: 45.8
          }
        }
      }
      
      this.segmentDetails = [
        {
          segment_id: 'S001',
          road_type: 'highway',
          segment_length: 2.5,
          avg_speed: 65.2,
          flow_rate: 1200,
          congestion_level: 'free'
        },
        {
          segment_id: 'S002', 
          road_type: 'arterial',
          segment_length: 1.8,
          avg_speed: 35.5,
          flow_rate: 800,
          congestion_level: 'moderate'
        },
        {
          segment_id: 'S003',
          road_type: 'urban',
          segment_length: 1.2,
          avg_speed: 25.0,
          flow_rate: 600,
          congestion_level: 'heavy'
        },
        {
          segment_id: 'S004',
          road_type: 'highway',
          segment_length: 3.1,
          avg_speed: 70.1,
          flow_rate: 1500,
          congestion_level: 'free'
        },
        {
          segment_id: 'S005',
          road_type: 'local',
          segment_length: 0.8,
          avg_speed: 20.5,
          flow_rate: 300,
          congestion_level: 'moderate'
        }
      ]
      
      this.speedDistributions = [
        { speed_range: '0-30 km/h', percentage: 25.5 },
        { speed_range: '30-50 km/h', percentage: 45.2 },
        { speed_range: '50-80 km/h', percentage: 29.3 }
      ]
      
      this.networkMetrics = {
        traffic_performance: {
          avg_speed: 45.8
        },
        efficiency_indicators: {
          network_utilization: 72.5,
          free_flow_percentage: 65.8,
          bottleneck_rate: 12.3
        }
      }
      
      console.log('模拟数据加载完成')
    },
    
    cleanup() {
      // 清理地图实例
      if (this.map) {
        try {
          this.map.clearMap()
          this.map.destroy()
          this.map = null
        } catch (error) {
          console.warn('清理地图实例时出错:', error)
        }
      }
      
      // 重置状态
      this.mapLoaded = false
      console.log('路段分析组件清理完成')
    },
    
    onConfigChange() {
      console.log('配置变更:', this.analysisConfig)
      // 延迟执行分析，避免频繁请求
      setTimeout(() => {
        this.performAnalysis()
      }, 1000)
    },
    
    onVisualizationChange() {
      console.log('可视化类型变更:', this.visualizationType)
    },
    
    refreshVisualization() {
      console.log('刷新可视化')
      this.initializeFallbackCanvas()
    },
    
    selectSegment(segment) {
      this.selectedSegment = segment
      console.log('选中路段:', segment.segment_id)
    },
    
    exportData() {
      if (!this.analysisData) return
      
      const data = {
        analysis_summary: this.analysisData.analysis,
        segment_details: this.segmentDetails,
        network_metrics: this.networkMetrics,
        export_time: new Date().toISOString()
      }
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `road_analysis_${Date.now()}.json`
      a.click()
      URL.revokeObjectURL(url)
      
      console.log('数据导出成功')
    },
    
    getRoadTypeLabel(type) {
      const labels = {
        highway: '高速公路',
        arterial: '主干道',
        urban: '城市道路',
        local: '支路'
      }
      return labels[type] || type
    },
    
    getCongestionLabel(level) {
      const labels = {
        free: '畅通',
        moderate: '缓慢',
        heavy: '拥堵',
        severe: '严重拥堵'
      }
      return labels[level] || level
    }
  }
}
</script>

<style scoped>
/* 基础样式 */
.road-segment-analysis {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.analysis-header {
  text-align: center;
  margin-bottom: 30px;
}

.analysis-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 14px;
}

/* 控制面板 */
.control-panel {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.panel-row {
  display: flex;
  gap: 20px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.control-group label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.control-group select,
.control-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.analyze-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 20px;
}

.analyze-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 统计卡片 */
.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
  flex: 1;
  min-width: 120px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #7f8c8d;
}

/* 主要内容 */
.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.map-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
}

.map-header {
  padding: 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.map-header h3 {
  margin: 0;
  color: #2c3e50;
}

.map-controls {
  display: flex;
  gap: 10px;
}

.map-controls button {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.map-container {
  position: relative;
  height: 400px;
}

.map-canvas,
.map-fallback {
  width: 100%;
  height: 100%;
}

.fallback-canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.canvas-overlay {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255,255,255,0.9);
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

/* 分析面板 */
.analysis-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chart-section h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 16px;
}

/* 速度图表 */
.speed-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.speed-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-container {
  flex: 1;
  position: relative;
  height: 24px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #2196F3);
  transition: width 0.3s ease;
}

.bar-label {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #333;
  z-index: 1;
}

.bar-value {
  min-width: 50px;
  text-align: right;
  font-size: 12px;
  color: #666;
}

/* 路段列表 */
.segments-list {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.segments-table {
  border: 1px solid #eee;
  border-radius: 4px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 80px 80px 80px 80px 60px 80px;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.table-header > div {
  padding: 10px 8px;
  font-size: 12px;
  font-weight: bold;
  color: #666;
  border-right: 1px solid #eee;
}

.table-row {
  display: grid;
  grid-template-columns: 80px 80px 80px 80px 60px 80px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f0f0f0;
}

.table-row:hover {
  background: #f8f9fa;
}

.table-row.active {
  background: #e3f2fd;
}

.table-row > div {
  padding: 10px 8px;
  font-size: 12px;
  border-right: 1px solid #f0f0f0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 拥堵状态样式 */
.congestion-free {
  color: #4CAF50;
  font-weight: bold;
}

.congestion-moderate {
  color: #FF9800;
  font-weight: bold;
}

.congestion-heavy {
  color: #F44336;
  font-weight: bold;
}

/* 网络指标 */
.network-summary {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.metric-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.metric-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

/* 加载遮罩 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  color: white;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .panel-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-cards {
    flex-direction: column;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style> 
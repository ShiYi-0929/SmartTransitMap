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
            id="road-analysis-map" 
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
              <p>地图加载中，使用Canvas降级显示</p>
            </div>
          </div>
        </div>

        <!-- 图例 -->
        <div class="legend" v-if="legendInfo && legendInfo.ranges">
          <h4>{{ legendInfo.title }}</h4>
          <div class="legend-items">
            <div 
              v-for="(range, index) in legendInfo.ranges" 
              :key="index"
              class="legend-item"
            >
              <div 
                class="legend-color" 
                :style="{ backgroundColor: range.color }"
              ></div>
              <span class="legend-label">{{ range.label }}</span>
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

        <!-- 流量模式图表 -->
        <div class="chart-section" v-if="flowPatterns && flowPatterns.length > 0">
          <h3>24小时流量模式</h3>
          <div class="flow-chart">
            <svg width="100%" height="200" viewBox="0 0 800 200">
              <g transform="translate(40,20)">
                <!-- 背景网格 -->
                <g class="grid">
                  <line v-for="i in 5" :key="'h'+i" 
                        :x1="0" :x2="720" 
                        :y1="i*36" :y2="i*36" 
                        stroke="#e0e0e0" stroke-width="1"/>
                  <line v-for="i in 25" :key="'v'+i" 
                        :x1="i*30" :x2="i*30" 
                        :y1="0" :y2="180" 
                        stroke="#e0e0e0" stroke-width="0.5"/>
                </g>
                
                <!-- 流量曲线 -->
                <polyline 
                  :points="getFlowPolylinePoints()"
                  fill="none" 
                  stroke="#2196F3" 
                  stroke-width="2"
                />
                
                <!-- 拥堵指数曲线 -->
                <polyline 
                  :points="getCongestionPolylinePoints()"
                  fill="none" 
                  stroke="#F44336" 
                  stroke-width="2"
                />
                
                <!-- X轴标签 -->
                <g class="x-axis">
                  <text v-for="hour in [0,6,12,18,24]" :key="hour"
                        :x="hour*30" y="195" 
                        text-anchor="middle" 
                        font-size="12" 
                        fill="#666">
                    {{ hour }}:00
                  </text>
                </g>
              </g>
            </svg>
            <div class="chart-legend">
              <span class="legend-item">
                <span class="legend-line flow"></span>
                流量
              </span>
              <span class="legend-item">
                <span class="legend-line congestion"></span>
                拥堵指数
              </span>
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
              <div class="col-action">操作</div>
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
                <div class="col-action">
                  <button @click.stop="focusOnSegment(segment)" class="focus-btn">
                    定位
                  </button>
                </div>
              </div>
            </div>
            <!-- 分页控制 -->
            <div class="pagination" v-if="totalPages > 1">
              <button 
                @click="currentPage = Math.max(1, currentPage - 1)"
                :disabled="currentPage === 1"
              >
                上一页
              </button>
              <span>{{ currentPage }} / {{ totalPages }}</span>
              <button 
                @click="currentPage = Math.min(totalPages, currentPage + 1)"
                :disabled="currentPage === totalPages"
              >
                下一页
              </button>
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
import { 
  performRoadAnalysis, 
  getRoadVisualizationData, 
  getRoadNetworkMetrics 
} from '@/api/traffic'

export default {
  name: 'TrafficRoad',
  data() {
    return {
      isLoading: false,
      mapLoaded: false,
      map: null,
      
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
      pageSize: 10,
      
      // 图例信息
      legendInfo: null
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
        // 尝试初始化高德地图
        if (typeof AMap !== 'undefined') {
          this.map = new AMap.Map('road-analysis-map', {
            zoom: 11,
            center: [116.397, 39.916],
            mapStyle: 'amap://styles/blue'
          })
          this.mapLoaded = true
        } else {
          console.warn('高德地图API未加载，使用Canvas降级模式')
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
      this.$nextTick(() => {
        const canvas = this.$refs.fallbackCanvas
        if (canvas) {
          const ctx = canvas.getContext('2d')
          ctx.fillStyle = '#f0f0f0'
          ctx.fillRect(0, 0, 800, 600)
          
          ctx.fillStyle = '#666'
          ctx.font = '16px Arial'
          ctx.textAlign = 'center'
          ctx.fillText('路段分析地图', 400, 300)
          ctx.fillText('(Canvas降级模式)', 400, 320)
        }
      })
    },
    
    async performAnalysis() {
      this.isLoading = true
      try {
        // 执行路段分析
        const analysisResult = await performRoadAnalysis(this.analysisConfig)
        
        if (analysisResult.success) {
          this.analysisData = analysisResult
          this.speedDistributions = analysisResult.speed_distributions || []
          this.flowPatterns = analysisResult.flow_patterns || []
          
          // 构建路段详情数据
          this.buildSegmentDetails()
          
          // 获取网络指标
          await this.loadNetworkMetrics()
          
          // 更新可视化
          await this.updateVisualization()
          
          this.$message.success('路段分析完成')
        } else {
          this.$message.error(`分析失败: ${analysisResult.message}`)
        }
      } catch (error) {
        console.error('路段分析失败:', error)
        this.$message.error('分析过程中发生错误')
      } finally {
        this.isLoading = false
      }
    },
    
    buildSegmentDetails() {
      if (!this.analysisData) return
      
      const segments = this.analysisData.analysis?.segments_data || []
      const trafficData = this.analysisData.traffic_data || []
      
      // 创建路段到交通数据的映射
      const trafficMap = {}
      trafficData.forEach(data => {
        if (!trafficMap[data.segment_id]) {
          trafficMap[data.segment_id] = []
        }
        trafficMap[data.segment_id].push(data)
      })
      
      // 构建详情数据
      this.segmentDetails = segments.map(segment => {
        const traffic = trafficMap[segment.segment_id] || []
        const avgTraffic = this.calculateAverageTraffic(traffic)
        
        return {
          ...segment,
          ...avgTraffic
        }
      })
    },
    
    calculateAverageTraffic(trafficList) {
      if (!trafficList || trafficList.length === 0) {
        return {
          avg_speed: 0,
          flow_rate: 0,
          congestion_level: 'unknown'
        }
      }
      
      const avgSpeed = trafficList.reduce((sum, t) => sum + t.avg_speed, 0) / trafficList.length
      const avgFlow = trafficList.reduce((sum, t) => sum + t.flow_rate, 0) / trafficList.length
      
      // 取最常见的拥堵等级
      const congestionCounts = {}
      trafficList.forEach(t => {
        congestionCounts[t.congestion_level] = (congestionCounts[t.congestion_level] || 0) + 1
      })
      
      const mostCommonCongestion = Object.keys(congestionCounts).reduce((a, b) => 
        congestionCounts[a] > congestionCounts[b] ? a : b
      )
      
      return {
        avg_speed: avgSpeed,
        flow_rate: avgFlow,
        congestion_level: mostCommonCongestion
      }
    },
    
    async loadNetworkMetrics() {
      try {
        const metricsResult = await getRoadNetworkMetrics()
        if (metricsResult.success) {
          this.networkMetrics = metricsResult.metrics
        }
      } catch (error) {
        console.error('加载网络指标失败:', error)
      }
    },
    
    async updateVisualization() {
      try {
        const params = {
          visualization_type: this.visualizationType,
          time_range: {
            start: Date.now() / 1000 - 3600,
            end: Date.now() / 1000
          }
        }
        
        const vizResult = await getRoadVisualizationData(params)
        
        if (vizResult.success) {
          this.visualizationData = vizResult.visualization_data
          this.legendInfo = vizResult.legend_info
          
          // 更新地图显示
          this.renderSegmentsOnMap()
        }
      } catch (error) {
        console.error('更新可视化失败:', error)
      }
    },
    
    renderSegmentsOnMap() {
      if (!this.visualizationData) return
      
      if (this.mapLoaded && this.map) {
        this.renderSegmentsOnAMap()
      } else {
        this.renderSegmentsOnCanvas()
      }
    },
    
    renderSegmentsOnAMap() {
      // 清除现有图层
      this.map.clearMap()
      
      const segments = this.visualizationData.segments || []
      
      segments.forEach(segment => {
        const startPoint = [segment.start_point.lng, segment.start_point.lat]
        const endPoint = [segment.end_point.lng, segment.end_point.lat]
        
        const polyline = new AMap.Polyline({
          path: [startPoint, endPoint],
          strokeColor: segment.color,
          strokeWeight: 4,
          strokeOpacity: 0.8
        })
        
        this.map.add(polyline)
        
        // 添加点击事件
        polyline.on('click', () => {
          this.showSegmentInfo(segment)
        })
      })
      
      // 调整地图视野
      if (segments.length > 0) {
        const bounds = new AMap.Bounds()
        segments.forEach(segment => {
          bounds.extend([segment.start_point.lng, segment.start_point.lat])
          bounds.extend([segment.end_point.lng, segment.end_point.lat])
        })
        this.map.setBounds(bounds)
      }
    },
    
    renderSegmentsOnCanvas() {
      const canvas = this.$refs.fallbackCanvas
      if (!canvas) return
      
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, 800, 600)
      
      // 绘制背景
      ctx.fillStyle = '#f8f9fa'
      ctx.fillRect(0, 0, 800, 600)
      
      // 绘制路段（简化显示）
      const segments = this.visualizationData.segments || []
      
      if (segments.length > 0) {
        segments.forEach((segment, index) => {
          const x = (index % 10) * 80 + 40
          const y = Math.floor(index / 10) * 60 + 40
          
          ctx.fillStyle = segment.color
          ctx.fillRect(x, y, 60, 40)
          
          ctx.fillStyle = '#333'
          ctx.font = '10px Arial'
          ctx.fillText(segment.segment_id.slice(-4), x + 5, y + 15)
          ctx.fillText(`${segment.value}`, x + 5, y + 30)
        })
      }
      
      // 绘制标题
      ctx.fillStyle = '#333'
      ctx.font = '16px Arial'
      ctx.fillText('路段可视化 (Canvas模式)', 20, 25)
    },
    
    async onConfigChange() {
      // 延迟执行分析，避免频繁请求
      clearTimeout(this.configChangeTimer)
      this.configChangeTimer = setTimeout(() => {
        this.performAnalysis()
      }, 1000)
    },
    
    async onVisualizationChange() {
      await this.updateVisualization()
    },
    
    async refreshVisualization() {
      await this.updateVisualization()
    },
    
    selectSegment(segment) {
      this.selectedSegment = segment
    },
    
    focusOnSegment(segment) {
      if (this.mapLoaded && this.map) {
        const center = [
          (segment.start_point.lng + segment.end_point.lng) / 2,
          (segment.start_point.lat + segment.end_point.lat) / 2
        ]
        this.map.setCenter(center)
        this.map.setZoom(15)
      }
      
      this.selectSegment(segment)
      this.$message.success(`已定位到路段: ${segment.segment_id}`)
    },
    
    showSegmentInfo(segment) {
      this.$message.info(`路段 ${segment.segment_id}: ${segment.value}`)
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
      
      this.$message.success('数据导出成功')
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
        jam: '严重拥堵'
      }
      return labels[level] || level
    },
    
    getFlowPolylinePoints() {
      if (!this.flowPatterns || this.flowPatterns.length === 0) return ''
      
      const maxFlow = Math.max(...this.flowPatterns.map(p => p.avg_flow))
      return this.flowPatterns.map(pattern => {
        const x = pattern.hour * 30
        const y = 180 - (pattern.avg_flow / maxFlow * 160)
        return `${x},${y}`
      }).join(' ')
    },
    
    getCongestionPolylinePoints() {
      if (!this.flowPatterns || this.flowPatterns.length === 0) return ''
      
      return this.flowPatterns.map(pattern => {
        const x = pattern.hour * 30
        const y = 180 - (pattern.congestion_index * 160)
        return `${x},${y}`
      }).join(' ')
    }
  }
}
</script> 

<style scoped>
.road-segment-analysis {
  padding: 20px;
  background: #f8f9fa;
  min-height: 100vh;
}

.analysis-header {
  text-align: center;
  margin-bottom: 20px;
}

.analysis-header h2 {
  color: #2c3e50;
  margin-bottom: 8px;
}

.subtitle {
  color: #7f8c8d;
  margin: 0;
}

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
  flex-wrap: wrap;
  align-items: center;
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

.legend {
  padding: 15px;
  border-top: 1px solid #eee;
}

.legend h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 14px;
}

.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 2px;
}

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
  background: #f5f5f5;
  border-radius: 12px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #2196F3);
  border-radius: 12px;
  transition: width 0.3s ease;
}

.bar-label {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  color: #333;
  font-weight: 500;
}

.bar-value {
  min-width: 40px;
  font-size: 12px;
  color: #666;
  text-align: right;
}

.flow-chart {
  margin-top: 10px;
}

.chart-legend {
  display: flex;
  gap: 20px;
  margin-top: 10px;
  justify-content: center;
}

.legend-line {
  display: inline-block;
  width: 20px;
  height: 2px;
  margin-right: 5px;
}

.legend-line.flow {
  background: #2196F3;
}

.legend-line.congestion {
  background: #F44336;
}

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

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 80px 60px 70px 70px 60px 80px 50px;
  align-items: center;
}

.table-header {
  background: #f8f9fa;
  font-weight: 600;
  font-size: 12px;
  color: #2c3e50;
  padding: 12px 8px;
  border-bottom: 1px solid #eee;
}

.table-row {
  padding: 10px 8px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 12px;
}

.table-row:hover {
  background: #f8f9fa;
}

.table-row.active {
  background: #e3f2fd;
}

.table-row > div {
  padding: 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.congestion-free { color: #4CAF50; }
.congestion-moderate { color: #FF9800; }
.congestion-heavy { color: #F44336; }
.congestion-jam { color: #D32F2F; }

.focus-btn {
  padding: 4px 8px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 10px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background: #f8f9fa;
}

.pagination button {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.pagination button:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

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

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255,255,255,0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .panel-row {
    justify-content: center;
  }
  
  .stats-cards {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 5px;
  }
  
  .table-header > div,
  .table-row > div {
    padding: 5px;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style> 
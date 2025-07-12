<template>
    <div class="road-analysis-advanced">
      <!-- 标题栏 -->
      <div class="analysis-header">
        <h2>路段智能分析</h2>
        <p class="subtitle">路程分析 | 订单速度分析</p>
      </div>
  
      <!-- 功能选择面板 -->
      <div class="feature-tabs">
        <div 
          class="tab-item"
          :class="{ active: activeTab === 'trip' }"
          @click="switchTab('trip')"
        >
          📊 路程分析
        </div>
        <div 
          class="tab-item"
          :class="{ active: activeTab === 'speed' }"
          @click="switchTab('speed')"
        >
          🚗 订单速度分析
        </div>
      </div>
  
      <!-- 路程分析面板 -->
      <div v-if="activeTab === 'trip'" class="analysis-content">
        <div class="control-panel">
          <div class="panel-row">
            <div class="control-group">
              <label>分析日期:</label>
              <select v-model="tripConfig.selected_date">
                <option value="all">全部日期</option>
                <option value="2013-09-11">2013年9月11日</option>
                <option value="2013-09-12">2013年9月12日</option>
                <option value="2013-09-13">2013年9月13日</option>
                <option value="2013-09-14">2013年9月14日</option>
                <option value="2013-09-15">2013年9月15日</option>
                <option value="2013-09-16">2013年9月16日</option>
                <option value="2013-09-17">2013年9月17日</option>
                <option value="2013-09-18">2013年9月18日</option>
              </select>
            </div>
            <div class="control-group">
              <label>最小订单数:</label>
              <input type="number" v-model.number="tripConfig.min_trip_count" min="5" max="100">
            </div>
            <div class="control-group">
              <button @click="performTripAnalysis" :disabled="isLoading" class="analyze-btn">
                {{ isLoading ? '分析中...' : '开始路程分析' }}
              </button>
            </div>
          </div>
        </div>
  
        <!-- 路程分析结果 -->
        <div v-if="tripAnalysisData" class="trip-results">
          <!-- 统计卡片 -->
          <div class="stats-cards">
            <div class="stat-card trip-short">
              <div class="stat-value">{{ tripStats.shortTripPercentage }}%</div>
              <div class="stat-label">短途(<4km)</div>
              <div class="stat-count">{{ tripStats.shortTripCount }} 单</div>
            </div>
            <div class="stat-card trip-medium">
              <div class="stat-value">{{ tripStats.mediumTripPercentage }}%</div>
              <div class="stat-label">中途(4-8km)</div>
              <div class="stat-count">{{ tripStats.mediumTripCount }} 单</div>
            </div>
            <div class="stat-card trip-long">
              <div class="stat-value">{{ tripStats.longTripPercentage }}%</div>
              <div class="stat-label">长途(>8km)</div>
              <div class="stat-count">{{ tripStats.longTripCount }} 单</div>
            </div>
            <div class="stat-card trip-total">
              <div class="stat-value">{{ tripStats.totalTrips }}</div>
              <div class="stat-label">总订单数</div>
              <div class="stat-extra">{{ tripStats.avgDistance }}km 平均距离</div>
            </div>
          </div>
  
          <!-- 路程分布图表 -->
          <div class="chart-section">
            <h3>路程分布图表 
              <span v-if="tripConfig.selected_date !== 'all'" class="date-indicator">
                ({{ formatSelectedDate(tripConfig.selected_date) }})
              </span>
              <span v-else class="date-indicator">(全部日期)</span>
            </h3>
            <div class="chart-container">
              <canvas ref="tripChartCanvas" class="trip-chart" width="600" height="400"></canvas>
            </div>
          </div>
  
          <!-- 日期明细表 -->
          <div class="daily-breakdown" v-if="tripAnalysisData.daily_classifications">
            <h3>日期明细 
              <span v-if="tripConfig.selected_date !== 'all'" class="date-indicator">
                ({{ formatSelectedDate(tripConfig.selected_date) }})
              </span>
              <span v-else class="date-indicator">(全部日期)</span>
            </h3>
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>日期</th>
                    <th>短途订单</th>
                    <th>中途订单</th>
                    <th>长途订单</th>
                    <th>总订单</th>
                    <th>平均距离</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="filteredDailyClassifications.length === 0">
                    <td colspan="6" class="no-data">
                      {{ tripAnalysisData ? '没有匹配的数据' : '请点击"开始路程分析"按钮进行分析' }}
                    </td>
                  </tr>
                  <tr v-for="day in filteredDailyClassifications" :key="day.date">
                    <td>{{ day.date }}</td>
                    <td>{{ day.short_trips }} ({{ (day.short_percentage || 0).toFixed(1) }}%)</td>
                    <td>{{ day.medium_trips }} ({{ (day.medium_percentage || 0).toFixed(1) }}%)</td>
                    <td>{{ day.long_trips }} ({{ (day.long_percentage || 0).toFixed(1) }}%)</td>
                    <td>{{ day.total_trips }}</td>
                    <td>{{ (day.avg_distance || 0).toFixed(2) }}km</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 订单速度分析面板 -->
      <div v-if="activeTab === 'speed'" class="analysis-content">
        <div class="control-panel">
          <div class="panel-row">
            <div class="control-group">
              <label>分析范围:</label>
              <select v-model="speedConfig.include_short_medium_only" @change="onSpeedConfigChange">
                <option :value="true">仅中短途订单(≤8km)</option>
                <option :value="false">全部订单</option>
              </select>
            </div>
            <div class="control-group">
              <label>空间分辨率:</label>
              <select v-model="speedConfig.spatial_resolution" @change="onSpeedConfigChange">
                <option value="0.001">高精度(100m)</option>
                <option value="0.005">中等(500m)</option>
                <option value="0.01">低精度(1km)</option>
              </select>
            </div>
            <div class="control-group">
              <label>最小订单数:</label>
              <input type="number" v-model.number="speedConfig.min_orders_per_location" min="3" max="20">
            </div>
            <div class="control-group">
              <button @click="performSpeedAnalysis" :disabled="isLoading" class="analyze-btn">
                {{ isLoading ? '分析中...' : '开始速度分析' }}
              </button>
            </div>
          </div>
        </div>
  
        <!-- 速度分析结果 -->
        <div v-if="speedAnalysisData" class="speed-results">
          <!-- 拥堵统计卡片 -->
          <div class="stats-cards">
            <div class="stat-card congestion-free">
              <div class="stat-value">{{ congestionStats.freeCount }}</div>
              <div class="stat-label">畅通区域</div>
              <div class="stat-extra">>40km/h</div>
            </div>
            <div class="stat-card congestion-moderate">
              <div class="stat-value">{{ congestionStats.moderateCount }}</div>
              <div class="stat-label">缓慢区域</div>
              <div class="stat-extra">25-40km/h</div>
            </div>
            <div class="stat-card congestion-heavy">
              <div class="stat-value">{{ congestionStats.heavyCount }}</div>
              <div class="stat-label">拥堵区域</div>
              <div class="stat-extra">15-25km/h</div>
            </div>
            <div class="stat-card congestion-jam">
              <div class="stat-value">{{ congestionStats.jamCount }}</div>
              <div class="stat-label">严重拥堵</div>
              <div class="stat-extra"><15km/h</div>
            </div>
          </div>
  
          <!-- 速度热力图 -->
          <div class="map-section">
            <h3>道路速度热力图</h3>
            <div class="map-container">
              <div class="speed-map">
                <canvas ref="speedHeatmapCanvas" class="heatmap-canvas" width="800" height="600"></canvas>
              </div>
              <div class="heatmap-legend">
                <div class="legend-item free">畅通</div>
                <div class="legend-item moderate">缓慢</div>
                <div class="legend-item heavy">拥堵</div>
                <div class="legend-item jam">严重拥堵</div>
              </div>
            </div>
          </div>
  
          <!-- 拥堵区域详情 -->
          <div class="congestion-details">
            <h3>拥堵区域详情</h3>
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>位置</th>
                    <th>平均速度</th>
                    <th>订单数量</th>
                    <th>拥堵等级</th>
                    <th>置信度</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(area, index) in topCongestionAreas" :key="index">
                    <td>{{ formatLocation(area.location) }}</td>
                    <td>{{ area.avg_speed.toFixed(1) }}km/h</td>
                    <td>{{ area.order_count }}</td>
                    <td>
                      <span :class="'congestion-' + area.congestion_level">
                        {{ getCongestionLabel(area.congestion_level) }}
                      </span>
                    </td>
                    <td>{{ (area.confidence_score * 100).toFixed(0) }}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 综合分析面板 -->
      <div v-if="activeTab === 'comprehensive'" class="analysis-content">
        <div class="control-panel">
          <div class="panel-row">
            <div class="control-group">
              <button @click="performComprehensiveAnalysis" :disabled="isLoading" class="analyze-btn">
                {{ isLoading ? '分析中...' : '开始综合分析' }}
              </button>
            </div>
            <div class="control-group">
              <button @click="exportAllData" :disabled="!hasAnyData" class="export-btn">
                导出全部数据
              </button>
            </div>
          </div>
        </div>
  
        <!-- 综合分析结果 -->
        <div v-if="comprehensiveData" class="comprehensive-results">
          <div class="overview-grid">
            <div class="overview-card">
              <h4>路程分析概览</h4>
              <div class="quick-stats">
                <div class="quick-stat">
                  <span class="label">主要出行距离:</span>
                  <span class="value">{{ dominantTripType }}</span>
                </div>
                <div class="quick-stat">
                  <span class="label">平均出行距离:</span>
                  <span class="value">{{ avgTripDistance }}km</span>
                </div>
              </div>
            </div>
            
            <div class="overview-card">
              <h4>道路速度概览</h4>
              <div class="quick-stats">
                <div class="quick-stat">
                  <span class="label">整体平均速度:</span>
                  <span class="value">{{ avgRoadSpeed }}km/h</span>
                </div>
                <div class="quick-stat">
                  <span class="label">拥堵程度:</span>
                  <span class="value">{{ overallCongestionLevel }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 加载遮罩 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>{{ loadingMessage }}</p>
      </div>
    </div>
  </template>
  
  <script>
  import { roadAPI } from '../../api/traffic'
  
  export default {
    name: 'TrafficRoadAdvanced',
    data() {
      return {
        isLoading: false,
        loadingMessage: '分析中...',
        activeTab: 'trip',
        
        // 路程分析配置
        tripConfig: {
          min_trip_count: 10,
          selected_date: 'all'
        },
        
        // 速度分析配置（保持不变）
        speedConfig: {
          speed_analysis_type: 'comprehensive',
          include_short_medium_only: true,
          spatial_resolution: 0.005,
          min_orders_per_location: 5
        },
        
        // 分析数据
        tripAnalysisData: null,
        speedAnalysisData: null,
        comprehensiveData: null
      }
    },
    
    computed: {
      // 路程统计
      tripStats() {
        if (!this.tripAnalysisData?.overall_stats) {
          return {
            shortTripCount: 0,
            mediumTripCount: 0,
            longTripCount: 0,
            totalTrips: 0,
            shortTripPercentage: '0.0',
            mediumTripPercentage: '0.0',
            longTripPercentage: '0.0',
            avgDistance: '0.00'
          }
        }
        
        // 如果选择了特定日期，优先显示该日期的数据
        if (this.tripConfig.selected_date !== 'all' && this.tripAnalysisData.daily_classifications) {
          const selectedDayData = this.tripAnalysisData.daily_classifications.find(
            day => day.date === this.tripConfig.selected_date
          )
          
          if (selectedDayData) {
            return {
              shortTripCount: selectedDayData.short_trips || 0,
              mediumTripCount: selectedDayData.medium_trips || 0,
              longTripCount: selectedDayData.long_trips || 0,
              totalTrips: selectedDayData.total_trips || 0,
              shortTripPercentage: (selectedDayData.short_percentage || 0).toFixed(1),
              mediumTripPercentage: (selectedDayData.medium_percentage || 0).toFixed(1),
              longTripPercentage: (selectedDayData.long_percentage || 0).toFixed(1),
              avgDistance: (selectedDayData.avg_distance || 0).toFixed(2)
            }
          }
        }
        
        // 否则显示整体统计
        const stats = this.tripAnalysisData.overall_stats
        return {
          shortTripCount: stats.short_trips_total || 0,
          mediumTripCount: stats.medium_trips_total || 0,
          longTripCount: stats.long_trips_total || 0,
          totalTrips: stats.total_trips || 0,
          shortTripPercentage: (stats.overall_short_percentage || 0).toFixed(1),
          mediumTripPercentage: (stats.overall_medium_percentage || 0).toFixed(1),
          longTripPercentage: (stats.overall_long_percentage || 0).toFixed(1),
          avgDistance: (stats.overall_avg_distance || 0).toFixed(2)
        }
      },
      
      // 拥堵统计
      congestionStats() {
        if (!this.speedAnalysisData?.speed_data) return {
          freeCount: 0,
          moderateCount: 0,
          heavyCount: 0,
          jamCount: 0
        }
        
        const data = this.speedAnalysisData.speed_data
        const counts = { free: 0, moderate: 0, heavy: 0, jam: 0 }
        
        data.forEach(item => {
          counts[item.congestion_level] = (counts[item.congestion_level] || 0) + 1
        })
        
        return {
          freeCount: counts.free,
          moderateCount: counts.moderate,
          heavyCount: counts.heavy,
          jamCount: counts.jam
        }
      },
      
      // 前十拥堵区域
      topCongestionAreas() {
        if (!this.speedAnalysisData?.speed_data) return []
        return this.speedAnalysisData.speed_data
          .filter(item => item.congestion_level === 'heavy' || item.congestion_level === 'jam')
          .sort((a, b) => a.avg_speed - b.avg_speed)
          .slice(0, 10)
      },
      
      // 过滤后的日期分类数据
      filteredDailyClassifications() {
        if (!this.tripAnalysisData?.daily_classifications) {
          return []
        }
        
        // 如果选择了特定日期，只显示该日期的数据
        if (this.tripConfig.selected_date !== 'all') {
          const filtered = this.tripAnalysisData.daily_classifications.filter(
            day => day.date === this.tripConfig.selected_date
          )
          return filtered
        }
        
        // 否则显示所有日期的数据
        return this.tripAnalysisData.daily_classifications
      },
      
      // 是否有任何数据
      hasAnyData() {
        return this.tripAnalysisData || this.speedAnalysisData || this.comprehensiveData
      },
      
      // 综合分析计算属性
      dominantTripType() {
        if (!this.tripAnalysisData?.trend_analysis) return '数据不足'
        const category = this.tripAnalysisData.trend_analysis.most_common_distance_category
        const labels = {
          'short_distance': '短途出行',
          'medium_distance': '中途出行', 
          'long_distance': '长途出行'
        }
        return labels[category] || '未知'
      },
      
      avgTripDistance() {
        return this.tripStats.avgDistance || '0.00'
      },
      
      avgRoadSpeed() {
        if (!this.speedAnalysisData?.congestion_summary) return '0.0'
        return (this.speedAnalysisData.congestion_summary.overall_avg_speed || 0).toFixed(1)
      },
      
      overallCongestionLevel() {
        const stats = this.congestionStats
        const total = stats.freeCount + stats.moderateCount + stats.heavyCount + stats.jamCount
        if (total === 0) return '无数据'
        
        const jamRate = stats.jamCount / total
        const heavyRate = stats.heavyCount / total
        
        if (jamRate > 0.3) return '严重拥堵'
        if (heavyRate + jamRate > 0.5) return '拥堵'
        if (stats.moderateCount / total > 0.5) return '缓慢'
        return '畅通'
      }
    },
    
    mounted() {
      this.initializeComponent()
    },
    
    methods: {
      initializeComponent() {
        // 默认执行路程分析
        this.performTripAnalysis()
      },
      
      switchTab(tab) {
        this.activeTab = tab
        if (tab === 'trip' && !this.tripAnalysisData) {
          this.performTripAnalysis()
        } else if (tab === 'speed' && !this.speedAnalysisData) {
          this.performSpeedAnalysis()
        } else if (tab === 'comprehensive' && !this.comprehensiveData) {
          this.performComprehensiveAnalysis()
        }
      },
      
      async performTripAnalysis() {
        try {
          this.isLoading = true
          this.loadingMessage = '正在分析路程数据...'
          
          const response = await roadAPI.tripAnalysis({
            min_trip_count: this.tripConfig.min_trip_count,
            selected_date: this.tripConfig.selected_date
          })
          
          console.log('路程分析API响应:', response)
          
          // 处理API响应
          if (response.data) {
            // axios 封装的响应格式
            this.tripAnalysisData = response.data.analysis_result
          } else {
            // 直接的响应格式
            this.tripAnalysisData = response.analysis_result
          }
          
          console.log('处理后的路程分析数据:', this.tripAnalysisData)
          
          // 绘制图表
          this.$nextTick(() => {
            this.drawTripChart()
          })
          
        } catch (error) {
          console.error('路程分析失败:', error)
          if (this.$message?.error) {
            this.$message.error('路程分析失败，请重试')
          } else {
            alert('路程分析失败，请重试')
          }
        } finally {
          this.isLoading = false
        }
      },
      
      async performSpeedAnalysis() {
        try {
          this.isLoading = true
          this.loadingMessage = '正在分析订单速度...'
          
          const response = await roadAPI.orderSpeedAnalysis(this.speedConfig)
          this.speedAnalysisData = response.speed_analysis
          
          // 绘制图表和热力图
          this.$nextTick(() => {
            this.drawSpeedHeatmap()
          })
          
        } catch (error) {
          console.error('速度分析失败:', error)
          // 兼容不同的消息提示方式
          if (this.$message?.error) {
            this.$message.error('速度分析失败，请重试')
          } else if (this.$notify) {
            this.$notify.error({ title: '错误', message: '速度分析失败，请重试' })
          } else {
            alert('速度分析失败，请重试')
          }
        } finally {
          this.isLoading = false
        }
      },
      
      async performComprehensiveAnalysis() {
        try {
          this.isLoading = true
          this.loadingMessage = '正在进行综合分析...'
          
          // 并行执行两个分析
          await Promise.all([
            this.tripAnalysisData ? Promise.resolve() : this.performTripAnalysis(),
            this.speedAnalysisData ? Promise.resolve() : this.performSpeedAnalysis()
          ])
          
          // 生成综合数据
          this.comprehensiveData = {
            tripData: this.tripAnalysisData,
            speedData: this.speedAnalysisData,
            timestamp: Date.now()
          }
          
        } catch (error) {
          console.error('综合分析失败:', error)
          // 兼容不同的消息提示方式
          if (this.$message?.error) {
            this.$message.error('综合分析失败，请重试')
          } else if (this.$notify) {
            this.$notify.error({ title: '错误', message: '综合分析失败，请重试' })
          } else {
            alert('综合分析失败，请重试')
          }
        } finally {
          this.isLoading = false
        }
      },
      
      onTripConfigChange() {
        // 配置变更时不再自动分析，需要手动点击按钮
        console.log('配置已更改，请点击"开始路程分析"按钮重新分析')
      },
      
      onSpeedConfigChange() {
        // 配置变更时重新分析
        if (this.speedAnalysisData) {
          this.performSpeedAnalysis()
        }
      },
      
      drawTripChart() {
        const canvas = this.$refs.tripChartCanvas
        if (!canvas || !this.tripAnalysisData) return
        
        const ctx = canvas.getContext('2d')
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        
        // 绘制饼图显示路程分布
        const centerX = 300
        const centerY = 200
        const radius = 120
        
        const data = [
          { label: '短途(<4km)', value: parseFloat(this.tripStats.shortTripPercentage), color: '#4CAF50' },
          { label: '中途(4-8km)', value: parseFloat(this.tripStats.mediumTripPercentage), color: '#2196F3' },
          { label: '长途(>8km)', value: parseFloat(this.tripStats.longTripPercentage), color: '#FF9800' }
        ]
        
        let startAngle = 0
        data.forEach(item => {
          if (item.value > 0) {
            const angle = (item.value / 100) * 2 * Math.PI
            
            ctx.beginPath()
            ctx.moveTo(centerX, centerY)
            ctx.arc(centerX, centerY, radius, startAngle, startAngle + angle)
            ctx.closePath()
            ctx.fillStyle = item.color
            ctx.fill()
            
            // 绘制标签
            const labelAngle = startAngle + angle / 2
            const labelX = centerX + Math.cos(labelAngle) * (radius + 30)
            const labelY = centerY + Math.sin(labelAngle) * (radius + 30)
            
            ctx.fillStyle = '#333'
            ctx.font = '14px Arial'
            ctx.textAlign = 'center'
            ctx.fillText(item.label, labelX, labelY)
            ctx.fillText(item.value + '%', labelX, labelY + 20)
            
            startAngle += angle
          }
        })
      },
      
      drawSpeedHeatmap() {
        const canvas = this.$refs.speedHeatmapCanvas
        if (!canvas || !this.speedAnalysisData) return
        
        const ctx = canvas.getContext('2d')
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        
        // 绘制背景
        ctx.fillStyle = '#f8f9fa'
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        
        // 绘制标题
        ctx.fillStyle = '#333'
        ctx.font = 'bold 16px Arial'
        ctx.textAlign = 'center'
        ctx.fillText('道路速度分布热力图', canvas.width / 2, 30)
        
        // 绘制热力点（真实数据）
        if (this.speedAnalysisData.heatmap_data && this.speedAnalysisData.heatmap_data.length > 0) {
          this.speedAnalysisData.heatmap_data.forEach(point => {
            // 使用真实的坐标数据或根据实际需求进行坐标映射
            const x = point.x || (Math.random() * (canvas.width - 100) + 50)
            const y = point.y || (Math.random() * (canvas.height - 100) + 50)
            
            const colors = {
              free: '#4CAF50',
              moderate: '#FFC107', 
              heavy: '#FF5722',
              jam: '#F44336'
            }
            
            ctx.fillStyle = colors[point.congestion_level] || '#999'
            ctx.beginPath()
            ctx.arc(x, y, 8, 0, 2 * Math.PI)
            ctx.fill()
          })
        } else {
          // 如果没有热力图数据，显示提示信息
          ctx.fillStyle = '#666'
          ctx.font = '16px Arial'
          ctx.textAlign = 'center'
          ctx.fillText('暂无热力图数据', canvas.width / 2, canvas.height / 2)
        }
      },
      
      formatLocation(location) {
        return `${location.lat.toFixed(4)}, ${location.lng.toFixed(4)}`
      },
      
      getCongestionLabel(level) {
        const labels = {
          free: '畅通',
          moderate: '缓慢', 
          heavy: '拥堵',
          jam: '严重拥堵'
        }
        return labels[level] || '未知'
      },
      
            formatSelectedDate(dateStr) {
        const dateMap = {
          '2013-09-11': '2013年9月11日',
          '2013-09-12': '2013年9月12日',
          '2013-09-13': '2013年9月13日',
          '2013-09-14': '2013年9月14日',
          '2013-09-15': '2013年9月15日',
          '2013-09-16': '2013年9月16日',
          '2013-09-17': '2013年9月17日',
          '2013-09-18': '2013年9月18日'
        }
        return dateMap[dateStr] || dateStr
      },
      
      exportAllData() {
        const data = {
          tripAnalysis: this.tripAnalysisData,
          speedAnalysis: this.speedAnalysisData,
          comprehensive: this.comprehensiveData,
          exportTime: new Date().toISOString()
        }
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `road_analysis_${Date.now()}.json`
        a.click()
        URL.revokeObjectURL(url)
      }
    }
  }
  </script>
  
  <style scoped>
  .road-analysis-advanced {
    padding: 20px;
    background: #f8f9fa;
    min-height: 100vh;
  }
  
  .analysis-header {
    text-align: center;
    margin-bottom: 30px;
  }
  
  .analysis-header h2 {
    color: #2c3e50;
    font-size: 28px;
    margin: 0 0 10px 0;
  }
  
  .subtitle {
    color: #7f8c8d;
    font-size: 16px;
    margin: 0;
  }
  
  .feature-tabs {
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    overflow: hidden;
  }
  
  .tab-item {
    flex: 1;
    text-align: center;
    padding: 15px 20px;
    cursor: pointer;
    background: white;
    border: none;
    transition: all 0.3s ease;
    font-size: 16px;
    font-weight: 500;
  }
  
  .tab-item:hover {
    background: #f8f9fa;
  }
  
  .tab-item.active {
    background: #3498db;
    color: white;
  }
  
  .control-panel {
    background: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }
  
  .panel-row {
    display: flex;
    gap: 20px;
    align-items: center;
    flex-wrap: wrap;
  }
  
  .control-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  
  .control-group label {
    font-weight: 500;
    color: #2c3e50;
    font-size: 14px;
  }
  
  .control-group select,
  .control-group input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 14px;
  }
  
  .control-group select:focus,
  .control-group input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }
  
  .date-indicator {
    font-size: 16px;
    color: #7f8c8d;
    font-weight: normal;
    margin-left: 10px;
  }
  
  .analyze-btn, .export-btn {
    background: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s ease;
  }
  
  .analyze-btn:hover, .export-btn:hover {
    background: #2980b9;
  }
  
  .analyze-btn:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
  }
  
  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }
  
  .stat-card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }
  
  .stat-value {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 5px;
  }
  
  .stat-label {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 5px;
  }
  
  .stat-count, .stat-extra {
    color: #95a5a6;
    font-size: 12px;
  }
  
  .trip-short .stat-value { color: #27ae60; }
  .trip-medium .stat-value { color: #3498db; }
  .trip-long .stat-value { color: #e67e22; }
  .trip-total .stat-value { color: #8e44ad; }
  
  .congestion-free .stat-value { color: #27ae60; }
  .congestion-moderate .stat-value { color: #f39c12; }
  .congestion-heavy .stat-value { color: #e74c3c; }
  .congestion-jam .stat-value { color: #c0392b; }
  
  .chart-section, .map-section {
    background: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }
  
  .chart-container, .map-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;
  }
  
  .speed-map {
    width: 100%;
    height: 400px;
    border: 1px solid #ddd;
    border-radius: 5px;
    position: relative;
  }
  
  .heatmap-canvas {
    width: 100%;
    height: 100%;
    border-radius: 5px;
  }
  
  .heatmap-legend {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 10px;
  }
  
  .legend-item {
    padding: 5px 10px;
    border-radius: 3px;
    color: white;
    font-size: 12px;
  }
  
  .legend-item.free { background: #4CAF50; }
  .legend-item.moderate { background: #FFC107; }
  .legend-item.heavy { background: #FF5722; }
  .legend-item.jam { background: #F44336; }
  
  .daily-breakdown, .congestion-details {
    background: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }
  
  .data-table th,
  .data-table td {
    padding: 12px 8px;
    text-align: left;
    border-bottom: 1px solid #eee;
  }
  
  .data-table th {
    background: #f8f9fa;
    font-weight: 600;
    color: #2c3e50;
  }
  
  .no-data {
    text-align: center;
    color: #7f8c8d;
    font-style: italic;
    padding: 20px !important;
  }
  
  .congestion-free { color: #27ae60; }
  .congestion-moderate { color: #f39c12; }
  .congestion-heavy { color: #e74c3c; }
  .congestion-jam { color: #c0392b; }
  
  .overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }
  
  .overview-card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }
  
  .overview-card h4 {
    margin: 0 0 15px 0;
    color: #2c3e50;
  }
  
  .quick-stats {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .quick-stat {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .quick-stat .label {
    color: #7f8c8d;
  }
  
  .quick-stat .value {
    font-weight: 600;
    color: #2c3e50;
  }
  
  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.7);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .loading-spinner {
    width: 50px;
    height: 50px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20px;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .loading-overlay p {
    color: white;
    font-size: 16px;
  }
  
  @media (max-width: 768px) {
    .panel-row {
      flex-direction: column;
      align-items: stretch;
    }
    
    .stats-cards {
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
  }
  </style>
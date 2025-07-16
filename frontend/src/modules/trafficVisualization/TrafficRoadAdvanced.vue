<template>
    <div class="road-analysis-advanced">
      <!-- 标题栏 -->
      <div class="analysis-header">
        <h2>路程智能分析</h2>
        <p class="subtitle">路程分析</p>
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
        <!-- 删除订单速度分析tab -->
      </div>
  
      <!-- 路程分析面板 -->
      <div v-if="activeTab === 'trip'" class="analysis-content">
        <div class="control-panel">
          <div class="panel-row">
            <div class="control-group">
              <label>分析日期:</label>
              <select v-model="tripConfig.selected_date">
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
              <button 
                @click="performTripAnalysis" 
                :disabled="isLoading" 
                class="analyze-btn"
              >
                {{ isLoading ? '分析中...' : '开始路程分析' }}
              </button>
            </div>
          </div>
        </div>
  
        <!-- 提示信息 -->
        <div v-if="!tripAnalysisData" class="analysis-prompt">
          <div class="prompt-content">
            <h3>📊 智能路程分析</h3>
            <p>请选择分析日期，然后点击"开始路程分析"按钮开始分析</p>
            <div class="data-info">
              <p><strong>📅 可用数据范围：</strong>2013年9月12日 - 2013年9月18日</p>
            </div>
            <div class="prompt-steps">
              <div class="step">
                <span class="step-number">1</span>
                <span class="step-text">选择分析日期</span>
              </div>
              <div class="step">
                <span class="step-number">2</span>
                <span class="step-text">调整最小订单数参数（可选）</span>
              </div>
              <div class="step">
                <span class="step-number">3</span>
                <span class="step-text">点击"开始路程分析"按钮</span>
              </div>
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
              <span class="date-indicator">
                ({{ formatSelectedDate(tripConfig.selected_date) }})
              </span>
            </h3>
            <div class="chart-container">
              <canvas ref="tripChartCanvas" class="trip-chart" width="600" height="400"></canvas>
            </div>
          </div>
  

        </div>
      </div>
  
      <!-- 删除订单速度分析面板及相关内容 -->
  
      <!-- 综合分析面板（如有速度相关内容也一并删除） -->
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
  import { ref, onMounted, nextTick, watch } from 'vue'
import { roadAPI } from '@/api/traffic'
  
  export default {
    name: 'TrafficRoadAdvanced',
    data() {
      return {
        isLoading: false,
        loadingMessage: '分析中...',
        loadingProgress: 0,
        activeTab: 'trip',
        
        // 路程分析配置
        tripConfig: {
          min_trip_count: 10,
          selected_date: '2013-09-12'
        },
        
        // 分析配置
        analysisConfig: {
          time_window: 60,
          min_speed: 5,
          max_speed: 120,
          grid_size: 0.001,
          analysis_type: 'comprehensive'
        },
        
        // 分析数据
        tripAnalysisData: null,
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
        
        // 显示选中日期的数据
        if (this.tripAnalysisData.daily_classifications) {
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
      
      // 过滤后的日期分类数据
      filteredDailyClassifications() {
        if (!this.tripAnalysisData?.daily_classifications) {
          return []
        }
        
        // 只显示选中日期的数据
          const filtered = this.tripAnalysisData.daily_classifications.filter(
            day => day.date === this.tripConfig.selected_date
          )
          return filtered
      },
      
      // 是否有任何数据
      hasAnyData() {
        return this.tripAnalysisData || this.comprehensiveData
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
      }
    },
    
    mounted() {
      this.initializeComponent()
    },

    // 使用 watch 监听地图和热力图数据，自动渲染热力图
    watch: {
      // 监听地图实例和热力图数据
      speedMap: {
        handler(newMap) {
          if (newMap && this.speedAnalysisData?.heatmap_data?.length > 0) {
            console.log('🎯 地图实例已准备好，自动渲染热力图')
            this.updateSpeedHeatmapOnMap()
          }
        },
        immediate: false
      },
      // 监听热力图数据变化
      'speedAnalysisData.heatmap_data': {
        handler(newData) {
          if (this.speedMap && newData && newData.length > 0) {
            console.log('🎯 热力图数据已准备好，自动渲染热力图')
            this.updateSpeedHeatmapOnMap()
          }
        },
        immediate: false
      }
    },
    
    beforeUnmount() {
      // 清理地图资源
      this.cleanupMap()
    },
    
    methods: {
      initializeComponent() {
        // 初始化组件，但不自动执行分析
        console.log('智能路程分析组件已初始化，请选择日期并点击"开始路程分析"按钮')
      },
      
      switchTab(tab) {
        this.activeTab = tab
        // 切换标签页时不自动执行分析，需要用户手动点击按钮
        console.log(`已切换到${tab === 'trip' ? '路程分析' : '综合分析'}标签页`)
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
      
      async performComprehensiveAnalysis() {
        try {
          this.isLoading = true
          this.loadingMessage = '正在进行综合分析...'
          
          // 并行执行两个分析
          await Promise.all([
            this.tripAnalysisData ? Promise.resolve() : this.performTripAnalysis(),
            // this.speedAnalysisData ? Promise.resolve() : this.performSpeedAnalysis() // 删除速度分析
          ])
          
          // 生成综合数据
          this.comprehensiveData = {
            tripData: this.tripAnalysisData,
            // speedData: this.speedAnalysisData, // 删除速度分析
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
          // speedAnalysis: this.speedAnalysisData, // 删除速度分析
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
      },

             // 新增：带重试机制的地图初始化（只负责底图显示）
       async initializeMapWithRetry(maxRetries = 3) {
         for (let attempt = 1; attempt <= maxRetries; attempt++) {
           console.log(`🔄 地图初始化尝试 ${attempt}/${maxRetries}`)
           
           try {
             await this.initializeMap()
             if (this.speedMap) {
               console.log('✅ 地图底图初始化成功，等待热力图数据...')
               return
             }
           } catch (error) {
             console.warn(`❌ 地图初始化尝试 ${attempt} 失败:`, error)
           }
           
           // 如果不是最后一次尝试，等待后重试
           if (attempt < maxRetries) {
             console.log(`⏳ 等待 ${attempt * 1000}ms 后重试...`)
             await new Promise(resolve => setTimeout(resolve, attempt * 1000))
           }
         }
         
         console.error('❌ 地图初始化失败，已达到最大重试次数')
       },

       // 新增：地图组件初始化方法（只负责底图显示）
       async initializeMap() {
         console.log('🗺️ 开始初始化地图底图...')
         console.log('地图容器ID:', this.speedMapContainerId)
         console.log('地图容器元素:', document.getElementById(this.speedMapContainerId))
         console.log('容器尺寸:', document.getElementById(this.speedMapContainerId)?.getBoundingClientRect())
         
         try {
           // 使用统一的地图API管理器
           console.log('📡 加载地图API...')
           // 检查地图容器是否存在并且有尺寸
           const mapContainer = document.getElementById(this.speedMapContainerId)
           if (!mapContainer) {
             throw new Error(`地图容器不存在: ${this.speedMapContainerId}`)
           }
           
           // 检查容器尺寸
           const containerRect = mapContainer.getBoundingClientRect()
           console.log('地图容器尺寸:', containerRect)
           
           if (containerRect.width === 0 || containerRect.height === 0) {
             throw new Error(`地图容器尺寸异常: ${containerRect.width}x${containerRect.height}`)
           }
           
           // 如果地图已存在，先清理
           if (this.speedMap) {
             console.log('🧹 清理现有地图实例')
             this.speedMap.destroy()
             this.speedMap = null
             this.speedMapInitialized = false
           }

           // 创建地图实例
           console.log('🏗️ 创建地图实例...')
           this.speedMap = new window.AMap.Map(this.speedMapContainerId, {
             zoom: 11, // 初始缩放级别
             center: [117.120, 36.651], // 济南市中心
             mapStyle: 'amap://styles/blue', // 地图样式
             zooms: [3, 20] // 缩放级别范围
           })
           
           console.log('📍 地图实例创建成功:', this.speedMap)

           // 等待地图加载完成
           await new Promise((resolve, reject) => {
             const timeout = setTimeout(() => {
               reject(new Error('地图加载超时'))
             }, 10000) // 10秒超时
             
             this.speedMap.on('complete', () => {
               clearTimeout(timeout)
               this.speedMapInitialized = true
               console.log('✅ 地图底图加载完成，watch 会自动处理热力图')
               resolve()
             })
           })

           // 添加基础控件
           this.speedMap.plugin(['AMap.Scale', 'AMap.ToolBar'], () => {
             this.speedMap.addControl(new window.AMap.Scale());
             this.speedMap.addControl(new window.AMap.ToolBar());
           });
           
         } catch (error) {
           console.error('❌ 地图底图初始化失败:', error)
           console.error('错误堆栈:', error.stack)
           // 清理失败的地图实例
           if (this.speedMap) {
             try {
               this.speedMap.destroy()
             } catch (e) {
               console.warn('清理失败的地图实例时出错:', e)
             }
             this.speedMap = null
           }
           this.speedMapInitialized = false
           throw error // 重新抛出错误，让重试机制处理
         }
       },

        // 注意：waitForMapAndUpdateHeatmap 方法已被 watch 替代，不再需要

        // 新增：更新地图上的速度热力图
        updateSpeedHeatmapOnMap() {
         console.log('🔥 开始渲染热力图到地图上...')
         console.log('地图实例:', this.speedMap)
         console.log('热力图数据点数:', this.speedAnalysisData?.heatmap_data?.length)
         
         if (!this.speedMap || !this.speedAnalysisData?.heatmap_data) {
           console.warn('❌ 热力图渲染失败：地图或数据不存在')
           console.warn('地图实例存在:', !!this.speedMap)
           console.warn('热力图数据存在:', !!this.speedAnalysisData?.heatmap_data)
           return
         }

         // 清除之前的热力图
         if (this.speedHeatmapLayer) {
           this.speedMap.remove(this.speedHeatmapLayer)
           this.speedHeatmapLayer = null
         }

         // 准备热力图数据
         const heatmapData = this.speedAnalysisData.heatmap_data.map(point => {
           const colors = {
             free: 100,      // 畅通 - 高值（绿色）
             moderate: 70,   // 缓慢 - 中高值（黄色）
             heavy: 40,      // 拥堵 - 中低值（橙色）
             jam: 10         // 严重拥堵 - 低值（红色）
           }
           
           return {
             lng: point.lng || point.location?.lng,
             lat: point.lat || point.location?.lat,
             count: colors[point.congestion_level] || 50
           }
         }).filter(point => point.lng && point.lat)

         if (heatmapData.length === 0) {
           console.warn('没有有效的热力图数据点')
           return
         }

         // 创建热力图插件
         this.speedMap.plugin(['AMap.HeatMap'], () => {
           this.speedHeatmapLayer = new window.AMap.HeatMap(this.speedMap, {
             radius: 25,
             opacity: [0, 0.8],
             gradient: {
               0.4: 'blue',      // 低速（拥堵）
               0.6: 'cyan',      
               0.7: 'lime',      
               0.8: 'yellow',    
               1.0: 'red'        // 高速（畅通）
             }
           })

           this.speedHeatmapLayer.setDataSet({
             data: heatmapData,
             max: 100
           })

           console.log(`热力图已更新，共 ${heatmapData.length} 个数据点`)
         })
       },

               // 新增：检查地图状态
        checkMapStatus() {
          console.log('🔍 地图状态检查')
          console.log('地图容器ID:', this.speedMapContainerId)
          console.log('地图容器元素:', document.getElementById(this.speedMapContainerId))
          console.log('容器尺寸:', document.getElementById(this.speedMapContainerId)?.getBoundingClientRect())
          console.log('地图初始化状态:', this.speedMapInitialized)
          console.log('地图实例:', this.speedMap)
          console.log('速度分析数据:', this.speedAnalysisData)
          console.log('热力图数据:', this.speedAnalysisData?.heatmap_data)
          console.log('window.AMap:', window.AMap)
          
          // 检查地图容器尺寸
          const container = document.getElementById(this.speedMapContainerId)
          if (container) {
            console.log('地图容器尺寸:', {
              width: container.offsetWidth,
              height: container.offsetHeight,
              display: window.getComputedStyle(container).display,
              visibility: window.getComputedStyle(container).visibility
            })
          }
        },

        // 新增：清理地图资源
        cleanupMap() {
          try {
            // 清理热力图图层
            if (this.speedHeatmapLayer) {
              this.speedMap?.remove(this.speedHeatmapLayer)
              this.speedHeatmapLayer = null
            }
            
            // 清理地图实例
            if (this.speedMap) {
              this.speedMap.clearMap()
              this.speedMap.destroy()
              this.speedMap = null
            }
            
            // 重置状态
            this.speedMapInitialized = false
            console.log('✅ 地图资源已清理')
          } catch (error) {
            console.warn('⚠️ 清理地图资源时出错:', error)
          }
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
  
  /* 加载指示器样式 */
  .loading-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-top: 15px;
    border: 1px solid #e9ecef;
  }
  
  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 15px;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .loading-text {
    flex: 1;
  }
  
  .loading-text p {
    margin: 5px 0;
    font-size: 16px;
    color: #333;
  }
  
  .loading-tip {
    font-size: 14px !important;
    color: #666 !important;
  }
  
  .loading-progress {
    width: 100%;
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
    margin-top: 10px;
  }
  
  .progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #3498db, #2ecc71);
    border-radius: 4px;
    transition: width 0.3s ease;
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
  
  .speed-heatmap-map {
    width: 100%;
    height: 100%;
    min-height: 400px;
    position: relative;
  }

  .map-loading {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    border-radius: 5px;
    z-index: 1;
  }

  .map-loading .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 10px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .debug-controls {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }

  .debug-btn {
    padding: 4px 8px;
    font-size: 12px;
    background: #f0f0f0;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .debug-btn:hover {
    background: #e0e0e0;
    border-color: #999;
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
  
  /* 提示信息样式 */
  .analysis-prompt {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    padding: 30px;
    margin: 20px 0;
    color: white;
    text-align: center;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  }
  
  .prompt-content h3 {
    margin: 0 0 15px 0;
    font-size: 24px;
    font-weight: 600;
  }
  
  .prompt-content p {
    margin: 0 0 25px 0;
    font-size: 16px;
    opacity: 0.9;
  }
  
  .data-info {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 15px;
    margin: 0 0 25px 0;
    border-left: 4px solid rgba(255, 255, 255, 0.3);
  }
  
  .data-info p {
    margin: 0;
    font-size: 14px;
    opacity: 0.95;
  }
  
  .prompt-steps {
    display: flex;
    flex-direction: column;
    gap: 15px;
    max-width: 400px;
    margin: 0 auto;
  }
  
  .step {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 12px 20px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    backdrop-filter: blur(10px);
  }
  
  .step-number {
    width: 30px;
    height: 30px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
  }
  
  .step-text {
    font-size: 14px;
    text-align: left;
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
<template>
  <div class="weekly-passenger-flow">
    <!-- 头部控制面板 -->
    <div class="control-panel">
      <div class="time-selector">
        <label>分析时间范围：</label>
        <input 
          type="datetime-local" 
          v-model="timeRange.start"
          :min="minDate"
          :max="maxDate"
          class="time-input"
        />
        <span class="to">至</span>
        <input 
          type="datetime-local" 
          v-model="timeRange.end"
          :min="minDate"
          :max="maxDate"
          class="time-input"
        />
        <button @click="analyzeFlow" :disabled="loading" class="analyze-btn">
          <span v-if="loading">分析中...</span>
          <span v-else>开始分析</span>
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在分析周客流量数据...</p>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="retryAnalysis" class="retry-btn">重试</button>
    </div>

    <!-- 分析结果 -->
    <div v-if="analysisData && !loading" class="analysis-results">
      
      <!-- 概览统计卡片 -->
      <div class="overview-cards">
        <div class="stat-card">
          <div class="card-icon vehicles">📊</div>
          <div class="card-content">
            <h3>总车辆数</h3>
            <p class="stat-value">{{ formatNumber(analysisData.statistics?.total_unique_vehicles || 0) }}</p>
            <span class="stat-label">独立车辆</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="card-icon days">📅</div>
          <div class="card-content">
            <h3>分析天数</h3>
            <p class="stat-value">{{ analysisData.statistics?.analysis_days || 0 }}</p>
            <span class="stat-label">天</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="card-icon average">📈</div>
          <div class="card-content">
            <h3>日均客流</h3>
            <p class="stat-value">{{ formatNumber(analysisData.statistics?.avg_daily_vehicles || 0) }}</p>
            <span class="stat-label">车辆/天</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="card-icon peak">🔥</div>
          <div class="card-content">
            <h3>峰值流量</h3>
            <p class="stat-value">{{ formatNumber(analysisData.statistics?.max_daily_vehicles || 0) }}</p>
            <span class="stat-label">车辆/天</span>
          </div>
        </div>
      </div>

      <!-- 工作日vs周末对比 -->
      <div class="comparison-section">
        <h2>工作日 vs 周末对比</h2>
        <div class="comparison-container">
          <div class="comparison-chart">
            <div class="bar-chart">
              <div class="bar weekday-bar">
                <div class="bar-fill" :style="{ height: getBarHeight(analysisData.weekday_comparison?.weekday_avg || 0, maxComparison) }"></div>
                <div class="bar-label">工作日</div>
                <div class="bar-value">{{ formatNumber(analysisData.weekday_comparison?.weekday_avg || 0) }}</div>
              </div>
              <div class="bar weekend-bar">
                <div class="bar-fill" :style="{ height: getBarHeight(analysisData.weekday_comparison?.weekend_avg || 0, maxComparison) }"></div>
                <div class="bar-label">周末</div>
                <div class="bar-value">{{ formatNumber(analysisData.weekday_comparison?.weekend_avg || 0) }}</div>
              </div>
            </div>
          </div>
          
          <div class="comparison-stats">
            <div class="stat-item">
              <span class="stat-name">差异百分比：</span>
              <span class="stat-value" :class="getDifferenceClass(analysisData.weekday_comparison?.difference_pct)">
                {{ formatPercent(analysisData.weekday_comparison?.difference_pct || 0) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-name">流量模式：</span>
              <span class="stat-value">{{ getPatternLabel(analysisData.weekday_comparison?.pattern) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 一周流量模式 -->
      <div class="weekly-pattern-section">
        <h2>一周流量模式</h2>
        <div class="weekly-chart-container">
          <div class="weekly-chart">
            <svg width="100%" height="300" viewBox="0 0 800 300">
              <!-- 背景网格 -->
              <defs>
                <pattern id="grid" width="80" height="30" patternUnits="userSpaceOnUse">
                  <path d="M 80 0 L 0 0 0 30" fill="none" stroke="#e0e0e0" stroke-width="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
              
              <!-- 周流量柱状图 -->
              <g transform="translate(50, 20)">
                <g v-for="(day, index) in weeklyPatternData" :key="index">
                  <rect 
                    :x="index * 100" 
                    :y="250 - getWeeklyBarHeight(day.COMMADDR)" 
                    width="80" 
                    :height="getWeeklyBarHeight(day.COMMADDR)"
                    :fill="getWeeklyBarColor(day.weekday)"
                    class="weekly-bar"
                  />
                  <text 
                    :x="index * 100 + 40" 
                    y="275" 
                    text-anchor="middle" 
                    font-size="12" 
                    fill="#666"
                  >
                    {{ day.weekday_name }}
                  </text>
                  <text 
                    :x="index * 100 + 40" 
                    :y="245 - getWeeklyBarHeight(day.COMMADDR)" 
                    text-anchor="middle" 
                    font-size="11" 
                    fill="#333"
                  >
                    {{ formatNumber(day.COMMADDR) }}
                  </text>
                </g>
              </g>
            </svg>
          </div>
          
          <!-- 周模式统计 -->
          <div class="weekly-stats">
            <div class="peak-day">
              <h4>客流最高日</h4>
              <p class="day-name">{{ analysisData.weekly_patterns?.peak_day?.day || 'N/A' }}</p>
              <p class="day-value">{{ formatNumber(analysisData.weekly_patterns?.peak_day?.vehicles || 0) }} 车辆</p>
            </div>
            <div class="lowest-day">
              <h4>客流最低日</h4>
              <p class="day-name">{{ analysisData.weekly_patterns?.lowest_day?.day || 'N/A' }}</p>
              <p class="day-value">{{ formatNumber(analysisData.weekly_patterns?.lowest_day?.vehicles || 0) }} 车辆</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 小时流量模式 -->
      <div class="hourly-pattern-section">
        <h2>24小时流量模式</h2>
        <div class="hourly-chart-tabs">
          <button 
            @click="activeTab = 'weekday'" 
            :class="{ active: activeTab === 'weekday' }"
            class="tab-btn"
          >
            工作日模式
          </button>
          <button 
            @click="activeTab = 'weekend'" 
            :class="{ active: activeTab === 'weekend' }"
            class="tab-btn"
          >
            周末模式
          </button>
        </div>
        
        <div class="hourly-chart">
          <svg width="100%" height="250" viewBox="0 0 900 250">
            <!-- 坐标轴 -->
            <g transform="translate(40, 20)">
              <!-- Y轴 -->
              <line x1="0" y1="0" x2="0" y2="180" stroke="#ccc" stroke-width="2"/>
              <!-- X轴 -->
              <line x1="0" y1="180" x2="840" y2="180" stroke="#ccc" stroke-width="2"/>
              
              <!-- 小时标签 -->
              <g class="x-axis-labels">
                <text v-for="hour in [0, 6, 12, 18, 24]" :key="hour"
                      :x="hour * 35" y="200" 
                      text-anchor="middle" 
                      font-size="12" 
                      fill="#666">
                  {{ hour }}:00
                </text>
              </g>
              
              <!-- 流量曲线 -->
              <polyline 
                :points="getHourlyPolylinePoints(activeTab)"
                fill="none" 
                :stroke="activeTab === 'weekday' ? '#3b82f6' : '#ef4444'" 
                stroke-width="3"
              />
              
              <!-- 数据点 -->
              <circle
                v-for="(point, index) in getHourlyPoints(activeTab)"
                :key="index"
                :cx="point.x"
                :cy="point.y"
                r="4"
                :fill="activeTab === 'weekday' ? '#3b82f6' : '#ef4444'"
                class="data-point"
              />
            </g>
          </svg>
        </div>
        
        <!-- 高峰时段信息 -->
        <div class="peak-info">
          <div class="peak-hour-info">
            <h4>工作日高峰时段</h4>
            <p>{{ analysisData.hourly_patterns?.peak_hours?.weekday || 0 }}:00</p>
          </div>
          <div class="peak-hour-info">
            <h4>周末高峰时段</h4>
            <p>{{ analysisData.hourly_patterns?.peak_hours?.weekend || 0 }}:00</p>
          </div>
        </div>
      </div>

      <!-- 趋势分析 -->
      <div class="trend-section" v-if="analysisData.flow_trends?.weekly_summary">
        <h2>客流量趋势分析</h2>
        <div class="trend-container">
          <div class="trend-chart">
            <svg width="100%" height="200" viewBox="0 0 600 200">
              <g transform="translate(40, 20)">
                <!-- 趋势线 -->
                <polyline 
                  :points="getTrendPolylinePoints()"
                  fill="none" 
                  stroke="#10b981" 
                  stroke-width="3"
                />
                
                <!-- 数据点 -->
                <circle
                  v-for="(point, index) in getTrendPoints()"
                  :key="index"
                  :cx="point.x"
                  :cy="point.y"
                  r="5"
                  fill="#10b981"
                />
                
                <!-- 周标签 -->
                <g class="week-labels">
                  <text v-for="(week, index) in analysisData.flow_trends.weekly_summary" :key="index"
                        :x="index * 100 + 50" y="195" 
                        text-anchor="middle" 
                        font-size="12" 
                        fill="#666">
                    第{{ week.week }}周
                  </text>
                </g>
              </g>
            </svg>
          </div>
          
          <div class="trend-stats">
            <div class="trend-direction">
              <h4>趋势方向</h4>
              <p class="trend-value" :class="getTrendClass()">
                {{ getTrendLabel() }}
              </p>
            </div>
            <div class="trend-slope">
              <h4>变化幅度</h4>
              <p>{{ Math.abs(analysisData.flow_trends?.trend_analysis?.slope || 0).toFixed(2) }}/周</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 详细数据表格 -->
      <div class="data-table-section">
        <h2>详细数据表格</h2>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>星期</th>
                <th>车辆数</th>
                <th>轨迹点数</th>
                <th>类型</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="day in dailyFlowData" :key="day.date">
                <td>{{ day.date }}</td>
                <td>{{ day.weekday_name }}</td>
                <td>{{ formatNumber(day.vehicles) }}</td>
                <td>{{ formatNumber(day.total_points) }}</td>
                <td>
                  <span :class="{ 'weekend-tag': day.is_weekend, 'weekday-tag': !day.is_weekend }">
                    {{ day.is_weekend ? '周末' : '工作日' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getWeeklyPassengerFlowAnalysis } from '@/api/traffic'

export default {
  name: 'WeeklyPassengerFlow',
  data() {
    return {
      loading: false,
      error: null,
      analysisData: null,
      activeTab: 'weekday',
      
      timeRange: {
        start: '2013-09-12T00:00',
        end: '2013-09-18T23:59'
      },
      
      // 时间限制
      minDate: '2013-09-12T00:00',
      maxDate: '2013-09-18T23:59'
    }
  },
  
  computed: {
    dailyFlowData() {
      return this.analysisData?.daily_flow?.daily_data || []
    },
    
    weeklyPatternData() {
      return this.analysisData?.weekly_patterns?.weekly_data || []
    },
    
    maxComparison() {
      const weekday = this.analysisData?.weekday_comparison?.weekday_avg || 0
      const weekend = this.analysisData?.weekday_comparison?.weekend_avg || 0
      return Math.max(weekday, weekend)
    },
    
    maxWeeklyFlow() {
      if (!this.weeklyPatternData.length) return 1
      return Math.max(...this.weeklyPatternData.map(d => d.COMMADDR))
    }
  },
  
  mounted() {
    // 自动执行一次分析
    this.analyzeFlow()
  },
  
  methods: {
    async analyzeFlow() {
      this.loading = true
      this.error = null
      
      try {
        // 转换时间格式
        const startTime = new Date(this.timeRange.start).getTime() / 1000
        const endTime = new Date(this.timeRange.end).getTime() / 1000
        
        // 验证时间范围
        if (endTime <= startTime) {
          throw new Error('结束时间必须晚于开始时间')
        }
        
        if (endTime - startTime < 3 * 24 * 3600) {
          throw new Error('分析周客流量需要至少3天的数据')
        }
        
        // 调用API
        const response = await getWeeklyPassengerFlowAnalysis(startTime, endTime)
        
        if (response.success) {
          this.analysisData = response.data
          this.$message.success('周客流量分析完成')
        } else {
          throw new Error(response.message || '分析失败')
        }
        
      } catch (error) {
        this.error = error.message
        this.$message.error(`分析失败: ${error.message}`)
      } finally {
        this.loading = false
      }
    },
    
    retryAnalysis() {
      this.error = null
      this.analyzeFlow()
    },
    
    formatNumber(num) {
      if (!num) return '0'
      return new Intl.NumberFormat('zh-CN').format(Math.round(num))
    },
    
    formatPercent(num) {
      if (!num) return '0%'
      return `${num > 0 ? '+' : ''}${num.toFixed(1)}%`
    },
    
    getBarHeight(value, max) {
      if (!max) return '0%'
      return `${(value / max) * 100}%`
    },
    
    getDifferenceClass(pct) {
      if (!pct) return ''
      return pct > 0 ? 'positive' : 'negative'
    },
    
    getPatternLabel(pattern) {
      const labels = {
        'weekend_higher': '周末客流更高',
        'weekday_higher': '工作日客流更高'
      }
      return labels[pattern] || '无明显模式'
    },
    
    getWeeklyBarHeight(value) {
      if (!this.maxWeeklyFlow) return 0
      return (value / this.maxWeeklyFlow) * 200
    },
    
    getWeeklyBarColor(weekday) {
      // 0=Monday, 6=Sunday
      return weekday >= 5 ? '#ef4444' : '#3b82f6'
    },
    
    getHourlyPoints(type) {
      const data = type === 'weekday' 
        ? this.analysisData?.hourly_patterns?.weekday_pattern || []
        : this.analysisData?.hourly_patterns?.weekend_pattern || []
      
      if (!data.length) return []
      
      const maxValue = Math.max(...data.map(d => d.COMMADDR))
      
      return data.map(item => ({
        x: item.hour * 35,
        y: 180 - (item.COMMADDR / maxValue * 160)
      }))
    },
    
    getHourlyPolylinePoints(type) {
      return this.getHourlyPoints(type).map(p => `${p.x},${p.y}`).join(' ')
    },
    
    getTrendPoints() {
      const data = this.analysisData?.flow_trends?.weekly_summary || []
      if (!data.length) return []
      
      const maxValue = Math.max(...data.map(d => d.avg_daily_vehicles))
      
      return data.map((item, index) => ({
        x: index * 100 + 50,
        y: 160 - (item.avg_daily_vehicles / maxValue * 140)
      }))
    },
    
    getTrendPolylinePoints() {
      return this.getTrendPoints().map(p => `${p.x},${p.y}`).join(' ')
    },
    
    getTrendClass() {
      const direction = this.analysisData?.flow_trends?.trend_analysis?.direction
      return {
        'trend-increasing': direction === 'increasing',
        'trend-decreasing': direction === 'decreasing',
        'trend-stable': direction === 'stable'
      }
    },
    
    getTrendLabel() {
      const direction = this.analysisData?.flow_trends?.trend_analysis?.direction
      const labels = {
        'increasing': '上升趋势',
        'decreasing': '下降趋势',
        'stable': '稳定'
      }
      return labels[direction] || '未知'
    }
  }
}
</script>

<style scoped>
.weekly-passenger-flow {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  font-family: 'Arial', sans-serif;
}

/* 控制面板 */
.control-panel {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.time-selector {
  display: flex;
  align-items: center;
  gap: 15px;
  color: white;
}

.time-selector label {
  font-weight: 600;
  font-size: 16px;
}

.time-input {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 10px;
  color: white;
  font-size: 14px;
}

.time-input:focus {
  outline: none;
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.3);
}

.to {
  color: white;
  font-weight: 500;
}

.analyze-btn {
  background: linear-gradient(45deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

.analyze-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 加载状态 */
.loading-container {
  text-align: center;
  padding: 60px 20px;
  color: white;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误信息 */
.error-message {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  border-radius: 12px;
  padding: 20px;
  color: white;
  text-align: center;
  margin-bottom: 20px;
}

.retry-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 10px;
}

/* 分析结果 */
.analysis-results {
  space-y: 30px;
}

/* 概览卡片 */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.card-icon {
  font-size: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
}

.card-content h3 {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  margin: 0 0 8px 0;
}

.stat-value {
  color: white;
  font-size: 32px;
  font-weight: bold;
  margin: 0;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

/* 对比区域 */
.comparison-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.comparison-section h2 {
  color: white;
  margin-bottom: 25px;
  font-size: 24px;
}

.comparison-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
}

.bar-chart {
  display: flex;
  justify-content: space-around;
  align-items: end;
  height: 200px;
  padding: 20px;
}

.bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 80px;
}

.bar-fill {
  width: 60px;
  background: linear-gradient(45deg, #3b82f6, #1d4ed8);
  border-radius: 8px 8px 0 0;
  transition: height 0.8s ease;
}

.weekend-bar .bar-fill {
  background: linear-gradient(45deg, #ef4444, #dc2626);
}

.bar-label {
  color: white;
  font-weight: 600;
  margin-top: 10px;
}

.bar-value {
  color: white;
  font-size: 18px;
  font-weight: bold;
}

.comparison-stats {
  color: white;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-name {
  font-weight: 600;
}

.positive {
  color: #10b981;
}

.negative {
  color: #ef4444;
}

/* 周模式区域 */
.weekly-pattern-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.weekly-pattern-section h2 {
  color: white;
  margin-bottom: 25px;
  font-size: 24px;
}

.weekly-chart-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  align-items: start;
}

.weekly-chart {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

.weekly-bar {
  transition: opacity 0.3s ease;
  cursor: pointer;
}

.weekly-bar:hover {
  opacity: 0.8;
}

.weekly-stats {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.peak-day, .lowest-day {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.peak-day h4, .lowest-day h4 {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 10px;
  font-size: 14px;
}

.day-name {
  color: white;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 5px;
}

.day-value {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

/* 小时模式区域 */
.hourly-pattern-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.hourly-pattern-section h2 {
  color: white;
  margin-bottom: 25px;
  font-size: 24px;
}

.hourly-chart-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.tab-btn.active {
  background: rgba(59, 130, 246, 0.5);
}

.hourly-chart {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.data-point {
  transition: r 0.3s ease;
}

.data-point:hover {
  r: 6;
}

.peak-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.peak-hour-info {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.peak-hour-info h4 {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 10px;
  font-size: 14px;
}

.peak-hour-info p {
  color: white;
  font-size: 24px;
  font-weight: bold;
}

/* 趋势分析 */
.trend-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.trend-section h2 {
  color: white;
  margin-bottom: 25px;
  font-size: 24px;
}

.trend-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  align-items: center;
}

.trend-chart {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

.trend-stats {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.trend-direction, .trend-slope {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.trend-direction h4, .trend-slope h4 {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 10px;
  font-size: 14px;
}

.trend-value {
  font-size: 18px;
  font-weight: bold;
}

.trend-increasing {
  color: #10b981;
}

.trend-decreasing {
  color: #ef4444;
}

.trend-stable {
  color: #f59e0b;
}

/* 数据表格 */
.data-table-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.data-table-section h2 {
  color: white;
  margin-bottom: 25px;
  font-size: 24px;
}

.table-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: rgba(59, 130, 246, 0.3);
  color: white;
  padding: 15px;
  text-align: left;
  font-weight: 600;
}

.data-table td {
  color: white;
  padding: 12px 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.data-table tr:hover {
  background: rgba(255, 255, 255, 0.1);
}

.weekend-tag {
  background: #ef4444;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.weekday-tag {
  background: #3b82f6;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .weekly-passenger-flow {
    padding: 15px;
  }
  
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .comparison-container,
  .weekly-chart-container,
  .trend-container {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .peak-info {
    grid-template-columns: 1fr;
  }
  
  .time-selector {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .stat-card {
    flex-direction: column;
    text-align: center;
  }
}
</style> 
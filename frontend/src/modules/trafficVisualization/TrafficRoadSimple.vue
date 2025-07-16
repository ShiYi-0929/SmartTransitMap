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
          <select v-model="config.analysis.analysis_type" @change="onConfigChange">
            <option value="comprehensive">综合分析</option>
            <option value="speed">速度分析</option>
            <option value="flow">流量分析</option>
            <option value="congestion">拥堵分析</option>
          </select>
        </div>

        <!-- 路段类型筛选 -->
        <div class="control-group">
          <label>路段类型:</label>
          <select v-model="config.analysis.segment_types[0]" @change="onConfigChange">
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
            v-model.number="config.analysis.min_vehicles" 
            min="1" 
            max="50"
            @change="onConfigChange"
          />
        </div>

        <!-- 分析时间范围 -->
        <div class="control-group">
          <label>分析时间范围:</label>
          
          <!-- 可用数据时间范围提示 -->
          <div class="data-range-info">
            <span class="data-range-label">📅 可用数据范围:</span>
            <span class="data-range-value">{{ getAvailableDataRange() }}</span>
          </div>
          
          <div class="time-range-picker">
            <!-- 开始时间 -->
            <div class="time-input-group">
              <label class="time-label">开始时间:</label>
          <el-date-picker
                v-model="startDateTime"
                type="datetime"
                placeholder="选择开始日期和时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
            :clearable="false"
                style="width: 200px"
                @change="onTimeChange"
              />
            </div>
            
            <!-- 结束时间 -->
            <div class="time-input-group">
              <label class="time-label">结束时间:</label>
              <el-date-picker
                v-model="endDateTime"
                type="datetime"
                placeholder="选择结束日期和时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
                :clearable="false"
                style="width: 200px"
                @change="onTimeChange"
          />
            </div>
            
            <!-- 快速选择按钮 -->
            <div class="quick-time-buttons">
              <button 
                @click="setQuickTimeRange('4h')" 
                class="quick-btn"
                :class="{ active: quickTimeRange === '4h' }"
              >
                4小时
              </button>
              <button 
                @click="setQuickTimeRange('8h')" 
                class="quick-btn"
                :class="{ active: quickTimeRange === '8h' }"
              >
                8小时
              </button>
              <button 
                @click="setQuickTimeRange('24h')" 
                class="quick-btn"
                :class="{ active: quickTimeRange === '24h' }"
              >
                24小时
              </button>
              <button 
                @click="setQuickTimeRange('custom')" 
                class="quick-btn"
                :class="{ active: quickTimeRange === 'custom' }"
              >
                自定义
              </button>
            </div>
            
            <!-- 时间范围信息 -->
            <div class="time-range-info" v-if="startDateTime && endDateTime">
              <div class="info-item">
                <span class="info-label">当前选择:</span>
                <span class="info-value">
                  {{ formatDateTime(startDateTime) }} 至 {{ formatDateTime(endDateTime) }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">时长:</span>
                <span class="info-value">{{ getTimeDuration() }}</span>
              </div>
              <div class="info-item" v-if="timeRangeWarning">
                <span class="info-warning">⚠️ {{ timeRangeWarning }}</span>
              </div>
            </div>
          </div>
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
          <h3>路段详情 (共{{ segmentDetails.length }}个路段)</h3>
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
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'
import { ConfigLoader } from '@/config/traffic.js'

export default {
  name: 'TrafficRoadSimple',
  data() {
    return {
      isLoading: false,
      mapLoaded: false,
      map: null,
      loadingMessage: '地图加载中...',
      
      // 配置对象 - 将从外部配置文件加载
      config: {
        // 提供默认配置，避免模板渲染错误
        analysis: {
        analysis_type: 'comprehensive',
        segment_types: ['all'],
        aggregation_level: 'segment',
        include_patterns: true,
          min_vehicles: 1
        },
        pagination: {
          pageSize: 50
        },
        map: {
          center: [117.02, 36.67],
          zoom: 12,
          style: 'amap://styles/blue',
          apiKey: 'ac9b745946df9aee02cf0515319407df',
          apiUrl: 'https://webapi.amap.com/maps?v=2.0'
        },
        time: {
          validTimeRange: {
            min: 1378944000,
            max: 1379548799
          }
        },
        api: {
          baseUrl: '/api/traffic/road/analysis',
          timeout: 60000
        }
      },
      
      // 可视化配置
      visualizationType: 'speed',
      
      // 分析数据
      analysisData: null,
      visualizationData: null,
      
      // 图表数据
      speedDistributions: [],
      flowPatterns: [],
      
      // 路段数据
      segmentDetails: [],
      selectedSegment: null,
      
      // 分页
      currentPage: 1,
      segmentColors: {},
      legendInfo: {},
      roadSegmentLayers: [],
      legend: null,
   
      // 动态时间范围 - 将在配置加载后设置
      dateRange: [],
      startDateTime: null,
      endDateTime: null,
      quickTimeRange: 'custom',
      timeRangeWarning: '',
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
      const pageSize = this.config?.pagination?.pageSize || 50
      const start = (this.currentPage - 1) * pageSize
      const end = start + pageSize
      return this.segmentDetails.slice(start, end)
    },
    
    totalPages() {
      const pageSize = this.config?.pagination?.pageSize || 50
      return Math.ceil(this.segmentDetails.length / pageSize)
    }
  },
  
  async mounted() {
    // 先加载配置
    await this.loadConfig()
    
    this.$nextTick(() => {
      // 如果高德地图API未加载，动态加载
      if (!window.AMap) {
        const script = document.createElement('script')
        const apiUrl = this.config?.map?.apiUrl || 'https://webapi.amap.com/maps?v=2.0'
        const apiKey = this.config?.map?.apiKey || 'ac9b745946df9aee02cf0515319407df'
        script.src = `${apiUrl}&key=${apiKey}&plugin=AMap.HeatMap`
        script.async = true
        script.onload = () => {
          this.initMap()
        }
        document.head.appendChild(script)
      } else {
        this.initMap()
      }
    });
  },

  beforeUnmount() {
    this.cleanup()
  },
  
  methods: {
    // 加载配置 - 从外部配置文件加载
    async loadConfig() {
      try {
        // 使用配置加载器加载配置
        const loadedConfig = await ConfigLoader.load()
        
        // 合并配置，保留默认值作为后备
        this.config = { ...this.config, ...loadedConfig }
        
        // 设置时间范围
        const validTimeRange = this.config?.time?.validTimeRange || { min: 1378944000, max: 1379548799 }
        this.dateRange = [
          new Date(validTimeRange.min * 1000 + 60000),
          new Date(validTimeRange.max * 1000 - 60000)
        ]
        
        // 设置默认的开始和结束时间（自定义默认：2013-09-13 00:00:00 ~ 2013-09-14 00:00:00）
        this.startDateTime = new Date('2013-09-13T00:00:00')
        this.endDateTime = new Date('2013-09-14T00:00:00')
        
        console.log('✅ 配置加载完成:', this.config)
        console.log('📅 默认时间范围:', {
          start: this.startDateTime.toLocaleString(),
          end: this.endDateTime.toLocaleString()
        })
      } catch (error) {
        console.warn('⚠️ 配置加载失败，使用默认配置:', error)
        
        // 设置时间范围（使用默认配置）
        const validTimeRange = this.config?.time?.validTimeRange || { min: 1378944000, max: 1379548799 }
        this.dateRange = [
          new Date(validTimeRange.min * 1000 + 60000),
          new Date(validTimeRange.max * 1000 - 60000)
        ]
        // 设置自定义默认时间
        this.startDateTime = new Date('2013-09-13T00:00:00')
        this.endDateTime = new Date('2013-09-14T00:00:00')
      }
    },
    
    async initializeComponent() {
      try {
        await this.loadConfig() // 先加载配置
        this.initMap() // 注意：这里不需要await，因为initMap不是async方法
        await this.performAnalysis()
      } catch (error) {
        console.error('初始化路段分析组件失败:', error)
      }
    },
    
    // 使用高德地图API初始化地图
    initMap() {
      try {
        console.log('🗺️ 开始初始化地图...');
        
        // 检查地图容器是否存在
        const mapContainer = document.getElementById('road-analysis-map-simple');
        if (!mapContainer) {
          console.warn('❌ 地图容器不存在，使用Canvas降级模式');
          this.mapLoaded = false;
          this.initializeFallbackCanvas();
          return;
        }
        console.log('✅ 地图容器存在');

        // 如果高德地图API可用，使用高德地图
        if (window.AMap) {
          try {
            console.log('✅ 高德地图API可用');
            
            // 如果地图已经初始化过，先销毁旧地图
            if (this.map) {
              console.log('🗑️ 销毁旧地图实例');
              this.map.destroy();
            }
            
            // 使用高德地图创建地图
            console.log('🚀 创建高德地图实例...');
            this.map = new AMap.Map('road-analysis-map-simple', {
              center: this.config?.map?.center || [117.02, 36.67],
              zoom: this.config?.map?.zoom || 12,
              mapStyle: this.config?.map?.style || 'amap://styles/blue',
              resizeEnable: true
            });
            
            // 初始化路段图层数组
            this.roadSegmentLayers = [];
            this.mapLoaded = true;
            console.log('✅ 高德地图加载完成，mapLoaded=', this.mapLoaded);
          } catch (amapError) {
            console.error('❌ 高德地图初始化失败:', amapError);
            this.mapLoaded = false;
            this.initializeFallbackCanvas();
          }
        } else {
          console.warn('⚠️ 高德地图API未加载，使用Canvas降级模式');
          this.mapLoaded = false;
          this.initializeFallbackCanvas();
        }
      } catch (error) {
        console.error('❌ 地图初始化失败:', error);
        this.mapLoaded = false;
        this.initializeFallbackCanvas();
      }
    },
    
    async performAnalysis() {
      try {
        this.isLoading = true;
        this.analysisError = null;
       
        // 验证时间范围
        if (!this.checkTimeRange()) {
          this.analysisError = this.timeRangeWarning;
          this.isLoading = false;
          return;
        }
        
        // 使用用户选择的时间范围，转换为时间戳
        const startDate = typeof this.startDateTime === 'string' ? new Date(this.startDateTime) : this.startDateTime;
        const endDate = typeof this.endDateTime === 'string' ? new Date(this.endDateTime) : this.endDateTime;
        
        // 检查是否为有效的Date对象
        if (!(startDate instanceof Date) || !(endDate instanceof Date)) {
          this.analysisError = '时间格式错误，请重新选择时间范围';
          this.isLoading = false;
          return;
        }
        
        if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
          this.analysisError = '无效的时间范围，请重新选择';
          this.isLoading = false;
          return;
        }
        
        const startTime = Math.floor(startDate.getTime() / 1000);
        const endTime = Math.floor(endDate.getTime() / 1000);
        
        console.log('🔍 用户选择的时间范围:', {
          startDateTime: this.startDateTime,
          endDateTime: this.endDateTime,
          startDate: startDate,
          endDate: endDate,
          startTime: startTime,
          endTime: endTime,
          startTimeDate: startDate.toLocaleString(),
          endTimeDate: endDate.toLocaleString()
        });
        
        // 使用 axios 发送请求，将时间参数作为查询参数
        const baseUrl = this.config?.api?.baseUrl || '/api/traffic/road/analysis'
        const response = await axios.post(
          `${baseUrl}?start_time=${startTime}&end_time=${endTime}`,
          {
            analysis_type: this.config?.analysis?.analysis_type || 'comprehensive',
            segment_types: [...(this.config?.analysis?.segment_types || ['all'])], // 转换为普通数组
            aggregation_level: "segment",
            include_patterns: true,
            min_vehicles: this.config?.analysis?.min_vehicles || 1
          }
        );
        
        if (response.data && response.data.success) {
          // 处理API返回的数据
          this.analysisData = response.data;
          // 使用segments数据作为详情显示（包含完整的路段信息）
          this.segmentDetails = response.data.segments || response.data.analysis?.segments || [];
          this.speedDistributions = response.data.speed_distributions || [];
          this.flowPatterns = response.data.flow_patterns || [];
          
          // 直接使用分析API返回的segments数据进行可视化
          console.log('🔍 前端接收到的数据:', {
            segments_data_count: this.segmentDetails.length,
            segments_count: response.data.segments?.length || 0,
            response_segments: response.data.segments || []
          });
          
          // 优先使用顶层的segments字段（修复后的API返回格式）
          if (response.data.segments && response.data.segments.length > 0) {
            this.visualizationData = response.data.segments;
            console.log('✅ 使用response.data.segments作为可视化数据:', this.visualizationData.length);
            
            // 直接渲染路段，不需要调用额外的可视化API
            this.renderRoadSegments();
          }
          // 备用：使用analysis.segments字段（兼容性）
          else if (response.data.analysis?.segments && response.data.analysis.segments.length > 0) {
            this.visualizationData = response.data.analysis.segments;
            console.log('✅ 使用analysis.segments作为可视化数据:', this.visualizationData.length);
            
            // 直接渲染路段，不需要调用额外的可视化API
            this.renderRoadSegments();
        } else {
            console.warn('⚠️ 没有找到segments数据，尝试调用可视化API...');
            // 如果两个位置都没有segments数据，尝试调用可视化API
            await this.loadVisualizationData(startTime, endTime);
          }
          
          this.isAnalysisComplete = true;
        } else {
          this.analysisError = response.data.message || "分析失败，请重试";
        }
      } catch (error) {
        console.error("路段分析出错:", error);
        this.analysisError = error.message || "分析过程中出现错误";
      } finally {
        this.isLoading = false;
      }
    },
    
    // 添加加载可视化数据的方法
    async loadVisualizationData(startTime, endTime) {
      try {
        // 准备请求参数 - 使用查询参数传递时间
        const visualizationType = this.visualizationType || "speed";
        
        // 调用可视化API
        const response = await axios.post(
          `/api/traffic/road/visualization?start_time=${startTime}&end_time=${endTime}`,
          {
            visualization_type: visualizationType
          }
        );
        
        if (response.data && response.data.success) {
          // 处理可视化数据
          this.visualizationData = response.data.visualization_data || {};
          this.segmentColors = response.data.segment_colors || {};
          this.legendInfo = response.data.legend_info || {};
          
          // 在地图上渲染路段
          this.renderRoadSegments();
        } else {
          console.error("加载可视化数据失败:", response.data.message);
        }
      } catch (error) {
        console.error("加载可视化数据出错:", error);
      }
    },

    // 添加渲染路段的方法（使用高德地图）
    renderRoadSegments() {
      console.log('🎨 renderRoadSegments被调用');
      console.log('🗺️ 地图实例状态:', !!this.map);
      console.log('📊 visualizationData:', this.visualizationData);
      console.log('📋 segmentDetails:', this.segmentDetails);
      
      // 确保地图已初始化
      if (!this.map) {
        console.warn('❌ 无法渲染路段，地图未初始化');
        return;
      }

      try {
        // 清除现有的路段图层
        this.roadSegmentLayers.forEach(layer => {
          this.map.remove(layer);
        });
        this.roadSegmentLayers = [];

        // 获取要渲染的路段数据
        let segmentsToRender = [];
        
        // 优先使用visualizationData（包含坐标信息的数据）
        if (this.visualizationData && Array.isArray(this.visualizationData) && this.visualizationData.length > 0) {
          segmentsToRender = this.visualizationData;
          console.log('✅ 使用visualizationData渲染路段:', segmentsToRender.length);
        } 
        // 备用：使用segmentDetails（如果它们包含坐标信息）
        else if (this.segmentDetails && this.segmentDetails.length > 0) {
          // 检查segmentDetails是否包含坐标信息
          const hasCoordinates = this.segmentDetails.some(segment => 
            segment.start_point && segment.end_point &&
            segment.start_point.lat && segment.start_point.lng &&
            segment.end_point.lat && segment.end_point.lng
          );
          
          if (hasCoordinates) {
            segmentsToRender = this.segmentDetails;
            console.log('✅ 使用segmentDetails渲染路段:', segmentsToRender.length);
          } else {
            console.warn('⚠️ segmentDetails不包含坐标信息，无法渲染');
            return;
          }
        }
        else {
          console.warn('⚠️ 没有可用的路段数据进行渲染');
          return;
        }

        console.log('🔍 开始渲染路段，数据样例:', segmentsToRender[0]);

        // 渲染每个路段
        segmentsToRender.forEach(segment => {
          if (segment.start_point && segment.end_point) {
            // 根据可视化类型确定颜色
            let color = this.getSegmentColor(segment);
            
            // 创建路段线段（高德地图格式）
            const segmentLine = new AMap.Polyline({
              path: [
                [segment.start_point.lng, segment.start_point.lat],
                [segment.end_point.lng, segment.end_point.lat]
              ],
              strokeColor: color,
              strokeWeight: 4,
              strokeOpacity: 0.8,
              cursor: 'pointer'
            });

            // 添加点击事件
            segmentLine.on('click', () => {
              this.selectSegment(segment);
            });

            // 创建信息窗体
            const infoWindow = new AMap.InfoWindow({
              content: `
                <div style="padding: 10px;">
                  <h4>路段 ${segment.segment_id}</h4>
                  <p>类型: ${this.getRoadTypeLabel(segment.road_type)}</p>
                  <p>长度: ${(segment.segment_length || 0).toFixed(3)} km</p>
                  <p>平均速度: ${(segment.avg_speed || 0).toFixed(1)} km/h</p>
                  <p>流量: ${(segment.flow_rate || 0).toFixed(0)} veh/h</p>
                  <p>状态: ${this.getCongestionLabel(segment.congestion_level)}</p>
                </div>
              `,
              offset: new AMap.Pixel(0, -30)
            });

            // 添加悬停事件
            segmentLine.on('mouseover', (e) => {
              infoWindow.open(this.map, e.lnglat);
            });

            segmentLine.on('mouseout', () => {
              infoWindow.close();
            });

            // 添加到地图和图层列表
            this.map.add(segmentLine);
            this.roadSegmentLayers.push(segmentLine);
          } else {
            console.warn(`路段 ${segment.segment_id} 缺少坐标信息:`, segment);
          }
        });

        console.log(`✅ 成功渲染了 ${this.roadSegmentLayers.length} 个路段`);

        // 添加图例
        this.addMapLegend();

      } catch (error) {
        console.error('❌ 渲染路段时出错:', error);
      }
    },

    getSegmentColor(segment) {
      switch (this.visualizationType) {
        case 'speed':
          return this.getSpeedColor(segment.avg_speed || 0);
        case 'flow':
          return this.getFlowColor(segment.flow_rate || 0);
        case 'congestion':
          return this.getCongestionColor(segment.congestion_level);
        case 'efficiency':
          return this.getEfficiencyColor(segment.efficiency_score || 0);
        default:
          return '#3388ff';
      }
    },

    getSpeedColor(speed) {
      if (speed >= 50) return '#1a9850';      // 绿色 - 高速
      if (speed >= 30) return '#91d1c2';      // 浅绿 - 中速
      if (speed >= 15) return '#fee08b';      // 黄色 - 低速
      if (speed >= 5) return '#fc8d59';       // 橙色 - 很慢
      return '#d73027';                       // 红色 - 极慢
    },

    getFlowColor(flow) {
      if (flow >= 800) return '#d73027';      // 红色 - 高流量
      if (flow >= 600) return '#fc8d59';      // 橙色 - 中高流量
      if (flow >= 400) return '#fee08b';      // 黄色 - 中流量
      if (flow >= 200) return '#91d1c2';      // 浅绿 - 低流量
      return '#1a9850';                       // 绿色 - 很低流量
    },

    getCongestionColor(level) {
      const colors = {
        'free': '#27ae60',      // 绿色 - 畅通
        'moderate': '#91d1c2',  // 浅绿 - 缓行
        'heavy': '#e7b73c',     // 黄色 - 拥堵
        'jam': '#c02b2b'        // 红色 - 严重拥堵
      };
      return colors[level] || '#3388ff';
    },

    getEfficiencyColor(score) {
      if (score >= 80) return '#1a9850';      // 绿色 - 高效
      if (score >= 60) return '#91d1c2';      // 浅绿 - 较高效
      if (score >= 40) return '#fee08b';      // 黄色 - 一般
      if (score >= 20) return '#fc8d59';      // 橙色 - 低效
      return '#d73027';                       // 红色 - 很低效
    },

    addMapLegend() {
      // 移除现有图例
      if (this.legend) {
        this.map.remove(this.legend);
      }

      // 创建高德地图的自定义控件作为图例
      const legendDiv = document.createElement('div');
      legendDiv.className = 'amap-legend';
      legendDiv.innerHTML = this.getLegendHtml();
      legendDiv.style.cssText = `
        position: absolute;
        bottom: 20px;
        right: 20px;
        background: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
        font-size: 12px;
        z-index: 999;
      `;

      // 添加到地图容器
      const mapContainer = document.getElementById('road-analysis-map-simple');
      if (mapContainer) {
        mapContainer.appendChild(legendDiv);
        this.legend = legendDiv;
      }
    },

    getLegendHtml() {
      const legendData = {
        'speed': {
          title: '速度 (km/h)',
          items: [
            {color: '#1a9850', label: '≥50'},
            {color: '#91d1c2', label: '30-50'},
            {color: '#fee08b', label: '15-30'},
            {color: '#fc8d59', label: '5-15'},
            {color: '#d73027', label: '<5'}
          ]
        },
        'flow': {
          title: '流量 (veh/h)',
          items: [
            {color: '#d73027', label: '≥800'},
            {color: '#fc8d59', label: '600-800'},
            {color: '#fee08b', label: '400-600'},
            {color: '#91d1c2', label: '200-400'},
            {color: '#1a9850', label: '<200'}
          ]
        },
        'congestion': {
          title: '拥堵状态',
          items: [
            {color: '#27ae60', label: '畅通'},
            {color: '#91d1c2', label: '缓行'},
            {color: '#e74c3c', label: '拥堵'},
            {color: '#c0392b', label: '严重拥堵'}
          ]
        },
        'efficiency': {
          title: '运行效率',
          items: [
            {color: '#1a9850', label: '高效 (≥80)'},
            {color: '#91d1c2', label: '较高效 (60-80)'},
            {color: '#fee08b', label: '一般 (40-60)'},
            {color: '#fc8d59', label: '低效 (20-40)'},
            {color: '#d73027', label: '很低效 (<20)'}
          ]
        }
      };

      const legend = legendData[this.visualizationType] || legendData['speed'];
      
      let html = `<h4>${legend.title}</h4>`;
      legend.items.forEach(item => {
        html += `<div><span style="background: ${item.color}; width: 18px; height: 18px; display: inline-block; margin-right: 5px;"></span>${item.label}</div>`;
      });
      
      return html;
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
            { x: 300, y: 400, width: 100, height: 12, color: '#ff0000', label: '城市道路' }
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
    
    cleanup() {
      // 清理地图实例
      if (this.map) {
        try {
          this.map.destroy();
          this.map = null;
        } catch (error) {
          console.warn('清理地图实例时出错:', error);
        }
      }
      
      // 清理图例
      if (this.legend) {
        try {
          const legend = this.legend; // 保存引用，避免在操作过程中被其他代码修改
          if (legend && legend.parentNode) {
            legend.parentNode.removeChild(legend);
          }
        } catch (error) {
          console.warn('清理图例时出错:', error);
        }
        this.legend = null;
      }
      
      // 重置状态
      this.mapLoaded = false;
      console.log('路段分析组件清理完成');
    },
    
    onConfigChange() {
      console.log('配置变更:', this.config);
      // 延迟执行分析，避免频繁请求
      clearTimeout(this.configChangeTimer);
      this.configChangeTimer = setTimeout(() => {
        this.performAnalysis();
      }, 1000);
    },
    
    onVisualizationChange() {
      console.log('可视化类型变更:', this.visualizationType);
      if (this.visualizationData) {
        this.renderRoadSegments();
      }
    },
    
    refreshVisualization() {
      console.log('刷新可视化');
      this.initMap();
      if (this.visualizationData) {
        this.renderRoadSegments();
      }
    },
    
    selectSegment(segment) {
      this.selectedSegment = segment;
      console.log('选中路段:', segment.segment_id);
      
      // 如果地图已加载，聚焦到选中的路段
      if (this.map && this.mapLoaded && segment.start_point && segment.end_point) {
        // 计算路段中心点
        const centerLng = (segment.start_point.lng + segment.end_point.lng) / 2;
        const centerLat = (segment.start_point.lat + segment.end_point.lat) / 2;
        
        // 设置地图中心和缩放
        this.map.setCenter([centerLng, centerLat]);
        this.map.setZoom(15);
      }
    },
    
    exportData() {
      if (!this.analysisData) return;
      
      const data = {
        analysis_summary: this.analysisData.analysis,
        segment_details: this.segmentDetails,
        export_time: new Date().toISOString()
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `road_analysis_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      console.log('数据导出成功');
    },
    
    getRoadTypeLabel(roadType) {
      const labels = {
        'highway': '高速公路',
        'arterial': '主干道', 
        'urban': '城市道路',
        'local': '支路',
        'unknown': '未知'
      }
      return labels[roadType] || roadType
    },
    
    getCongestionLabel(level) {
      const labels = {
        'free': '畅通',
        'moderate': '缓行',
        'heavy': '拥堵', 
        'jam': '严重拥堵'
      }
      return labels[level] || level
    },

    onTimeChange() {
      console.log('时间选择器变更:', this.startDateTime, this.endDateTime);
      
      // 验证时间范围
      if (this.checkTimeRange()) {
        this.performAnalysis();
      }
    },

    setQuickTimeRange(range) {
      this.quickTimeRange = range;
      
      // 获取有效的时间范围
      const validTimeRange = this.config?.time?.validTimeRange || { min: 1378944000, max: 1379548799 }
      const validStart = new Date(validTimeRange.min * 1000);
      const validEnd = new Date(validTimeRange.max * 1000);
      
      let start, end;
      
      if (range === '4h') {
        // 选择有效时间范围的中间4小时
        const midTime = validStart.getTime() + (validEnd.getTime() - validStart.getTime()) / 2;
        start = new Date(midTime - 2 * 60 * 60 * 1000);
        end = new Date(midTime + 2 * 60 * 60 * 1000);
      } else if (range === '8h') {
        // 选择有效时间范围的中间8小时
        const midTime = validStart.getTime() + (validEnd.getTime() - validStart.getTime()) / 2;
        start = new Date(midTime - 4 * 60 * 60 * 1000);
        end = new Date(midTime + 4 * 60 * 60 * 1000);
      } else if (range === '24h') {
        // 选择有效时间范围的中间24小时
        const midTime = validStart.getTime() + (validEnd.getTime() - validStart.getTime()) / 2;
        start = new Date(midTime - 12 * 60 * 60 * 1000);
        end = new Date(midTime + 12 * 60 * 60 * 1000);
      } else if (range === 'custom') {
        // 自定义时，默认设置为2013-09-13 00:00:00 ~ 2013-09-14 00:00:00
        this.startDateTime = new Date('2013-09-13T00:00:00')
        this.endDateTime = new Date('2013-09-14T00:00:00')
        return;
      }
      
      // 确保时间范围在有效范围内
      if (start < validStart) start = validStart;
      if (end > validEnd) end = validEnd;
      
      this.startDateTime = start;
      this.endDateTime = end;
      
      console.log(`🔍 设置快速时间范围 ${range}:`, {
        start: start.toLocaleString(),
        end: end.toLocaleString()
      });
      
      // 验证时间范围并执行分析
      if (this.checkTimeRange()) {
        this.performAnalysis();
      }
    },

    toDate(val) {
      if (val instanceof Date) return val;
      if (typeof val === 'string' || typeof val === 'number') return new Date(val);
      return new Date(NaN); // 其它类型直接无效
    },

    formatDateTime(date) {
      if (!date) return '未选择';
      try {
        const dateObj = this.toDate(date);
        if (isNaN(dateObj.getTime())) return '无效时间';
        return dateObj.toLocaleString();
      } catch (error) {
        console.error('格式化时间时出错:', error);
        return '格式化错误';
      }
    },

    getTimeDuration() {
      if (!this.startDateTime || !this.endDateTime) return 'N/A';
      try {
        const startDate = this.toDate(this.startDateTime);
        const endDate = this.toDate(this.endDateTime);
        if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) return '无效时间';
        const duration = endDate.getTime() - startDate.getTime();
        const hours = Math.floor(duration / (1000 * 60 * 60));
        const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
        return `${hours}小时${minutes}分钟`;
      } catch (error) {
        console.error('计算时间持续时间时出错:', error);
        return '计算错误';
      }
    },

    checkTimeRange() {
      const validTimeRange = this.config?.time?.validTimeRange || { min: 1378944000, max: 1379548799 }
      const validStart = new Date(validTimeRange.min * 1000);
      const validEnd = new Date(validTimeRange.max * 1000);

      if (!this.startDateTime || !this.endDateTime) {
        this.timeRangeWarning = '请选择时间范围';
        return false;
      }

      try {
        // 确保转换为Date对象
        const startDate = typeof this.startDateTime === 'string' ? new Date(this.startDateTime) : this.startDateTime;
        const endDate = typeof this.endDateTime === 'string' ? new Date(this.endDateTime) : this.endDateTime;

        // 检查是否为有效的Date对象
        if (!(startDate instanceof Date) || !(endDate instanceof Date)) {
          this.timeRangeWarning = '时间格式错误';
          return false;
        }

        if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
          this.timeRangeWarning = '时间格式无效';
          return false;
        }

        if (startDate < validStart) {
          this.timeRangeWarning = `开始时间不能早于 ${validStart.toLocaleString()}`;
          return false;
        }
        if (endDate > validEnd) {
          this.timeRangeWarning = `结束时间不能晚于 ${validEnd.toLocaleString()}`;
          return false;
        }
        if (startDate >= endDate) {
          this.timeRangeWarning = '结束时间必须晚于开始时间';
          return false;
        }

        this.timeRangeWarning = '';
        return true;
      } catch (error) {
        console.error('检查时间范围时出错:', error);
        this.timeRangeWarning = '时间验证错误';
        return false;
      }
    },

    getAvailableDataRange() {
      const validTimeRange = this.config?.time?.validTimeRange || { min: 1378944000, max: 1379548799 }
      const start = new Date(validTimeRange.min * 1000).toLocaleString()
      const end = new Date(validTimeRange.max * 1000).toLocaleString()
      return `${start} - ${end}`
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
  margin-bottom: 30px;
}

.analysis-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.control-panel {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.panel-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.control-group label {
  font-weight: 500;
  color: #333;
  font-size: 12px;
}

.control-group select,
.control-group input {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.analyze-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  margin-top: 18px;
}

.analyze-btn:hover {
  background: #2980b9;
}

.analyze-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.stats-cards {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
  color: #666;
}

.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.map-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
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

.map-controls button:hover {
  background: #f8f9fa;
}

.map-container {
  position: relative;
  height: 600px;
}

.map-canvas {
  width: 100%;
  height: 100%;
}

.map-fallback {
  position: relative;
  width: 100%;
  height: 100%;
}

.fallback-canvas {
  width: 100%;
  height: 100%;
  background: #f0f0f0;
}

.canvas-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #666;
}

.analysis-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-section,
.segments-list {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-section h3,
.segments-list h3 {
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
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2980b9);
  border-radius: 10px;
  transition: width 0.3s ease;
}

.bar-label {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  color: white;
  font-weight: 500;
}

.bar-value {
  font-size: 12px;
  color: #666;
  min-width: 40px;
  text-align: right;
}

.segments-table {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 80px 80px 80px 80px 60px 100px;
  gap: 1px;
  background: #f8f9fa;
}

.table-header {
  background: #e9ecef;
  font-weight: 600;
  font-size: 12px;
}

.table-header > div,
.table-row > div {
  padding: 8px 6px;
  background: white;
  font-size: 11px;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.table-row:hover {
  background: #f0f7ff;
}

.table-row.active {
  background: #e3f2fd;
}

.table-row.active > div {
  background: #e3f2fd;
}

.col-id {
  font-family: monospace;
  font-size: 10px;
}

.congestion-free {
  color: #27ae60;
  font-weight: 500;
}

.congestion-moderate {
  color: #f39c12;
  font-weight: 500;
}

.congestion-heavy {
  color: #e74c3c;
  font-weight: 500;
}

.congestion-jam {
  color: #c0392b;
  font-weight: 600;
}

.time-range-picker {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fafafa;
}

.time-input-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.time-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  min-width: 70px;
}

.quick-time-buttons {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e4e7ed;
}

.quick-btn {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
  color: #606266;
}

.quick-btn:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
  color: #409eff;
}

.quick-btn.active {
  background: #409eff;
  color: white;
  border-color: #409eff;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.2);
}

.quick-btn:active {
  transform: translateY(1px);
}

.time-range-info {
  margin-top: 10px;
  padding: 10px;
  background: #f0f7ff;
  border: 1px solid #d9edf7;
  border-radius: 4px;
  font-size: 12px;
  color: #31708f;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.info-label {
  font-weight: 500;
  color: #555;
}

.info-value {
  font-weight: 600;
  color: #333;
}

.info-warning {
  color: #c09853;
  font-weight: 500;
}

.data-range-info {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
}

.data-range-label {
  font-weight: 500;
  color: #333;
}

.data-range-value {
  font-weight: 600;
  color: #2c3e50;
}


.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
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

/* 高德地图图例样式 */
:deep(.amap-legend) {
  background: white;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 0 15px rgba(0,0,0,0.2);
  font-size: 12px;
}

:deep(.amap-legend h4) {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #333;
}

:deep(.amap-legend div) {
  margin: 3px 0;
  display: flex;
  align-items: center;
}

:deep(.amap-legend span) {
  border-radius: 2px;
  margin-right: 5px;
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .panel-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-cards {
    justify-content: center;
  }
  

}
</style> 
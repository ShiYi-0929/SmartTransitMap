<template>
  <div class="spatiotemporal-analysis">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">时空动态分析</h2>
      <p class="page-desc">时间与空间热力图展示，支持聚类算法与OD对分析</p>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <div class="panel-section">
        <h3>分析配置</h3>
        <div class="form-grid">
          <!-- 时间范围 -->
          <div class="form-group">
            <label>开始时间</label>
            <el-date-picker
              v-model="analysisParams.startTime"
              type="datetime"
              placeholder="选择开始时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
            />
          </div>
          
          <div class="form-group">
            <label>结束时间</label>
            <el-date-picker
              v-model="analysisParams.endTime"
              type="datetime"
              placeholder="选择结束时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
            />
          </div>

          <!-- 分析类型 -->
          <div class="form-group">
            <label>分析类型</label>
            <el-select v-model="analysisType" placeholder="选择分析类型">
              <el-option label="动态热力图" value="heatmap" />
              <el-option label="聚类分析" value="clustering" />
              <el-option label="OD对分析" value="od_analysis" />
              <el-option label="综合分析" value="comprehensive" />
            </el-select>
          </div>

          <!-- 时间分辨率 -->
          <div class="form-group">
            <label>时间分辨率(分钟)</label>
            <el-input-number
              v-model="heatmapParams.temporal_resolution"
              :min="5"
              :max="120"
              :step="5"
              controls-position="right"
            />
          </div>

          <!-- 空间分辨率 -->
          <div class="form-group">
            <label>空间分辨率</label>
            <el-select v-model="heatmapParams.spatial_resolution">
              <el-option label="高精度(0.0005°)" :value="0.0005" />
              <el-option label="中精度(0.001°)" :value="0.001" />
              <el-option label="低精度(0.002°)" :value="0.002" />
            </el-select>
          </div>

          <!-- 聚类算法选择 -->
          <div class="form-group" v-show="analysisType === 'clustering'">
            <label>聚类算法</label>
            <el-select v-model="clusteringParams.algorithm">
              <el-option 
                v-for="algo in availableAlgorithms" 
                :key="algo" 
                :label="algo.toUpperCase()" 
                :value="algo" 
              />
            </el-select>
          </div>

          <!-- 数据类型 -->
          <div class="form-group" v-show="analysisType === 'clustering'">
            <label>数据类型</label>
            <el-select v-model="clusteringParams.data_type">
              <el-option label="起点分析" value="pickup" />
              <el-option label="终点分析" value="dropoff" />
              <el-option label="所有点" value="all_points" />
            </el-select>
          </div>
        </div>

        <div class="action-buttons">
          <el-button type="primary" @click="startAnalysis" :loading="loading">
            开始分析
          </el-button>
          <el-button @click="resetParams">重置参数</el-button>
        </div>
      </div>
    </div>

    <!-- 结果展示区域 -->
    <div class="results-section" v-if="analysisResults">
      <!-- 统计卡片 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-value">{{ analysisResults.totalFrames || 0 }}</div>
          <div class="stat-label">时间帧数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ analysisResults.totalClusters || 0 }}</div>
          <div class="stat-label">聚类数量</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ analysisResults.totalODPairs || 0 }}</div>
          <div class="stat-label">OD对数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ formatNumber(analysisResults.avgIntensity) }}</div>
          <div class="stat-label">平均强度</div>
        </div>
      </div>

      <!-- 地图和时间轴控制 -->
      <div class="map-section">
        <div class="map-container">
          <div id="spatiotemporal-map" class="map-display"></div>
          
          <!-- 时间轴控制器 -->
          <div class="time-control-panel" v-if="analysisType === 'heatmap' && timeFrames.length > 0">
            <div class="time-info">
              <span class="current-time">{{ currentTimeLabel }}</span>
              <span class="time-range">{{ timeRangeLabel }}</span>
            </div>
            
            <div class="time-slider">
              <el-slider
                v-model="currentFrameIndex"
                :min="0"
                :max="timeFrames.length - 1"
                :step="1"
                @change="onTimeFrameChange"
              />
            </div>
            
            <div class="playback-controls">
              <el-button-group>
                <el-button icon="el-icon-d-arrow-left" @click="previousFrame" :disabled="currentFrameIndex === 0">
                  上一帧
                </el-button>
                <el-button :icon="isPlaying ? 'el-icon-video-pause' : 'el-icon-video-play'" @click="togglePlayback">
                  {{ isPlaying ? '暂停' : '播放' }}
                </el-button>
                <el-button icon="el-icon-d-arrow-right" @click="nextFrame" :disabled="currentFrameIndex === timeFrames.length - 1">
                  下一帧
                </el-button>
              </el-button-group>
              
              <div class="playback-speed">
                <span>播放速度：</span>
                <el-select v-model="playbackSpeed" size="mini">
                  <el-option label="0.5x" :value="2000" />
                  <el-option label="1x" :value="1000" />
                  <el-option label="2x" :value="500" />
                  <el-option label="4x" :value="250" />
                </el-select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 详细结果 -->
      <div class="detailed-results">
        <!-- 聚类结果 -->
        <div v-if="analysisType === 'clustering' && clusteringResults" class="clustering-results">
          <h3>聚类分析结果</h3>
          <div class="cluster-list">
            <div 
              v-for="cluster in clusteringResults.clusters" 
              :key="cluster.cluster_id"
              class="cluster-item"
              @click="locateCluster(cluster)"
            >
              <div class="cluster-header">
                <span class="cluster-id">聚类 #{{ cluster.cluster_id }}</span>
                <span class="cluster-density">密度: {{ formatNumber(cluster.density) }}</span>
              </div>
              <div class="cluster-info">
                <span>点数: {{ cluster.point_count }}</span>
                <span>中心: ({{ formatCoordinate(cluster.center_lat) }}, {{ formatCoordinate(cluster.center_lng) }})</span>
              </div>
            </div>
          </div>
        </div>

        <!-- OD分析结果 -->
        <div v-if="analysisType === 'od_analysis' && odResults" class="od-results">
          <h3>OD流量分析</h3>
          <div class="top-flows">
            <h4>热门流量路径 TOP 10</h4>
            <div class="flow-list">
              <div 
                v-for="(flow, index) in odResults.top_flows?.slice(0, 10)" 
                :key="index"
                class="flow-item"
                @click="showFlowOnMap(flow)"
              >
                <div class="flow-rank">#{{ index + 1 }}</div>
                <div class="flow-info">
                  <div class="flow-count">{{ flow.flow_count }} 次行程</div>
                  <div class="flow-details">
                    <span>平均距离: {{ formatNumber(flow.avg_distance) }}km</span>
                    <span>平均时长: {{ formatDuration(flow.avg_duration) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  getDynamicHeatmap, 
  performClusteringAnalysis, 
  performODAnalysis, 
  performComprehensiveAnalysis,
  getAvailableAlgorithms 
} from '@/api/traffic'

export default {
  name: 'SpatioTemporalAnalysis',
  data() {
    return {
      // 分析参数
      analysisType: 'heatmap',
      analysisParams: {
        startTime: '2013-09-13T08:00:00',
        endTime: '2013-09-13T12:00:00'
      },
      
      // 热力图参数
      heatmapParams: {
        temporal_resolution: 15,
        spatial_resolution: 0.001,
        smoothing: true,
        normalization: 'minmax'
      },
      
      // 聚类参数
      clusteringParams: {
        algorithm: 'dbscan',
        data_type: 'pickup',
        params: {}
      },
      
      // OD分析参数
      odParams: {
        min_trip_duration: 60,
        max_trip_duration: 7200,
        min_trip_distance: 0.1,
        aggregate_level: 'individual'
      },
      
      // 状态
      loading: false,
      map: null,
      heatmapLayer: null,
      
      // 结果数据
      analysisResults: null,
      timeFrames: [],
      clusteringResults: null,
      odResults: null,
      
      // 时间轴控制
      currentFrameIndex: 0,
      isPlaying: false,
      playbackSpeed: 1000,
      playbackTimer: null,
      
      // 可用算法
      availableAlgorithms: ['dbscan', 'kmeans', 'hierarchical'],
      
      // 地图模式
      mapMode: 'canvas'
    }
  },
  
  computed: {
    currentTimeLabel() {
      if (this.timeFrames.length > 0 && this.currentFrameIndex < this.timeFrames.length) {
        return this.timeFrames[this.currentFrameIndex].time_label
      }
      return ''
    },
    
    timeRangeLabel() {
      if (this.timeFrames.length > 0) {
        const firstFrame = this.timeFrames[0]
        const lastFrame = this.timeFrames[this.timeFrames.length - 1]
        return `${firstFrame.time_label.split('-')[0]} - ${lastFrame.time_label.split('-')[1]}`
      }
      return ''
    }
  },
  
  async mounted() {
    // 暂时跳过地图加载，直接使用Canvas模式
    this.initCanvasDisplay()
    await this.loadAvailableAlgorithms()
  },
  
  beforeDestroy() {
    if (this.playbackTimer) {
      clearInterval(this.playbackTimer)
    }
    if (this.map && this.map.destroy) {
      this.map.destroy()
    }
  },
  
  methods: {
    async waitForAMapLoad() {
      // 等待AMap加载
      return new Promise((resolve) => {
        if (typeof AMap !== 'undefined') {
          resolve()
        } else {
          const checkAMap = () => {
            if (typeof AMap !== 'undefined') {
              resolve()
            } else {
              setTimeout(checkAMap, 100)
            }
          }
          checkAMap()
        }
      })
    },
    
    initMap() {
      try {
        // 检查AMap是否已加载
        if (typeof AMap === 'undefined') {
          console.warn('高德地图API未加载，使用Canvas显示模式')
          this.initCanvasDisplay()
          return
        }
        
        // 初始化高德地图
        this.map = new AMap.Map('spatiotemporal-map', {
          zoom: 12,
          center: [118.8, 32.05],
          mapStyle: 'amap://styles/grey'
        })
        
        // 添加工具条
        this.map.addControl(new AMap.ToolBar({
          position: 'RB'
        }))
        
        this.mapMode = 'amap'
        console.log('地图初始化成功')
      } catch (error) {
        console.error('地图初始化失败:', error)
        this.$message.warning('地图服务不可用，使用简化显示模式')
        this.initCanvasDisplay()
      }
    },
    
    initCanvasDisplay() {
      // 当地图API不可用时，使用Canvas作为降级方案
      const mapContainer = document.getElementById('spatiotemporal-map')
      if (mapContainer) {
        mapContainer.innerHTML = `
          <div style="
            height: 100%; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            text-align: center;
            padding: 20px;
          ">
            <div style="font-size: 24px; margin-bottom: 10px;">📊</div>
            <div style="font-size: 18px; margin-bottom: 10px;">时空分析可视化区域</div>
            <div style="font-size: 14px; opacity: 0.8;">数据将以列表和统计图表形式展示</div>
            <div id="canvas-content" style="margin-top: 20px; width: 100%; max-width: 600px;">
              <!-- 分析结果将在这里显示 -->
            </div>
          </div>
        `
        
        this.mapMode = 'canvas'
        console.log('Canvas显示模式初始化完成')
      }
    },
    
    async loadAvailableAlgorithms() {
      try {
        const result = await getAvailableAlgorithms()
        if (result.success) {
          this.availableAlgorithms = result.algorithms
        }
      } catch (error) {
        console.error('加载算法列表失败:', error)
      }
    },
    
    async startAnalysis() {
      this.loading = true
      
      try {
        switch (this.analysisType) {
          case 'heatmap':
            await this.performHeatmapAnalysis()
            break
          case 'clustering':
            await this.performClusteringAnalysisAction()
            break
          case 'od_analysis':
            await this.performODAnalysisAction()
            break
          case 'comprehensive':
            await this.performComprehensiveAnalysisAction()
            break
        }
      } catch (error) {
        this.$message.error('分析失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    async performHeatmapAnalysis() {
      const params = {
        start_time: this.analysisParams.startTime,
        end_time: this.analysisParams.endTime,
        temporal_resolution: this.heatmapParams.temporal_resolution,
        spatial_resolution: this.heatmapParams.spatial_resolution,
        smoothing: this.heatmapParams.smoothing
      }
      
      const result = await getDynamicHeatmap(params)
      
      if (result.success) {
        this.timeFrames = result.frames
        this.analysisResults = {
          totalFrames: result.frames.length,
          avgIntensity: result.time_series_stats?.avg_intensity_per_frame || 0
        }
        
        this.currentFrameIndex = 0
        this.displayCurrentFrame()
        this.$message.success(`成功生成${result.frames.length}个时间帧的动态热力图`)
      } else {
        throw new Error(result.message)
      }
    },
    
    async performClusteringAnalysisAction() {
      const result = await performClusteringAnalysis(
        this.analysisParams.startTime,
        this.analysisParams.endTime,
        this.clusteringParams
      )
      
      if (result.success) {
        this.clusteringResults = result
        this.analysisResults = {
          totalClusters: result.clusters.length
        }
        
        this.displayClusters()
        this.$message.success(`聚类分析完成，发现${result.clusters.length}个聚类`)
      } else {
        throw new Error(result.message)
      }
    },
    
    async performODAnalysisAction() {
      const result = await performODAnalysis(
        this.analysisParams.startTime,
        this.analysisParams.endTime,
        this.odParams
      )
      
      if (result.success) {
        this.odResults = result
        this.analysisResults = {
          totalODPairs: result.od_pairs.length
        }
        
        this.displayODFlows()
        this.$message.success(`OD分析完成，找到${result.od_pairs.length}个OD对`)
      } else {
        throw new Error(result.message)
      }
    },
    
    async performComprehensiveAnalysisAction() {
      const result = await performComprehensiveAnalysis(
        this.analysisParams.startTime,
        this.analysisParams.endTime,
        this.heatmapParams
      )
      
      if (result.success) {
        this.timeFrames = result.data.data // 时间帧数据
        this.analysisResults = {
          totalFrames: result.data.data.length,
          avgIntensity: result.data.statistics?.time_series_stats?.avg_intensity_per_frame || 0
        }
        
        this.currentFrameIndex = 0
        this.displayCurrentFrame()
        this.$message.success('综合时空分析完成')
      } else {
        throw new Error(result.message)
      }
    },
    
    displayCurrentFrame() {
      if (this.timeFrames.length === 0 || this.currentFrameIndex >= this.timeFrames.length) {
        return
      }
      
      const currentFrame = this.timeFrames[this.currentFrameIndex]
      
      if (this.mapMode === 'canvas') {
        // Canvas模式下显示数据
        this.displayFrameInCanvas(currentFrame)
        return
      }
      
      // 清除之前的热力图
      if (this.heatmapLayer) {
        this.map.remove(this.heatmapLayer)
      }
      
      // 创建热力图数据
      const heatmapData = currentFrame.heatmap_points.map(point => ({
        lng: point.lng,
        lat: point.lat,
        count: point.intensity
      }))
      
      // 创建热力图层
      this.heatmapLayer = new AMap.HeatMap(this.map, {
        radius: 20,
        opacity: [0, 0.8],
        gradient: {
          0.4: 'blue',
          0.6: 'cyan',
          0.7: 'lime',
          0.8: 'yellow',
          1.0: 'red'
        }
      })
      
      this.heatmapLayer.setDataSet({
        data: heatmapData,
        max: Math.max(...heatmapData.map(d => d.count))
      })
    },
    
    displayFrameInCanvas(frame) {
      // 在Canvas模式下显示时间帧数据
      const canvasContent = document.getElementById('canvas-content')
      if (!canvasContent) return
      
      const topPoints = frame.heatmap_points
        .sort((a, b) => b.intensity - a.intensity)
        .slice(0, 10)
      
      canvasContent.innerHTML = `
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; text-align: left;">
          <div style="margin-bottom: 10px; font-weight: bold;">时间: ${frame.time_label}</div>
          <div style="margin-bottom: 10px;">总强度: ${frame.total_intensity.toFixed(2)}</div>
          <div style="margin-bottom: 10px;">数据点数: ${frame.point_count}</div>
          <div style="margin-bottom: 5px; font-weight: bold;">热点区域 TOP 10:</div>
          ${topPoints.map((point, index) => `
            <div style="margin: 3px 0; font-size: 12px;">
              ${index + 1}. (${point.lat.toFixed(4)}, ${point.lng.toFixed(4)}) - 强度: ${point.intensity.toFixed(2)}
            </div>
          `).join('')}
        </div>
      `
    },
    
    displayClusters() {
      if (this.mapMode === 'canvas') {
        this.displayClustersInCanvas()
        return
      }
      
      // 清除地图
      this.map.clearMap()
      
      const colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500', '#800080']
      
      this.clusteringResults.clusters.forEach((cluster, index) => {
        const color = colors[index % colors.length]
        
        // 聚类中心标记
        const centerMarker = new AMap.Marker({
          position: [cluster.center_lng, cluster.center_lat],
          icon: new AMap.Icon({
            size: new AMap.Size(20, 20),
            image: `data:image/svg+xml;base64,${btoa(`<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="10" r="8" fill="${color}" stroke="white" stroke-width="2"/><text x="10" y="14" text-anchor="middle" fill="white" font-size="10">${cluster.cluster_id}</text></svg>`)}`
          }),
          title: `聚类 ${cluster.cluster_id} (${cluster.point_count} 点)`
        })
        
        this.map.add(centerMarker)
        
        // 聚类点
        cluster.points.forEach(point => {
          const pointMarker = new AMap.CircleMarker({
            center: [point.lng, point.lat],
            radius: 3,
            fillColor: color,
            fillOpacity: 0.6,
            strokeColor: color,
            strokeOpacity: 0.8,
            strokeWeight: 1
          })
          
          this.map.add(pointMarker)
        })
      })
      
      // 调整地图视野
      if (this.clusteringResults.clusters.length > 0) {
        const bounds = new AMap.Bounds()
        this.clusteringResults.clusters.forEach(cluster => {
          bounds.extend([cluster.center_lng, cluster.center_lat])
        })
        this.map.setBounds(bounds)
      }
    },
    
    displayClustersInCanvas() {
      const canvasContent = document.getElementById('canvas-content')
      if (!canvasContent) return
      
      const clusters = this.clusteringResults.clusters
        .sort((a, b) => b.density - a.density)
        .slice(0, 8)
      
      canvasContent.innerHTML = `
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; text-align: left;">
          <div style="margin-bottom: 10px; font-weight: bold;">聚类分析结果</div>
          <div style="margin-bottom: 10px;">总聚类数: ${this.clusteringResults.clusters.length}</div>
          <div style="margin-bottom: 5px; font-weight: bold;">密度最高的聚类:</div>
          ${clusters.map((cluster, index) => `
            <div style="margin: 5px 0; padding: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; font-size: 12px;">
              <div>聚类 #${cluster.cluster_id} - 密度: ${cluster.density.toFixed(4)}</div>
              <div>中心: (${cluster.center_lat.toFixed(4)}, ${cluster.center_lng.toFixed(4)})</div>
              <div>点数: ${cluster.point_count}</div>
            </div>
          `).join('')}
        </div>
      `
    },
    
    displayODFlows() {
      // 清除地图
      this.map.clearMap()
      
      // 显示前20个流量最高的OD对
      const topFlows = this.odResults.top_flows?.slice(0, 20) || []
      
      topFlows.forEach((flow, index) => {
        const color = this.getFlowColor(flow.flow_count, topFlows[0].flow_count)
        
        // 起点标记
        const originMarker = new AMap.Marker({
          position: [flow.origin_lng, flow.origin_lat],
          icon: new AMap.Icon({
            size: new AMap.Size(12, 12),
            image: `data:image/svg+xml;base64,${btoa(`<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12"><circle cx="6" cy="6" r="5" fill="green" stroke="white" stroke-width="1"/></svg>`)}`
          })
        })
        
        // 终点标记
        const destMarker = new AMap.Marker({
          position: [flow.destination_lng, flow.destination_lat],
          icon: new AMap.Icon({
            size: new AMap.Size(12, 12),
            image: `data:image/svg+xml;base64,${btoa(`<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12"><circle cx="6" cy="6" r="5" fill="red" stroke="white" stroke-width="1"/></svg>`)}`
          })
        })
        
        // 流量线
        const flowLine = new AMap.Polyline({
          path: [
            [flow.origin_lng, flow.origin_lat],
            [flow.destination_lng, flow.destination_lat]
          ],
          strokeColor: color,
          strokeWeight: Math.max(1, Math.min(8, flow.flow_count / topFlows[0].flow_count * 8)),
          strokeOpacity: 0.7
        })
        
        this.map.add([originMarker, destMarker, flowLine])
      })
    },
    
    getFlowColor(count, maxCount) {
      const ratio = count / maxCount
      if (ratio > 0.8) return '#FF0000'  // 红色
      if (ratio > 0.6) return '#FF8000'  // 橙色
      if (ratio > 0.4) return '#FFFF00'  // 黄色
      if (ratio > 0.2) return '#80FF00'  // 绿黄色
      return '#00FF00'  // 绿色
    },
    
    // 时间轴控制方法
    onTimeFrameChange(index) {
      this.currentFrameIndex = index
      this.displayCurrentFrame()
    },
    
    previousFrame() {
      if (this.currentFrameIndex > 0) {
        this.currentFrameIndex--
        this.displayCurrentFrame()
      }
    },
    
    nextFrame() {
      if (this.currentFrameIndex < this.timeFrames.length - 1) {
        this.currentFrameIndex++
        this.displayCurrentFrame()
      }
    },
    
    togglePlayback() {
      if (this.isPlaying) {
        this.stopPlayback()
      } else {
        this.startPlayback()
      }
    },
    
    startPlayback() {
      this.isPlaying = true
      this.playbackTimer = setInterval(() => {
        if (this.currentFrameIndex < this.timeFrames.length - 1) {
          this.currentFrameIndex++
          this.displayCurrentFrame()
        } else {
          this.stopPlayback()
        }
      }, this.playbackSpeed)
    },
    
    stopPlayback() {
      this.isPlaying = false
      if (this.playbackTimer) {
        clearInterval(this.playbackTimer)
        this.playbackTimer = null
      }
    },
    
    // 交互方法
    locateCluster(cluster) {
      this.map.setCenter([cluster.center_lng, cluster.center_lat])
      this.map.setZoom(15)
    },
    
    showFlowOnMap(flow) {
      const bounds = new AMap.Bounds()
      bounds.extend([flow.origin_lng, flow.origin_lat])
      bounds.extend([flow.destination_lng, flow.destination_lat])
      this.map.setBounds(bounds)
    },
    
    // 工具方法
    formatNumber(num) {
      if (typeof num !== 'number') return '0'
      return num.toFixed(2)
    },
    
    formatCoordinate(coord) {
      return coord.toFixed(4)
    },
    
    formatDuration(seconds) {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      if (hours > 0) {
        return `${hours}小时${minutes}分钟`
      }
      return `${minutes}分钟`
    },
    
    resetParams() {
      this.analysisParams = {
        startTime: '2013-09-13T08:00:00',
        endTime: '2013-09-13T12:00:00'
      }
      this.heatmapParams = {
        temporal_resolution: 15,
        spatial_resolution: 0.001,
        smoothing: true,
        normalization: 'minmax'
      }
      this.clusteringParams = {
        algorithm: 'dbscan',
        data_type: 'pickup',
        params: {}
      }
    }
  }
}
</script>

<style scoped>
.spatiotemporal-analysis {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin: 0 0 10px 0;
}

.page-desc {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.control-panel {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.panel-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2196F3;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.map-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
}

.map-container {
  position: relative;
}

.map-display {
  height: 500px;
  width: 100%;
}

.time-control-panel {
  padding: 15px;
  background: #f8f9fa;
  border-top: 1px solid #eee;
}

.time-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.current-time {
  font-weight: bold;
  color: #2196F3;
}

.time-range {
  color: #666;
  font-size: 14px;
}

.time-slider {
  margin-bottom: 15px;
}

.playback-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.playback-speed {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.detailed-results {
  margin-top: 20px;
}

.clustering-results, .od-results {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.cluster-list, .flow-list {
  max-height: 400px;
  overflow-y: auto;
}

.cluster-item, .flow-item {
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.cluster-item:hover, .flow-item:hover {
  background: #f0f8ff;
  border-color: #2196F3;
}

.cluster-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.cluster-id {
  font-weight: bold;
  color: #2196F3;
}

.cluster-density {
  color: #666;
  font-size: 14px;
}

.cluster-info {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.flow-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.flow-rank {
  background: #2196F3;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.flow-info {
  flex: 1;
}

.flow-count {
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.flow-details {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.top-flows h4 {
  margin: 0 0 15px 0;
  color: #333;
}
</style> 
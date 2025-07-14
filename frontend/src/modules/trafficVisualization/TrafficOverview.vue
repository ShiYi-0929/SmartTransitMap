<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-white mb-2">📊 交通数据总览</h1>
        <p class="text-gray-300">实时交通数据分析与可视化</p>
      </div>

      <!-- 实时统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:border-blue-400/50 transition-all duration-200">
          <div class="flex items-center">
            <div class="p-3 bg-blue-500/20 rounded-lg">
              <svg class="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-gray-300 text-sm">总记录数</p>
              <p class="text-2xl font-bold text-white">{{ totalCount.toLocaleString() }}</p>
              <p class="text-blue-400 text-xs">📊 实时数据</p>
            </div>
          </div>
        </div>

        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:border-green-400/50 transition-all duration-200">
          <div class="flex items-center">
            <div class="p-3 bg-green-500/20 rounded-lg">
              <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-gray-300 text-sm">平均速度</p>
              <p class="text-2xl font-bold text-white">{{ averageSpeed }} km/h</p>
              <p class="text-green-400 text-xs">🚗 当前查询</p>
            </div>
          </div>
        </div>

        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:border-purple-400/50 transition-all duration-200">
          <div class="flex items-center">
            <div class="p-3 bg-purple-500/20 rounded-lg">
              <svg class="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-gray-300 text-sm">活跃车辆</p>
              <p class="text-2xl font-bold text-white">{{ activeVehicles }}</p>
              <p class="text-purple-400 text-xs">🚕 车辆数量</p>
            </div>
          </div>
        </div>

        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:border-orange-400/50 transition-all duration-200">
          <div class="flex items-center">
            <div class="p-3 bg-orange-500/20 rounded-lg">
              <svg class="w-8 h-8 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3"/>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-gray-300 text-sm">时间跨度</p>
              <p class="text-2xl font-bold text-white">{{ timeSpan }}</p>
              <p class="text-orange-400 text-xs">⏱️ 查询范围</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 查询控制面板 -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 mb-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-white">🔍 数据查询控制</h2>
          <div v-if="showError" class="px-4 py-2 bg-red-500/20 border border-red-500/40 rounded-lg">
            <span class="text-red-400 text-sm">{{ errorMessage }}</span>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <!-- 开始时间 -->
          <div>
            <label class="block text-gray-300 text-sm mb-2">开始时间</label>
            <input 
              type="datetime-local" 
              v-model="queryParams.startTime"
              :min="minDate"
              :max="maxDate"
              class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-white focus:border-blue-400 focus:outline-none"
            />
          </div>
          
          <!-- 结束时间 -->
          <div>
            <label class="block text-gray-300 text-sm mb-2">结束时间</label>
            <input 
              type="datetime-local" 
              v-model="queryParams.endTime"
              :min="minDate"
              :max="maxDate"
              class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-white focus:border-blue-400 focus:outline-none"
            />
          </div>
          
          <!-- 地图样式 -->
          <div>
            <label class="block text-gray-300 text-sm mb-2">地图样式</label>
            <select 
              v-model="queryParams.mapStyle"
              @change="changeMapStyle"
              class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-white focus:border-blue-400 focus:outline-none"
            >
              <option value="normal">标准地图</option>
              <option value="dark">暗色地图</option>
              <option value="light">亮色地图</option>
              <option value="whitesmoke">浅灰地图</option>
              <option value="fresh">清新地图</option>
              <option value="blue">蓝色地图</option>
              <option value="darkblue">深蓝地图</option>
            </select>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <!-- 显示点数量限制 -->
          <div>
            <label class="block text-gray-300 text-sm mb-2">地图显示点数量</label>
            <select 
              v-model="queryParams.maxPoints"
              class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-white focus:border-blue-400 focus:outline-none"
            >
              <option value="500">500个点 (快速)</option>
              <option value="1000">1000个点 (推荐)</option>
              <option value="2000">2000个点 (详细)</option>
              <option value="5000">5000个点 (完整)</option>
            </select>
          </div>
          
          <!-- 性能模式 -->
          <div>
            <label class="block text-gray-300 text-sm mb-2">性能模式</label>
            <select 
              v-model="queryParams.performanceMode"
              class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-white focus:border-blue-400 focus:outline-none"
            >
              <option value="balanced">平衡模式</option>
              <option value="performance">性能优先</option>
              <option value="quality">质量优先</option>
            </select>
          </div>
        </div>
        
        <div class="flex items-center justify-between">
          <div class="flex space-x-2">
            <button 
              @click="submitQuery" 
              :disabled="loading"
              class="px-6 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 text-white rounded-lg transition-colors duration-200 flex items-center space-x-2"
            >
              <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <span>{{ loading ? '查询中...' : '开始查询' }}</span>
            </button>
            <button 
              @click="resetQuery"
              class="px-6 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200"
            >
              重置
            </button>
          </div>
          
          <div class="text-sm text-gray-400">
            数据范围：2013年9月11日 - 2013年9月18日
            <span v-if="dataSummary.total_records" class="ml-2">
              ({{ Math.round(dataSummary.total_records / 10000) }}万条记录)
            </span>
            <br>
            <span class="text-xs">
              显示模式：最多{{ queryParams.maxPoints }}个点 | {{ queryParams.performanceMode === 'performance' ? '性能优先' : queryParams.performanceMode === 'quality' ? '质量优先' : '平衡模式' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 功能区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- 交通地图可视化区域 -->
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold text-white">📍 交通地图可视化</h2>
            <div class="flex items-center space-x-2">
              <button 
                @click="queryParams.viewType = 'distribution'"
                :class="queryParams.viewType === 'distribution' ? 'bg-blue-500 text-white' : 'bg-blue-500/20 text-blue-400 transition-all duration-200'"
              >
                分布视图
              </button>
              <div class="flex space-x-1">
                <button @click="zoomIn" class="p-1 bg-gray-600/50 hover:bg-gray-600 text-white rounded">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                  </svg>
                </button>
                <button @click="zoomOut" class="p-1 bg-gray-600/50 hover:bg-gray-600 text-white rounded">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 12H6"/>
                  </svg>
                </button>
                <button @click="resetMap" class="p-1 bg-gray-600/50 hover:bg-gray-600 text-white rounded">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div 
            id="traffic-map" 
            class="h-96 bg-gray-800/50 rounded-lg relative overflow-hidden"
            :class="{ 'opacity-50': loading }"
          >
            <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black/20 z-10">
              <div class="text-center">
                <div class="w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                <p class="text-white text-sm">加载地图数据中...</p>
              </div>
            </div>
            <div v-else-if="!trafficData.length" class="absolute inset-0 flex items-center justify-center">
              <div class="text-center">
                <div class="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <svg class="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3"/>
                  </svg>
                </div>
                <p class="text-gray-300">请设置查询条件并点击"开始查询"</p>
                <p class="text-gray-500 text-sm mt-1">支持分布视图、轨迹分析等多种展示模式</p>
              </div>
            </div>
          </div>
          <!-- 速度颜色图例 -->
          <div class="mt-4 flex justify-center space-x-4">
            <div class="flex items-center">
              <div class="w-4 h-4 rounded-full bg-red-500 mr-2"></div>
              <span class="text-gray-300 text-sm">高速 (>60 km/h)</span>
            </div>
            <div class="flex items-center">
              <div class="w-4 h-4 rounded-full bg-orange-500 mr-2"></div>
              <span class="text-gray-300 text-sm">中速 (30-60 km/h)</span>
            </div>
            <div class="flex items-center">
              <div class="w-4 h-4 rounded-full bg-green-500 mr-2"></div>
              <span class="text-gray-300 text-sm">低速 (10-30 km/h)</span>
            </div>
            <div class="flex items-center">
              <div class="w-4 h-4 rounded-full bg-gray-500 mr-2"></div>
              <span class="text-gray-300 text-sm">静止 (<10 km/h)</span>
            </div>
          </div>
        </div>

        <!-- 实时数据统计面板 -->
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold text-white">📈 实时数据统计</h2>
            <div class="text-xs text-gray-400">
              更新时间: {{ lastUpdate }}
            </div>
          </div>
          
          <div class="space-y-4">
            <!-- 总记录数 -->
            <div class="flex justify-between items-center">
              <span class="text-gray-300">总记录数</span>
              <span class="text-white font-semibold">{{ totalCount.toLocaleString() }} 条</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div class="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500" 
                   :style="`width: ${Math.min((totalCount / 100000) * 100, 100)}%`"></div>
            </div>
            
            <!-- 时间跨度 -->
            <div class="flex justify-between items-center">
              <span class="text-gray-300">时间跨度</span>
              <span class="text-white font-semibold">{{ timeSpan }}</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div class="bg-gradient-to-r from-orange-500 to-yellow-500 h-2 rounded-full transition-all duration-500" 
                   :style="`width: ${Math.min((timeSpanHours / 168) * 100, 100)}%`"></div>
            </div>
            
            <!-- 活跃车辆数 -->
            <div class="flex justify-between items-center">
              <span class="text-gray-300">活跃车辆数</span>
              <span class="text-white font-semibold">{{ activeVehicles }} 辆</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div class="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full transition-all duration-500" 
                   :style="`width: ${Math.min((activeVehicles / 1000) * 100, 100)}%`"></div>
            </div>
            
            <!-- 平均速度 -->
            <div class="flex justify-between items-center">
              <span class="text-gray-300">平均速度</span>
              <span class="text-white font-semibold">{{ averageSpeed }} km/h</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div class="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all duration-500" 
                   :style="`width: ${Math.min((averageSpeed / 80) * 100, 100)}%`"></div>
            </div>
            
            <!-- 总里程 -->
            <div class="flex justify-between items-center">
              <span class="text-gray-300">总里程</span>
              <span class="text-white font-semibold">{{ totalDistance.toLocaleString() }} km</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div class="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-500" 
                   :style="`width: ${Math.min((totalDistance / 10000) * 100, 100)}%`"></div>
            </div>
            
            <!-- 覆盖区域 -->
            <div class="flex justify-between items-center">
              <span class="text-gray-300">覆盖区域</span>
              <span class="text-white font-semibold">{{ coverageArea }}</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div class="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full transition-all duration-500" 
                   :style="`width: ${coverageArea === '济南市区' ? 100 : 0}%`"></div>
            </div>
          </div>
          
          <!-- 数据质量指标 -->
          <div class="mt-6 pt-4 border-t border-gray-600">
            <div class="flex justify-between items-center mb-2">
              <span class="text-gray-300 text-sm">数据质量评分</span>
              <span class="text-green-400 font-semibold">{{ dataQualityScore }}%</span>
            </div>
            <div class="w-full h-1">
              <div class="bg-gradient-to-r from-green-500 to-emerald-400 h-1 rounded-full transition-all duration-500" 
                   :style="`width: ${dataQualityScore}%`"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 功能模块导航 -->
      <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <h2 class="text-xl font-semibold text-white mb-4">🚀 交通分析模块</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button @click="navigateToModule('track')" class="p-3 bg-blue-500/20 hover:bg-blue-500/30 rounded-lg text-blue-400 transition-all duration-200">
            <div class="flex flex-col items-center">
              <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3"/>
              </svg>
              <span class="text-xs">轨迹查询</span>
            </div>
          </button>
          <button @click="navigateToModule('heatmap')" class="p-3 bg-purple-500/20 hover:bg-purple-500/30 rounded-lg text-purple-400 transition-all duration-200">
            <div class="flex flex-col items-center">
              <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              <span class="text-xs">热力图分析</span>
            </div>
          </button>
          <button @click="navigateToModule('anomaly')" class="p-3 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-red-400 transition-all duration-200">
            <div class="flex flex-col items-center">
              <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 15.5c-.77.833.192 2.5 1.732 2.5z"/>
              </svg>
              <span class="text-xs">异常检测</span>
            </div>
          </button>
          <button @click="navigateToModule('statistics')" class="p-3 bg-green-500/20 hover:bg-green-500/30 rounded-lg text-green-400 transition-all duration-200">
            <div class="flex flex-col items-center">
              <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              <span class="text-xs">统计分析</span>
            </div>
          </button>
          <button @click="navigateToModule('spatiotemporal')" class="p-3 bg-indigo-500/20 hover:bg-indigo-500/30 rounded-lg text-indigo-400 transition-all duration-200">
            <div class="flex flex-col items-center">
              <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span class="text-xs">时空动态</span>
            </div>
          </button>
          <button @click="navigateToModule('road')" class="p-3 bg-yellow-500/20 hover:bg-yellow-500/30 rounded-lg text-yellow-400 transition-all duration-200">
            <div class="flex flex-col items-center">
              <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3"/>
              </svg>
              <span class="text-xs">路段分析</span>
            </div>
          </button>
          <button @click="showAllModules" class="p-3 bg-cyan-500/20 hover:bg-cyan-500/30 rounded-lg text-cyan-400 transition-all duration-200">
            <div class="flex flex-col items-center">
              <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"/>
              </svg>
              <span class="text-xs">所有模块</span>
            </div>
          </button>
        </div>
      </div>

      <!-- 底部提示 -->
      <div class="mt-8 text-center">
        <div class="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-500/20 rounded-lg px-4 py-2">
          <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span class="text-blue-400 text-sm">
            点击上方标签页切换到不同的功能模块，如轨迹查询、热力图分析等
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getTrafficVisualization, getTrafficSummary, getDataFilesInfo } from '@/api/traffic'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const trafficData = ref([])
const dataSummary = ref({})
const filesInfo = ref([])
const queryParams = ref({
  startTime: "2013-09-11T16:00",
  endTime: "2013-09-11T20:00",
  viewType: 'distribution',
  mapStyle: 'normal',
  maxPoints: 1000,
  performanceMode: 'balanced'
})

// 错误处理
const errorMessage = ref('')
const showError = ref(false)

// 地图相关
let map = null
const markers = ref([])

// 地图风格配置
const mapStyleOptions = {
  normal: 'amap://styles/normal',
  dark: 'amap://styles/dark',
  light: 'amap://styles/light',
  whitesmoke: 'amap://styles/whitesmoke',
  fresh: 'amap://styles/fresh',
  blue: 'amap://styles/blue',
  darkblue: 'amap://styles/darkblue'
}

// 计算属性 - 实时统计数据
const totalCount = computed(() => trafficData.value.length)

const timeSpan = computed(() => {
  if (!queryParams.value.startTime || !queryParams.value.endTime) return '-'
  const start = new Date(queryParams.value.startTime)
  const end = new Date(queryParams.value.endTime)
  const hours = Math.round((end - start) / (1000 * 60 * 60))
  return `${hours} 小时`
})

const timeSpanHours = computed(() => {
  if (!queryParams.value.startTime || !queryParams.value.endTime) return 0
  const start = new Date(queryParams.value.startTime)
  const end = new Date(queryParams.value.endTime)
  return (end - start) / (1000 * 60 * 60)
})

const coverageArea = computed(() => {
  return trafficData.value.length > 0 ? '济南市区' : '-'
})

const activeVehicles = computed(() => {
  if (trafficData.value.length > 0) {
    const uniqueVehicles = new Set(trafficData.value.map(item => item.vehicleId || item.vehicle_id))
    return uniqueVehicles.size
  }
  return dataSummary.value.unique_vehicles || 0
})

const averageSpeed = computed(() => {
  if (trafficData.value.length > 0) {
    const validSpeeds = trafficData.value
      .map(item => item.speed)
      .filter(speed => speed !== null && speed !== undefined && !isNaN(speed))
    
    if (validSpeeds.length > 0) {
      const totalSpeed = validSpeeds.reduce((sum, speed) => sum + speed, 0)
      return Math.round(totalSpeed / validSpeeds.length)
    }
  }
  return dataSummary.value.avg_speed_kmh || 0
})

const totalDistance = computed(() => {
  if (trafficData.value.length > 0) {
    return Math.round(trafficData.value.length * 0.1)
  }
  return Math.round((dataSummary.value.total_records || 0) * 0.05)
})

const lastUpdate = computed(() => {
  return new Date().toLocaleTimeString()
})

const dataQualityScore = computed(() => {
  if (trafficData.value.length === 0) return 0
  let score = 100
  const missingCoords = trafficData.value.filter(item => 
    !item.lng || !item.lat || item.lng <= 0 || item.lat <= 0
  ).length
  score -= (missingCoords / trafficData.value.length) * 30
  const invalidSpeeds = trafficData.value.filter(item => 
    item.speed === null || item.speed === undefined || isNaN(item.speed) || item.speed < 0
  ).length
  score -= (invalidSpeeds / trafficData.value.length) * 30
  const invalidTimestamps = trafficData.value.filter(item => 
    !item.timestamp || isNaN(new Date(item.timestamp).getTime())
  ).length
  score -= (invalidTimestamps / trafficData.value.length) * 20
  const missingVehicleIds = trafficData.value.filter(item => 
    !item.vehicleId && !item.vehicle_id
  ).length
  score -= (missingVehicleIds / trafficData.value.length) * 20
  return Math.max(0, Math.round(score))
})

// 设置日期选择器的最小和最大值
const minDate = "2013-09-11T00:00"
const maxDate = "2013-09-18T23:59"

// 查询相关函数
const submitQuery = async () => {
  errorMessage.value = ''
  showError.value = false
  
  if (!queryParams.value.startTime || !queryParams.value.endTime) {
    errorMessage.value = '请选择查询时间范围'
    showError.value = true
    return
  }
  
  const startTimeUTC = convertToUTC(queryParams.value.startTime)
  const endTimeUTC = convertToUTC(queryParams.value.endTime)
  
  const minValidTime = 1378857600
  const maxValidTime = 1379548799
  
  if (startTimeUTC < minValidTime || startTimeUTC > maxValidTime || 
      endTimeUTC < minValidTime || endTimeUTC > maxValidTime) {
    errorMessage.value = '查询时间超出数据集范围（2013年9月11日至9月18日）'
    showError.value = true
    return
  }
  
  loading.value = true
  try {
    const response = await getTrafficVisualization(
      startTimeUTC,
      endTimeUTC,
      queryParams.value.viewType,
      null, // 移除 vehicleId 参数
      queryParams.value.mapStyle
    )
    
    if (response.data.success) {
      trafficData.value = response.data.data
      nextTick(() => {
        setTimeout(() => {
          updateMap()
        }, 200)
      })
    } else {
      errorMessage.value = response.data.message || '查询失败'
      showError.value = true
    }
  } catch (error) {
    errorMessage.value = `查询失败: ${error.message}`
    showError.value = true
    console.error('API请求错误:', error)
  } finally {
    loading.value = false
  }
}

const resetQuery = () => {
  queryParams.value.startTime = "2013-09-11T16:00"
  queryParams.value.endTime = "2013-09-11T20:00"
  queryParams.value.viewType = 'distribution'
  queryParams.value.mapStyle = 'normal'
  queryParams.value.maxPoints = 1000
  queryParams.value.performanceMode = 'balanced'
  
  errorMessage.value = ''
  showError.value = false
  trafficData.value = []
  
  if (map) {
    try {
      if (markers.value.length > 0) {
        map.remove(markers.value)
        markers.value = []
      }
      changeMapStyle()
    } catch (error) {
      console.error('❌ 重置地图失败:', error)
    }
  }
}

const convertToUTC = (dateString) => {
  if (!dateString) return 0
  try {
    const date = new Date(dateString)
    return Math.floor(date.getTime() / 1000)
  } catch (error) {
    console.error('时间转换错误:', error)
    return 0
  }
}

const navigateToModule = (module) => {
  console.log(`导航到模块: ${module}`)
  router.push(`/traffic/${module}`)
}

const showAllModules = () => {
  console.log('显示所有模块')
}

const initMap = () => {
  console.log('🗺️ 开始初始化地图...')
  console.log('🌍 AMap 可用性:', !!window.AMap)
  
  const mapContainer = document.getElementById('traffic-map')
  if (!mapContainer) {
    console.error('❌ 地图容器未找到')
    return
  }
  console.log('📦 地图容器找到:', mapContainer)
  
  if (window.AMap) {
    try {
      map = new window.AMap.Map('traffic-map', {
        zoom: 13,
        center: [117.000923, 36.675807],
        mapStyle: getMapStyleUrl()
      })
      
      map.on('complete', () => {
        console.log('✅ 地图初始化完成')
        console.log('🗺️ 地图实例信息:', {
          center: map.getCenter(),
          zoom: map.getZoom(),
          size: map.getSize()
        })
      })
      
      map.on('click', (e) => {
        console.log('🖱️ 地图点击事件:', e.lnglat)
      })
      
      console.log('🗺️ 地图实例已创建:', map)
    } catch (error) {
      console.error('❌ 地图初始化失败:', error)
    }
  } else {
    console.error('❌ AMap 库未加载')
  }
}

const updateMap = () => {
  if (!map || !trafficData.value?.length) {
    console.log('⚠️ 跳过地图更新:', { hasMap: !!map, dataLength: trafficData.value?.length || 0 })
    return
  }
  
  try {
    if (markers.value.length > 0) {
      map.remove(markers.value)
    }
    markers.value = []
    
    if (queryParams.value.viewType === 'distribution') {
      renderDistributionView()
    }
  } catch (error) {
    console.error('❌ 更新地图失败:', error)
  }
}

const getMapStyleUrl = () => {
  return mapStyleOptions[queryParams.value.mapStyle] || mapStyleOptions.normal
}

const renderDistributionView = () => {
  console.log('🗺️ renderDistributionView 开始执行')
  
  if (!map) {
    console.warn('❌ 地图实例不存在')
    return
  }
  
  if (!trafficData.value || trafficData.value.length === 0) {
    console.warn('❌ 没有数据:', trafficData.value?.length || 0)
    return
  }
  
  console.log('✅ 开始渲染分布视图，数据点数量:', trafficData.value.length)
  console.log('📊 前3个数据点示例:', trafficData.value.slice(0, 3))
  
  const newMarkers = []
  let validPoints = 0
  let invalidPoints = 0
  
  let dataToProcess = trafficData.value
  const maxPoints = parseInt(queryParams.value.maxPoints) || 1000
  
  if (dataToProcess.length > maxPoints) {
    console.log(`📊 数据点过多(${dataToProcess.length}个)，采样到${maxPoints}个点`)
    
    if (queryParams.value.performanceMode === 'performance') {
      const step = Math.floor(dataToProcess.length / maxPoints)
      dataToProcess = dataToProcess.filter((_, index) => index % step === 0).slice(0, maxPoints)
    } else if (queryParams.value.performanceMode === 'quality') {
      const highSpeedPoints = dataToProcess.filter(p => (p.speed || 0) > 50)
      const normalPoints = dataToProcess.filter(p => (p.speed || 0) <= 50)
      
      const highSpeedCount = Math.min(highSpeedPoints.length, Math.floor(maxPoints * 0.3))
      const normalCount = maxPoints - highSpeedCount
      
      const step = Math.floor(normalPoints.length / normalCount)
      const sampledNormal = normalPoints.filter((_, index) => index % step === 0).slice(0, normalCount)
      
      dataToProcess = [...highSpeedPoints.slice(0, highSpeedCount), ...sampledNormal]
    } else {
      const step = Math.floor(dataToProcess.length / maxPoints)
      dataToProcess = dataToProcess.filter((_, index) => index % step === 0).slice(0, maxPoints)
    }
  }
  
  console.log(`📍 将处理 ${dataToProcess.length} 个数据点 (${queryParams.value.performanceMode}模式)`)
  
  for (let i = 0; i < dataToProcess.length; i++) {
    const point = dataToProcess[i]
    const lng = point.lng || point.lon
    const lat = point.lat
    const vehicleId = point.vehicle_id || point.vehicleId || 'unknown'
    const speed = point.speed || 0
    
    if (i < 3 || i % 100 === 0) {
      console.log(`📍 第${i+1}个点:`, { lng, lat, vehicleId, speed })
    }
    
    if (lng && lat && typeof lng === 'number' && typeof lat === 'number') {
      if (lat >= 36.0 && lat <= 37.0 && lng >= 116.0 && lng <= 118.0) {
        try {
          let color = '#00cfff'
          if (speed > 60) {
            color = '#ff4444'
          } else if (speed > 30) {
            color = '#ffaa00'
          } else if (speed > 10) {
            color = '#00ff00'
          } else {
            color = '#888888'
          }
          
          const marker = new window.AMap.Marker({
            position: [lng, lat],
            title: `车辆: ${vehicleId} 速度: ${speed.toFixed(1)} km/h`,
            icon: new window.AMap.Icon({
              size: new window.AMap.Size(12, 12),
              image: `data:image/svg+xml;base64,${btoa(`
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="6" cy="6" r="5" fill="${color}" stroke="#fff" stroke-width="1"/>
                  <circle cx="6" cy="6" r="2" fill="#fff"/>
                </svg>
              `)}`,
              imageSize: new window.AMap.Size(12, 12)
            })
          })
          newMarkers.push(marker)
          validPoints++
        } catch (error) {
          console.error('❌ 创建标记失败:', error)
          invalidPoints++
        }
      } else {
        console.warn('⚠️ 坐标超出范围:', { lng, lat })
        invalidPoints++
      }
    } else {
      console.warn('⚠️ 无效坐标:', { lng, lat })
      invalidPoints++
    }
  }
  
  console.log(`📈 统计: 有效=${validPoints}, 无效=${invalidPoints}`)
  
  if (newMarkers.length > 0) {
    try {
      console.log('🎯 准备添加标记到地图...')
      console.log('📌 第一个标记位置:', newMarkers[0].getPosition())
      
      map.add(newMarkers)
      console.log('✅ 标记已添加到地图')
      
      markers.value = newMarkers
      
      if (newMarkers.length > 1) {
        map.setFitView(newMarkers)
        console.log('🔍 地图视图已调整')
      } else {
        const pos = newMarkers[0].getPosition()
        map.setCenter([pos.lng, pos.lat])
        console.log('🎯 地图中心已设置到标记位置')
      }
      
      setTimeout(() => {
        const overlays = map.getAllOverlays()
        console.log('🗺️ 地图上的覆盖物数量:', overlays.length)
        console.log('📍 当前地图中心:', map.getCenter())
        console.log('🔍 当前地图缩放:', map.getZoom())
      }, 1000)
      
      console.log('✅ 成功渲染', newMarkers.length, '个标记')
    } catch (error) {
      console.error('❌ 添加标记失败:', error)
      console.error('错误详情:', error.stack)
    }
  } else {
    console.warn('⚠️ 没有有效标记')
  }
}

const renderTrajectoryView = () => {
  if (!map || !trafficData.value) return
  
  trafficData.value.forEach(track => {
    if (!track.points || track.points.length < 2) return
    
    const path = track.points.map(point => [point.lng, point.lat])
    
    const polyline = new window.AMap.Polyline({
      path: path,
      strokeColor: '#3366FF',
      strokeWeight: 5,
      strokeOpacity: 0.8
    })
    
    map.add(polyline)
    
    const startMarker = new window.AMap.Marker({
      position: path[0],
      title: '起点',
      icon: new window.AMap.Icon({
        size: new window.AMap.Size(20, 20),
        image: `data:image/svg+xml;base64,${btoa(`
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="8" fill="#00ff00" stroke="#fff" stroke-width="2"/>
            <text x="10" y="14" text-anchor="middle" fill="#fff" font-size="10" font-weight="bold">S</text>
          </svg>
        `)}`,
        imageSize: new window.AMap.Size(20, 20)
      })
    })
    
    const endMarker = new window.AMap.Marker({
      position: path[path.length - 1],
      title: '终点',
      icon: new window.AMap.Icon({
        size: new window.AMap.Size(20, 20),
        image: `data:image/svg+xml;base64,${btoa(`
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="8" fill="#ff4444" stroke="#fff" stroke-width="2"/>
            <text x="10" y="14" text-anchor="middle" fill="#fff" font-size="10" font-weight="bold">E</text>
          </svg>
        `)}`,
        imageSize: new window.AMap.Size(20, 20)
      })
    })
    
    map.add([startMarker, endMarker])
  })
  
  map.setFitView()
}

const renderHeatmapView = () => {
  if (!map || !trafficData.value || !window.AMap.HeatMap) return
  
  const heatmap = new window.AMap.HeatMap(map, {
    radius: 25,
    opacity: [0, 0.8]
  })
  
  const points = trafficData.value.map(point => {
    return {
      lng: point.lng,
      lat: point.lat,
      count: point.count || 1
    }
  })
  
  heatmap.setDataSet({
    data: points,
    max: 100
  })
}

const zoomIn = () => {
  if (map) map.zoomIn()
}

const zoomOut = () => {
  if (map) map.zoomOut()
}

const resetMap = () => {
  if (map) {
    map.setZoom(13)
    map.setCenter([117.000923, 36.675807])
  }
}

const changeMapStyle = () => {
  if (map) {
    const newStyle = getMapStyleUrl()
    map.setMapStyle(newStyle)
    console.log('地图风格已切换为:', queryParams.value.mapStyle, newStyle)
  }
}

const loadDataSummary = async () => {
  try {
    const response = await getTrafficSummary()
    if (response.data.success) {
      dataSummary.value = response.data.summary
      console.log('数据概要加载成功:', dataSummary.value)
    } else {
      console.warn('数据概要加载失败:', response.data.message)
    }
  } catch (error) {
    console.error('获取数据概要失败:', error)
  }
}

const loadFilesInfo = async () => {
  try {
    const response = await getDataFilesInfo()
    if (response.data.success) {
      filesInfo.value = response.data.files
      console.log('文件信息加载成功:', filesInfo.value)
    }
  } catch (error) {
    console.error('获取文件信息失败:', error)
  }
}

onMounted(async () => {
  console.log('📊 交通数据总览页面已加载')
  
  await loadDataSummary()
  await loadFilesInfo()
  
  queryParams.value.startTime = "2013-09-11T16:00"
  queryParams.value.endTime = "2013-09-11T20:00"
  
  initMap()
  
  if (!window.AMap) {
    const script = document.createElement('script')
    script.src = 'https://webapi.amap.com/maps?v=2.0&key=ac9b745946df9aee02cf0515319407df&plugin=AMap.HeatMap'
    script.async = true
    script.onload = () => {
      initMap()
    }
    document.head.appendChild(script)
  }
})
</script>

<style scoped>
.tech-bg {
  background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #312e81 100%);
}

.alert {
  margin-bottom: 20px;
  padding: 12px 16px;
  border-radius: 4px;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
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
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
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
          
          <!-- 车辆ID -->
          <div>
            <label class="block text-gray-300 text-sm mb-2">车辆ID（可选）</label>
            <input 
              type="text" 
              v-model="queryParams.vehicleId"
              placeholder="输入车辆ID"
              class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-white focus:border-blue-400 focus:outline-none placeholder-gray-500"
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
            数据范围：2013年9月12日 - 2013年9月18日
          </div>
        </div>
      </div>

      <!-- 功能区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- 交通地图可视化区域 -->
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold text-white">📍 交通地图可视化</h2>
            <div class="flex items-center space-x-2">
              <button 
                @click="queryParams.viewType = 'distribution'"
                :class="queryParams.viewType === 'distribution' ? 'bg-blue-500 text-white' : 'bg-blue-500/20 text-blue-400'"
                class="px-3 py-1 rounded-lg text-sm transition-all duration-200"
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
            
            <!-- 覆盖区域 -->
            <div class="flex justify-between items-center">
              <span class="text-gray-300">覆盖区域</span>
              <span class="text-white font-semibold">{{ coverageArea }}</span>
            </div>
          </div>
          
          <!-- 数据质量指标 -->
          <div class="mt-6 pt-4 border-t border-gray-600">
            <div class="flex justify-between items-center mb-2">
              <span class="text-gray-300 text-sm">数据质量评分</span>
              <span class="text-green-400 font-semibold">{{ dataQualityScore }}%</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-1">
              <div class="bg-gradient-to-r from-green-500 to-emerald-400 h-1 rounded-full transition-all duration-500" 
                   :style="`width: ${dataQualityScore}%`"></div>
            </div>
          </div>
        </div>

        <!-- 功能模块导航 -->
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <h2 class="text-xl font-semibold text-white mb-4">🚀 交通分析模块</h2>
          <div class="grid grid-cols-2 gap-3">
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
            <button @click="navigateToModule('pattern')" class="p-3 bg-pink-500/20 hover:bg-pink-500/30 rounded-lg text-pink-400 transition-all duration-200">
              <div class="flex flex-col items-center">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                </svg>
                <span class="text-xs">模式识别</span>
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

        <!-- 最近活动 -->
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <h2 class="text-xl font-semibold text-white mb-4">🕒 最近活动</h2>
          <div class="space-y-3">
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-green-400 rounded-full"></div>
              <div class="flex-1">
                <p class="text-gray-300 text-sm">数据同步完成</p>
                <p class="text-gray-500 text-xs">2分钟前</p>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
              <div class="flex-1">
                <p class="text-gray-300 text-sm">新增 1,234 条轨迹记录</p>
                <p class="text-gray-500 text-xs">15分钟前</p>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-orange-400 rounded-full"></div>
              <div class="flex-1">
                <p class="text-gray-300 text-sm">检测到异常车辆行为</p>
                <p class="text-gray-500 text-xs">1小时前</p>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-purple-400 rounded-full"></div>
              <div class="flex-1">
                <p class="text-gray-300 text-sm">定时报告生成</p>
                <p class="text-gray-500 text-xs">3小时前</p>
              </div>
            </div>
          </div>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTrafficVisualization } from '@/api/traffic'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const trafficData = ref([])
const queryParams = ref({
  startTime: "2013-09-13T08:00",
  endTime: "2013-09-13T12:00",
  vehicleId: '',
  viewType: 'distribution',
  mapStyle: 'normal'
})

// 错误处理
const errorMessage = ref('')
const showError = ref(false)

// 地图相关
let map = null
let markers = []

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

const coverageArea = computed(() => {
  return trafficData.value.length > 0 ? '济南市区' : '-'
})

const activeVehicles = computed(() => {
  const uniqueVehicles = new Set(trafficData.value.map(item => item.vehicleId || item.vehicle_id))
  return uniqueVehicles.size
})

const averageSpeed = computed(() => {
  if (trafficData.value.length === 0) return 0
  const totalSpeed = trafficData.value.reduce((sum, item) => sum + (item.speed || 0), 0)
  return Math.round(totalSpeed / trafficData.value.length)
})

const totalDistance = computed(() => {
  return Math.round(trafficData.value.length * 0.1) // 模拟计算，每条记录约0.1km
})

const lastUpdate = computed(() => {
  return new Date().toLocaleTimeString()
})

const dataQualityScore = computed(() => {
  if (trafficData.value.length === 0) return 0
  // 简单的数据质量评分算法
  const validRecords = trafficData.value.filter(item => 
    item.lng && item.lat && item.lng > 0 && item.lat > 0
  ).length
  return Math.round((validRecords / trafficData.value.length) * 100)
})

// 设置日期选择器的最小和最大值
const minDate = "2013-09-12T00:00"
const maxDate = "2013-09-18T23:59"

// 查询相关函数
const submitQuery = async () => {
  // 清除之前的错误
  errorMessage.value = ''
  showError.value = false
  
  // 检查必填字段
  if (!queryParams.value.startTime || !queryParams.value.endTime) {
    errorMessage.value = '请选择查询时间范围'
    showError.value = true
    return
  }
  
  // 转换为UTC时间戳
  const startTimeUTC = convertToUTC(queryParams.value.startTime)
  const endTimeUTC = convertToUTC(queryParams.value.endTime)
  
  // 定义数据集的有效时间范围
  const minValidTime = 1378944000  // 2013-09-12 00:00:00 UTC
  const maxValidTime = 1379548799  // 2013-09-18 23:59:59 UTC
  
  // 验证时间范围
  if (startTimeUTC < minValidTime || startTimeUTC > maxValidTime || 
      endTimeUTC < minValidTime || endTimeUTC > maxValidTime) {
    errorMessage.value = '查询时间超出数据集范围（2013年9月12日至9月18日）'
    showError.value = true
    return
  }
  
  // 时间范围有效，继续查询
  loading.value = true
  try {
    const response = await getTrafficVisualization(
      startTimeUTC,
      endTimeUTC,
      queryParams.value.viewType,
      queryParams.value.vehicleId || null,
      queryParams.value.mapStyle
    )
    
    if (response.data.success) {
      trafficData.value = response.data.data
      // 更新地图显示
      setTimeout(() => {
        updateMap()
      }, 100)
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
  queryParams.value.startTime = "2013-09-13T08:00"
  queryParams.value.endTime = "2013-09-13T12:00"
  queryParams.value.vehicleId = ""
  queryParams.value.viewType = 'distribution'
  queryParams.value.mapStyle = 'normal'
  
  errorMessage.value = ''
  showError.value = false
  trafficData.value = []
  
  // 清除地图并重置风格
  if (map) {
    map.clearMap()
    changeMapStyle()
  }
}

// 时间转换函数
const convertToUTC = (dateString) => {
  if (!dateString) return 0
  try {
    const date = new Date(dateString)
    return Math.floor(date.getTime() / 1000) // 转换为秒级时间戳
  } catch (error) {
    console.error('时间转换错误:', error)
    return 0
  }
}

// 导航功能
const navigateToModule = (module) => {
  console.log(`导航到模块: ${module}`)
  router.push(`/traffic/${module}`)
}

const showAllModules = () => {
  console.log('显示所有模块')
  // 可以导航到一个显示所有模块的页面，或者保持在当前页面
}



// 地图相关功能
const initMap = () => {
  console.log('初始化地图...')
  if (window.AMap) {
    map = new window.AMap.Map('traffic-map', {
      zoom: 13,
      center: [117.000923, 36.675807], // 济南市中心坐标
      mapStyle: getMapStyleUrl()
    })
  } else {
    console.error('AMap is not loaded')
  }
}

// 更新地图显示
const updateMap = () => {
  if (!map || !trafficData.value.length) return
  
  // 清除之前的标记
  map.clearMap()
  markers = []
  
  // 根据视图类型更新地图
  if (queryParams.value.viewType === 'distribution') {
    renderDistributionView()
  }
}

// 获取地图样式URL
const getMapStyleUrl = () => {
  return mapStyleOptions[queryParams.value.mapStyle] || mapStyleOptions.normal
}

const renderDistributionView = () => {
  if (!map || !trafficData.value) return
  
  trafficData.value.forEach(point => {
    const marker = new window.AMap.Marker({
      position: [point.lng, point.lat],
      title: `车辆ID: ${point.vehicle_id}`
    })
    markers.push(marker)
  })
  
  map.add(markers)
  
  // 调整视图以包含所有标记
  if (markers.length > 0) {
    map.setFitView(markers)
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
    
    // 添加起点和终点标记
    const startMarker = new window.AMap.Marker({
      position: path[0],
      title: '起点',
      icon: 'https://webapi.amap.com/theme/v1.3/markers/n/start.png'
    })
    
    const endMarker = new window.AMap.Marker({
      position: path[path.length - 1],
      title: '终点',
      icon: 'https://webapi.amap.com/theme/v1.3/markers/n/end.png'
    })
    
    map.add([startMarker, endMarker])
  })
  
  // 调整视图
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

// 地图控制
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

// 地图风格切换
const changeMapStyle = () => {
  if (map) {
    const newStyle = getMapStyleUrl()
    map.setMapStyle(newStyle)
    console.log('地图风格已切换为:', queryParams.value.mapStyle, newStyle)
  }
}

onMounted(() => {
  console.log('📊 交通数据总览页面已加载')
  
  // 设置默认值为数据集范围内的时间（优化后的4小时范围）
  queryParams.value.startTime = "2013-09-13T08:00"
  queryParams.value.endTime = "2013-09-13T12:00"
  
  // 初始化地图
  initMap()
  
  // 加载高德地图API
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
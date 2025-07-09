<template>
  <div class="p-6">
    <div class="max-w-7xl mx-auto">
      <!-- 功能标签页 -->
      <div class="mb-6">
        <div class="border-b border-slate-200">
          <nav class="-mb-px flex space-x-8">
            <button
              @click="activeTab = 'detection'"
              :class="[
                'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'detection'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300',
              ]"
            >
              <Camera class="h-4 w-4 mr-2 inline" />
              实时检测
            </button>
            <button
              @click="activeTab = 'history'"
              :class="[
                'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'history'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300',
              ]"
            >
              <Clock class="h-4 w-4 mr-2 inline" />
              检测历史
            </button>
            <button
              @click="activeTab = 'statistics'"
              :class="[
                'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'statistics'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300',
              ]"
            >
              <BarChart3 class="h-4 w-4 mr-2 inline" />
              统计分析
            </button>
          </nav>
        </div>
      </div>

      <!-- 实时检测标签页 -->
      <div v-show="activeTab === 'detection'">
        <!-- 页面标题 -->
        <div class="mb-8">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-slate-800 flex items-center">
                <Camera class="h-6 w-6 mr-3 text-blue-600" />
                智能识别路面病害，提供精准检测与分析
              </h1>
              <div class="flex items-center mt-2 text-sm text-slate-600">
                <Clock class="h-4 w-4 mr-1" />
                {{ currentTime }}
              </div>
            </div>
          </div>
        </div>

        <!-- 告警面板 -->
        <div v-if="alarms.length > 0" class="mb-6">
          <div class="bg-red-50 border border-red-200 rounded-lg p-4 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <AlertTriangle class="h-5 w-5 text-red-500 mr-2" />
                <h3 class="text-red-800 font-medium">
                  系统告警 ({{ alarms.length }})
                </h3>
              </div>
              <button
                @click="dismissAlarms"
                class="text-red-600 hover:text-red-800 text-sm"
              >
                全部清除
              </button>
            </div>
            <div class="mt-3 space-y-2">
              <div
                v-for="alarm in alarms"
                :key="alarm.id"
                class="flex items-center justify-between p-2 bg-white rounded border-l-4 border-red-400"
              >
                <div class="flex-1">
                  <div class="text-red-800 font-medium">
                    {{ alarm.message }}
                  </div>
                  <div class="text-red-600 text-sm">
                    严重程度: {{ alarm.level }} | {{ alarm.time }}
                  </div>
                </div>
                <button
                  @click="dismissAlarm(alarm.id)"
                  class="text-red-400 hover:text-red-600"
                >
                  <X class="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- 左侧：上传和检测区域 -->
          <div class="lg:col-span-2 space-y-6">
            <!-- 文件上传区域 -->
            <div
              class="bg-white rounded-lg shadow-md border border-slate-200 p-6"
            >
              <h2
                class="text-xl font-semibold mb-4 flex items-center text-slate-800"
              >
                <Upload class="h-5 w-5 mr-2 text-blue-600" />
                图像上传
                <span class="ml-auto text-sm text-slate-500"
                  >支持 JPG, PNG, MP4 (最大50MB)</span
                >
              </h2>

              <div
                @drop="handleDrop"
                @dragover.prevent
                @dragenter.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                class="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center hover:border-blue-400 transition-all duration-200"
                :class="{ 'border-blue-400 bg-blue-50 scale-105': isDragging }"
              >
                <div v-if="!selectedFile">
                  <ImageIcon class="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <p class="text-slate-600 mb-2">拖拽图片到此处或点击上传</p>
                  <input
                    type="file"
                    ref="fileInput"
                    @change="handleFileSelect"
                    accept="image/*,video/*"
                    class="hidden"
                  />
                  <button
                    @click="$refs.fileInput.click()"
                    class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors shadow-sm font-medium"
                  >
                    选择文件
                  </button>
                </div>

                <div v-else class="space-y-4">
                  <div class="relative inline-block">
                    <!-- 图片预览 -->
                    <img
                      v-if="
                        selectedFile.type.startsWith('image/') && previewUrl
                      "
                      :src="previewUrl"
                      alt="预览图片"
                      class="max-h-64 mx-auto rounded-lg shadow-md"
                    />
                    <!-- 视频预览 -->
                    <video
                      v-else-if="
                        selectedFile.type.startsWith('video/') && previewUrl
                      "
                      :src="previewUrl"
                      controls
                      class="max-h-64 mx-auto rounded-lg shadow-md"
                    >
                      您的浏览器不支持视频播放
                    </video>
                    <div class="absolute top-2 right-2">
                      <button
                        @click="clearFile"
                        class="bg-red-500 text-white p-1 rounded-full hover:bg-red-600 shadow-lg"
                      >
                        <X class="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  <div class="bg-slate-50 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-3">
                      <div class="flex items-center">
                        <component
                          :is="
                            selectedFile.type.startsWith('video/')
                              ? 'Video'
                              : 'FileImage'
                          "
                          class="h-5 w-5 text-slate-500 mr-2"
                        />
                        <span class="text-slate-700 font-medium">{{
                          selectedFile.name
                        }}</span>
                      </div>
                      <div class="text-right">
                        <span class="text-sm text-slate-500">{{
                          formatFileSize(selectedFile.size)
                        }}</span>
                        <div class="text-xs text-slate-400">
                          {{
                            selectedFile.type.startsWith("video/")
                              ? "视频文件"
                              : "图片文件"
                          }}
                        </div>
                      </div>
                    </div>

                    <button
                      @click="detectDamage"
                      :disabled="isDetecting"
                      class="w-full bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm font-medium"
                    >
                      <div
                        v-if="isDetecting"
                        class="flex items-center justify-center"
                      >
                        <Loader2 class="h-5 w-5 mr-2 animate-spin" />
                        检测中... ({{ detectionProgress }}%)
                      </div>
                      <div v-else class="flex items-center justify-center">
                        <Search class="h-5 w-5 mr-2" />
                        开始检测
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 检测结果展示 -->
            <div
              v-if="detectionResult"
              class="bg-white rounded-lg shadow-md border border-slate-200 p-6"
            >
              <div class="flex items-center justify-between mb-4">
                <h2
                  class="text-xl font-semibold flex items-center text-slate-800"
                >
                  <Eye class="h-5 w-5 mr-2 text-green-600" />
                  检测结果
                  <span
                    v-if="detectionResult.isVideo"
                    class="ml-2 text-sm bg-purple-100 text-purple-800 px-2 py-1 rounded-full"
                  >
                    视频 ({{ detectionResult.totalFrames }} 帧)
                  </span>
                </h2>
                <div class="flex space-x-2">
                  <button
                    v-if="detectionResult.isVideo"
                    @click="playFrameSequence"
                    class="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
                  >
                    <Play class="h-4 w-4 mr-1 inline" />
                    播放序列
                  </button>
                  <button
                    @click="exportResult"
                    class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    <Download class="h-4 w-4 mr-1 inline" />
                    导出结果
                  </button>
                  <button
                    @click="shareResult"
                    class="bg-slate-600 text-white px-4 py-2 rounded-lg hover:bg-slate-700 transition-colors text-sm font-medium"
                  >
                    <Share2 class="h-4 w-4 mr-1 inline" />
                    分享
                  </button>
                </div>
              </div>

              <!-- 视频时间轴 (仅视频显示) -->
              <div v-if="detectionResult.isVideo" class="mb-6">
                <h3 class="font-medium mb-3 flex items-center text-slate-700">
                  <Clock class="h-4 w-4 mr-2" />
                  视频时间轴 (总时长: {{ detectionResult.duration }}s)
                </h3>
                <div class="bg-slate-100 rounded-lg p-4">
                  <!-- 时间轴进度条 -->
                  <div class="relative h-8 bg-slate-200 rounded-full mb-4">
                    <div
                      v-for="(frame, index) in detectionResult.frames"
                      :key="frame.frameIndex"
                      class="absolute top-0 h-8 cursor-pointer transition-all duration-200 hover:scale-110"
                      :style="{
                        left:
                          (frame.timestamp / detectionResult.duration) * 100 +
                          '%',
                        width: '8px',
                        marginLeft: '-4px',
                      }"
                      @click="switchToFrame(index)"
                    >
                      <div
                        class="w-2 h-8 rounded-full shadow-md"
                        :class="[
                          index === currentFrameIndex
                            ? 'bg-blue-600'
                            : frame.damages.length > 0
                            ? 'bg-red-500'
                            : 'bg-green-500',
                        ]"
                      ></div>
                      <div
                        class="absolute top-10 left-1/2 transform -translate-x-1/2 text-xs text-slate-600 whitespace-nowrap"
                      >
                        {{ frame.timestamp }}s
                      </div>
                    </div>

                    <!-- 当前播放位置指示器 -->
                    <div
                      class="absolute top-0 w-1 h-8 bg-blue-700 rounded-full shadow-lg transition-all duration-300"
                      :style="{
                        left:
                          (currentFrame?.timestamp / detectionResult.duration) *
                            100 +
                          '%',
                        marginLeft: '-2px',
                      }"
                    ></div>
                  </div>

                  <!-- 帧信息卡片 -->
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div
                      v-for="(frame, index) in detectionResult.frames"
                      :key="frame.frameIndex"
                      class="p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:shadow-md"
                      :class="[
                        index === currentFrameIndex
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-slate-200 bg-white',
                      ]"
                      @click="switchToFrame(index)"
                    >
                      <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-slate-700"
                          >帧 {{ frame.frameIndex + 1 }}</span
                        >
                        <span class="text-xs text-slate-500"
                          >{{ frame.timestamp }}s</span
                        >
                      </div>
                      <div class="text-xs text-slate-600">
                        检测到 {{ frame.damages.length }} 处病害
                      </div>
                      <div class="flex space-x-1 mt-2">
                        <div
                          v-for="damage in frame.damages.slice(0, 3)"
                          :key="damage.id"
                          class="w-2 h-2 rounded-full"
                          :class="getDamageBgStyle(damage.type)"
                        ></div>
                        <span
                          v-if="frame.damages.length > 3"
                          class="text-xs text-slate-400"
                        >
                          +{{ frame.damages.length - 3 }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 快速统计卡片 -->
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div
                  class="bg-blue-50 p-4 rounded-lg text-center border border-blue-100"
                >
                  <div class="text-2xl font-bold text-blue-700">
                    {{ detectionResult.totalCount }}
                  </div>
                  <div class="text-sm text-slate-600">
                    {{ detectionResult.isVideo ? "总病害数" : "检测到病害" }}
                  </div>
                </div>
                <div
                  class="bg-red-50 p-4 rounded-lg text-center border border-red-100"
                >
                  <div class="text-2xl font-bold text-red-600">
                    {{ detectionResult.totalArea.toFixed(2) }}
                  </div>
                  <div class="text-sm text-slate-600">总面积(m²)</div>
                </div>
                <div
                  class="bg-yellow-50 p-4 rounded-lg text-center border border-yellow-100"
                >
                  <div class="text-2xl font-bold text-yellow-600">
                    {{ averageConfidence }}%
                  </div>
                  <div class="text-sm text-slate-600">平均置信度</div>
                </div>
                <div
                  class="bg-green-50 p-4 rounded-lg text-center border border-green-100"
                >
                  <div class="text-2xl font-bold text-green-600">
                    {{
                      detectionResult.isVideo
                        ? detectionResult.totalFrames
                        : detectionTime + "s"
                    }}
                  </div>
                  <div class="text-sm text-slate-600">
                    {{ detectionResult.isVideo ? "检测帧数" : "检测用时" }}
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- 结果图像/当前帧 -->
                <div>
                  <h3 class="font-medium mb-3 text-slate-700">
                    {{
                      detectionResult.isVideo
                        ? `当前帧 (${currentFrame?.timestamp}s)`
                        : "标注结果"
                    }}
                  </h3>
                  <div class="relative bg-slate-100 rounded-lg overflow-hidden">
                    <img
                      :src="
                        detectionResult.isVideo
                          ? currentFrame?.imageUrl
                          : detectionResult.imageUrl
                      "
                      alt="检测结果"
                      class="w-full rounded-lg"
                    />
                    <!-- 病害标注叠加 -->
                    <div
                      v-for="damage in detectionResult.isVideo
                        ? frameDamages
                        : detectionResult.damages"
                      :key="damage.id"
                      class="absolute border-2 bg-opacity-20 cursor-pointer hover:bg-opacity-40 transition-all"
                      :class="getDamageStyle(damage.type)"
                      :style="{
                        left: damage.bbox.x + 'px',
                        top: damage.bbox.y + 'px',
                        width: damage.bbox.width + 'px',
                        height: damage.bbox.height + 'px',
                      }"
                      @click="selectDamage(damage)"
                    >
                      <div
                        class="text-white text-xs px-2 py-1 rounded shadow-lg font-medium"
                        :class="getDamageBgStyle(damage.type)"
                      >
                        {{ damage.type }} ({{
                          (damage.confidence * 100).toFixed(1)
                        }}%)
                      </div>
                    </div>
                  </div>

                  <!-- 视频帧导航 -->
                  <div
                    v-if="detectionResult.isVideo"
                    class="flex justify-center mt-4 space-x-2"
                  >
                    <button
                      @click="switchToFrame(Math.max(0, currentFrameIndex - 1))"
                      :disabled="currentFrameIndex === 0"
                      class="px-3 py-1 bg-slate-200 rounded hover:bg-slate-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronLeft class="h-4 w-4" />
                    </button>
                    <span
                      class="px-4 py-1 bg-blue-100 text-blue-800 rounded font-medium"
                    >
                      {{ currentFrameIndex + 1 }} /
                      {{ detectionResult.totalFrames }}
                    </span>
                    <button
                      @click="
                        switchToFrame(
                          Math.min(
                            detectionResult.totalFrames - 1,
                            currentFrameIndex + 1
                          )
                        )
                      "
                      :disabled="
                        currentFrameIndex === detectionResult.totalFrames - 1
                      "
                      class="px-3 py-1 bg-slate-200 rounded hover:bg-slate-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronRight class="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <!-- 检测详情 -->
                <div class="space-y-4">
                  <div class="bg-slate-50 rounded-lg p-4">
                    <h3 class="font-medium mb-3 text-slate-700">
                      {{ detectionResult.isVideo ? "整体摘要" : "检测摘要" }}
                    </h3>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                      <div class="flex justify-between">
                        <span class="text-slate-600">
                          {{
                            detectionResult.isVideo ? "总病害:" : "病害数量:"
                          }}
                        </span>
                        <span class="font-medium text-slate-800">{{
                          detectionResult.totalCount
                        }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-slate-600">总面积:</span>
                        <span class="font-medium text-slate-800"
                          >{{ detectionResult.totalArea.toFixed(2) }}m²</span
                        >
                      </div>
                      <div class="flex justify-between">
                        <span class="text-slate-600">严重病害:</span>
                        <span class="font-medium text-red-600">{{
                          severeDamageCount
                        }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-slate-600">
                          {{
                            detectionResult.isVideo ? "问题帧数:" : "建议处理:"
                          }}
                        </span>
                        <span class="font-medium text-yellow-600">
                          {{
                            detectionResult.isVideo
                              ? detectionResult.frames.filter(
                                  (f) => f.damages.length > 0
                                ).length
                              : recommendedActions
                          }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div class="space-y-2">
                    <div class="flex items-center justify-between">
                      <h3 class="font-medium text-slate-700">
                        {{
                          detectionResult.isVideo ? "当前帧病害" : "病害详情"
                        }}
                      </h3>
                      <select
                        v-model="damageFilter"
                        class="text-sm border border-slate-300 rounded px-2 py-1 bg-white"
                      >
                        <option value="all">全部类型</option>
                        <option value="裂缝">裂缝</option>
                        <option value="坑洞">坑洞</option>
                        <option value="破损">破损</option>
                        <option value="其他">其他</option>
                      </select>
                    </div>

                    <div
                      class="max-h-64 overflow-y-auto space-y-2 custom-scrollbar"
                    >
                      <div
                        v-for="damage in detectionResult.isVideo
                          ? frameDamages.filter(
                              (d) =>
                                damageFilter === 'all' ||
                                d.type === damageFilter
                            )
                          : filteredDamages"
                        :key="damage.id"
                        class="flex items-center justify-between p-3 rounded-lg border cursor-pointer hover:bg-slate-50 transition-colors"
                        :class="{
                          'bg-blue-50 border-blue-200':
                            selectedDamage?.id === damage.id,
                        }"
                        @click="selectDamage(damage)"
                      >
                        <div class="flex items-center">
                          <div
                            class="w-3 h-3 rounded-full mr-3"
                            :class="getDamageBgStyle(damage.type)"
                          ></div>
                          <div>
                            <div class="font-medium text-slate-800">
                              {{ damage.type }}
                            </div>
                            <div class="text-slate-600 text-sm">
                              置信度:
                              {{ (damage.confidence * 100).toFixed(1) }}%
                            </div>
                          </div>
                        </div>
                        <div class="text-right">
                          <div class="font-medium text-slate-800">
                            {{ damage.area.toFixed(2) }}m²
                          </div>
                          <div
                            class="text-sm px-2 py-1 rounded-full"
                            :class="getSeverityStyle(damage.severity)"
                          >
                            {{ getSeverityText(damage.severity) }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧：实时统计 -->
          <div class="space-y-6">
            <!-- 实时统计 -->
            <div
              class="bg-white rounded-lg shadow-md border border-slate-200 p-6"
            >
              <h2
                class="text-xl font-semibold mb-4 flex items-center text-slate-800"
              >
                <BarChart3 class="h-5 w-5 mr-2 text-purple-600" />
                实时统计
              </h2>

              <div class="space-y-4">
                <div class="grid grid-cols-1 gap-4">
                  <div
                    class="text-center p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200"
                  >
                    <div class="text-3xl font-bold text-blue-700">
                      {{ stats.todayDetections }}
                    </div>
                    <div class="text-sm text-slate-600">今日检测</div>
                    <div class="text-xs text-slate-500 mt-1">
                      比昨日 {{ stats.todayGrowth > 0 ? "+" : ""
                      }}{{ stats.todayGrowth }}%
                    </div>
                  </div>
                  <div
                    class="text-center p-4 bg-gradient-to-r from-red-50 to-red-100 rounded-lg border border-red-200"
                  >
                    <div class="text-3xl font-bold text-red-600">
                      {{ stats.totalDamages }}
                    </div>
                    <div class="text-sm text-slate-600">发现病害</div>
                    <div class="text-xs text-slate-500 mt-1">
                      严重: {{ stats.severeDamages }} | 中等:
                      {{ stats.moderateDamages }}
                    </div>
                  </div>
                </div>

                <!-- 病害类型分布 -->
                <div>
                  <h3 class="font-medium mb-3 text-slate-700">病害类型分布</h3>
                  <div class="space-y-3">
                    <div
                      v-for="type in stats.damageTypes"
                      :key="type.name"
                      class="space-y-1"
                    >
                      <div class="flex items-center justify-between text-sm">
                        <span class="flex items-center">
                          <div
                            class="w-3 h-3 rounded-full mr-2"
                            :style="{ backgroundColor: type.color }"
                          ></div>
                          <span class="text-slate-700">{{ type.name }}</span>
                        </span>
                        <span class="font-medium text-slate-800">{{
                          type.count
                        }}</span>
                      </div>
                      <div class="w-full bg-slate-200 rounded-full h-2">
                        <div
                          class="h-2 rounded-full transition-all duration-500"
                          :style="{
                            width:
                              (type.count / stats.totalDamages) * 100 + '%',
                            backgroundColor: type.color,
                          }"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 操作日志 -->
            <div
              class="bg-white rounded-lg shadow-md border border-slate-200 p-6"
            >
              <div class="flex items-center justify-between mb-4">
                <h2
                  class="text-xl font-semibold flex items-center text-slate-800"
                >
                  <FileText class="h-5 w-5 mr-2 text-green-600" />
                  操作日志
                </h2>
                <button
                  @click="refreshLogs"
                  class="text-slate-500 hover:text-slate-700"
                  :disabled="isRefreshingLogs"
                >
                  <RotateCcw
                    class="h-4 w-4"
                    :class="{ 'animate-spin': isRefreshingLogs }"
                  />
                </button>
              </div>

              <div class="max-h-80 overflow-y-auto space-y-2 custom-scrollbar">
                <div
                  v-for="log in logs"
                  :key="log.id"
                  class="flex items-start justify-between p-3 hover:bg-slate-50 rounded-lg transition-colors border-l-4"
                  :class="getLogBorderStyle(log.type)"
                >
                  <div class="flex-1">
                    <div class="flex items-center">
                      <component
                        :is="getLogIcon(log.type)"
                        class="h-4 w-4 mr-2"
                        :class="getLogIconStyle(log.type)"
                      />
                      <div class="font-medium text-sm text-slate-800">
                        {{ log.action }}
                      </div>
                    </div>
                    <div class="text-slate-600 text-xs mt-1">
                      操作人: {{ log.operator }}
                      <span v-if="log.result" class="ml-2"
                        >| {{ log.result }}</span
                      >
                    </div>
                  </div>
                  <div class="text-slate-500 text-xs whitespace-nowrap ml-2">
                    {{ formatTime(log.timestamp) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 检测历史标签页 -->
      <div v-show="activeTab === 'history'">
        <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
          <h2 class="text-2xl font-bold mb-6 text-slate-800">检测历史记录</h2>

          <!-- 搜索和筛选 -->
          <div class="flex flex-col md:flex-row gap-4 mb-6">
            <div class="flex-1">
              <input
                type="text"
                placeholder="搜索文件名或检测结果..."
                class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                v-model="searchQuery"
              />
            </div>
            <select
              class="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent md:w-48"
              v-model="filterType"
            >
              <option value="all">全部类型</option>
              <option value="image">图片检测</option>
              <option value="video">视频检测</option>
            </select>
          </div>

          <!-- 历史记录列表 -->
          <div class="space-y-4">
            <div
              v-for="record in filteredHistory"
              :key="record.id"
              class="border border-slate-200 rounded-lg p-4 hover:bg-slate-50 transition-colors"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3">
                    <div
                      class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center"
                    >
                      <component
                        :is="record.type === 'video' ? 'Video' : 'FileImage'"
                        class="h-6 w-6 text-blue-600"
                      />
                    </div>
                    <div>
                      <h3 class="font-medium text-slate-800">
                        {{ record.filename }}
                      </h3>
                      <p class="text-sm text-slate-600">
                        检测时间: {{ formatDate(record.timestamp) }}
                      </p>
                    </div>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-lg font-bold text-blue-600">
                    {{ record.damageCount }}
                  </div>
                  <div class="text-sm text-slate-600">检测到病害</div>
                </div>
              </div>

              <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span class="text-slate-600">总面积:</span>
                  <span class="font-medium ml-1 text-slate-800"
                    >{{ record.totalArea }}m²</span
                  >
                </div>
                <div>
                  <span class="text-slate-600">平均置信度:</span>
                  <span class="font-medium ml-1 text-slate-800"
                    >{{ record.confidence }}%</span
                  >
                </div>
                <div>
                  <span class="text-slate-600">严重病害:</span>
                  <span class="font-medium ml-1 text-red-600">{{
                    record.severeDamages
                  }}</span>
                </div>
                <div>
                  <span class="text-slate-600">检测用时:</span>
                  <span class="font-medium ml-1 text-slate-800"
                    >{{ record.detectionTime }}s</span
                  >
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="filteredHistory.length === 0" class="text-center py-12">
            <div class="text-slate-400 mb-4">
              <FileText class="h-16 w-16 mx-auto" />
            </div>
            <h3 class="text-lg font-medium text-slate-900 mb-2">
              暂无检测记录
            </h3>
            <p class="text-slate-600 mb-4">开始您的第一次路面病害检测</p>
            <button
              @click="activeTab = 'detection'"
              class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              立即开始检测
            </button>
          </div>
        </div>
      </div>

      <!-- 统计分析标签页 -->
      <div v-show="activeTab === 'statistics'">
        <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
          <h2
            class="text-xl font-semibold mb-6 flex items-center text-slate-800"
          >
            <TrendingUp class="h-5 w-5 mr-2 text-indigo-600" />
            趋势分析
          </h2>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- 时间趋势图 -->
            <div>
              <h3 class="font-medium mb-3 text-slate-700">
                病害检测趋势 (近7天)
              </h3>
              <div
                class="h-64 bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg flex items-center justify-center border-2 border-dashed border-slate-300"
              >
                <div class="text-center">
                  <TrendingUp class="h-12 w-12 text-slate-400 mx-auto mb-2" />
                  <div class="text-slate-500 font-medium">趋势图表区域</div>
                  <div class="text-slate-400 text-sm mt-1">
                    集成 Chart.js 或 ECharts
                  </div>
                </div>
              </div>
            </div>

            <!-- 类型分布饼图 -->
            <div>
              <h3 class="font-medium mb-3 text-slate-700">病害类型分布</h3>
              <div
                class="h-64 bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg flex items-center justify-center border-2 border-dashed border-slate-300"
              >
                <div class="text-center">
                  <PieChart class="h-12 w-12 text-slate-400 mx-auto mb-2" />
                  <div class="text-slate-500 font-medium">饼图区域</div>
                  <div class="text-slate-400 text-sm mt-1">可视化类型分布</div>
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
import { ref, onMounted, computed } from "vue";
import {
  Upload,
  Search,
  Eye,
  BarChart3,
  FileText,
  TrendingUp,
  AlertTriangle,
  Loader2,
  X,
  ImageIcon,
  Camera,
  Clock,
  Download,
  Share2,
  FileImage,
  RotateCcw,
  PieChart,
  Video,
  Play,
  ChevronLeft,
  ChevronRight,
} from "lucide-vue-next";

export default {
  name: "RoadDamageDetection",
  components: {
    Upload,
    Search,
    Eye,
    BarChart3,
    FileText,
    TrendingUp,
    AlertTriangle,
    Loader2,
    X,
    ImageIcon,
    Camera,
    Clock,
    Download,
    Share2,
    FileImage,
    RotateCcw,
    PieChart,
    Video,
    Play,
    ChevronLeft,
    ChevronRight,
  },
  setup() {
    // 响应式数据
    const activeTab = ref("detection");
    const selectedFile = ref(null);
    const previewUrl = ref("");
    const isDragging = ref(false);
    const isDetecting = ref(false);
    const detectionProgress = ref(0);
    const detectionTime = ref(0);
    const detectionResult = ref(null);
    const selectedDamage = ref(null);
    const damageFilter = ref("all");
    const alarms = ref([]);
    const stats = ref({
      todayDetections: 0,
      totalDamages: 0,
      todayGrowth: 0,
      severeDamages: 0,
      moderateDamages: 0,
      damageTypes: [],
    });
    const logs = ref([]);
    const fileInput = ref(null);
    const currentTime = ref("");
    const isRefreshingLogs = ref(false);
    const currentFrameIndex = ref(0);

    // 历史记录相关
    const searchQuery = ref("");
    const filterType = ref("all");
    const historyRecords = ref([]);

    // API 基础URL
    const API_BASE = "/api";

    // 计算属性
    const averageConfidence = computed(() => {
      if (!detectionResult.value?.damages?.length) return 0;
      const total = detectionResult.value.damages.reduce(
        (sum, d) => sum + d.confidence,
        0
      );
      return Math.round((total / detectionResult.value.damages.length) * 100);
    });

    const severeDamageCount = computed(() => {
      if (!detectionResult.value?.damages?.length) return 0;
      return detectionResult.value.damages.filter((d) => d.severity === "high")
        .length;
    });

    const recommendedActions = computed(() => {
      if (!detectionResult.value?.damages?.length) return 0;
      return detectionResult.value.damages.filter(
        (d) => d.severity === "high" || d.severity === "medium"
      ).length;
    });

    const filteredDamages = computed(() => {
      if (!detectionResult.value?.damages?.length) return [];
      if (damageFilter.value === "all") return detectionResult.value.damages;
      return detectionResult.value.damages.filter(
        (d) => d.type === damageFilter.value
      );
    });

    const currentFrame = computed(() => {
      if (!detectionResult.value?.isVideo) return null;
      return detectionResult.value.frames[currentFrameIndex.value];
    });

    const frameDamages = computed(() => {
      const frame = currentFrame.value;
      return frame ? frame.damages : [];
    });

    const filteredHistory = computed(() => {
      let filtered = historyRecords.value;

      if (filterType.value !== "all") {
        filtered = filtered.filter(
          (record) => record.type === filterType.value
        );
      }

      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter((record) =>
          record.filename.toLowerCase().includes(query)
        );
      }

      return filtered;
    });

    // 时间更新
    const updateTime = () => {
      currentTime.value = new Date().toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    };

    // 文件处理
    const handleFileSelect = (event) => {
      const file = event.target.files[0];
      if (file) {
        selectedFile.value = file;
        previewUrl.value = URL.createObjectURL(file);
        detectionResult.value = null;
      }
    };

    const handleDrop = (event) => {
      event.preventDefault();
      isDragging.value = false;
      const file = event.dataTransfer.files[0];
      if (
        file &&
        (file.type.startsWith("image/") || file.type.startsWith("video/"))
      ) {
        selectedFile.value = file;
        previewUrl.value = URL.createObjectURL(file);
        detectionResult.value = null;
      }
    };

    const clearFile = () => {
      selectedFile.value = null;
      previewUrl.value = "";
      detectionResult.value = null;
      selectedDamage.value = null;
      if (fileInput.value) {
        fileInput.value.value = "";
      }
    };

    const formatFileSize = (bytes) => {
      if (bytes === 0) return "0 Bytes";
      const k = 1024;
      const sizes = ["Bytes", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    };

    const formatDate = (timestamp) => {
      return new Date(timestamp).toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    // 上传文件
    /* eslint-disable no-unused-vars */
    const uploadImage = async (file) => {
      const formData = new FormData();
      formData.append("image", file);

      try {
        const response = await fetch(`${API_BASE}/upload/image`, {
          method: "POST",
          body: formData,
        });
        return await response.json();
      } catch (error) {
        console.error("上传失败:", error);
        throw error;
      }
    };
    /* eslint-disable no-unused-vars */
    // 检测病害
    const detectDamage = async () => {
      if (!selectedFile.value) return;

      isDetecting.value = true;
      detectionProgress.value = 0;
      const startTime = Date.now();

      const progressInterval = setInterval(() => {
        if (detectionProgress.value < 90) {
          detectionProgress.value += Math.random() * 15;
        }
      }, 200);

      try {
        detectionProgress.value = 20;
        // const uploadResult = await uploadImage(selectedFile.value)

        detectionProgress.value = 40;
        // 模拟API调用
        await new Promise((resolve) => setTimeout(resolve, 1000));

        detectionProgress.value = 70;
        await new Promise((resolve) => setTimeout(resolve, 500));
        detectionProgress.value = 100;

        if (selectedFile.value.type.startsWith("video/")) {
          const mockVideoFrames = [
            {
              frameIndex: 0,
              timestamp: 0.5,
              imageUrl: previewUrl.value,
              damages: [
                {
                  id: 1,
                  type: "裂缝",
                  bbox: { x: 50, y: 80, width: 120, height: 40 },
                  area: 2.5,
                  confidence: 0.92,
                  severity: "high",
                },
              ],
            },
            {
              frameIndex: 1,
              timestamp: 2.3,
              imageUrl: previewUrl.value,
              damages: [
                {
                  id: 2,
                  type: "坑洞",
                  bbox: { x: 200, y: 150, width: 80, height: 60 },
                  area: 1.8,
                  confidence: 0.87,
                  severity: "medium",
                },
                {
                  id: 3,
                  type: "破损",
                  bbox: { x: 300, y: 100, width: 100, height: 50 },
                  area: 3.2,
                  confidence: 0.78,
                  severity: "low",
                },
              ],
            },
            {
              frameIndex: 2,
              timestamp: 4.1,
              imageUrl: previewUrl.value,
              damages: [
                {
                  id: 4,
                  type: "裂缝",
                  bbox: { x: 100, y: 200, width: 150, height: 30 },
                  area: 1.9,
                  confidence: 0.85,
                  severity: "medium",
                },
              ],
            },
          ];

          const allDamages = mockVideoFrames.flatMap((frame) => frame.damages);

          detectionResult.value = {
            isVideo: true,
            duration: 5.2,
            totalFrames: mockVideoFrames.length,
            frames: mockVideoFrames,
            totalCount: allDamages.length,
            totalArea: allDamages.reduce((sum, d) => sum + d.area, 0),
            damages: allDamages,
          };

          currentFrameIndex.value = 0;
        } else {
          const mockDamages = [
            {
              id: 1,
              type: "裂缝",
              bbox: { x: 50, y: 80, width: 120, height: 40 },
              area: 2.5,
              confidence: 0.92,
              severity: "high",
            },
            {
              id: 2,
              type: "坑洞",
              bbox: { x: 200, y: 150, width: 80, height: 60 },
              area: 1.8,
              confidence: 0.87,
              severity: "medium",
            },
            {
              id: 3,
              type: "破损",
              bbox: { x: 300, y: 100, width: 100, height: 50 },
              area: 3.2,
              confidence: 0.78,
              severity: "low",
            },
          ];

          detectionResult.value = {
            isVideo: false,
            imageUrl: previewUrl.value,
            totalCount: mockDamages.length,
            totalArea: mockDamages.reduce((sum, d) => sum + d.area, 0),
            damages: mockDamages,
          };
        }

        detectionTime.value = ((Date.now() - startTime) / 1000).toFixed(1);

        // 添加到历史记录
        const newRecord = {
          id: Date.now(),
          filename: selectedFile.value.name,
          type: selectedFile.value.type.startsWith("video/")
            ? "video"
            : "image",
          timestamp: new Date(),
          damageCount: detectionResult.value.totalCount,
          totalArea: detectionResult.value.totalArea.toFixed(1),
          confidence: averageConfidence.value,
          severeDamages: severeDamageCount.value,
          detectionTime: detectionTime.value,
        };
        historyRecords.value.unshift(newRecord);

        await fetchStats();
        await fetchLogs();

        logs.value.unshift({
          id: Date.now(),
          action: "完成病害检测",
          operator: "系统",
          timestamp: new Date(),
          type: "detection",
          result: `检测到 ${detectionResult.value.totalCount} 处病害`,
        });
      } catch (error) {
        console.error("检测失败:", error);
        alert("检测失败，请重试");
      } finally {
        clearInterval(progressInterval);
        isDetecting.value = false;
        detectionProgress.value = 0;
      }
    };

    const switchToFrame = (frameIndex) => {
      currentFrameIndex.value = frameIndex;
    };

    const playFrameSequence = () => {
      if (!detectionResult.value?.isVideo) return;

      let index = 0;
      const interval = setInterval(() => {
        currentFrameIndex.value = index;
        index++;
        if (index >= detectionResult.value.frames.length) {
          clearInterval(interval);
          currentFrameIndex.value = 0;
        }
      }, 1000);
    };

    const selectDamage = (damage) => {
      selectedDamage.value = damage;
    };

    const exportResult = () => {
      const data = {
        timestamp: new Date().toISOString(),
        filename: selectedFile.value?.name,
        results: detectionResult.value,
      };

      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `detection_result_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    };

    const shareResult = () => {
      if (navigator.share) {
        navigator.share({
          title: "路面病害检测结果",
          text: `检测到 ${
            detectionResult.value.totalCount
          } 处病害，总面积 ${detectionResult.value.totalArea.toFixed(2)}m²`,
          url: window.location.href,
        });
      } else {
        const text = `路面病害检测结果：检测到 ${
          detectionResult.value.totalCount
        } 处病害，总面积 ${detectionResult.value.totalArea.toFixed(2)}m²`;
        navigator.clipboard.writeText(text).then(() => {
          alert("结果已复制到剪贴板");
        });
      }
    };

    const dismissAlarm = (alarmId) => {
      alarms.value = alarms.value.filter((a) => a.id !== alarmId);
    };

    const dismissAlarms = () => {
      alarms.value = [];
    };

    const fetchAlarms = async () => {
      try {
        const response = await fetch(`${API_BASE}/alarm`);
        const data = await response.json();
        alarms.value = data.alarms || [];
      } catch (error) {
        console.error("获取告警数据失败:", error);
        alarms.value = [
          {
            id: 1,
            message: "检测到严重路面病害，建议立即处理",
            level: "high",
            time: "2分钟前",
          },
        ];
      }
    };

    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_BASE}/trend`);
        const data = await response.json();
        stats.value = {
          todayDetections: data.todayDetections || 23,
          totalDamages: data.totalDamages || 45,
          todayGrowth: data.todayGrowth || 12,
          severeDamages: data.severeDamages || 8,
          moderateDamages: data.moderateDamages || 15,
          damageTypes: data.damageTypes || [
            { name: "裂缝", count: 18, color: "#ef4444" },
            { name: "坑洞", count: 12, color: "#f97316" },
            { name: "破损", count: 10, color: "#eab308" },
            { name: "其他", count: 5, color: "#6b7280" },
          ],
        };
      } catch (error) {
        console.error("获取统计数据失败:", error);
        stats.value = {
          todayDetections: 23,
          totalDamages: 45,
          todayGrowth: 12,
          severeDamages: 8,
          moderateDamages: 15,
          damageTypes: [
            { name: "裂缝", count: 18, color: "#ef4444" },
            { name: "坑洞", count: 12, color: "#f97316" },
            { name: "破损", count: 10, color: "#eab308" },
            { name: "其他", count: 5, color: "#6b7280" },
            { name: "破损", count: 10, color: "#eab308" },
            { name: "其他", count: 5, color: "#6b7280" },
          ],
        };
      }
    };

    const fetchLogs = async () => {
      try {
        const response = await fetch(`${API_BASE}/logs`);
        const data = await response.json();
        logs.value = data.logs || [];
      } catch (error) {
        console.error("获取日志失败:", error);
        if (logs.value.length === 0) {
          logs.value = [
            {
              id: 1,
              action: "系统启动",
              operator: "系统",
              timestamp: new Date(Date.now() - 3600000),
              type: "system",
            },
            {
              id: 2,
              action: "用户登录",
              operator: "管理员",
              timestamp: new Date(Date.now() - 1800000),
              type: "auth",
            },
            {
              id: 3,
              action: "上传图像文件",
              operator: "用户",
              timestamp: new Date(Date.now() - 900000),
              type: "upload",
            },
          ];
        }
      }
    };

    const refreshLogs = async () => {
      isRefreshingLogs.value = true;
      await fetchLogs();
      setTimeout(() => {
        isRefreshingLogs.value = false;
      }, 1000);
    };

    const loadHistory = () => {
      // 模拟历史数据
      if (historyRecords.value.length === 0) {
        historyRecords.value = [
          {
            id: 1,
            filename: "road_damage_001.jpg",
            type: "image",
            timestamp: new Date(Date.now() - 3600000),
            damageCount: 5,
            totalArea: 12.5,
            confidence: 92,
            severeDamages: 2,
            detectionTime: 2.3,
          },
          {
            id: 2,
            filename: "highway_inspection.mp4",
            type: "video",
            timestamp: new Date(Date.now() - 7200000),
            damageCount: 15,
            totalArea: 45.8,
            confidence: 88,
            severeDamages: 6,
            detectionTime: 15.7,
          },
          {
            id: 3,
            filename: "street_check_002.jpg",
            type: "image",
            timestamp: new Date(Date.now() - 86400000),
            damageCount: 3,
            totalArea: 8.2,
            confidence: 95,
            severeDamages: 1,
            detectionTime: 1.8,
          },
        ];
      }
    };

    const getDamageStyle = (type) => {
      const styles = {
        裂缝: "border-red-500 bg-red-500",
        坑洞: "border-orange-500 bg-orange-500",
        破损: "border-yellow-500 bg-yellow-500",
        其他: "border-slate-500 bg-slate-500",
      };
      return styles[type] || "border-slate-500 bg-slate-500";
    };

    const getDamageBgStyle = (type) => {
      const styles = {
        裂缝: "bg-red-500",
        坑洞: "bg-orange-500",
        破损: "bg-yellow-500",
        其他: "bg-slate-500",
      };
      return styles[type] || "bg-slate-500";
    };

    const getSeverityStyle = (severity) => {
      const styles = {
        high: "bg-red-100 text-red-800",
        medium: "bg-yellow-100 text-yellow-800",
        low: "bg-green-100 text-green-800",
      };
      return styles[severity] || "bg-slate-100 text-slate-800";
    };

    const getSeverityText = (severity) => {
      const texts = {
        high: "严重",
        medium: "中等",
        low: "轻微",
      };
      return texts[severity] || severity;
    };

    const getLogBorderStyle = (type) => {
      const styles = {
        detection: "border-blue-400",
        upload: "border-green-400",
        system: "border-purple-400",
        auth: "border-indigo-400",
      };
      return styles[type] || "border-slate-400";
    };

    const getLogIcon = (type) => {
      const icons = {
        detection: Search,
        upload: Upload,
        system: BarChart3,
        auth: Eye,
      };
      return icons[type] || FileText;
    };

    const getLogIconStyle = (type) => {
      const styles = {
        detection: "text-blue-500",
        upload: "text-green-500",
        system: "text-purple-500",
        auth: "text-indigo-500",
      };
      return styles[type] || "text-slate-500";
    };

    const formatTime = (timestamp) => {
      const now = new Date();
      const time = new Date(timestamp);
      const diff = now - time;

      if (diff < 60000) return "刚刚";
      if (diff < 3600000) return Math.floor(diff / 60000) + "分钟前";
      if (diff < 86400000) return Math.floor(diff / 3600000) + "小时前";

      return time.toLocaleString("zh-CN", {
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    onMounted(() => {
      updateTime();
      setInterval(updateTime, 1000);

      fetchAlarms();
      fetchStats();
      fetchLogs();
      loadHistory();

      setInterval(fetchAlarms, 30000);
    });

    return {
      activeTab,
      selectedFile,
      previewUrl,
      isDragging,
      isDetecting,
      detectionProgress,
      detectionTime,
      detectionResult,
      selectedDamage,
      damageFilter,
      alarms,
      stats,
      logs,
      fileInput,
      currentTime,
      isRefreshingLogs,
      currentFrameIndex,
      searchQuery,
      filterType,
      filteredHistory,
      averageConfidence,
      severeDamageCount,
      recommendedActions,
      filteredDamages,
      currentFrame,
      frameDamages,
      handleFileSelect,
      handleDrop,
      clearFile,
      formatFileSize,
      formatDate,
      detectDamage,
      switchToFrame,
      playFrameSequence,
      selectDamage,
      exportResult,
      shareResult,
      dismissAlarm,
      dismissAlarms,
      refreshLogs,
      getDamageStyle,
      getDamageBgStyle,
      getSeverityStyle,
      getSeverityText,
      getLogBorderStyle,
      getLogIcon,
      getLogIconStyle,
      formatTime,
    };
  },
};
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.transition-all {
  transition: all 0.3s ease;
}

@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }

  .lg\:col-span-2 {
    grid-column: span 1;
  }
}
</style>

<template>
  <div class="space-y-6 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 p-6">
    <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <TrendingUp class="h-8 w-8 text-blue-400 mr-3" />
          <div>
            <h2 class="text-2xl font-bold text-white">数据分析中心</h2>
            <p class="text-blue-200">深度分析交通数据趋势</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="text-center text-blue-200 py-8">
      <div class="inline-flex items-center">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        正在加载数据...
      </div>
    </div>

    <div v-if="errorMessage" class="bg-red-500/20 border border-red-500/30 text-red-400 rounded-xl p-4 mb-6">
      <div class="flex items-center">
        <svg class="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <span>{{ errorMessage }}</span>
      </div>
      <div class="mt-2 text-sm text-red-300">
        <p>请检查：</p>
        <ul class="list-disc list-inside mt-1">
          <li>选择的日期是否在 2013年9月12日 至 2013年9月18日 范围内</li>
          <li>网络连接是否正常</li>
          <li>后端服务是否运行正常</li>
        </ul>
      </div>
    </div>

    <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-4 border border-blue-500/30">
      <div class="flex justify-center space-x-2">
        <button 
          v-for="period in timePeriods" 
          :key="period.key"
          @click="handlePeriodChange(period.key)"
          :class="[
            'px-4 py-2 rounded-lg transition-all',
            selectedPeriod === period.key 
              ? 'bg-gradient-to-r from-blue-500 to-sky-500 text-white shadow-lg' 
              : 'bg-blue-700/30 text-blue-200 hover:bg-blue-600/40 hover:text-white'
          ]"
        >
          {{ period.label }}
        </button>
      </div>
    </div>

    <div v-if="selectedPeriod === 'today'" class="bg-blue-800/40 backdrop-blur-md rounded-xl p-4 border border-blue-500/30">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-white">选择日期</h3>
        <div class="text-right">
          <span class="text-blue-200 text-sm">当前选择: {{ formatDateDisplay(selectedDate) }}</span>
          <div class="text-xs text-blue-300 mt-1">
            数据范围: 2013年9月12日 - 9月18日
          </div>
        </div>
      </div>
      <div class="grid grid-cols-4 md:grid-cols-7 gap-2 max-h-32 overflow-y-auto">
        <button 
          v-for="date in availableDates" 
          :key="date"
          @click="handleDateChange(date)"
          :class="[
            'px-3 py-2 rounded-lg text-sm transition-all relative',
            selectedDate === date 
              ? 'bg-gradient-to-r from-blue-500 to-sky-500 text-white shadow-lg' 
              : 'bg-blue-700/30 text-blue-200 hover:bg-blue-600/40 hover:text-white'
          ]"
          :title="`${formatDateDisplay(date)} (${date})`"
        >
          {{ formatDateDisplay(date) }}
          <div class="text-xs opacity-75 mt-1">
            {{ date.split('-')[2] }}日
          </div>
        </button>
      </div>
      <div class="mt-3 text-xs text-blue-300">
        提示: 数据集仅包含2013年9月12日至18日的交通数据
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div 
        v-for="metric in displayMetrics" 
        :key="metric.title"
        class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-blue-200 text-sm">{{ metric.title }}</p>
            <p class="text-2xl font-bold text-white">{{ metric.value }}</p>
          </div>
          <component :is="metric.icon" :class="['h-8 w-8', metric.color]" />
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30">
      <h3 class="text-lg font-semibold text-white mb-4">流量趋势图</h3>
      <div v-if="shouldShowNoData" class="h-64 flex items-center justify-center text-blue-300">
        <div class="text-center">
          <svg class="h-16 w-16 mx-auto mb-4 text-blue-400/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p class="text-lg font-medium">暂无数据</p>
          <p class="text-sm text-blue-400 mt-1">
            {{ selectedPeriod === 'today' ? 
                `${formatDateDisplay(selectedDate)} 暂无流量数据` : 
                `从 ${formatDateDisplay(selectedDate)} 开始的一周暂无数据` 
            }}
          </p>
          <button @click="fetchData" 
                  class="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors">
            重新加载
          </button>
        </div>
      </div>
      <div v-else class="relative h-64">
        <canvas ref="chartCanvas" class="w-full h-full"></canvas>
      </div>
    </div>

    <div class="bg-blue-800/40 backdrop-blur-md rounded-xl p-6 border border-blue-500/30">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-white">高峰时段分析</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div v-for="period in timePeriodStats" :key="period.name" class="bg-blue-700/30 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-white font-medium">{{ period.name }}</h4>
            <span :class="['px-2 py-1 rounded text-xs', period.statusClass]">{{ period.status }}</span>
          </div>
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-blue-200">时间段:</span>
              <span class="text-white">{{ period.timeRange }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-blue-200">平均车流:</span>
              <span class="text-white">{{ period.avgVehicles }} 辆/小时</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-blue-200">平均速度:</span>
              <span class="text-white">{{ period.avgSpeed }} km/h</span>
            </div>
            <div class="w-full bg-blue-900/50 rounded-full h-2 mt-3">
              <div 
                class="h-full rounded-full bg-gradient-to-r from-blue-500 to-sky-400" 
                :style="{ width: `${(period.avgVehicles / 2000) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { Chart } from 'chart.js/auto';
import { TrendingUp, Car, Clock, Users } from 'lucide-vue-next';
import axios from 'axios';

// 响应式数据
const selectedPeriod = ref('today');
const selectedDate = ref('2013-09-12');
const chartCanvas = ref(null);
const isLoading = ref(false);
const errorMessage = ref('');

// 时间周期选项
const timePeriods = [
  { key: 'today', label: '今日' },
  { key: 'week', label: '本周' }
];

// 可选择的日期
const availableDates = computed(() => {
  return [
    '2013-09-12', '2013-09-13', '2013-09-14', '2013-09-15',
    '2013-09-16', '2013-09-17', '2013-09-18'
  ];
});

// 原始关键指标数据
const keyMetrics = ref([
  { title: '总流量', value: '0', icon: Car, color: 'text-blue-400' },
  { title: '平均速度', value: '0.0km/h', icon: TrendingUp, color: 'text-sky-400' },
  { title: '高峰时长', value: '0.0h', icon: Clock, color: 'text-indigo-400' },
  { title: '活跃用户', value: '0', icon: Users, color: 'text-purple-400' }
]);

// 🔧 计算属性：根据时间周期调整指标显示
const displayMetrics = computed(() => {
  return keyMetrics.value.map(metric => {
    if (metric.title === '总流量' && selectedPeriod.value === 'week') {
      // 每周界面显示"平均每日流量"
      return {
        ...metric,
        title: '平均每日流量'
      };
    }
    return metric;
  });
});

// 流量数据
const trafficData = ref([]);
const timePeriodStats = ref([]);

// 图表实例
let chartInstance = null;

// 计算属性
const timeLabels = computed(() => {
  if (selectedPeriod.value === 'today') {
    return Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`);
  } else {
    return ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  }
});

// 无数据状态判断
const shouldShowNoData = computed(() => {
  return !trafficData.value || trafficData.value.length === 0 || 
         trafficData.value.every(val => val === 0 || val === null || val === undefined);
});

// 图表更新函数
const updateChart = async () => {
  if (!chartCanvas.value) {
    console.warn('图表canvas未找到');
    return;
  }

  // 等待DOM更新
  await nextTick();

  const ctx = chartCanvas.value.getContext('2d');
  const data = trafficData.value.map(val => val ?? 0);
  const labels = timeLabels.value;

  console.log('更新图表:', { data, labels, period: selectedPeriod.value });

  // 销毁旧图表
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }

  // 创建新图表
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: selectedPeriod.value === 'today' ? '每小时流量' : '每日流量',
        data: data,
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#ffffff' }
        },
        tooltip: {
          callbacks: {
            label: (context) => `${context.dataset.label}: ${context.parsed.y.toLocaleString()} 辆`
          }
        }
      },
      scales: {
        x: {
          title: { 
            display: true, 
            text: selectedPeriod.value === 'today' ? '时间 (小时)' : '日期', 
            color: '#ffffff' 
          },
          ticks: { color: '#ffffff' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        },
        y: {
          title: { 
            display: true, 
            text: '流量 (辆)', 
            color: '#ffffff' 
          },
          ticks: { 
            color: '#ffffff',
            callback: (value) => value.toLocaleString()
          },
          grid: { color: 'rgba(255, 255, 255, 0.1)' },
          beginAtZero: true
        }
      }
    }
  });
};

// 处理函数
const handlePeriodChange = async (period) => {
  console.log('切换时间周期:', period);
  selectedPeriod.value = period;
  await fetchData();
};

const handleDateChange = async (date) => {
  console.log('切换日期:', date);
  selectedDate.value = date;
  await fetchData();
};

const formatDateDisplay = (dateStr) => {
  const date = new Date(dateStr);
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
};

// 🚀 修复后的数据获取函数
const fetchData = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  console.log('=== 开始获取数据 ===');
  console.log('参数:', {
    period: selectedPeriod.value,
    date: selectedDate.value
  });

  try {
    // 🔧 修复：统一API参数格式
    const commonParams = {
      date: selectedDate.value,
      period: selectedPeriod.value
    };

    // 获取流量数据
    if (selectedPeriod.value === 'today') {
      const response = await axios.get('/api/traffic/daily', {
        params: { date: selectedDate.value }
      });
      console.log('每日数据响应:', response.data);

      if (response.data.success) {
        trafficData.value = response.data.data?.length === 24 
          ? response.data.data.map(val => val ?? 0)
          : new Array(24).fill(0);
      } else {
        errorMessage.value = response.data.message || '每日流量数据加载失败';
        trafficData.value = new Array(24).fill(0);
      }
    } else {
      const response = await axios.get('/api/traffic/weekly', {
        params: { start_date: selectedDate.value }
      });
      console.log('每周数据响应:', response.data);

      if (response.data.success) {
        trafficData.value = response.data.data?.length === 7
          ? response.data.data.map(item => item.totalVehicles ?? 0)
          : new Array(7).fill(0);
      } else {
        errorMessage.value = response.data.message || '每周流量数据加载失败';
        trafficData.value = new Array(7).fill(0);
      }
    }

    // 🔧 修复：获取关键指标 - 使用正确的参数
    try {
      console.log('🔍 获取关键指标，参数:', commonParams);
      const metricsResponse = await axios.get('/api/traffic/metrics', { 
        params: commonParams 
      });
      console.log('📊 关键指标响应:', metricsResponse.data);
      
      if (metricsResponse.data.success) {
        keyMetrics.value = metricsResponse.data.data.map(metric => ({
          ...metric,
          icon: metric.title === '总流量' ? Car :
                metric.title === '平均速度' ? TrendingUp :
                metric.title === '高峰时长' ? Clock : Users,
          color: metric.title === '总流量' ? 'text-blue-400' :
                 metric.title === '平均速度' ? 'text-sky-400' :
                 metric.title === '高峰时长' ? 'text-indigo-400' : 'text-purple-400'
        }));
        console.log('✅ 关键指标更新成功:', keyMetrics.value);
      } else {
        console.warn('⚠️ 关键指标获取失败:', metricsResponse.data.message);
      }
    } catch (error) {
      console.error('❌ 关键指标获取失败:', error);
      // 显示具体的错误信息
      if (error.response) {
        console.error('错误响应:', error.response.data);
      }
    }

    // 获取时间段统计
    try {
      const periodsResponse = await axios.get('/api/traffic/periods', { 
        params: commonParams 
      });
      if (periodsResponse.data.success) {
        timePeriodStats.value = periodsResponse.data.data ?? [];
      }
    } catch (error) {
      console.warn('时间段统计获取失败:', error);
    }

    console.log('=== 数据获取完成 ===');
    console.log('流量数据:', trafficData.value);

    // 数据加载完成后更新图表
    await nextTick();
    if (!shouldShowNoData.value) {
      updateChart();
    }

  } catch (error) {
    console.error('数据获取错误:', error);
    errorMessage.value = `数据加载失败: ${error.message || '未知错误'}`;
    trafficData.value = selectedPeriod.value === 'today' ? new Array(24).fill(0) : new Array(7).fill(0);
  } finally {
    isLoading.value = false;
  }
};

// 初始化
onMounted(async () => {
  console.log('组件挂载，初始化数据');
  await fetchData();
});
</script>

<style scoped>
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.space-y-6 > * {
  animation: fadeInUp 0.6s ease-out;
}

.overflow-x-auto {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
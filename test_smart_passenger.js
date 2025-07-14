// 智能客流分析API测试脚本
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000/api';

async function testSmartPassengerAPI() {
  console.log('🧪 开始测试智能客流分析API...\n');

  try {
    // 测试1: 天气影响分析
    console.log('1️⃣ 测试天气影响分析API...');
    const weatherResponse = await axios.post(`${API_BASE_URL}/smart-passenger/weather-impact`, {
      include_prediction: false,
      correlation_threshold: 0.3,
      time_window: '7d'
    });
    
    if (weatherResponse.data.success) {
      console.log('✅ 天气影响分析成功');
      console.log(`   - 天气记录数: ${weatherResponse.data.weather_stats?.total_weather_records || 0}`);
      console.log(`   - 影响分析数: ${weatherResponse.data.weather_impact_analysis?.length || 0}`);
    } else {
      console.log('❌ 天气影响分析失败:', weatherResponse.data.message);
    }

    // 测试2: 出租车需求分析
    console.log('\n2️⃣ 测试出租车需求分析API...');
    const taxiResponse = await axios.post(`${API_BASE_URL}/smart-passenger/taxi-demand`, {
      historical_analysis: true,
      include_prediction: false,
      hotspot_analysis: true,
      time_window: '1h'
    });
    
    if (taxiResponse.data.success) {
      console.log('✅ 出租车需求分析成功');
      console.log(`   - 供需分析数: ${taxiResponse.data.supply_demand_analysis?.length || 0}`);
      console.log(`   - 热点区域数: ${taxiResponse.data.hotspot_visualization?.hotspots?.length || 0}`);
    } else {
      console.log('❌ 出租车需求分析失败:', taxiResponse.data.message);
    }

    // 测试3: 历史分析数据
    console.log('\n3️⃣ 测试历史分析API...');
    const historicalResponse = await axios.get(`${API_BASE_URL}/api/smart-passenger/historical`);
    
    if (historicalResponse.data.success) {
      console.log('✅ 历史分析数据获取成功');
      const data = historicalResponse.data.historical_data;
      console.log(`   - 活跃乘客: ${data.passenger_stats?.active_passengers || 0}`);
      console.log(`   - 载客车辆: ${data.taxi_stats?.loaded_taxis || 0}`);
      console.log(`   - 需求指数: ${(data.taxi_stats?.avg_demand_index || 0).toFixed(3)}`);
    } else {
      console.log('❌ 历史分析数据获取失败:', historicalResponse.data.message);
    }

    // 测试4: 综合智能客运分析
    console.log('\n4️⃣ 测试综合智能客运分析API...');
    const comprehensiveResponse = await axios.post(`${API_BASE_URL}/smart-passenger/analysis`, {
      analysis_type: 'comprehensive',
      include_weather: true,
      include_taxi_analysis: true,
      min_passenger_threshold: 1,
      weather_correlation: true,
      time_resolution: 15
    });
    
    if (comprehensiveResponse.data.success) {
      console.log('✅ 综合智能客运分析成功');
      console.log(`   - 处理时间: ${comprehensiveResponse.data.processing_time?.toFixed(2)}秒`);
      console.log(`   - 分析类型: ${comprehensiveResponse.data.analysis_type}`);
    } else {
      console.log('❌ 综合智能客运分析失败:', comprehensiveResponse.data.message);
    }

    console.log('\n🎉 所有API测试完成！');

  } catch (error) {
    console.error('❌ API测试失败:', error.message);
    if (error.response) {
      console.error('   响应状态:', error.response.status);
      console.error('   响应数据:', error.response.data);
    }
  }
}

// 运行测试
testSmartPassengerAPI(); 
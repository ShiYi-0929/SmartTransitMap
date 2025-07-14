/**
 * 订单速度分析API测试脚本
 * 在浏览器控制台中运行此脚本来测试API功能
 * 
 * 使用方法：
 * 1. 打开浏览器开发者工具
 * 2. 进入Console标签
 * 3. 复制并粘贴此脚本
 * 4. 运行 testSpeedAnalysis() 函数
 */

// 测试配置
const TEST_CONFIG = {
    baseURL: 'http://localhost:8082',
    apiPath: '/api/traffic/road/order-speed-analysis',
    timeout: 30000,
    defaultConfig: {
        include_short_medium_only: true,
        spatial_resolution: 0.001,
        min_orders_per_location: 5,
        congestion_threshold: {
            free: 40,
            moderate: 25,
            heavy: 15,
            jam: 0
        }
    }
};

// 工具函数
function log(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const styles = {
        info: 'color: #17a2b8;',
        success: 'color: #28a745; font-weight: bold;',
        error: 'color: #dc3545; font-weight: bold;',
        warning: 'color: #ffc107; font-weight: bold;'
    };
    
    console.log(`%c[${timestamp}] ${message}`, styles[type] || styles.info);
}

// 创建axios实例（如果axios不存在，使用fetch）
function createHttpClient() {
    if (typeof axios !== 'undefined') {
        return axios.create({
            baseURL: TEST_CONFIG.baseURL,
            timeout: TEST_CONFIG.timeout,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    } else {
        // 使用fetch的简单包装
        return {
            post: async (url, data) => {
                const response = await fetch(TEST_CONFIG.baseURL + url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return {
                    status: response.status,
                    data: await response.json()
                };
            },
            get: async (url) => {
                const response = await fetch(TEST_CONFIG.baseURL + url);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return {
                    status: response.status,
                    data: await response.json()
                };
            }
        };
    }
}

// 测试后端连接
async function testConnection() {
    log('🔍 测试后端连接...');
    
    const client = createHttpClient();
    
    try {
        const response = await client.get('/api/traffic/summary');
        if (response.status === 200) {
            log('✅ 后端连接正常', 'success');
            return true;
        } else {
            log(`❌ 后端连接异常，状态码: ${response.status}`, 'error');
            return false;
        }
    } catch (error) {
        log(`❌ 后端连接失败: ${error.message}`, 'error');
        return false;
    }
}

// 测试订单速度分析API
async function testSpeedAnalysisAPI(config = TEST_CONFIG.defaultConfig) {
    log('🚀 开始测试订单速度分析API...');
    
    const client = createHttpClient();
    
    // 时间参数
    const startTime = 1378944000; // 2013-09-12 00:00:00 UTC
    const endTime = 1379548799;   // 2013-09-18 23:59:59 UTC
    
    const url = `${TEST_CONFIG.apiPath}?start_time=${startTime}&end_time=${endTime}`;
    
    log(`📋 请求配置:`);
    console.table(config);
    
    try {
        log('📤 发送请求...');
        const requestStart = Date.now();
        
        const response = await client.post(url, config);
        
        const requestEnd = Date.now();
        const duration = requestEnd - requestStart;
        
        log(`✅ 请求成功! 耗时: ${duration}ms`, 'success');
        log(`📊 响应状态: ${response.status}`, 'success');
        
        // 检查响应数据
        const data = response.data;
        
        if (data.success) {
            log(`✅ 分析成功: ${data.message}`, 'success');
            
            if (data.speed_analysis) {
                const analysis = data.speed_analysis;
                log('📈 分析结果统计:');
                console.log('  速度数据点:', analysis.speed_data?.length || 0);
                console.log('  热力图数据:', analysis.heatmap_data?.length || 0);
                console.log('  拥堵摘要:', Object.keys(analysis.congestion_summary || {}).length);
                
                // 显示部分数据样本
                if (analysis.speed_data && analysis.speed_data.length > 0) {
                    log('📍 速度数据样本:');
                    console.table(analysis.speed_data.slice(0, 5));
                }
                
                if (analysis.congestion_summary) {
                    log('🚦 拥堵摘要:');
                    console.log(analysis.congestion_summary);
                }
            }
            
            if (data.visualization_data) {
                log('📊 可视化数据:');
                console.log(data.visualization_data);
            }
            
            return true;
            
        } else {
            log(`❌ 分析失败: ${data.message}`, 'error');
            return false;
        }
        
    } catch (error) {
        log(`❌ API调用失败: ${error.message}`, 'error');
        
        if (error.response) {
            log(`HTTP错误: ${error.response.status}`, 'error');
            console.log('错误详情:', error.response.data);
        } else if (error.request) {
            log('网络错误: 请求未收到响应', 'error');
            console.log('请求详情:', error.request);
        } else {
            log('配置错误', 'error');
        }
        
        return false;
    }
}

// 测试不同配置
async function testDifferentConfigs() {
    log('🔄 测试不同配置参数...');
    
    const configs = [
        {
            name: '高精度短途',
            config: {
                include_short_medium_only: true,
                spatial_resolution: 0.001,
                min_orders_per_location: 3
            }
        },
        {
            name: '中等精度全部',
            config: {
                include_short_medium_only: false,
                spatial_resolution: 0.005,
                min_orders_per_location: 5
            }
        },
        {
            name: '低精度高阈值',
            config: {
                include_short_medium_only: true,
                spatial_resolution: 0.01,
                min_orders_per_location: 10
            }
        }
    ];
    
    const results = [];
    
    for (const testCase of configs) {
        log(`📋 测试配置: ${testCase.name}`);
        
        try {
            const result = await testSpeedAnalysisAPI(testCase.config);
            results.push({ name: testCase.name, success: result });
            
            if (result) {
                log(`✅ ${testCase.name} 测试通过`, 'success');
            } else {
                log(`❌ ${testCase.name} 测试失败`, 'error');
            }
            
        } catch (error) {
            log(`❌ ${testCase.name} 测试异常: ${error.message}`, 'error');
            results.push({ name: testCase.name, success: false });
        }
        
        // 添加延迟避免请求过快
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // 显示结果汇总
    log('📊 配置测试结果:');
    console.table(results);
    
    return results;
}

// 性能测试
async function performanceTest() {
    log('⚡ 开始性能测试...');
    
    const testCount = 3;
    const times = [];
    
    for (let i = 0; i < testCount; i++) {
        log(`🔄 执行第 ${i + 1} 次性能测试...`);
        
        try {
            const start = Date.now();
            const result = await testSpeedAnalysisAPI();
            const end = Date.now();
            
            const duration = end - start;
            times.push(duration);
            
            if (result) {
                log(`✅ 第 ${i + 1} 次: ${duration}ms`, 'success');
            } else {
                log(`❌ 第 ${i + 1} 次: ${duration}ms (失败)`, 'error');
            }
            
        } catch (error) {
            log(`❌ 第 ${i + 1} 次测试异常: ${error.message}`, 'error');
        }
        
        // 添加延迟
        if (i < testCount - 1) {
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }
    
    if (times.length > 0) {
        const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
        const minTime = Math.min(...times);
        const maxTime = Math.max(...times);
        
        log('📊 性能统计结果:');
        console.log(`  平均响应时间: ${avgTime.toFixed(2)}ms`);
        console.log(`  最快响应时间: ${minTime}ms`);
        console.log(`  最慢响应时间: ${maxTime}ms`);
        
        if (avgTime < 5000) {
            log('✅ 性能良好 (平均 < 5秒)', 'success');
        } else if (avgTime < 10000) {
            log('⚠️ 性能一般 (平均 5-10秒)', 'warning');
        } else {
            log('❌ 性能较差 (平均 > 10秒)', 'error');
        }
    }
    
    return times;
}

// 完整测试套件
async function runFullTest() {
    log('🚀 开始完整测试套件...');
    log('=' * 50);
    
    const testResults = [];
    
    // 测试列表
    const tests = [
        { name: '后端连接测试', func: testConnection },
        { name: '基础API测试', func: () => testSpeedAnalysisAPI() },
        { name: '不同配置测试', func: testDifferentConfigs },
        { name: '性能测试', func: performanceTest }
    ];
    
    for (const test of tests) {
        log(`\n📋 ${test.name}`);
        log('-'.repeat(30));
        
        try {
            const result = await test.func();
            testResults.push({ name: test.name, success: !!result });
            
            if (result) {
                log(`✅ ${test.name} 通过`, 'success');
            } else {
                log(`❌ ${test.name} 失败`, 'error');
            }
            
        } catch (error) {
            log(`❌ ${test.name} 异常: ${error.message}`, 'error');
            testResults.push({ name: test.name, success: false });
        }
        
        // 测试间隔
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // 显示总结
    log('\n' + '='.repeat(50));
    log('📊 测试结果总结');
    log('='.repeat(50));
    
    console.table(testResults);
    
    const passed = testResults.filter(r => r.success).length;
    const total = testResults.length;
    
    log(`\n📈 总计: ${passed}/${total} 个测试通过`);
    
    if (passed === total) {
        log('🎉 所有测试通过！', 'success');
    } else {
        log('⚠️ 部分测试失败，请检查问题', 'warning');
    }
    
    return testResults;
}

// 快速测试函数
async function quickTest() {
    log('⚡ 快速测试模式...');
    
    const connectionOk = await testConnection();
    if (!connectionOk) {
        log('❌ 后端连接失败，终止测试', 'error');
        return false;
    }
    
    const apiOk = await testSpeedAnalysisAPI();
    if (apiOk) {
        log('✅ 快速测试通过！', 'success');
    } else {
        log('❌ 快速测试失败', 'error');
    }
    
    return apiOk;
}

// 导出函数到全局作用域
window.testSpeedAnalysis = testSpeedAnalysisAPI;
window.testConnection = testConnection;
window.testDifferentConfigs = testDifferentConfigs;
window.performanceTest = performanceTest;
window.runFullTest = runFullTest;
window.quickTest = quickTest;

// 使用说明
log('📋 API测试脚本已加载！');
log('🔧 可用的测试函数:');
console.log('  - quickTest()           : 快速测试');
console.log('  - testConnection()      : 测试后端连接');
console.log('  - testSpeedAnalysis()   : 测试速度分析API');
console.log('  - testDifferentConfigs(): 测试不同配置');
console.log('  - performanceTest()     : 性能测试');
console.log('  - runFullTest()         : 完整测试套件');
log('💡 建议先运行 quickTest() 进行快速验证'); 
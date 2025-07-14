#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单速度分析功能测试脚本
测试后端API接口的各种情况
"""

import requests
import json
import time
import sys
from datetime import datetime

# 配置
BACKEND_URL = "http://localhost:8000"
API_BASE = f"{BACKEND_URL}/api/traffic"

def log(message, level="INFO"):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_backend_connection():
    """测试后端连接"""
    log("开始测试后端连接...")
    
    try:
        response = requests.get(f"{API_BASE}/summary", timeout=10)
        if response.status_code == 200:
            log("✅ 后端连接正常", "SUCCESS")
            return True
        else:
            log(f"❌ 后端连接异常，状态码: {response.status_code}", "ERROR")
            return False
    except requests.exceptions.RequestException as e:
        log(f"❌ 后端连接失败: {str(e)}", "ERROR")
        return False

def test_api_routes():
    """测试API路由"""
    log("开始测试API路由...")
    
    routes = [
        ("/summary", "GET", "交通概要"),
        ("/files/info", "GET", "文件信息"),
        ("/road/segments", "GET", "路段信息")
    ]
    
    results = []
    for route, method, name in routes:
        try:
            url = f"{API_BASE}{route}"
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, timeout=10)
            
            if response.status_code == 200:
                log(f"✅ {name} API 正常 ({route})", "SUCCESS")
                results.append(True)
            else:
                log(f"❌ {name} API 异常，状态码: {response.status_code}", "ERROR")
                results.append(False)
                
        except requests.exceptions.RequestException as e:
            log(f"❌ {name} API 失败: {str(e)}", "ERROR")
            results.append(False)
    
    return all(results)

def test_speed_analysis_api():
    """测试订单速度分析API"""
    log("开始测试订单速度分析API...")
    
    # 测试配置
    config = {
        "speed_analysis_type": "comprehensive",
        "include_short_medium_only": True,
        "spatial_resolution": 0.001,
        "min_orders_per_location": 5,
        "congestion_threshold": {
            "free": 40,
            "moderate": 25,
            "heavy": 15,
            "jam": 0
        }
    }
    
    # 时间参数
    start_time = 1378944000  # 2013-09-12 00:00:00 UTC
    end_time = 1379548799    # 2013-09-18 23:59:59 UTC
    
    url = f"{API_BASE}/road/order-speed-analysis"
    params = {
        "start_time": start_time,
        "end_time": end_time
    }
    
    try:
        log(f"请求URL: {url}")
        log(f"请求参数: {params}")
        log(f"请求配置: {json.dumps(config, indent=2)}")
        
        # 发送请求
        start_request = time.time()
        response = requests.post(url, params=params, json=config, timeout=60)
        end_request = time.time()
        
        log(f"请求耗时: {(end_request - start_request):.2f}秒")
        log(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            log("✅ 订单速度分析API调用成功", "SUCCESS")
            
            # 解析响应数据
            try:
                data = response.json()
                log("响应数据结构:")
                log(f"  - success: {data.get('success')}")
                log(f"  - message: {data.get('message')}")
                log(f"  - processing_time: {data.get('processing_time')}")
                
                if data.get('speed_analysis'):
                    analysis = data['speed_analysis']
                    log("速度分析结果:")
                    log(f"  - 速度数据点: {len(analysis.get('speed_data', []))}")
                    log(f"  - 热力图数据: {len(analysis.get('heatmap_data', []))}")
                    log(f"  - 拥堵摘要: {len(analysis.get('congestion_summary', {}))}")
                    
                    # 显示部分数据样本
                    if analysis.get('speed_data'):
                        log("速度数据样本:")
                        for i, data_point in enumerate(analysis['speed_data'][:3]):
                            log(f"  [{i+1}] 位置: {data_point.get('location')}, 速度: {data_point.get('avg_speed')}km/h")
                
                if data.get('visualization_data'):
                    viz_data = data['visualization_data']
                    log("可视化数据:")
                    for key, value in viz_data.items():
                        if isinstance(value, dict) and 'data' in value:
                            log(f"  - {key}: {len(value['data'])} 个数据点")
                        else:
                            log(f"  - {key}: {type(value)}")
                
                return True
                
            except json.JSONDecodeError as e:
                log(f"❌ 响应JSON解析失败: {str(e)}", "ERROR")
                log(f"响应内容: {response.text[:500]}...")
                return False
                
        else:
            log(f"❌ API调用失败，状态码: {response.status_code}", "ERROR")
            log(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        log("❌ 请求超时", "ERROR")
        return False
    except requests.exceptions.RequestException as e:
        log(f"❌ 请求异常: {str(e)}", "ERROR")
        return False

def test_different_configurations():
    """测试不同配置参数"""
    log("开始测试不同配置参数...")
    
    test_configs = [
        {
            "name": "高精度短途",
            "config": {
                "include_short_medium_only": True,
                "spatial_resolution": 0.001,
                "min_orders_per_location": 3
            }
        },
        {
            "name": "中等精度全部",
            "config": {
                "include_short_medium_only": False,
                "spatial_resolution": 0.005,
                "min_orders_per_location": 5
            }
        },
        {
            "name": "低精度高阈值",
            "config": {
                "include_short_medium_only": True,
                "spatial_resolution": 0.01,
                "min_orders_per_location": 10
            }
        }
    ]
    
    results = []
    for test_case in test_configs:
        log(f"测试配置: {test_case['name']}")
        
        url = f"{API_BASE}/road/order-speed-analysis"
        params = {
            "start_time": 1378944000,
            "end_time": 1379548799
        }
        
        try:
            start_time = time.time()
            response = requests.post(url, params=params, json=test_case['config'], timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    log(f"✅ {test_case['name']} 测试成功 ({(end_time - start_time):.2f}秒)", "SUCCESS")
                    results.append(True)
                else:
                    log(f"❌ {test_case['name']} 分析失败: {data.get('message')}", "ERROR")
                    results.append(False)
            else:
                log(f"❌ {test_case['name']} HTTP错误: {response.status_code}", "ERROR")
                results.append(False)
                
        except Exception as e:
            log(f"❌ {test_case['name']} 异常: {str(e)}", "ERROR")
            results.append(False)
    
    return all(results)

def test_error_handling():
    """测试错误处理"""
    log("开始测试错误处理...")
    
    error_tests = [
        {
            "name": "无效时间范围",
            "params": {"start_time": 0, "end_time": 0},
            "config": {}
        },
        {
            "name": "无效配置参数",
            "params": {"start_time": 1378944000, "end_time": 1379548799},
            "config": {"spatial_resolution": -1}
        },
        {
            "name": "空配置",
            "params": {"start_time": 1378944000, "end_time": 1379548799},
            "config": {}
        }
    ]
    
    results = []
    for test in error_tests:
        log(f"测试: {test['name']}")
        
        url = f"{API_BASE}/road/order-speed-analysis"
        
        try:
            response = requests.post(url, params=test['params'], json=test['config'], timeout=10)
            
            if response.status_code in [200, 400, 422]:
                log(f"✅ {test['name']} 错误处理正常 (状态码: {response.status_code})", "SUCCESS")
                results.append(True)
            else:
                log(f"❌ {test['name']} 意外状态码: {response.status_code}", "ERROR")
                results.append(False)
                
        except Exception as e:
            log(f"❌ {test['name']} 异常: {str(e)}", "ERROR")
            results.append(False)
    
    return all(results)

def performance_test():
    """性能测试"""
    log("开始性能测试...")
    
    config = {
        "include_short_medium_only": True,
        "spatial_resolution": 0.005,
        "min_orders_per_location": 5
    }
    
    url = f"{API_BASE}/road/order-speed-analysis"
    params = {
        "start_time": 1378944000,
        "end_time": 1379548799
    }
    
    times = []
    test_count = 3
    
    for i in range(test_count):
        try:
            log(f"执行第 {i+1} 次性能测试...")
            start_time = time.time()
            response = requests.post(url, params=params, json=config, timeout=60)
            end_time = time.time()
            
            duration = end_time - start_time
            times.append(duration)
            
            if response.status_code == 200:
                log(f"第 {i+1} 次: {duration:.2f}秒 ✅", "SUCCESS")
            else:
                log(f"第 {i+1} 次: {duration:.2f}秒 ❌ (状态码: {response.status_code})", "ERROR")
                
        except Exception as e:
            log(f"第 {i+1} 次测试失败: {str(e)}", "ERROR")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        log("📊 性能统计:")
        log(f"  平均响应时间: {avg_time:.2f}秒")
        log(f"  最快响应时间: {min_time:.2f}秒")
        log(f"  最慢响应时间: {max_time:.2f}秒")
        
        if avg_time < 10:
            log("✅ 性能良好 (平均 < 10秒)", "SUCCESS")
            return True
        elif avg_time < 30:
            log("⚠️ 性能一般 (平均 10-30秒)", "WARNING")
            return True
        else:
            log("❌ 性能较差 (平均 > 30秒)", "ERROR")
            return False
    
    return False

def main():
    """主测试函数"""
    log("🚀 开始订单速度分析功能测试")
    log("=" * 50)
    
    test_results = []
    
    # 测试列表
    tests = [
        ("后端连接测试", test_backend_connection),
        ("API路由测试", test_api_routes),
        ("订单速度分析API测试", test_speed_analysis_api),
        ("不同配置参数测试", test_different_configurations),
        ("错误处理测试", test_error_handling),
        ("性能测试", performance_test)
    ]
    
    for test_name, test_func in tests:
        log(f"\n📋 {test_name}")
        log("-" * 30)
        
        try:
            result = test_func()
            test_results.append((test_name, result))
            
            if result:
                log(f"✅ {test_name} 通过", "SUCCESS")
            else:
                log(f"❌ {test_name} 失败", "ERROR")
                
        except Exception as e:
            log(f"❌ {test_name} 异常: {str(e)}", "ERROR")
            test_results.append((test_name, False))
    
    # 总结报告
    log("\n" + "=" * 50)
    log("📊 测试结果总结")
    log("=" * 50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        log(f"{test_name}: {status}")
    
    log(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        log("🎉 所有测试通过！", "SUCCESS")
        return 0
    else:
        log("⚠️ 部分测试失败，请检查问题", "WARNING")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
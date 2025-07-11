#!/usr/bin/env python3
"""
API性能测试脚本
测试优化后的交通数据查询API性能
"""

import requests
import time
import json

# API配置
BASE_URL = "http://localhost:8000/api/traffic"
DEFAULT_PARAMS = {
    "start_time": 1379030400,  # 2013-09-13 08:00 UTC
    "end_time": 1379044800,    # 2013-09-13 12:00 UTC
}

def test_sample_vehicles():
    """测试示例车辆获取"""
    print("🚗 测试示例车辆获取...")
    
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/sample-vehicles", params=DEFAULT_PARAMS)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取示例车辆 ({duration:.2f}s)")
            print(f"   找到 {len(data.get('vehicles', []))} 个车辆")
            if data.get('vehicles'):
                # 显示前3个车辆
                for i, vehicle in enumerate(data['vehicles'][:3]):
                    print(f"   - {vehicle['vehicle_id']}: {vehicle['data_points']} 个数据点")
            return data.get('vehicles', [])
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return []

def test_track_query(vehicle_id, performance_mode='fast'):
    """测试轨迹查询"""
    print(f"📍 测试轨迹查询 - 车辆:{vehicle_id}, 模式:{performance_mode}")
    
    params = {
        **DEFAULT_PARAMS,
        "vehicle_id": vehicle_id,
        "performance_mode": performance_mode
    }
    
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/track", params=params)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                tracks = data.get('tracks', [])
                total_points = sum(len(track.get('points', [])) for track in tracks)
                print(f"✅ 轨迹查询成功 ({duration:.2f}s)")
                print(f"   {len(tracks)} 条轨迹，共 {total_points} 个点")
                
                if tracks:
                    track = tracks[0]
                    print(f"   距离: {track.get('distance', 0):.2f}km")
                    print(f"   时长: {track.get('duration', 0):.0f}s")
                
                return True
            else:
                print(f"❌ 查询失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_heatmap_query():
    """测试热力图查询"""
    print("🔥 测试热力图查询...")
    
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/heatmap", params=DEFAULT_PARAMS)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                points = data.get('data', [])
                print(f"✅ 热力图查询成功 ({duration:.2f}s)")
                print(f"   {len(points)} 个热力点")
                return True
            else:
                print(f"❌ 查询失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_cache_performance(vehicle_id):
    """测试缓存性能"""
    print("📦 测试缓存性能...")
    
    params = {
        **DEFAULT_PARAMS,
        "vehicle_id": vehicle_id,
        "performance_mode": "fast"
    }
    
    # 第一次查询
    print("   第一次查询（无缓存）...")
    start_time = time.time()
    response1 = requests.get(f"{BASE_URL}/track", params=params)
    duration1 = time.time() - start_time
    
    # 第二次查询（应该使用缓存）
    print("   第二次查询（使用缓存）...")
    start_time = time.time()
    response2 = requests.get(f"{BASE_URL}/track", params=params)
    duration2 = time.time() - start_time
    
    if response1.status_code == 200 and response2.status_code == 200:
        speedup = duration1 / duration2 if duration2 > 0 else 1
        print(f"✅ 缓存性能测试完成")
        print(f"   第一次: {duration1:.2f}s")
        print(f"   第二次: {duration2:.2f}s")
        print(f"   加速比: {speedup:.1f}x")
        return True
    else:
        print(f"❌ 缓存测试失败")
        return False

def main():
    """主测试函数"""
    print("🚀 开始API性能测试")
    print("=" * 50)
    
    # 1. 测试示例车辆获取
    vehicles = test_sample_vehicles()
    print()
    
    if not vehicles:
        print("❌ 无法获取示例车辆，停止测试")
        return
    
    # 选择第一个车辆进行测试
    test_vehicle = vehicles[0]['vehicle_id']
    print(f"📝 使用车辆 {test_vehicle} 进行后续测试")
    print()
    
    # 2. 测试不同性能模式的轨迹查询
    performance_modes = ['fast', 'medium', 'full']
    results = {}
    
    for mode in performance_modes:
        print(f"测试 {mode} 模式:")
        success = test_track_query(test_vehicle, mode)
        results[mode] = success
        print()
    
    # 3. 测试热力图查询
    test_heatmap_query()
    print()
    
    # 4. 测试缓存性能
    test_cache_performance(test_vehicle)
    print()
    
    # 5. 总结
    print("📊 测试总结:")
    print("=" * 50)
    print(f"✅ 示例车辆获取: {'成功' if vehicles else '失败'}")
    for mode, success in results.items():
        print(f"✅ {mode}模式轨迹查询: {'成功' if success else '失败'}")
    
    # 6. 性能建议
    print("\n💡 性能优化建议:")
    print("- 推荐使用 fast 模式进行日常查询")
    print("- 大时间范围查询时选择 medium 模式")
    print("- 只在需要完整数据分析时使用 full 模式")
    print("- 重复查询会自动使用缓存加速")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试traffic API的功能
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/traffic"

def test_traffic_summary():
    """测试数据概要接口"""
    print("=" * 50)
    print("测试数据概要接口")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/summary")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")

def test_files_info():
    """测试文件信息接口"""
    print("\n" + "=" * 50)
    print("测试文件信息接口")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/files/info")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")

def test_traffic_visualization():
    """测试可视化数据接口"""
    print("\n" + "=" * 50)
    print("测试可视化数据接口")
    print("=" * 50)
    
    # 使用真实数据的时间范围
    start_time = 1378915200  # 2013-09-11 16:00:00 UTC
    end_time = 1378918800    # 2013-09-11 17:00:00 UTC (1小时范围)
    
    params = {
        "start_time": start_time,
        "end_time": end_time,
        "view_type": "distribution",
        "limit": 100  # 限制返回100条记录用于测试
    }
    
    try:
        response = requests.get(f"{BASE_URL}/visualization", params=params)
        print(f"状态码: {response.status_code}")
        print(f"查询参数: {params}")
        print(f"时间范围: {datetime.fromtimestamp(start_time)} 到 {datetime.fromtimestamp(end_time)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"数据条数: {data.get('count')}")
            print(f"使用文件: {data.get('file_used')}")
            print(f"消息: {data.get('message')}")
            
            # 显示前几条数据示例
            if data.get('data') and len(data['data']) > 0:
                print("\n前3条数据示例:")
                for i, item in enumerate(data['data'][:3]):
                    print(f"  记录 {i+1}: 车辆={item.get('vehicle_id')}, "
                          f"坐标=({item.get('lat'):.6f}, {item.get('lng'):.6f}), "
                          f"速度={item.get('speed'):.1f}km/h, "
                          f"载客={item.get('is_occupied')}")
            else:
                print("无数据返回")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    print("🧪 开始测试Traffic API")
    print("请确保后端服务已启动在 http://localhost:8000")
    
    # 依次测试各个接口
    test_traffic_summary()
    test_files_info()
    test_traffic_visualization()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print("=" * 50)
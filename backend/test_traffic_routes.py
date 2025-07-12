#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试traffic路由是否正确注册
"""

import asyncio
from main import app

def test_routes():
    """检查注册的路由"""
    print("=" * 60)
    print("检查已注册的API路由")
    print("=" * 60)
    
    traffic_routes = []
    all_routes = []
    
    for route in app.routes:
        all_routes.append(route.path)
        if "/traffic" in route.path:
            traffic_routes.append(route.path)
    
    print(f"总路由数: {len(all_routes)}")
    print(f"Traffic相关路由数: {len(traffic_routes)}")
    
    print("\n所有路由:")
    for route in sorted(all_routes):
        print(f"  {route}")
    
    print(f"\nTraffic路由:")
    for route in sorted(traffic_routes):
        print(f"  ✅ {route}")
    
    # 检查我们需要的特定路由
    required_routes = [
        "/api/traffic/summary",
        "/api/traffic/files/info", 
        "/api/traffic/visualization"
    ]
    
    print(f"\n检查必需的路由:")
    missing_routes = []
    for required in required_routes:
        if required in all_routes:
            print(f"  ✅ {required}")
        else:
            print(f"  ❌ {required} - 缺失")
            missing_routes.append(required)
    
    if missing_routes:
        print(f"\n⚠️  缺失 {len(missing_routes)} 个必需路由")
        return False
    else:
        print(f"\n🎉 所有必需路由都已注册！")
        return True

async def test_traffic_api():
    """测试traffic API导入和功能"""
    print("\n" + "=" * 60)
    print("测试Traffic API导入")
    print("=" * 60)
    
    try:
        from app.api.traffic_simple import get_traffic_summary, get_data_files_info, get_traffic_visualization
        print("✅ Traffic API函数导入成功")
        
        # 测试数据目录
        import os
        data_dir = os.path.join(os.path.dirname(__file__), "detect", "traffic_visualization", "data", "cleaned")
        print(f"数据目录: {data_dir}")
        
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            print(f"✅ 找到 {len(files)} 个数据文件")
            for file in files:
                file_path = os.path.join(data_dir, file)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                print(f"  - {file}: {size_mb:.1f} MB")
        else:
            print(f"❌ 数据目录不存在: {data_dir}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Traffic API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 开始测试Traffic路由注册")
    
    success = True
    success &= test_routes()
    success &= asyncio.run(test_traffic_api())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过！")
        print("现在可以重启服务器:")
        print("  uvicorn main:app --reload")
        print("或者:")
        print("  python main.py")
    else:
        print("❌ 部分测试失败，请检查配置")
    print("=" * 60)
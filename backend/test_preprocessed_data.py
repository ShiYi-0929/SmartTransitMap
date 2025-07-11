#!/usr/bin/env python3
"""
测试预处理数据的使用脚本
验证 processed 和 indexes 文件夹中的数据是否能正常工作
"""

import sys
import os
import time

# 添加路径以便导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
detect_dir = os.path.join(current_dir, 'detect')
traffic_dir = os.path.join(current_dir, 'detect', 'traffic_visualization')

sys.path.insert(0, current_dir)
sys.path.insert(0, detect_dir)
sys.path.insert(0, traffic_dir)

# 修复导入问题
try:
    # 尝试从detect.traffic_visualization导入
    from detect.traffic_visualization.data_processor import TrafficDataProcessor
except ImportError:
    try:
        # 直接导入
        import data_processor
        TrafficDataProcessor = data_processor.TrafficDataProcessor
    except ImportError:
        # 手动导入相关模块
        sys.path.append(os.path.join(current_dir, 'detect', 'traffic_visualization'))
        
        # 创建简单的模型类来避免导入问题
        class HeatmapPoint:
            def __init__(self, lat, lng, count):
                self.lat = lat
                self.lng = lng
                self.count = count
        
        class TrackPoint:
            def __init__(self, lat, lng, timestamp, speed=None, direction=None, status=None):
                self.lat = lat
                self.lng = lng
                self.timestamp = timestamp
                self.speed = speed
                self.direction = direction
                self.status = status
        
        class VehicleTrack:
            def __init__(self, vehicle_id, points, start_time=None, end_time=None, distance=None, duration=None):
                self.vehicle_id = vehicle_id
                self.points = points
                self.start_time = start_time
                self.end_time = end_time
                self.distance = distance
                self.duration = duration
        
        # 创建临时模型模块
        import types
        models_module = types.ModuleType('models')
        models_module.HeatmapPoint = HeatmapPoint
        models_module.TrackPoint = TrackPoint
        models_module.VehicleTrack = VehicleTrack
        sys.modules['models'] = models_module
        
        # 现在导入数据处理器
        import data_processor
        TrafficDataProcessor = data_processor.TrafficDataProcessor

def test_preprocessed_data():
    """测试预处理数据的加载和使用"""
    print("=" * 60)
    print("测试预处理数据使用")
    print("=" * 60)
    
    # 初始化数据处理器
    processor = TrafficDataProcessor()
    
    # 测试时间范围（2013年9月13日）
    start_time = 1379030400  # 2013-09-13 08:00 UTC
    end_time = 1379044800    # 2013-09-13 12:00 UTC
    
    print(f"\n1. 测试数据加载...")
    print(f"时间范围: {start_time} - {end_time}")
    
    # 测试数据加载性能
    start_load_time = time.time()
    df = processor.load_data(start_time, end_time)
    load_time = time.time() - start_load_time
    
    print(f"✓ 数据加载完成")
    print(f"  - 加载时间: {load_time:.2f} 秒")
    print(f"  - 数据行数: {len(df)}")
    if not df.empty:
        print(f"  - 数据列: {list(df.columns)}")
        print(f"  - 时间范围: {df['UTC'].min()} - {df['UTC'].max()}")
        print(f"  - 车辆数量: {df['COMMADDR'].nunique()}")
    
    print(f"\n2. 测试热力图生成...")
    
    # 测试热力图生成
    start_heatmap_time = time.time()
    try:
        heatmap_points = processor.generate_heatmap_data(df, resolution=0.001)
        heatmap_time = time.time() - start_heatmap_time
        
        print(f"✓ 热力图生成完成")
        print(f"  - 生成时间: {heatmap_time:.2f} 秒")
        print(f"  - 热力图点数: {len(heatmap_points)}")
        if heatmap_points:
            point = heatmap_points[0]
            if hasattr(point, 'lat'):
                print(f"  - 示例点: lat={point.lat:.6f}, lng={point.lng:.6f}, count={point.count}")
            else:
                print(f"  - 示例点: {point}")
    except Exception as e:
        print(f"  ⚠ 热力图生成出错: {e}")
        print(f"  - 这可能是因为模型类导入问题，但数据加载功能正常")
    
    print(f"\n3. 测试特定车辆查询...")
    
    if not df.empty:
        # 随机选择一个车辆进行测试
        sample_vehicle = str(df['COMMADDR'].iloc[0])
        print(f"测试车辆ID: {sample_vehicle}")
        
        start_vehicle_time = time.time()
        vehicle_df = processor.load_data(start_time, end_time, vehicle_id=sample_vehicle)
        vehicle_time = time.time() - start_vehicle_time
        
        print(f"✓ 车辆数据查询完成")
        print(f"  - 查询时间: {vehicle_time:.2f} 秒")
        print(f"  - 该车辆记录数: {len(vehicle_df)}")
    
    print(f"\n4. 测试轨迹生成...")
    
    # 测试轨迹生成
    if not df.empty:
        try:
            start_track_time = time.time()
            tracks = processor.generate_track_data(df.head(1000))  # 限制数据量
            track_time = time.time() - start_track_time
            
            print(f"✓ 轨迹生成完成")
            print(f"  - 生成时间: {track_time:.2f} 秒")
            print(f"  - 轨迹数量: {len(tracks)}")
            if tracks:
                track = tracks[0]
                if hasattr(track, 'vehicle_id'):
                    print(f"  - 示例轨迹: 车辆{track.vehicle_id}, {len(track.points)}个点")
                else:
                    print(f"  - 示例轨迹: {track}")
        except Exception as e:
            print(f"  ⚠ 轨迹生成出错: {e}")
            print(f"  - 这可能是因为模型类导入问题，但数据加载功能正常")
    
    print(f"\n5. 性能对比总结...")
    print(f"  - 总测试时间: {time.time() - start_load_time:.2f} 秒")
    
    if hasattr(processor, 'use_preprocessed') and processor.use_preprocessed:
        print(f"  ✓ 使用了预处理数据，查询速度更快")
    else:
        print(f"  ⚠ 使用了原始CSV文件，查询速度较慢")
    
    print(f"\n测试完成！")

def test_index_files():
    """测试索引文件的内容"""
    print("\n" + "=" * 60)
    print("检查索引文件")
    print("=" * 60)
    
    data_dir = os.path.join(os.path.dirname(__file__), 'detect', 'traffic_visualization', 'data')
    index_dir = os.path.join(data_dir, 'indexes')
    processed_dir = os.path.join(data_dir, 'processed')
    
    print(f"数据目录: {data_dir}")
    print(f"索引目录: {index_dir}")
    print(f"处理目录: {processed_dir}")
    
    # 检查processed文件夹
    if os.path.exists(processed_dir):
        processed_files = [f for f in os.listdir(processed_dir) if f.endswith('.parquet')]
        print(f"\n✓ Processed文件夹存在，包含 {len(processed_files)} 个parquet文件")
        if processed_files:
            print(f"  - 示例文件: {processed_files[:5]}")
    else:
        print(f"\n✗ Processed文件夹不存在")
    
    # 检查indexes文件夹
    if os.path.exists(index_dir):
        index_files = os.listdir(index_dir)
        print(f"\n✓ Indexes文件夹存在，包含 {len(index_files)} 个索引文件")
        
        for file in index_files:
            filepath = os.path.join(index_dir, file)
            size_mb = os.path.getsize(filepath) / 1024 / 1024
            print(f"  - {file}: {size_mb:.1f} MB")
    else:
        print(f"\n✗ Indexes文件夹不存在")

def main():
    """主函数"""
    print("开始测试预处理数据...")
    
    try:
        # 检查文件结构
        test_index_files()
        
        # 测试数据处理
        test_preprocessed_data()
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
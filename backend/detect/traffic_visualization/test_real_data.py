 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于真实交通数据的路程分析和订单速度分析测试脚本
数据来源：济南市2013年9月12日-18日的出租车轨迹数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '../../../')
sys.path.insert(0, project_root)

try:
    from backend.detect.traffic_visualization.road_analysis_engine import RoadAnalysisEngine
    from backend.detect.traffic_visualization.models import TrafficData
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


class RealDataProcessor:
    """真实数据处理器"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.engine = RoadAnalysisEngine()
    
    def load_data_sample(self, filename, sample_size=10000):
        """
        加载数据样本（避免内存溢出）
        
        Args:
            filename: 数据文件名
            sample_size: 采样大小
        """
        filepath = os.path.join(self.data_dir, filename)
        print(f"正在从 {filepath} 加载 {sample_size} 条数据...")
        
        try:
            # 读取数据样本
            df = pd.read_csv(filepath, nrows=sample_size)
            print(f"成功加载 {len(df)} 条记录")
            
            # 数据预处理
            df = self.preprocess_data(df)
            return df
            
        except Exception as e:
            print(f"数据加载失败: {e}")
            return None
    
    def preprocess_data(self, df):
        """
        数据预处理
        """
        print("正在进行数据预处理...")
        
        # 1. 处理坐标数据（转换为正常的经纬度）
        df['lat'] = df['LAT'] / 1000000.0  # 纬度
        df['lon'] = df['LON'] / 1000000.0  # 经度
        
        # 查看坐标范围
        print(f"原始坐标范围:")
        print(f"  纬度: {df['lat'].min():.6f} ~ {df['lat'].max():.6f}")
        print(f"  经度: {df['lon'].min():.6f} ~ {df['lon'].max():.6f}")
        
        # 2. 处理时间戳（UTC转datetime）
        df['timestamp'] = pd.to_datetime(df['UTC'], unit='s')
        
        # 3. 速度转换（cm/s -> km/h）
        df['speed_kmh'] = df['SPEED'] * 0.036
        
        # 4. 载客状态判断
        df['is_occupied'] = df['TFLAG'] == 268435456
        
        # 5. 基础数据清洗
        print(f"清洗前记录数: {len(df)}")
        
        # 过滤异常坐标（根据实际数据调整范围）
        lat_min, lat_max = df['lat'].quantile([0.01, 0.99])
        lon_min, lon_max = df['lon'].quantile([0.01, 0.99])
        
        print(f"使用坐标范围:")
        print(f"  纬度: {lat_min:.6f} ~ {lat_max:.6f}")
        print(f"  经度: {lon_min:.6f} ~ {lon_max:.6f}")
        
        df = df[(df['lat'] >= lat_min) & (df['lat'] <= lat_max)]
        df = df[(df['lon'] >= lon_min) & (df['lon'] <= lon_max)]
        
        print(f"坐标过滤后记录数: {len(df)}")
        
        # 过滤异常速度
        df = df[df['speed_kmh'] <= 120]  # 最大速度限制
        df = df[df['speed_kmh'] >= 0]    # 最小速度限制
        
        print(f"速度过滤后记录数: {len(df)}")
        
        # 按车辆和时间排序
        df = df.sort_values(['COMMADDR', 'timestamp'])
        
        print(f"预处理完成，剩余 {len(df)} 条有效记录")
        return df
    
    def convert_to_traffic_data(self, df):
        """
        将DataFrame转换为TrafficData对象列表
        """
        traffic_data_list = []
        
        for _, row in df.iterrows():
            traffic_data = TrafficData(
                vehicle_id=str(row['COMMADDR']),
                timestamp=row['timestamp'],
                latitude=row['lat'],
                longitude=row['lon'],
                speed=row['speed_kmh'],
                heading=row['HEAD'],
                passenger_status=1 if row['is_occupied'] else 0
            )
            traffic_data_list.append(traffic_data)
        
        return traffic_data_list
    
    def analyze_vehicle_trips(self, df, vehicle_id):
        """
        分析单个车辆的行程
        """
        vehicle_data = df[df['COMMADDR'] == vehicle_id].copy()
        vehicle_data = vehicle_data.sort_values('timestamp')
        
        print(f"\n=== 车辆 {vehicle_id} 行程分析 ===")
        print(f"总记录数: {len(vehicle_data)}")
        print(f"时间范围: {vehicle_data['timestamp'].min()} 到 {vehicle_data['timestamp'].max()}")
        print(f"载客记录: {vehicle_data['is_occupied'].sum()} 条")
        print(f"空载记录: {(~vehicle_data['is_occupied']).sum()} 条")
        
        # 计算行驶距离（简化计算）
        vehicle_data['distance'] = 0
        for i in range(1, len(vehicle_data)):
            prev_row = vehicle_data.iloc[i-1]
            curr_row = vehicle_data.iloc[i]
            
            # 简化的距离计算（基于经纬度差值）
            lat_diff = curr_row['lat'] - prev_row['lat']
            lon_diff = curr_row['lon'] - prev_row['lon']
            distance_km = np.sqrt(lat_diff**2 + lon_diff**2) * 111  # 粗略转换为km
            vehicle_data.iloc[i, vehicle_data.columns.get_loc('distance')] = distance_km
        
        total_distance = vehicle_data['distance'].sum()
        print(f"总行驶距离: {total_distance:.2f} km")
        
        return vehicle_data
    
    def test_trip_distance_analysis(self, df):
        """
        测试路程分析功能
        """
        print("\n" + "="*50)
        print("测试路程距离分析功能")
        print("="*50)
        
        try:
            print(f"输入数据记录数: {len(df)}")
            
            # 准备轨迹数据DataFrame（使用原始格式）
            trajectory_data = df[['COMMADDR', 'timestamp', 'lat', 'lon', 'speed_kmh', 'is_occupied']].copy()
            trajectory_data.rename(columns={
                'COMMADDR': 'vehicle_id',
                'speed_kmh': 'speed'
            }, inplace=True)
            
            print(f"轨迹数据格式: {list(trajectory_data.columns)}")
            
            # 调用分析方法
            result = self.engine.analyze_trip_distance_classification(
                trajectory_data=trajectory_data
            )
            
            if result and result.daily_classifications:
                print("\n路程分析结果:")
                for stat in result.daily_classifications:
                    print(f"日期: {stat.date}")
                    print(f"  短途(<4km): {stat.short_percentage:.2f}%")
                    print(f"  中途(4-8km): {stat.medium_percentage:.2f}%") 
                    print(f"  长途(>8km): {stat.long_percentage:.2f}%")
                    print(f"  总订单数: {stat.total_trips}")
                
                if result.overall_stats:
                    print(f"\n总体统计:")
                    print(f"  总订单数: {result.overall_stats.get('total_trips', 0)}")
                    print(f"  整体平均距离: {result.overall_stats.get('overall_avg_distance', 0):.2f} km")
                    
            return result
            
        except Exception as e:
            print(f"路程分析测试失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_order_speed_analysis(self, df):
        """
        测试订单速度分析功能
        """
        print("\n" + "="*50)
        print("测试订单速度分析功能")
        print("="*50)
        
        try:
            print(f"输入数据记录数: {len(df)}")
            
            # 准备轨迹数据DataFrame（使用原始格式）
            trajectory_data = df[['COMMADDR', 'timestamp', 'lat', 'lon', 'speed_kmh', 'is_occupied']].copy()
            trajectory_data.rename(columns={
                'COMMADDR': 'vehicle_id',
                'speed_kmh': 'speed'
            }, inplace=True)
            
            print(f"轨迹数据格式: {list(trajectory_data.columns)}")
            
            # 调用分析方法
            result = self.engine.analyze_order_based_road_speed(
                trajectory_data=trajectory_data,
                include_short_medium_only=True,
                spatial_resolution=0.01,  # 1km网格
                min_orders_per_location=3  # 降低阈值以获得更多结果
            )
            
            if result and result.speed_data:
                print(f"\n速度分析结果:")
                print(f"分析的区域数: {len(result.speed_data)}")
                
                # 统计拥堵情况
                congestion_counts = {}
                for analysis in result.speed_data:
                    level = analysis.congestion_level
                    congestion_counts[level] = congestion_counts.get(level, 0) + 1
                
                print("\n拥堵分布:")
                for level, count in congestion_counts.items():
                    print(f"  {level}: {count} 个区域")
                
                # 显示平均速度
                avg_speeds = [analysis.avg_speed for analysis in result.speed_data]
                if avg_speeds:
                    print(f"\n整体平均速度: {np.mean(avg_speeds):.2f} km/h")
                
                if result.heatmap_data:
                    print(f"\n生成了 {len(result.heatmap_data)} 个热力图数据点")
                
                if result.congestion_summary:
                    print(f"\n拥堵摘要统计完成")
                    
            return result
            
        except Exception as e:
            print(f"订单速度分析测试失败: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """
    主测试函数
    """
    print("="*60)
    print("真实交通数据分析测试")
    print("="*60)
    
    # 初始化处理器
    processor = RealDataProcessor()
    
    # 加载数据样本（为了测试，只加载一小部分数据）
    sample_size = 5000  # 可以根据机器性能调整
    df = processor.load_data_sample("jn0918.csv", sample_size)
    
    if df is None or len(df) == 0:
        print("数据加载失败或为空")
        return
    
    print(f"\n数据统计:")
    print(f"车辆数量: {df['COMMADDR'].nunique()}")
    print(f"时间跨度: {df['timestamp'].max() - df['timestamp'].min()}")
    print(f"载客记录比例: {df['is_occupied'].mean():.2%}")
    print(f"平均速度: {df['speed_kmh'].mean():.2f} km/h")
    
    # 分析几个车辆的详细轨迹
    sample_vehicles = df['COMMADDR'].unique()[:3]
    for vehicle_id in sample_vehicles:
        processor.analyze_vehicle_trips(df, vehicle_id)
    
    # 测试路程分析功能
    trip_result = processor.test_trip_distance_analysis(df)
    
    # 测试订单速度分析功能
    speed_result = processor.test_order_speed_analysis(df)
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"路程分析功能: {'✓ 成功' if trip_result else '✗ 失败'}")
    print(f"订单速度分析功能: {'✓ 成功' if speed_result else '✗ 失败'}")
    
    if trip_result and speed_result:
        print("\n所有功能测试通过！真实数据分析正常工作。")
    else:
        print("\n部分功能存在问题，请检查错误信息。")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试订单速度分析
分析为什么所有订单都显示严重拥堵的问题
"""

import pandas as pd
import numpy as np
import math
from datetime import datetime
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from detect.traffic_visualization.data_processor import TrafficDataProcessor
from detect.traffic_visualization.road_analysis_engine import RoadAnalysisEngine

def debug_speed_analysis():
    """调试速度分析"""
    print("=" * 60)
    print("调试订单速度分析 - 新版本")
    print("=" * 60)
    
    # 创建数据处理器
    data_processor = TrafficDataProcessor()
    
    # 使用2013-09-12的数据进行测试
    start_time = 1379001600  # 2013-09-12 16:00:00
    end_time = 1379005200    # 2013-09-12 17:00:00
    
    print(f"加载数据: {datetime.fromtimestamp(start_time)} 到 {datetime.fromtimestamp(end_time)}")
    
    # 加载数据
    df = data_processor.load_data(start_time, end_time)
    
    if df.empty:
        print("❌ 没有找到数据")
        return
    
    print(f"✅ 成功加载 {len(df)} 条轨迹数据")
    
    # 标准化数据列名
    if 'COMMADDR' in df.columns:
        df['vehicle_id'] = df['COMMADDR']
    if 'UTC' in df.columns:
        df['timestamp'] = df['UTC']
    if 'LAT' in df.columns and 'LON' in df.columns:
        df['latitude'] = df['LAT'] / 1e5
        df['longitude'] = df['LON'] / 1e5
    
    print(f"数据范围:")
    print(f"  - 车辆数: {df['vehicle_id'].nunique()}")
    print(f"  - 时间范围: {datetime.fromtimestamp(float(df['timestamp'].min()))} 到 {datetime.fromtimestamp(float(df['timestamp'].max()))}")
    print(f"  - 纬度范围: {df['latitude'].min():.6f} 到 {df['latitude'].max():.6f}")
    print(f"  - 经度范围: {df['longitude'].min():.6f} 到 {df['longitude'].max():.6f}")
    
    # 创建路段分析引擎
    road_engine = RoadAnalysisEngine()
    
    # 使用新的订单提取逻辑
    print("\n" + "=" * 60)
    print("使用新的订单提取逻辑")
    print("=" * 60)
    
    try:
        # 进行订单速度分析
        speed_analysis = road_engine.analyze_order_based_road_speed(
            df,
            include_short_medium_only=True,
            spatial_resolution=0.001,
            min_orders_per_location=5,
            congestion_threshold={
                "free": 20,      # >20km/h 为畅通 (降低阈值)
                "moderate": 10,  # 10-20km/h 为缓慢 (降低阈值)
                "heavy": 5,      # 5-10km/h 为拥堵 (降低阈值)
                "jam": 0         # <5km/h 为严重拥堵 (降低阈值)
            }
        )
        
        print(f"✅ 成功完成速度分析")
        print(f"分析结果:")
        print(f"  - 总分析位置: {len(speed_analysis.speed_data)}")
        print(f"  - 热力图点数: {len(speed_analysis.heatmap_data)}")
        
        if speed_analysis.speed_data:
            speeds = [data.avg_speed for data in speed_analysis.speed_data]
            print(f"  - 平均速度: {np.mean(speeds):.2f} km/h")
            print(f"  - 最小速度: {min(speeds):.2f} km/h")
            print(f"  - 最大速度: {max(speeds):.2f} km/h")
            
            # 拥堵等级分布
            congestion_counts = {}
            for data in speed_analysis.speed_data:
                level = data.congestion_level
                congestion_counts[level] = congestion_counts.get(level, 0) + 1
            
            print(f"\n拥堵等级分布 (综合算法):")
            for level, count in congestion_counts.items():
                percentage = count / len(speed_analysis.speed_data) * 100
                print(f"  {level}: {count} ({percentage:.1f}%)")
            
            # 显示订单数量分布
            order_counts = [data.order_count for data in speed_analysis.speed_data]
            print(f"\n订单密度统计:")
            print(f"  - 平均每网格订单数: {np.mean(order_counts):.1f}")
            print(f"  - 最小订单数: {min(order_counts)}")
            print(f"  - 最大订单数: {max(order_counts)}")
            
            # 计算实际的订单密度和时间密度
            spatial_resolution = 0.001
            grid_area_km2 = (spatial_resolution * 111) ** 2
            
            actual_densities = []
            time_densities = []
            
            for data in speed_analysis.speed_data:
                order_density = data.order_count / grid_area_km2
                actual_densities.append(order_density)
                # 假设1小时时间窗口
                time_density = data.order_count / 1.0  # 订单数/小时
                time_densities.append(time_density)
            
            print(f"\n实际密度分析:")
            print(f"  - 平均订单密度: {np.mean(actual_densities):.1f} 订单/km²")
            print(f"  - 最小订单密度: {min(actual_densities):.1f} 订单/km²")
            print(f"  - 最大订单密度: {max(actual_densities):.1f} 订单/km²")
            print(f"  - 平均时间密度: {np.mean(time_densities):.1f} 订单/小时")
            print(f"  - 最小时间密度: {min(time_densities):.1f} 订单/小时")
            print(f"  - 最大时间密度: {max(time_densities):.1f} 订单/小时")
            
            # 分析密度分布
            low_density_count = len([d for d in actual_densities if d <= 150])
            medium_density_count = len([d for d in actual_densities if 150 < d <= 400])
            high_density_count = len([d for d in actual_densities if d > 400])
            
            print(f"\n密度分布分析:")
            print(f"  - 低密度区域 (≤150): {low_density_count} ({low_density_count/len(actual_densities)*100:.1f}%)")
            print(f"  - 中密度区域 (150-400): {medium_density_count} ({medium_density_count/len(actual_densities)*100:.1f}%)")
            print(f"  - 高密度区域 (>400): {high_density_count} ({high_density_count/len(actual_densities)*100:.1f}%)")
            
            # 分析时间密度分布
            low_time_density_count = len([d for d in time_densities if d <= 15])
            medium_time_density_count = len([d for d in time_densities if 15 < d <= 40])
            high_time_density_count = len([d for d in time_densities if d > 40])
            
            print(f"\n时间密度分布分析:")
            print(f"  - 低频率区域 (≤15): {low_time_density_count} ({low_time_density_count/len(time_densities)*100:.1f}%)")
            print(f"  - 中频率区域 (15-40): {medium_time_density_count} ({medium_time_density_count/len(time_densities)*100:.1f}%)")
            print(f"  - 高频率区域 (>40): {high_time_density_count} ({high_time_density_count/len(time_densities)*100:.1f}%)")
            
            # 显示置信度分布
            confidence_scores = [data.confidence_score for data in speed_analysis.speed_data]
            print(f"\n置信度统计:")
            print(f"  - 平均置信度: {np.mean(confidence_scores):.3f}")
            print(f"  - 高置信度位置 (>0.5): {len([c for c in confidence_scores if c > 0.5])}")
        
        # 显示拥堵摘要
        if speed_analysis.congestion_summary:
            print(f"\n拥堵摘要 (综合算法):")
            summary = speed_analysis.congestion_summary
            
            if 'total_analysis_locations' in summary:
                print(f"  - 总分析位置: {summary['total_analysis_locations']}")
            
            if 'overall_avg_speed' in summary:
                print(f"  - 整体平均速度: {summary['overall_avg_speed']:.2f} km/h")
            
            if 'congestion_distribution' in summary:
                print(f"  - 拥堵分布:")
                for level, info in summary['congestion_distribution'].items():
                    print(f"    {level}: {info['count']} ({info['percentage']:.1f}%)")
            
            if 'total_orders_analyzed' in summary:
                print(f"  - 总订单数: {summary['total_orders_analyzed']}")
        
        # 分析改进效果
        print("\n" + "=" * 60)
        print("综合算法改进效果分析")
        print("=" * 60)
        
        if speed_analysis.speed_data:
            avg_speed = np.mean([data.avg_speed for data in speed_analysis.speed_data])
            
            print(f"平均速度: {avg_speed:.2f} km/h")
            
            if avg_speed > 15:
                print("✅ 速度分析合理")
            elif avg_speed > 10:
                print("🔄 速度偏低但可接受")
            else:
                print("⚠️  速度仍然偏低")
            
            # 检查拥堵等级分布是否更合理
            jam_percentage = congestion_counts.get('jam', 0) / len(speed_analysis.speed_data) * 100
            free_percentage = congestion_counts.get('free', 0) / len(speed_analysis.speed_data) * 100
            
            print(f"拥堵等级分布:")
            print(f"  - 严重拥堵比例: {jam_percentage:.1f}%")
            print(f"  - 畅通比例: {free_percentage:.1f}%")
            
            if jam_percentage < 30:
                print("✅ 严重拥堵比例合理")
            elif jam_percentage < 50:
                print("🔄 严重拥堵比例有所改善")
            else:
                print("❌ 严重拥堵比例仍然过高")
            
            if free_percentage > 10:
                print("✅ 有畅通区域，分布更合理")
            elif free_percentage > 0:
                print("🔄 有少量畅通区域")
            else:
                print("❌ 没有畅通区域")
            
            # 综合评价
            if jam_percentage < 30 and free_percentage > 10:
                print("\n🎉 综合算法效果优秀！拥堵等级分布合理")
            elif jam_percentage < 50 and (free_percentage > 0 or congestion_counts.get('moderate', 0) > 0):
                print("\n👍 综合算法效果良好，比单纯速度判断更准确")
            else:
                print("\n🔧 综合算法有改善，但仍需进一步优化")
            
    except Exception as e:
        print(f"❌ 速度分析失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_speed_analysis() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
路网数据处理测试脚本
测试路网数据加载、预处理和分析功能
"""

import os
import sys
import time
import logging
import pandas as pd
from typing import List, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

def create_cache_directory():
    """创建缓存目录"""
    from pathlib import Path
    cache_dir = Path(current_dir) / "detect" / "traffic_visualization" / "data" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"创建缓存目录: {cache_dir}")
    return str(cache_dir)

def test_load_road_network():
    """测试路网数据加载功能"""
    logger.info("=== 测试路网数据加载功能 ===")
    
    from detect.traffic_visualization.road_analysis_engine import RoadAnalysisEngine
    road_engine = RoadAnalysisEngine()
    
    start_time = time.time()
    road_segments = road_engine.load_road_network()
    load_time = time.time() - start_time
    
    if road_segments:
        logger.info(f"成功加载 {len(road_segments)} 条路段，耗时 {load_time:.2f} 秒")
        
        # 统计道路类型
        road_types = {}
        for segment in road_segments:
            if segment.road_type not in road_types:
                road_types[segment.road_type] = 0
            road_types[segment.road_type] += 1
        
        logger.info(f"路段类型统计: {road_types}")
        
        # 查看一些路段示例
        for i in range(min(3, len(road_segments))):
            segment = road_segments[i]
            logger.info(f"路段 {i+1}: ID={segment.segment_id}, 类型={segment.road_type}, 长度={segment.segment_length:.2f}公里")
            logger.info(f"  起点: {segment.start_point}, 终点: {segment.end_point}")
    else:
        logger.error("路网数据加载失败")

def test_preprocess_road_network():
    """测试路网数据预处理功能"""
    logger.info("=== 测试路网数据预处理功能 ===")
    
    from detect.traffic_visualization.preprocess_road_network import preprocess_road_network, load_preprocessed_road_network
    
    # 创建缓存目录
    cache_dir = create_cache_directory()
    output_path = os.path.join(cache_dir, "road_network_test.pkl")
    
    # 预处理路网数据
    start_time = time.time()
    segments = preprocess_road_network(output_path=output_path)
    preprocess_time = time.time() - start_time
    
    if segments:
        logger.info(f"成功预处理 {len(segments)} 条路段，耗时 {preprocess_time:.2f} 秒")
        
        # 从预处理文件加载
        start_time = time.time()
        loaded_segments = load_preprocessed_road_network(pickle_path=output_path)
        load_time = time.time() - start_time
        
        if loaded_segments:
            logger.info(f"成功从预处理文件加载 {len(loaded_segments)} 条路段，耗时 {load_time:.2f} 秒")
        else:
            logger.error("从预处理文件加载失败")
    else:
        logger.error("路网数据预处理失败")

def test_road_traffic_analysis():
    """测试路段交通分析功能"""
    logger.info("=== 测试路段交通分析功能 ===")
    
    from detect.traffic_visualization.road_analysis_engine import RoadAnalysisEngine
    from detect.traffic_visualization.data_processor import TrafficDataProcessor
    
    # 创建数据处理器和路段分析引擎
    data_processor = TrafficDataProcessor()
    road_engine = RoadAnalysisEngine()
    
    # 加载路网数据
    logger.info("加载路网数据...")
    start_time = time.time()
    road_segments = road_engine.load_road_network()
    load_time = time.time() - start_time
    logger.info(f"加载了 {len(road_segments)} 条路段，耗时 {load_time:.2f} 秒")
    
    # 加载轨迹数据
    logger.info("加载轨迹数据...")
    start_time = time.time()
    
    # 使用特定时间范围的数据（2013-09-13）
    start_timestamp = 1379030400  # 2013-09-13 00:00:00 UTC
    end_timestamp = 1379116799    # 2013-09-13 23:59:59 UTC
    df = data_processor.load_data(start_timestamp, end_timestamp)
    load_data_time = time.time() - start_time
    
    logger.info(f"加载了 {len(df)} 条轨迹数据，耗时 {load_data_time:.2f} 秒")
    
    # 分析路段交通数据
    logger.info("分析路段交通数据...")
    start_time = time.time()
    traffic_data = road_engine.analyze_road_traffic(df, road_segments[:100])  # 只分析前100个路段以提高速度
    analyze_time = time.time() - start_time
    
    if traffic_data:
        logger.info(f"成功分析 {len(traffic_data)} 条路段交通数据，耗时 {analyze_time:.2f} 秒")
        
        # 查看一些交通数据示例
        for i in range(min(3, len(traffic_data))):
            data = traffic_data[i]
            logger.info(f"交通数据 {i+1}: 路段ID={data.segment_id}")
            logger.info(f"  平均速度: {data.avg_speed:.2f}km/h, 车辆数: {data.vehicle_count}")
            logger.info(f"  交通密度: {data.traffic_density:.2f}辆/公里, 流量: {data.flow_rate:.2f}辆/小时")
            logger.info(f"  拥堵级别: {data.congestion_level}")
    else:
        logger.error("路段交通分析失败")

def test_visualization_data_generation():
    """测试可视化数据生成功能"""
    logger.info("=== 测试可视化数据生成功能 ===")
    
    from detect.traffic_visualization.road_analysis_engine import RoadAnalysisEngine
    from detect.traffic_visualization.data_processor import TrafficDataProcessor
    
    # 创建数据处理器和路段分析引擎
    data_processor = TrafficDataProcessor()
    road_engine = RoadAnalysisEngine()
    
    # 加载路网数据
    road_segments = road_engine.load_road_network()
    
    # 加载轨迹数据（使用较短时间范围以加快测试速度）
    start_timestamp = 1379030400  # 2013-09-13 00:00:00 UTC
    end_timestamp = 1379037600    # 2013-09-13 02:00:00 UTC
    df = data_processor.load_data(start_timestamp, end_timestamp)
    
    # 分析路段交通数据（只分析前50个路段以加快测试速度）
    traffic_data = road_engine.analyze_road_traffic(df, road_segments[:50])
    
    # 生成可视化数据
    logger.info("生成可视化数据...")
    start_time = time.time()
    
    # 使用data_processor的方法生成可视化数据
    visualization_data = data_processor.generate_road_visualization_data(
        road_segments[:50],
        traffic_data,
        visualization_type="speed"
    )
    
    viz_time = time.time() - start_time
    
    if visualization_data:
        logger.info(f"成功生成可视化数据，耗时 {viz_time:.2f} 秒")
        logger.info(f"可视化数据包含 {len(visualization_data.get('segment_colors', {}))} 个路段颜色映射")
    else:
        logger.error("可视化数据生成失败")

if __name__ == "__main__":
    # 测试路网数据加载
    test_load_road_network()
    
    # 测试路网数据预处理
    test_preprocess_road_network()
    
    # 测试路段交通分析
    test_road_traffic_analysis()
    
    # 测试可视化数据生成
    test_visualization_data_generation() 
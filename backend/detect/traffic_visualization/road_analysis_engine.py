"""
路段分析引擎
提供道路层面的交通数据分析功能，包括通行状况、速度分布、距离统计等
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
from geopy.distance import geodesic
import math
from scipy import stats
from collections import defaultdict
import os
import time

from .models import (
    RoadSegment, RoadTrafficData, RoadSegmentStatistics, 
    RoadNetworkAnalysis, SpeedDistribution, TrafficFlowPattern,
    TripDistanceClassification, OrderSpeedAnalysis, RoadSpeedHeatmap,
    TripAnalysisStatistics, RoadSpeedAnalysisResult
)

logger = logging.getLogger(__name__)

class RoadAnalysisEngine:
    """路段分析引擎"""
    
    def __init__(self):
        # 道路类型配置
        self.road_type_configs = {
            'highway': {
                'free_flow_speed': 80,  # km/h
                'capacity_per_lane': 2000,  # vehicles/hour/lane
                'default_lanes': 3
            },
            'arterial': {
                'free_flow_speed': 50,
                'capacity_per_lane': 1200,
                'default_lanes': 2
            },
            'urban': {
                'free_flow_speed': 40,
                'capacity_per_lane': 800,
                'default_lanes': 2
            },
            'local': {
                'free_flow_speed': 30,
                'capacity_per_lane': 600,
                'default_lanes': 1
            }
        }
        
        # 拥堵级别定义
        self.congestion_thresholds = {
            'free': 0.3,      # 自由流：< 30% 容量
            'moderate': 0.6,   # 缓慢：30-60% 容量
            'heavy': 0.8,      # 拥堵：60-80% 容量
            'jam': 1.0         # 严重拥堵：> 80% 容量
        }
    
    def extract_road_segments(self, trajectory_data: pd.DataFrame) -> List[RoadSegment]:
        """从轨迹数据中提取路段信息"""
        try:
            segments = []
            
            # 按vehicle_id和时间排序
            trajectory_data = trajectory_data.sort_values(['vehicle_id', 'timestamp'])
            
            segment_id = 0
            processed_segments = set()
            
            for vehicle_id in trajectory_data['vehicle_id'].unique():
                vehicle_data = trajectory_data[trajectory_data['vehicle_id'] == vehicle_id]
                
                # 生成路径段
                for i in range(len(vehicle_data) - 1):
                    current = vehicle_data.iloc[i]
                    next_point = vehicle_data.iloc[i + 1]
                    
                    # 计算路段长度
                    start_point = {'lat': current['latitude'], 'lng': current['longitude']}
                    end_point = {'lat': next_point['latitude'], 'lng': next_point['longitude']}
                    
                    distance = geodesic(
                        (start_point['lat'], start_point['lng']),
                        (end_point['lat'], end_point['lng'])
                    ).kilometers
                    
                    # 只处理有意义的路段（距离 > 50m）
                    if distance > 0.05:
                        # 创建路段唯一标识（基于起终点坐标）
                        segment_key = f"{start_point['lat']:.6f},{start_point['lng']:.6f}-{end_point['lat']:.6f},{end_point['lng']:.6f}"
                        
                        if segment_key not in processed_segments:
                            road_type = self._classify_road_type(distance, current.get('speed', 0))
                            
                            segment = RoadSegment(
                                segment_id=f"seg_{segment_id}",
                                start_point=start_point,
                                end_point=end_point,
                                segment_length=distance,
                                road_type=road_type,
                                road_name=f"Road_{segment_id}"
                            )
                            segments.append(segment)
                            processed_segments.add(segment_key)
                            segment_id += 1
            
            logger.info(f"提取了 {len(segments)} 个路段")
            return segments
            
        except Exception as e:
            logger.error(f"提取路段信息时出错: {str(e)}")
            return []
    
    def _classify_road_type(self, distance: float, speed: float) -> str:
        """根据距离和速度分类道路类型"""
        if distance > 2.0 and speed > 60:
            return "highway"
        elif distance > 1.0 and speed > 40:
            return "arterial"
        elif distance > 0.5:
            return "urban"
        else:
            return "local"
    
    def analyze_road_traffic(self, trajectory_data: pd.DataFrame, 
                           road_segments: List[RoadSegment]) -> List[RoadTrafficData]:
        """分析路段交通数据，优化版本"""
        try:
            start_time = time.time()
            traffic_data = []
            
            # 标准化数据列名
            trajectory_data = self._standardize_column_names(trajectory_data)
            
            # 确保数据有必需的列
            required_columns = ['timestamp', 'latitude', 'longitude']
            missing_columns = [col for col in required_columns if col not in trajectory_data.columns]
            if missing_columns:
                logger.error(f"数据中缺少必需的列: {missing_columns}")
                return []
            
            logger.info(f"原始数据: {len(trajectory_data)} 条记录")
            
            # 数据量过大时进行智能采样
            original_size = len(trajectory_data)
            if original_size > 100000:
                # 使用分层采样确保覆盖所有时间段和区域
                sample_rate = min(1.0, 100000 / original_size)
                logger.info(f"数据量过大，使用智能采样，目标采样率: {sample_rate:.2f}")
                
                # 先按时间窗口分组
                trajectory_data['time_window'] = pd.to_datetime(trajectory_data['timestamp'], unit='s')
                trajectory_data['time_window'] = trajectory_data['time_window'].dt.floor('15min')
                
                # 分时间窗口采样
                sampled_dfs = []
                for _, group in trajectory_data.groupby('time_window'):
                    group_size = len(group)
                    if group_size > 1000:
                        # 对大时间窗口应用采样
                        group_sample_rate = min(1.0, 1000 / group_size)
                        sampled_group = group.sample(frac=group_sample_rate, random_state=42)
                    else:
                        # 小时间窗口保持原样
                        sampled_group = group
                    sampled_dfs.append(sampled_group)
                
                trajectory_data = pd.concat(sampled_dfs)
                logger.info(f"智能采样后数据量: {len(trajectory_data)} 条记录，实际采样率: {len(trajectory_data)/original_size:.2f}")
            
            # 创建更高效的路段空间索引
            logger.info("创建优化的路段空间索引...")
            from .preprocess_road_network import RoadNetworkPreprocessor
            preprocessor = RoadNetworkPreprocessor()
            
            # 检查是否可以使用预处理的空间索引
            try:
                if preprocessor.cache_exists:
                    logger.info("使用预处理的空间索引")
                    cached_data = preprocessor.load_cached_network()
                    if cached_data and 'spatial_index' in cached_data:
                        spatial_index = cached_data['spatial_index']
                        # 使用预处理的空间索引
                        logger.info(f"加载了预处理的空间索引，包含 {spatial_index.get('grid_count', 0)} 个网格")
                    else:
                        # 如果预处理索引不可用，创建临时索引
                        logger.info("预处理索引不可用，创建临时索引")
                        segment_map = self._create_segment_spatial_index(road_segments)
                        logger.info(f"临时空间索引创建完成，包含 {len(segment_map)} 个网格")
                else:
                    # 创建临时索引
                    logger.info("预处理索引不可用，创建临时索引")
                    segment_map = self._create_segment_spatial_index(road_segments)
                    logger.info(f"临时空间索引创建完成，包含 {len(segment_map)} 个网格")
            except Exception as e:
                # 如果预处理器出错，回退到原始方法
                logger.error(f"使用预处理器时出错: {str(e)}")
                logger.info("回退到原始加载方法")
                segment_map = self._create_segment_spatial_index(road_segments)
                logger.info(f"临时空间索引创建完成，包含 {len(segment_map)} 个网格")
            
            # 使用向量化操作计算网格索引
            logger.info("计算轨迹点网格索引（向量化操作）...")
            trajectory_data['grid_lat'] = np.round(trajectory_data['latitude'], 3)
            trajectory_data['grid_lng'] = np.round(trajectory_data['longitude'], 3)
            trajectory_data['grid_key'] = trajectory_data['grid_lat'].astype(str) + ',' + trajectory_data['grid_lng'].astype(str)
            
            # 按时间窗口聚合数据（15分钟窗口）
            logger.info("按时间窗口聚合数据...")
            if 'time_window' not in trajectory_data.columns:
                trajectory_data['time_window'] = pd.to_datetime(trajectory_data['timestamp'], unit='s')
                trajectory_data['time_window'] = trajectory_data['time_window'].dt.floor('15min')
            
            # 获取唯一的时间窗口
            time_windows = trajectory_data['time_window'].unique()
            total_windows = len(time_windows)
            logger.info(f"共 {total_windows} 个时间窗口需要处理")
            
            # 批量处理路段，而不是逐一处理
            # 将路段分批处理以提高效率
            batch_size = 50  # 每批处理的路段数
            total_segments = len(road_segments)
            batch_count = (total_segments + batch_size - 1) // batch_size  # 向上取整
            
            for batch_idx in range(batch_count):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, total_segments)
                
                logger.info(f"处理路段批次 {batch_idx+1}/{batch_count}，路段 {start_idx+1} 到 {end_idx}...")
                
                # 处理这批路段
                for segment_idx in range(start_idx, end_idx):
                    segment = road_segments[segment_idx]
                    
                    # 获取路段的边界框
                    start_lat = segment.start_point['lat']
                    start_lng = segment.start_point['lng']
                    end_lat = segment.end_point['lat']
                    end_lng = segment.end_point['lng']
                    
                    # 扩展边界以包括周围区域
                    buffer = 0.001  # 约100米的缓冲区
                    min_lat = min(start_lat, end_lat) - buffer
                    max_lat = max(start_lat, end_lat) + buffer
                    min_lng = min(start_lng, end_lng) - buffer
                    max_lng = max(start_lng, end_lng) + buffer
                    
                    # 使用向量化操作过滤数据
                    segment_data = trajectory_data[
                        (trajectory_data['latitude'] >= min_lat) & 
                        (trajectory_data['latitude'] <= max_lat) &
                        (trajectory_data['longitude'] >= min_lng) & 
                        (trajectory_data['longitude'] <= max_lng)
                    ]
                    
                    # 如果没有相关数据，跳过此路段
                    if len(segment_data) == 0:
                        continue
                    
                    # 处理每个时间窗口
                    segment_traffic_batch = []
                    
                    for time_window in time_windows:
                        window_data = segment_data[segment_data['time_window'] == time_window]
                        
                        # 如果此时间窗口内没有数据，跳过
                        if len(window_data) == 0:
                            continue
                        
                        # 转换时间窗口为时间戳
                        timestamp = pd.Timestamp(time_window).timestamp()
                        
                        # 计算路段交通数据
                        segment_traffic = self._calculate_segment_traffic_optimized(window_data, segment, timestamp)
                        
                        # 如果有交通数据，添加到批次结果中
                        if segment_traffic:
                            segment_traffic_batch.append(segment_traffic)
                    
                    # 批量添加到总结果中
                    if segment_traffic_batch:
                        traffic_data.extend(segment_traffic_batch)
                        
                # 每完成一批，记录一次进度
                current_progress = min(end_idx / total_segments * 100, 100)
                logger.info(f"完成进度: {current_progress:.1f}%，当前已处理 {len(traffic_data)} 条交通数据")
            
            processing_time = time.time() - start_time
            logger.info(f"分析了 {len(traffic_data)} 条路段交通数据，耗时 {processing_time:.2f} 秒")
            return traffic_data
            
        except Exception as e:
            logger.error(f"分析路段交通数据时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化数据列名，处理不同格式的数据源"""
        # 复制数据框以避免修改原始数据
        df = df.copy()
        
        # 标准化时间戳列
        if 'timestamp' not in df.columns:
            for col in ['UTC', 'time', 'Time', 'TIME']:
                if col in df.columns:
                    df['timestamp'] = df[col]
                    break
        
        # 标准化纬度列
        if 'latitude' not in df.columns:
            for col in ['LAT', 'lat', 'Lat', 'LATITUDE']:
                if col in df.columns:
                    # 检查是否需要除以因子（某些数据集中坐标可能被乘以了1e5）
                    sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else 0
                    if abs(sample) > 1000:  # 值过大，可能需要除以因子
                        df['latitude'] = df[col] / 1e5
                    else:
                        df['latitude'] = df[col]
                    break
        
        # 标准化经度列
        if 'longitude' not in df.columns:
            for col in ['LON', 'lon', 'Lon', 'lng', 'LONGITUDE']:
                if col in df.columns:
                    # 检查是否需要除以因子
                    sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else 0
                    if abs(sample) > 1000:  # 值过大，可能需要除以因子
                        df['longitude'] = df[col] / 1e5
                    else:
                        df['longitude'] = df[col]
                    break
        
        # 标准化速度列
        if 'speed' not in df.columns:
            # 优先使用清洗后的speed_kmh字段
            if 'speed_kmh' in df.columns:
                df['speed'] = df['speed_kmh']
            elif 'SPEED' in df.columns:
                # 分析SPEED字段的数值分布来判断处理方式
                speed_values = df['SPEED'].dropna()
                if not speed_values.empty:
                    speed_stats = speed_values.describe()
                    median_speed = speed_stats['50%']
                    max_speed = speed_stats['max']
                    
                    print(f"SPEED字段分析: 中位数={median_speed:.2f}, 最大值={max_speed:.2f}")
                    
                    # 判断数值范围和可能的单位
                    if max_speed > 500:  # 明显异常，可能是厘米/秒或其他单位
                        if median_speed > 100:  # 大部分值都很大，可能需要除以100
                            df['speed'] = df['SPEED'] / 100
                            print("应用转换: SPEED / 100")
                        else:  # 只有部分值很大，可能是异常数据
                            # 限制最大速度为150km/h，异常值设为中位数
                            df['speed'] = df['SPEED'].copy()
                            df.loc[df['speed'] > 150, 'speed'] = median_speed
                            print(f"异常值处理: >150km/h的值设为中位数{median_speed:.2f}")
                    else:
                        df['speed'] = df['SPEED']
                        print("直接使用SPEED字段")
                else:
                    df['speed'] = df['SPEED']
            elif 'Speed' in df.columns:
                df['speed'] = df['Speed']
            else:
                # 如果没有速度字段，设置为0
                df['speed'] = 0
        
        # 对速度进行最终的合理性检查和过滤
        if 'speed' in df.columns:
            # 记录处理前的统计
            before_stats = df['speed'].describe()
            print(f"处理前速度统计: 平均={before_stats['mean']:.2f}, 最大={before_stats['max']:.2f}")
            
            # 过滤异常速度值：负值、过大值（>120 km/h）
            df.loc[df['speed'] < 0, 'speed'] = 0
            df.loc[df['speed'] > 120, 'speed'] = 0  # 将异常高速度设为0而不是120
            # 将NaN值设为0
            df['speed'] = df['speed'].fillna(0)
            
            # 记录处理后的统计
            after_stats = df['speed'].describe()
            print(f"处理后速度统计: 平均={after_stats['mean']:.2f}, 最大={after_stats['max']:.2f}")
            
            # 统计有效速度记录
            valid_speed_count = len(df[df['speed'] > 0])
            print(f"有效速度记录: {valid_speed_count}/{len(df)} ({valid_speed_count/len(df)*100:.1f}%)")
        
        # 标准化车辆ID列
        if 'vehicle_id' not in df.columns:
            for col in ['COMMADDR', 'VehicleID', 'vehicle_id', 'id']:
                if col in df.columns:
                    df['vehicle_id'] = df[col].astype(str)
                    break
        
        return df
            
    def _calculate_segment_traffic_optimized(self, window_data: pd.DataFrame, 
                                          segment: RoadSegment, timestamp: float) -> Optional[RoadTrafficData]:
        """优化版本的路段交通数据计算"""
        try:
            # 使用更高效的方法查找经过该路段的车辆
            buffer_distance = 0.001  # 约100米缓冲区
            
            # 获取路段的起点和终点
            start_lat = segment.start_point['lat']
            start_lng = segment.start_point['lng']
            end_lat = segment.end_point['lat']
            end_lng = segment.end_point['lng']
            
            # 计算路段的边界框
            min_lat = min(start_lat, end_lat) - buffer_distance
            max_lat = max(start_lat, end_lat) + buffer_distance
            min_lng = min(start_lng, end_lng) - buffer_distance
            max_lng = max(start_lng, end_lng) + buffer_distance
            
            # 快速过滤：只考虑在边界框内的点
            filtered_data = window_data[
                (window_data['latitude'] >= min_lat) & 
                (window_data['latitude'] <= max_lat) & 
                (window_data['longitude'] >= min_lng) & 
                (window_data['longitude'] <= max_lng)
            ]
            
            if filtered_data.empty:
                return None
            
            # 获取过滤后数据中的车辆ID
            vehicle_ids = []
            if 'vehicle_id' in filtered_data.columns:
                vehicle_ids = filtered_data['vehicle_id'].unique().tolist()
            elif 'COMMADDR' in filtered_data.columns:
                vehicle_ids = filtered_data['COMMADDR'].unique().tolist()
            
            # 如果没有车辆，返回None（避免产生流量为0但有速度的情况）
            if len(vehicle_ids) == 0:
                return None
            
            # 计算路段长度（公里）
            segment_length = segment.segment_length
            
            # 计算车辆平均速度
            speeds = []
            if 'speed' in filtered_data.columns:
                speeds = filtered_data['speed'].values.tolist()
            
            if not speeds:
                avg_speed = 0
                min_speed = 0
                max_speed = 0
            else:
                # 过滤无效数据
                valid_speeds = [s for s in speeds if s > 0]
                if valid_speeds:
                    avg_speed = sum(valid_speeds) / len(valid_speeds)
                    min_speed = min(valid_speeds)
                    max_speed = max(valid_speeds)
                else:
                    avg_speed = 0
                    min_speed = 0
                    max_speed = 0
            
            # 计算交通密度（车辆/公里）
            vehicle_count = len(vehicle_ids)
            traffic_density = vehicle_count / max(0.1, segment_length)  # 防止除以0
            
            # 计算流量率（车辆/小时）
            # 假设时间窗口为15分钟
            time_window_hours = 0.25  # 15分钟 = 0.25小时
            flow_rate = vehicle_count / time_window_hours
            
            # 确定拥堵级别
            congestion_level = self._determine_congestion_level(
                segment.road_type, avg_speed, traffic_density
            )
            
            # 创建路段交通数据对象
            traffic_data = RoadTrafficData(
                segment_id=segment.segment_id,
                timestamp=timestamp,
                vehicle_count=vehicle_count,
                avg_speed=avg_speed,
                min_speed=min_speed,
                max_speed=max_speed,
                traffic_density=traffic_density,
                flow_rate=flow_rate,
                congestion_level=congestion_level
            )
            
            return traffic_data
            
        except Exception as e:
            logger.error(f"计算路段交通数据时出错: {str(e)}")
            return None
    
    def _create_segment_spatial_index(self, segments: List[RoadSegment]) -> Dict:
        """
        创建路段的空间索引，用于快速查找某个位置附近的路段
        
        Args:
            segments: 路段列表
            
        Returns:
            网格到路段列表的映射
        """
        try:
            # 创建网格索引
            grid_map = defaultdict(list)
            
            for segment in segments:
                # 获取起点和终点的坐标
                start_lat = segment.start_point['lat']
                start_lng = segment.start_point['lng']
                end_lat = segment.end_point['lat']
                end_lng = segment.end_point['lng']
                
                # 计算路段的网格键（四舍五入到3位小数）
                start_grid_key = f"{round(start_lat, 3)},{round(start_lng, 3)}"
                end_grid_key = f"{round(end_lat, 3)},{round(end_lng, 3)}"
                
                # 将路段添加到对应的网格中
                grid_map[start_grid_key].append(segment)
                
                # 如果起点和终点不在同一个网格，也添加到终点网格
                if start_grid_key != end_grid_key:
                    grid_map[end_grid_key].append(segment)
                
                # 计算路段经过的中间网格点，确保长路段被正确索引
                # 这里使用简单的线性插值
                if start_grid_key != end_grid_key:
                    # 获取两点之间的步长（按0.001度网格）
                    steps = max(
                        abs(int((end_lat - start_lat) / 0.001)),
                        abs(int((end_lng - start_lng) / 0.001))
                    )
                    
                    if steps > 1:
                        for i in range(1, steps):
                            # 线性插值计算中间点
                            mid_lat = start_lat + (end_lat - start_lat) * i / steps
                            mid_lng = start_lng + (end_lng - start_lng) * i / steps
                            
                            # 计算中间点的网格键
                            mid_grid_key = f"{round(mid_lat, 3)},{round(mid_lng, 3)}"
                            
                            # 将路段添加到中间网格
                            if mid_grid_key != start_grid_key and mid_grid_key != end_grid_key:
                                grid_map[mid_grid_key].append(segment)
            
            return grid_map
            
        except Exception as e:
            logger.error(f"创建路段空间索引时出错: {str(e)}")
            return defaultdict(list)
    
    def _calculate_segment_traffic(self, window_data: pd.DataFrame, 
                                 segment: RoadSegment, timestamp: float) -> Optional[RoadTrafficData]:
        """计算单个路段的交通数据"""
        try:
            # 查找经过该路段的车辆
            vehicles_on_segment = self._find_vehicles_on_segment(window_data, segment)
            
            if len(vehicles_on_segment) == 0:
                return None
            
            # 计算统计数据
            speeds = vehicles_on_segment['speed'].values
            valid_speeds = speeds[speeds > 0]
            
            if len(valid_speeds) == 0:
                return None
            
            vehicle_count = len(vehicles_on_segment)
            avg_speed = float(np.mean(valid_speeds))
            min_speed = float(np.min(valid_speeds))
            max_speed = float(np.max(valid_speeds))
            
            # 计算交通密度和流量率
            traffic_density = vehicle_count / segment.segment_length  # vehicles/km
            flow_rate = vehicle_count * 4  # vehicles/hour (15min窗口 * 4)
            
            # 确定拥堵等级
            congestion_level = self._determine_congestion_level(
                segment.road_type, avg_speed, traffic_density
            )
            
            return RoadTrafficData(
                segment_id=segment.segment_id,
                timestamp=timestamp,
                vehicle_count=vehicle_count,
                avg_speed=avg_speed,
                min_speed=min_speed,
                max_speed=max_speed,
                traffic_density=traffic_density,
                flow_rate=flow_rate,
                congestion_level=congestion_level
            )
            
        except Exception as e:
            logger.error(f"计算路段交通数据时出错: {str(e)}")
            return None
    
    def _find_vehicles_on_segment(self, window_data: pd.DataFrame, 
                                segment: RoadSegment) -> pd.DataFrame:
        """查找经过指定路段的车辆"""
        # 简化的路段匹配：查找在路段起终点附近的车辆
        buffer_distance = 0.001  # 约100米缓冲区
        
        start_lat, start_lng = segment.start_point['lat'], segment.start_point['lng']
        end_lat, end_lng = segment.end_point['lat'], segment.end_point['lng']
        
        # 计算边界框
        min_lat = min(start_lat, end_lat) - buffer_distance
        max_lat = max(start_lat, end_lat) + buffer_distance
        min_lng = min(start_lng, end_lng) - buffer_distance
        max_lng = max(start_lng, end_lng) + buffer_distance
        
        # 筛选在边界框内的车辆
        vehicles_in_box = window_data[
            (window_data['latitude'] >= min_lat) &
            (window_data['latitude'] <= max_lat) &
            (window_data['longitude'] >= min_lng) &
            (window_data['longitude'] <= max_lng)
        ]
        
        return vehicles_in_box
    
    def _determine_congestion_level(self, road_type: str, avg_speed: float, 
                                  traffic_density: float) -> str:
        """确定拥堵等级"""
        config = self.road_type_configs.get(road_type, self.road_type_configs['urban'])
        free_flow_speed = config['free_flow_speed']
        
        # 基于速度的拥堵判断
        speed_ratio = avg_speed / free_flow_speed
        
        if speed_ratio > 0.8:
            return "free"
        elif speed_ratio > 0.6:
            return "moderate"
        elif speed_ratio > 0.3:
            return "heavy"
        else:
            return "jam"
    
    def calculate_segment_statistics(self, traffic_data: List[RoadTrafficData], 
                                   time_range: Tuple[float, float]) -> List[RoadSegmentStatistics]:
        """计算路段统计数据"""
        try:
            statistics = []
            
            # 按路段分组
            segment_groups = defaultdict(list)
            for data in traffic_data:
                if time_range[0] <= data.timestamp <= time_range[1]:
                    segment_groups[data.segment_id].append(data)
            
            for segment_id, segment_data in segment_groups.items():
                if len(segment_data) < 2:
                    continue
                
                stats = self._calculate_single_segment_stats(segment_id, segment_data, time_range)
                if stats:
                    statistics.append(stats)
            
            logger.info(f"计算了 {len(statistics)} 个路段的统计数据")
            return statistics
            
        except Exception as e:
            logger.error(f"计算路段统计数据时出错: {str(e)}")
            return []
    
    def _calculate_single_segment_stats(self, segment_id: str, 
                                      segment_data: List[RoadTrafficData],
                                      time_range: Tuple[float, float]) -> Optional[RoadSegmentStatistics]:
        """计算单个路段的统计数据"""
        try:
            if not segment_data:
                return None
            
            # 基础统计
            speeds = [d.avg_speed for d in segment_data]
            flows = [d.flow_rate for d in segment_data]
            vehicles = [d.vehicle_count for d in segment_data]
            
            # 修复：计算平均车辆数而不是累加（避免重复计算）
            total_vehicles = int(np.mean(vehicles)) if vehicles else 0
            avg_speed = np.mean(speeds)
            speed_variance = np.var(speeds)
            
            # 峰值和非峰值流量
            timestamps = [d.timestamp for d in segment_data]
            hours = [datetime.fromtimestamp(ts).hour for ts in timestamps]
            
            peak_hours = [7, 8, 9, 17, 18, 19]  # 早晚高峰
            peak_flows = [flows[i] for i, h in enumerate(hours) if h in peak_hours]
            off_peak_flows = [flows[i] for i, h in enumerate(hours) if h not in peak_hours]
            
            peak_hour_flow = np.mean(peak_flows) if peak_flows else 0
            off_peak_flow = np.mean(off_peak_flows) if off_peak_flows else 0
            
            # 拥堵小时数
            congestion_hours = len([d for d in segment_data if d.congestion_level in ['heavy', 'jam']]) * 0.25
            
            # 自由流速度（最高10%速度的平均值）
            sorted_speeds = sorted(speeds, reverse=True)
            top_10_percent = max(1, len(sorted_speeds) // 10)
            free_flow_speed = np.mean(sorted_speeds[:top_10_percent])
            
            # 通行能力利用率（简化计算）
            max_flow = max(flows) if flows else 0
            estimated_capacity = 1200  # 估计容量
            capacity_utilization = min(1.0, max_flow / estimated_capacity)
            
            # 效率评分（基于速度、流量、拥堵时长）
            # 防止除以零的错误
            if free_flow_speed > 0:
                speed_score = min(100, (avg_speed / free_flow_speed) * 100)
            else:
                speed_score = 0  # 如果free_flow_speed为0，直接设置分数为0
                
            # 防止除以零的错误    
            if peak_hour_flow > 0:
                flow_score = min(100, (off_peak_flow / peak_hour_flow) * 100)
            else:
                flow_score = 100  # 如果peak_hour_flow为0，则设置满分（表示没有高峰拥堵）
                
            congestion_score = max(0, 100 - (congestion_hours / 24) * 100)
            efficiency_score = (speed_score + flow_score + congestion_score) / 3
            
            return RoadSegmentStatistics(
                segment_id=segment_id,
                time_period={"start": time_range[0], "end": time_range[1]},
                total_vehicles=total_vehicles,
                avg_speed=avg_speed,
                speed_variance=speed_variance,
                peak_hour_flow=peak_hour_flow,
                off_peak_flow=off_peak_flow,
                congestion_hours=congestion_hours,
                free_flow_speed=free_flow_speed,
                capacity_utilization=capacity_utilization,
                efficiency_score=efficiency_score
            )
            
        except Exception as e:
            logger.error(f"计算单个路段统计数据时出错: {str(e)}")
            return None
    
    def analyze_speed_distribution(self, traffic_data: List[RoadTrafficData]) -> List[SpeedDistribution]:
        """分析速度分布"""
        try:
            speed_ranges = [
                "0-20", "20-40", "40-60", "60-80", "80-100", "100+"
            ]
            
            # 方式1：基于路段的分布（每个路段算一个数据点）
            segment_counts = defaultdict(int)
            total_segments = len(traffic_data)
            
            # 修复速度值的处理逻辑
            for data in traffic_data:
                speed = data.avg_speed
                
                # 应用与前端相同的速度修正逻辑
                if speed > 100:  # 异常高值，除以10
                    speed = speed / 10
                elif speed < 2:  # 可能是m/s，转换为km/h
                    speed = speed * 3.6
                
                # 限制在合理范围内
                speed = max(0, min(speed, 120))
                
                # 分配到合适的速度区间
                if speed < 20:
                    segment_counts["0-20"] += 1
                elif speed < 40:
                    segment_counts["20-40"] += 1
                elif speed < 60:
                    segment_counts["40-60"] += 1
                elif speed < 80:
                    segment_counts["60-80"] += 1
                elif speed < 100:
                    segment_counts["80-100"] += 1
                else:
                    segment_counts["100+"] += 1
            
            print(f"速度分布计算调试 (修复后):")
            print(f"  总路段数: {total_segments}")
            print(f"  各速度区间路段数: {dict(segment_counts)}")
            
            distributions = []
            for speed_range in speed_ranges:
                segment_count = segment_counts[speed_range]
                percentage = (segment_count / total_segments * 100) if total_segments > 0 else 0
                
                # 使用路段数而不是车辆数
                distributions.append(SpeedDistribution(
                    speed_range=speed_range,
                    vehicle_count=segment_count,  # 这里存储的是路段数
                    percentage=percentage
                ))
                
                print(f"  {speed_range}: {segment_count}个路段 ({percentage:.1f}%)")
            
            return distributions
            
        except Exception as e:
            logger.error(f"分析速度分布时出错: {str(e)}")
            return []
    
    def analyze_traffic_patterns(self, traffic_data: List[RoadTrafficData]) -> List[TrafficFlowPattern]:
        """分析交通流模式"""
        try:
            hourly_data = defaultdict(list)
            
            # 按小时分组
            for data in traffic_data:
                hour = datetime.fromtimestamp(data.timestamp).hour
                hourly_data[hour].append(data)
            
            patterns = []
            for hour in range(24):
                hour_traffic = hourly_data.get(hour, [])
                
                if hour_traffic:
                    avg_flow = np.mean([d.flow_rate for d in hour_traffic])
                    avg_speed = np.mean([d.avg_speed for d in hour_traffic])
                    
                    # 计算拥堵指数
                    congested_count = len([d for d in hour_traffic if d.congestion_level in ['heavy', 'jam']])
                    congestion_index = congested_count / len(hour_traffic)
                else:
                    avg_flow = 0
                    avg_speed = 0
                    congestion_index = 0
                
                patterns.append(TrafficFlowPattern(
                    hour=hour,
                    avg_flow=avg_flow,
                    avg_speed=avg_speed,
                    congestion_index=congestion_index
                ))
            
            return patterns
            
        except Exception as e:
            logger.error(f"分析交通流模式时出错: {str(e)}")
            return []
    
    def identify_bottlenecks(self, segment_stats: List[RoadSegmentStatistics]) -> List[str]:
        """识别瓶颈路段"""
        try:
            bottlenecks = []
            
            # 瓶颈识别标准
            for stats in segment_stats:
                is_bottleneck = (
                    stats.efficiency_score < 50 or  # 效率评分低
                    stats.capacity_utilization > 0.8 or  # 容量利用率高
                    stats.congestion_hours > 4 or  # 拥堵时间长
                    stats.avg_speed < 20  # 平均速度低
                )
                
                if is_bottleneck:
                    bottlenecks.append(stats.segment_id)
            
            return bottlenecks
            
        except Exception as e:
            logger.error(f"识别瓶颈路段时出错: {str(e)}")
            return []
    
    def generate_network_summary(self, segment_stats: List[RoadSegmentStatistics],
                               traffic_data: List[RoadTrafficData]) -> Dict[str, Any]:
        """生成路网摘要统计"""
        try:
            if not segment_stats:
                return {}
            
            summary = {
                "total_segments": len(segment_stats),
                "total_vehicles": sum([s.total_vehicles for s in segment_stats]),
                "network_avg_speed": np.mean([s.avg_speed for s in segment_stats]),
                "network_efficiency": np.mean([s.efficiency_score for s in segment_stats]),
                "peak_hour_utilization": np.mean([s.capacity_utilization for s in segment_stats]),
                "total_congestion_hours": sum([s.congestion_hours for s in segment_stats]),
                "bottleneck_percentage": 0,
                "road_type_distribution": defaultdict(int),
                "congestion_distribution": defaultdict(int)
            }
            
            # 道路类型分布（需要从原始数据获取）
            for data in traffic_data:
                summary["congestion_distribution"][data.congestion_level] += 1
            
            return dict(summary)
            
        except Exception as e:
            logger.error(f"生成路网摘要时出错: {str(e)}")
            return {} 
    
    def analyze_trip_distance_classification(self, trajectory_data: pd.DataFrame) -> TripAnalysisStatistics:
        """
        分析路程距离分类：短途(<4km)、中途(4-8km)、长途(>8km)
        统计每日占比，完成路程分析的可视化展示
        """
        try:
            # 生成订单数据（基于轨迹数据推断）
            orders_data = self._extract_trip_orders(trajectory_data)
            
            if not orders_data:
                return TripAnalysisStatistics(
                    time_range={"start": 0, "end": 0},
                    daily_classifications=[],
                    overall_stats={},
                    trend_analysis={}
                )
            
            orders_df = pd.DataFrame(orders_data)
            
            # 按日期分组统计
            orders_df['date'] = pd.to_datetime(orders_df['start_time'], unit='s').dt.date
            daily_classifications = []
            
            for date, daily_orders in orders_df.groupby('date'):
                # 按距离分类
                short_trips = len(daily_orders[daily_orders['distance_km'] < 4])
                medium_trips = len(daily_orders[(daily_orders['distance_km'] >= 4) & 
                                               (daily_orders['distance_km'] <= 8)])
                long_trips = len(daily_orders[daily_orders['distance_km'] > 8])
                total_trips = len(daily_orders)
                
                # 计算占比
                short_percentage = (short_trips / total_trips * 100) if total_trips > 0 else 0
                medium_percentage = (medium_trips / total_trips * 100) if total_trips > 0 else 0
                long_percentage = (long_trips / total_trips * 100) if total_trips > 0 else 0
                
                daily_classifications.append(TripDistanceClassification(
                    date=str(date),
                    short_trips=short_trips,
                    medium_trips=medium_trips,
                    long_trips=long_trips,
                    total_trips=total_trips,
                    short_percentage=short_percentage,
                    medium_percentage=medium_percentage,
                    long_percentage=long_percentage,
                    avg_distance=daily_orders['distance_km'].mean()
                ))
            
            # 计算总体统计
            total_short = sum(d.short_trips for d in daily_classifications)
            total_medium = sum(d.medium_trips for d in daily_classifications)
            total_long = sum(d.long_trips for d in daily_classifications)
            total_all = sum(d.total_trips for d in daily_classifications)
            
            overall_stats = {
                "total_trips": total_all,
                "short_trips_total": total_short,
                "medium_trips_total": total_medium,
                "long_trips_total": total_long,
                "overall_short_percentage": (total_short / total_all * 100) if total_all > 0 else 0,
                "overall_medium_percentage": (total_medium / total_all * 100) if total_all > 0 else 0,
                "overall_long_percentage": (total_long / total_all * 100) if total_all > 0 else 0,
                "avg_daily_trips": total_all / len(daily_classifications) if daily_classifications else 0,
                "overall_avg_distance": orders_df['distance_km'].mean()
            }
            
            # 趋势分析
            if len(daily_classifications) > 1:
                dates = [d.date for d in daily_classifications]
                short_percentages = [d.short_percentage for d in daily_classifications]
                medium_percentages = [d.medium_percentage for d in daily_classifications]
                long_percentages = [d.long_percentage for d in daily_classifications]
                
                trend_analysis = {
                    "short_trip_trend": self._calculate_trend(short_percentages),
                    "medium_trip_trend": self._calculate_trend(medium_percentages),
                    "long_trip_trend": self._calculate_trend(long_percentages),
                    "most_common_distance_category": self._get_dominant_category(overall_stats),
                    "distance_stability": self._calculate_stability(
                        [d.avg_distance for d in daily_classifications]
                    )
                }
            else:
                trend_analysis = {
                    "insufficient_data": "需要至少2天的数据来进行趋势分析"
                }
            
            time_range = {
                "start": orders_df['start_time'].min(),
                "end": orders_df['end_time'].max()
            }
            
            logger.info(f"完成路程分析，共分析 {total_all} 个订单，{len(daily_classifications)} 天数据")
            
            return TripAnalysisStatistics(
                time_range=time_range,
                daily_classifications=daily_classifications,
                overall_stats=overall_stats,
                trend_analysis=trend_analysis
            )
            
        except Exception as e:
            logger.error(f"分析路程距离分类时出错: {str(e)}")
            return TripAnalysisStatistics(
                time_range={"start": 0, "end": 0},
                daily_classifications=[],
                overall_stats={"error": str(e)},
                trend_analysis={}
            )
    
    def analyze_order_based_road_speed(self, trajectory_data: pd.DataFrame, 
                                     include_short_medium_only: bool = True,
                                     spatial_resolution: float = 0.001,
                                     min_orders_per_location: int = 5,
                                     congestion_threshold: dict = None) -> RoadSpeedAnalysisResult:
        """
        基于订单数据的道路速度分析
        利用中短途订单的预估距离与起止时间，计算订单的平均速度
        完成道路速度的可视化展示
        """
        try:
            if congestion_threshold is None:
                congestion_threshold = {
                    "free": 20,      # >20km/h 为畅通 (降低阈值)
                    "moderate": 10,  # 10-20km/h 为缓慢 (降低阈值)
                    "heavy": 5,      # 5-10km/h 为拥堵 (降低阈值)
                    "jam": 0         # <5km/h 为严重拥堵 (降低阈值)
                }
            
            # 生成订单数据
            orders_data = self._extract_trip_orders(trajectory_data)
            
            if not orders_data:
                return RoadSpeedAnalysisResult(
                    time_range={"start": 0, "end": 0},
                    speed_data=[],
                    heatmap_data=[],
                    congestion_summary={},
                    road_speed_trends=[]
                )
            
            orders_df = pd.DataFrame(orders_data)
            
            # 筛选中短途订单（如果需要）
            if include_short_medium_only:
                orders_df = orders_df[orders_df['distance_km'] <= 8]
                logger.info(f"筛选中短途订单（≤8km），保留 {len(orders_df)} 个订单")
            
            # 计算订单速度
            orders_df['speed_kmh'] = (orders_df['distance_km'] / 
                                    (orders_df['duration_min'] / 60)).fillna(0)
            
            # 过滤异常速度（0-100 km/h）
            orders_df = orders_df[(orders_df['speed_kmh'] > 0) & (orders_df['speed_kmh'] <= 100)]
            
            # 空间网格化分析
            speed_data = []
            heatmap_data = []
            
            # 按空间网格聚合
            grid_data = self._aggregate_by_spatial_grid(orders_df, spatial_resolution)
            
            for grid_key, grid_orders in grid_data.items():
                if len(grid_orders) >= min_orders_per_location:
                    lat, lng = self._grid_key_to_coords(grid_key, spatial_resolution)
                    
                    speeds = grid_orders['speed_kmh']
                    avg_speed = speeds.mean()
                    speed_variance = speeds.var()
                    order_count = len(grid_orders)
                    
                    # 计算订单密度（订单数/km²）
                    grid_area_km2 = (spatial_resolution * 111) ** 2  # 网格面积（km²）
                    order_density = order_count / grid_area_km2
                    
                    # 计算时间密度（订单数/小时）
                    time_span_hours = (grid_orders['end_time'].max() - grid_orders['start_time'].min()) / 3600
                    time_density = order_count / max(time_span_hours, 1)
                    
                    # 综合判断拥堵等级（考虑速度、密度、流量）
                    congestion_level = self._classify_congestion_level_comprehensive(
                        avg_speed, order_density, time_density, congestion_threshold
                    )
                    
                    # 确定道路类型
                    avg_distance = grid_orders['distance_km'].mean()
                    road_type = "short_medium_trip" if avg_distance <= 8 else "long_trip"
                    
                    # 计算置信度（基于订单数量和密度）
                    confidence_score = min(1.0, (order_count / 20) * (order_density / 100))
                    
                    # 添加到速度分析数据
                    speed_analysis = OrderSpeedAnalysis(
                        timestamp=grid_orders['start_time'].mean(),
                        location={"lat": lat, "lng": lng},
                        order_count=order_count,
                        avg_speed=avg_speed,
                        speed_variance=speed_variance,
                        congestion_level=congestion_level,
                        road_type=road_type,
                        confidence_score=confidence_score
                    )
                    speed_data.append(speed_analysis)
                    
                    # 添加到热力图数据
                    # 拥堵程度越高，热力图强度越大
                    intensity = self._speed_to_intensity_comprehensive(
                        avg_speed, order_density, time_density, congestion_threshold
                    )
                    
                    heatmap_point = RoadSpeedHeatmap(
                        lat=lat,
                        lng=lng,
                        speed=avg_speed,
                        intensity=intensity,
                        order_count=order_count,
                        congestion_level=congestion_level
                    )
                    heatmap_data.append(heatmap_point)
            
            # 生成拥堵摘要统计
            congestion_summary = self._generate_congestion_summary(speed_data, orders_df)
            
            # 生成道路速度趋势
            road_speed_trends = self._generate_speed_trends(orders_df)
            
            time_range = {
                "start": orders_df['start_time'].min(),
                "end": orders_df['end_time'].max()
            }
            
            logger.info(f"完成订单速度分析，生成 {len(speed_data)} 个网格点，{len(heatmap_data)} 个热力图点")
            
            return RoadSpeedAnalysisResult(
                time_range=time_range,
                speed_data=speed_data,
                heatmap_data=heatmap_data,
                congestion_summary=congestion_summary,
                road_speed_trends=road_speed_trends
            )
            
        except Exception as e:
            logger.error(f"分析订单速度时出错: {str(e)}")
            return RoadSpeedAnalysisResult(
                time_range={"start": 0, "end": 0},
                speed_data=[],
                heatmap_data=[],
                congestion_summary={"error": str(e)},
                road_speed_trends=[]
            )
    
    def _extract_trip_orders(self, trajectory_data: pd.DataFrame) -> List[Dict]:
        """
        从轨迹数据中提取订单信息
        简化版：使用时间窗口内的起终点
        """
        try:
            orders_data = []
            
            # 按车辆分组处理
            for vehicle_id, group in trajectory_data.groupby('vehicle_id'):
                # 按时间排序
                group = group.sort_values('timestamp')
                
                if len(group) < 2:
                    continue
                
                # 使用第一个和最后一个点作为订单的起终点
                start_point = group.iloc[0]
                end_point = group.iloc[-1]
            
                start_timestamp = float(start_point['timestamp'])
                end_timestamp = float(end_point['timestamp'])
                duration_min = (end_timestamp - start_timestamp) / 60
            
                # 过滤过短的行程（小于1分钟）
                if duration_min < 1:
                    continue
            
                # 计算距离
                distance_km = self._calculate_distance(
                    start_point['latitude'], start_point['longitude'],
                    end_point['latitude'], end_point['longitude']
                )
            
                # 过滤过短的距离（小于0.05km）
                if distance_km < 0.05:
                    continue
                
                orders_data.append({
                    'order_id': f"{vehicle_id}_{len(orders_data)}",
                    'vehicle_id': vehicle_id,
                    'start_time': start_timestamp,
                    'end_time': end_timestamp,
                    'duration_min': duration_min,
                    'distance_km': distance_km,
                    'start_lat': start_point['latitude'],
                    'start_lng': start_point['longitude'],
                    'end_lat': end_point['latitude'],
                    'end_lng': end_point['longitude']
                })
            
            logger.info(f"从 {trajectory_data['vehicle_id'].nunique()} 个车辆中提取了 {len(orders_data)} 个订单")
            return orders_data
            
        except Exception as e:
            logger.error(f"提取订单数据时出错: {str(e)}")
            return []
    
    def _aggregate_by_spatial_grid(self, orders_df: pd.DataFrame, resolution: float) -> Dict:
        """按空间网格聚合订单数据"""
        try:
            grid_data = defaultdict(list)
            
            for _, order in orders_df.iterrows():
                # 使用起点坐标进行网格化
                grid_lat = round(order['start_lat'] / resolution) * resolution
                grid_lng = round(order['start_lng'] / resolution) * resolution
                grid_key = f"{grid_lat:.6f},{grid_lng:.6f}"
                
                grid_data[grid_key].append(order)
            
            # 转换为DataFrame格式
            result = {}
            for grid_key, orders in grid_data.items():
                result[grid_key] = pd.DataFrame(orders)
            
            return result
            
        except Exception as e:
            logger.error(f"空间网格聚合时出错: {str(e)}")
            return {}
    
    def _grid_key_to_coords(self, grid_key: str, resolution: float) -> Tuple[float, float]:
        """将网格键转换为坐标"""
        try:
            lat_str, lng_str = grid_key.split(',')
            lat = float(lat_str) + resolution / 2  # 网格中心点
            lng = float(lng_str) + resolution / 2
            return lat, lng
        except Exception:
            return 0.0, 0.0
    
    def _classify_congestion_level(self, speed: float, threshold: dict) -> str:
        """根据速度分类拥堵等级"""
        if speed >= threshold["free"]:
            return "free"
        elif speed >= threshold["moderate"]:
            return "moderate"
        elif speed >= threshold["heavy"]:
            return "heavy"
        else:
            return "jam"
    
    def _speed_to_intensity(self, speed: float, threshold: dict) -> float:
        """将速度转换为热力图强度（0-1）"""
        max_speed = threshold["free"]
        # 速度越低，强度越高（表示拥堵程度）
        intensity = max(0, min(1, (max_speed - speed) / max_speed))
        return intensity
    
    def _generate_congestion_summary(self, speed_data: List[OrderSpeedAnalysis], 
                                   orders_df: pd.DataFrame) -> Dict[str, Any]:
        """生成拥堵摘要统计"""
        try:
            if not speed_data:
                return {}
            
            # 按拥堵等级统计
            congestion_counts = defaultdict(int)
            total_locations = len(speed_data)
            
            for data in speed_data:
                congestion_counts[data.congestion_level] += 1
            
            # 整体速度统计
            all_speeds = [data.avg_speed for data in speed_data]
            
            summary = {
                "total_analysis_locations": total_locations,
                "congestion_distribution": {
                    level: {
                        "count": count,
                        "percentage": (count / total_locations * 100) if total_locations > 0 else 0
                    }
                    for level, count in congestion_counts.items()
                },
                "overall_avg_speed": np.mean(all_speeds) if all_speeds else 0,
                "speed_statistics": {
                    "min_speed": min(all_speeds) if all_speeds else 0,
                    "max_speed": max(all_speeds) if all_speeds else 0,
                    "median_speed": np.median(all_speeds) if all_speeds else 0,
                    "std_speed": np.std(all_speeds) if all_speeds else 0
                },
                "high_confidence_locations": len([d for d in speed_data if d.confidence_score > 0.7]),
                "total_orders_analyzed": len(orders_df)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"生成拥堵摘要时出错: {str(e)}")
            return {"error": str(e)}
    
    def _generate_speed_trends(self, orders_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """生成道路速度趋势分析"""
        try:
            # 按小时分组分析趋势
            orders_df['hour'] = pd.to_datetime(orders_df['start_time'], unit='s').dt.hour
            hourly_trends = []
            
            for hour in range(24):
                hour_orders = orders_df[orders_df['hour'] == hour]
                if len(hour_orders) > 0:
                    avg_speed = hour_orders['speed_kmh'].mean()
                    order_count = len(hour_orders)
                    
                    # 判断高峰时段
                    is_peak = hour in [7, 8, 9, 17, 18, 19]  # 早晚高峰
                    
                    hourly_trends.append({
                        "hour": hour,
                        "avg_speed": avg_speed,
                        "order_count": order_count,
                        "is_peak_hour": is_peak,
                        "speed_category": self._classify_congestion_level(
                            avg_speed, {"free": 40, "moderate": 25, "heavy": 15, "jam": 0}
                        )
                    })
            
            return hourly_trends
            
        except Exception as e:
            logger.error(f"生成速度趋势时出错: {str(e)}")
            return []
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势方向"""
        if len(values) < 2:
            return "insufficient_data"
        
        # 简单线性趋势
        x = list(range(len(values)))
        if len(values) > 1:
            slope = np.polyfit(x, values, 1)[0]
            if slope > 0.5:
                return "increasing"
            elif slope < -0.5:
                return "decreasing"
            else:
                return "stable"
        return "stable"
    
    def _get_dominant_category(self, overall_stats: Dict) -> str:
        """获取占主导地位的距离类别"""
        short_pct = overall_stats.get("overall_short_percentage", 0)
        medium_pct = overall_stats.get("overall_medium_percentage", 0)
        long_pct = overall_stats.get("overall_long_percentage", 0)
        
        max_pct = max(short_pct, medium_pct, long_pct)
        
        if max_pct == short_pct:
            return "short_distance"
        elif max_pct == medium_pct:
            return "medium_distance"
        else:
            return "long_distance"
    
    def _calculate_stability(self, values: List[float]) -> str:
        """计算数据稳定性"""
        if len(values) < 2:
            return "insufficient_data"
        
        cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
        
        if cv < 0.1:
            return "very_stable"
        elif cv < 0.2:
            return "stable"
        elif cv < 0.3:
            return "moderate"
        else:
            return "unstable"
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        计算两点间的距离（公里）
        使用Haversine公式
        """
        try:
            import math
            
            # 将角度转换为弧度
            lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
            
            # Haversine公式
            dlat = lat2 - lat1
            dlng = lng2 - lng1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # 地球半径（公里）
            r = 6371
            
            return c * r
            
        except Exception:
            # 如果计算失败，使用简化的欧几里得距离
            dlat = lat2 - lat1
            dlng = lng2 - lng1
            return math.sqrt(dlat**2 + dlng**2) * 111  # 大约转换为公里

    def _classify_congestion_level_comprehensive(self, speed: float, order_density: float, 
                                               time_density: float, threshold: dict) -> str:
        """
        综合判断拥堵等级
        考虑速度、订单密度、时间密度三个因素
        """
        # 速度权重 (40%)
        speed_score = 0
        if speed >= threshold["free"]:
            speed_score = 4  # 畅通
        elif speed >= threshold["moderate"]:
            speed_score = 3  # 缓慢
        elif speed >= threshold["heavy"]:
            speed_score = 2  # 拥堵
        else:
            speed_score = 1  # 严重拥堵
        
        # 订单密度权重 (30%) - 密度越高，拥堵程度越高
        # 调整阈值，让低密度区域更容易被识别为畅通
        density_score = 4  # 默认畅通
        if order_density > 800:  # 高密度 (降低阈值)
            density_score = 1
        elif order_density > 400:  # 中高密度 (降低阈值)
            density_score = 2
        elif order_density > 150:  # 中密度 (降低阈值)
            density_score = 3
        # order_density <= 150 保持为 4 (畅通)
        
        # 时间密度权重 (30%) - 单位时间内订单越多，说明交通越繁忙
        # 调整阈值，让低频率区域更容易被识别为畅通
        time_score = 4  # 默认畅通
        if time_density > 80:  # 高频率 (降低阈值)
            time_score = 1
        elif time_density > 40:  # 中高频率 (降低阈值)
            time_score = 2
        elif time_density > 15:  # 中频率 (降低阈值)
            time_score = 3
        # time_density <= 15 保持为 4 (畅通)
        
        # 综合评分
        comprehensive_score = (speed_score * 0.4 + density_score * 0.3 + time_score * 0.3)
        
        # 调整判断阈值，让更多区域被识别为畅通
        if comprehensive_score >= 3.2:  # 降低畅通阈值 (原来是3.5)
            return "free"
        elif comprehensive_score >= 2.3:  # 降低缓慢阈值 (原来是2.5)
            return "moderate"
        elif comprehensive_score >= 1.4:  # 降低拥堵阈值 (原来是1.5)
            return "heavy"
        else:
            return "jam"

    def _speed_to_intensity_comprehensive(self, speed: float, order_density: float, 
                                        time_density: float, threshold: dict) -> float:
        """
        综合计算热力图强度
        考虑速度、订单密度、时间密度
        """
        # 速度强度 (速度越低，强度越高)
        max_speed = threshold["free"]
        speed_intensity = max(0, min(1, (max_speed - speed) / max_speed))
        
        # 密度强度 (密度越高，强度越高)
        density_intensity = min(1, order_density / 1000)
        
        # 时间强度 (频率越高，强度越高)
        time_intensity = min(1, time_density / 100)
        
        # 综合强度
        comprehensive_intensity = (speed_intensity * 0.4 + density_intensity * 0.3 + time_intensity * 0.3)
        
        return comprehensive_intensity

    def load_road_network(self, csv_path: str = None) -> List[RoadSegment]:
        """
        从预处理的pickle文件或jn_FX.csv文件加载路网数据
        优先使用预处理的pickle文件以提高加载速度
        
        Args:
            csv_path: CSV文件路径，如果为None则使用默认路径
            
        Returns:
            路段对象列表
        """
        try:
            from .preprocess_road_network import load_preprocessed_road_network
            
            logger.info("尝试从预处理文件加载路网数据...")
            start_time = time.time()
            
            # 尝试从预处理文件加载
            segments = load_preprocessed_road_network()
            
            # 如果预处理文件加载成功，直接返回
            if segments and len(segments) > 0:
                load_time = time.time() - start_time
                logger.info(f"成功从预处理文件加载 {len(segments)} 条路段，耗时 {load_time:.2f} 秒")
                
                # 将字典转换为RoadSegment对象
                road_segments = []
                for segment in segments:
                    road_segment = RoadSegment(
                        segment_id=segment['segment_id'],
                        start_point=segment['start_point'],
                        end_point=segment['end_point'],
                        segment_length=segment['segment_length'],
                        road_type=segment['road_type'],
                        road_name=segment['road_name']
                    )
                    road_segments.append(road_segment)
                
                return road_segments
            
            # 如果预处理文件加载失败，使用原始方法加载
            logger.warning("预处理文件加载失败，使用原始CSV文件加载")
            
            # 以下是原始加载逻辑
            # 如果未指定路径，使用默认路径
            if csv_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                csv_path = os.path.join(current_dir, 'data', 'jn_FX.csv')
            
            logger.info(f"从 {csv_path} 加载路网数据...")
            
            # 读取CSV文件
            df = pd.read_csv(csv_path)
            logger.info(f"加载了 {len(df)} 条路段数据")
            
            # 转换为RoadSegment对象列表
            segments = []
            for _, row in df.iterrows():
                segment_id = str(row['ID'])
                start_point = {'lat': row['Start_Y'], 'lng': row['Start_X']}
                end_point = {'lat': row['END_Y'], 'lng': row['END_X']}
                
                # 确定道路类型（简单分类）
                length = row['Length']
                road_type = self._classify_road_type_by_length(length)
                
                # 创建路段对象
                segment = RoadSegment(
                    segment_id=segment_id,
                    start_point=start_point,
                    end_point=end_point,
                    segment_length=length / 1000,  # 转换为公里
                    road_type=road_type,
                    road_name=f"Road_{segment_id}"
                )
                segments.append(segment)
            
            # 保存为预处理文件，以便下次使用
            from .preprocess_road_network import preprocess_road_network
            preprocess_road_network(csv_path=csv_path)
            
            logger.info(f"成功转换 {len(segments)} 条路段")
            return segments
            
        except Exception as e:
            logger.error(f"加载路网数据时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def _classify_road_type_by_length(self, length: float) -> str:
        """根据路段长度简单分类道路类型"""
        if length > 1000:  # 大于1000米
            return "highway"
        elif length > 500:  # 500-1000米
            return "arterial"
        elif length > 200:  # 200-500米
            return "urban"
        else:  # 小于200米
            return "local"
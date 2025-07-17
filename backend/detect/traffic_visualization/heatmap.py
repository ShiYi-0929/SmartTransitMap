import pandas as pd
import numpy as np
import os
from typing import List, Dict, Optional, Any, Tuple
import math
from datetime import datetime
from .data_processor import TrafficDataProcessor

class HeatmapGenerator:
    """热力图生成器，提供热力图数据处理功能"""
    
    def __init__(self):
        """初始化热力图生成器"""
        self.data_processor = TrafficDataProcessor()
    
    def generate_heatmap(self, start_time: float, end_time: float, 
                         resolution: float = 0.001, 
                         min_count: int = 1,
                         max_points: int = 10000) -> List[Dict[str, Any]]:
        """
        生成热力图数据
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            resolution: 热力图分辨率（经纬度网格大小）
            min_count: 最小计数，低于此值的点将被过滤
            max_points: 最大返回点数，超过此值将进行采样
            
        Returns:
            热力图数据列表
        """
        # 加载数据
        df = self.data_processor.load_data(start_time, end_time)
        
        if df.empty:
            return []
        
        # 生成热力图数据
        heatmap_points = self.data_processor.generate_heatmap_data(df, resolution)
        
        # 过滤低计数点
        filtered_points = [point for point in heatmap_points if point.count >= min_count]
        
        # 如果点数过多，进行采样
        if len(filtered_points) > max_points:
            # 按计数排序
            filtered_points.sort(key=lambda x: x.count, reverse=True)
            # 取前max_points个点
            filtered_points = filtered_points[:max_points]
        
        # 转换为字典列表
        return [point.dict() for point in filtered_points]
    
    def generate_time_filtered_heatmap(self, start_time: float, end_time: float,
                                      time_segments: List[Tuple[int, int]] = None,
                                      resolution: float = 0.001) -> Dict[str, List[Dict[str, Any]]]:
        """
        生成按时间段过滤的热力图数据
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            time_segments: 时间段列表，每个元素为(开始小时,结束小时)，如[(7,9),(17,19)]表示早晚高峰
            resolution: 热力图分辨率
            
        Returns:
            按时间段分组的热力图数据
        """
        # 如果未指定时间段，使用默认时间段
        if time_segments is None:
            time_segments = [
                (7, 9),    # 早高峰
                (11, 14),  # 午餐时间
                (17, 19),  # 晚高峰
                (22, 6)    # 夜间
            ]
        
        # 加载数据
        df = self.data_processor.load_data(start_time, end_time)
        
        if df.empty:
            return {f"{seg[0]}-{seg[1]}": [] for seg in time_segments}
        
        # 添加小时列
        df['datetime'] = pd.to_datetime(df['UTC'], unit='s')
        df['hour'] = df['datetime'].dt.hour
        
        # 按时间段分组处理
        result = {}
        
        for start_hour, end_hour in time_segments:
            segment_name = f"{start_hour}-{end_hour}"
            
            # 过滤时间段
            if start_hour < end_hour:
                # 正常时间段，如7-9
                segment_df = df[(df['hour'] >= start_hour) & (df['hour'] < end_hour)]
            else:
                # 跨日时间段，如22-6
                segment_df = df[(df['hour'] >= start_hour) | (df['hour'] < end_hour)]
            
            if segment_df.empty:
                result[segment_name] = []
                continue
            
            # 生成热力图数据
            heatmap_points = self.data_processor.generate_heatmap_data(segment_df, resolution)
            
            # 转换为字典列表
            result[segment_name] = [point.dict() for point in heatmap_points]
        
        return result
    
    def generate_pickup_heatmap(self, start_time: float, end_time: float,
                               resolution: float = 0.001) -> List[Dict[str, Any]]:
        """
        生成上客点热力图
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            resolution: 热力图分辨率
            
        Returns:
            上客点热力图数据
        """
        # 加载数据
        df = self.data_processor.load_data(start_time, end_time)
        
        if df.empty:
            return []
        
        # 模拟上客点识别（实际应根据真实业务逻辑识别）
        # 这里我们简化为：车辆停留超过一定时间后再次移动的点视为上客点
        pickup_points = self._identify_pickup_points(df)
        
        if pickup_points.empty:
            return []
        
        # 生成热力图数据
        heatmap_points = self.data_processor.generate_heatmap_data(pickup_points, resolution)
        
        # 转换为字典列表
        return [point.dict() for point in heatmap_points]
    
    def _identify_pickup_points(self, df: pd.DataFrame, 
                               min_stop_time: float = 60,  # 最小停留时间（秒）
                               max_speed: float = 5  # 最大停留速度（km/h）
                              ) -> pd.DataFrame:
        """
        识别上客点
        
        Args:
            df: 轨迹数据DataFrame
            min_stop_time: 最小停留时间（秒）
            max_speed: 最大停留速度（km/h）
            
        Returns:
            上客点DataFrame
        """
        # 确保数据按车辆ID和时间排序
        df = df.sort_values(['COMMADDR', 'UTC'])
        
        # 存储上客点
        pickup_points = []
        
        # 按车辆分组处理
        for vehicle_id, group in df.groupby('COMMADDR'):
            # 如果轨迹点太少，跳过
            if len(group) < 3:
                continue
            
            # 计算相邻点之间的时间差和距离
            group = group.reset_index(drop=True)
            group['next_UTC'] = group['UTC'].shift(-1)
            group['time_diff'] = group['next_UTC'] - group['UTC']
            
            # 计算速度（如果数据中没有速度列）
            if 'SPEED' not in group.columns:
                group['next_LON'] = group['LON'].shift(-1)
                group['next_LAT'] = group['LAT'].shift(-1)
                
                # 计算距离（简化版，使用欧几里得距离）
                group['distance'] = np.sqrt(
                    ((group['next_LON'] - group['LON']) / 1e5) ** 2 + 
                    ((group['next_LAT'] - group['LAT']) / 1e5) ** 2
                ) * 111  # 转换为公里
                
                # 计算速度（km/h）
                group['speed'] = group['distance'] / (group['time_diff'] / 3600)
            else:
                group['speed'] = group['SPEED']
            
            # 识别停留点（速度低且停留时间长）
            stop_points = group[(group['speed'] <= max_speed) & (group['time_diff'] >= min_stop_time)]
            
            # 将停留点添加到上客点列表
            if not stop_points.empty:
                pickup_points.append(stop_points)
        
        # 合并所有上客点
        if pickup_points:
            return pd.concat(pickup_points, ignore_index=True)
        else:
            return pd.DataFrame() 
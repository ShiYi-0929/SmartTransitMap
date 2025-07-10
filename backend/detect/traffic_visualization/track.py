import pandas as pd
import numpy as np
import os
from typing import List, Dict, Optional, Any
import math
from datetime import datetime
from .data_processor import TrafficDataProcessor

class TrackAnalyzer:
    """轨迹分析类，提供轨迹查询和分析功能"""
    
    def __init__(self):
        """初始化轨迹分析器"""
        self.data_processor = TrafficDataProcessor()
    
    def query_track(self, start_time: float, end_time: float, vehicle_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        查询指定时间范围和车辆ID的轨迹
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            vehicle_id: 车辆ID，如果为None则返回所有车辆的轨迹
            
        Returns:
            轨迹数据列表
        """
        # 加载数据
        df = self.data_processor.load_data(start_time, end_time, vehicle_id)
        
        if df.empty:
            return []
        
        # 生成轨迹数据
        tracks = self.data_processor.generate_track_data(df, vehicle_id)
        
        # 转换为字典列表
        return [track.dict() for track in tracks]
    
    def calculate_track_metrics(self, track_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算轨迹指标
        
        Args:
            track_data: 轨迹数据列表
            
        Returns:
            轨迹指标字典
        """
        if not track_data:
            return {
                'total_tracks': 0,
                'total_distance': 0,
                'avg_distance': 0,
                'avg_duration': 0,
                'avg_speed': 0
            }
        
        # 计算总轨迹数
        total_tracks = len(track_data)
        
        # 计算总距离
        total_distance = sum(track.get('distance', 0) or 0 for track in track_data)
        
        # 计算平均距离
        avg_distance = total_distance / total_tracks if total_tracks > 0 else 0
        
        # 计算平均持续时间
        total_duration = sum(
            (track.get('end_time', 0) - track.get('start_time', 0)) / 60  # 转换为分钟
            for track in track_data if track.get('end_time') and track.get('start_time')
        )
        avg_duration = total_duration / total_tracks if total_tracks > 0 else 0
        
        # 计算平均速度（公里/小时）
        avg_speed = (avg_distance / (avg_duration / 60)) if avg_duration > 0 else 0
        
        return {
            'total_tracks': total_tracks,
            'total_distance': round(total_distance, 2),
            'avg_distance': round(avg_distance, 2),
            'avg_duration': round(avg_duration, 2),
            'avg_speed': round(avg_speed, 2)
        }
    
    def find_similar_tracks(self, track_id: str, start_time: float, end_time: float, 
                           similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        查找相似轨迹
        
        Args:
            track_id: 参考轨迹的车辆ID
            start_time: 开始时间戳
            end_time: 结束时间戳
            similarity_threshold: 相似度阈值（0-1）
            
        Returns:
            相似轨迹列表
        """
        # 获取参考轨迹
        reference_tracks = self.query_track(start_time, end_time, track_id)
        
        if not reference_tracks:
            return []
        
        reference_track = reference_tracks[0]
        
        # 获取所有轨迹
        all_tracks = self.query_track(start_time, end_time)
        
        # 计算相似度并筛选
        similar_tracks = []
        
        for track in all_tracks:
            # 跳过参考轨迹自身
            if track['vehicle_id'] == track_id:
                continue
            
            # 计算轨迹相似度
            similarity = self._calculate_track_similarity(reference_track, track)
            
            # 如果相似度超过阈值，添加到结果中
            if similarity >= similarity_threshold:
                track['similarity'] = round(similarity, 2)
                similar_tracks.append(track)
        
        # 按相似度降序排序
        similar_tracks.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_tracks
    
    def _calculate_track_similarity(self, track1: Dict[str, Any], track2: Dict[str, Any]) -> float:
        """
        计算两条轨迹的相似度
        
        Args:
            track1: 第一条轨迹
            track2: 第二条轨迹
            
        Returns:
            相似度（0-1）
        """
        # 提取轨迹点
        points1 = track1.get('points', [])
        points2 = track2.get('points', [])
        
        if not points1 or not points2:
            return 0
        
        # 简化计算：使用轨迹起点和终点的相似度
        start_similarity = self._calculate_point_similarity(points1[0], points2[0])
        end_similarity = self._calculate_point_similarity(points1[-1], points2[-1])
        
        # 计算平均相似度
        return (start_similarity + end_similarity) / 2
    
    def _calculate_point_similarity(self, point1: Dict[str, Any], point2: Dict[str, Any]) -> float:
        """
        计算两个点的相似度
        
        Args:
            point1: 第一个点
            point2: 第二个点
            
        Returns:
            相似度（0-1）
        """
        # 计算两点之间的距离
        distance = math.sqrt(
            (point1.get('lng', 0) - point2.get('lng', 0)) ** 2 +
            (point1.get('lat', 0) - point2.get('lat', 0)) ** 2
        )
        
        # 将距离转换为相似度（距离越小，相似度越高）
        # 使用高斯函数：similarity = exp(-distance^2 / (2 * sigma^2))
        sigma = 0.001  # 可调参数
        similarity = math.exp(-distance ** 2 / (2 * sigma ** 2))
        
        return similarity 
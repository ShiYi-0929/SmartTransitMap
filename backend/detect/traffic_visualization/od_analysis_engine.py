"""
OD对(Origin-Destination)分析引擎
处理车辆起点终点数据，生成OD流量矩阵和分析
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
import math
from datetime import datetime, timedelta

class ODAnalysisEngine:
    """OD对分析引擎主类"""
    
    def __init__(self):
        self.od_pairs = []
        self.flow_matrix = None
        self.grid_size = 0.01  # 默认网格大小（约1km）
        
    def extract_od_pairs(
        self, 
        df: pd.DataFrame,
        min_trip_duration: int = 60,
        max_trip_duration: int = 7200,
        min_trip_distance: float = 0.1,
        stop_duration_threshold: int = 300
    ) -> List[Dict[str, Any]]:
        """
        从轨迹数据中提取OD对
        
        Args:
            df: 轨迹数据DataFrame
            min_trip_duration: 最小行程时间（秒）
            max_trip_duration: 最大行程时间（秒）
            min_trip_distance: 最小行程距离（公里）
            stop_duration_threshold: 停车时长阈值（秒），用于识别行程的起止点
            
        Returns:
            OD对列表
        """
        od_pairs = []
        
        # 按车辆分组处理
        for vehicle_id, group in df.groupby('COMMADDR'):
            group = group.sort_values('UTC').reset_index(drop=True)
            
            if len(group) < 2:
                continue
                
            # 识别行程片段
            trips = self._identify_trips(group, stop_duration_threshold)
            
            for trip in trips:
                # 计算行程统计
                duration = trip['end_time'] - trip['start_time']
                distance = self._calculate_distance(
                    trip['origin_lat'], trip['origin_lng'],
                    trip['destination_lat'], trip['destination_lng']
                )
                
                # 过滤条件
                if (duration >= min_trip_duration and 
                    duration <= max_trip_duration and 
                    distance >= min_trip_distance):
                    
                    od_pair = {
                        "vehicle_id": str(vehicle_id),
                        "trip_id": f"{vehicle_id}_{trip['start_time']}",
                        "origin_lat": trip['origin_lat'],
                        "origin_lng": trip['origin_lng'],
                        "destination_lat": trip['destination_lat'],
                        "destination_lng": trip['destination_lng'],
                        "start_time": trip['start_time'],
                        "end_time": trip['end_time'],
                        "duration": duration,
                        "distance": distance
                    }
                    
                    od_pairs.append(od_pair)
        
        self.od_pairs = od_pairs
        return od_pairs
    
    def _identify_trips(self, vehicle_data: pd.DataFrame, stop_threshold: int) -> List[Dict[str, Any]]:
        """
        识别车辆的行程片段
        通过检测长时间停车来分割行程
        """
        trips = []
        
        if len(vehicle_data) < 2:
            return trips
            
        # 找出停车点（连续位置变化很小的点）
        stop_points = []
        distance_threshold = 0.0002  # 约20米的经纬度距离
        
        for i in range(1, len(vehicle_data)):
            prev_row = vehicle_data.iloc[i-1]
            curr_row = vehicle_data.iloc[i]
            
            # 计算距离
            distance = math.sqrt(
                (curr_row['LAT']/1e5 - prev_row['LAT']/1e5)**2 + 
                (curr_row['LON']/1e5 - prev_row['LON']/1e5)**2
            )
            
            time_diff = curr_row['UTC'] - prev_row['UTC']
            
            # 如果距离很小且时间差很大，认为是停车
            if distance < distance_threshold and time_diff > stop_threshold:
                stop_points.append({
                    'index': i-1,
                    'lat': prev_row['LAT'] / 1e5,
                    'lng': prev_row['LON'] / 1e5,
                    'time': prev_row['UTC'],
                    'stop_duration': time_diff
                })
        
        # 基于停车点分割行程
        if not stop_points:
            # 如果没有明显的停车点，整个轨迹作为一个行程
            first_row = vehicle_data.iloc[0]
            last_row = vehicle_data.iloc[-1]
            
            trips.append({
                'origin_lat': first_row['LAT'] / 1e5,
                'origin_lng': first_row['LON'] / 1e5,
                'destination_lat': last_row['LAT'] / 1e5,
                'destination_lng': last_row['LON'] / 1e5,
                'start_time': first_row['UTC'],
                'end_time': last_row['UTC']
            })
        else:
            # 根据停车点分割行程
            start_idx = 0
            
            for stop in stop_points:
                if start_idx < stop['index']:
                    start_row = vehicle_data.iloc[start_idx]
                    end_row = vehicle_data.iloc[stop['index']]
                    
                    trips.append({
                        'origin_lat': start_row['LAT'] / 1e5,
                        'origin_lng': start_row['LON'] / 1e5,
                        'destination_lat': end_row['LAT'] / 1e5,
                        'destination_lng': end_row['LON'] / 1e5,
                        'start_time': start_row['UTC'],
                        'end_time': end_row['UTC']
                    })
                
                # 下一个行程从停车点之后开始
                start_idx = stop['index'] + 1
            
            # 处理最后一段行程
            if start_idx < len(vehicle_data) - 1:
                start_row = vehicle_data.iloc[start_idx]
                end_row = vehicle_data.iloc[-1]
                
                trips.append({
                    'origin_lat': start_row['LAT'] / 1e5,
                    'origin_lng': start_row['LON'] / 1e5,
                    'destination_lat': end_row['LAT'] / 1e5,
                    'destination_lng': end_row['LON'] / 1e5,
                    'start_time': start_row['UTC'],
                    'end_time': end_row['UTC']
                })
        
        return trips
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """计算两点间的距离（公里）"""
        R = 6371  # 地球半径
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def generate_flow_matrix(
        self, 
        od_pairs: List[Dict[str, Any]] = None,
        grid_size: float = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        生成OD流量矩阵
        
        Args:
            od_pairs: OD对数据，如果为None则使用self.od_pairs
            grid_size: 网格大小（度），如果为None则使用self.grid_size
            
        Returns:
            flow_matrix: 流量矩阵
            grid_info: 网格信息
        """
        if od_pairs is None:
            od_pairs = self.od_pairs
            
        if grid_size is None:
            grid_size = self.grid_size
            
        if not od_pairs:
            return np.array([]), {}
        
        # 计算空间范围
        all_lats = []
        all_lngs = []
        
        for od in od_pairs:
            all_lats.extend([od['origin_lat'], od['destination_lat']])
            all_lngs.extend([od['origin_lng'], od['destination_lng']])
        
        min_lat, max_lat = min(all_lats), max(all_lats)
        min_lng, max_lng = min(all_lngs), max(all_lngs)
        
        # 创建网格
        lat_bins = np.arange(min_lat, max_lat + grid_size, grid_size)
        lng_bins = np.arange(min_lng, max_lng + grid_size, grid_size)
        
        n_lat_bins = len(lat_bins) - 1
        n_lng_bins = len(lng_bins) - 1
        n_grids = n_lat_bins * n_lng_bins
        
        # 初始化流量矩阵
        flow_matrix = np.zeros((n_grids, n_grids))
        
        # 网格索引映射
        def get_grid_index(lat, lng):
            lat_idx = min(int((lat - min_lat) / grid_size), n_lat_bins - 1)
            lng_idx = min(int((lng - min_lng) / grid_size), n_lng_bins - 1)
            return lat_idx * n_lng_bins + lng_idx
        
        # 填充流量矩阵
        for od in od_pairs:
            origin_idx = get_grid_index(od['origin_lat'], od['origin_lng'])
            dest_idx = get_grid_index(od['destination_lat'], od['destination_lng'])
            
            if 0 <= origin_idx < n_grids and 0 <= dest_idx < n_grids:
                flow_matrix[origin_idx, dest_idx] += 1
        
        # 网格信息
        grid_info = {
            'grid_size': grid_size,
            'n_lat_bins': n_lat_bins,
            'n_lng_bins': n_lng_bins,
            'lat_bins': lat_bins.tolist(),
            'lng_bins': lng_bins.tolist(),
            'min_lat': min_lat,
            'max_lat': max_lat,
            'min_lng': min_lng,
            'max_lng': max_lng,
            'total_flows': int(flow_matrix.sum())
        }
        
        self.flow_matrix = flow_matrix
        return flow_matrix, grid_info
    
    def analyze_top_flows(
        self, 
        od_pairs: List[Dict[str, Any]] = None,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        分析最高流量的OD对
        
        Args:
            od_pairs: OD对数据
            top_k: 返回前k个流量最高的OD对
            
        Returns:
            流量分析结果
        """
        if od_pairs is None:
            od_pairs = self.od_pairs
            
        if not od_pairs:
            return []
        
        # 按起终点位置聚合流量
        flow_counts = {}
        
        for od in od_pairs:
            # 将坐标量化到网格
            origin_key = f"{od['origin_lat']:.3f},{od['origin_lng']:.3f}"
            dest_key = f"{od['destination_lat']:.3f},{od['destination_lng']:.3f}"
            od_key = f"{origin_key}->{dest_key}"
            
            if od_key not in flow_counts:
                flow_counts[od_key] = {
                    'origin_lat': od['origin_lat'],
                    'origin_lng': od['origin_lng'],
                    'destination_lat': od['destination_lat'],
                    'destination_lng': od['destination_lng'],
                    'flow_count': 0,
                    'avg_duration': 0,
                    'avg_distance': 0,
                    'total_duration': 0,
                    'total_distance': 0
                }
            
            flow_counts[od_key]['flow_count'] += 1
            flow_counts[od_key]['total_duration'] += od['duration']
            flow_counts[od_key]['total_distance'] += od['distance']
        
        # 计算平均值
        for flow_data in flow_counts.values():
            if flow_data['flow_count'] > 0:
                flow_data['avg_duration'] = flow_data['total_duration'] / flow_data['flow_count']
                flow_data['avg_distance'] = flow_data['total_distance'] / flow_data['flow_count']
        
        # 按流量排序并返回前k个
        top_flows = sorted(
            flow_counts.values(),
            key=lambda x: x['flow_count'],
            reverse=True
        )[:top_k]
        
        return top_flows
    
    def analyze_temporal_patterns(
        self, 
        od_pairs: List[Dict[str, Any]] = None,
        time_resolution: int = 60  # 时间分辨率（分钟）
    ) -> Dict[str, Any]:
        """
        分析OD对的时间模式
        
        Args:
            od_pairs: OD对数据
            time_resolution: 时间分辨率（分钟）
            
        Returns:
            时间模式分析结果
        """
        if od_pairs is None:
            od_pairs = self.od_pairs
            
        if not od_pairs:
            return {}
        
        # 按时间窗口统计
        time_counts = {}
        
        for od in od_pairs:
            # 将时间戳转换为时间窗口
            dt = datetime.fromtimestamp(od['start_time'])
            time_window = dt.replace(
                minute=(dt.minute // time_resolution) * time_resolution,
                second=0,
                microsecond=0
            )
            
            time_key = time_window.strftime('%H:%M')
            
            if time_key not in time_counts:
                time_counts[time_key] = 0
            time_counts[time_key] += 1
        
        # 计算小时分布
        hour_counts = {}
        for od in od_pairs:
            hour = datetime.fromtimestamp(od['start_time']).hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # 计算工作日vs周末分布（简化版，假设数据在一周内）
        weekday_counts = {'weekday': 0, 'weekend': 0}
        for od in od_pairs:
            weekday = datetime.fromtimestamp(od['start_time']).weekday()
            if weekday < 5:  # 0-4是周一到周五
                weekday_counts['weekday'] += 1
            else:
                weekday_counts['weekend'] += 1
        
        return {
            'time_window_distribution': time_counts,
            'hourly_distribution': hour_counts,
            'weekday_distribution': weekday_counts,
            'total_trips': len(od_pairs),
            'time_resolution_minutes': time_resolution
        }
    
    def analyze_spatial_patterns(
        self, 
        od_pairs: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分析OD对的空间模式
        
        Args:
            od_pairs: OD对数据
            
        Returns:
            空间模式分析结果
        """
        if od_pairs is None:
            od_pairs = self.od_pairs
            
        if not od_pairs:
            return {}
        
        # 分析起点分布
        origin_points = [(od['origin_lat'], od['origin_lng']) for od in od_pairs]
        dest_points = [(od['destination_lat'], od['destination_lng']) for od in od_pairs]
        
        # 计算空间范围
        all_lats = [od['origin_lat'] for od in od_pairs] + [od['destination_lat'] for od in od_pairs]
        all_lngs = [od['origin_lng'] for od in od_pairs] + [od['destination_lng'] for od in od_pairs]
        
        spatial_bounds = {
            'min_lat': min(all_lats),
            'max_lat': max(all_lats),
            'min_lng': min(all_lngs),
            'max_lng': max(all_lngs),
            'lat_range': max(all_lats) - min(all_lats),
            'lng_range': max(all_lngs) - min(all_lngs)
        }
        
        # 计算距离分布
        distances = [od['distance'] for od in od_pairs]
        distance_stats = {
            'min_distance': min(distances),
            'max_distance': max(distances),
            'avg_distance': np.mean(distances),
            'median_distance': np.median(distances),
            'std_distance': np.std(distances)
        }
        
        # 计算持续时间分布
        durations = [od['duration'] for od in od_pairs]
        duration_stats = {
            'min_duration': min(durations),
            'max_duration': max(durations),
            'avg_duration': np.mean(durations),
            'median_duration': np.median(durations),
            'std_duration': np.std(durations)
        }
        
        return {
            'spatial_bounds': spatial_bounds,
            'distance_statistics': distance_stats,
            'duration_statistics': duration_stats,
            'total_unique_origins': len(set(origin_points)),
            'total_unique_destinations': len(set(dest_points))
        }
    
    def calculate_od_statistics(self, od_pairs: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        计算OD对的综合统计信息
        
        Args:
            od_pairs: OD对数据
            
        Returns:
            统计信息
        """
        if od_pairs is None:
            od_pairs = self.od_pairs
            
        if not od_pairs:
            return {
                'total_trips': 0,
                'total_vehicles': 0,
                'temporal_patterns': {},
                'spatial_patterns': {},
                'top_flows': []
            }
        
        # 基本统计
        total_trips = len(od_pairs)
        total_vehicles = len(set(od['vehicle_id'] for od in od_pairs))
        
        # 时间和空间模式分析
        temporal_patterns = self.analyze_temporal_patterns(od_pairs)
        spatial_patterns = self.analyze_spatial_patterns(od_pairs)
        top_flows = self.analyze_top_flows(od_pairs, top_k=10)
        
        return {
            'total_trips': total_trips,
            'total_vehicles': total_vehicles,
            'temporal_patterns': temporal_patterns,
            'spatial_patterns': spatial_patterns,
            'top_flows': top_flows
        } 
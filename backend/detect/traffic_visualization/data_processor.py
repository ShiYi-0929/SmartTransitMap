import pandas as pd
import numpy as np
import os
import json
from typing import List, Dict, Tuple, Optional, Union, Any
from datetime import datetime
import math
from collections import defaultdict
from .models import HeatmapPoint, TrackPoint, VehicleTrack
import logging
import time
import traceback

class TrafficDataProcessor:
    """交通数据处理类，负责加载、处理和转换交通数据"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化数据处理器
        
        Args:
            data_dir: 数据目录路径，如果为None则使用默认路径
        """
        if data_dir is None:
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 尝试多种可能的数据路径
            possible_paths = [
                os.path.join(current_dir, 'data'),
                os.path.join(current_dir, '..', '..', 'data'),
                os.path.join(current_dir, '..', '..', '..', 'data')
            ]
            
            # 使用第一个存在的路径
            for path in possible_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    self.data_dir = path
                    break
            else:
                # 如果都不存在，使用相对路径
                self.data_dir = os.path.join(current_dir, 'data')
        else:
            self.data_dir = data_dir
            
        print(f"数据目录: {self.data_dir}")
        
        # 预处理数据目录
        self.processed_dir = os.path.join(self.data_dir, 'processed')
        self.index_dir = os.path.join(self.data_dir, 'indexes')
        
        # 检查是否存在预处理数据
        self.use_preprocessed = (
            os.path.exists(self.processed_dir) and 
            os.path.exists(self.index_dir) and
            len(os.listdir(self.processed_dir)) > 0
        )
        
        if self.use_preprocessed:
            print("✓ 发现预处理数据，将使用高效查询模式")
            self._load_indexes()
        else:
            print("✗ 未发现预处理数据，将使用原始CSV文件（较慢）")
        
        # 增强的缓存系统
        self._cached_data = {}
        self._cache_maxsize = 10  # 增加缓存大小
        self._sample_cache = {}   # 采样数据缓存
        self._heatmap_cache = {}  # 热力图缓存
        self._csv_files = None
        
        # 性能优化参数
        self.max_data_points = 50000  # 单次查询最大数据点数
        self.sample_ratio = 0.2       # 数据采样比例
        self.enable_sampling = True   # 禁用智能采样
    
    def _load_indexes(self):
        """加载预处理的索引数据"""
        try:
            # 加载车辆索引
            vehicle_index_path = os.path.join(self.index_dir, 'vehicle_index.json')
            if os.path.exists(vehicle_index_path):
                with open(vehicle_index_path, 'r') as f:
                    self.vehicle_index = json.load(f)
                print(f"✓ 加载车辆索引: {len(self.vehicle_index)} 个车辆")
            else:
                self.vehicle_index = {}
            
            # 加载空间网格
            self.spatial_grids = {}
            for filename in os.listdir(self.index_dir):
                if filename.startswith('spatial_grid_') and filename.endswith('.json'):
                    resolution = float(filename.split('_')[2].split('.')[0])
                    filepath = os.path.join(self.index_dir, filename)
                    with open(filepath, 'r') as f:
                        self.spatial_grids[resolution] = json.load(f)
                    print(f"✓ 加载空间网格 ({resolution}): {len(self.spatial_grids[resolution])} 个网格")
            
        except Exception as e:
            print(f"警告：加载索引时出错: {e}")
            self.use_preprocessed = False

    def get_csv_files(self) -> List[str]:
        """获取数据目录中的所有CSV文件"""
        if self._csv_files is None:
            # 获取所有CSV文件
            self._csv_files = [
                os.path.join(self.data_dir, f) 
                for f in os.listdir(self.data_dir) 
                if f.endswith('.csv')
            ]
        return self._csv_files
    
    def load_data(self, start_time: float, end_time: float, vehicle_id: Optional[str] = None) -> pd.DataFrame:
        """
        加载指定时间范围和车辆ID的数据（性能优化版本）
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            vehicle_id: 车辆ID，如果为None则加载所有车辆数据
            
        Returns:
            符合条件的数据DataFrame
        """
        print(f"⚡ 快速加载数据: {start_time} 到 {end_time}")
        
        # 生成缓存键
        cache_key = f"data_{start_time}_{end_time}_{vehicle_id}_{self.sample_ratio}"
        
        # 检查缓存
        if cache_key in self._cached_data:
            print("📦 使用缓存数据（秒级响应）")
            return self._cached_data[cache_key]
        
        # 使用预处理数据进行快速查询
        if self.use_preprocessed:
            result = self._load_data_fast(start_time, end_time, vehicle_id)
        else:
            result = self._load_data_legacy(start_time, end_time, vehicle_id)
        
        # 智能采样以提高性能
        if self.enable_sampling and len(result) > self.max_data_points:
            print(f"🔄 数据量过大({len(result)}条)，进行智能采样...")
            result = self._smart_sample_data(result, vehicle_id)
        
        # 加载数据后，优先用清洗后的速度
        if 'speed_kmh' in result.columns:
            result['SPEED'] = result['speed_kmh']
        
        # 更新缓存（LRU策略）
        if len(self._cached_data) >= self._cache_maxsize:
            # 删除最旧的缓存
            oldest_key = next(iter(self._cached_data))
            del self._cached_data[oldest_key]
        
        self._cached_data[cache_key] = result
        print(f"✅ 数据加载完成: {len(result)} 条记录")
        return result
    
    def _smart_sample_data(self, df: pd.DataFrame, vehicle_id: Optional[str] = None) -> pd.DataFrame:
        """智能数据采样，保持数据分布特性"""
        if df.empty:
            return df
        
        # 如果指定了车辆ID，保留所有该车辆的数据
        if vehicle_id:
            vehicle_data = df[df['COMMADDR'].astype(str) == str(vehicle_id)]
            if len(vehicle_data) <= self.max_data_points:
                return vehicle_data
            else:
                # 对单车数据进行时间均匀采样
                n_samples = min(self.max_data_points, len(vehicle_data))
                indices = np.linspace(0, len(vehicle_data)-1, n_samples, dtype=int)
                return vehicle_data.iloc[indices].copy()
        
        # 对所有车辆进行分层采样
        target_size = int(self.max_data_points * self.sample_ratio)
        
        # 按车辆ID分组采样
        sampled_groups = []
        vehicle_groups = df.groupby('COMMADDR')
        
        # 计算每个车辆应该采样的数量
        n_vehicles = len(vehicle_groups)
        # 确保每个车辆至少保留2条记录以便进行路程分析
        min_samples_per_vehicle = 2
        samples_per_vehicle = max(min_samples_per_vehicle, target_size // n_vehicles)
        
        # 如果总需求超过目标大小，则按比例调整
        total_demand = n_vehicles * samples_per_vehicle
        if total_demand > target_size:
            # 优先保证每个车辆至少有2条记录
            samples_per_vehicle = max(min_samples_per_vehicle, target_size // n_vehicles)
        
        for vehicle_id, group in vehicle_groups:
            if len(group) <= samples_per_vehicle:
                sampled_groups.append(group)
            else:
                # 时间均匀采样，确保包含起点和终点
                if samples_per_vehicle == 2:
                    # 如果只能保留2条记录，选择第一条和最后一条
                    selected_indices = [0, len(group)-1]
                else:
                    # 时间均匀采样
                    indices = np.linspace(0, len(group)-1, samples_per_vehicle, dtype=int)
                    selected_indices = indices
                sampled_groups.append(group.iloc[selected_indices])
        
        result = pd.concat(sampled_groups, ignore_index=True)
        print(f"   采样结果: {len(result)} 条记录 ({len(df)} -> {len(result)})")
        return result

    def _load_data_fast(self, start_time: float, end_time: float, vehicle_id: Optional[str] = None) -> pd.DataFrame:
        """使用预处理数据进行快速加载（优化版本）"""
        print("🚀 使用预处理数据进行极速查询...")
        
        # 计算需要的时间段（小时级别）
        start_hour = (int(start_time) // 3600) * 3600
        end_hour = (int(end_time) // 3600) * 3600
        
        # 如果指定了车辆ID，先检查车辆索引
        if vehicle_id and vehicle_id in self.vehicle_index:
            available_hours = set(self.vehicle_index[vehicle_id])
            print(f"🚗 车辆 {vehicle_id} 在 {len(available_hours)} 个时间段出现")
        else:
            available_hours = None
        
        # 限制最大时间范围（防止加载过多数据）
        max_hours = 24  # 最多加载24小时的数据
        time_span_hours = (end_hour - start_hour) // 3600
        
        if time_span_hours > max_hours:
            print(f"⚠️  时间范围过大({time_span_hours}小时)，限制为{max_hours}小时")
            end_hour = start_hour + max_hours * 3600
        
        # 加载相关时间段的数据
        data_frames = []
        current_hour = start_hour
        processed_count = 0
        max_files = 24  # 允许加载24小时的数据文件
        file_count = 0
        
        while current_hour <= end_hour and file_count < max_files:
            if available_hours is None or current_hour in available_hours:
                filename = f"hour_{int(current_hour)}.parquet"
                filepath = os.path.join(self.processed_dir, filename)
                
                if os.path.exists(filepath):
                    try:
                        # 使用列选择优化
                        columns_to_load = [
                            'UTC', 'COMMADDR', 'LAT', 'LON', 'SPEED',
                            'lat', 'lon', 'speed_kmh', 'is_occupied', 'timestamp', 'hour'
                        ]
                        df = pd.read_parquet(filepath, columns=columns_to_load)
                        
                        # 精确时间过滤
                        df = df[(df['UTC'] >= start_time) & (df['UTC'] <= end_time)]
                        
                        # 车辆ID过滤
                        if vehicle_id:
                            df['COMMADDR'] = df['COMMADDR'].astype(str)
                            df = df[df['COMMADDR'] == str(vehicle_id)]
                        
                        if not df.empty:
                            data_frames.append(df)
                            processed_count += len(df)
                            print(f"   📁 {filename}: {len(df)} 条记录")
                            file_count += 1
                        
                    except Exception as e:
                        print(f"❌ 读取 {filename} 时出错: {e}")
            
            current_hour += 3600  # 下一小时
        
        # 合并数据
        if data_frames:
            result = pd.concat(data_frames, ignore_index=True)
            
            # 按时间排序
            result = result.sort_values('UTC')
            
            print(f"⚡ 快速加载完成，共 {len(result)} 条记录")
            return result
        else:
            print("❌ 未找到匹配的数据")
            return pd.DataFrame()

    def _load_data_legacy(self, start_time: float, end_time: float, vehicle_id: Optional[str] = None) -> pd.DataFrame:
        """使用原始CSV文件进行加载（备用方法）"""
        print("使用原始CSV文件进行查询（较慢）...")
        
        # 添加数据集时间范围验证
        min_valid_time = 1378944000  # 2013-09-12 00:00:00 UTC
        max_valid_time = 1379548799  # 2013-09-18 23:59:59 UTC
        
        # 检查请求的时间范围是否与数据集时间范围有交集
        if end_time < min_valid_time or start_time > max_valid_time:
            print(f"警告：请求的时间范围 ({start_time}-{end_time}) 超出数据集范围 ({min_valid_time}-{max_valid_time})")
            return pd.DataFrame()
        
        # 限制查询时间范围，避免处理过多数据
        time_span_hours = (end_time - start_time) / 3600
        if time_span_hours > 24:
            print(f"警告：查询时间跨度过大 ({time_span_hours:.1f} 小时)，建议缩短到24小时以内")
            end_time = start_time + 24 * 3600
            print(f"自动截断到24小时: {start_time} 到 {end_time}")
        
        # 生成缓存键
        cache_key = f"{start_time}_{end_time}_{vehicle_id}"
        
        # 如果已缓存，直接返回
        if cache_key in self._cached_data:
            print("使用缓存数据")
            return self._cached_data[cache_key]
        
        # 获取所有CSV文件
        csv_files = self.get_csv_files()
        
        if not csv_files:
            print("未找到CSV文件")
            return pd.DataFrame()
        
        print(f"找到 {len(csv_files)} 个CSV文件")
        
        # 存储所有符合条件的数据
        all_data = []
        total_rows_processed = 0
        max_rows_limit = 200000  # 减少内存占用
        
        for i, file_path in enumerate(csv_files):
            print(f"处理文件 {i+1}/{len(csv_files)}: {os.path.basename(file_path)}")
            
            try:
                # 使用分块读取大文件
                chunk_size = 50000
                chunks = pd.read_csv(file_path, chunksize=chunk_size)
                
                for chunk_num, chunk in enumerate(chunks):
                    if total_rows_processed >= max_rows_limit:
                        print(f"达到最大行数限制 ({max_rows_limit})，停止处理更多数据")
                        break
                        
                    # 检查必要的列是否存在
                    required_cols = ['UTC', 'LAT', 'LON', 'COMMADDR']
                    if not all(col in chunk.columns for col in required_cols):
                        continue
                    
                    # 时间过滤
                    filtered_chunk = chunk[(chunk['UTC'] >= start_time) & (chunk['UTC'] <= end_time)]
                    
                    # 车辆ID过滤
                    if vehicle_id:
                        filtered_chunk['COMMADDR'] = filtered_chunk['COMMADDR'].astype(str)
                        filtered_chunk = filtered_chunk[filtered_chunk['COMMADDR'] == str(vehicle_id)]
                    
                    if not filtered_chunk.empty:
                        all_data.append(filtered_chunk)
                        total_rows_processed += len(filtered_chunk)
                
                if total_rows_processed >= max_rows_limit:
                    break
            
            except Exception as e:
                print(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
        
        # 合并所有数据
        if all_data:
            result_df = pd.concat(all_data, ignore_index=True)
            
            # 智能采样
            if len(result_df) > 100000:
                result_df = result_df.sample(n=100000, random_state=42)
            
            # 缓存结果
            if len(self._cached_data) < 3:
                self._cached_data[cache_key] = result_df
            
            return result_df
        else:
            return pd.DataFrame()

    def generate_heatmap_data(self, df: pd.DataFrame, resolution: float = 0.001) -> List[HeatmapPoint]:
        """
        生成热力图数据（优化缓存版本）
        """
        # 生成热力图缓存键
        if df.empty:
            cache_key = f"heatmap_empty_{resolution}"
        else:
            # 基于数据特征生成缓存键
            data_hash = hash(f"{len(df)}_{df['UTC'].min()}_{df['UTC'].max()}_{resolution}")
            cache_key = f"heatmap_{data_hash}"
        
        # 检查缓存
        if cache_key in self._heatmap_cache:
            print("📦 使用热力图缓存（秒级响应）")
            return self._heatmap_cache[cache_key]
        
        # 生成热力图
        if self.use_preprocessed and hasattr(self, 'spatial_grids'):
            result = self._generate_heatmap_fast(df, resolution)
        else:
            result = self._generate_heatmap_legacy(df, resolution)
        
        # 缓存结果（限制缓存大小）
        if len(self._heatmap_cache) >= 5:
            # 删除最旧的缓存
            oldest_key = next(iter(self._heatmap_cache))
            del self._heatmap_cache[oldest_key]
        
        self._heatmap_cache[cache_key] = result
        return result
    
    def _generate_heatmap_fast(self, df: pd.DataFrame, resolution: float = 0.001) -> List[HeatmapPoint]:
        """使用预计算数据快速生成热力图"""
        # 寻找最接近的分辨率
        available_resolutions = list(self.spatial_grids.keys())
        if not available_resolutions:
            return self._generate_heatmap_legacy(df, resolution)
        
        # 选择最接近的分辨率
        closest_resolution = min(available_resolutions, key=lambda x: abs(x - resolution))
        print(f"使用预计算网格 (分辨率: {closest_resolution})")
        
        grid_data = self.spatial_grids[closest_resolution]
        
        # 如果df为空或没有时间过滤需求，直接返回预计算结果
        if df.empty:
            heatmap_points = []
            for grid_key, count in grid_data.items():
                try:
                    lat, lng = map(float, grid_key.split(','))
                    heatmap_points.append(HeatmapPoint(lat=lat, lng=lng, count=count))
                except:
                    continue
            print(f"快速热力图生成完成，共 {len(heatmap_points)} 个点")
            return heatmap_points
        
        # 如果有特定数据过滤，结合实时计算
        return self._generate_heatmap_legacy(df, resolution)
    
    def _generate_heatmap_legacy(self, df: pd.DataFrame, resolution: float = 0.001) -> List[HeatmapPoint]:
        """传统方式生成热力图"""
        if df.empty:
            return []
        
        # 确保经纬度列存在
        if 'LAT' not in df.columns or 'LON' not in df.columns:
            print("数据中缺少经纬度列")
            return []
        
        # 转换坐标（假设原始数据需要除以1e5）
        df['lat'] = df['LAT'] / 1e5
        df['lng'] = df['LON'] / 1e5
        
        # 按分辨率网格化
        df['lat_grid'] = (df['lat'] / resolution).round() * resolution
        df['lng_grid'] = (df['lng'] / resolution).round() * resolution
        
        # 统计每个网格的点数
        grid_counts = df.groupby(['lat_grid', 'lng_grid']).size().reset_index(name='count')
        
        # 转换为热力图点列表
        heatmap_points = [
            HeatmapPoint(lat=row['lat_grid'], lng=row['lng_grid'], count=row['count'])
            for _, row in grid_counts.iterrows()
        ]
        
        return heatmap_points
    
    def generate_track_data(self, df: pd.DataFrame, vehicle_id: str = None) -> List[VehicleTrack]:
        """
        生成车辆轨迹数据（性能优化版本）
        
        Args:
            df: 包含轨迹数据的DataFrame
            vehicle_id: 车辆ID，如果为None则处理所有车辆
            
        Returns:
            车辆轨迹列表
        """
        if df.empty:
            return []
        
        # 确保必要的列存在
        required_cols = ['UTC', 'LAT', 'LON', 'COMMADDR']
        if not all(col in df.columns for col in required_cols):
            print("❌ 数据中缺少必要的列")
            return []
        
        # 如果指定了车辆ID，则只处理该车辆
        if vehicle_id:
            # 确保类型匹配，避免因类型不一致导致过滤失败
            df['COMMADDR'] = df['COMMADDR'].astype(str)
            vehicle_id_str = str(vehicle_id) if vehicle_id else ""
            df = df[df['COMMADDR'] == vehicle_id_str]
            if df.empty:
                return []
        
        # 限制处理的车辆数量以提高性能
        unique_vehicles = df['COMMADDR'].unique()
        max_vehicles = 50  # 最多处理50个车辆
        
        if len(unique_vehicles) > max_vehicles and vehicle_id is None:
            print(f"⚠️  车辆数量过多({len(unique_vehicles)})，随机选择{max_vehicles}个")
            selected_vehicles = np.random.choice(unique_vehicles, max_vehicles, replace=False)
            df = df[df['COMMADDR'].isin(selected_vehicles)]
        
        # 存储所有车辆的轨迹
        all_tracks = []
        
        print(f"🚗 开始处理 {len(df['COMMADDR'].unique())} 个车辆的轨迹...")
        
        # 按车辆ID分组处理
        for i, (veh_id, group) in enumerate(df.groupby('COMMADDR')):
            # 按时间排序
            group = group.sort_values('UTC')
            
            # 提取轨迹点
            track_points = []
            for _, row in group.iterrows():
                # 尝试获取速度字段（可能有不同的名称）
                speed = None
                for speed_field in ['SPEED', 'speed', 'speed_kmh']:
                    if speed_field in row:
                        speed = row[speed_field]
                        break
                
                point = TrackPoint(
                    lat=row['LAT'] / 1e5,
                    lng=row['LON'] / 1e5,
                    timestamp=row['UTC'],
                    speed=speed,
                    direction=row.get('DIRECTION'),
                    status=row.get('STATUS')
                )
                track_points.append(point)
            
            # 计算轨迹距离（简化版，实际应使用Haversine公式）
            distance = None
            if len(track_points) > 1:
                distance = 0
                for i in range(1, len(track_points)):
                    p1, p2 = track_points[i-1], track_points[i]
                    # 使用欧几里得距离作为简化（实际应使用Haversine公式）
                    dist = math.sqrt((p2.lng - p1.lng)**2 + (p2.lat - p1.lat)**2)
                    # 转换为公里（粗略估计）
                    dist_km = dist * 111  # 1度约等于111公里
                    distance += dist_km
            
            # 创建车辆轨迹
            track = VehicleTrack(
                vehicle_id=str(veh_id),  # 确保vehicle_id是字符串类型
                points=track_points,
                start_time=track_points[0].timestamp if track_points else None,
                end_time=track_points[-1].timestamp if track_points else None,
                distance=round(distance, 2) if distance is not None else None
            )
            
            all_tracks.append(track)
        
        return all_tracks
    
    def calculate_statistics(self, df: pd.DataFrame, group_by: str = 'hour') -> Dict[str, Any]:
        """
        计算交通数据统计信息
        
        Args:
            df: 交通数据DataFrame
            group_by: 时间分组方式（hour, day, week, month）
            
        Returns:
            统计信息字典
        """
        if df.empty:
            return {
                'total_vehicles': 0,
                'total_points': 0,
                'active_vehicles': 0,
                'time_span': '0小时',
                'coverage_area': '未知',
                'average_speed': 0,
                'time_distribution': []
            }
        
        # 计算基本统计信息
        total_points = len(df)
        unique_vehicles = df['COMMADDR'].nunique()
        
        # 计算时间跨度
        min_time = df['UTC'].min()
        max_time = df['UTC'].max()
        time_span_hours = (max_time - min_time) / 3600
        time_span = f"{time_span_hours:.1f}小时"
        
        # 计算平均速度（如果有速度列）
        avg_speed = 0
        if 'SPEED' in df.columns:
            avg_speed = df['SPEED'].mean()
        
        # 计算覆盖区域（简化版，实际应计算凸包面积）
        lat_range = df['LAT'].max() - df['LAT'].min()
        lon_range = df['LON'].max() - df['LON'].min()
        coverage_area = '济南市区'  # 简化处理，实际应根据经纬度范围确定
        
        # 时间分布统计
        df['datetime'] = pd.to_datetime(df['UTC'], unit='s')
        
        if group_by == 'hour':
            df['time_group'] = df['datetime'].dt.hour
            group_format = '{:02d}时'
        elif group_by == 'day':
            df['time_group'] = df['datetime'].dt.day
            group_format = '{:02d}日'
        elif group_by == 'week':
            df['time_group'] = df['datetime'].dt.isocalendar().week
            group_format = '第{:02d}周'
        elif group_by == 'month':
            df['time_group'] = df['datetime'].dt.month
            group_format = '{:02d}月'
        else:
            df['time_group'] = df['datetime'].dt.hour
            group_format = '{:02d}时'
        
        # 计算每个时间段的数据点数量
        time_counts = df.groupby('time_group').size()
        
        # 转换为列表格式
        time_distribution = [
            {'time_key': group_format.format(key), 'count': count}
            for key, count in time_counts.items()
        ]
        
        # 返回统计结果
        return {
            'total_vehicles': unique_vehicles,
            'total_points': total_points,
            'active_vehicles': unique_vehicles,
            'time_span': time_span,
            'coverage_area': coverage_area,
            'average_speed': round(avg_speed, 1),
            'time_distribution': time_distribution
        }
    
    def clear_cache(self):
        """清除数据缓存"""
        self._cached_data = {}
        print("数据缓存已清除")
    
    def detect_anomalies(self, df: pd.DataFrame, detection_types: str = "all", thresholds: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        检测交通异常事件
        
        Args:
            df: 交通数据DataFrame
            detection_types: 检测类型（all, long_stop, abnormal_route, speed_anomaly, cluster_anomaly）
            thresholds: 检测阈值参数
            
        Returns:
            异常事件列表
        """
        if df.empty:
            return []
        
        if thresholds is None:
            thresholds = {}
        
        # 默认阈值
        default_thresholds = {
            "long_stop_duration": 300,  # 5分钟
            "speed_threshold_low": 5,   # 低速阈值 km/h
            "speed_threshold_high": 80, # 高速阈值 km/h
            "detour_ratio": 1.5,       # 绕路比例
            "cluster_density": 50,      # 聚集密度
            "stop_distance_threshold": 0.0001  # 停车距离阈值（度）
        }
        thresholds = {**default_thresholds, **thresholds}
        
        anomalies = []
        
        # 根据检测类型调用相应的检测方法
        if detection_types == "all" or "long_stop" in detection_types:
            anomalies.extend(self._detect_long_stops(df, thresholds))
        
        if detection_types == "all" or "speed_anomaly" in detection_types:
            anomalies.extend(self._detect_speed_anomalies(df, thresholds))
        
        if detection_types == "all" or "cluster_anomaly" in detection_types:
            anomalies.extend(self._detect_cluster_anomalies(df, thresholds))
        
        if detection_types == "all" or "abnormal_route" in detection_types:
            anomalies.extend(self._detect_abnormal_routes(df, thresholds))
        
        # 去重和排序
        anomalies = self._deduplicate_anomalies(anomalies)
        anomalies.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        return anomalies
    
    def _detect_long_stops(self, df: pd.DataFrame, thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测长时间停车异常"""
        anomalies = []
        stop_duration_threshold = thresholds.get("long_stop_duration", 300)
        distance_threshold = thresholds.get("stop_distance_threshold", 0.0001)
        
        # 按车辆分组
        for vehicle_id, group in df.groupby('COMMADDR'):
            group = group.sort_values('UTC').reset_index(drop=True)
            
            if len(group) < 2:
                continue
            
            # 计算连续位置的距离和时间差
            for i in range(1, len(group)):
                lat1, lon1 = group.iloc[i-1]['LAT'] / 1e5, group.iloc[i-1]['LON'] / 1e5
                lat2, lon2 = group.iloc[i]['LAT'] / 1e5, group.iloc[i]['LON'] / 1e5
                
                # 计算距离（简化版）
                distance = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
                time_diff = group.iloc[i]['UTC'] - group.iloc[i-1]['UTC']
                
                # 如果距离很小且时间差很大，认为是停车
                if distance < distance_threshold and time_diff > stop_duration_threshold:
                    anomaly = {
                        "id": f"long_stop_{vehicle_id}_{group.iloc[i-1]['UTC']}",
                        "type": "long_stop",
                        "name": "长时间停车",
                        "vehicle_id": str(vehicle_id),
                        "timestamp": group.iloc[i-1]['UTC'],
                        "end_timestamp": group.iloc[i]['UTC'],
                        "duration": time_diff,
                        "latitude": lat1,
                        "longitude": lon1,
                        "severity": self._calculate_severity("long_stop", {"duration": time_diff}),
                        "description": f"车辆 {vehicle_id} 在位置 ({lat1:.4f}, {lon1:.4f}) 停车 {time_diff//60:.0f} 分钟",
                        "details": {
                            "stop_duration": time_diff,
                            "location": f"{lat1:.4f}, {lon1:.4f}",
                            "threshold_used": stop_duration_threshold
                        }
                    }
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_speed_anomalies(self, df: pd.DataFrame, thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测速度异常"""
        anomalies = []
        low_threshold = thresholds.get("speed_threshold_low", 10)
        high_threshold = thresholds.get("speed_threshold_high", 80)
        
        # 如果没有速度列，计算速度
        if 'SPEED' not in df.columns:
            df = self._calculate_speed(df)
        
        # 检测异常速度
        for _, row in df.iterrows():
            speed = row.get('SPEED', 0)
            
            if pd.isna(speed) or speed == 0:
                continue
            
            anomaly_type = None
            severity = "low"
            
            if speed < low_threshold:
                anomaly_type = "low_speed"
                severity = "medium" if speed < 10 else "low"
            elif speed > high_threshold:
                anomaly_type = "high_speed"
                severity = "high" if speed > 100 else "medium"
            
            if anomaly_type:
                anomaly = {
                    "id": f"speed_{anomaly_type}_{row['COMMADDR']}_{row['UTC']}",
                    "type": "speed_anomaly",
                    "name": "异常速度" if anomaly_type == "low_speed" else "超速行驶",
                    "vehicle_id": str(row['COMMADDR']),
                    "timestamp": row['UTC'],
                    "latitude": row['LAT'] / 1e5,
                    "longitude": row['LON'] / 1e5,
                    "severity": severity,
                    "description": f"车辆 {row['COMMADDR']} 速度异常: {speed:.1f} km/h",
                    "details": {
                        "speed": speed,
                        "speed_type": anomaly_type,
                        "thresholds": {"low": low_threshold, "high": high_threshold}
                    }
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_cluster_anomalies(self, df: pd.DataFrame, thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测车辆异常聚集"""
        anomalies = []
        density_threshold = thresholds.get("cluster_density", 50)
        
        # 使用空间网格来检测聚集
        grid_size = 0.005  # 约500米
        df['lat_grid'] = (df['LAT'] / 1e5 / grid_size).round() * grid_size
        df['lng_grid'] = (df['LON'] / 1e5 / grid_size).round() * grid_size
        
        # 按时间窗口和空间网格分组
        time_window = 900  # 15分钟时间窗口
        df['time_window'] = (df['UTC'] / time_window).round() * time_window
        
        cluster_counts = df.groupby(['time_window', 'lat_grid', 'lng_grid']).agg({
            'COMMADDR': 'nunique',  # 唯一车辆数
            'UTC': 'mean'  # 平均时间
        }).reset_index()
        
        cluster_counts.columns = ['time_window', 'lat_grid', 'lng_grid', 'vehicle_count', 'avg_time']
        
        # 找出异常聚集
        abnormal_clusters = cluster_counts[cluster_counts['vehicle_count'] > density_threshold]
        
        for _, cluster in abnormal_clusters.iterrows():
            anomaly = {
                "id": f"cluster_{cluster['time_window']}_{cluster['lat_grid']}_{cluster['lng_grid']}",
                "type": "cluster_anomaly",
                "name": "车辆异常聚集",
                "timestamp": cluster['avg_time'],
                "latitude": cluster['lat_grid'],
                "longitude": cluster['lng_grid'],
                "severity": self._calculate_severity("cluster", {"vehicle_count": cluster['vehicle_count']}),
                "description": f"在位置 ({cluster['lat_grid']:.4f}, {cluster['lng_grid']:.4f}) 发现 {cluster['vehicle_count']} 辆车异常聚集",
                "details": {
                    "vehicle_count": cluster['vehicle_count'],
                    "threshold_used": density_threshold,
                    "time_window": time_window
                }
            }
            anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_abnormal_routes(self, df: pd.DataFrame, thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测异常绕路行为"""
        anomalies = []
        detour_ratio = thresholds.get("detour_ratio", 1.5)
        
        # 按车辆分组检测绕路
        for vehicle_id, group in df.groupby('COMMADDR'):
            group = group.sort_values('UTC').reset_index(drop=True)
            
            if len(group) < 3:
                continue
            
            # 计算轨迹总长度和直线距离
            total_distance = 0
            for i in range(1, len(group)):
                lat1, lon1 = group.iloc[i-1]['LAT'] / 1e5, group.iloc[i-1]['LON'] / 1e5
                lat2, lon2 = group.iloc[i]['LAT'] / 1e5, group.iloc[i]['LON'] / 1e5
                
                # 计算两点间距离
                segment_distance = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # 转换为公里
                total_distance += segment_distance
            
            # 计算起终点直线距离
            start_lat, start_lon = group.iloc[0]['LAT'] / 1e5, group.iloc[0]['LON'] / 1e5
            end_lat, end_lon = group.iloc[-1]['LAT'] / 1e5, group.iloc[-1]['LON'] / 1e5
            straight_distance = math.sqrt((end_lat - start_lat)**2 + (end_lon - start_lon)**2) * 111
            
            # 计算绕路比例
            if straight_distance > 0.1:  # 直线距离大于100米才检测
                actual_ratio = total_distance / straight_distance
                
                if actual_ratio > detour_ratio:
                    anomaly = {
                        "id": f"detour_{vehicle_id}_{group.iloc[0]['UTC']}",
                        "type": "abnormal_route",
                        "name": "异常绕路",
                        "vehicle_id": str(vehicle_id),
                        "timestamp": group.iloc[0]['UTC'],
                        "end_timestamp": group.iloc[-1]['UTC'],
                        "latitude": start_lat,
                        "longitude": start_lon,
                        "severity": self._calculate_severity("detour", {"ratio": actual_ratio}),
                        "description": f"车辆 {vehicle_id} 绕路行驶，实际路径是直线距离的 {actual_ratio:.1f} 倍",
                        "details": {
                            "total_distance": total_distance,
                            "straight_distance": straight_distance,
                            "detour_ratio": actual_ratio,
                            "threshold_used": detour_ratio,
                            "start_location": f"{start_lat:.4f}, {start_lon:.4f}",
                            "end_location": f"{end_lat:.4f}, {end_lon:.4f}"
                        }
                    }
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_speed(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算车辆速度"""
        df = df.copy()
        
        # 如果已经有清洗后的speed_kmh字段，直接使用
        if 'speed_kmh' in df.columns:
            df['SPEED'] = df['speed_kmh']
            return df
        
        # 如果已经有SPEED字段，统一将cm/s转换为km/h
        if 'SPEED' in df.columns:
            df['SPEED'] = df['SPEED'] * 0.036
            return df
        
        # 如果没有合适的速度字段，则通过GPS轨迹计算
        df['SPEED'] = 0.0
        
        for vehicle_id, group in df.groupby('COMMADDR'):
            group = group.sort_values('UTC').reset_index()
            
            for i in range(1, len(group)):
                lat1, lon1 = group.iloc[i-1]['LAT'] / 1e5, group.iloc[i-1]['LON'] / 1e5
                lat2, lon2 = group.iloc[i]['LAT'] / 1e5, group.iloc[i]['LON'] / 1e5
                time_diff = group.iloc[i]['UTC'] - group.iloc[i-1]['UTC']
                
                if time_diff > 0:
                    # 使用Haversine公式计算更准确的距离
                    from geopy.distance import geodesic
                    distance_km = geodesic((lat1, lon1), (lat2, lon2)).kilometers
                    
                    # 计算速度（km/h）
                    speed = distance_km / (time_diff / 3600)
                    
                    # 限制速度在合理范围内（0-150 km/h）
                    speed = max(0, min(speed, 150))
                    
                    df.loc[group.iloc[i]['index'], 'SPEED'] = speed
        
        return df
    
    def _calculate_severity(self, anomaly_type: str, params: Dict[str, Any]) -> str:
        """计算异常严重程度"""
        if anomaly_type == "long_stop":
            duration = params.get("duration", 0)
            if duration > 1800:  # 30分钟
                return "high"
            elif duration > 600:  # 10分钟
                return "medium"
            else:
                return "low"
        
        elif anomaly_type == "cluster":
            count = params.get("vehicle_count", 0)
            if count > 100:
                return "high"
            elif count > 70:
                return "medium"
            else:
                return "low"
        
        elif anomaly_type == "detour":
            ratio = params.get("ratio", 1.0)
            if ratio > 3.0:
                return "high"
            elif ratio > 2.0:
                return "medium"
            else:
                return "low"
        
        return "low"
    
    def _deduplicate_anomalies(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去除重复的异常事件"""
        seen_ids = set()
        unique_anomalies = []
        
        for anomaly in anomalies:
            anomaly_id = anomaly.get("id")
            if anomaly_id not in seen_ids:
                seen_ids.add(anomaly_id)
                unique_anomalies.append(anomaly)
        
        return unique_anomalies
    
    def calculate_anomaly_statistics(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算异常统计信息"""
        if not anomalies:
            return {
                "total_count": 0,
                "by_type": {},
                "by_severity": {"high": 0, "medium": 0, "low": 0},
                "time_distribution": [],
                "top_locations": []
            }
        
        # 按类型统计
        type_counts = {}
        for anomaly in anomalies:
            anomaly_type = anomaly.get("type", "unknown")
            type_counts[anomaly_type] = type_counts.get(anomaly_type, 0) + 1
        
        # 按严重程度统计
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for anomaly in anomalies:
            severity = anomaly.get("severity", "low")
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # 时间分布统计（按小时）
        import pandas as pd
        timestamps = [anomaly.get("timestamp", 0) for anomaly in anomalies]
        df_time = pd.DataFrame({"timestamp": timestamps})
        df_time['datetime'] = pd.to_datetime(df_time['timestamp'], unit='s')
        df_time['hour'] = df_time['datetime'].dt.hour
        
        time_distribution = []
        for hour in range(24):
            count = len(df_time[df_time['hour'] == hour])
            time_distribution.append({"hour": hour, "count": count})
        
        # 热点位置统计
        location_counts = {}
        for anomaly in anomalies:
            lat = anomaly.get("latitude", 0)
            lng = anomaly.get("longitude", 0)
            # 将坐标四舍五入到小数点后3位来聚合
            location_key = f"{lat:.3f},{lng:.3f}"
            if location_key not in location_counts:
                location_counts[location_key] = {"lat": lat, "lng": lng, "count": 0}
            location_counts[location_key]["count"] += 1
        
        # 获取前5个热点位置
        top_locations = sorted(
            location_counts.values(),
            key=lambda x: x["count"],
            reverse=True
        )[:5]
        
        return {
            "total_count": len(anomalies),
            "by_type": type_counts,
            "by_severity": severity_counts,
            "time_distribution": time_distribution,
            "top_locations": top_locations
        }
    
    def generate_anomaly_heatmap(self, anomalies: List[Dict[str, Any]], resolution: float = 0.002) -> List[Dict[str, Any]]:
        """生成异常事件热力图"""
        if not anomalies:
            return []
        
        # 按网格聚合异常事件
        grid_counts = {}
        
        for anomaly in anomalies:
            lat = anomaly.get("latitude", 0)
            lng = anomaly.get("longitude", 0)
            
            # 网格化坐标
            lat_grid = round(lat / resolution) * resolution
            lng_grid = round(lng / resolution) * resolution
            
            grid_key = f"{lat_grid},{lng_grid}"
            if grid_key not in grid_counts:
                grid_counts[grid_key] = {
                    "lat": lat_grid,
                    "lng": lng_grid,
                    "count": 0,
                    "severity_score": 0
                }
            
            grid_counts[grid_key]["count"] += 1
            
            # 计算严重性分数
            severity = anomaly.get("severity", "low")
            severity_score = {"high": 3, "medium": 2, "low": 1}.get(severity, 1)
            grid_counts[grid_key]["severity_score"] += severity_score
        
        # 转换为列表格式
        heatmap_points = []
        for grid_data in grid_counts.values():
            # 计算平均严重性
            avg_severity = grid_data["severity_score"] / grid_data["count"]
            
            heatmap_points.append({
                "lat": grid_data["lat"],
                "lng": grid_data["lng"],
                "count": grid_data["count"],
                "intensity": min(grid_data["count"] * avg_severity, 100)  # 限制最大强度
            })
        
        return heatmap_points
    
    def generate_dynamic_heatmap(
        self, 
        df: pd.DataFrame, 
        temporal_resolution: int = 15,
        spatial_resolution: float = 0.001,
        smoothing: bool = True
    ) -> List[Dict[str, Any]]:
        """
        生成动态热力图数据（时间序列热力图帧）
        
        Args:
            df: 交通数据DataFrame
            temporal_resolution: 时间分辨率（分钟）
            spatial_resolution: 空间分辨率（度）
            smoothing: 是否平滑处理
            
        Returns:
            时间帧列表，每帧包含该时间段的热力图数据
        """
        if df.empty:
            return []
        
        # 确保时间列存在
        if 'UTC' not in df.columns:
            return []
        
        # 计算时间范围
        min_time = df['UTC'].min()
        max_time = df['UTC'].max()
        
        # 创建时间窗口
        time_window_seconds = temporal_resolution * 60
        time_frames = []
        
        current_time = min_time
        while current_time < max_time:
            end_time = current_time + time_window_seconds
            
            # 过滤当前时间窗口的数据
            window_data = df[(df['UTC'] >= current_time) & (df['UTC'] < end_time)]
            
            if not window_data.empty:
                # 生成该时间窗口的热力图
                heatmap_points = self.generate_heatmap_data(window_data, spatial_resolution)
                
                # 计算时间标签
                time_label = f"{datetime.fromtimestamp(current_time).strftime('%H:%M')}-{datetime.fromtimestamp(end_time).strftime('%H:%M')}"
                
                # 计算总强度
                total_intensity = sum(point.count for point in heatmap_points)
                
                frame_data = {
                    "timestamp": current_time,
                    "time_label": time_label,
                    "heatmap_points": [
                        {"lat": point.lat, "lng": point.lng, "intensity": point.count}
                        for point in heatmap_points
                    ],
                    "total_intensity": total_intensity,
                    "point_count": len(heatmap_points)
                }
                
                time_frames.append(frame_data)
            
            current_time = end_time
        
        # 如果需要平滑处理
        if smoothing and len(time_frames) > 2:
            time_frames = self._smooth_temporal_data(time_frames)
        
        return time_frames
    
    def _smooth_temporal_data(self, time_frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对时间序列数据进行平滑处理"""
        # 简单的移动平均平滑
        smoothed_frames = []
        window_size = 3
        
        for i, frame in enumerate(time_frames):
            if i < window_size // 2 or i >= len(time_frames) - window_size // 2:
                # 边界帧不平滑
                smoothed_frames.append(frame)
                continue
            
            # 计算窗口内的平均值
            window_frames = time_frames[i - window_size//2:i + window_size//2 + 1]
            
            # 对热力图点进行平滑
            point_dict = {}
            for w_frame in window_frames:
                for point in w_frame['heatmap_points']:
                    key = f"{point['lat']:.4f},{point['lng']:.4f}"
                    if key not in point_dict:
                        point_dict[key] = {
                            'lat': point['lat'],
                            'lng': point['lng'],
                            'intensities': []
                        }
                    point_dict[key]['intensities'].append(point['intensity'])
            
            # 计算平均强度
            smoothed_points = []
            for point_data in point_dict.values():
                avg_intensity = sum(point_data['intensities']) / len(point_data['intensities'])
                smoothed_points.append({
                    'lat': point_data['lat'],
                    'lng': point_data['lng'],
                    'intensity': avg_intensity
                })
            
            smoothed_frame = frame.copy()
            smoothed_frame['heatmap_points'] = smoothed_points
            smoothed_frame['total_intensity'] = sum(p['intensity'] for p in smoothed_points)
            smoothed_frames.append(smoothed_frame)
        
        return smoothed_frames
    
    def extract_od_pairs_from_data(
        self, 
        df: pd.DataFrame,
        min_trip_duration: int = 60,
        max_trip_duration: int = 7200,
        min_trip_distance: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        从交通数据中提取OD对
        
        Args:
            df: 交通数据DataFrame
            min_trip_duration: 最小行程时间（秒）
            max_trip_duration: 最大行程时间（秒）
            min_trip_distance: 最小行程距离（公里）
            
        Returns:
            OD对列表
        """
        from .od_analysis_engine import ODAnalysisEngine
        
        od_engine = ODAnalysisEngine()
        od_pairs = od_engine.extract_od_pairs(
            df, 
            min_trip_duration=min_trip_duration,
            max_trip_duration=max_trip_duration,
            min_trip_distance=min_trip_distance
        )
        
        return od_pairs
    
    def perform_clustering_analysis(
        self, 
        df: pd.DataFrame,
        data_type: str = "pickup",
        algorithm: str = "dbscan",
        params: Dict[str, Any] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        执行聚类分析
        
        Args:
            df: 交通数据DataFrame
            data_type: 数据类型 ("pickup", "dropoff", "all_points")
            algorithm: 聚类算法
            params: 算法参数
            
        Returns:
            聚类结果和统计信息
        """
        from .clustering_engine import ClusteringEngine
        
        if df.empty:
            return [], {}
        
        # 准备聚类数据
        if data_type == "pickup":
            # 提取起点数据（假设每个车辆的第一个点是起点）
            pickup_data = []
            for vehicle_id, group in df.groupby('COMMADDR'):
                first_point = group.sort_values('UTC').iloc[0]
                pickup_data.append({
                    'lat': first_point['LAT'] / 1e5,
                    'lng': first_point['LON'] / 1e5,
                    'weight': 1.0
                })
            cluster_data = pickup_data
            
        elif data_type == "dropoff":
            # 提取终点数据（假设每个车辆的最后一个点是终点）
            dropoff_data = []
            for vehicle_id, group in df.groupby('COMMADDR'):
                last_point = group.sort_values('UTC').iloc[-1]
                dropoff_data.append({
                    'lat': last_point['LAT'] / 1e5,
                    'lng': last_point['LON'] / 1e5,
                    'weight': 1.0
                })
            cluster_data = dropoff_data
            
        else:  # all_points
            # 使用所有数据点，但进行采样以提高性能
            sample_size = min(10000, len(df))
            sampled_df = df.sample(sample_size) if len(df) > sample_size else df
            
            cluster_data = []
            for _, row in sampled_df.iterrows():
                cluster_data.append({
                    'lat': row['LAT'] / 1e5,
                    'lng': row['LON'] / 1e5,
                    'weight': 1.0
                })
        
        if not cluster_data:
            return [], {}
        
        # 执行聚类
        clustering_engine = ClusteringEngine()
        labels, metrics = clustering_engine.cluster_data(
            cluster_data,
            algorithm=algorithm,
            params=params or {}
        )
        
        # 分析聚类结果
        clusters = clustering_engine.analyze_clusters(
            cluster_data,
            labels,
            cluster_type=data_type
        )
        
        return clusters, metrics
    
    def generate_spatiotemporal_heatmap(
        self, 
        df: pd.DataFrame,
        analysis_type: str = "density",
        temporal_resolution: int = 15,
        spatial_resolution: float = 0.001
    ) -> Dict[str, Any]:
        """
        生成时空热力图分析
        
        Args:
            df: 交通数据DataFrame
            analysis_type: 分析类型 ("density", "speed", "flow")
            temporal_resolution: 时间分辨率（分钟）
            spatial_resolution: 空间分辨率（度）
            
        Returns:
            时空分析结果
        """
        if df.empty:
            return {}
        
        # 生成动态热力图帧
        heatmap_frames = self.generate_dynamic_heatmap(
            df, 
            temporal_resolution=temporal_resolution,
            spatial_resolution=spatial_resolution
        )
        
        # 计算时间序列统计
        time_series_stats = self._calculate_time_series_stats(heatmap_frames)
        
        # 计算空间统计
        spatial_stats = self._calculate_spatial_stats(df)
        
        # 计算空间边界
        spatial_bounds = {
            'min_lat': float(df['LAT'].min() / 1e5),
            'max_lat': float(df['LAT'].max() / 1e5),
            'min_lng': float(df['LON'].min() / 1e5),
            'max_lng': float(df['LON'].max() / 1e5)
        }
        
        # 计算时间范围
        time_range = {
            'start': float(df['UTC'].min()),
            'end': float(df['UTC'].max())
        }
        
        return {
            'analysis_type': analysis_type,
            'time_range': time_range,
            'spatial_bounds': spatial_bounds,
            'heatmap_frames': heatmap_frames,
            'time_series_stats': time_series_stats,
            'spatial_stats': spatial_stats,
            'algorithm_params': {
                'temporal_resolution': temporal_resolution,
                'spatial_resolution': spatial_resolution
            }
        }
    
    def _calculate_time_series_stats(self, frames: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算时间序列统计信息"""
        if not frames:
            return {}
        
        # 提取时间序列数据
        timestamps = [frame['timestamp'] for frame in frames]
        intensities = [frame['total_intensity'] for frame in frames]
        point_counts = [frame['point_count'] for frame in frames]
        
        return {
            'total_frames': len(frames),
            'time_span_hours': (max(timestamps) - min(timestamps)) / 3600,
            'avg_intensity_per_frame': np.mean(intensities),
            'max_intensity': max(intensities),
            'min_intensity': min(intensities),
            'avg_points_per_frame': np.mean(point_counts),
            'intensity_trend': self._calculate_trend(intensities),
            'peak_time': timestamps[intensities.index(max(intensities))] if intensities else None
        }
    
    def _calculate_spatial_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算空间统计信息"""
        if df.empty:
            return {}
        
        # 计算空间分布
        lats = df['LAT'] / 1e5
        lngs = df['LON'] / 1e5
        
        return {
            'spatial_extent_km2': self._calculate_spatial_extent(lats, lngs),
            'centroid_lat': float(lats.mean()),
            'centroid_lng': float(lngs.mean()),
            'lat_std': float(lats.std()),
            'lng_std': float(lngs.std()),
            'total_data_points': len(df),
            'unique_vehicles': df['COMMADDR'].nunique()
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势方向"""
        if len(values) < 2:
            return "stable"
        
        # 简单的线性回归计算趋势
        x = np.arange(len(values))
        y = np.array(values)
        
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_spatial_extent(self, lats: pd.Series, lngs: pd.Series) -> float:
        """计算空间范围（简化为对角线距离）"""
        from geopy.distance import geodesic
        
        try:
            lat_range = (lats.min(), lats.max())
            lng_range = (lngs.min(), lngs.max())
            
            # 计算对角线距离作为空间范围指标
            distance = geodesic(
                (lat_range[0], lng_range[0]),
                (lat_range[1], lng_range[1])
            ).kilometers
            
            return round(distance, 2)
        except:
            return 0.0

    # 路段分析相关方法
    
    def analyze_road_segments(
        self, 
        df: pd.DataFrame,
        analysis_type: str = "comprehensive",
        segment_types: List[str] = ["all"],
        aggregation_level: str = "segment",
        min_vehicles: int = 1
    ) -> Dict[str, Any]:
        """
        分析路段数据 - 使用预定义路网数据
        
        Args:
            df: 轨迹数据DataFrame
            analysis_type: 分析类型 (comprehensive, speed, flow, congestion)
            segment_types: 路段类型过滤 (highway, urban, arterial, local, all)
            aggregation_level: 聚合级别 (segment, road, network)
            min_vehicles: 最小车辆数阈值
            
        Returns:
            路段分析结果字典
        """
        try:
            from .road_analysis_engine import RoadAnalysisEngine
            from .models import RoadSegmentStatistics
            
            if df.empty:
                return {"error": "数据为空"}
            
            # 标准化数据列名
            df = self._standardize_dataframe(df)
            
            # 初始化路段分析引擎
            road_engine = RoadAnalysisEngine()
            
            # 从预定义路网文件加载路段信息，而不是从轨迹动态提取
            print("加载预定义路网数据...")
            road_segments = road_engine.load_road_network()
            
            if not road_segments:
                return {"error": "无法加载路网数据"}
            
            print(f"成功加载 {len(road_segments)} 个路段")
            
            # 分析路段交通数据
            print("分析路段交通数据...")
            traffic_data = road_engine.analyze_road_traffic(df, road_segments)
            
            if not traffic_data:
                return {"error": "无法分析交通数据"}
            
            # 应用车辆数量过滤
            filtered_traffic_data = [
                data for data in traffic_data 
                if data.vehicle_count >= min_vehicles
            ]
            
            if not filtered_traffic_data:
                return {"error": f"没有满足最小车辆数({min_vehicles})的路段数据"}
            
            # 计算时间范围
            timestamps = [data.timestamp for data in filtered_traffic_data]
            time_range = {"start": min(timestamps), "end": max(timestamps)}
            
            # 计算路段统计
            print("计算路段统计...")
            segment_stats = road_engine.calculate_segment_statistics(filtered_traffic_data, (time_range["start"], time_range["end"]))
            
            # 构建符合Pydantic模型要求的segments_data格式
            segments_data = []
            for stats in segment_stats:
                # 将RoadSegmentStatistics对象转换为字典，确保包含所有必需字段
                segment_data = {
                    "segment_id": stats.segment_id,
                    "time_period": stats.time_period,
                    "total_vehicles": stats.total_vehicles,
                    "avg_speed": stats.avg_speed,
                    "speed_variance": stats.speed_variance,
                    "peak_hour_flow": stats.peak_hour_flow,
                    "off_peak_flow": stats.off_peak_flow,
                    "congestion_hours": stats.congestion_hours,
                    "free_flow_speed": stats.free_flow_speed,
                    "capacity_utilization": stats.capacity_utilization,
                    "efficiency_score": stats.efficiency_score
                }
                segments_data.append(segment_data)
            
            # 构建符合前端期望的简化segments格式（用于可视化）
            segments_for_display = []
            matched_count = 0
            
            print(f"🔍 开始匹配路段，segment_stats数量: {len(segment_stats)}")
            print(f"🔍 路网路段数量: {len(road_segments)}")
            
            # 创建路段ID映射以提高查找效率
            road_segment_map = {seg.segment_id: seg for seg in road_segments}
            print(f"🔍 路段ID映射创建完成，包含 {len(road_segment_map)} 个路段")
            
            # 检查ID格式示例
            if segment_stats:
                print(f"🔍 统计数据ID示例: '{segment_stats[0].segment_id}' (类型: {type(segment_stats[0].segment_id)})")
            if road_segments:
                print(f"🔍 路网数据ID示例: '{road_segments[0].segment_id}' (类型: {type(road_segments[0].segment_id)})")
            
            for stats in segment_stats:
                # 找到对应的路段几何信息
                road_segment = road_segment_map.get(stats.segment_id)
                
                if road_segment:
                    matched_count += 1
                    # 计算实际流量：选择峰值和非峰值中的较大值作为代表性流量
                    actual_flow_rate = max(stats.peak_hour_flow, stats.off_peak_flow)
                    
                    segment_display = {
                        "segment_id": stats.segment_id,
                        "avg_speed": stats.avg_speed,
                        "flow_rate": actual_flow_rate,
                        "congestion_level": self._calculate_congestion_level_from_stats(stats),
                        "segment_length": road_segment.segment_length,
                        "road_type": road_segment.road_type,
                        "vehicle_count": stats.total_vehicles,
                        "efficiency_score": stats.efficiency_score,
                        "start_point": road_segment.start_point,
                        "end_point": road_segment.end_point
                    }
                    segments_for_display.append(segment_display)
                else:
                    print(f"⚠️ 未找到路段几何信息: {stats.segment_id}")
                    # 即使没有找到几何信息，也创建一个默认的可视化数据
                    segment_display = {
                        "segment_id": stats.segment_id,
                        "avg_speed": stats.avg_speed,
                        "flow_rate": stats.peak_hour_flow,
                        "congestion_level": self._calculate_congestion_level_from_stats(stats),
                        "segment_length": 0.5,  # 默认长度
                        "road_type": "urban",    # 默认类型
                        "vehicle_count": stats.total_vehicles,
                        "efficiency_score": stats.efficiency_score,
                        "start_point": {"lat": 36.67, "lng": 117.02},  # 济南市中心默认坐标
                        "end_point": {"lat": 36.67 + 0.001, "lng": 117.02 + 0.001}  # 略微偏移的终点
                    }
                    segments_for_display.append(segment_display)
            
            print(f"✅ 路段匹配完成: 成功匹配 {matched_count}/{len(segment_stats)} 个路段")
            print(f"✅ 生成可视化数据: {len(segments_for_display)} 个路段")
            
            # 调试：打印segments_for_display的内容
            print(f"🔍 segments_for_display内容预览:")
            for i, seg in enumerate(segments_for_display[:3]):  # 只打印前3个
                print(f"  路段 {i}: ID={seg.get('segment_id')}, 起点={seg.get('start_point')}, 终点={seg.get('end_point')}")
            
            # 计算网络摘要
            network_summary = road_engine.generate_network_summary(segment_stats, filtered_traffic_data)
            
            # 识别瓶颈路段
            bottleneck_segments = road_engine.identify_bottlenecks(segment_stats)
            
            # 分析结果
            result = {
                "success": True,
                "total_segments": len(road_segments),
                "segments_data": segments_data,  # 符合Pydantic模型的数据结构
                "segments": segments_for_display,  # 符合前端期望的格式（保持向后兼容）
                "network_summary": network_summary,
                "bottleneck_segments": bottleneck_segments,
                "analysis_metadata": {
                    "analysis_type": analysis_type,
                    "segment_types": segment_types,
                    "aggregation_level": aggregation_level,
                    "min_vehicles": min_vehicles,
                    "time_range": time_range,
                    "active_segments": len(filtered_traffic_data),
                    "analysis_timestamp": time.time()
                }
            }
            
            # 调试：验证result中的segments字段
            print(f"🔍 result构建完成:")
            print(f"  segments_data数量: {len(result.get('segments_data', []))}")
            print(f"  segments数量: {len(result.get('segments', []))}")
            print(f"  第一个segment: {result.get('segments', [{}])[0] if result.get('segments') else 'None'}")
            
            # 根据分析类型添加特定分析
            if analysis_type in ["comprehensive", "speed"]:
                # 使用最终的路段统计数据来计算速度分布，而不是原始的traffic_data
                # 从segments_data中提取速度信息来计算分布
                speed_data_for_distribution = []
                for segment in segments_data:
                    # 创建一个模拟的RoadTrafficData对象用于分布计算
                    from .models import RoadTrafficData
                    
                    # 获取路段的速度统计信息
                    avg_speed = float(segment.get('avg_speed', 0.0))
                    vehicle_count = int(segment.get('vehicle_count', 0))
                    
                    # 估算min_speed和max_speed（基于avg_speed和一些合理的变化范围）
                    speed_variance = avg_speed * 0.3  # 假设速度变化范围为平均速度的30%
                    min_speed = max(0.0, avg_speed - speed_variance)
                    max_speed = avg_speed + speed_variance
                    
                    # 估算traffic_density（基于vehicle_count和路段特征）
                    segment_length = float(segment.get('length', 1.0))  # 默认1公里
                    traffic_density = vehicle_count / segment_length if segment_length > 0 else 0.0
                    
                    mock_traffic_data = RoadTrafficData(
                        segment_id=str(segment.get('segment_id', '')),
                        timestamp=int(time.time()),
                        vehicle_count=vehicle_count,
                        avg_speed=avg_speed,
                        min_speed=float(min_speed),
                        max_speed=float(max_speed),
                        traffic_density=float(traffic_density),
                        flow_rate=float(segment.get('flow_rate', 0.0)),
                        congestion_level=str(segment.get('congestion_level', 'unknown'))
                    )
                    speed_data_for_distribution.append(mock_traffic_data)
                
                speed_distributions = road_engine.analyze_speed_distribution(speed_data_for_distribution)
                result["speed_distributions"] = [dist.dict() for dist in speed_distributions]
            
            if analysis_type in ["comprehensive", "flow"]:
                # 同样使用最终的路段数据
                flow_data_for_patterns = []
                for segment in segments_data:
                    from .models import RoadTrafficData
                    
                    avg_speed = float(segment.get('avg_speed', 0.0))
                    vehicle_count = int(segment.get('vehicle_count', 0))
                    segment_length = float(segment.get('length', 1.0))
                    
                    speed_variance = avg_speed * 0.3
                    min_speed = max(0.0, avg_speed - speed_variance)
                    max_speed = avg_speed + speed_variance
                    traffic_density = vehicle_count / segment_length if segment_length > 0 else 0.0
                    
                    mock_traffic_data = RoadTrafficData(
                        segment_id=str(segment.get('segment_id', '')),
                        timestamp=int(time.time()),
                        vehicle_count=vehicle_count,
                        avg_speed=avg_speed,
                        min_speed=float(min_speed),
                        max_speed=float(max_speed),
                        traffic_density=float(traffic_density),
                        flow_rate=float(segment.get('flow_rate', 0.0)),
                        congestion_level=str(segment.get('congestion_level', 'unknown'))
                    )
                    flow_data_for_patterns.append(mock_traffic_data)
                
                flow_patterns = road_engine.analyze_traffic_patterns(flow_data_for_patterns)
                result["flow_patterns"] = [pattern.dict() for pattern in flow_patterns]
            
            return result
            
        except Exception as e:
            import traceback
            print(f"分析失败详细信息: {traceback.format_exc()}")
            return {"error": f"分析失败: {str(e)}"}

    def _calculate_congestion_level_from_stats(self, stats) -> str:
        """根据统计数据计算拥堵等级"""
        if stats.efficiency_score >= 80:
            return "free"
        elif stats.efficiency_score >= 60:
            return "moderate"
        elif stats.efficiency_score >= 40:
            return "heavy"
        else:
            return "jam"
    
    def generate_road_visualization_data(
        self, 
        segments_data: List[Any],
        traffic_data: List[Dict],
        visualization_type: str = "speed"
    ) -> Dict[str, Any]:
        """
        生成道路可视化数据
        
        Args:
            segments_data: 路段数据列表（可以是字典或RoadSegment对象）
            traffic_data: 交通数据列表
            visualization_type: 可视化类型：speed（速度）, flow（流量）, congestion（拥堵）, efficiency（效率）
            
        Returns:
            包含可视化数据的字典
        """
        try:
            start_time = time.time()
            result = {
                "segment_colors": {},
                "legend_info": self._get_visualization_legend(visualization_type),
                "segments": []  # 添加路段几何数据列表，用于前端渲染
            }
            
            # 如果没有交通数据，返回空结果
            if not traffic_data:
                logger.warning("没有交通数据，无法生成可视化")
                return result
            
            # 创建交通数据的映射，便于快速查找
            traffic_map = {}
            for data in traffic_data:
                # 支持dict或RoadTrafficData对象
                segment_id = data.segment_id if hasattr(data, 'segment_id') else data.get('segment_id')
                if segment_id:
                    traffic_map[segment_id] = data
            
            logger.info(f"处理 {len(segments_data)} 个路段的可视化数据...")
            
            # 处理每个路段
            for segment in segments_data:
                # 支持dict或RoadSegment对象
                if hasattr(segment, 'segment_id'):
                    segment_id = segment.segment_id
                else:
                    segment_id = segment.get('segment_id')
                
                if not segment_id:
                    continue
                
                # 获取该路段的交通数据
                traffic_info = traffic_map.get(segment_id)
                if not traffic_info:
                    continue
                
                # 根据可视化类型确定颜色
                if visualization_type == "speed":
                    # 获取平均速度
                    if hasattr(traffic_info, 'avg_speed'):
                        avg_speed = traffic_info.avg_speed
                    else:
                        avg_speed = traffic_info.get('avg_speed', 0)
                    color = self._get_speed_color(avg_speed)
                    
                elif visualization_type == "flow":
                    # 获取流量
                    if hasattr(traffic_info, 'flow_rate'):
                        flow_rate = traffic_info.flow_rate
                    else:
                        flow_rate = traffic_info.get('flow_rate', 0)
                    color = self._get_flow_color(flow_rate)
                    
                elif visualization_type == "congestion":
                    # 获取拥堵级别
                    if hasattr(traffic_info, 'congestion_level'):
                        congestion_level = traffic_info.congestion_level
                    else:
                        congestion_level = traffic_info.get('congestion_level', 'free')
                    
                    # 将拥堵级别映射为数值
                    congestion_map = {"free": 0, "moderate": 0.33, "heavy": 0.67, "jam": 1.0}
                    congestion_score = congestion_map.get(congestion_level, 0)
                    color = self._get_congestion_color(congestion_score)
                    
                elif visualization_type == "efficiency":
                    # 获取效率评分
                    if hasattr(traffic_info, 'efficiency_score'):
                        efficiency = traffic_info.efficiency_score
                    else:
                        efficiency = traffic_info.get('efficiency_score', 80)
                    color = self._get_efficiency_color(efficiency)
                    
                else:
                    # 默认为灰色
                    color = "#888888"
                
                # 将颜色添加到结果中
                result["segment_colors"][segment_id] = color
                
                # 构建路段几何数据，用于前端地图渲染
                segment_geometry = {}
                
                # 提取路段起点和终点
                if hasattr(segment, 'start_point') and hasattr(segment, 'end_point'):
                    # RoadSegment对象
                    segment_geometry = {
                        "id": segment_id,
                        "start": {
                            "lat": segment.start_point.get('lat', 0) if isinstance(segment.start_point, dict) else segment.start_point.lat,
                            "lng": segment.start_point.get('lng', 0) if isinstance(segment.start_point, dict) else segment.start_point.lng
                        },
                        "end": {
                            "lat": segment.end_point.get('lat', 0) if isinstance(segment.end_point, dict) else segment.end_point.lat,
                            "lng": segment.end_point.get('lng', 0) if isinstance(segment.end_point, dict) else segment.end_point.lng
                        },
                        "road_type": segment.road_type if hasattr(segment, 'road_type') else "unknown",
                    }
                elif isinstance(segment, dict):
                    # 字典对象
                    start_point = segment.get('start_point', {})
                    end_point = segment.get('end_point', {})
                    
                    segment_geometry = {
                        "id": segment_id,
                        "start": {
                            "lat": start_point.get('lat', 0),
                            "lng": start_point.get('lng', 0)
                        },
                        "end": {
                            "lat": end_point.get('lat', 0),
                            "lng": end_point.get('lng', 0)
                        },
                        "road_type": segment.get('road_type', "unknown"),
                    }
                
                # 添加可视化特定属性
                if visualization_type == "speed":
                    if hasattr(traffic_info, 'avg_speed'):
                        segment_geometry["avg_speed"] = traffic_info.avg_speed
                    else:
                        segment_geometry["avg_speed"] = traffic_info.get('avg_speed', 0)
                        
                elif visualization_type == "flow":
                    if hasattr(traffic_info, 'flow_rate'):
                        segment_geometry["flow"] = traffic_info.flow_rate
                    else:
                        segment_geometry["flow"] = traffic_info.get('flow_rate', 0)
                        
                elif visualization_type == "congestion":
                    if hasattr(traffic_info, 'congestion_level'):
                        segment_geometry["congestion_level"] = traffic_info.congestion_level
                    else:
                        segment_geometry["congestion_level"] = traffic_info.get('congestion_level', 'free')
                    segment_geometry["congestion_score"] = congestion_score
                    
                elif visualization_type == "efficiency":
                    segment_geometry["efficiency"] = efficiency
                
                # 添加到结果的路段列表中
                result["segments"].append(segment_geometry)
            
            processing_time = time.time() - start_time
            logger.info(f"道路可视化数据生成完成，处理了 {len(result['segments'])} 个路段，耗时 {processing_time:.2f} 秒")
            
            return result
            
        except Exception as e:
            logger.error(f"生成可视化数据时出错: {str(e)}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            return {
                "segment_colors": {},
                "legend_info": {},
                "segments": [],
                "error": str(e)
            }
    
    def _get_visualization_legend(self, viz_type: str) -> Dict[str, Any]:
        """获取可视化图例信息"""
        legends = {
            "speed": {
                "title": "平均速度 (km/h)",
                "ranges": [
                    {"color": "#d73027", "label": "< 20", "range": [0, 20]},
                    {"color": "#fc8d59", "label": "20-40", "range": [20, 40]},
                    {"color": "#fee08b", "label": "40-60", "range": [40, 60]},
                    {"color": "#d9ef8b", "label": "60-80", "range": [60, 80]},
                    {"color": "#91d1c2", "label": "> 80", "range": [80, 999]}
                ]
            },
            "flow": {
                "title": "交通流量 (vehicles/h)",
                "ranges": [
                    {"color": "#2c7fb8", "label": "< 100", "range": [0, 100]},
                    {"color": "#7fcdbb", "label": "100-300", "range": [100, 300]},
                    {"color": "#c7e9b4", "label": "300-500", "range": [300, 500]},
                    {"color": "#fec44f", "label": "500-800", "range": [500, 800]},
                    {"color": "#d95f0e", "label": "> 800", "range": [800, 9999]}
                ]
            },
            "congestion": {
                "title": "拥堵程度",
                "ranges": [
                    {"color": "#1a9850", "label": "畅通", "range": [0, 0.3]},
                    {"color": "#91d1c2", "label": "缓慢", "range": [0.3, 0.6]},
                    {"color": "#fee08b", "label": "拥堵", "range": [0.6, 0.8]},
                    {"color": "#d73027", "label": "严重拥堵", "range": [0.8, 1.0]}
                ]
            },
            "efficiency": {
                "title": "运行效率",
                "ranges": [
                    {"color": "#d73027", "label": "很低", "range": [0, 30]},
                    {"color": "#fc8d59", "label": "较低", "range": [30, 50]},
                    {"color": "#fee08b", "label": "中等", "range": [50, 70]},
                    {"color": "#d9ef8b", "label": "较高", "range": [70, 85]},
                    {"color": "#1a9850", "label": "很高", "range": [85, 100]}
                ]
            }
        }
        return legends.get(viz_type, {"title": "未知", "ranges": []})
    
    def _get_speed_color(self, speed: float) -> str:
        """根据速度获取颜色"""
        if speed < 20:
            return "#d73027"
        elif speed < 40:
            return "#fc8d59"
        elif speed < 60:
            return "#fee08b"
        elif speed < 80:
            return "#d9ef8b"
        else:
            return "#91d1c2"
    
    def _get_flow_color(self, flow: float) -> str:
        """根据流量获取颜色"""
        if flow < 100:
            return "#2c7fb8"
        elif flow < 300:
            return "#7fcdbb"
        elif flow < 500:
            return "#c7e9b4"
        elif flow < 800:
            return "#fec44f"
        else:
            return "#d95f0e"
    
    def _get_congestion_color(self, congestion_score: float) -> str:
        """根据拥堵分数获取颜色"""
        if congestion_score < 0.3:
            return "#1a9850"  # 绿色 - 畅通
        elif congestion_score < 0.6:
            return "#91d1c2"  # 浅绿 - 缓慢
        elif congestion_score < 0.8:
            return "#fee08b"  # 黄色 - 拥堵
        else:
            return "#d73027"  # 红色 - 严重拥堵
    
    def _get_efficiency_color(self, efficiency: float) -> str:
        """根据效率分数获取颜色"""
        if efficiency < 30:
            return "#d73027"
        elif efficiency < 50:
            return "#fc8d59"
        elif efficiency < 70:
            return "#fee08b"
        elif efficiency < 85:
            return "#d9ef8b"
        else:
            return "#1a9850"
    
    def _calculate_congestion_score(self, congestion_levels: List[str]) -> float:
        """计算拥堵分数"""
        if not congestion_levels:
            return 0.0
        
        level_scores = {
            'free': 0.1,
            'moderate': 0.4,
            'heavy': 0.7,
            'jam': 0.9
        }
        
        total_score = sum(level_scores.get(level, 0.1) for level in congestion_levels)
        return total_score / len(congestion_levels)
    
    def calculate_road_network_metrics(
        self, 
        segments_data: List[Dict],
        traffic_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        计算路网整体指标
        
        Args:
            segments_data: 路段数据
            traffic_data: 交通数据
            
        Returns:
            路网指标字典
        """
        try:
            if not segments_data or not traffic_data:
                return {"error": "数据不足"}
            
            # 基础统计
            total_segments = len(segments_data)
            total_length = sum(s.get('segment_length', 0) for s in segments_data)
            
            # 交通指标
            speeds = [t.get('avg_speed', 0) for t in traffic_data]
            flows = [t.get('flow_rate', 0) for t in traffic_data]
            densities = [t.get('traffic_density', 0) for t in traffic_data]
            
            # 拥堵分析
            congestion_counts = {}
            for t in traffic_data:
                level = t.get('congestion_level', 'free')
                congestion_counts[level] = congestion_counts.get(level, 0) + 1
            
            # 道路类型分布
            road_type_counts = {}
            for s in segments_data:
                road_type = s.get('road_type', 'unknown')
                road_type_counts[road_type] = road_type_counts.get(road_type, 0) + 1
            
            metrics = {
                "network_overview": {
                    "total_segments": total_segments,
                    "total_length_km": round(total_length, 2),
                    "avg_segment_length": round(total_length / total_segments, 3) if total_segments > 0 else 0,
                    "active_segments": len(traffic_data)
                },
                "traffic_performance": {
                    "avg_speed": round(np.mean(speeds), 2) if speeds else 0,
                    "min_speed": round(min(speeds), 2) if speeds else 0,
                    "max_speed": round(max(speeds), 2) if speeds else 0,
                    "speed_variance": round(np.var(speeds), 2) if len(speeds) > 1 else 0,
                    "avg_flow": round(np.mean(flows), 2) if flows else 0,
                    "max_flow": round(max(flows), 2) if flows else 0,
                    "avg_density": round(np.mean(densities), 2) if densities else 0
                },
                "congestion_analysis": {
                    "congestion_distribution": congestion_counts,
                    "congestion_rate": {
                        level: round(count / len(traffic_data) * 100, 1) 
                        for level, count in congestion_counts.items()
                    } if traffic_data else {},
                    "total_congested_segments": congestion_counts.get('heavy', 0) + congestion_counts.get('jam', 0)
                },
                "road_infrastructure": {
                    "road_type_distribution": road_type_counts,
                    "road_type_percentage": {
                        road_type: round(count / total_segments * 100, 1)
                        for road_type, count in road_type_counts.items()
                    } if total_segments > 0 else {}
                },
                "efficiency_indicators": {
                    "network_utilization": round(len(traffic_data) / total_segments * 100, 1) if total_segments > 0 else 0,
                    "free_flow_percentage": round(congestion_counts.get('free', 0) / len(traffic_data) * 100, 1) if traffic_data else 0,
                    "bottleneck_rate": round((congestion_counts.get('heavy', 0) + congestion_counts.get('jam', 0)) / len(traffic_data) * 100, 1) if traffic_data else 0
                }
            }
            
            return metrics
            
        except Exception as e:
            print(f"计算路网指标时出错: {str(e)}")
            return {"error": f"计算失败: {str(e)}"}
    
    def analyze_weekly_passenger_flow(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        分析周客流量数据
        
        Args:
            df: 交通数据DataFrame
            
        Returns:
            周客流量分析结果
        """
        if df.empty:
            return {
                'success': False,
                'message': '没有可用数据',
                'weekly_flow': {},
                'comparison': {},
                'patterns': {},
                'statistics': {}
            }
        
        try:
            # 标准化DataFrame列名
            df = self._standardize_dataframe(df)
            
            # 添加时间相关列
            df['datetime'] = pd.to_datetime(df['UTC'], unit='s')
            df['weekday'] = df['datetime'].dt.weekday  # 0=Monday, 6=Sunday
            df['hour'] = df['datetime'].dt.hour
            df['date'] = df['datetime'].dt.date
            df['week'] = df['datetime'].dt.isocalendar().week
            
            # 1. 每日客流量统计
            daily_flow = self._calculate_daily_passenger_flow(df)
            
            # 2. 工作日vs周末对比
            weekday_comparison = self._calculate_weekday_weekend_comparison(df)
            
            # 3. 一周内各天的流量模式
            weekly_patterns = self._calculate_weekly_patterns(df)
            
            # 4. 小时级流量分布（按工作日/周末分组）
            hourly_patterns = self._calculate_hourly_patterns_by_day_type(df)
            
            # 5. 客流量趋势分析
            flow_trends = self._calculate_weekly_flow_trends(df)
            
            # 6. 高峰时段分析
            peak_analysis = self._analyze_weekly_peak_periods(df)
            
            # 7. 综合统计信息
            weekly_statistics = self._calculate_weekly_statistics(df)
            
            return {
                'success': True,
                'message': '周客流量分析完成',
                'daily_flow': daily_flow,
                'weekday_comparison': weekday_comparison,
                'weekly_patterns': weekly_patterns,
                'hourly_patterns': hourly_patterns,
                'flow_trends': flow_trends,
                'peak_analysis': peak_analysis,
                'statistics': weekly_statistics,
                'analysis_period': {
                    'start_date': str(df['date'].min()),
                    'end_date': str(df['date'].max()),
                    'total_days': df['date'].nunique(),
                    'total_weeks': df['week'].nunique()
                }
            }
        
        except Exception as e:
            logging.error(f"周客流量分析失败: {str(e)}")
            return {
                'success': False,
                'message': f'分析失败: {str(e)}',
                'weekly_flow': {},
                'comparison': {},
                'patterns': {},
                'statistics': {}
            }
    
    def _calculate_daily_passenger_flow(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算每日客流量"""
        # 按日期分组计算车辆数和轨迹点数
        daily_stats = df.groupby('date').agg({
            'COMMADDR': 'nunique',  # 独立车辆数
            'UTC': 'count'          # 轨迹点数
        }).reset_index()
        
        daily_stats.columns = ['date', 'vehicles', 'total_points']
        daily_stats['date'] = daily_stats['date'].astype(str)
        
        # 添加星期信息
        daily_stats['weekday'] = pd.to_datetime(daily_stats['date']).dt.weekday
        daily_stats['weekday_name'] = pd.to_datetime(daily_stats['date']).dt.day_name()
        daily_stats['is_weekend'] = daily_stats['weekday'].isin([5, 6])
        
        return {
            'daily_data': daily_stats.to_dict('records'),
            'total_days': len(daily_stats),
            'avg_daily_vehicles': daily_stats['vehicles'].mean(),
            'max_daily_vehicles': daily_stats['vehicles'].max(),
            'min_daily_vehicles': daily_stats['vehicles'].min()
        }
    
    def _calculate_weekday_weekend_comparison(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算工作日vs周末对比"""
        df['is_weekend'] = df['weekday'].isin([5, 6])
        
        # 按工作日/周末分组统计
        comparison = df.groupby(['date', 'is_weekend']).agg({
            'COMMADDR': 'nunique',
            'UTC': 'count'
        }).reset_index()
        
        weekday_data = comparison[comparison['is_weekend'] == False]['COMMADDR']
        weekend_data = comparison[comparison['is_weekend'] == True]['COMMADDR']
        
        weekday_avg = weekday_data.mean() if len(weekday_data) > 0 else 0
        weekend_avg = weekend_data.mean() if len(weekend_data) > 0 else 0
        
        # 计算差异百分比
        if weekday_avg > 0:
            difference_pct = ((weekend_avg - weekday_avg) / weekday_avg) * 100
        else:
            difference_pct = 0
        
        return {
            'weekday_avg': round(weekday_avg, 1),
            'weekend_avg': round(weekend_avg, 1),
            'difference_pct': round(difference_pct, 1),
            'weekday_days': len(weekday_data),
            'weekend_days': len(weekend_data),
            'pattern': 'weekend_higher' if weekend_avg > weekday_avg else 'weekday_higher'
        }
    
    def _calculate_weekly_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算一周内各天的流量模式"""
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        # 按星期分组统计
        weekly_flow = df.groupby(['date', 'weekday']).agg({
            'COMMADDR': 'nunique',
            'UTC': 'count'
        }).reset_index()
        
        # 计算每个星期几的平均流量
        avg_by_weekday = weekly_flow.groupby('weekday')['COMMADDR'].mean().reset_index()
        avg_by_weekday['weekday_name'] = [weekday_names[i] for i in avg_by_weekday['weekday']]
        
        # 找出最高和最低流量的天
        max_day = avg_by_weekday.loc[avg_by_weekday['COMMADDR'].idxmax()]
        min_day = avg_by_weekday.loc[avg_by_weekday['COMMADDR'].idxmin()]
        
        return {
            'weekly_data': avg_by_weekday.to_dict('records'),
            'peak_day': {
                'day': max_day['weekday_name'],
                'vehicles': round(max_day['COMMADDR'], 1)
            },
            'lowest_day': {
                'day': min_day['weekday_name'],
                'vehicles': round(min_day['COMMADDR'], 1)
            },
            'weekly_variance': round(avg_by_weekday['COMMADDR'].var(), 2)
        }
    
    def _calculate_hourly_patterns_by_day_type(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算按工作日/周末分组的小时流量模式"""
        df['is_weekend'] = df['weekday'].isin([5, 6])
        df['day_type'] = df['is_weekend'].map({True: '周末', False: '工作日'})
        
        # 按小时和日期类型分组
        hourly_patterns = df.groupby(['day_type', 'hour', 'date']).agg({
            'COMMADDR': 'nunique'
        }).reset_index()
        
        # 计算每小时的平均流量
        hourly_avg = hourly_patterns.groupby(['day_type', 'hour'])['COMMADDR'].mean().reset_index()
        
        # 分离工作日和周末数据
        weekday_hourly = hourly_avg[hourly_avg['day_type'] == '工作日']
        weekend_hourly = hourly_avg[hourly_avg['day_type'] == '周末']
        
        # 找出高峰时段
        weekday_peak_hour = weekday_hourly.loc[weekday_hourly['COMMADDR'].idxmax(), 'hour'] if len(weekday_hourly) > 0 else 0
        weekend_peak_hour = weekend_hourly.loc[weekend_hourly['COMMADDR'].idxmax(), 'hour'] if len(weekend_hourly) > 0 else 0
        
        return {
            'hourly_data': hourly_avg.to_dict('records'),
            'weekday_pattern': weekday_hourly.to_dict('records'),
            'weekend_pattern': weekend_hourly.to_dict('records'),
            'peak_hours': {
                'weekday': int(weekday_peak_hour),
                'weekend': int(weekend_peak_hour)
            }
        }
    
    def _calculate_weekly_flow_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算周客流量趋势"""
        # 按周统计
        weekly_trends = df.groupby(['week', 'date']).agg({
            'COMMADDR': 'nunique'
        }).reset_index()
        
        # 按周聚合
        weekly_summary = weekly_trends.groupby('week').agg({
            'COMMADDR': ['mean', 'sum', 'count']
        }).reset_index()
        
        weekly_summary.columns = ['week', 'avg_daily_vehicles', 'total_vehicles', 'days_count']
        
        # 计算趋势
        if len(weekly_summary) > 1:
            trend_slope = np.polyfit(range(len(weekly_summary)), weekly_summary['avg_daily_vehicles'], 1)[0]
            trend_direction = 'increasing' if trend_slope > 0 else 'decreasing'
        else:
            trend_slope = 0
            trend_direction = 'stable'
        
        return {
            'weekly_summary': weekly_summary.to_dict('records'),
            'trend_analysis': {
                'slope': round(trend_slope, 2),
                'direction': trend_direction,
                'total_weeks': len(weekly_summary)
            }
        }
    
    def _analyze_weekly_peak_periods(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析周高峰时段"""
        df['is_weekend'] = df['weekday'].isin([5, 6])
        
        # 定义时段
        def get_time_period(hour):
            if 6 <= hour < 9:
                return '早高峰'
            elif 17 <= hour < 20:
                return '晚高峰'
            elif 9 <= hour < 17:
                return '日间'
            else:
                return '夜间'
        
        df['time_period'] = df['hour'].apply(get_time_period)
        
        # 按时段和日期类型统计
        period_stats = df.groupby(['is_weekend', 'time_period', 'date']).agg({
            'COMMADDR': 'nunique'
        }).reset_index()
        
        period_avg = period_stats.groupby(['is_weekend', 'time_period'])['COMMADDR'].mean().reset_index()
        period_avg['day_type'] = period_avg['is_weekend'].map({True: '周末', False: '工作日'})
        
        return {
            'period_analysis': period_avg.to_dict('records'),
            'peak_periods': self._identify_peak_periods(period_avg)
        }
    
    def _identify_peak_periods(self, period_avg: pd.DataFrame) -> Dict[str, Any]:
        """识别高峰时段"""
        weekday_data = period_avg[period_avg['is_weekend'] == False]
        weekend_data = period_avg[period_avg['is_weekend'] == True]
        
        weekday_peak = weekday_data.loc[weekday_data['COMMADDR'].idxmax()] if len(weekday_data) > 0 else None
        weekend_peak = weekend_data.loc[weekend_data['COMMADDR'].idxmax()] if len(weekend_data) > 0 else None
        
        return {
            'weekday_peak': {
                'period': weekday_peak['time_period'] if weekday_peak is not None else 'N/A',
                'vehicles': round(weekday_peak['COMMADDR'], 1) if weekday_peak is not None else 0
            },
            'weekend_peak': {
                'period': weekend_peak['time_period'] if weekend_peak is not None else 'N/A', 
                'vehicles': round(weekend_peak['COMMADDR'], 1) if weekend_peak is not None else 0
            }
        }
    
    def _calculate_weekly_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算周客流量综合统计"""
        # 基础统计
        total_vehicles = df['COMMADDR'].nunique()
        total_points = len(df)
        date_span = df['date'].nunique()
        
        # 按日统计
        daily_vehicles = df.groupby('date')['COMMADDR'].nunique()
        
        return {
            'total_unique_vehicles': int(total_vehicles),
            'total_data_points': int(total_points),
            'analysis_days': int(date_span),
            'avg_daily_vehicles': round(daily_vehicles.mean(), 1),
            'max_daily_vehicles': int(daily_vehicles.max()),
            'min_daily_vehicles': int(daily_vehicles.min()),
            'vehicle_flow_variance': round(daily_vehicles.var(), 2),
            'data_completeness': round((date_span / 7) * 100, 1)  # 假设一周7天的完整度
        } 

    def get_vehicle_count_estimate(self) -> int:
        """
        读取车辆索引文件，返回车辆数量估算
        """
        try:
            index_path = os.path.join(
                os.path.dirname(__file__),
                'data', 'indexes', 'vehicle_index.json'
            )
            if not os.path.exists(index_path):
                return 0
            with open(index_path, 'r', encoding='utf-8') as f:
                vehicle_index = json.load(f)
            return len(vehicle_index)
        except Exception as e:
            print(f"车辆数量估算失败: {e}")
            return 0
            
    def get_point_count_estimate(self) -> int:
        """
        估算数据点总数
        """
        try:
            # 尝试使用预处理数据统计
            if self.use_preprocessed:
                total_points = 0
                # 统计所有parquet文件的大小来估算
                for file in os.listdir(self.processed_dir):
                    if file.endswith('.parquet'):
                        file_path = os.path.join(self.processed_dir, file)
                        # 使用文件大小估算
                        # 假设每条记录平均50字节
                        total_points += os.path.getsize(file_path) // 50
                
                if total_points > 0:
                    return total_points
            
            # 如果没有预处理数据，使用CSV文件估算
            total_size = 0
            for file in self.get_csv_files():
                if os.path.exists(file):
                    total_size += os.path.getsize(file)
            
            # 假设每条记录平均100字节
            estimated_points = total_size // 100
            return max(1000000, estimated_points)  # 至少返回100万点
            
        except Exception as e:
            print(f"数据点数量估算失败: {e}")
            # 返回一个合理的默认值
            return 5000000

    def _standardize_dataframe(self, df):
        """
        统一常用字段名，防止后续分析出错，并自动归一化经纬度
        """
        rename_map = {
            'COMMADDR': 'vehicle_id',
            'UTC': 'timestamp',
            'LAT': 'latitude',
            'LON': 'longitude'
        }
        for old, new in rename_map.items():
            if old in df.columns:
                df[new] = df[old]
        # 经纬度如果是整型，转为浮点型
        if 'latitude' in df.columns and df['latitude'].dtype != float:
            df['latitude'] = df['latitude'].astype(float)
        if 'longitude' in df.columns and df['longitude'].dtype != float:
            df['longitude'] = df['longitude'].astype(float)
        # 自动归一化经纬度（如超出地理范围，自动除以1e5）
        if 'latitude' in df.columns and df['latitude'].abs().max() > 90:
            df['latitude'] = df['latitude'] / 1e5
        if 'longitude' in df.columns and df['longitude'].abs().max() > 180:
            df['longitude'] = df['longitude'] / 1e5
        return df
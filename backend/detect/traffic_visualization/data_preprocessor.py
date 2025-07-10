import pandas as pd
import numpy as np
import os
import json
import pickle
from typing import Dict, List, Tuple
from collections import defaultdict
import math

class TrafficDataPreprocessor:
    """
    交通数据预处理器
    将原始CSV数据预处理为可快速查询的格式
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        else:
            self.data_dir = data_dir
        
        self.processed_dir = os.path.join(self.data_dir, 'processed')
        self.index_dir = os.path.join(self.data_dir, 'indexes')
        
        # 创建处理后的数据目录
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.index_dir, exist_ok=True)
    
    def preprocess_all_data(self):
        """预处理所有原始数据"""
        print("开始预处理所有数据...")
        
        # 1. 时间分片预聚合
        self._create_time_based_aggregations()
        
        # 2. 空间网格化
        self._create_spatial_grids()
        
        # 3. 车辆轨迹索引
        self._create_vehicle_indexes()
        
        # 4. 热力图预计算
        self._create_heatmap_precomputed()
        
        print("数据预处理完成！")
    
    def _create_time_based_aggregations(self):
        """按时间分片聚合数据"""
        print("创建时间分片聚合...")
        
        csv_files = self._get_csv_files()
        hourly_data = defaultdict(list)
        
        for file_path in csv_files:
            print(f"处理文件: {os.path.basename(file_path)}")
            
            # 分块读取大文件
            for chunk in pd.read_csv(file_path, chunksize=100000):
                if 'UTC' not in chunk.columns:
                    continue
                
                # 转换为小时
                chunk['hour'] = (chunk['UTC'] // 3600) * 3600
                
                # 按小时分组
                for hour, group in chunk.groupby('hour'):
                    # 采样到合理大小（每小时最多1万个点）
                    if len(group) > 10000:
                        group = group.sample(10000, random_state=42)
                    
                    hourly_data[hour].append(group)
        
        # 保存每小时的数据
        for hour, data_list in hourly_data.items():
            if data_list:
                hour_df = pd.concat(data_list, ignore_index=True)
                filename = f"hour_{int(hour)}.parquet"
                filepath = os.path.join(self.processed_dir, filename)
                hour_df.to_parquet(filepath, compression='snappy')
                print(f"保存小时数据: {filename}, 记录数: {len(hour_df)}")
    
    def _create_spatial_grids(self):
        """创建空间网格索引"""
        print("创建空间网格索引...")
        
        # 不同分辨率的网格
        resolutions = [0.001, 0.005, 0.01]  # 高、中、低分辨率
        
        for resolution in resolutions:
            print(f"创建 {resolution} 度分辨率网格...")
            grid_data = defaultdict(int)
            
            # 读取所有小时数据
            for filename in os.listdir(self.processed_dir):
                if filename.endswith('.parquet'):
                    filepath = os.path.join(self.processed_dir, filename)
                    df = pd.read_parquet(filepath)
                    
                    if 'LAT' in df.columns and 'LON' in df.columns:
                        # 转换坐标
                        df['lat'] = df['LAT'] / 1e5
                        df['lng'] = df['LON'] / 1e5
                        
                        # 网格化
                        df['lat_grid'] = (df['lat'] / resolution).round() * resolution
                        df['lng_grid'] = (df['lng'] / resolution).round() * resolution
                        
                        # 统计每个网格的点数
                        grid_counts = df.groupby(['lat_grid', 'lng_grid']).size()
                        
                        for (lat, lng), count in grid_counts.items():
                            grid_key = f"{lat:.6f},{lng:.6f}"
                            grid_data[grid_key] += count
            
            # 保存网格数据
            grid_filename = f"spatial_grid_{resolution}.json"
            grid_filepath = os.path.join(self.index_dir, grid_filename)
            with open(grid_filepath, 'w') as f:
                json.dump(dict(grid_data), f)
            
            print(f"保存空间网格: {grid_filename}, 网格数: {len(grid_data)}")
    
    def _create_vehicle_indexes(self):
        """创建车辆索引"""
        print("创建车辆索引...")
        
        vehicle_index = defaultdict(list)  # vehicle_id -> [时间段列表]
        
        for filename in os.listdir(self.processed_dir):
            if filename.endswith('.parquet'):
                hour = int(filename.split('_')[1].split('.')[0])
                filepath = os.path.join(self.processed_dir, filename)
                df = pd.read_parquet(filepath)
                
                if 'COMMADDR' in df.columns:
                    # 记录每个车辆在这个时间段出现
                    unique_vehicles = df['COMMADDR'].unique()
                    for vehicle_id in unique_vehicles:
                        vehicle_index[str(vehicle_id)].append(hour)
        
        # 保存车辆索引
        index_filepath = os.path.join(self.index_dir, 'vehicle_index.json')
        with open(index_filepath, 'w') as f:
            json.dump(dict(vehicle_index), f)
        
        print(f"车辆索引创建完成，索引车辆数: {len(vehicle_index)}")
    
    def _create_heatmap_precomputed(self):
        """预计算不同时间段的热力图"""
        print("预计算热力图数据...")
        
        # 按天预计算热力图
        daily_heatmaps = defaultdict(lambda: defaultdict(int))
        
        for filename in os.listdir(self.processed_dir):
            if filename.endswith('.parquet'):
                hour = int(filename.split('_')[1].split('.')[0])
                day = hour // (24 * 3600) * (24 * 3600)  # 所属天
                
                filepath = os.path.join(self.processed_dir, filename)
                df = pd.read_parquet(filepath)
                
                if 'LAT' in df.columns and 'LON' in df.columns:
                    # 转换坐标并网格化
                    df['lat'] = df['LAT'] / 1e5
                    df['lng'] = df['LON'] / 1e5
                    
                    resolution = 0.002  # 热力图使用中等分辨率
                    df['lat_grid'] = (df['lat'] / resolution).round() * resolution
                    df['lng_grid'] = (df['lng'] / resolution).round() * resolution
                    
                    # 统计网格密度
                    grid_counts = df.groupby(['lat_grid', 'lng_grid']).size()
                    
                    for (lat, lng), count in grid_counts.items():
                        grid_key = f"{lat:.6f},{lng:.6f}"
                        daily_heatmaps[day][grid_key] += count
        
        # 保存每日热力图
        for day, heatmap_data in daily_heatmaps.items():
            filename = f"heatmap_day_{int(day)}.json"
            filepath = os.path.join(self.index_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(dict(heatmap_data), f)
            
            print(f"保存日热力图: {filename}, 网格数: {len(heatmap_data)}")
    
    def _get_csv_files(self) -> List[str]:
        """获取所有CSV文件路径"""
        csv_files = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                csv_files.append(os.path.join(self.data_dir, filename))
        return sorted(csv_files)

class FastTrafficDataLoader:
    """
    快速交通数据加载器
    使用预处理的数据进行快速查询
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        else:
            self.data_dir = data_dir
        
        self.processed_dir = os.path.join(self.data_dir, 'processed')
        self.index_dir = os.path.join(self.data_dir, 'indexes')
        
        # 加载索引
        self.vehicle_index = self._load_vehicle_index()
        self.spatial_grids = self._load_spatial_grids()
    
    def _load_vehicle_index(self) -> Dict:
        """加载车辆索引"""
        index_filepath = os.path.join(self.index_dir, 'vehicle_index.json')
        if os.path.exists(index_filepath):
            with open(index_filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_spatial_grids(self) -> Dict:
        """加载空间网格"""
        grids = {}
        for filename in os.listdir(self.index_dir):
            if filename.startswith('spatial_grid_') and filename.endswith('.json'):
                resolution = float(filename.split('_')[2].split('.')[0])
                filepath = os.path.join(self.index_dir, filename)
                with open(filepath, 'r') as f:
                    grids[resolution] = json.load(f)
        return grids
    
    def fast_load_data(self, start_time: float, end_time: float, vehicle_id: str = None) -> pd.DataFrame:
        """快速加载数据"""
        print(f"快速加载数据: {start_time} - {end_time}")
        
        # 计算需要的时间段
        start_hour = (int(start_time) // 3600) * 3600
        end_hour = (int(end_time) // 3600) * 3600
        
        # 如果指定了车辆ID，先检查车辆索引
        if vehicle_id and vehicle_id in self.vehicle_index:
            available_hours = set(self.vehicle_index[vehicle_id])
        else:
            available_hours = None
        
        # 加载相关时间段的数据
        data_frames = []
        current_hour = start_hour
        
        while current_hour <= end_hour:
            if available_hours is None or current_hour in available_hours:
                filename = f"hour_{int(current_hour)}.parquet"
                filepath = os.path.join(self.processed_dir, filename)
                
                if os.path.exists(filepath):
                    df = pd.read_parquet(filepath)
                    
                    # 精确时间过滤
                    df = df[(df['UTC'] >= start_time) & (df['UTC'] <= end_time)]
                    
                    # 车辆ID过滤
                    if vehicle_id:
                        df['COMMADDR'] = df['COMMADDR'].astype(str)
                        df = df[df['COMMADDR'] == str(vehicle_id)]
                    
                    if not df.empty:
                        data_frames.append(df)
            
            current_hour += 3600  # 下一小时
        
        # 合并数据
        if data_frames:
            result = pd.concat(data_frames, ignore_index=True)
            print(f"快速加载完成，共 {len(result)} 条记录")
            return result
        else:
            print("未找到匹配的数据")
            return pd.DataFrame()
    
    def fast_get_heatmap(self, start_time: float, end_time: float, resolution: float = 0.002) -> List[Dict]:
        """快速获取热力图数据"""
        # 使用预计算的热力图数据
        start_day = (int(start_time) // (24 * 3600)) * (24 * 3600)
        end_day = (int(end_time) // (24 * 3600)) * (24 * 3600)
        
        combined_heatmap = defaultdict(int)
        current_day = start_day
        
        while current_day <= end_day:
            filename = f"heatmap_day_{int(current_day)}.json"
            filepath = os.path.join(self.index_dir, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    day_heatmap = json.load(f)
                
                for grid_key, count in day_heatmap.items():
                    combined_heatmap[grid_key] += count
            
            current_day += 24 * 3600  # 下一天
        
        # 转换为热力图点格式
        heatmap_points = []
        for grid_key, count in combined_heatmap.items():
            lat, lng = map(float, grid_key.split(','))
            heatmap_points.append({
                'lat': lat,
                'lng': lng,
                'count': count
            })
        
        print(f"快速热力图生成完成，共 {len(heatmap_points)} 个点")
        return heatmap_points

if __name__ == "__main__":
    # 使用示例
    preprocessor = TrafficDataPreprocessor()
    
    # 运行预处理（只需要运行一次）
    print("开始数据预处理...")
    preprocessor.preprocess_all_data()
    
    # 测试快速加载
    fast_loader = FastTrafficDataLoader()
    
    # 测试时间范围查询
    start_time = 1379030400  # 2013-09-13 08:00
    end_time = 1379044800    # 2013-09-13 12:00
    
    data = fast_loader.fast_load_data(start_time, end_time)
    print(f"查询结果: {len(data)} 条记录")
    
    # 测试快速热力图
    heatmap = fast_loader.fast_get_heatmap(start_time, end_time)
    print(f"热力图点数: {len(heatmap)}") 
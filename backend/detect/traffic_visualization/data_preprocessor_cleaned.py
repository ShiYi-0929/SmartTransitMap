import pandas as pd
import numpy as np
import os
import json
import pickle
from typing import Dict, List, Tuple
from collections import defaultdict
import math

def convert_numpy_types(obj):
    """递归转换numpy类型为Python原生类型，确保JSON序列化兼容"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    else:
        return obj

class CleanedTrafficDataPreprocessor:
    """
    清洗后交通数据预处理器
    将清洗后的CSV数据预处理为可快速查询的格式
    
    清洗后数据格式：
    COMMADDR,UTC,LAT,LON,HEAD,SPEED,TFLAG,lat,lon,speed_kmh,is_occupied,timestamp
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # 指向清洗后数据目录
            self.data_dir = os.path.join(os.path.dirname(__file__), 'data', 'cleaned')
        else:
            self.data_dir = data_dir
        
        # 确保使用清洗后的数据目录
        if not self.data_dir.endswith('cleaned'):
            self.data_dir = os.path.join(self.data_dir, 'cleaned')
        
        # 预处理输出目录（与原来的保持一致，但基于清洗后数据）
        self.processed_dir = os.path.join(os.path.dirname(self.data_dir), 'processed')
        self.index_dir = os.path.join(os.path.dirname(self.data_dir), 'indexes')
        
        print(f"清洗后数据目录: {self.data_dir}")
        print(f"预处理输出目录: {self.processed_dir}")
        print(f"索引输出目录: {self.index_dir}")
        
        # 创建处理后的数据目录
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.index_dir, exist_ok=True)
    
    def preprocess_all_data(self):
        """预处理所有清洗后的数据"""
        print("开始预处理清洗后的数据...")
        
        # 检查清洗后的数据文件
        cleaned_files = self._get_cleaned_csv_files()
        if not cleaned_files:
            print("❌ 未找到清洗后的数据文件！")
            print(f"请确保 {self.data_dir} 目录下有清洗后的CSV文件")
            return
        
        print(f"找到 {len(cleaned_files)} 个清洗后的数据文件")
        for file_path in cleaned_files:
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  - {os.path.basename(file_path)}: {file_size:.1f} MB")
        
        # 1. 时间分片预聚合
        self._create_time_based_aggregations()
        
        # 2. 空间网格化
        self._create_spatial_grids()
        
        # 3. 车辆轨迹索引
        self._create_vehicle_indexes()
        
        # 4. 热力图预计算
        self._create_heatmap_precomputed()
        
        # 5. 生成数据统计信息
        self._create_data_summary()
        
        print("✅ 清洗后数据预处理完成！")
    
    def _create_time_based_aggregations(self):
        """按时间分片聚合清洗后的数据"""
        print("创建时间分片聚合...")
        
        cleaned_files = self._get_cleaned_csv_files()
        hourly_data = defaultdict(list)
        total_records = 0
        
        for file_path in cleaned_files:
            print(f"处理清洗后文件: {os.path.basename(file_path)}")
            
            try:
                # 分块读取大文件（清洗后的数据应该已经有了正确的列名）
                chunk_count = 0
                for chunk in pd.read_csv(file_path, chunksize=50000):
                    chunk_count += 1
                    if chunk_count % 20 == 0:
                        print(f"  处理第 {chunk_count} 个数据块...")
                    
                    # 验证必要的列是否存在
                    if 'UTC' not in chunk.columns:
                        print(f"⚠️ 跳过文件 {os.path.basename(file_path)} - 缺少UTC列")
                        continue
                    
                    # 清洗后的数据已经有了转换后的坐标，直接使用
                    if 'lat' not in chunk.columns or 'lon' not in chunk.columns:
                        print(f"⚠️ 文件 {os.path.basename(file_path)} 缺少转换后的坐标列")
                        continue
                    
                    # 确保数据类型正确
                    chunk['UTC'] = pd.to_numeric(chunk['UTC'], errors='coerce')
                    chunk = chunk.dropna(subset=['UTC'])
                    
                    if len(chunk) == 0:
                        continue
                    
                    # 转换为小时时间戳
                    chunk['hour'] = (chunk['UTC'] // 3600) * 3600
                    
                    # 按小时分组
                    for hour, group in chunk.groupby('hour'):
                        # 每小时最多保留2万个点（比原版更多，因为清洗后数据质量更好）
                        if len(group) > 20000:
                            # 分层采样：保持车辆分布
                            if 'COMMADDR' in group.columns:
                                vehicle_groups = group.groupby('COMMADDR')
                                sample_per_vehicle = max(1, 20000 // len(vehicle_groups))
                                sampled_groups = []
                                for _, vg in vehicle_groups:
                                    if len(vg) <= sample_per_vehicle:
                                        sampled_groups.append(vg)
                                    else:
                                        sampled_groups.append(vg.sample(sample_per_vehicle, random_state=42))
                                group = pd.concat(sampled_groups, ignore_index=True)
                            else:
                                group = group.sample(20000, random_state=42)
                        
                        hourly_data[hour].append(group)
                    
                    total_records += len(chunk)
                
                print(f"  文件处理完成，总记录数: {total_records}")
                
            except Exception as e:
                print(f"❌ 处理文件 {os.path.basename(file_path)} 时出错: {e}")
                continue
        
        # 保存每小时的数据
        saved_hours = 0
        for hour, data_list in hourly_data.items():
            if data_list:
                try:
                    hour_df = pd.concat(data_list, ignore_index=True)
                    filename = f"hour_{int(hour)}.parquet"
                    filepath = os.path.join(self.processed_dir, filename)
                    hour_df.to_parquet(filepath, compression='snappy')
                    
                    # 转换时间戳为可读格式用于日志
                    from datetime import datetime
                    readable_time = datetime.fromtimestamp(hour).strftime('%Y-%m-%d %H:%M')
                    print(f"✅ 保存小时数据: {filename} ({readable_time}), 记录数: {len(hour_df)}")
                    saved_hours += 1
                except Exception as e:
                    print(f"❌ 保存小时数据失败 (hour={hour}): {e}")
        
        print(f"✅ 时间分片聚合完成，保存了 {saved_hours} 个小时的数据")
    
    def _create_spatial_grids(self):
        """创建基于清洗后数据的空间网格索引"""
        print("创建空间网格索引...")
        
        # 不同分辨率的网格
        resolutions = [0.001, 0.002, 0.005, 0.01]  # 增加0.002精度用于热力图
        
        for resolution in resolutions:
            print(f"创建 {resolution} 度分辨率网格...")
            grid_data = defaultdict(int)
            
            # 读取所有小时数据
            processed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('.parquet')]
            if not processed_files:
                print("⚠️ 未找到预处理的小时数据文件，请先运行时间分片聚合")
                continue
            
            for filename in processed_files:
                filepath = os.path.join(self.processed_dir, filename)
                try:
                    df = pd.read_parquet(filepath)
                    
                    # 使用清洗后数据中已经转换好的坐标
                    if 'lat' in df.columns and 'lon' in df.columns:
                        # 直接使用转换后的坐标
                        df['lat_grid'] = (df['lat'] / resolution).round() * resolution
                        df['lng_grid'] = (df['lon'] / resolution).round() * resolution
                        
                        # 统计每个网格的点数
                        grid_counts = df.groupby(['lat_grid', 'lng_grid']).size()
                        
                        for (lat, lng), count in grid_counts.items():
                            grid_key = f"{lat:.6f},{lng:.6f}"
                            grid_data[grid_key] += count
                    else:
                        print(f"⚠️ 文件 {filename} 缺少坐标列")
                        
                except Exception as e:
                    print(f"❌ 处理文件 {filename} 时出错: {e}")
            
            # 保存网格数据
            if grid_data:
                grid_filename = f"spatial_grid_{resolution}.json"
                grid_filepath = os.path.join(self.index_dir, grid_filename)
                with open(grid_filepath, 'w') as f:
                    # 转换numpy类型为Python原生类型
                    grid_data_serializable = convert_numpy_types(dict(grid_data))
                    json.dump(grid_data_serializable, f)
                
                print(f"✅ 保存空间网格: {grid_filename}, 网格数: {len(grid_data)}")
            else:
                print(f"⚠️ 分辨率 {resolution} 未生成有效网格数据")
    
    def _create_vehicle_indexes(self):
        """创建基于清洗后数据的车辆索引（优化版本）"""
        print("创建车辆索引...")
        
        vehicle_index = defaultdict(list)  # vehicle_id -> [时间段列表]
        vehicle_stats = defaultdict(lambda: {'records': 0, 'time_span': [float('inf'), 0]})
        
        processed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('.parquet')]
        total_files = len(processed_files)
        
        for i, filename in enumerate(processed_files):
            print(f"处理车辆索引 ({i+1}/{total_files}): {filename}")
            
            try:
                hour = int(filename.split('_')[1].split('.')[0])
                filepath = os.path.join(self.processed_dir, filename)
                df = pd.read_parquet(filepath)
                
                if 'COMMADDR' in df.columns:
                    # 优化：使用groupby一次性处理所有车辆，避免反复筛选
                    vehicle_groups = df.groupby('COMMADDR')
                    
                    for vehicle_id, vehicle_data in vehicle_groups:
                        vehicle_str = str(vehicle_id)
                        vehicle_index[vehicle_str].append(hour)
                        
                        # 统计车辆信息
                        record_count = len(vehicle_data)
                        vehicle_stats[vehicle_str]['records'] += record_count
                        
                        if 'UTC' in vehicle_data.columns:
                            min_time = vehicle_data['UTC'].min()
                            max_time = vehicle_data['UTC'].max()
                            vehicle_stats[vehicle_str]['time_span'][0] = min(
                                vehicle_stats[vehicle_str]['time_span'][0], min_time
                            )
                            vehicle_stats[vehicle_str]['time_span'][1] = max(
                                vehicle_stats[vehicle_str]['time_span'][1], max_time
                            )
                    
                    print(f"  处理了 {len(vehicle_groups)} 个车辆的数据")
                            
            except Exception as e:
                print(f"❌ 处理车辆索引文件 {filename} 时出错: {e}")
        
        # 保存车辆索引
        if vehicle_index:
            print("保存车辆索引文件...")
            index_filepath = os.path.join(self.index_dir, 'vehicle_index.json')
            with open(index_filepath, 'w') as f:
                # 转换numpy类型为Python原生类型
                vehicle_index_serializable = convert_numpy_types(dict(vehicle_index))
                json.dump(vehicle_index_serializable, f)
            
            # 保存车辆统计信息
            print("保存车辆统计信息...")
            stats_filepath = os.path.join(self.index_dir, 'vehicle_stats.json')
            with open(stats_filepath, 'w') as f:
                # 转换numpy类型为Python原生类型
                vehicle_stats_serializable = convert_numpy_types(dict(vehicle_stats))
                json.dump(vehicle_stats_serializable, f)
            
            print(f"✅ 车辆索引创建完成，索引车辆数: {len(vehicle_index)}")
            
            # 显示一些统计信息
            if vehicle_stats:
                record_counts = [stats['records'] for stats in vehicle_stats.values()]
                print(f"   车辆记录数统计: 平均 {np.mean(record_counts):.0f}, "
                      f"最多 {max(record_counts)}, 最少 {min(record_counts)}")
        else:
            print("⚠️ 未生成车辆索引数据")
    
    def _create_heatmap_precomputed(self):
        """基于清洗后数据预计算热力图"""
        print("预计算热力图数据...")
        
        # 按天和按小时预计算热力图
        daily_heatmaps = defaultdict(lambda: defaultdict(int))
        hourly_heatmaps = defaultdict(lambda: defaultdict(int))
        
        processed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('.parquet')]
        
        for filename in processed_files:
            try:
                hour = int(filename.split('_')[1].split('.')[0])
                day = hour // (24 * 3600) * (24 * 3600)  # 所属天
                
                filepath = os.path.join(self.processed_dir, filename)
                df = pd.read_parquet(filepath)
                
                # 使用清洗后数据的转换坐标
                if 'lat' in df.columns and 'lon' in df.columns:
                    resolution = 0.002  # 热力图使用中等分辨率
                    df['lat_grid'] = (df['lat'] / resolution).round() * resolution
                    df['lng_grid'] = (df['lon'] / resolution).round() * resolution
                    
                    # 统计网格密度
                    grid_counts = df.groupby(['lat_grid', 'lng_grid']).size()
                    
                    for (lat, lng), count in grid_counts.items():
                        grid_key = f"{lat:.6f},{lng:.6f}"
                        daily_heatmaps[day][grid_key] += count
                        hourly_heatmaps[hour][grid_key] += count
                        
            except Exception as e:
                print(f"❌ 处理热力图文件 {filename} 时出错: {e}")
        
        # 保存每日热力图
        saved_daily = 0
        for day, heatmap_data in daily_heatmaps.items():
            if heatmap_data:
                try:
                    filename = f"heatmap_day_{int(day)}.json"
                    filepath = os.path.join(self.index_dir, filename)
                    with open(filepath, 'w') as f:
                        # 转换numpy类型为Python原生类型
                        heatmap_data_serializable = convert_numpy_types(dict(heatmap_data))
                        json.dump(heatmap_data_serializable, f)
                    
                    from datetime import datetime
                    readable_date = datetime.fromtimestamp(day).strftime('%Y-%m-%d')
                    print(f"✅ 保存日热力图: {filename} ({readable_date}), 网格数: {len(heatmap_data)}")
                    saved_daily += 1
                except Exception as e:
                    print(f"❌ 保存日热力图失败 (day={day}): {e}")
        
        # 保存每小时热力图（用于更精细的查询）
        saved_hourly = 0
        for hour, heatmap_data in hourly_heatmaps.items():
            if heatmap_data:
                try:
                    filename = f"heatmap_hour_{int(hour)}.json"
                    filepath = os.path.join(self.index_dir, filename)
                    with open(filepath, 'w') as f:
                        # 转换numpy类型为Python原生类型
                        heatmap_data_serializable = convert_numpy_types(dict(heatmap_data))
                        json.dump(heatmap_data_serializable, f)
                    saved_hourly += 1
                except Exception as e:
                    print(f"❌ 保存小时热力图失败 (hour={hour}): {e}")
        
        print(f"✅ 热力图预计算完成: {saved_daily} 个日热力图, {saved_hourly} 个小时热力图")
    
    def _create_data_summary(self):
        """生成数据概要统计"""
        print("生成数据概要统计...")
        
        summary = {
            'preprocessing_time': pd.Timestamp.now().isoformat(),
            'source_directory': self.data_dir,
            'total_hours': 0,
            'total_records': 0,
            'total_vehicles': 0,
            'time_range': {'start': None, 'end': None},
            'coordinate_range': {'lat_min': float('inf'), 'lat_max': float('-inf'),
                               'lng_min': float('inf'), 'lng_max': float('-inf')},
            'files_processed': []
        }
        
        # 统计预处理结果
        processed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('.parquet')]
        
        all_times = []
        all_lats = []
        all_lngs = []
        
        for filename in processed_files:
            try:
                filepath = os.path.join(self.processed_dir, filename)
                df = pd.read_parquet(filepath)
                
                summary['total_records'] += len(df)
                
                if 'UTC' in df.columns:
                    times = df['UTC'].dropna()
                    all_times.extend(times.tolist())
                
                if 'lat' in df.columns and 'lon' in df.columns:
                    lats = df['lat'].dropna()
                    lngs = df['lon'].dropna()
                    all_lats.extend(lats.tolist())
                    all_lngs.extend(lngs.tolist())
                
                if 'COMMADDR' in df.columns:
                    unique_vehicles = df['COMMADDR'].nunique()
                    summary['total_vehicles'] = max(summary['total_vehicles'], unique_vehicles)
                    
            except Exception as e:
                print(f"❌ 统计文件 {filename} 时出错: {e}")
        
        # 汇总统计信息
        summary['total_hours'] = len(processed_files)
        
        if all_times:
            summary['time_range']['start'] = min(all_times)
            summary['time_range']['end'] = max(all_times)
        
        if all_lats and all_lngs:
            summary['coordinate_range'] = {
                'lat_min': min(all_lats),
                'lat_max': max(all_lats),
                'lng_min': min(all_lngs),
                'lng_max': max(all_lngs)
            }
        
        # 记录原始文件信息
        for file_path in self._get_cleaned_csv_files():
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            summary['files_processed'].append({
                'filename': os.path.basename(file_path),
                'size_mb': round(file_size, 2)
            })
        
        # 保存概要统计
        summary_filepath = os.path.join(self.index_dir, 'data_summary.json')
        with open(summary_filepath, 'w') as f:
            # 转换numpy类型为Python原生类型
            summary_serializable = convert_numpy_types(summary)
            json.dump(summary_serializable, f, indent=2)
        
        print(f"✅ 数据概要统计完成:")
        print(f"   总记录数: {summary['total_records']:,}")
        print(f"   总车辆数: {summary['total_vehicles']:,}")
        print(f"   时间跨度: {summary['total_hours']} 小时")
        if summary['time_range']['start']:
            from datetime import datetime
            start_time = datetime.fromtimestamp(summary['time_range']['start'])
            end_time = datetime.fromtimestamp(summary['time_range']['end'])
            print(f"   时间范围: {start_time} ~ {end_time}")
    
    def _get_cleaned_csv_files(self) -> List[str]:
        """获取清洗后数据目录中的所有CSV文件"""
        if not os.path.exists(self.data_dir):
            print(f"❌ 清洗后数据目录不存在: {self.data_dir}")
            return []
        
        csv_files = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.data_dir, filename)
                csv_files.append(file_path)
        
        return sorted(csv_files)
    
    def clean_existing_preprocessed_data(self):
        """清理现有的预处理数据"""
        print("清理现有的预处理数据...")
        
        # 清理processed目录
        if os.path.exists(self.processed_dir):
            for filename in os.listdir(self.processed_dir):
                if filename.endswith('.parquet'):
                    file_path = os.path.join(self.processed_dir, filename)
                    os.remove(file_path)
                    print(f"删除: {filename}")
        
        # 清理indexes目录
        if os.path.exists(self.index_dir):
            for filename in os.listdir(self.index_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.index_dir, filename)
                    os.remove(file_path)
                    print(f"删除: {filename}")
        
        print("✅ 清理完成")

# 为了保持兼容性，创建一个增强版的快速加载器
class EnhancedFastTrafficDataLoader:
    """
    增强版快速交通数据加载器
    支持清洗后数据的预处理结果
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
        self.vehicle_stats = self._load_vehicle_stats()
        self.spatial_grids = self._load_spatial_grids()
        self.data_summary = self._load_data_summary()
        
        print(f"📊 数据概要: {self.data_summary.get('total_records', 0):,} 条记录, "
              f"{self.data_summary.get('total_vehicles', 0):,} 辆车, "
              f"{self.data_summary.get('total_hours', 0)} 小时")
    
    def _load_vehicle_index(self) -> Dict:
        """加载车辆索引"""
        index_filepath = os.path.join(self.index_dir, 'vehicle_index.json')
        if os.path.exists(index_filepath):
            with open(index_filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_vehicle_stats(self) -> Dict:
        """加载车辆统计信息"""
        stats_filepath = os.path.join(self.index_dir, 'vehicle_stats.json')
        if os.path.exists(stats_filepath):
            with open(stats_filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_spatial_grids(self) -> Dict:
        """加载空间网格"""
        grids = {}
        if not os.path.exists(self.index_dir):
            return grids
            
        for filename in os.listdir(self.index_dir):
            if filename.startswith('spatial_grid_') and filename.endswith('.json'):
                try:
                    resolution = float(filename.split('_')[2].split('.')[0])
                    filepath = os.path.join(self.index_dir, filename)
                    with open(filepath, 'r') as f:
                        grids[resolution] = json.load(f)
                except:
                    continue
        return grids
    
    def _load_data_summary(self) -> Dict:
        """加载数据概要"""
        summary_filepath = os.path.join(self.index_dir, 'data_summary.json')
        if os.path.exists(summary_filepath):
            with open(summary_filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def get_data_summary(self) -> Dict:
        """获取数据概要统计"""
        return self.data_summary
    
    def get_vehicle_stats(self, vehicle_id: str = None) -> Dict:
        """获取车辆统计信息"""
        if vehicle_id:
            return self.vehicle_stats.get(str(vehicle_id), {})
        else:
            return self.vehicle_stats
    
    def fast_load_data(self, start_time: float, end_time: float, vehicle_id: str = None) -> pd.DataFrame:
        """快速加载数据（增强版）"""
        print(f"⚡ 快速加载数据: {start_time} - {end_time}")
        
        # 计算需要的时间段
        start_hour = (int(start_time) // 3600) * 3600
        end_hour = (int(end_time) // 3600) * 3600
        
        # 如果指定了车辆ID，先检查车辆索引
        if vehicle_id and vehicle_id in self.vehicle_index:
            available_hours = set(self.vehicle_index[vehicle_id])
            print(f"🚗 车辆 {vehicle_id} 在 {len(available_hours)} 个小时段有数据")
        else:
            available_hours = None
        
        # 加载相关时间段的数据
        data_frames = []
        current_hour = start_hour
        loaded_hours = 0
        
        while current_hour <= end_hour:
            if available_hours is None or current_hour in available_hours:
                filename = f"hour_{int(current_hour)}.parquet"
                filepath = os.path.join(self.processed_dir, filename)
                
                if os.path.exists(filepath):
                    try:
                        df = pd.read_parquet(filepath)
                        
                        # 精确时间过滤
                        df = df[(df['UTC'] >= start_time) & (df['UTC'] <= end_time)]
                        
                        # 车辆ID过滤
                        if vehicle_id:
                            df['COMMADDR'] = df['COMMADDR'].astype(str)
                            df = df[df['COMMADDR'] == str(vehicle_id)]
                        
                        if not df.empty:
                            data_frames.append(df)
                            loaded_hours += 1
                            
                    except Exception as e:
                        print(f"⚠️ 加载文件 {filename} 时出错: {e}")
            
            current_hour += 3600  # 下一小时
        
        # 合并数据
        if data_frames:
            result = pd.concat(data_frames, ignore_index=True)
            print(f"✅ 快速加载完成: {len(result):,} 条记录 (来自 {loaded_hours} 个小时段)")
            return result
        else:
            print("📭 未找到匹配的数据")
            return pd.DataFrame()
    
    def fast_get_heatmap(self, start_time: float, end_time: float, resolution: str = "daily") -> List[Dict]:
        """快速获取热力图数据（增强版）"""
        print(f"🗺️ 快速生成热力图: {resolution} 模式")
        
        combined_heatmap = defaultdict(int)
        
        if resolution == "daily":
            # 使用预计算的日热力图
            start_day = (int(start_time) // (24 * 3600)) * (24 * 3600)
            end_day = (int(end_time) // (24 * 3600)) * (24 * 3600)
            
            current_day = start_day
            loaded_days = 0
            
            while current_day <= end_day:
                filename = f"heatmap_day_{int(current_day)}.json"
                filepath = os.path.join(self.index_dir, filename)
                
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r') as f:
                            day_heatmap = json.load(f)
                        
                        for grid_key, count in day_heatmap.items():
                            combined_heatmap[grid_key] += count
                        
                        loaded_days += 1
                    except Exception as e:
                        print(f"⚠️ 加载日热力图 {filename} 时出错: {e}")
                
                current_day += 24 * 3600  # 下一天
            
            print(f"📊 加载了 {loaded_days} 天的热力图数据")
            
        else:  # hourly
            # 使用预计算的小时热力图
            start_hour = (int(start_time) // 3600) * 3600
            end_hour = (int(end_time) // 3600) * 3600
            
            current_hour = start_hour
            loaded_hours = 0
            
            while current_hour <= end_hour:
                filename = f"heatmap_hour_{int(current_hour)}.json"
                filepath = os.path.join(self.index_dir, filename)
                
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r') as f:
                            hour_heatmap = json.load(f)
                        
                        for grid_key, count in hour_heatmap.items():
                            combined_heatmap[grid_key] += count
                        
                        loaded_hours += 1
                    except Exception as e:
                        print(f"⚠️ 加载小时热力图 {filename} 时出错: {e}")
                
                current_hour += 3600  # 下一小时
            
            print(f"📊 加载了 {loaded_hours} 小时的热力图数据")
        
        # 转换为热力图点格式
        heatmap_points = []
        for grid_key, count in combined_heatmap.items():
            try:
                lat, lng = map(float, grid_key.split(','))
                heatmap_points.append({
                    'lat': lat,
                    'lng': lng,
                    'count': count
                })
            except:
                continue
        
        # 按密度排序，取前10000个点
        heatmap_points.sort(key=lambda x: x['count'], reverse=True)
        result = heatmap_points[:10000]
        
        print(f"🗺️ 热力图生成完成: {len(result)} 个点")
        return result

if __name__ == "__main__":
    print("🚀 基于清洗后数据的预处理器")
    print("=" * 60)
    
    # 创建预处理器实例
    preprocessor = CleanedTrafficDataPreprocessor()
    
    # 可选：清理现有的预处理数据
    response = input("是否清理现有的预处理数据？(y/N): ")
    if response.lower() == 'y':
        preprocessor.clean_existing_preprocessed_data()
    
    # 运行预处理
    print("\n开始预处理清洗后的数据...")
    preprocessor.preprocess_all_data()
    
    # 测试增强版快速加载器
    print("\n" + "=" * 60)
    print("测试增强版快速加载器")
    print("=" * 60)
    
    loader = EnhancedFastTrafficDataLoader()
    
    # 显示数据概要
    summary = loader.get_data_summary()
    if summary:
        print("📊 数据概要:")
        print(f"   处理时间: {summary.get('preprocessing_time', 'Unknown')}")
        print(f"   数据文件: {len(summary.get('files_processed', []))} 个")
        print(f"   总记录数: {summary.get('total_records', 0):,}")
        print(f"   总车辆数: {summary.get('total_vehicles', 0):,}")
        
        time_range = summary.get('time_range', {})
        if time_range.get('start'):
            from datetime import datetime
            start = datetime.fromtimestamp(time_range['start'])
            end = datetime.fromtimestamp(time_range['end'])
            print(f"   时间范围: {start} ~ {end}")
    
    # 测试数据加载
    if summary and summary.get('time_range', {}).get('start'):
        test_start = summary['time_range']['start']
        test_end = test_start + 3600  # 1小时范围
        
        print(f"\n测试数据加载 (1小时范围)...")
        test_data = loader.fast_load_data(test_start, test_end)
        print(f"测试结果: {len(test_data)} 条记录")
        
        # 测试热力图
        print(f"\n测试热力图生成...")
        test_heatmap = loader.fast_get_heatmap(test_start, test_end, "daily")
        print(f"热力图点数: {len(test_heatmap)}")
    
    print("\n✅ 预处理和测试完成！")
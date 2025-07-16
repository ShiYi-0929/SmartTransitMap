import pandas as pd
import numpy as np
import os
import json
from typing import List, Dict, Tuple, Optional, Union, Any
from datetime import datetime, timedelta, timezone
import logging

class TrafficStatisticsLoader:
    """专用于流量统计的数据加载器，确保数据完整性，不进行采样"""
    
    def __init__(self, data_dir: str = None):
        """
        初始化流量统计数据加载器
        
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
            
        print(f"流量统计数据目录: {self.data_dir}")
        
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
            print("✓ 发现预处理数据，将使用高效统计模式")
            self._load_indexes()
        else:
            print("✗ 未发现预处理数据，将使用原始CSV文件统计")
        
        # 流量统计专用缓存
        self._hourly_cache = {}       # 按小时统计缓存
        self._daily_cache = {}        # 按天统计缓存
        self._weekly_cache = {}       # 按周统计缓存
        self._cache_maxsize = 20      # 增大缓存以支持统计查询
        self._csv_files = None
        
        # 日志配置
        self.logger = logging.getLogger(__name__)
    
    def _load_indexes(self):
        """加载预处理的索引数据"""
        try:
            # 加载时间索引（用于快速定位时间段）
            time_index_path = os.path.join(self.index_dir, 'time_index.json')
            if os.path.exists(time_index_path):
                with open(time_index_path, 'r') as f:
                    self.time_index = json.load(f)
                print(f"✓ 加载时间索引")
            else:
                self.time_index = {}
            
        except Exception as e:
            print(f"警告：加载索引时出错: {e}")
            self.use_preprocessed = False

    def get_csv_files(self) -> List[str]:
        """获取数据目录中的所有CSV文件"""
        if self._csv_files is None:
            self._csv_files = [
                os.path.join(self.data_dir, f) 
                for f in os.listdir(self.data_dir) 
                if f.endswith('.csv')
            ]
        return self._csv_files
    
    def load_traffic_count_data(self, start_time: float, end_time: float) -> pd.DataFrame:
        """
        专门用于流量统计的数据加载，确保数据完整性
        只加载必要的列：时间戳和车辆ID，用于计数统计
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        Returns:
            包含时间戳和车辆ID的完整DataFrame，用于统计
        """
        print(f"🚗 加载流量统计数据: {start_time} 到 {end_time}")
        
        # 生成缓存键
        cache_key = f"traffic_count_{start_time}_{end_time}"
        
        # 检查缓存
        if cache_key in self._hourly_cache:
            print("📊 使用流量统计缓存")
            return self._hourly_cache[cache_key]
        
        # 使用相应的加载方法
        if self.use_preprocessed:
            result = self._load_traffic_count_fast(start_time, end_time)
        else:
            result = self._load_traffic_count_legacy(start_time, end_time)
        
        # 更新缓存（LRU策略）
        if len(self._hourly_cache) >= self._cache_maxsize:
            oldest_key = next(iter(self._hourly_cache))
            del self._hourly_cache[oldest_key]
        
        self._hourly_cache[cache_key] = result
        print(f"✅ 流量统计数据加载完成: {len(result)} 条记录")
        return result
    
    def _load_traffic_count_fast(self, start_time: float, end_time: float) -> pd.DataFrame:
        """使用预处理数据进行快速流量统计加载"""
        print("🚀 使用预处理数据进行流量统计...")
        
        # 计算需要的时间段（小时级别）
        start_hour = (int(start_time) // 3600) * 3600
        end_hour = (int(end_time) // 3600) * 3600
        
        # 加载相关时间段的数据
        data_frames = []
        current_hour = start_hour
        
        while current_hour <= end_hour:
            filename = f"hour_{int(current_hour)}.parquet"
            filepath = os.path.join(self.processed_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    # 只加载统计必需的列
                    columns_to_load = ['UTC', 'COMMADDR']
                    df = pd.read_parquet(filepath, columns=columns_to_load)
                    
                    # 精确时间过滤
                    df = df[(df['UTC'] >= start_time) & (df['UTC'] <= end_time)]
                    
                    if not df.empty:
                        data_frames.append(df)
                        print(f"   📁 {filename}: {len(df)} 条记录")
                        
                except Exception as e:
                    print(f"❌ 读取 {filename} 时出错: {e}")
            
            current_hour += 3600  # 下一小时
        
        # 合并数据
        if data_frames:
            result = pd.concat(data_frames, ignore_index=True)
            # 按时间排序
            result = result.sort_values('UTC')
            print(f"⚡ 快速流量统计加载完成，共 {len(result)} 条记录")
            return result
        else:
            print("❌ 未找到匹配的流量数据")
            return pd.DataFrame()

    def _load_traffic_count_legacy(self, start_time: float, end_time: float) -> pd.DataFrame:
        """使用原始CSV文件进行流量统计加载"""
        print("📈 使用原始CSV文件进行流量统计...")
        
        # 添加数据集时间范围验证
        min_valid_time = 1378944000  # 2013-09-12 00:00:00 UTC
        max_valid_time = 1379548799  # 2013-09-18 23:59:59 UTC
        
        # 检查请求的时间范围是否与数据集时间范围有交集
        if end_time < min_valid_time or start_time > max_valid_time:
            print(f"警告：请求的时间范围 ({start_time}-{end_time}) 超出数据集范围 ({min_valid_time}-{max_valid_time})")
            return pd.DataFrame()
        
        # 生成缓存键
        cache_key = f"legacy_traffic_{start_time}_{end_time}"
        
        # 获取所有CSV文件
        csv_files = self.get_csv_files()
        
        if not csv_files:
            print("未找到CSV文件")
            return pd.DataFrame()
        
        print(f"找到 {len(csv_files)} 个CSV文件，进行流量统计")
        
        # 存储所有符合条件的数据
        all_data = []
        
        for i, file_path in enumerate(csv_files):
            print(f"统计文件 {i+1}/{len(csv_files)}: {os.path.basename(file_path)}")
            
            try:
                # 使用分块读取，但不限制数据量（确保统计完整性）
                chunk_size = 100000
                chunks = pd.read_csv(file_path, chunksize=chunk_size)
                
                for chunk_num, chunk in enumerate(chunks):
                    # 检查必要的列是否存在
                    required_cols = ['UTC', 'COMMADDR']
                    if not all(col in chunk.columns for col in required_cols):
                        continue
                    
                    # 只保留统计需要的列
                    chunk = chunk[required_cols]
                    
                    # 时间过滤
                    filtered_chunk = chunk[(chunk['UTC'] >= start_time) & (chunk['UTC'] <= end_time)]
                    
                    if not filtered_chunk.empty:
                        all_data.append(filtered_chunk)
                        print(f"   处理块 {chunk_num + 1}: {len(filtered_chunk)} 条记录")
            
            except Exception as e:
                print(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
        
        # 合并所有数据
        if all_data:
            result_df = pd.concat(all_data, ignore_index=True)
            print(f"📊 流量统计数据加载完成: {len(result_df)} 条记录")
            return result_df
        else:
            print("❌ 未找到符合条件的流量数据")
            return pd.DataFrame()
    
    def get_hourly_traffic_counts(self, start_time: float, end_time: float) -> List[int]:
        """
        获取指定时间段的每小时车辆统计
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        Returns:
            24个小时的车辆数列表（如果跨度小于24小时则按实际小时数返回）
        """
        # 加载数据
        df = self.load_traffic_count_data(start_time, end_time)
        
        if df.empty:
            # 返回24小时的零值
            return [0] * 24
        
        # 检查时间列
        time_col = self._get_time_column(df)
        if not time_col:
            return [0] * 24
        
        # 🔧 修复时区问题：将UTC时间转换为北京时间（UTC+8）
        print(f"🕐 处理时区转换：UTC → 北京时间（UTC+8）")
        
        # 将UTC时间戳转换为北京时间的小时
        df['datetime_utc'] = pd.to_datetime(df[time_col], unit='s')
        df['datetime_beijing'] = df['datetime_utc'] + pd.Timedelta(hours=8)
        df['hour'] = df['datetime_beijing'].dt.hour
        
        # 按小时聚合车辆数
        hourly_counts = df.groupby('hour').size().reindex(range(24), fill_value=0).tolist()
        
        print(f"📊 小时统计完成: 总计 {sum(hourly_counts)} 车次")
        print(f"🕐 时间转换验证:")
        print(f"   样本UTC时间: {df['datetime_utc'].iloc[0] if len(df) > 0 else 'N/A'}")
        print(f"   样本北京时间: {df['datetime_beijing'].iloc[0] if len(df) > 0 else 'N/A'}")
        
        return hourly_counts
    
    def get_daily_traffic_counts(self, start_time: float, end_time: float, days: int = 7) -> List[Dict[str, Union[str, int]]]:
        """
        获取指定时间段的每日车辆统计
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            days: 天数，默认7天
            
        Returns:
            包含日期和车辆总数的字典列表
        """
        # 加载数据
        df = self.load_traffic_count_data(start_time, end_time)
        
        if df.empty:
            # 返回指定天数的零值 - 修复时区问题
            result = []
            # 🔧 修复：统一使用UTC时间转换为北京时间
            start_datetime_utc = datetime.fromtimestamp(start_time, tz=timezone.utc)
            start_datetime_beijing = start_datetime_utc + timedelta(hours=8)
            
            for i in range(days):
                date_obj = (start_datetime_beijing + timedelta(days=i)).date()
                date_str = date_obj.strftime("%Y-%m-%d")
                result.append({"date": date_str, "totalVehicles": 0})
            return result
        
        # 检查时间列
        time_col = self._get_time_column(df)
        if not time_col:
            return []
        
        # 🔧 修复时区问题：将UTC时间转换为北京时间（UTC+8）
        print(f"🕐 处理每日统计时区转换：UTC → 北京时间（UTC+8）")
        
        # 将UTC时间戳转换为北京时间的日期
        df['datetime_utc'] = pd.to_datetime(df[time_col], unit='s')
        df['datetime_beijing'] = df['datetime_utc'] + pd.Timedelta(hours=8)
        df['date'] = df['datetime_beijing'].dt.date
        
        # 按天聚合车辆数
        daily_counts = df.groupby('date').size().reset_index(name='totalVehicles')
        
        # 🔧 修复：补齐指定天数的数据 - 确保时区一致性
        result = []
        # 使用与数据处理相同的时区转换逻辑
        start_datetime_utc = datetime.fromtimestamp(start_time, tz=timezone.utc)
        start_datetime_beijing = start_datetime_utc + timedelta(hours=8)
        
        for i in range(days):
            date_obj = (start_datetime_beijing + timedelta(days=i)).date()
            date_str = date_obj.strftime("%Y-%m-%d")
            # 查找该日期的车辆数
            matching_count = daily_counts[daily_counts['date'] == date_obj]['totalVehicles']
            count = matching_count.iloc[0] if len(matching_count) > 0 else 0
            result.append({"date": date_str, "totalVehicles": int(count)})
        
        total_vehicles = sum(item['totalVehicles'] for item in result)
        print(f"📊 每日统计完成: {days}天总计 {total_vehicles} 车次")
        
        # 显示时区转换验证信息
        if len(df) > 0:
            print(f"🕐 每日统计时间转换验证:")
            print(f"   样本UTC时间: {df['datetime_utc'].iloc[0]}")
            print(f"   样本北京时间: {df['datetime_beijing'].iloc[0]}")
            print(f"   基准日期范围: {start_datetime_beijing.date()} 到 {(start_datetime_beijing + timedelta(days=days-1)).date()}")
        
        return result
    
    def _get_time_column(self, df: pd.DataFrame) -> Optional[str]:
        """获取时间列名"""
        if 'UTC' in df.columns:
            return 'UTC'
        elif 'timestamp' in df.columns:
            return 'timestamp'
        elif 'TIMESTAMP' in df.columns:
            return 'TIMESTAMP'
        else:
            print(f"错误：未找到时间列，可用列: {list(df.columns)}")
            return None
    
    def clear_cache(self):
        """清除所有缓存"""
        self._hourly_cache.clear()
        self._daily_cache.clear()
        self._weekly_cache.clear()
        print("🧹 流量统计缓存已清除")
    
    def load_metrics_data(self, start_time: float, end_time: float) -> pd.DataFrame:
        """
        专门用于关键指标计算的数据加载，包含速度等额外信息
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        Returns:
            包含时间戳、车辆ID、速度等的DataFrame，用于指标计算
        """
        print(f"📊 加载指标计算数据: {start_time} 到 {end_time}")
        
        # 生成缓存键
        cache_key = f"metrics_data_{start_time}_{end_time}"
        
        # 检查缓存
        if cache_key in self._daily_cache:
            print("📈 使用指标计算缓存")
            return self._daily_cache[cache_key]
        
        # 使用相应的加载方法
        if self.use_preprocessed:
            result = self._load_metrics_data_fast(start_time, end_time)
        else:
            result = self._load_metrics_data_legacy(start_time, end_time)
        
        # 更新缓存
        if len(self._daily_cache) >= self._cache_maxsize:
            oldest_key = next(iter(self._daily_cache))
            del self._daily_cache[oldest_key]
        
        self._daily_cache[cache_key] = result
        print(f"✅ 指标计算数据加载完成: {len(result)} 条记录")
        return result
    
    def _load_metrics_data_fast(self, start_time: float, end_time: float) -> pd.DataFrame:
        """使用预处理数据进行快速指标数据加载"""
        print("🚀 使用预处理数据进行指标计算...")
        
        # 计算需要的时间段（小时级别）
        start_hour = (int(start_time) // 3600) * 3600
        end_hour = (int(end_time) // 3600) * 3600
        
        # 加载相关时间段的数据
        data_frames = []
        current_hour = start_hour
        
        while current_hour <= end_hour:
            filename = f"hour_{int(current_hour)}.parquet"
            filepath = os.path.join(self.processed_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    # 加载指标计算需要的列
                    columns_to_load = ['UTC', 'COMMADDR', 'SPEED', 'LAT', 'LON']
                    df = pd.read_parquet(filepath, columns=columns_to_load)
                    
                    # 精确时间过滤
                    df = df[(df['UTC'] >= start_time) & (df['UTC'] <= end_time)]
                    
                    if not df.empty:
                        data_frames.append(df)
                        print(f"   📁 {filename}: {len(df)} 条记录")
                        
                except Exception as e:
                    print(f"❌ 读取 {filename} 时出错: {e}")
            
            current_hour += 3600  # 下一小时
        
        # 合并数据
        if data_frames:
            result = pd.concat(data_frames, ignore_index=True)
            # 按时间排序
            result = result.sort_values('UTC')
            print(f"⚡ 快速指标数据加载完成，共 {len(result)} 条记录")
            return result
        else:
            print("❌ 未找到匹配的指标数据")
            return pd.DataFrame()

    def _load_metrics_data_legacy(self, start_time: float, end_time: float) -> pd.DataFrame:
        """使用原始CSV文件进行指标数据加载"""
        print("📈 使用原始CSV文件进行指标计算...")
        
        # 添加数据集时间范围验证
        min_valid_time = 1378944000  # 2013-09-12 00:00:00 UTC
        max_valid_time = 1379548799  # 2013-09-18 23:59:59 UTC
        
        # 检查请求的时间范围是否与数据集时间范围有交集
        if end_time < min_valid_time or start_time > max_valid_time:
            print(f"警告：请求的时间范围 ({start_time}-{end_time}) 超出数据集范围 ({min_valid_time}-{max_valid_time})")
            return pd.DataFrame()
        
        # 获取所有CSV文件
        csv_files = self.get_csv_files()
        
        if not csv_files:
            print("未找到CSV文件")
            return pd.DataFrame()
        
        print(f"找到 {len(csv_files)} 个CSV文件，进行指标计算")
        
        # 存储所有符合条件的数据
        all_data = []
        
        for i, file_path in enumerate(csv_files):
            print(f"处理文件 {i+1}/{len(csv_files)}: {os.path.basename(file_path)}")
            
            try:
                # 使用分块读取
                chunk_size = 100000
                chunks = pd.read_csv(file_path, chunksize=chunk_size)
                
                for chunk_num, chunk in enumerate(chunks):
                    # 检查必要的列是否存在
                    required_cols = ['UTC', 'COMMADDR']
                    if not all(col in chunk.columns for col in required_cols):
                        continue
                    
                    # 保留指标计算需要的列
                    available_cols = ['UTC', 'COMMADDR']
                    if 'SPEED' in chunk.columns:
                        available_cols.append('SPEED')
                    if 'LAT' in chunk.columns:
                        available_cols.append('LAT')
                    if 'LON' in chunk.columns:
                        available_cols.append('LON')
                    
                    chunk = chunk[available_cols]
                    
                    # 时间过滤
                    filtered_chunk = chunk[(chunk['UTC'] >= start_time) & (chunk['UTC'] <= end_time)]
                    
                    if not filtered_chunk.empty:
                        all_data.append(filtered_chunk)
                        print(f"   处理块 {chunk_num + 1}: {len(filtered_chunk)} 条记录")
            
            except Exception as e:
                print(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
        
        # 合并所有数据
        if all_data:
            result_df = pd.concat(all_data, ignore_index=True)
            print(f"📊 指标数据加载完成: {len(result_df)} 条记录")
            return result_df
        else:
            print("❌ 未找到符合条件的指标数据")
            return pd.DataFrame()
    
    def calculate_key_metrics(self, start_time: float, end_time: float, hours: int) -> Dict[str, any]:
        """
        计算关键指标
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            hours: 时间跨度（小时）
            
        Returns:
            包含各项指标的字典
        """
        print(f"📊 计算关键指标，时间跨度: {hours} 小时")
        
        # 加载指标计算数据
        df = self.load_metrics_data(start_time, end_time)
        
        if df.empty:
            return {
                "total_vehicles": 0,
                "avg_speed": 0.0,
                "peak_hours": 0.0,
                "unique_vehicles": 0,
                "data_available": False
            }
        
        # 1. 总流量（数据点总数）
        total_vehicles = len(df)
        
        # 2. 平均速度
        avg_speed = 0.0
        if 'SPEED' in df.columns:
            # 过滤掉异常速度值
            valid_speeds = df['SPEED'][(df['SPEED'] >= 0) & (df['SPEED'] <= 200)]
            if len(valid_speeds) > 0:
                avg_speed = valid_speeds.mean()
        
        # 3. 活跃用户（唯一车辆数）
        unique_vehicles = df['COMMADDR'].nunique()
        
        # 4. 高峰时长计算 - 🔧 修复时区问题
        peak_hours = 0.0
        if hours > 0:
            time_col = self._get_time_column(df)
            if time_col:
                print(f"🕐 计算高峰时长，处理时区转换：UTC → 北京时间（UTC+8）")
                
                # 将UTC时间转换为北京时间再按小时分组
                df['datetime_utc'] = pd.to_datetime(df[time_col], unit='s')
                df['datetime_beijing'] = df['datetime_utc'] + pd.Timedelta(hours=8)
                df['hour'] = df['datetime_beijing'].dt.floor('H')
                
                hourly_counts = df.groupby('hour').size()
                
                if len(hourly_counts) > 0:
                    avg_vehicles_per_hour = total_vehicles / hours
                    # 定义高峰为超过平均值1.3倍的小时
                    peak_threshold = avg_vehicles_per_hour * 1.3
                    peak_hours = len([count for count in hourly_counts if count > peak_threshold])
                    
                    print(f"🚦 高峰分析: 平均{avg_vehicles_per_hour:.1f}车次/小时, 阈值{peak_threshold:.1f}, 高峰时段{peak_hours}小时")
        
        return {
            "total_vehicles": total_vehicles,
            "avg_speed": round(avg_speed, 1),
            "peak_hours": round(peak_hours, 1),
            "unique_vehicles": unique_vehicles,
            "data_available": True
        }

    def get_cache_info(self) -> Dict[str, int]:
        """获取缓存状态信息"""
        return {
            "hourly_cache_size": len(self._hourly_cache),
            "daily_cache_size": len(self._daily_cache),
            "weekly_cache_size": len(self._weekly_cache),
            "total_cached_items": len(self._hourly_cache) + len(self._daily_cache) + len(self._weekly_cache)
        }
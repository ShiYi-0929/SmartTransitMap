"""
智能客运分析引擎
提供天气对客流影响分析、载客出租车需求分析、智能客运监控等功能
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict
from scipy import stats
import requests
import json
from pydantic import BaseModel

try:
    # 尝试相对导入（在模块内使用时）
    from .models import (
        WeatherData, PassengerFlowData, TaxiDemandData, WeatherImpactAnalysis,
        TaxiSupplyDemand, SmartPassengerStatistics
    )
except ImportError:
    # 回退到绝对导入（作为脚本运行时）
    from models import (
        WeatherData, PassengerFlowData, TaxiDemandData, WeatherImpactAnalysis,
        TaxiSupplyDemand, SmartPassengerStatistics
    )

logger = logging.getLogger(__name__)

class SmartPassengerEngine:
    """智能客运分析引擎"""
    
    def __init__(self):
        # 天气类型映射（基于济南9月份天气特征）
        self.weather_type_mapping = {
            'sunny': {'level': 1, 'name': '晴天', 'description': '阳光充足，适宜出行'},
            'cloudy': {'level': 2, 'name': '阴天', 'description': '多云天气，对出行影响较小'},
            'light_rain': {'level': 3, 'name': '小雨', 'description': '小雨天气，略微增加出行需求'},
            'heavy_rain': {'level': 4, 'name': '大雨', 'description': '降雨较大，显著影响出行'},
            'snow': {'level': 5, 'name': '雪天', 'description': '雪天出行，需求大幅增加'},
            'foggy': {'level': 4, 'name': '雾天', 'description': '能见度低，影响出行安全'}
        }
        
        # 载客车辆识别参数
        self.taxi_identification_params = {
            'min_speed_change': 5,  # 最小速度变化(km/h)
            'max_stop_duration': 300,  # 最大停车时长(秒)
            'pickup_radius': 100,  # 上客点半径(米)
            'min_trip_distance': 0.5  # 最小载客距离(公里)
        }
    
    def get_weather_data(self, start_time: float, end_time: float) -> List[WeatherData]:
        """获取天气数据（从真实的济南天气数据文件读取）"""
        try:
            import os
            
            # 获取天气数据文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            weather_file_path = os.path.join(current_dir, 'data', 'jn_weather_c.csv')
            
            if not os.path.exists(weather_file_path):
                logger.warning(f"天气数据文件不存在: {weather_file_path}")
                return self._get_fallback_weather_data(start_time, end_time)
            
            # 读取天气数据
            weather_df = pd.read_csv(weather_file_path)
            logger.info(f"成功读取天气数据文件，共 {len(weather_df)} 条记录")
            
            # 转换时间格式 - 修复时间戳转换问题
            try:
                weather_df['timestamp'] = pd.to_datetime(weather_df['Time_new']).astype(np.int64) // 10**9
            except Exception as e:
                logger.warning(f"时间戳转换失败，使用备用方法: {e}")
                # 备用方法：直接使用数值转换
                weather_df['timestamp'] = pd.to_numeric(weather_df['Time_new'], errors='coerce')
                # 如果还是失败，使用默认时间戳
                if weather_df['timestamp'].isna().any():
                    logger.warning("使用默认时间戳")
                    weather_df['timestamp'] = start_time
            
            # 过滤时间范围内的数据
            weather_df_filtered = weather_df[
                (weather_df['timestamp'] >= start_time) & 
                (weather_df['timestamp'] <= end_time)
            ]
            
            if weather_df_filtered.empty:
                logger.warning(f"指定时间范围内没有天气数据 ({start_time} - {end_time})")
                # 如果没有匹配的时间范围，使用全部数据进行演示
                weather_df_filtered = weather_df.head(24)  # 取前24小时数据
                logger.info("使用天气数据文件中的前24小时数据进行演示")
            
            weather_data = []
            for _, row in weather_df_filtered.iterrows():
                # 根据温度和降水量推断天气类型
                weather_type = self._classify_weather_type(
                    temperature=row['Temperature'],
                    humidity=row['Humidity'],
                    precipitation=row['Precip'],
                    wind_speed=row['Wind_Speed']
                )
                
                # 计算能见度（基于湿度和降水量估算）
                visibility = self._estimate_visibility(row['Humidity'], row['Precip'])
                
                weather_data.append(WeatherData(
                    timestamp=row['timestamp'],
                    temperature=row['Temperature'],
                    humidity=row['Humidity'],
                    precipitation=row['Precip'],
                    wind_speed=row['Wind_Speed'],
                    visibility=visibility,
                    weather_type=weather_type,
                    weather_level=self.weather_type_mapping[weather_type]['level']
                ))
            
            logger.info(f"处理了 {len(weather_data)} 条真实天气数据")
            return weather_data
            
        except Exception as e:
            logger.error(f"读取天气数据文件时出错: {str(e)}")
            return self._get_fallback_weather_data(start_time, end_time)
    
    def _classify_weather_type(self, temperature: float, humidity: float, 
                              precipitation: float, wind_speed: float) -> str:
        """根据天气参数分类天气类型"""
        try:
            # 基于真实天气数据的分类逻辑
            if precipitation > 5.0:  # 大雨
                return 'heavy_rain'
            elif precipitation > 0.5:  # 小雨
                return 'light_rain'
            elif humidity > 90 and wind_speed < 2:  # 雾天
                return 'foggy'
            elif humidity > 80:  # 阴天
                return 'cloudy'
            else:  # 晴天
                return 'sunny'
                
        except Exception:
            return 'sunny'  # 默认晴天
    
    def _estimate_visibility(self, humidity: float, precipitation: float) -> float:
        """基于湿度和降水量估算能见度"""
        try:
            # 基础能见度
            base_visibility = 20.0
            
            # 湿度影响
            humidity_factor = max(0.3, (100 - humidity) / 100)
            
            # 降水影响
            if precipitation > 5:
                precip_factor = 0.2
            elif precipitation > 1:
                precip_factor = 0.5
            elif precipitation > 0:
                precip_factor = 0.8
            else:
                precip_factor = 1.0
            
            visibility = base_visibility * humidity_factor * precip_factor
            return max(0.5, min(20.0, visibility))  # 限制在0.5-20km之间
            
        except Exception:
            return 10.0  # 默认能见度
    
    def _get_fallback_weather_data(self, start_time: float, end_time: float) -> List[WeatherData]:
        """获取备用天气数据（模拟实现）"""
        try:
            weather_data = []
            current_time = start_time
            
            logger.info("使用备用模拟天气数据")
            
            # 生成模拟天气数据
            while current_time <= end_time:
                # 模拟不同天气条件
                hour = datetime.fromtimestamp(current_time).hour
                
                if 6 <= hour <= 18:  # 白天
                    if np.random.random() < 0.7:
                        weather_type = 'sunny'
                        temperature = np.random.normal(25, 5)
                        precipitation = 0
                    else:
                        weather_type = 'cloudy'
                        temperature = np.random.normal(22, 3)
                        precipitation = np.random.exponential(0.5)
                else:  # 夜晚
                    temperature = np.random.normal(18, 3)
                    if np.random.random() < 0.2:
                        weather_type = 'light_rain'
                        precipitation = np.random.exponential(2)
                    else:
                        weather_type = 'cloudy'
                        precipitation = 0
                
                weather_data.append(WeatherData(
                    timestamp=current_time,
                    temperature=max(0, temperature),
                    humidity=np.random.uniform(40, 90),
                    precipitation=max(0, precipitation),
                    wind_speed=np.random.uniform(0, 15),
                    visibility=np.random.uniform(5, 20),
                    weather_type=weather_type,
                    weather_level=self.weather_type_mapping[weather_type]['level']
                ))
                
                current_time += 3600  # 每小时一条数据
            
            logger.info(f"生成了 {len(weather_data)} 条备用天气数据")
            return weather_data
            
        except Exception as e:
            logger.error(f"生成备用天气数据时出错: {str(e)}")
            return []
    
    def identify_passenger_vehicles(self, trajectory_data: pd.DataFrame) -> List[PassengerFlowData]:
        """识别载客车辆和客流数据"""
        try:
            passenger_flows = []
            
            # 处理列名重复问题：如果同时存在timestamp和UTC，优先使用UTC
            if 'timestamp' in trajectory_data.columns and 'UTC' in trajectory_data.columns:
                # 删除重复的timestamp列，保留UTC
                trajectory_data = trajectory_data.drop(columns=['timestamp'])
            
            # 标准化列名映射
            column_mapping = {
                'COMMADDR': 'vehicle_id',
                'UTC': 'timestamp',
                'lat': 'latitude',
                'lon': 'longitude',
                'SPEED': 'speed',
                'TFLAG': 'tflag',
                'is_occupied': 'is_occupied'
            }
            
            # 重命名列
            trajectory_data = trajectory_data.rename(columns=column_mapping)
            
            # 确保必要的列存在
            required_columns = ['vehicle_id', 'timestamp', 'latitude', 'longitude']
            missing_columns = [col for col in required_columns if col not in trajectory_data.columns]
            if missing_columns:
                logger.error(f"缺少必要的列: {missing_columns}")
                return []
            
            # 按车辆ID分组处理
            for vehicle_id in trajectory_data['vehicle_id'].unique():
                vehicle_data = trajectory_data[trajectory_data['vehicle_id'] == vehicle_id].sort_values('timestamp')
                
                # 分析轨迹特征识别载客行为
                passenger_segments = self._analyze_passenger_segments(vehicle_data)
                
                for segment in passenger_segments:
                    passenger_flows.append(PassengerFlowData(
                        timestamp=segment['start_time'],
                        location={"lat": segment['start_lat'], "lng": segment['start_lng']},
                        passenger_count=segment['passenger_count'],
                        vehicle_type=self._classify_vehicle_type(vehicle_data),
                        is_pickup=True,
                        zone_id=self._get_zone_id(segment['start_lat'], segment['start_lng'])
                    ))
                    
                    passenger_flows.append(PassengerFlowData(
                        timestamp=segment['end_time'],
                        location={"lat": segment['end_lat'], "lng": segment['end_lng']},
                        passenger_count=segment['passenger_count'],
                        vehicle_type=self._classify_vehicle_type(vehicle_data),
                        is_pickup=False,
                        zone_id=self._get_zone_id(segment['end_lat'], segment['end_lng'])
                    ))
            
            logger.info(f"识别了 {len(passenger_flows)} 条客流数据")
            return passenger_flows
            
        except Exception as e:
            logger.error(f"识别载客车辆时出错: {str(e)}")
            return []
    
    def analyze_taxi_demand(self, trajectory_data: pd.DataFrame, 
                          time_resolution: int = 15) -> List[TaxiDemandData]:
        """分析出租车需求"""
        try:
            taxi_demand_data = []
            
            # 处理列名重复问题：如果同时存在timestamp和UTC，优先使用UTC
            if 'timestamp' in trajectory_data.columns and 'UTC' in trajectory_data.columns:
                # 删除重复的timestamp列，保留UTC
                trajectory_data = trajectory_data.drop(columns=['timestamp'])
            
            # 标准化列名映射
            column_mapping = {
                'COMMADDR': 'vehicle_id',
                'UTC': 'timestamp',
                'lat': 'latitude',
                'lon': 'longitude',
                'SPEED': 'speed',
                'TFLAG': 'tflag',
                'is_occupied': 'is_occupied'
            }
            
            # 重命名列
            trajectory_data = trajectory_data.rename(columns=column_mapping)
            
            # 确保必要的列存在
            required_columns = ['vehicle_id', 'timestamp', 'latitude', 'longitude']
            missing_columns = [col for col in required_columns if col not in trajectory_data.columns]
            if missing_columns:
                logger.error(f"缺少必要的列: {missing_columns}")
                return []
            
            # 识别出租车轨迹
            taxi_data = self._filter_taxi_trajectories(trajectory_data)
            
            # 按时间窗口分析 - 修复时间戳转换问题
            try:
                # 确保timestamp是数值类型
                if hasattr(taxi_data['timestamp'], 'dtype'):
                    if taxi_data['timestamp'].dtype == 'object':
                        taxi_data['timestamp'] = pd.to_numeric(taxi_data['timestamp'], errors='coerce')
                else:
                    # 如果不是Series，直接转换
                    taxi_data['timestamp'] = pd.to_numeric(taxi_data['timestamp'], errors='coerce')
                
            taxi_data['time_window'] = pd.to_datetime(taxi_data['timestamp'], unit='s')
            taxi_data['time_window'] = taxi_data['time_window'].dt.floor(f'{time_resolution}min')
            except Exception as e:
                logger.error(f"时间窗口处理失败: {e}")
                # 如果失败，使用默认时间窗口
                taxi_data['time_window'] = pd.Timestamp.now().floor(f'{time_resolution}min')
            
            # 空间网格化
            grid_size = 0.01  # 约1km
            taxi_data['grid_lat'] = (taxi_data['latitude'] / grid_size).astype(int) * grid_size
            taxi_data['grid_lng'] = (taxi_data['longitude'] / grid_size).astype(int) * grid_size
            
            # 按时间窗口和网格分组
            for (time_window, grid_lat, grid_lng), group in taxi_data.groupby(['time_window', 'grid_lat', 'grid_lng']):
                loaded_taxis, empty_taxis = self._classify_taxi_status(group)
                total_orders = self._estimate_orders(group)
                
                demand_index = min(1.0, total_orders / max(loaded_taxis + empty_taxis, 1))
                supply_ratio = loaded_taxis / max(total_orders, 1)
                
                taxi_demand_data.append(TaxiDemandData(
                    timestamp=time_window.timestamp(),
                    location={"lat": grid_lat, "lng": grid_lng},
                    loaded_taxis=loaded_taxis,
                    empty_taxis=empty_taxis,
                    total_orders=total_orders,
                    waiting_orders=max(0, total_orders - loaded_taxis),
                    demand_index=demand_index,
                    supply_ratio=supply_ratio
                ))
            
            logger.info(f"分析了 {len(taxi_demand_data)} 个区域的出租车需求")
            return taxi_demand_data
            
        except Exception as e:
            logger.error(f"分析出租车需求时出错: {str(e)}")
            return []
    
    def analyze_weather_impact(self, passenger_flows: List[PassengerFlowData],
                             weather_data: List[WeatherData]) -> List[WeatherImpactAnalysis]:
        """分析天气对客流的影响"""
        try:
            impact_analyses = []
            
            # 按天气类型分组分析
            weather_groups = defaultdict(list)
            for weather in weather_data:
                weather_groups[weather.weather_type].append(weather)
            
            for weather_type, weather_list in weather_groups.items():
                if not weather_list:
                    continue
                
                # 计算该天气条件下的客流量
                weather_timestamps = [w.timestamp for w in weather_list]
                weather_passenger_flows = [
                    pf for pf in passenger_flows 
                    if any(abs(pf.timestamp - wt) < 1800 for wt in weather_timestamps)  # 30分钟内
                ]
                
                actual_flow = sum(pf.passenger_count for pf in weather_passenger_flows)
                
                # 计算基准客流量（晴天）
                sunny_flows = [
                    pf for pf in passenger_flows
                    if any(w.weather_type == 'sunny' and abs(pf.timestamp - w.timestamp) < 1800 
                          for w in weather_data)
                ]
                baseline_flow = sum(pf.passenger_count for pf in sunny_flows) if sunny_flows else actual_flow
                
                # 计算影响
                if baseline_flow > 0:
                    impact_percentage = ((actual_flow - baseline_flow) / baseline_flow) * 100
                else:
                    impact_percentage = 0
                
                # 计算相关系数
                correlation_coefficient = self._calculate_weather_correlation(
                    weather_list, weather_passenger_flows
                )
                
                # 确定影响等级
                impact_level = "low"
                if abs(impact_percentage) > 20:
                    impact_level = "high"
                elif abs(impact_percentage) > 10:
                    impact_level = "medium"
                
                impact_analyses.append(WeatherImpactAnalysis(
                    weather_condition=weather_type,
                    baseline_flow=baseline_flow,
                    actual_flow=actual_flow,
                    impact_percentage=impact_percentage,
                    correlation_coefficient=correlation_coefficient,
                    impact_level=impact_level
                ))
            
            logger.info(f"完成了 {len(impact_analyses)} 种天气条件的影响分析")
            return impact_analyses
            
        except Exception as e:
            logger.error(f"分析天气影响时出错: {str(e)}")
            return []
    
    def calculate_taxi_supply_demand(self, taxi_demand_data: List[TaxiDemandData],
                                   time_period: str = "1h") -> List[TaxiSupplyDemand]:
        """计算出租车供需分析"""
        try:
            supply_demand_analyses = []
            
            # 按时间段聚合数据
            time_groups = self._group_by_time_period(taxi_demand_data, time_period)
            
            for period, data_list in time_groups.items():
                total_loaded_taxis = sum(d.loaded_taxis for d in data_list)
                total_demand = sum(d.total_orders for d in data_list)
                
                supply_demand_ratio = total_loaded_taxis / max(total_demand, 1)
                
                # 识别热点区域（高需求区域）
                hotspot_areas = [
                    {
                        "location": d.location,
                        "demand_index": d.demand_index,
                        "orders": d.total_orders
                    }
                    for d in data_list if d.demand_index > 0.7
                ]
                
                # 识别供应不足区域
                shortage_areas = [
                    {
                        "location": d.location,
                        "supply_ratio": d.supply_ratio,
                        "waiting_orders": d.waiting_orders
                    }
                    for d in data_list if d.supply_ratio < 0.5 and d.waiting_orders > 0
                ]
                
                supply_demand_analyses.append(TaxiSupplyDemand(
                    time_period=period,
                    total_loaded_taxis=total_loaded_taxis,
                    total_demand=total_demand,
                    supply_demand_ratio=supply_demand_ratio,
                    hotspot_areas=hotspot_areas,
                    shortage_areas=shortage_areas
                ))
            
            logger.info(f"完成了 {len(supply_demand_analyses)} 个时段的供需分析")
            return supply_demand_analyses
            
        except Exception as e:
            logger.error(f"计算出租车供需时出错: {str(e)}")
            return []
    
    def generate_smart_passenger_statistics(self, 
                                          passenger_flows: List[PassengerFlowData],
                                          weather_data: List[WeatherData],
                                          taxi_demand_data: List[TaxiDemandData],
                                          weather_impact: List[WeatherImpactAnalysis],
                                          time_range: Tuple[float, float]) -> SmartPassengerStatistics:
        """生成智能客运统计数据"""
        try:
            total_passengers = sum(pf.passenger_count for pf in passenger_flows)
            
            # 客流统计
            passenger_flow_stats = {
                "total_pickup_points": len([pf for pf in passenger_flows if pf.is_pickup]),
                "total_dropoff_points": len([pf for pf in passenger_flows if not pf.is_pickup]),
                "avg_passenger_per_trip": np.mean([pf.passenger_count for pf in passenger_flows]) if passenger_flows else 0,
                "peak_hour_flow": max([pf.passenger_count for pf in passenger_flows]) if passenger_flows else 0
            }
            
            # 出租车需求统计
            taxi_demand_stats = {
                "total_loaded_taxis": sum(td.loaded_taxis for td in taxi_demand_data),
                "total_empty_taxis": sum(td.empty_taxis for td in taxi_demand_data),
                "avg_demand_index": np.mean([td.demand_index for td in taxi_demand_data]) if taxi_demand_data else 0,
                "avg_supply_ratio": np.mean([td.supply_ratio for td in taxi_demand_data]) if taxi_demand_data else 0
            }
            
            # 天气影响摘要
            weather_impact_summary = {}
            for impact in weather_impact:
                weather_impact_summary[impact.weather_condition] = impact.impact_percentage
            
            # 识别高峰需求时段
            peak_demand_periods = self._identify_peak_periods(passenger_flows, taxi_demand_data)
            
            return SmartPassengerStatistics(
                time_range={"start": time_range[0], "end": time_range[1]},
                total_passengers=total_passengers,
                weather_conditions=weather_data,
                passenger_flow_stats=passenger_flow_stats,
                taxi_demand_stats=taxi_demand_stats,
                weather_impact_summary=weather_impact_summary,
                peak_demand_periods=peak_demand_periods
            )
            
        except Exception as e:
            logger.error(f"生成智能客运统计时出错: {str(e)}")
            return SmartPassengerStatistics(
                time_range={"start": time_range[0], "end": time_range[1]},
                total_passengers=0,
                weather_conditions=[],
                passenger_flow_stats={},
                taxi_demand_stats={},
                weather_impact_summary={},
                peak_demand_periods=[]
            )
    
    # 私有辅助方法
    
    def _analyze_passenger_segments(self, vehicle_data: pd.DataFrame) -> List[Dict]:
        """分析载客路段"""
        segments = []
        
        # 标准化列名映射
        column_mapping = {
            'COMMADDR': 'vehicle_id',
            'UTC': 'timestamp',
            'lat': 'latitude',
            'lon': 'longitude',
            'SPEED': 'speed',
            'TFLAG': 'tflag',
            'is_occupied': 'is_occupied'
        }
        
        # 重命名列
        vehicle_data = vehicle_data.rename(columns=column_mapping)
        
        # 使用真实的载客状态字段
        if len(vehicle_data) >= 2:
            # 检查载客状态字段
            if 'is_occupied' in vehicle_data.columns:
                # 使用is_occupied字段
                loaded_records = vehicle_data[vehicle_data['is_occupied'] == True]
            elif 'tflag' in vehicle_data.columns:
                # 使用TFLAG字段
                loaded_records = vehicle_data[vehicle_data['tflag'] == 268435456]
            else:
                # 如果没有载客状态字段，使用距离和时长判断
            if self._is_passenger_trip(vehicle_data):
                    loaded_records = vehicle_data
                else:
                    loaded_records = pd.DataFrame()
            
            # 如果有载客记录，生成载客路段
            if not loaded_records.empty:
                start_point = loaded_records.iloc[0]
                end_point = loaded_records.iloc[-1]
                
                # 载客数量就是载客记录的数量
                passenger_count = len(loaded_records)
                
                segments.append({
                    'start_time': start_point['timestamp'],
                    'end_time': end_point['timestamp'],
                    'start_lat': start_point['latitude'],
                    'start_lng': start_point['longitude'],
                    'end_lat': end_point['latitude'],
                    'end_lng': end_point['longitude'],
                    'passenger_count': passenger_count  # 使用真实载客数量
                })
        
        return segments
    
    def _classify_vehicle_type(self, vehicle_data: pd.DataFrame) -> str:
        """分类车辆类型"""
        # 简化逻辑，实际可基于轨迹特征分类
        return "taxi"
    
    def _get_zone_id(self, lat: float, lng: float) -> str:
        """获取区域ID"""
        # 简化的区域划分
        return f"zone_{int(lat*100)}_{int(lng*100)}"
    
    def _filter_taxi_trajectories(self, trajectory_data: pd.DataFrame) -> pd.DataFrame:
        """过滤出租车轨迹"""
        # 这里简化处理，实际可基于更复杂的特征识别
        return trajectory_data.copy()
    
    def _classify_taxi_status(self, group_data: pd.DataFrame) -> Tuple[int, int]:
        """分类出租车载客状态（基于真实数据）"""
        # 标准化列名映射
        column_mapping = {
            'COMMADDR': 'vehicle_id',
            'UTC': 'timestamp',
            'lat': 'latitude',
            'lon': 'longitude',
            'SPEED': 'speed',
            'TFLAG': 'tflag',
            'is_occupied': 'is_occupied'
        }
        
        # 重命名列
        group_data = group_data.rename(columns=column_mapping)
        
        # 优先使用is_occupied字段
        if 'is_occupied' in group_data.columns:
            loaded_taxis = group_data[group_data['is_occupied'] == True]['vehicle_id'].nunique()
            empty_taxis = group_data[group_data['is_occupied'] == False]['vehicle_id'].nunique()
        # 兼容tflag字段
        elif 'tflag' in group_data.columns:
            loaded_taxis = group_data[group_data['tflag'] == 268435456]['vehicle_id'].nunique()
            empty_taxis = group_data[group_data['tflag'] == 0]['vehicle_id'].nunique()
        else:
            # 无法判断时全部视为空载
            loaded_taxis = 0
            empty_taxis = group_data['vehicle_id'].nunique()
        return loaded_taxis, empty_taxis
    
    def _estimate_orders(self, group_data: pd.DataFrame) -> int:
        """估算订单数量"""
        # 简化逻辑：基于车辆数量估算
        return int(len(group_data['vehicle_id'].unique()) * np.random.uniform(0.8, 1.5))
    
    def _is_passenger_trip(self, vehicle_data: pd.DataFrame) -> bool:
        """判断是否为载客行程"""
        # 简化判断逻辑
        if len(vehicle_data) < 2:
            return False
        
        # 基于行程距离和时长判断
        distance = self._calculate_distance(
            vehicle_data.iloc[0]['latitude'], vehicle_data.iloc[0]['longitude'],
            vehicle_data.iloc[-1]['latitude'], vehicle_data.iloc[-1]['longitude']
        )
        duration = vehicle_data.iloc[-1]['timestamp'] - vehicle_data.iloc[0]['timestamp']
        
        return distance > 0.5 and duration > 300  # 距离>0.5km，时长>5分钟
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """计算两点间距离（公里）"""
        from geopy.distance import geodesic
        return geodesic((lat1, lng1), (lat2, lng2)).kilometers
    
    def _calculate_weather_correlation(self, weather_list: List[WeatherData], 
                                     passenger_flows: List[PassengerFlowData]) -> float:
        """计算天气与客流的相关系数"""
        if not weather_list or not passenger_flows:
            return 0.0
        
        # 简化计算
        weather_levels = [w.weather_level for w in weather_list]
        flow_counts = [pf.passenger_count for pf in passenger_flows[:len(weather_levels)]]
        
        if len(weather_levels) == len(flow_counts) and len(weather_levels) > 1:
            correlation, _ = stats.pearsonr(weather_levels, flow_counts)
            return correlation if not np.isnan(correlation) else 0.0
        
        return 0.0
    
    def _group_by_time_period(self, taxi_demand_data: List[TaxiDemandData], 
                            period: str) -> Dict[str, List[TaxiDemandData]]:
        """按时间段分组数据"""
        groups = defaultdict(list)
        
        for data in taxi_demand_data:
            dt = datetime.fromtimestamp(data.timestamp)
            
            if period == "1h":
                key = dt.strftime("%Y-%m-%d %H:00")
            elif period == "30m":
                minute = "00" if dt.minute < 30 else "30"
                key = dt.strftime(f"%Y-%m-%d %H:{minute}")
            else:  # 默认1小时
                key = dt.strftime("%Y-%m-%d %H:00")
            
            groups[key].append(data)
        
        return dict(groups)
    
    def _identify_peak_periods(self, passenger_flows: List[PassengerFlowData],
                             taxi_demand_data: List[TaxiDemandData]) -> List[Dict[str, Any]]:
        """识别高峰需求时段"""
        peak_periods = []
        
        # 按小时统计客流量
        hourly_flows = defaultdict(int)
        for pf in passenger_flows:
            hour = datetime.fromtimestamp(pf.timestamp).hour
            hourly_flows[hour] += pf.passenger_count
        
        # 找出高峰时段（客流量超过平均值的1.5倍）
        if hourly_flows:
            avg_flow = np.mean(list(hourly_flows.values()))
            for hour, flow in hourly_flows.items():
                if flow > avg_flow * 1.5:
                    peak_periods.append({
                        "period": f"{hour:02d}:00-{hour+1:02d}:00",
                        "passenger_flow": flow,
                        "peak_level": "high" if flow > avg_flow * 2 else "medium"
                    })
        
        return peak_periods

class HourlyWeatherImpact(BaseModel):
    hour: int
    weather_condition: str
    temperature: float
    humidity: float
    precipitation: float
    loaded_vehicles: int
    total_vehicles: int
    impact_factor: float
    impact_description: str

class DailyWeatherImpact(BaseModel):
    date: str
    hourly_impacts: List[HourlyWeatherImpact]
    daily_summary: Dict[str, Any]

def analyze_daily_weather_impact(self, trajectory_data: pd.DataFrame, weather_data: List[WeatherData]) -> List[DailyWeatherImpact]:
    """分析每天每小时的天气影响"""
    from collections import defaultdict
    from datetime import datetime
    # 1. 按日期分组天气
    weather_by_day = defaultdict(list)
    for w in weather_data:
        date_str = datetime.fromtimestamp(w.timestamp).strftime('%Y-%m-%d')
        weather_by_day[date_str].append(w)
    # 2. 按日期分组轨迹
    trajectory_data['date'] = pd.to_datetime(trajectory_data['timestamp'], unit='s').dt.strftime('%Y-%m-%d')
    trajectory_data['hour'] = pd.to_datetime(trajectory_data['timestamp'], unit='s').dt.hour
    traj_by_day = {d: df for d, df in trajectory_data.groupby('date')}
    # 3. 每天分析
    daily_results = []
    for date, weather_list in weather_by_day.items():
        day_traj = traj_by_day.get(date, pd.DataFrame())
        hourly_impacts = []
        for hour in range(24):
            # 找到该小时的天气
            hour_weather = next((w for w in weather_list if datetime.fromtimestamp(w.timestamp).hour == hour), None)
            if hour_weather is None:
                continue
            # 该小时的车辆
            hour_traj = day_traj[day_traj['hour'] == hour] if not day_traj.empty else pd.DataFrame()
            loaded_vehicles = hour_traj[hour_traj['is_occupied'] == True]['vehicle_id'].nunique() if not hour_traj.empty else 0
            total_vehicles = hour_traj['vehicle_id'].nunique() if not hour_traj.empty else 0
            impact_factor = (loaded_vehicles / total_vehicles) if total_vehicles > 0 else 0
            impact_description = f"载客率：{impact_factor:.2%}，温度：{hour_weather.temperature}°C，降水：{hour_weather.precipitation}mm"
            hourly_impacts.append(HourlyWeatherImpact(
                hour=hour,
                weather_condition=hour_weather.weather_type,
                temperature=hour_weather.temperature,
                humidity=hour_weather.humidity,
                precipitation=hour_weather.precipitation,
                loaded_vehicles=loaded_vehicles,
                total_vehicles=total_vehicles,
                impact_factor=impact_factor,
                impact_description=impact_description
            ))
        # 每日汇总
        avg_impact = sum(h.impact_factor for h in hourly_impacts) / len(hourly_impacts) if hourly_impacts else 0
        daily_summary = {
            'avg_impact_factor': avg_impact,
            'max_impact_hour': max(hourly_impacts, key=lambda h: h.impact_factor).hour if hourly_impacts else None,
            'min_impact_hour': min(hourly_impacts, key=lambda h: h.impact_factor).hour if hourly_impacts else None
        }
        daily_results.append(DailyWeatherImpact(
            date=date,
            hourly_impacts=hourly_impacts,
            daily_summary=daily_summary
        ))
    return daily_results
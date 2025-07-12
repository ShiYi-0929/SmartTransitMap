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
        """分析路段交通数据"""
        try:
            traffic_data = []
            
            # 创建路段空间索引
            segment_map = self._create_segment_spatial_index(road_segments)
            
            # 按时间窗口聚合数据（15分钟窗口）
            trajectory_data['time_window'] = pd.to_datetime(trajectory_data['timestamp'], unit='s')
            trajectory_data['time_window'] = trajectory_data['time_window'].dt.floor('15min')
            
            for time_window in trajectory_data['time_window'].unique():
                window_data = trajectory_data[trajectory_data['time_window'] == time_window]
                
                for segment in road_segments:
                    segment_traffic = self._calculate_segment_traffic(
                        window_data, segment, time_window.timestamp()
                    )
                    if segment_traffic:
                        traffic_data.append(segment_traffic)
            
            logger.info(f"分析了 {len(traffic_data)} 条路段交通数据")
            return traffic_data
            
        except Exception as e:
            logger.error(f"分析路段交通数据时出错: {str(e)}")
            return []
    
    def _create_segment_spatial_index(self, segments: List[RoadSegment]) -> Dict:
        """创建路段空间索引"""
        segment_map = {}
        for segment in segments:
            # 简化的空间索引，基于起点坐标的网格
            grid_lat = round(segment.start_point['lat'], 3)
            grid_lng = round(segment.start_point['lng'], 3)
            grid_key = f"{grid_lat},{grid_lng}"
            
            if grid_key not in segment_map:
                segment_map[grid_key] = []
            segment_map[grid_key].append(segment)
        
        return segment_map
    
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
            avg_speed = np.mean(valid_speeds)
            min_speed = np.min(valid_speeds)
            max_speed = np.max(valid_speeds)
            
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
            
            total_vehicles = sum(vehicles)
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
            speed_score = min(100, (avg_speed / free_flow_speed) * 100)
            flow_score = min(100, (off_peak_flow / max(peak_hour_flow, 1)) * 100)
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
            speed_counts = defaultdict(int)
            total_records = 0
            
            for data in traffic_data:
                speed = data.avg_speed
                total_records += data.vehicle_count
                
                if speed < 20:
                    speed_counts["0-20"] += data.vehicle_count
                elif speed < 40:
                    speed_counts["20-40"] += data.vehicle_count
                elif speed < 60:
                    speed_counts["40-60"] += data.vehicle_count
                elif speed < 80:
                    speed_counts["60-80"] += data.vehicle_count
                elif speed < 100:
                    speed_counts["80-100"] += data.vehicle_count
                else:
                    speed_counts["100+"] += data.vehicle_count
            
            distributions = []
            for speed_range in speed_ranges:
                count = speed_counts[speed_range]
                percentage = (count / total_records * 100) if total_records > 0 else 0
                
                distributions.append(SpeedDistribution(
                    speed_range=speed_range,
                    vehicle_count=count,
                    percentage=percentage
                ))
            
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
                    "free": 40,      # >40km/h 为畅通
                    "moderate": 25,  # 25-40km/h 为缓慢  
                    "heavy": 15,     # 15-25km/h 为拥堵
                    "jam": 0         # <15km/h 为严重拥堵
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
                    
                    # 确定拥堵等级
                    congestion_level = self._classify_congestion_level(avg_speed, congestion_threshold)
                    
                    # 确定道路类型
                    avg_distance = grid_orders['distance_km'].mean()
                    road_type = "short_medium_trip" if avg_distance <= 8 else "long_trip"
                    
                    # 计算置信度（基于订单数量）
                    confidence_score = min(1.0, order_count / 20)  # 20个订单以上置信度为1
                    
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
                    intensity = self._speed_to_intensity(avg_speed, congestion_threshold)
                    
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
        """从轨迹数据中提取订单信息"""
        try:
            orders_data = []
            
            # 添加调试信息
            total_vehicles = trajectory_data['vehicle_id'].nunique()
            logger.info(f"开始处理 {total_vehicles} 辆车的轨迹数据")
            
            # 按车辆分组处理
            processed_vehicles = 0
            for vehicle_id in trajectory_data['vehicle_id'].unique():
                vehicle_data = trajectory_data[trajectory_data['vehicle_id'] == vehicle_id].copy()
                vehicle_data = vehicle_data.sort_values('timestamp')
                
                if len(vehicle_data) < 2:
                    continue
                
                processed_vehicles += 1
                if processed_vehicles <= 3:  # 只调试前3辆车
                    logger.info(f"处理车辆 {vehicle_id}: {len(vehicle_data)} 条记录")
                    logger.info(f"时间范围: {vehicle_data['timestamp'].min()} - {vehicle_data['timestamp'].max()}")
                
                # 检测行程段（基于停车时间间隔）
                time_gaps = vehicle_data['timestamp'].diff()
                # 处理时间间隔：如果是数值类型，直接比较；如果是时间类型，转换为秒
                if pd.api.types.is_numeric_dtype(time_gaps):
                    # 数值类型时间戳，直接比较秒数
                    # 采样数据间隔可能很大，所以使用更大的间隔来分割行程
                    trip_breaks = time_gaps > 3600  # 1小时间隔认为是新行程
                    if processed_vehicles <= 3:
                        logger.info(f"车辆 {vehicle_id} 时间间隔: {time_gaps.dropna().head(5).tolist()}")
                        logger.info(f"车辆 {vehicle_id} 行程分割点: {trip_breaks.sum()} 个")
                else:
                    # pandas时间类型，使用Timedelta
                    trip_breaks = time_gaps > pd.Timedelta(seconds=3600)
                
                trip_id = 0
                current_trip_start = 0
                
                for i, is_break in enumerate(trip_breaks):
                    # 跳过第一个NaN值
                    if i == 0:
                        continue
                        
                    if is_break or i == len(vehicle_data) - 1:
                        # 结束当前行程
                        if i > current_trip_start:
                            trip_data = vehicle_data.iloc[current_trip_start:i+1]
                            order = self._create_order_from_trip(trip_data, vehicle_id, trip_id)
                            if order:
                                orders_data.append(order)
                        
                        trip_id += 1
                        current_trip_start = i
                
                # 处理最后一个行程段
                if current_trip_start < len(vehicle_data) - 1:
                    trip_data = vehicle_data.iloc[current_trip_start:]
                    order = self._create_order_from_trip(trip_data, vehicle_id, trip_id)
                    if order:
                        orders_data.append(order)
            
            logger.info(f"从 {trajectory_data['vehicle_id'].nunique()} 辆车的轨迹中提取了 {len(orders_data)} 个订单")
            return orders_data
            
        except Exception as e:
            logger.error(f"提取订单信息时出错: {str(e)}")
            return []
    
    def _create_order_from_trip(self, trip_data: pd.DataFrame, vehicle_id: str, trip_id: int) -> Optional[Dict]:
        """从行程数据创建订单"""
        try:
            if len(trip_data) < 2:
                return None
            
            start_point = trip_data.iloc[0]
            end_point = trip_data.iloc[-1]
            
            start_time = start_point['timestamp']
            end_time = end_point['timestamp']
            # 处理时间戳：如果是pandas时间戳，转换为Unix时间戳
            if hasattr(start_time, 'timestamp'):
                start_timestamp = start_time.timestamp()
                end_timestamp = end_time.timestamp()
            else:
                # 如果已经是Unix时间戳
                start_timestamp = float(start_time)
                end_timestamp = float(end_time)
            duration_min = (end_timestamp - start_timestamp) / 60
            
            # 过滤过短的行程（小于1分钟）- 放宽条件
            if duration_min < 1:
                logger.debug(f"过滤过短行程: {duration_min:.2f}分钟 < 1分钟")
                return None
            
            # 计算距离
            start_lat = start_point['latitude']
            start_lng = start_point['longitude']
            end_lat = end_point['latitude']
            end_lng = end_point['longitude']
            
            distance_km = self._calculate_distance(start_lat, start_lng, end_lat, end_lng)
            
            # 过滤过短的距离（小于0.05km）- 放宽条件
            if distance_km < 0.05:
                logger.debug(f"过滤过短距离: {distance_km:.3f}km < 0.05km")
                return None
            
            # 调试信息：记录成功创建的订单
            logger.debug(f"创建订单: 车辆{vehicle_id}, 行程{trip_id}, 距离{distance_km:.2f}km, 时长{duration_min:.2f}分钟")
            
            return {
                'order_id': f"{vehicle_id}_{trip_id}",
                'vehicle_id': vehicle_id,
                'start_time': start_timestamp,
                'end_time': end_timestamp,
                'duration_min': duration_min,
                'distance_km': distance_km,
                'start_lat': start_lat,
                'start_lng': start_lng,
                'end_lat': end_lat,
                'end_lng': end_lng
            }
            
        except Exception as e:
            logger.error(f"创建订单时出错: {str(e)}")
            return None
    
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
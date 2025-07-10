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
    RoadNetworkAnalysis, SpeedDistribution, TrafficFlowPattern
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
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any
from datetime import datetime

# 请求模型
class TimeRangeRequest(BaseModel):
    """时间范围请求模型"""
    start_time: float = Field(..., description="开始时间戳（UTC）")
    end_time: float = Field(..., description="结束时间戳（UTC）")
    
class TrafficQueryRequest(TimeRangeRequest):
    """交通数据查询请求"""
    vehicle_id: Optional[str] = Field(None, description="车辆ID，可选")
    view_type: str = Field("distribution", description="视图类型：distribution, trajectory, heatmap")
    map_style: Optional[str] = Field("blue", description="地图样式")
    
class HeatmapRequest(TimeRangeRequest):
    """热力图数据请求"""
    resolution: Optional[float] = Field(0.001, description="热力图分辨率，经纬度网格大小")
    
class TrackQueryRequest(TimeRangeRequest):
    """轨迹查询请求"""
    vehicle_id: str = Field(..., description="车辆ID")
    
class StatisticsRequest(TimeRangeRequest):
    """统计数据请求"""
    group_by: Optional[str] = Field("hour", description="分组方式：hour, day, week, month")

# 响应模型
class Point(BaseModel):
    """地理坐标点"""
    lng: float
    lat: float
    
class TrackPoint(Point):
    """轨迹点"""
    timestamp: float
    speed: Optional[float] = None
    direction: Optional[float] = None
    status: Optional[str] = None
    
class HeatmapPoint(Point):
    """热力图点"""
    count: int = 1
    
class VehicleTrack(BaseModel):
    """车辆轨迹"""
    vehicle_id: str
    points: List[TrackPoint]
    start_time: float
    end_time: float
    distance: Optional[float] = None
    
class TrafficStatItem(BaseModel):
    """交通统计项"""
    key: str
    value: Union[int, float, str]
    
class TrafficOverview(BaseModel):
    """交通数据总览"""
    total_vehicles: int
    total_points: int
    active_vehicles: int
    time_span: str
    coverage_area: str
    average_speed: float
    
class TimeDistribution(BaseModel):
    """时间分布"""
    time_key: str  # 小时、日期等
    count: int
    
class TrafficResponse(BaseModel):
    """交通数据响应基类"""
    success: bool = True
    message: Optional[str] = None
    
class TrafficDataResponse(TrafficResponse):
    """交通数据响应"""
    view_type: str
    data: Any
    stats: Optional[TrafficOverview] = None
    
class HeatmapResponse(TrafficResponse):
    """热力图响应"""
    points: List[HeatmapPoint]
    
class TracksResponse(TrafficResponse):
    """轨迹响应"""
    tracks: List[VehicleTrack]
    
class StatisticsResponse(TrafficResponse):
    """统计数据响应"""
    overview: TrafficOverview
    time_distribution: List[TimeDistribution]
    vehicle_distribution: Optional[Dict[str, int]] = None

# 新增时空分析相关模型

class ODPair(BaseModel):
    """起点终点对模型"""
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float
    vehicle_id: str
    start_time: float
    end_time: float
    duration: float
    distance: Optional[float] = None
    trip_id: Optional[str] = None

class SpatialCluster(BaseModel):
    """空间聚类结果模型"""
    cluster_id: int
    center_lat: float
    center_lng: float
    points: List[Dict[str, float]]  # [{"lat": float, "lng": float, "weight": float}]
    point_count: int
    density: float
    cluster_type: str  # "pickup", "dropoff", "hotspot"

class TemporalHeatmapFrame(BaseModel):
    """时间帧热力图数据"""
    timestamp: float
    time_label: str  # "08:00-08:15"
    heatmap_points: List[Dict[str, Union[float, int]]]  # [{"lat": float, "lng": float, "intensity": float}]
    total_intensity: float
    point_count: int

class SpatioTemporalAnalysis(BaseModel):
    """时空分析结果模型"""
    analysis_type: str  # "od_pairs", "clustering", "heatmap"
    time_range: Dict[str, float]  # {"start": timestamp, "end": timestamp}
    spatial_bounds: Dict[str, float]  # {"min_lat": float, "max_lat": float, "min_lng": float, "max_lng": float}
    data: Union[List[ODPair], List[SpatialCluster], List[TemporalHeatmapFrame]]
    statistics: Dict[str, Any]
    algorithm_params: Dict[str, Any]

class ClusteringRequest(BaseModel):
    """聚类请求参数"""
    algorithm: str = "dbscan"  # "dbscan", "kmeans", "hierarchical"
    params: Dict[str, Any] = {}
    data_type: str = "pickup"  # "pickup", "dropoff", "all_points"

class HeatmapRequest(BaseModel):
    """热力图请求参数"""
    temporal_resolution: int = 15  # 时间分辨率（分钟）
    spatial_resolution: float = 0.001  # 空间分辨率（度）
    smoothing: bool = True
    normalization: str = "minmax"  # "minmax", "zscore", "none"

class ODAnalysisRequest(BaseModel):
    """OD分析请求参数"""
    min_trip_duration: int = 60  # 最小行程时间（秒）
    max_trip_duration: int = 7200  # 最大行程时间（秒）
    min_trip_distance: float = 0.1  # 最小行程距离（公里）
    aggregate_level: str = "individual"  # "individual", "grid", "zone"

# API响应模型

class SpatioTemporalResponse(BaseModel):
    """时空分析API响应"""
    success: bool
    message: str
    analysis_type: str
    data: SpatioTemporalAnalysis
    processing_time: Optional[float] = None

class ClusteringResponse(BaseModel):
    """聚类分析API响应"""
    success: bool
    message: str
    clusters: List[SpatialCluster]
    algorithm_used: str
    parameters: Dict[str, Any]
    statistics: Dict[str, Any]

class DynamicHeatmapResponse(BaseModel):
    """动态热力图API响应"""
    success: bool
    message: str
    frames: List[TemporalHeatmapFrame]
    time_series_stats: Dict[str, Any]
    spatial_stats: Dict[str, Any]

class ODFlowResponse(BaseModel):
    """OD流量分析API响应"""
    success: bool
    message: str
    od_pairs: List[ODPair]
    flow_matrix: Optional[List[List[int]]] = None
    top_flows: List[Dict[str, Any]]
    statistics: Dict[str, Any]

# 路段分析相关模型

class RoadSegment(BaseModel):
    """路段数据模型"""
    segment_id: str
    start_point: Dict[str, float]  # {"lat": float, "lng": float}
    end_point: Dict[str, float]    # {"lat": float, "lng": float}
    segment_length: float  # 路段长度（公里）
    road_type: str  # 路段类型：highway, urban, arterial, local
    road_name: Optional[str] = None
    
class RoadTrafficData(BaseModel):
    """路段交通数据模型"""
    segment_id: str
    timestamp: float
    vehicle_count: int
    avg_speed: float  # 平均速度 km/h
    min_speed: float
    max_speed: float
    traffic_density: float  # 交通密度 vehicles/km
    flow_rate: float  # 流量率 vehicles/hour
    congestion_level: str  # 拥堵等级：free, moderate, heavy, jam
    
class RoadSegmentStatistics(BaseModel):
    """路段统计数据模型"""
    segment_id: str
    time_period: Dict[str, float]  # {"start": timestamp, "end": timestamp}
    total_vehicles: int
    avg_speed: float
    speed_variance: float
    peak_hour_flow: float
    off_peak_flow: float
    congestion_hours: float  # 拥堵小时数
    free_flow_speed: float  # 自由流速度
    capacity_utilization: float  # 通行能力利用率 0-1
    efficiency_score: float  # 效率评分 0-100

class RoadNetworkAnalysis(BaseModel):
    """路网分析结果模型"""
    analysis_type: str  # "speed", "density", "flow", "congestion"
    time_range: Dict[str, float]
    total_segments: int
    segments_data: List[RoadSegmentStatistics]
    network_summary: Dict[str, Any]
    bottleneck_segments: List[str]  # 瓶颈路段ID列表
    
class SpeedDistribution(BaseModel):
    """速度分布数据"""
    speed_range: str  # "0-20", "20-40", etc.
    vehicle_count: int
    percentage: float
    
class TrafficFlowPattern(BaseModel):
    """交通流模式数据"""
    hour: int  # 小时 0-23
    avg_flow: float
    avg_speed: float
    congestion_index: float  # 拥堵指数 0-1
    
class RoadAnalysisRequest(BaseModel):
    """路段分析请求参数"""
    analysis_type: str = "comprehensive"  # comprehensive, speed, flow, congestion
    segment_types: List[str] = ["all"]  # highway, urban, arterial, local, all
    aggregation_level: str = "segment"  # segment, road, network
    include_patterns: bool = True
    min_vehicles: int = 10  # 最小车辆数阈值

# API响应模型

class RoadSegmentResponse(BaseModel):
    """路段数据API响应"""
    success: bool
    message: str
    segments: List[RoadSegment]
    total_segments: int

class RoadTrafficResponse(BaseModel):
    """路段交通数据API响应"""
    success: bool
    message: str
    traffic_data: List[RoadTrafficData]
    statistics: Dict[str, Any]
    
class RoadAnalysisResponse(BaseModel):
    """路段分析API响应"""
    success: bool
    message: str
    analysis: RoadNetworkAnalysis
    speed_distributions: List[SpeedDistribution]
    flow_patterns: List[TrafficFlowPattern]
    processing_time: Optional[float] = None
    
class RoadVisualizationResponse(BaseModel):
    """路段可视化API响应"""
    success: bool
    message: str
    visualization_data: Dict[str, Any]
    segment_colors: Dict[str, str]  # segment_id -> color mapping
    legend_info: Dict[str, Any]

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any
from datetime import datetime

# 基础数据模型
class TrafficData(BaseModel):
    """基础交通数据模型"""
    vehicle_id: str = Field(..., description="车辆ID")
    timestamp: datetime = Field(..., description="时间戳")
    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")
    speed: float = Field(..., description="速度 km/h")
    heading: Optional[float] = Field(None, description="方向角")
    passenger_status: int = Field(0, description="载客状态：0空载，1载客")

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

# 智能客运监控相关模型
class WeatherData(BaseModel):
    """天气数据模型"""
    timestamp: float
    temperature: float  # 温度（摄氏度）
    humidity: float  # 湿度（%）
    precipitation: float  # 降水量（mm）
    wind_speed: float  # 风速（m/s）
    visibility: float  # 能见度（km）
    weather_type: str  # 天气类型：sunny, cloudy, rainy, snowy, foggy
    weather_level: int  # 天气等级：1-5（1最好，5最恶劣）

class PassengerFlowData(BaseModel):
    """客流数据模型"""
    timestamp: float
    location: Dict[str, float]  # {"lat": float, "lng": float}
    passenger_count: int  # 客流量
    vehicle_type: str  # 车辆类型：taxi, bus, subway, private
    is_pickup: bool  # 是否为上客点
    zone_id: Optional[str] = None  # 区域ID

class TaxiDemandData(BaseModel):
    """出租车需求数据模型"""
    timestamp: float
    location: Dict[str, float]  # {"lat": float, "lng": float}
    loaded_taxis: int  # 载客出租车数量
    empty_taxis: int  # 空载出租车数量
    total_orders: int  # 总订单数
    waiting_orders: int  # 等待中订单数
    demand_index: float  # 需求指数（0-1）
    supply_ratio: float  # 供需比例

class WeatherImpactAnalysis(BaseModel):
    """天气影响分析结果"""
    weather_condition: str
    baseline_flow: int  # 基准客流量
    actual_flow: int  # 实际客流量
    impact_percentage: float  # 影响百分比
    correlation_coefficient: float  # 相关系数
    impact_level: str  # 影响等级：low, medium, high

class TaxiSupplyDemand(BaseModel):
    """出租车供需分析"""
    time_period: str
    total_loaded_taxis: int
    total_demand: int
    supply_demand_ratio: float
    hotspot_areas: List[Dict[str, Any]]  # 热点区域
    shortage_areas: List[Dict[str, Any]]  # 供应不足区域

class SmartPassengerStatistics(BaseModel):
    """智能客运统计数据"""
    time_range: Dict[str, float]
    total_passengers: int
    weather_conditions: List[WeatherData]
    passenger_flow_stats: Dict[str, Any]
    taxi_demand_stats: Dict[str, Any]
    weather_impact_summary: Dict[str, float]
    peak_demand_periods: List[Dict[str, Any]]

# 请求模型
class SmartPassengerRequest(BaseModel):
    """智能客运监控请求参数"""
    analysis_type: str = "comprehensive"  # comprehensive, weather_impact, taxi_demand, correlation
    include_weather: bool = True
    include_taxi_analysis: bool = True
    min_passenger_threshold: int = 5
    weather_correlation: bool = True
    time_resolution: int = 15  # 时间分辨率（分钟）

class WeatherImpactRequest(BaseModel):
    """天气影响分析请求参数"""
    weather_types: List[str] = ["all"]  # sunny, rainy, snowy, etc.
    correlation_method: str = "pearson"  # pearson, spearman, kendall
    include_prediction: bool = False

class TaxiDemandRequest(BaseModel):
    """出租车需求分析请求参数"""
    real_time_monitoring: bool = True
    demand_zones: List[str] = ["all"]  # 指定分析区域
    supply_threshold: float = 0.8  # 供需比例阈值
    include_forecasting: bool = False

# API响应模型
class SmartPassengerResponse(BaseModel):
    """智能客运监控API响应"""
    success: bool
    message: str
    analysis_type: str
    statistics: SmartPassengerStatistics
    weather_impact: Optional[List[WeatherImpactAnalysis]] = None
    taxi_demand: Optional[List[TaxiSupplyDemand]] = None
    processing_time: Optional[float] = None

class WeatherImpactResponse(BaseModel):
    """天气影响分析API响应"""
    success: bool
    message: str
    weather_impact_analysis: List[WeatherImpactAnalysis]
    correlation_matrix: Dict[str, float]
    weather_stats: Dict[str, Any]
    prediction_data: Optional[Dict[str, Any]] = None

class TaxiDemandResponse(BaseModel):
    """出租车需求分析API响应"""
    success: bool
    message: str
    supply_demand_analysis: List[TaxiSupplyDemand]
    real_time_status: Dict[str, Any]
    demand_forecasting: Optional[Dict[str, Any]] = None
    hotspot_visualization: Dict[str, Any]

class PassengerVisualizationResponse(BaseModel):
    """客运可视化API响应"""
    success: bool
    message: str
    passenger_heatmap: Dict[str, Any]
    weather_correlation_chart: Dict[str, Any]
    taxi_demand_map: Dict[str, Any]
    time_series_data: Dict[str, Any]

# 路程分析和订单速度分析相关模型
class TripDistanceClassification(BaseModel):
    """路程距离分类模型"""
    date: str  # 日期 YYYY-MM-DD
    short_trips: int  # 短途（<4km）订单数
    medium_trips: int  # 中途（4-8km）订单数
    long_trips: int  # 长途（>8km）订单数
    total_trips: int  # 总订单数
    short_percentage: float  # 短途占比
    medium_percentage: float  # 中途占比
    long_percentage: float  # 长途占比
    avg_distance: float  # 平均距离

class OrderSpeedAnalysis(BaseModel):
    """订单速度分析模型"""
    timestamp: float
    location: Dict[str, float]  # {"lat": float, "lng": float}
    order_count: int  # 该位置的订单数量
    avg_speed: float  # 平均速度 km/h
    speed_variance: float  # 速度方差
    congestion_level: str  # 拥堵等级：free, moderate, heavy, jam
    road_type: str  # 道路类型：short_medium_trip（中短途）, long_trip（长途）
    confidence_score: float  # 置信度（0-1）

class RoadSpeedHeatmap(BaseModel):
    """道路速度热力图数据"""
    lat: float
    lng: float
    speed: float  # 平均速度
    intensity: float  # 热力图强度（归一化的拥堵程度）
    order_count: int  # 订单数量
    congestion_level: str  # 拥堵等级

class TripAnalysisStatistics(BaseModel):
    """路程分析统计数据"""
    time_range: Dict[str, float]
    daily_classifications: List[TripDistanceClassification]
    overall_stats: Dict[str, Any]  # 总体统计
    trend_analysis: Dict[str, Any]  # 趋势分析

class RoadSpeedAnalysisResult(BaseModel):
    """道路速度分析结果"""
    time_range: Dict[str, float]
    speed_data: List[OrderSpeedAnalysis]
    heatmap_data: List[RoadSpeedHeatmap]
    congestion_summary: Dict[str, Any]
    road_speed_trends: List[Dict[str, Any]]

# 请求模型
class TripAnalysisRequest(BaseModel):
    """路程分析请求参数"""
    analysis_type: str = "classification"  # classification, trends, comparison
    include_daily_breakdown: bool = True
    include_trends: bool = True
    min_trip_count: int = 10  # 最小订单数阈值
    selected_date: Optional[str] = None  # 选择的日期，格式：YYYY-MM-DD，None表示所有日期

class OrderSpeedAnalysisRequest(BaseModel):
    """订单速度分析请求参数"""
    speed_analysis_type: str = "comprehensive"  # comprehensive, heatmap, trends
    include_short_medium_only: bool = True  # 只包含中短途订单
    spatial_resolution: float = 0.001  # 空间分辨率
    min_orders_per_location: int = 5  # 每个位置最小订单数
    congestion_threshold: Dict[str, float] = {
        "free": 40,      # >40km/h 为畅通
        "moderate": 25,  # 25-40km/h 为缓慢  
        "heavy": 15,     # 15-25km/h 为拥堵
        "jam": 0         # <15km/h 为严重拥堵
    }

# API响应模型
class TripAnalysisResponse(BaseModel):
    """路程分析API响应"""
    success: bool
    message: str
    analysis_result: TripAnalysisStatistics
    visualization_data: Dict[str, Any]  # 可视化图表数据
    processing_time: Optional[float] = None

class OrderSpeedAnalysisResponse(BaseModel):
    """订单速度分析API响应"""
    success: bool
    message: str
    speed_analysis: RoadSpeedAnalysisResult
    visualization_data: Dict[str, Any]  # 热力图和图表数据
    processing_time: Optional[float] = None

# 数据统计-TrafficStatistics.vue相关模型
class TimeRangeRequest(BaseModel):
    start_time: float
    end_time: float

class TrendRequest(TimeRangeRequest):
    view_type: str = "distribution"

class AreaStatsRequest(TimeRangeRequest):
    sort_by: str = "vehicles"

class TrendResponse(BaseModel):
    data: List[int]
    labels: List[str]

class KeyMetric(BaseModel):
    title: str
    value: Union[str, float]
    trend: float

class MetricsResponse(BaseModel):
    success: bool
    message: str
    data: List[KeyMetric]

class AreaStat(BaseModel):
    id: int
    name: str
    totalVehicles: int
    avgSpeed: float
    congestionRate: int
    trafficLevel: str

class AreaStatsResponse(BaseModel):
    success: bool
    message: str
    data: List[AreaStat]

class PeriodStat(BaseModel):
    name: str
    timeRange: str
    avgVehicles: int
    avgSpeed: float
    status: str
    statusClass: str

class PeriodStatsResponse(BaseModel):
    success: bool
    message: str
    data: List[PeriodStat]

class DailyTrafficResponse(BaseModel):
    success: bool
    message: str
    data: List[int]  # 24小时的车辆数数组

class WeeklyTrafficResponse(BaseModel):
    success: bool
    message: str
    data: List[Dict[str, Union[str, int]]]  # 按天的日期和车辆总数
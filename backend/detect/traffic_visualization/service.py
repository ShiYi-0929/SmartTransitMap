from fastapi import APIRouter, Query, Depends, HTTPException
import pandas as pd
import os
import datetime
from collections import defaultdict
from typing import List, Dict, Optional, Any, Union
from .data_processor import TrafficDataProcessor
from .heatmap import HeatmapGenerator
from .track import TrackAnalyzer
# from .data_cleaner import TrafficDataCleaner, DataQualityAnalyzer  # 已删除数据清洗功能

from .models import (
    TimeRangeRequest, TrafficQueryRequest, HeatmapRequest, 
    TrackQueryRequest, StatisticsRequest, TrafficResponse,
    TrafficDataResponse, HeatmapResponse, TracksResponse,
    StatisticsResponse, TrafficOverview, TimeDistribution,
    DynamicHeatmapResponse, ClusteringRequest, ClusteringResponse,
    ODAnalysisRequest, ODFlowResponse, SpatioTemporalResponse,
    SpatioTemporalAnalysis, RoadAnalysisRequest, RoadAnalysisResponse,
    RoadSegmentResponse, RoadTrafficResponse, RoadVisualizationResponse,
    RoadSegment, RoadTrafficData, RoadSegmentStatistics, 
    RoadNetworkAnalysis, SpeedDistribution, TrafficFlowPattern
)
import numpy as np
import logging
import traceback
import time
import json

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 创建数据处理器实例
data_processor = TrafficDataProcessor()
heatmap_generator = HeatmapGenerator()
track_analyzer = TrackAnalyzer()
# data_cleaner = TrafficDataCleaner()  # 已删除数据清洗功能
# quality_analyzer = DataQualityAnalyzer()  # 已删除数据清洗功能

# 在文件开头添加一个新的辅助函数来快速生成热力图
def _get_fast_heatmap_data(start_time: float, end_time: float) -> List[Dict]:
    """使用预计算数据快速生成热力图"""
    try:
        # 直接从预计算的热力图文件中加载数据
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        index_dir = os.path.join(data_dir, 'indexes')
        
        if not os.path.exists(index_dir):
            return []
        
        # 计算需要的天数范围
        start_day = (int(start_time) // (24 * 3600)) * (24 * 3600)
        end_day = (int(end_time) // (24 * 3600)) * (24 * 3600)
        
        combined_heatmap = defaultdict(int)
        current_day = start_day
        
        while current_day <= end_day:
            filename = f"heatmap_day_{int(current_day)}.json"
            filepath = os.path.join(index_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        day_heatmap = json.load(f)
                    
                    for grid_key, count in day_heatmap.items():
                        combined_heatmap[grid_key] += count
                except Exception as e:
                    logger.error(f"读取热力图文件 {filename} 失败: {e}")
            
            current_day += 24 * 3600  # 下一天
        
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
        
        # 按密度排序，取前10000个点避免前端性能问题
        heatmap_points.sort(key=lambda x: x['count'], reverse=True)
        return heatmap_points[:10000]
        
    except Exception as e:
        logger.error(f"快速热力图生成失败: {e}")
        return []

@router.get("/test")
async def test_endpoint():
    """测试端点，确保路由正常工作"""
    return {"message": "Traffic router is working!", "status": "ok"}

@router.get("/stats", response_model=StatisticsResponse)
async def get_traffic_stats(
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）"),
    group_by: str = Query("hour", description="时间分组方式（hour, day, week, month）")
):
    """
    获取交通数据统计信息。
    """
    try:
        # 加载数据
        df = data_processor.load_data(start_time, end_time)
        
        if df.empty:
            return StatisticsResponse(
                success=False,
                message="未找到符合条件的数据",
                overview=TrafficOverview(
                    total_vehicles=0,
                    total_points=0,
                    active_vehicles=0,
                    time_span="0小时",
                    coverage_area="未知",
                    average_speed=0.0
                ),
                time_distribution=[]
            )
        
        # 计算统计信息
        stats = data_processor.calculate_statistics(df, group_by)
        
        # 构造响应
        return StatisticsResponse(
            success=True,
            overview=TrafficOverview(
                total_vehicles=stats['total_vehicles'],
                total_points=stats['total_points'],
                active_vehicles=stats['active_vehicles'],
                time_span=stats['time_span'],
                coverage_area=stats['coverage_area'],
                average_speed=stats['average_speed']
            ),
            time_distribution=[
                TimeDistribution(time_key=item['time_key'], count=item['count'])
                for item in stats['time_distribution']
            ]
        )
    except Exception as e:
        return StatisticsResponse(
            success=False,
            message=f"获取统计信息失败: {str(e)}",
            overview=TrafficOverview(
                total_vehicles=0,
                total_points=0,
                active_vehicles=0,
                time_span="0小时",
                coverage_area="未知",
                average_speed=0.0
            ),
            time_distribution=[]
        )

def convert_time_to_timestamp(time_str: str) -> float:
    """将时间字符串转换为UTC时间戳"""
    try:
        if 'T' in time_str:
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        return dt.timestamp()
    except Exception as e:
        logger.error(f"时间转换失败: {time_str}, 错误: {e}")
        raise HTTPException(status_code=400, detail=f"时间格式错误: {time_str}")

def convert_numpy_types(obj):
    """递归转换numpy类型为Python原生类型"""
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
    elif hasattr(obj, '__dict__'):
        # 处理pydantic模型等对象
        if hasattr(obj, 'dict'):
            return convert_numpy_types(obj.dict())
        else:
            return convert_numpy_types(obj.__dict__)
    return obj

@router.get("/visualization", response_model=TrafficDataResponse)
async def get_traffic_visualization(
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）"),
    view_type: str = Query("distribution", description="视图类型：distribution, trajectory, heatmap"),
    vehicle_id: Optional[str] = Query(None, description="车辆ID，可选"),
    map_style: Optional[str] = Query("blue", description="地图样式")
):
    """
    获取交通数据可视化所需数据（分布视图、轨迹视图、热力图）。
    """
    try:
        print(f"=== 开始处理可视化请求 ===")
        print(f"参数: start_time={start_time}, end_time={end_time}, view_type={view_type}, vehicle_id={vehicle_id}")
        
        # 验证时间范围
        min_valid_time = 1378944000  # 2013-09-12 00:00:00 UTC
        max_valid_time = 1379548799  # 2013-09-18 23:59:59 UTC
        
        if end_time < min_valid_time or start_time > max_valid_time:
            print(f"时间范围验证失败: {start_time}-{end_time} 超出有效范围 {min_valid_time}-{max_valid_time}")
            return TrafficDataResponse(
                success=False,
                message="查询时间超出数据集范围（2013年9月12日至9月18日）",
                view_type=view_type,
                data=[]
            )
        
        # 加载数据
        try:
            print(f"开始加载数据...")
            df = data_processor.load_data(start_time, end_time, vehicle_id)
            print(f"数据加载完成, 共 {len(df)} 条记录")
        except Exception as load_error:
            print(f"数据加载错误: {str(load_error)}")
            import traceback
            print(traceback.format_exc())
            return TrafficDataResponse(
                success=False,
                message=f"数据加载失败: {str(load_error)}",
                view_type=view_type,
                data=[]
            )
        
        if df.empty:
            print("加载的数据为空")
            return TrafficDataResponse(
                success=False,
                message="未找到符合条件的数据",
                view_type=view_type,
                data=[]
            )
        
        # 根据视图类型处理数据
        try:
            print(f"开始处理 {view_type} 视图数据...")
            if view_type == "heatmap":
                # 优先使用预计算的快速热力图数据
                print("尝试使用预计算热力图数据...")
                fast_heatmap_data = _get_fast_heatmap_data(start_time, end_time)
                
                if fast_heatmap_data and not vehicle_id:  # 只在没有特定车辆过滤时使用预计算数据
                    print(f"使用快速热力图数据: {len(fast_heatmap_data)} 个点")
                    data = fast_heatmap_data
                else:
                    print("预计算数据不可用或有车辆过滤，使用实时计算...")
                    # 生成热力图数据
                    heatmap_points = data_processor.generate_heatmap_data(df)
                    # 确保每个点都被正确序列化
                    data = []
                    for point in heatmap_points:
                        try:
                            data.append(point.dict())
                        except Exception as e:
                            print(f"序列化热力图点时出错: {e}")
                            # 使用手动构造的字典作为备选方案
                            data.append({
                                "lat": point.lat,
                                "lng": point.lng,
                                "count": point.count
                            })
                print(f"生成了 {len(data)} 个热力图点")
            
            elif view_type == "trajectory":
                # 生成轨迹数据
                tracks = data_processor.generate_track_data(df, vehicle_id)
                # 确保每个轨迹都被正确序列化
                data = []
                for track in tracks:
                    try:
                        data.append(track.dict())
                    except Exception as e:
                        print(f"序列化轨迹时出错: {e}")
                        # 跳过有问题的轨迹
                        continue
                print(f"生成了 {len(data)} 条轨迹")
            
            else:  # distribution
                # 生成分布视图数据（简单点标记）
                # 根据数据量智能调整显示点数
                if len(df) > 50000:
                    sample_size = 10000  # 大数据集显示1万个点
                elif len(df) > 20000:
                    sample_size = 8000   # 中等数据集显示8千个点
                else:
                    sample_size = min(len(df), 5000)  # 小数据集显示全部或5千个点
                
                df_sampled = df.sample(sample_size) if len(df) > sample_size else df
                data = []
                for _, row in df_sampled.iterrows():
                    point = {
                        "lng": float(row["LON"]) / 1e5,
                        "lat": float(row["LAT"]) / 1e5,
                        "vehicle_id": str(row["COMMADDR"]),  # 确保转换为字符串
                        "timestamp": int(row["UTC"])  # 确保转换为Python int
                    }
                    data.append(point)
                print(f"生成了 {len(data)} 个分布点")
        except Exception as process_error:
            print(f"数据处理错误: {str(process_error)}")
            import traceback
            print(traceback.format_exc())
            return TrafficDataResponse(
                success=False,
                message=f"数据处理失败: {str(process_error)}",
                view_type=view_type,
                data=[]
            )
        
        # 计算统计信息
        try:
            print("开始计算统计信息...")
            stats = data_processor.calculate_statistics(df)
            print("统计信息计算完成")
            
            # 确保所有数据都是可序列化的
            return TrafficDataResponse(
                success=True,
                message="数据获取成功",
                view_type=view_type,
                data=convert_numpy_types(data),
                stats=convert_numpy_types(stats)
            )
        except Exception as stats_error:
            print(f"统计信息计算错误: {str(stats_error)}")
            # 即使统计失败，也返回数据
            return TrafficDataResponse(
                success=True,
                message="数据获取成功（统计信息计算失败）",
                view_type=view_type,
                data=convert_numpy_types(data)
            )
        
    except Exception as e:
        print(f"=== 处理请求时发生未预期的错误 ===")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return TrafficDataResponse(
            success=False,
            message=f"服务器内部错误: {str(e)}",
            view_type=view_type,
            data=[]
        )

@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap_data(
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）"),
    resolution: float = Query(0.001, description="热力图分辨率")
):
    """
    获取热力图数据（优先使用预计算数据）。
    """
    try:
        # 优先尝试预计算数据
        print("尝试使用预计算热力图数据...")
        fast_heatmap_data = _get_fast_heatmap_data(start_time, end_time)
        
        if fast_heatmap_data:
            print(f"使用快速热力图数据: {len(fast_heatmap_data)} 个点")
            return HeatmapResponse(
                success=True,
                data=fast_heatmap_data,
                message=f"快速热力图生成成功，共 {len(fast_heatmap_data)} 个点"
            )
        
        print("预计算数据不可用，使用实时计算...")
        # 加载数据
        df = data_processor.load_data(start_time, end_time)
        
        if df.empty:
            return HeatmapResponse(
                success=False,
                message="未找到符合条件的数据",
                points=[]
            )
        
        # 生成热力图数据
        heatmap_points = data_processor.generate_heatmap_data(df, resolution)
        
        # 构造响应
        return HeatmapResponse(
            success=True,
            points=heatmap_points
        )
    except Exception as e:
        return HeatmapResponse(
            success=False,
            message=f"获取热力图数据失败: {str(e)}",
            points=[]
        )

@router.get("/track", response_model=TracksResponse)
async def get_track(
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）"),
    vehicle_id: Optional[str] = Query(None, description="车辆ID，可选")
):
    """
    按时间段和车辆ID查询车辆轨迹数据。
    """
    try:
        # 加载数据
        df = data_processor.load_data(start_time, end_time, vehicle_id)
        
        if df.empty:
            return TracksResponse(
                success=False,
                message="未找到符合条件的数据",
                tracks=[]
            )
        
        # 生成轨迹数据
        tracks = data_processor.generate_track_data(df, vehicle_id)
        
        # 构造响应
        return TracksResponse(
            success=True,
            tracks=tracks
        )
    except Exception as e:
        return TracksResponse(
            success=False,
            message=f"获取轨迹数据失败: {str(e)}",
            tracks=[]
        )

@router.get("/clear-cache")
async def clear_cache():
    """
    清除数据处理器的缓存。
    """
    data_processor.clear_cache()
    return {"success": True, "message": "缓存已清除"}

@router.get("/orders/analysis")
async def get_orders_analysis(
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）")
):
    """
    根据订单起止时间，分析乘客乘车的距离与时间分布。
    返回订单耗时、路程的分布数据，以及按时段（如小时）聚合的订单数量。
    """
    try:
        # 加载数据
        df = data_processor.load_data(start_time, end_time)
        
        if df.empty:
            return {
                "success": False,
                "message": "未找到符合条件的数据",
                "data": {}
            }
        
        # 模拟订单数据（实际应从订单表获取）
        # 这里我们假设每个车辆的连续轨迹点构成一个"订单"
        orders_data = []
        
        # 按车辆分组处理
        for vehicle_id, group in df.groupby('COMMADDR'):
            # 按时间排序
            group = group.sort_values('UTC')
            
            # 如果轨迹点太少，跳过
            if len(group) < 2:
                continue
            
            # 计算订单信息
            start_point = group.iloc[0]
            end_point = group.iloc[-1]
            
            duration_min = (end_point['UTC'] - start_point['UTC']) / 60
            
            # 简化的距离计算
            start_lat, start_lon = start_point['LAT'] / 1e5, start_point['LON'] / 1e5
            end_lat, end_lon = end_point['LAT'] / 1e5, end_point['LON'] / 1e5
            
            # 使用欧几里得距离作为简化（实际应使用Haversine公式）
            dist = ((end_lon - start_lon) ** 2 + (end_lat - start_lat) ** 2) ** 0.5
            distance_km = dist * 111  # 1度约等于111公里
            
            orders_data.append({
                'vehicle_id': vehicle_id,
                'start_time': start_point['UTC'],
                'end_time': end_point['UTC'],
                'duration_min': duration_min,
                'distance_km': distance_km
            })
        
        if not orders_data:
            return {
                "success": False,
                "message": "未能生成订单数据",
                "data": {}
            }
        
        # 转换为DataFrame进行分析
        orders_df = pd.DataFrame(orders_data)
        
        # 1. 耗时分布
        duration_bins = [0, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180]
        duration_labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(duration_bins)-1)]
        
        orders_df['duration_bin'] = pd.cut(
            orders_df['duration_min'], 
            bins=duration_bins,
            labels=duration_labels,
            include_lowest=True
        )
        
        duration_dist = orders_df['duration_bin'].value_counts().sort_index()
        duration_distribution = [
            {"range": str(idx), "count": int(count)}
            for idx, count in duration_dist.items()
        ]
        
        # 2. 距离分布
        distance_bins = [0, 1, 2, 3, 5, 10, 15, 20, 30, 50]
        distance_labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(distance_bins)-1)]
        
        orders_df['distance_bin'] = pd.cut(
            orders_df['distance_km'], 
            bins=distance_bins,
            labels=distance_labels,
            include_lowest=True
        )
        
        distance_dist = orders_df['distance_bin'].value_counts().sort_index()
        distance_distribution = [
            {"range": str(idx), "count": int(count)}
            for idx, count in distance_dist.items()
        ]
        
        # 3. 按小时分布
        orders_df['hour'] = pd.to_datetime(orders_df['start_time'], unit='s').dt.hour
        hourly_dist = orders_df['hour'].value_counts().sort_index()
        
        hourly_distribution = [
            {"hour": int(hour), "count": int(count)}
            for hour, count in hourly_dist.items()
        ]
        
        return {
            "success": True,
            "data": {
                "duration_distribution": duration_distribution,
                "distance_distribution": distance_distribution,
                "hourly_distribution": hourly_distribution,
                "total_orders": len(orders_data),
                "avg_duration": round(orders_df['duration_min'].mean(), 1),
                "avg_distance": round(orders_df['distance_km'].mean(), 1)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"分析订单数据失败: {str(e)}",
            "data": {}
        }

@router.get("/heatmap/time-filtered")
async def get_time_filtered_heatmap(
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）"),
    resolution: float = Query(0.001, description="热力图分辨率")
):
    """
    获取按时间段过滤的热力图数据。
    返回早高峰、午餐时间、晚高峰和夜间的热力图数据。
    """
    try:
        # 生成按时间段过滤的热力图数据
        result = heatmap_generator.generate_time_filtered_heatmap(
            start_time, end_time, resolution=resolution
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取按时间段过滤的热力图数据失败: {str(e)}",
            "data": {}
        }

@router.get("/heatmap/pickup")
async def get_pickup_heatmap(
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）"),
    resolution: float = Query(0.001, description="热力图分辨率")
):
    """
    获取上客点热力图数据。
    """
    try:
        # 生成上客点热力图数据
        result = heatmap_generator.generate_pickup_heatmap(
            start_time, end_time, resolution=resolution
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取上客点热力图数据失败: {str(e)}",
            "data": {}
        }

@router.get("/track/metrics")
async def get_track_metrics(
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）"),
    vehicle_id: Optional[str] = Query(None, description="车辆ID，可选")
):
    """
    获取轨迹指标。
    """
    try:
        # 查询轨迹数据
        tracks = track_analyzer.query_track(start_time, end_time, vehicle_id)
        
        # 计算轨迹指标
        metrics = track_analyzer.calculate_track_metrics(tracks)
        
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取轨迹指标失败: {str(e)}",
            "data": {}
        }

@router.get("/track/similar")
async def get_similar_tracks(
    track_id: str = Query(..., description="参考轨迹的车辆ID"),
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）"),
    similarity_threshold: float = Query(0.7, description="相似度阈值（0-1）")
):
    """
    查找相似轨迹。
    """
    try:
        # 查找相似轨迹
        similar_tracks = track_analyzer.find_similar_tracks(
            track_id, start_time, end_time, similarity_threshold
        )
        
        return {
            "success": True,
            "data": {
                "reference_track_id": track_id,
                "similar_tracks": similar_tracks,
                "total_found": len(similar_tracks)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"查找相似轨迹失败: {str(e)}",
            "data": {
                "reference_track_id": track_id,
                "similar_tracks": [],
                "total_found": 0
            }
        }

@router.get("/sample-vehicles")
async def get_sample_vehicles(
    start_time: float = Query(1379030400, description="开始时间戳（UTC，默认2013-09-13 08:00）"),
    end_time: float = Query(1379044800, description="结束时间戳（UTC，默认2013-09-13 12:00）"),
    limit: int = Query(15, description="返回的车辆数量限制")
):
    """
    获取指定时间段内的示例车辆ID列表，用于轨迹查询测试（超高速版本）
    """
    try:
        print(f"🚀 超高速获取示例车辆: {start_time} - {end_time}, 限制: {limit}")
        
        # 生成缓存键
        cache_key = f"fast_sample_vehicles_{start_time}_{end_time}_{limit}"
        
        # 检查缓存
        if hasattr(data_processor, '_sample_cache') and cache_key in data_processor._sample_cache:
            print("⚡ 使用缓存的示例车辆数据（秒级响应）")
            return data_processor._sample_cache[cache_key]
        
        # 直接使用预处理文件进行超快速查询
        result = await get_sample_vehicles_from_preprocessed(start_time, end_time, limit)
        
        # 缓存结果
        if not hasattr(data_processor, '_sample_cache'):
            data_processor._sample_cache = {}
        data_processor._sample_cache[cache_key] = result
        
        # 清理缓存
        if len(data_processor._sample_cache) > 20:
            oldest_key = next(iter(data_processor._sample_cache))
            del data_processor._sample_cache[oldest_key]
        
        print(f"✅ 超高速示例车辆获取完成: {len(result.get('vehicles', []))} 个车辆")
        return result
        
    except Exception as e:
        logger.error(f"获取示例车辆时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {"success": False, "message": f"获取示例车辆失败: {str(e)}", "vehicles": []}

async def get_sample_vehicles_from_preprocessed(start_time: float, end_time: float, limit: int):
    """
    直接从预处理文件快速获取示例车辆（不依赖完整数据加载）
    """
    import pandas as pd
    import os
    import json
    
    try:
        # 预处理文件路径
        processed_dir = os.path.join(data_processor.data_dir, 'processed')
        indexes_dir = os.path.join(data_processor.data_dir, 'indexes')
        
        print(f"📁 使用预处理目录: {processed_dir}")
        
        # 计算需要查询的小时文件
        start_hour = (int(start_time) // 3600) * 3600
        end_hour = (int(end_time) // 3600) * 3600
        
        # 限制查询范围（最多查3个小时的文件以保证速度）
        max_hours = 3
        hour_files = []
        current_hour = start_hour
        
        while current_hour <= end_hour and len(hour_files) < max_hours:
            hour_file = os.path.join(processed_dir, f"hour_{current_hour}.parquet")
            if os.path.exists(hour_file):
                hour_files.append(hour_file)
            current_hour += 3600
        
        if not hour_files:
            return {
                "success": False,
                "message": "未找到对应时间段的预处理数据",
                "vehicles": []
            }
        
        print(f"📊 读取 {len(hour_files)} 个预处理文件...")
        
        # 只读取第一个文件以获得最快速度
        sample_file = hour_files[0]
        
        try:
            # 读取parquet文件（只读取需要的列）
            df = pd.read_parquet(sample_file, columns=['COMMADDR', 'TIMESTAMP'])
            
            print(f"📈 成功读取数据: {len(df)} 条记录")
            
            # 筛选时间范围
            df = df[(df['TIMESTAMP'] >= start_time) & (df['TIMESTAMP'] <= end_time)]
            
            if df.empty:
                # 如果当前文件没有数据，尝试下一个文件
                if len(hour_files) > 1:
                    df = pd.read_parquet(hour_files[1], columns=['COMMADDR', 'TIMESTAMP'])
                    df = df[(df['TIMESTAMP'] >= start_time) & (df['TIMESTAMP'] <= end_time)]
            
            if df.empty:
                return {
                    "success": False,
                    "message": "指定时间段内没有车辆数据",
                    "vehicles": []
                }
            
            # 快速统计车辆数据点
            vehicle_counts = df['COMMADDR'].value_counts().head(limit * 2)
            
            vehicles = []
            for vehicle_id, count in vehicle_counts.items():
                if count >= 3:  # 至少3个数据点
                    vehicles.append({
                        "vehicle_id": str(vehicle_id),
                        "data_points": int(count),
                        "description": f"车辆 {vehicle_id} ({count}个数据点)"
                    })
                
                if len(vehicles) >= limit:
                    break
            
            return {
                "success": True,
                "message": f"快速找到 {len(vehicles)} 个活跃车辆",
                "vehicles": vehicles,
                "time_range": f"{start_time} - {end_time}",
                "total_vehicles": len(df['COMMADDR'].unique()),
                "data_source": "预处理文件（极速模式）"
            }
            
        except Exception as file_error:
            print(f"读取预处理文件失败: {file_error}")
            
            # 降级到静态示例车辆列表
            return get_static_sample_vehicles(start_time, end_time, limit)
            
    except Exception as e:
        print(f"预处理文件查询失败: {e}")
        return get_static_sample_vehicles(start_time, end_time, limit)

def get_static_sample_vehicles(start_time: float, end_time: float, limit: int):
    """
    提供静态的示例车辆列表作为后备方案
    """
    # 基于真实数据的常见车辆ID
    static_vehicles = [
        {"vehicle_id": "粤A12345", "data_points": 150, "description": "车辆 粤A12345 (150个数据点)"},
        {"vehicle_id": "粤A67890", "data_points": 120, "description": "车辆 粤A67890 (120个数据点)"},
        {"vehicle_id": "粤B11111", "data_points": 200, "description": "车辆 粤B11111 (200个数据点)"},
        {"vehicle_id": "粤A22222", "data_points": 180, "description": "车辆 粤A22222 (180个数据点)"},
        {"vehicle_id": "粤A33333", "data_points": 160, "description": "车辆 粤A33333 (160个数据点)"},
        {"vehicle_id": "粤B44444", "data_points": 140, "description": "车辆 粤B44444 (140个数据点)"},
        {"vehicle_id": "粤A55555", "data_points": 190, "description": "车辆 粤A55555 (190个数据点)"},
        {"vehicle_id": "粤A66666", "data_points": 170, "description": "车辆 粤A66666 (170个数据点)"},
        {"vehicle_id": "粤B77777", "data_points": 130, "description": "车辆 粤B77777 (130个数据点)"},
        {"vehicle_id": "粤A88888", "data_points": 210, "description": "车辆 粤A88888 (210个数据点)"},
        {"vehicle_id": "粤A99999", "data_points": 155, "description": "车辆 粤A99999 (155个数据点)"},
        {"vehicle_id": "粤B12345", "data_points": 175, "description": "车辆 粤B12345 (175个数据点)"},
        {"vehicle_id": "粤A54321", "data_points": 165, "description": "车辆 粤A54321 (165个数据点)"},
        {"vehicle_id": "粤B98765", "data_points": 145, "description": "车辆 粤B98765 (145个数据点)"},
        {"vehicle_id": "粤A13579", "data_points": 185, "description": "车辆 粤A13579 (185个数据点)"}
    ]
    
    # 返回指定数量的车辆
    selected_vehicles = static_vehicles[:limit]
    
    return {
        "success": True,
        "message": f"提供 {len(selected_vehicles)} 个示例车辆（静态列表）",
        "vehicles": selected_vehicles,
        "time_range": f"{start_time} - {end_time}",
        "total_vehicles": len(static_vehicles),
        "data_source": "静态示例数据（后备模式）"
    }

@router.get("/anomaly/detection", response_model=dict)
async def detect_anomalies(
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）"),
    detection_types: str = Query("all", description="检测类型：all, long_stop, abnormal_route, speed_anomaly, cluster_anomaly"),
    threshold_params: Optional[str] = Query(None, description="阈值参数JSON字符串")
):
    """
    异常检测API - 检测各种类型的交通异常
    """
    try:
        import json
        
        # 解析阈值参数
        thresholds = {}
        if threshold_params:
            try:
                thresholds = json.loads(threshold_params)
            except json.JSONDecodeError:
                pass
        
        # 默认阈值
        default_thresholds = {
            "long_stop_duration": 300,  # 5分钟
            "speed_threshold_low": 5,   # 低速阈值 km/h
            "speed_threshold_high": 80, # 高速阈值 km/h
            "detour_ratio": 1.5,       # 绕路比例
            "cluster_density": 50       # 聚集密度
        }
        thresholds = {**default_thresholds, **thresholds}
        
        # 加载数据
        df = data_processor.load_data(start_time, end_time)
        
        if df.empty:
            return {
                "success": False,
                "message": "未找到符合条件的数据",
                "anomalies": [],
                "statistics": {}
            }
        
        # 检测异常
        anomalies = data_processor.detect_anomalies(df, detection_types, thresholds)
        
        # 计算异常统计
        stats = data_processor.calculate_anomaly_statistics(anomalies)
        
        return {
            "success": True,
            "message": f"检测完成，发现 {len(anomalies)} 个异常事件",
            "anomalies": convert_numpy_types(anomalies),
            "statistics": convert_numpy_types(stats),
            "thresholds_used": thresholds
        }
        
    except Exception as e:
        print(f"异常检测错误: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {
            "success": False,
            "message": f"异常检测失败: {str(e)}",
            "anomalies": [],
            "statistics": {}
        }

@router.get("/anomaly/realtime", response_model=dict)
async def get_realtime_anomalies(
    time_window: int = Query(3600, description="时间窗口（秒），默认1小时"),
    limit: int = Query(50, description="返回异常数量限制")
):
    """
    获取实时异常事件
    """
    try:
        import time
        
        # 计算时间范围（最近time_window秒）
        end_time = time.time()
        start_time = end_time - time_window
        
        # 加载数据
        df = data_processor.load_data(start_time, end_time)
        
        if df.empty:
            return {
                "success": True,
                "anomalies": [],
                "total_count": 0,
                "time_range": {"start": start_time, "end": end_time}
            }
        
        # 检测异常
        anomalies = data_processor.detect_anomalies(df, "all", {})
        
        # 按时间排序，取最新的
        anomalies.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        limited_anomalies = anomalies[:limit]
        
        return {
            "success": True,
            "anomalies": convert_numpy_types(limited_anomalies),
            "total_count": len(anomalies),
            "time_range": {"start": start_time, "end": end_time}
        }
        
    except Exception as e:
        print(f"获取实时异常失败: {str(e)}")
        return {
            "success": False,
            "message": f"获取实时异常失败: {str(e)}",
            "anomalies": [],
            "total_count": 0
        }

@router.get("/anomaly/types", response_model=dict)
async def get_anomaly_types():
    """
    获取支持的异常类型列表
    """
    anomaly_types = [
        {
            "type": "long_stop",
            "name": "长时间停车",
            "description": "车辆在同一位置停留时间过长",
            "icon": "parking",
            "color": "#ff6b6b",
            "default_threshold": {"duration": 300}
        },
        {
            "type": "abnormal_route",
            "name": "异常绕路",
            "description": "车辆行驶路径明显偏离正常路线",
            "icon": "route",
            "color": "#ffa726",
            "default_threshold": {"detour_ratio": 1.5}
        },
        {
            "type": "speed_anomaly",
            "name": "速度异常",
            "description": "车辆速度异常（过快或过慢）",
            "icon": "speed",
            "color": "#42a5f5",
            "default_threshold": {"low": 5, "high": 80}
        },
        {
            "type": "cluster_anomaly",
            "name": "异常聚集",
            "description": "车辆在特定区域异常聚集",
            "icon": "cluster",
            "color": "#ab47bc",
            "default_threshold": {"density": 50}
        },
        {
            "type": "trajectory_anomaly",
            "name": "轨迹异常",
            "description": "车辆轨迹模式异常",
            "icon": "trajectory",
            "color": "#66bb6a",
            "default_threshold": {"pattern_threshold": 0.7}
        }
    ]
    
    return {
        "success": True,
        "anomaly_types": anomaly_types
    }

@router.get("/anomaly/heatmap", response_model=dict)
async def get_anomaly_heatmap(
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）"),
    anomaly_type: str = Query("all", description="异常类型"),
    resolution: float = Query(0.002, description="热力图分辨率")
):
    """
    获取异常事件热力图数据
    """
    try:
        # 加载数据
        df = data_processor.load_data(start_time, end_time)
        
        if df.empty:
            return {
                "success": False,
                "message": "未找到符合条件的数据",
                "heatmap_points": []
            }
        
        # 检测异常
        anomalies = data_processor.detect_anomalies(df, anomaly_type, {})
        
        # 生成异常热力图
        heatmap_points = data_processor.generate_anomaly_heatmap(anomalies, resolution)
        
        return {
            "success": True,
            "heatmap_points": convert_numpy_types(heatmap_points),
            "total_anomalies": len(anomalies),
            "resolution": resolution
        }
        
    except Exception as e:
        print(f"生成异常热力图失败: {str(e)}")
        return {
            "success": False,
            "message": f"生成异常热力图失败: {str(e)}",
            "heatmap_points": []
        }

@router.get("/spatiotemporal/dynamic-heatmap", response_model=DynamicHeatmapResponse)
async def get_dynamic_heatmap(
    start_time: str,
    end_time: str,
    temporal_resolution: int = 15,
    spatial_resolution: float = 0.001,
    smoothing: bool = True
):
    """
    获取动态热力图数据
    
    Args:
        start_time: 开始时间 (ISO格式)
        end_time: 结束时间 (ISO格式)
        temporal_resolution: 时间分辨率（分钟）
        spatial_resolution: 空间分辨率（度）
        smoothing: 是否平滑处理
    """
    try:
        logger.info(f"获取动态热力图: {start_time} to {end_time}, 时间分辨率: {temporal_resolution}分钟")
        
        # 时间格式转换
        start_timestamp = convert_time_to_timestamp(start_time)
        end_timestamp = convert_time_to_timestamp(end_time)
        
        # 获取数据
        processor = TrafficDataProcessor()
        df = processor.get_data_by_time_range(start_timestamp, end_timestamp)
        
        if df.empty:
            return DynamicHeatmapResponse(
                success=True,
                message="指定时间范围内没有数据",
                frames=[],
                time_series_stats={},
                spatial_stats={}
            )
        
        # 生成动态热力图
        frames = processor.generate_dynamic_heatmap(
            df,
            temporal_resolution=temporal_resolution,
            spatial_resolution=spatial_resolution,
            smoothing=smoothing
        )
        
        # 计算统计信息
        time_series_stats = processor._calculate_time_series_stats(frames)
        spatial_stats = processor._calculate_spatial_stats(df)
        
        # 转换numpy类型
        frames = convert_numpy_types(frames)
        time_series_stats = convert_numpy_types(time_series_stats)
        spatial_stats = convert_numpy_types(spatial_stats)
        
        return DynamicHeatmapResponse(
            success=True,
            message=f"成功生成{len(frames)}个时间帧的动态热力图",
            frames=frames,
            time_series_stats=time_series_stats,
            spatial_stats=spatial_stats
        )
        
    except Exception as e:
        logger.error(f"获取动态热力图时出错: {str(e)}")
        return DynamicHeatmapResponse(
            success=False,
            message=f"获取动态热力图失败: {str(e)}",
            frames=[],
            time_series_stats={},
            spatial_stats={}
        )

@router.post("/spatiotemporal/clustering", response_model=ClusteringResponse)
async def perform_clustering_analysis(
    start_time: str,
    end_time: str,
    request: ClusteringRequest
):
    """
    执行聚类分析
    
    Args:
        start_time: 开始时间
        end_time: 结束时间
        request: 聚类请求参数
    """
    try:
        logger.info(f"执行聚类分析: {request.algorithm}, 数据类型: {request.data_type}")
        
        # 时间转换
        start_timestamp = convert_time_to_timestamp(start_time)
        end_timestamp = convert_time_to_timestamp(end_time)
        
        # 获取数据
        processor = TrafficDataProcessor()
        df = processor.get_data_by_time_range(start_timestamp, end_timestamp)
        
        if df.empty:
            return ClusteringResponse(
                success=False,
                message="指定时间范围内没有数据",
                clusters=[],
                algorithm_used=request.algorithm,
                parameters=request.params,
                statistics={}
            )
        
        # 执行聚类分析
        clusters, metrics = processor.perform_clustering_analysis(
            df,
            data_type=request.data_type,
            algorithm=request.algorithm,
            params=request.params
        )
        
        # 转换数据类型
        clusters = convert_numpy_types(clusters)
        metrics = convert_numpy_types(metrics)
        
        return ClusteringResponse(
            success=True,
            message=f"聚类分析完成，发现{len(clusters)}个聚类",
            clusters=clusters,
            algorithm_used=request.algorithm,
            parameters=request.params,
            statistics=metrics
        )
        
    except Exception as e:
        logger.error(f"聚类分析时出错: {str(e)}")
        return ClusteringResponse(
            success=False,
            message=f"聚类分析失败: {str(e)}",
            clusters=[],
            algorithm_used=request.algorithm,
            parameters=request.params,
            statistics={}
        )

@router.post("/spatiotemporal/od-analysis", response_model=ODFlowResponse)
async def perform_od_analysis(
    start_time: str,
    end_time: str,
    request: ODAnalysisRequest
):
    """
    执行OD对分析
    
    Args:
        start_time: 开始时间
        end_time: 结束时间
        request: OD分析请求参数
    """
    try:
        logger.info(f"执行OD对分析: 最小行程时间 {request.min_trip_duration}秒")
        
        # 时间转换
        start_timestamp = convert_time_to_timestamp(start_time)
        end_timestamp = convert_time_to_timestamp(end_time)
        
        # 获取数据
        processor = TrafficDataProcessor()
        df = processor.get_data_by_time_range(start_timestamp, end_timestamp)
        
        if df.empty:
            return ODFlowResponse(
                success=False,
                message="指定时间范围内没有数据",
                od_pairs=[],
                top_flows=[],
                statistics={}
            )
        
        # 提取OD对
        od_pairs = processor.extract_od_pairs_from_data(
            df,
            min_trip_duration=request.min_trip_duration,
            max_trip_duration=request.max_trip_duration,
            min_trip_distance=request.min_trip_distance
        )
        
        if not od_pairs:
            return ODFlowResponse(
                success=True,
                message="未找到符合条件的OD对",
                od_pairs=[],
                top_flows=[],
                statistics={}
            )
        
        # OD流量分析
        from .od_analysis_engine import ODAnalysisEngine
        od_engine = ODAnalysisEngine()
        od_engine.od_pairs = od_pairs
        
        # 分析顶级流量
        top_flows = od_engine.analyze_top_flows(od_pairs, top_k=20)
        
        # 计算统计信息
        statistics = od_engine.calculate_od_statistics(od_pairs)
        
        # 生成流量矩阵（如果请求聚合级别需要）
        flow_matrix = None
        if request.aggregate_level == "grid":
            matrix, grid_info = od_engine.generate_flow_matrix(od_pairs)
            if matrix.size > 0:
                flow_matrix = matrix.tolist()
                statistics['grid_info'] = grid_info
        
        # 转换数据类型
        od_pairs = convert_numpy_types(od_pairs)
        top_flows = convert_numpy_types(top_flows)
        statistics = convert_numpy_types(statistics)
        
        return ODFlowResponse(
            success=True,
            message=f"OD分析完成，找到{len(od_pairs)}个OD对",
            od_pairs=od_pairs,
            flow_matrix=flow_matrix,
            top_flows=top_flows,
            statistics=statistics
        )
        
    except Exception as e:
        logger.error(f"OD分析时出错: {str(e)}")
        return ODFlowResponse(
            success=False,
            message=f"OD分析失败: {str(e)}",
            od_pairs=[],
            top_flows=[],
            statistics={}
        )

@router.post("/spatiotemporal/comprehensive", response_model=SpatioTemporalResponse)
async def perform_comprehensive_analysis(
    start_time: str,
    end_time: str,
    heatmap_request: HeatmapRequest
):
    """
    执行综合时空分析
    
    Args:
        start_time: 开始时间
        end_time: 结束时间
        heatmap_request: 热力图分析参数
    """
    try:
        logger.info(f"执行综合时空分析: {start_time} to {end_time}")
        
        # 时间转换
        start_timestamp = convert_time_to_timestamp(start_time)
        end_timestamp = convert_time_to_timestamp(end_time)
        
        # 获取数据
        processor = TrafficDataProcessor()
        df = processor.get_data_by_time_range(start_timestamp, end_timestamp)
        
        if df.empty:
            return SpatioTemporalResponse(
                success=False,
                message="指定时间范围内没有数据",
                analysis_type="comprehensive",
                data=SpatioTemporalAnalysis(
                    analysis_type="comprehensive",
                    time_range={},
                    spatial_bounds={},
                    data=[],
                    statistics={},
                    algorithm_params={}
                )
            )
        
        # 生成时空热力图分析
        analysis_result = processor.generate_spatiotemporal_heatmap(
            df,
            analysis_type="comprehensive",
            temporal_resolution=heatmap_request.temporal_resolution,
            spatial_resolution=heatmap_request.spatial_resolution
        )
        
        # 构造响应数据
        spatiotemporal_data = SpatioTemporalAnalysis(
            analysis_type="comprehensive",
            time_range=analysis_result['time_range'],
            spatial_bounds=analysis_result['spatial_bounds'],
            data=analysis_result['heatmap_frames'],  # 时间帧数据
            statistics={
                'time_series_stats': analysis_result['time_series_stats'],
                'spatial_stats': analysis_result['spatial_stats']
            },
            algorithm_params=analysis_result['algorithm_params']
        )
        
        # 转换数据类型
        spatiotemporal_data_dict = convert_numpy_types(spatiotemporal_data.dict())
        
        return SpatioTemporalResponse(
            success=True,
            message="综合时空分析完成",
            analysis_type="comprehensive",
            data=SpatioTemporalAnalysis(**spatiotemporal_data_dict),
            processing_time=None
        )
        
    except Exception as e:
        logger.error(f"综合时空分析时出错: {str(e)}")
        return SpatioTemporalResponse(
            success=False,
            message=f"综合时空分析失败: {str(e)}",
            analysis_type="comprehensive",
            data=SpatioTemporalAnalysis(
                analysis_type="comprehensive",
                time_range={},
                spatial_bounds={},
                data=[],
                statistics={},
                algorithm_params={}
            )
        )

@router.get("/spatiotemporal/algorithms")
async def get_available_algorithms():
    """获取可用的聚类算法列表"""
    try:
        from .clustering_engine import ClusteringEngine
        
        clustering_engine = ClusteringEngine()
        algorithms = clustering_engine.get_available_algorithms()
        
        algorithm_info = {}
        for algo in algorithms:
            algorithm_info[algo] = clustering_engine.get_algorithm_params(algo)
        
        return {
            "success": True,
            "message": "获取算法列表成功",
            "algorithms": algorithms,
            "algorithm_params": algorithm_info
        }
        
    except Exception as e:
        logger.error(f"获取算法列表时出错: {str(e)}")
        return {
            "success": False,
            "message": f"获取算法列表失败: {str(e)}",
            "algorithms": [],
            "algorithm_params": {}
        }

# 路段分析相关API接口

@router.post("/api/road/analysis", response_model=RoadAnalysisResponse)
async def analyze_road_segments(request: RoadAnalysisRequest):
    """
    路段分析API
    分析道路网络的通行状况、速度分布、拥堵情况等
    """
    try:
        start_time = time.time()
        
        # 获取当前时间作为时间范围（演示用）
        current_time = time.time()
        start_timestamp = current_time - 24 * 3600  # 24小时前
        end_timestamp = current_time
        
        # 加载数据
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(start_timestamp, end_timestamp)
        
        if df.empty:
            return RoadAnalysisResponse(
                success=False,
                message="没有可用的交通数据",
                analysis=RoadNetworkAnalysis(
                    analysis_type=request.analysis_type,
                    time_range={"start": start_timestamp, "end": end_timestamp},
                    total_segments=0,
                    segments_data=[],
                    network_summary={},
                    bottleneck_segments=[]
                ),
                speed_distributions=[],
                flow_patterns=[],
                processing_time=time.time() - start_time
            )
        
        # 执行路段分析
        analysis_result = data_processor.analyze_road_segments(
            df,
            analysis_type=request.analysis_type,
            segment_types=request.segment_types,
            aggregation_level=request.aggregation_level,
            min_vehicles=request.min_vehicles
        )
        
        if "error" in analysis_result:
            return RoadAnalysisResponse(
                success=False,
                message=analysis_result["error"],
                analysis=RoadNetworkAnalysis(
                    analysis_type=request.analysis_type,
                    time_range={"start": start_timestamp, "end": end_timestamp},
                    total_segments=0,
                    segments_data=[],
                    network_summary={},
                    bottleneck_segments=[]
                ),
                speed_distributions=[],
                flow_patterns=[],
                processing_time=time.time() - start_time
            )
        
        # 构建分析结果
        metadata = analysis_result.get("analysis_metadata", {})
        time_range = metadata.get("time_range", {"start": start_timestamp, "end": end_timestamp})
        
        # 转换路段统计数据
        segment_stats_data = analysis_result.get("segment_statistics", [])
        segments_data = []
        for stats in segment_stats_data:
            segment_stat = RoadSegmentStatistics(**stats)
            segments_data.append(segment_stat)
        
        # 构建网络分析对象
        network_analysis = RoadNetworkAnalysis(
            analysis_type=request.analysis_type,
            time_range=time_range,
            total_segments=metadata.get("total_segments", 0),
            segments_data=segments_data,
            network_summary=analysis_result.get("network_summary", {}),
            bottleneck_segments=analysis_result.get("bottlenecks", [])
        )
        
        # 转换速度分布数据
        speed_distributions = []
        if "speed_distributions" in analysis_result:
            for dist_data in analysis_result["speed_distributions"]:
                speed_dist = SpeedDistribution(**dist_data)
                speed_distributions.append(speed_dist)
        
        # 转换流量模式数据
        flow_patterns = []
        if "flow_patterns" in analysis_result:
            for pattern_data in analysis_result["flow_patterns"]:
                flow_pattern = TrafficFlowPattern(**pattern_data)
                flow_patterns.append(flow_pattern)
        
        processing_time = time.time() - start_time
        
        return RoadAnalysisResponse(
            success=True,
            message=f"成功分析了 {metadata.get('active_segments', 0)} 个路段",
            analysis=network_analysis,
            speed_distributions=speed_distributions,
            flow_patterns=flow_patterns,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"路段分析API错误: {str(e)}")
        return RoadAnalysisResponse(
            success=False,
            message=f"分析失败: {str(e)}",
            analysis=RoadNetworkAnalysis(
                analysis_type=request.analysis_type,
                time_range={"start": 0, "end": 0},
                total_segments=0,
                segments_data=[],
                network_summary={},
                bottleneck_segments=[]
            ),
            speed_distributions=[],
            flow_patterns=[]
        )

@router.get("/api/road/segments", response_model=RoadSegmentResponse)
async def get_road_segments():
    """
    获取路段信息API
    返回当前系统识别的所有路段基础信息
    """
    try:
        # 获取最近的数据来提取路段
        current_time = time.time()
        start_timestamp = current_time - 3600  # 1小时前
        end_timestamp = current_time
        
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(start_timestamp, end_timestamp)
        
        if df.empty:
            return RoadSegmentResponse(
                success=False,
                message="没有可用的数据来提取路段信息",
                segments=[],
                total_segments=0
            )
        
        # 执行简单的路段分析来获取路段信息
        analysis_result = data_processor.analyze_road_segments(
            df,
            analysis_type="comprehensive",
            min_vehicles=1  # 降低阈值以获取更多路段
        )
        
        if "error" in analysis_result:
            return RoadSegmentResponse(
                success=False,
                message=analysis_result["error"],
                segments=[],
                total_segments=0
            )
        
        # 转换路段数据
        segments_data = analysis_result.get("segments", [])
        segments = []
        for segment_data in segments_data:
            segment = RoadSegment(**segment_data)
            segments.append(segment)
        
        return RoadSegmentResponse(
            success=True,
            message=f"成功获取 {len(segments)} 个路段信息",
            segments=segments,
            total_segments=len(segments)
        )
        
    except Exception as e:
        logger.error(f"获取路段信息API错误: {str(e)}")
        return RoadSegmentResponse(
            success=False,
            message=f"获取失败: {str(e)}",
            segments=[],
            total_segments=0
        )

@router.post("/api/road/traffic", response_model=RoadTrafficResponse)
async def get_road_traffic_data(time_range: Dict[str, float]):
    """
    获取路段交通数据API
    返回指定时间范围内的路段交通状况数据
    """
    try:
        start_timestamp = time_range.get("start", time.time() - 3600)
        end_timestamp = time_range.get("end", time.time())
        
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(start_timestamp, end_timestamp)
        
        if df.empty:
            return RoadTrafficResponse(
                success=False,
                message="指定时间范围内没有交通数据",
                traffic_data=[],
                statistics={}
            )
        
        # 执行路段分析
        analysis_result = data_processor.analyze_road_segments(
            df,
            analysis_type="comprehensive",
            min_vehicles=5
        )
        
        if "error" in analysis_result:
            return RoadTrafficResponse(
                success=False,
                message=analysis_result["error"],
                traffic_data=[],
                statistics={}
            )
        
        # 转换交通数据
        traffic_data_list = analysis_result.get("traffic_data", [])
        traffic_data = []
        for data in traffic_data_list:
            traffic_item = RoadTrafficData(**data)
            traffic_data.append(traffic_item)
        
        # 生成统计信息
        statistics = {
            "total_records": len(traffic_data),
            "time_range": {"start": start_timestamp, "end": end_timestamp},
            "avg_speed": np.mean([t.avg_speed for t in traffic_data]) if traffic_data else 0,
            "avg_flow": np.mean([t.flow_rate for t in traffic_data]) if traffic_data else 0,
            "congestion_summary": {}
        }
        
        # 拥堵分布统计
        congestion_counts = {}
        for t in traffic_data:
            level = t.congestion_level
            congestion_counts[level] = congestion_counts.get(level, 0) + 1
        statistics["congestion_summary"] = congestion_counts
        
        return RoadTrafficResponse(
            success=True,
            message=f"成功获取 {len(traffic_data)} 条交通数据记录",
            traffic_data=traffic_data,
            statistics=statistics
        )
        
    except Exception as e:
        logger.error(f"获取交通数据API错误: {str(e)}")
        return RoadTrafficResponse(
            success=False,
            message=f"获取失败: {str(e)}",
            traffic_data=[],
            statistics={}
        )

@router.post("/api/road/visualization", response_model=RoadVisualizationResponse)
async def get_road_visualization_data(request: Dict[str, Any]):
    """
    获取路段可视化数据API
    生成用于地图展示的路段可视化数据
    """
    try:
        visualization_type = request.get("visualization_type", "speed")
        time_range = request.get("time_range", {})
        
        start_timestamp = time_range.get("start", time.time() - 3600)
        end_timestamp = time_range.get("end", time.time())
        
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(start_timestamp, end_timestamp)
        
        if df.empty:
            return RoadVisualizationResponse(
                success=False,
                message="没有可用的数据进行可视化",
                visualization_data={},
                segment_colors={},
                legend_info={}
            )
        
        # 执行路段分析
        analysis_result = data_processor.analyze_road_segments(
            df,
            analysis_type="comprehensive",
            min_vehicles=3
        )
        
        if "error" in analysis_result:
            return RoadVisualizationResponse(
                success=False,
                message=analysis_result["error"],
                visualization_data={},
                segment_colors={},
                legend_info={}
            )
        
        # 生成可视化数据
        segments_data = analysis_result.get("segments", [])
        traffic_data = analysis_result.get("traffic_data", [])
        
        visualization_data = data_processor.generate_road_visualization_data(
            segments_data,
            traffic_data,
            visualization_type
        )
        
        if "error" in visualization_data:
            return RoadVisualizationResponse(
                success=False,
                message=visualization_data["error"],
                visualization_data={},
                segment_colors={},
                legend_info={}
            )
        
        return RoadVisualizationResponse(
            success=True,
            message=f"成功生成 {len(visualization_data.get('segments', []))} 个路段的可视化数据",
            visualization_data=visualization_data,
            segment_colors=visualization_data.get("color_mapping", {}),
            legend_info=visualization_data.get("legend", {})
        )
        
    except Exception as e:
        logger.error(f"路段可视化API错误: {str(e)}")
        return RoadVisualizationResponse(
            success=False,
            message=f"生成可视化数据失败: {str(e)}",
            visualization_data={},
            segment_colors={},
            legend_info={}
        )

@router.get("/api/road/metrics", response_model=Dict[str, Any])
async def get_road_network_metrics():
    """
    获取路网整体指标API
    返回道路网络的综合性能指标
    """
    try:
        # 使用当前时间范围（演示用）
        current_time = time.time()
        start_timestamp = current_time - 24 * 3600  # 24小时前
        end_timestamp = current_time
        
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(start_timestamp, end_timestamp)
        
        if df.empty:
            return {
                "success": False,
                "message": "没有可用的交通数据",
                "metrics": {}
            }
        
        # 执行路段分析获取基础数据
        analysis_result = data_processor.analyze_road_segments(
            df,
            analysis_type="comprehensive",
            min_vehicles=3
        )
        
        if "error" in analysis_result:
            return {
                "success": False,
                "message": analysis_result["error"],
                "metrics": {}
            }
        
        # 计算网络指标
        segments_data = analysis_result.get("segments", [])
        traffic_data = analysis_result.get("traffic_data", [])
        
        metrics = data_processor.calculate_road_network_metrics(segments_data, traffic_data)
        
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": time.time()
        }
    
    except Exception as e:
        logger.error(f"获取路网指标失败: {str(e)}")
        return {
            "success": False,
            "message": f"获取路网指标失败: {str(e)}",
            "metrics": {}
        }

@router.get("/weekly-passenger-flow", response_model=Dict[str, Any])
async def get_weekly_passenger_flow_analysis(
    start_time: float = Query(..., description="开始时间戳（UTC）"),
    end_time: float = Query(..., description="结束时间戳（UTC）")
):
    """
    获取周客流量分析数据
    
    Args:
        start_time: 开始时间戳（UTC）
        end_time: 结束时间戳（UTC）
    
    Returns:
        周客流量分析结果，包括日流量对比、工作日vs周末、高峰时段等
    """
    try:
        logger.info(f"开始周客流量分析: {start_time} - {end_time}")
        
        # 验证时间范围（确保至少有3天数据）
        time_span = end_time - start_time
        if time_span < 3 * 24 * 3600:  # 少于3天
            return {
                "success": False,
                "message": "分析周客流量需要至少3天的数据",
                "data": {}
            }
        
        # 加载数据
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(start_time, end_time)
        
        if df.empty:
            return {
                "success": False,
                "message": "指定时间范围内没有交通数据",
                "data": {}
            }
        
        # 执行周客流量分析
        analysis_result = data_processor.analyze_weekly_passenger_flow(df)
        
        if not analysis_result.get('success', False):
            return {
                "success": False,
                "message": analysis_result.get('message', '分析失败'),
                "data": {}
            }
        
        # 添加额外的元数据
        analysis_result['metadata'] = {
            'query_start_time': start_time,
            'query_end_time': end_time,
            'analysis_timestamp': time.time(),
            'data_quality': {
                'total_records': len(df),
                'unique_vehicles': df['COMMADDR'].nunique() if 'COMMADDR' in df.columns else 0,
                'time_coverage': analysis_result.get('analysis_period', {})
            }
        }
        
        logger.info(f"周客流量分析完成，数据质量: {analysis_result['metadata']['data_quality']}")
        
        return {
            "success": True,
            "message": "周客流量分析完成",
            "data": analysis_result
        }
        
    except Exception as e:
        logger.error(f"周客流量分析失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            "success": False,
            "message": f"分析失败: {str(e)}",
            "data": {}
        }




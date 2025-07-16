from typing import Tuple
from fastapi import APIRouter, Query, Depends, HTTPException, Request, Body
import pandas as pd
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Optional, Any, Union
from .data_processor import TrafficDataProcessor
from .heatmap import HeatmapGenerator
from .track import TrackAnalyzer
from .traffic_analysis_cache import get_traffic_cache
from .log import logger  # 导入自定义日志记录器
# from .data_cleaner import TrafficDataCleaner, DataQualityAnalyzer  # 已删除数据清洗功能
from .traffic_statistics_loader import TrafficStatisticsLoader
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
    RoadNetworkAnalysis, SpeedDistribution, TrafficFlowPattern,
    SmartPassengerRequest, SmartPassengerResponse, WeatherImpactRequest,
    WeatherImpactResponse, TaxiDemandRequest, TaxiDemandResponse,
    PassengerVisualizationResponse, WeatherData, PassengerFlowData,
    TaxiDemandData, WeatherImpactAnalysis, TaxiSupplyDemand,
    TripAnalysisRequest, TripAnalysisResponse, TripAnalysisStatistics,
    OrderSpeedAnalysisRequest, OrderSpeedAnalysisResponse,
    TripDistanceClassification, OrderSpeedAnalysis
)
import numpy as np
import logging
import traceback
import time
import json
from pydantic import BaseModel
from .traffic_analysis_cache import get_traffic_cache
from functools import lru_cache

CACHE_DIR = os.path.join(os.path.dirname(__file__), 'data', 'cache')

router = APIRouter()
print("[DEBUG] traffic_visualization.service.py loaded")
print("[DEBUG] router id:", id(router))

# 设置标准日志（用于调试）
logging.basicConfig(level=logging.INFO)
standard_logger = logging.getLogger(__name__)

# 创建数据处理器实例
data_processor = TrafficDataProcessor()
heatmap_generator = HeatmapGenerator()
track_analyzer = TrackAnalyzer()
traffic_stats_loader = TrafficStatisticsLoader()

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
                    logger.error("热力图生成", f"读取热力图文件 {filename} 失败: {e}", source="文件读取", user="系统")

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
        logger.error("热力图生成", f"快速热力图生成失败: {e}", source="文件读取", user="系统")
        return []


@router.get("/test")
async def test_endpoint():
    """测试端点，确保路由正常工作"""
    logger.info("系统管理", "交通可视化路由测试", source="API调用", user="系统")
    return {"message": "Traffic router is working!", "status": "ok"}


@router.get("/summary")
async def get_traffic_summary():
    """获取交通数据概要统计信息"""
    try:
        # 获取基本的数据统计信息
        data_dir = os.path.join(os.path.dirname(__file__), 'data')

        # 计算文件数量和总大小
        file_count = 0
        total_size = 0

        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.csv') or file.endswith('.parquet'):
                    file_path = os.path.join(root, file)
                    file_count += 1
                    total_size += os.path.getsize(file_path)

        # 获取数据时间范围
        time_range = {
            "start": 1378944000,  # 2013-09-12 00:00:00 UTC
            "end": 1379548799  # 2013-09-18 23:59:59 UTC
        }

        # 获取车辆数量估计
        vehicle_count = data_processor.get_vehicle_count_estimate()

        # 获取数据点数量估计
        point_count = data_processor.get_point_count_estimate()

        # 构造响应
        return {
            "success": True,
            "message": "获取交通数据概要成功",
            "summary": {
                "time_range": time_range,
                "vehicle_count": vehicle_count,
                "point_count": point_count,
                "file_count": file_count,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "data_source": "T-Drive轨迹数据集",
                "description": "北京市出租车轨迹数据集，包含多天的GPS轨迹数据"
            }
        }
    except Exception as e:
        logger.error("系统管理", f"获取交通数据概要失败: {str(e)}", source="API调用", user="系统")
        return {
            "success": False,
            "message": f"获取交通数据概要失败: {str(e)}",
            "summary": {
                "time_range": {"start": 0, "end": 0},
                "vehicle_count": 0,
                "point_count": 0,
                "file_count": 0,
                "total_size_mb": 0,
                "data_source": "未知",
                "description": "数据加载失败"
            }
        }


@router.get("/files/info")
async def get_data_files_info():
    """获取数据文件信息"""
    try:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')

        # 获取文件列表
        files_info = []

        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.csv') or file.endswith('.parquet'):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    file_modified = os.path.getmtime(file_path)

                    # 计算文件中的记录数（估计值）
                    record_count = 0
                    if file.endswith('.csv'):
                        try:
                            with open(file_path, 'r') as f:
                                for i, _ in enumerate(f):
                                    if i >= 10:  # 只读取前10行来估计
                                        break
                                    record_count += 1
                            # 根据文件大小估算总行数
                            if record_count > 0:
                                avg_line_size = os.path.getsize(file_path) / record_count
                                record_count = int(file_size / avg_line_size)
                        except:
                            record_count = 0

                    # 构造文件信息
                    rel_path = os.path.relpath(file_path, data_dir)
                    files_info.append({
                        "filename": file,
                        "path": rel_path,
                        "size": file_size,
                        "size_formatted": f"{file_size / (1024 * 1024):.2f} MB" if file_size > 1024 * 1024 else f"{file_size / 1024:.2f} KB",
                        "modified": file_modified,
                        "modified_formatted": datetime.fromtimestamp(file_modified).strftime('%Y-%m-%d %H:%M:%S'),
                        "record_count_estimate": record_count
                    })

        # 按修改时间排序
        files_info.sort(key=lambda x: x["modified"], reverse=True)

        return {
            "success": True,
            "message": "获取数据文件信息成功",
            "files": files_info,
            "total_files": len(files_info),
            "total_size": sum(f["size"] for f in files_info),
            "total_size_formatted": f"{sum(f['size'] for f in files_info) / (1024 * 1024):.2f} MB"
        }
    except Exception as e:
        logger.error(f"获取数据文件信息失败: {str(e)}")
        return {
            "success": False,
            "message": f"获取数据文件信息失败: {str(e)}",
            "files": [],
            "total_files": 0,
            "total_size": 0,
            "total_size_formatted": "0 MB"
        }


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

        # 记录API调用日志
        try:
            logger.traffic(
                "数据总览可视化",
                f"数据总览可视化API调用",
                source="API调用",
                user="系统",
                details={
                    "start_time": start_time,
                    "end_time": end_time,
                    "view_type": view_type,
                    "vehicle_id": vehicle_id,
                    "map_style": map_style
                }
            )
        except Exception as log_error:
            print(f"日志记录失败: {log_error}")

        # 验证时间范围
        min_valid_time = 1378944000  # 2013-09-12 00:00:00 UTC
        max_valid_time = 1379548799  # 2013-09-18 23:59:59 UTC

        if end_time < min_valid_time or start_time > max_valid_time:
            print(f"时间范围验证失败: {start_time}-{end_time} 超出有效范围 {min_valid_time}-{max_valid_time}")

            # 记录时间范围错误日志
            try:
                logger.warning(
                    "数据总览可视化",
                    f"数据总览查询时间范围超出数据集范围",
                    source="API调用",
                    user="系统",
                    details={
                        "start_time": start_time,
                        "end_time": end_time,
                        "min_valid_time": min_valid_time,
                        "max_valid_time": max_valid_time
                    }
                )
            except Exception as log_error:
                print(f"日志记录失败: {log_error}")

            return TrafficDataResponse(
                success=False,
                message="查询时间超出数据集范围（2013年9月12日至9月18日）",
                view_type=view_type,
                data=[],
                points=0
            )

        # 加载数据
        try:
            print(f"开始加载数据...")
            # 处理vehicle_id参数，确保不为None
            vehicle_id_param = vehicle_id if vehicle_id else ""
            df = data_processor.load_data(start_time, end_time, vehicle_id_param)
            print(f"数据加载完成, 共 {len(df)} 条记录")

            # 记录数据加载成功日志
            try:
                logger.info(
                    "数据总览可视化",
                    f"数据总览数据加载成功，共 {len(df)} 条记录",
                    source="API调用",
                    user="系统",
                    details={
                        "start_time": start_time,
                        "end_time": end_time,
                        "data_count": len(df),
                        "view_type": view_type
                    }
                )
            except Exception as log_error:
                print(f"日志记录失败: {log_error}")

        except Exception as load_error:
            print(f"数据加载错误: {str(load_error)}")
            import traceback
            print(traceback.format_exc())

            # 记录数据加载失败日志
            try:
                logger.error(
                    "数据总览可视化",
                    f"数据总览数据加载失败: {str(load_error)}",
                    source="API调用",
                    user="系统",
                    details={
                        "start_time": start_time,
                        "end_time": end_time,
                        "error_message": str(load_error),
                        "error_stack": traceback.format_exc()
                    }
                )
            except Exception as log_error:
                print(f"日志记录失败: {log_error}")

            return TrafficDataResponse(
                success=False,
                message=f"数据加载失败: {str(load_error)}",
                view_type=view_type,
                data=[],
                points=0
            )

        if df.empty:
            print("加载的数据为空")

            # 记录数据为空日志
            try:
                logger.warning(
                    "数据总览可视化",
                    f"数据总览查询未找到符合条件的数据",
                    source="API调用",
                    user="系统",
                    details={
                        "start_time": start_time,
                        "end_time": end_time,
                        "view_type": view_type
                    }
                )
            except Exception as log_error:
                print(f"日志记录失败: {log_error}")

            return TrafficDataResponse(
                success=False,
                message="未找到符合条件的数据",
                view_type=view_type,
                data=[],
                points=0
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
                vehicle_id_param = vehicle_id if vehicle_id else ""
                tracks = data_processor.generate_track_data(df, vehicle_id_param)
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
                    sample_size = 8000  # 中等数据集显示8千个点
                else:
                    sample_size = min(len(df), 5000)  # 小数据集显示全部或5千个点
                df_sampled = df.sample(sample_size) if len(df) > sample_size else df

                data = []
                for _, row in df_sampled.iterrows():
                    # 计算速度（如果没有预计算的速度，则从GPS数据计算）
                    speed = 0.0
                    if "SPEED" in row and pd.notna(row["SPEED"]):
                        speed = float(row["SPEED"])
                    elif "speed" in row and pd.notna(row["speed"]):
                        speed = float(row["speed"])
                    elif "speed_kmh" in row and pd.notna(row["speed_kmh"]):
                        speed = float(row["speed_kmh"])

                    point = {
                        "lng": float(row["LON"]) / 1e5,
                        "lat": float(row["LAT"]) / 1e5,
                        "vehicle_id": str(row["COMMADDR"]),  # 确保转换为字符串
                        "timestamp": int(row["UTC"]),  # 确保转换为Python int
                        "speed": speed  # 添加速度字段
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
                data=[],
                points=0
            )

        # 计算统计信息
        try:
            print("开始计算统计信息...")
            stats = data_processor.calculate_statistics(df)
            print("统计信息计算完成")
            # 确保所有数据都是可序列化的
            # 修复：只传递TrafficOverview对象或None给stats
            stats_obj = None
            if isinstance(stats, dict) and all(k in stats for k in
                                               ["total_vehicles", "total_points", "active_vehicles", "time_span",
                                                "coverage_area", "average_speed"]):
                try:
                    from .models import TrafficOverview
                    stats_obj = TrafficOverview(**stats)
                except ImportError:
                    # 如果导入失败，使用None
                    stats_obj = None
            elif hasattr(stats, '__class__') and stats.__class__.__name__ == 'TrafficOverview':
                stats_obj = stats
            # 其余情况不传递stats

            # 记录查询成功日志
            try:
                logger.info(
                    "数据总览可视化",
                    f"数据总览查询成功，返回 {len(data)} 条数据",
                    source="API调用",
                    user="系统",
                    details={
                        "start_time": start_time,
                        "end_time": end_time,
                        "data_count": len(data),
                        "view_type": view_type,
                        "map_style": map_style
                    }
                )
            except Exception as log_error:
                print(f"日志记录失败: {log_error}")

            return TrafficDataResponse(
                success=True,
                message="数据获取成功",
                view_type=view_type,
                data=convert_numpy_types(data),
                stats=stats_obj
            )
        except Exception as stats_error:
            print(f"统计信息计算错误: {str(stats_error)}")

            # 记录统计计算失败日志
            try:
                logger.warning(
                    "数据总览可视化",
                    f"数据总览统计信息计算失败，但数据获取成功",
                    source="API调用",
                    user="系统",
                    details={
                        "start_time": start_time,
                        "end_time": end_time,
                        "data_count": len(data),
                        "view_type": view_type,
                        "error_message": str(stats_error)
                    }
                )
            except Exception as log_error:
                print(f"日志记录失败: {log_error}")

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

        # 记录未预期错误日志
        try:
            logger.error(
                "数据总览可视化",
                f"数据总览查询发生未预期错误: {str(e)}",
                source="API调用",
                user="系统",
                details={
                    "start_time": start_time,
                    "end_time": end_time,
                    "view_type": view_type,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "error_stack": traceback.format_exc()
                }
            )
        except Exception as log_error:
            print(f"日志记录失败: {log_error}")

        return TrafficDataResponse(
            success=False,
            message=f"服务器内部错误: {str(e)}",
            view_type=view_type,
            data=[],
            points=0
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
        # 记录热力图请求
        print(f"🔥 热力图API开始: {start_time} - {end_time}")
        logger.traffic("热力图生成", f"开始生成热力图，时间范围: {start_time} - {end_time}",
                       source="API调用", user="用户",
                       details={"start_time": start_time, "end_time": end_time, "resolution": resolution})

        # 优先尝试预计算数据
        print("尝试使用预计算热力图数据...")
        fast_heatmap_data = _get_fast_heatmap_data(start_time, end_time)

        if fast_heatmap_data:
            print(f"✅ 使用快速热力图数据: {len(fast_heatmap_data)} 个点")
            logger.traffic("热力图生成", f"使用预计算热力图数据，共 {len(fast_heatmap_data)} 个点",
                           source="API调用", user="用户",
                           details={"point_count": len(fast_heatmap_data), "method": "precomputed"})
            return HeatmapResponse(
                success=True,
                data=fast_heatmap_data,
                message=f"快速热力图生成成功，共 {len(fast_heatmap_data)} 个点",
                points=fast_heatmap_data
            )

        print("⚠️ 预计算数据不可用，使用实时计算...")
        logger.traffic("热力图生成", "预计算数据不可用，使用实时计算", source="API调用", user="用户")

        # 加载数据
        print("📊 开始加载数据...")
        df = data_processor.load_data(start_time, end_time)

        if df.empty:
            logger.warning("热力图生成", "未找到符合条件的数据", source="API调用", user="用户")
            return HeatmapResponse(
                success=False,
                message="未找到符合条件的数据",
                points=[]
            )

        # 生成热力图数据
        heatmap_points = data_processor.generate_heatmap_data(df, resolution)

        # 记录成功日志
        logger.traffic("热力图生成", f"实时热力图生成成功，共 {len(heatmap_points)} 个点",
                       source="API调用", user="用户",
                       details={"point_count": len(heatmap_points), "method": "realtime"})

        # 构造响应
        return HeatmapResponse(
            success=True,
            points=heatmap_points
        )
    except Exception as e:
        logger.error("热力图生成", f"获取热力图数据失败: {str(e)}", source="API调用", user="用户")
        return HeatmapResponse(
            success=False,
            message=f"获取热力图数据失败: {str(e)}",
            points=[]
        )


@router.get("/track", response_model=TracksResponse)
async def get_track(
        start_time: float = Query(..., description="开始时间戳（UTC）"),
        end_time: float = Query(..., description="结束时间戳（UTC）"),
        vehicle_id: Optional[str] = Query(None, description="车辆ID，可选"),
        view_type: str = Query("trajectory", description="视图类型：trajectory, path, stops"),
        performance_mode: str = Query("normal", description="性能模式：fast, medium, full"),
        max_points: int = Query(5000, description="最大返回点数")
):
    """
    按时间段和车辆ID查询车辆轨迹数据。
    支持性能模式和最大点数限制。
    """
    try:
        # 记录轨迹查询请求
        logger.traffic("轨迹查询", f"开始查询轨迹，时间范围: {start_time} - {end_time}, 车辆: {vehicle_id}",
                       source="API调用", user="用户",
                       details={"start_time": start_time, "end_time": end_time, "vehicle_id": vehicle_id,
                                "performance_mode": performance_mode, "max_points": max_points})

        print(
            f"🚗 轨迹查询参数: 时间={start_time}-{end_time}, 车辆={vehicle_id}, 模式={performance_mode}, 最大点数={max_points}")

        # 加载数据
        if vehicle_id:
            df = data_processor.load_data(start_time, end_time, vehicle_id)
        else:
            df = data_processor.load_data(start_time, end_time)

        if df.empty:
            print(f"⚠️ 未找到车辆 {vehicle_id} 在时间段 {start_time}-{end_time} 的数据")
            logger.warning("轨迹查询", f"未找到车辆 {vehicle_id} 在指定时间段的数据", source="API调用", user="用户")
            return TracksResponse(
                success=False,
                message=f"未找到车辆 {vehicle_id} 在指定时间段的数据",
                tracks=[],
                points=0
            )

        print(f"✅ 成功加载数据: {len(df)} 条记录")

        # 根据性能模式采样数据
        if performance_mode == "fast" and len(df) > max_points:
            # 快速模式：均匀采样
            sample_ratio = max_points / len(df)
            df = df.sample(frac=sample_ratio)
            print(f"⚡ 快速模式: 采样后 {len(df)} 条记录")
        elif performance_mode == "medium" and len(df) > max_points:
            # 中等模式：保留关键点的采样
            # 这里简化为随机采样，实际可以用更复杂的算法
            sample_ratio = max_points / len(df)
            df = df.sample(frac=sample_ratio)
            print(f"📊 中等模式: 采样后 {len(df)} 条记录")

        # 生成轨迹数据
        tracks = data_processor.generate_track_data(df, vehicle_id)

        if not tracks:
            print(f"⚠️ 轨迹生成失败: 车辆 {vehicle_id}")
            return TracksResponse(
                success=False,
                message=f"未能生成车辆 {vehicle_id} 的轨迹数据",
                tracks=[],
                points=0
            )

        print(f"✅ 轨迹生成成功: {len(tracks)} 条轨迹, 共 {sum(len(t.points) for t in tracks)} 个点")

        # 记录成功日志
        logger.traffic("轨迹查询", f"轨迹查询成功，共 {len(tracks)} 条轨迹, {sum(len(t.points) for t in tracks)} 个点",
                       source="API调用", user="用户",
                       details={"track_count": len(tracks), "point_count": sum(len(t.points) for t in tracks),
                                "vehicle_id": vehicle_id, "performance_mode": performance_mode})

        # 构造响应
        return TracksResponse(
            success=True,
            tracks=tracks
        )
    except Exception as e:
        import traceback
        print(f"❌ 轨迹查询失败: {str(e)}")
        print(traceback.format_exc())
        logger.error("轨迹查询", f"获取轨迹数据失败: {str(e)}", source="API调用", user="用户")
        return TracksResponse(
            success=False,
            message=f"获取轨迹数据失败: {str(e)}",
            tracks=[],
            points=0
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
        duration_labels = [f"{bins[i]}-{bins[i + 1]}" for i in range(len(duration_bins) - 1)]

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
        distance_labels = [f"{bins[i]}-{bins[i + 1]}" for i in range(len(distance_bins) - 1)]

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
    使用真实数据格式的数字车辆ID
    """
    # 基于真实数据的常见车辆ID（数字格式）
    static_vehicles = [
        {"vehicle_id": "15053114280", "data_points": 150, "description": "车辆 15053114280 (150个数据点)"},
        {"vehicle_id": "15053114281", "data_points": 120, "description": "车辆 15053114281 (120个数据点)"},
        {"vehicle_id": "15053114282", "data_points": 200, "description": "车辆 15053114282 (200个数据点)"},
        {"vehicle_id": "15053114283", "data_points": 180, "description": "车辆 15053114283 (180个数据点)"},
        {"vehicle_id": "15053114284", "data_points": 160, "description": "车辆 15053114284 (160个数据点)"},
        {"vehicle_id": "15053114285", "data_points": 140, "description": "车辆 15053114285 (140个数据点)"},
        {"vehicle_id": "15053114286", "data_points": 190, "description": "车辆 15053114286 (190个数据点)"},
        {"vehicle_id": "15053114287", "data_points": 170, "description": "车辆 15053114287 (170个数据点)"},
        {"vehicle_id": "15053114288", "data_points": 130, "description": "车辆 15053114288 (130个数据点)"},
        {"vehicle_id": "15053114289", "data_points": 210, "description": "车辆 15053114289 (210个数据点)"},
        {"vehicle_id": "15053114290", "data_points": 155, "description": "车辆 15053114290 (155个数据点)"},
        {"vehicle_id": "15053114291", "data_points": 175, "description": "车辆 15053114291 (175个数据点)"},
        {"vehicle_id": "15053114292", "data_points": 165, "description": "车辆 15053114292 (165个数据点)"},
        {"vehicle_id": "15053114293", "data_points": 145, "description": "车辆 15053114293 (145个数据点)"},
        {"vehicle_id": "15053114294", "data_points": 185, "description": "车辆 15053114294 (185个数据点)"}
    ]

    # 返回指定数量的车辆
    selected_vehicles = static_vehicles[:limit]

    return {
        "success": True,
        "message": f"提供 {len(selected_vehicles)} 个示例车辆（静态列表，数字格式）",
        "vehicles": selected_vehicles,
        "time_range": f"{start_time} - {end_time}",
        "total_vehicles": len(static_vehicles),
        "data_source": "静态示例数据（后备模式，已修正为数字格式）"
    }


@router.get("/anomaly/detection", response_model=dict)
async def detect_anomalies(
        start_time: float = Query(..., description="开始时间戳（UTC）"),
        end_time: float = Query(..., description="结束时间戳（UTC）"),
        detection_types: str = Query("all",
                                     description="检测类型：all, long_stop, abnormal_route, speed_anomaly, cluster_anomaly"),
        threshold_params: Optional[str] = Query(None, description="阈值参数JSON字符串")
):
    """
    异常检测API - 检测各种类型的交通异常
    """
    try:
        # 记录异常检测请求
        logger.anomaly("异常检测", f"开始异常检测，时间范围: {start_time} - {end_time}",
                       source="API调用", user="用户",
                       details={"start_time": start_time, "end_time": end_time, "detection_types": detection_types})

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
            "speed_threshold_low": 5,  # 低速阈值 km/h
            "speed_threshold_high": 80,  # 高速阈值 km/h
            "detour_ratio": 1.5,  # 绕路比例
            "cluster_density": 50  # 聚集密度
        }
        thresholds = {**default_thresholds, **thresholds}

        # 加载数据
        df = data_processor.load_data(start_time, end_time)

        if df.empty:
            logger.warning("异常检测", "未找到符合条件的数据", source="API调用", user="用户")
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

@router.post("/road/analysis", response_model=RoadAnalysisResponse)
async def analyze_road_segments(
        start_time: float = Query(..., description="开始时间戳（UTC）"),
        end_time: float = Query(..., description="结束时间戳（UTC）"),
        request: RoadAnalysisRequest = Body(...)
):
    """
    路段分析API
    分析道路网络的通行状况、速度分布、拥堵情况等
    支持缓存系统，避免重复计算
    """
    import math
    import pandas as pd
    import os
    try:
        start_processing = time.time()

        # 获取缓存系统
        cache = get_traffic_cache()

        # 生成缓存键
        cache_key = cache.generate_cache_key(
            start_time=start_time,
            end_time=end_time,
            analysis_type=request.analysis_type,
            min_vehicles=getattr(request, 'min_vehicles', 10)
        )

        # 尝试从缓存加载结果
        logger.info("路段分析", f"检查缓存: {cache_key}")
        cached_result = cache.load_analysis_result(cache_key)

        if cached_result:
            logger.info("路段分析", "使用缓存的分析结果（秒级响应）")

            # 构造分析结果对象
            analysis = RoadNetworkAnalysis(
                analysis_type=cached_result.get("analysis_metadata", {}).get("analysis_type", request.analysis_type),
                time_range=cached_result.get("analysis_metadata", {}).get("time_range",
                                                                          {"start": start_time, "end": end_time}),
                total_segments=cached_result.get("total_segments", 0),
                segments_data=cached_result.get("segments_data", []),
                network_summary=cached_result.get("network_summary", {}),
                bottleneck_segments=cached_result.get("bottleneck_segments", [])
            )

            return RoadAnalysisResponse(
                success=True,
                message="从缓存加载分析结果",
                analysis=analysis,
                segments=cached_result.get("segments", []),  # 添加segments字段
                speed_distributions=cached_result.get("speed_distributions", []),
                flow_patterns=cached_result.get("flow_patterns", []),
                processing_time=time.time() - start_processing
            )

        # 缓存未命中，执行实时分析
        logger.info("路段分析", "缓存未命中，执行实时分析...")
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(start_time, end_time)

        if df.empty:
            return RoadAnalysisResponse(
                success=False,
                message="指定时间范围内没有交通数据",
                analysis=RoadNetworkAnalysis(
                    analysis_type=request.analysis_type,
                    time_range={"start": start_time, "end": end_time},
                    total_segments=0,
                    segments_data=[],
                    network_summary={},
                    bottleneck_segments=[]
                ),
                speed_distributions=[],
                flow_patterns=[],
                processing_time=0
            )

        # 执行路段分析
        analysis_result = data_processor.analyze_road_segments(
            df,
            analysis_type=request.analysis_type,
            min_vehicles=getattr(request, 'min_vehicles', 10)
        )

        if "error" in analysis_result:
            return RoadAnalysisResponse(
                success=False,
                message=analysis_result["error"],
                analysis=RoadNetworkAnalysis(
                    analysis_type=request.analysis_type,
                    time_range={"start": start_time, "end": end_time},
                    total_segments=0,
                    segments_data=[],
                    network_summary={},
                    bottleneck_segments=[]
                ),
                speed_distributions=[],
                flow_patterns=[],
                processing_time=time.time() - start_processing
            )

        # 保存分析结果到缓存
        metadata = {
            "start_time": start_time,
            "end_time": end_time,
            "analysis_type": request.analysis_type,
            "min_vehicles": getattr(request, 'min_vehicles', 10),
            "request_time": datetime.now().isoformat(),
            "data_records": len(df)
        }

        cache_saved = cache.save_analysis_result(cache_key, analysis_result, metadata)
        if cache_saved:
            logger.info("路段分析", f"分析结果已保存到缓存: {cache_key}")
        else:
            logger.warning("路段分析", "缓存保存失败")

        # 构造分析结果对象
        analysis = RoadNetworkAnalysis(
            analysis_type=request.analysis_type,
            time_range={"start": start_time, "end": end_time},
            total_segments=analysis_result.get("total_segments", 0),
            segments_data=analysis_result.get("segments_data", []),
            network_summary=analysis_result.get("network_summary", {}),
            bottleneck_segments=analysis_result.get("bottleneck_segments", [])
        )

        processing_time = time.time() - start_processing
        message = f"实时分析完成，耗时 {processing_time:.2f} 秒"
        if cache_saved:
            message += "，结果已缓存"

        # 新增：详细日志记录
        try:
            avg_speed = None
            avg_flow = None
            if analysis_result.get("segments_data"):
                speeds = [seg.get("avg_speed", 0) for seg in analysis_result["segments_data"] if
                          seg.get("avg_speed") is not None]
                flows = [seg.get("flow_rate", 0) for seg in analysis_result["segments_data"] if
                         seg.get("flow_rate") is not None]
                if speeds:
                    avg_speed = sum(speeds) / len(speeds)
                if flows:
                    avg_flow = sum(flows) / len(flows)
            logger.traffic(
                "路段分析",  # module
                f"分析完成: {message}",  # message
                source="API调用",
                user="用户",
                details={
                    "start_time": start_time,
                    "end_time": end_time,
                    "analysis_type": request.analysis_type,
                    "total_segments": analysis_result.get("total_segments", 0),
                    "bottleneck_count": len(analysis_result.get("bottleneck_segments", [])),
                    "avg_speed": avg_speed,
                    "avg_flow": avg_flow,
                    "processing_time": processing_time
                }
            )
        except Exception as log_err:
            logger.error("路段分析", f"日志记录失败: {log_err}")

        return RoadAnalysisResponse(
            success=True,
            message=message,
            analysis=analysis,
            segments=analysis_result.get("segments", []),  # 添加segments字段
            speed_distributions=analysis_result.get("speed_distributions", []),
            flow_patterns=analysis_result.get("flow_patterns", []),
            processing_time=processing_time
        )

    except Exception as e:
        logger.error("路段分析", f"路段分析时出错: {str(e)}")
        import traceback
        logger.error("路段分析", f"详细错误信息: {traceback.format_exc()}")

        return RoadAnalysisResponse(
            success=False,
            message=f"路段分析时出错: {str(e)}",
            analysis=RoadNetworkAnalysis(
                analysis_type=request.analysis_type,
                time_range={"start": start_time, "end": end_time},
                total_segments=0,
                segments_data=[],
                network_summary={},
                bottleneck_segments=[]
            ),
            speed_distributions=[],
            flow_patterns=[],
            processing_time=time.time() - start_processing
        )


@router.get("/road/segments", response_model=RoadSegmentResponse)
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


@router.post("/road/traffic", response_model=RoadTrafficResponse)
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


@router.post("/road/visualization", response_model=RoadVisualizationResponse)
async def get_road_visualization_data(
        start_time: float = Query(..., description="开始时间戳（UTC）"),
        end_time: float = Query(..., description="结束时间戳（UTC）"),
        request: Dict[str, Any] = Body(...)
):
    """
    路段可视化API
    生成路段可视化数据
    """
    import math
    import pandas as pd
    import os
    try:
        start_processing = time.time()
        # 只走实时分析逻辑
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(start_time, end_time)
        if df.empty:
            return RoadVisualizationResponse(
                success=False,
                message="指定时间范围内没有交通数据",
                visualization_data=[],
                segment_colors={},
                legend_info={}
            )
        # 执行路段分析，生成可视化数据
        analysis_result = data_processor.analyze_road_segments(
            df,
            analysis_type=getattr(request, 'analysis_type', 'comprehensive'),
            min_vehicles=getattr(request, 'min_vehicles', 10)
        )
        if "error" in analysis_result:
            return RoadVisualizationResponse(
                success=False,
                message=analysis_result["error"],
                visualization_data=[],
                segment_colors={},
                legend_info={}
            )
        visualization_data = analysis_result.get("segments", [])
        return RoadVisualizationResponse(
            success=True,
            message="实时分析完成",
            visualization_data=visualization_data,
            segment_colors=analysis_result.get("segment_colors", {}),
            legend_info=analysis_result.get("legend_info", {})
        )
    except Exception as e:
        logger.error(f"生成路段可视化数据时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return RoadVisualizationResponse(
            success=False,
            message=f"生成可视化数据时出错: {str(e)}",
            visualization_data=[],
            segment_colors={},
            legend_info={}
        )


@router.get("/road/metrics", response_model=Dict[str, Any])
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


# 智能客运监控相关API接口

@router.post("/smart-passenger/analysis", response_model=SmartPassengerResponse)
async def analyze_smart_passenger(request: SmartPassengerRequest):
    """
    智能客运分析API
    分析天气对客流的影响，载客出租车需求等
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
            logger.warning("智能乘客分析", "没有可用的交通数据", source="API调用", user="用户")
            return SmartPassengerResponse(
                success=False,
                message="没有可用的交通数据",
                analysis_type=request.analysis_type,
                statistics=None,
                processing_time=time.time() - start_time
            )

        # 初始化智能客运分析引擎
        from .smart_passenger_engine import SmartPassengerEngine
        smart_engine = SmartPassengerEngine()

        # 获取天气数据
        weather_data = []
        if request.include_weather:
            weather_data = smart_engine.get_weather_data(start_timestamp, end_timestamp)

        # 识别载客车辆和客流数据
        passenger_flows = smart_engine.identify_passenger_vehicles(df)

        # 分析出租车需求
        taxi_demand_data = []
        if request.include_taxi_analysis:
            taxi_demand_data = smart_engine.analyze_taxi_demand(df, request.time_resolution)

        # 分析天气影响
        weather_impact = []
        if request.weather_correlation and weather_data:
            weather_impact = smart_engine.analyze_weather_impact(passenger_flows, weather_data)

        # 计算出租车供需
        taxi_supply_demand = []
        if taxi_demand_data:
            taxi_supply_demand = smart_engine.calculate_taxi_supply_demand(taxi_demand_data)

        # 生成统计数据
        statistics = smart_engine.generate_smart_passenger_statistics(
            passenger_flows, weather_data, taxi_demand_data, weather_impact,
            (start_timestamp, end_timestamp)
        )

        return SmartPassengerResponse(
            success=True,
            message=f"智能客运监控分析完成，分析了 {len(passenger_flows)} 条客流数据",
            analysis_type=request.analysis_type,
            statistics=statistics,
            weather_impact=weather_impact if weather_impact else None,
            taxi_demand=taxi_supply_demand if taxi_supply_demand else None,
            processing_time=time.time() - start_time
        )

    except Exception as e:
        logger.error(f"智能客运监控分析失败: {str(e)}")
        return SmartPassengerResponse(
            success=False,
            message=f"分析失败: {str(e)}",
            analysis_type=request.analysis_type,
            statistics=None,
            processing_time=time.time() - start_time if 'start_time' in locals() else 0
        )


@router.post("/smart-passenger/weather-impact", response_model=WeatherImpactResponse)
async def analyze_weather_impact(request: WeatherImpactRequest):
    """
    天气影响分析API
    专门分析天气变化对客流量的影响
    """
    try:
        # 获取时间范围
        current_time = time.time()
        # 优先使用请求中的时间范围，如果没有则使用默认值
        if request.start_time and request.end_time:
            start_timestamp = request.start_time
            end_timestamp = request.end_time
        else:
            # 默认使用2013年9月12-18日的数据范围
            start_timestamp = 1378944000  # 2013-09-12 00:00:00 UTC
            end_timestamp = 1379548800  # 2013-09-18 23:59:59 UTC

        # 加载数据
        data_processor = TrafficDataProcessor()
        logger.info(f"开始加载交通数据，时间范围: {start_timestamp} - {end_timestamp}")
        df = data_processor.load_data(start_timestamp, end_timestamp)
        logger.info(f"交通数据加载完成，共 {len(df)} 条记录")

        if df.empty:
            logger.warning("没有找到交通数据")
            return WeatherImpactResponse(
                success=False,
                message="没有可用的交通数据",
                weather_impact_analysis=[],
                correlation_matrix={},
                weather_stats={}
            )

        # 初始化智能客运分析引擎
        from .smart_passenger_engine import SmartPassengerEngine
        smart_engine = SmartPassengerEngine()

        # 获取天气数据
        weather_data = smart_engine.get_weather_data(start_timestamp, end_timestamp)

        # 识别客流数据
        passenger_flows = smart_engine.identify_passenger_vehicles(df)

        # 分析天气影响
        weather_impact_analysis = smart_engine.analyze_weather_impact(passenger_flows, weather_data)

        # 计算相关性矩阵
        correlation_matrix = {}
        for impact in weather_impact_analysis:
            correlation_matrix[impact.weather_condition] = impact.correlation_coefficient

        # 生成天气统计
        weather_stats = {
            "total_weather_records": len(weather_data),
            "weather_type_distribution": {},
            "avg_temperature": np.mean([w.temperature for w in weather_data]) if weather_data else 0,
            "avg_precipitation": np.mean([w.precipitation for w in weather_data]) if weather_data else 0
        }

        # 统计天气类型分布
        for weather in weather_data:
            weather_type = weather.weather_type
            weather_stats["weather_type_distribution"][weather_type] = \
                weather_stats["weather_type_distribution"].get(weather_type, 0) + 1

        return WeatherImpactResponse(
            success=True,
            message=f"天气影响分析完成，分析了 {len(weather_data)} 条天气数据",
            weather_impact_analysis=weather_impact_analysis,
            correlation_matrix=correlation_matrix,
            weather_stats=weather_stats,
            prediction_data=None  # 暂不实现预测功能
        )

    except Exception as e:
        logger.error(f"天气影响分析失败: {str(e)}")
        return WeatherImpactResponse(
            success=False,
            message=f"分析失败: {str(e)}",
            weather_impact_analysis=[],
            correlation_matrix={},
            weather_stats={}
        )


# 已删除旧的出租车需求分析API，因为使用了估算逻辑
# 新的载客车辆时间线API使用真实的载客车辆数据

@router.post("/smart-passenger/visualization", response_model=PassengerVisualizationResponse)
async def get_passenger_visualization_data(request: Dict[str, Any]):
    """
    客运可视化数据API
    生成客流热力图、天气关联图表、出租车需求地图等可视化数据
    """
    try:
        visualization_type = request.get("visualization_type", "comprehensive")
        time_range = request.get("time_range", {})

        start_timestamp = time_range.get("start", time.time() - 3600)
        end_timestamp = time_range.get("end", time.time())

        # 加载数据
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(start_timestamp, end_timestamp)

        if df.empty:
            return PassengerVisualizationResponse(
                success=False,
                message="没有可用的数据进行可视化",
                passenger_heatmap={},
                weather_correlation_chart={},
                taxi_demand_map={},
                time_series_data={}
            )

        # 初始化智能客运分析引擎
        from .smart_passenger_engine import SmartPassengerEngine
        smart_engine = SmartPassengerEngine()

        # 获取基础数据
        weather_data = smart_engine.get_weather_data(start_timestamp, end_timestamp)
        passenger_flows = smart_engine.identify_passenger_vehicles(df)
        taxi_demand_data = smart_engine.analyze_taxi_demand(df)

        # 生成客流热力图数据
        passenger_heatmap = {
            "heatmap_points": [
                {
                    "lat": pf.location["lat"],
                    "lng": pf.location["lng"],
                    "intensity": pf.passenger_count,
                    "type": "pickup" if pf.is_pickup else "dropoff"
                }
                for pf in passenger_flows
            ],
            "legend": {
                "pickup": "上客点",
                "dropoff": "下客点"
            }
        }

        # 生成天气关联图表数据
        weather_correlation_chart = {
            "weather_passenger_correlation": [],
            "time_series": []
        }

        if weather_data and passenger_flows:
            weather_impact = smart_engine.analyze_weather_impact(passenger_flows, weather_data)
            for impact in weather_impact:
                weather_correlation_chart["weather_passenger_correlation"].append({
                    "weather_type": impact.weather_condition,
                    "impact_percentage": impact.impact_percentage,
                    "correlation": impact.correlation_coefficient
                })

        # 生成出租车需求地图数据
        taxi_demand_map = {
            "demand_zones": [
                {
                    "lat": td.location["lat"],
                    "lng": td.location["lng"],
                    "loaded_taxis": td.loaded_taxis,
                    "demand_index": td.demand_index,
                    "supply_ratio": td.supply_ratio
                }
                for td in taxi_demand_data
            ],
            "supply_demand_legend": {
                "high_demand": {"color": "#ff4444", "threshold": 0.7},
                "medium_demand": {"color": "#ffaa44", "threshold": 0.4},
                "low_demand": {"color": "#44ff44", "threshold": 0.0}
            }
        }

        # 生成时间序列数据
        time_series_data = {
            "passenger_flow_trend": [],
            "weather_trend": [],
            "taxi_demand_trend": []
        }

        # 按小时聚合时间序列
        hourly_passenger = defaultdict(int)
        hourly_weather = defaultdict(list)
        hourly_taxi = defaultdict(list)

        for pf in passenger_flows:
            hour = datetime.fromtimestamp(pf.timestamp).strftime("%Y-%m-%d %H:00")
            hourly_passenger[hour] += pf.passenger_count

        for w in weather_data:
            hour = datetime.fromtimestamp(w.timestamp).strftime("%Y-%m-%d %H:00")
            hourly_weather[hour].append(w)

        for td in taxi_demand_data:
            hour = datetime.fromtimestamp(td.timestamp).strftime("%Y-%m-%d %H:00")
            hourly_taxi[hour].append(td)

        for hour in sorted(set(list(hourly_passenger.keys()) + list(hourly_weather.keys()))):
            time_series_data["passenger_flow_trend"].append({
                "time": hour,
                "passenger_count": hourly_passenger.get(hour, 0)
            })

            if hour in hourly_weather:
                avg_temp = np.mean([w.temperature for w in hourly_weather[hour]])
                avg_precip = np.mean([w.precipitation for w in hourly_weather[hour]])
                time_series_data["weather_trend"].append({
                    "time": hour,
                    "temperature": avg_temp,
                    "precipitation": avg_precip
                })

            if hour in hourly_taxi:
                avg_demand = np.mean([td.demand_index for td in hourly_taxi[hour]])
                total_loaded = sum(td.loaded_taxis for td in hourly_taxi[hour])
                time_series_data["taxi_demand_trend"].append({
                    "time": hour,
                    "demand_index": avg_demand,
                    "loaded_taxis": total_loaded
                })

        return PassengerVisualizationResponse(
            success=True,
            message=f"成功生成可视化数据，包含 {len(passenger_flows)} 个客流点",
            passenger_heatmap=passenger_heatmap,
            weather_correlation_chart=weather_correlation_chart,
            taxi_demand_map=taxi_demand_map,
            time_series_data=time_series_data
        )

    except Exception as e:
        logger.error(f"客运可视化数据生成失败: {str(e)}")
        return PassengerVisualizationResponse(
            success=False,
            message=f"生成可视化数据失败: {str(e)}",
            passenger_heatmap={},
            weather_correlation_chart={},
            taxi_demand_map={},
            time_series_data={}
        )


@router.get("/smart-passenger/historical", response_model=Dict[str, Any])
async def get_historical_passenger_analysis():
    """
    历史客运分析API
    获取历史时段的客流和载客车辆状态
    """
    try:
        # 使用2013年9月12-18日的数据范围
        start_timestamp = 1378944000  # 2013-09-12 00:00:00 UTC
        end_timestamp = 1379548800  # 2013-09-18 23:59:59 UTC
        current_time = time.time()  # 当前时间用于状态计算

        # 加载历史数据
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(start_timestamp, end_timestamp)

        if df.empty:
            return {
                "success": False,
                "message": "没有历史数据",
                "historical_data": {}
            }

        # 初始化智能客运分析引擎
        from .smart_passenger_engine import SmartPassengerEngine
        smart_engine = SmartPassengerEngine()

        # 获取历史数据
        passenger_flows = smart_engine.identify_passenger_vehicles(df)
        taxi_demand_data = smart_engine.analyze_taxi_demand(df, 5)  # 5分钟分辨率

        # 计算历史指标
        historical_data = {
            "current_timestamp": current_time,
            "time_window": "15min",
            "passenger_stats": {
                "active_passengers": sum(pf.passenger_count for pf in passenger_flows),
                "pickup_points": len([pf for pf in passenger_flows if pf.is_pickup]),
                "dropoff_points": len([pf for pf in passenger_flows if not pf.is_pickup])
            },
            "taxi_stats": {
                "loaded_taxis": sum(td.loaded_taxis for td in taxi_demand_data),
                "empty_taxis": sum(td.empty_taxis for td in taxi_demand_data),
                "total_demand": sum(td.total_orders for td in taxi_demand_data),
                "avg_demand_index": np.mean([td.demand_index for td in taxi_demand_data]) if taxi_demand_data else 0
            },
            "status_indicators": {
                "demand_level": "normal",
                "supply_status": "adequate",
                "traffic_flow": "smooth"
            }
        }

        # 判断状态指标
        if historical_data["taxi_stats"]["avg_demand_index"] > 0.7:
            historical_data["status_indicators"]["demand_level"] = "high"
        elif historical_data["taxi_stats"]["avg_demand_index"] < 0.3:
            historical_data["status_indicators"]["demand_level"] = "low"

        supply_ratio = (historical_data["taxi_stats"]["loaded_taxis"] /
                        max(historical_data["taxi_stats"]["total_demand"], 1))
        if supply_ratio < 0.5:
            historical_data["status_indicators"]["supply_status"] = "shortage"
        elif supply_ratio > 1.5:
            historical_data["status_indicators"]["supply_status"] = "surplus"

        return {
            "success": True,
            "message": "历史分析数据获取成功",
            "historical_data": historical_data
        }

    except Exception as e:
        logger.error(f"历史客运分析失败: {str(e)}")
        return {
            "success": False,
            "message": f"历史分析失败: {str(e)}",
            "historical_data": {}
        }


# ===== 路程分析和订单速度分析API接口 =====

@router.post("/road/trip-analysis", response_model=TripAnalysisResponse)
async def analyze_trip_distance_classification(
        start_time: float = Query(..., description="开始时间戳（UTC）"),
        end_time: float = Query(..., description="结束时间戳（UTC）"),
        request: TripAnalysisRequest = None
):
    """
    路程分析功能
    规定以小于4千米为短途，4千米至8千米为中途，大于8千米为长途
    查看每天三种距离运输的占比，完成路程分析的可视化展示
    """
    try:
        start_processing = time.time()

        # 默认请求参数
        if request is None:
            request = TripAnalysisRequest()

        # 根据选择的日期调整时间范围
        if request.selected_date and request.selected_date != 'all':
            # 将日期字符串转换为时间戳
            from datetime import datetime
            date_obj = datetime.strptime(request.selected_date, '%Y-%m-%d')
            # 设置为该日期的开始和结束时间（UTC）
            day_start = int(date_obj.timestamp())
            day_end = day_start + 86400 - 1  # 86400秒 = 24小时

            actual_start_time = day_start
            actual_end_time = day_end
        else:
            actual_start_time = start_time
            actual_end_time = end_time

        # 加载数据
        df = data_processor.load_data(actual_start_time, actual_end_time)

        if df.empty:
            return TripAnalysisResponse(
                success=False,
                message="未找到符合条件的数据",
                analysis_result=TripAnalysisStatistics(
                    time_range={"start": actual_start_time, "end": actual_end_time},
                    daily_classifications=[],
                    overall_stats={},
                    trend_analysis={}
                ),
                visualization_data={}
            )

        # 创建路段分析引擎
        from .road_analysis_engine import RoadAnalysisEngine
        road_engine = RoadAnalysisEngine()

        # 标准化数据列名并调试
        if 'COMMADDR' in df.columns:
            df['vehicle_id'] = df['COMMADDR']
        if 'UTC' in df.columns:
            df['timestamp'] = df['UTC']
        if 'LAT' in df.columns and 'LON' in df.columns:
            df['latitude'] = df['LAT'] / 1e5
            df['longitude'] = df['LON'] / 1e5

        # 进行路程分析
        analysis_result = road_engine.analyze_trip_distance_classification(df)

        # 生成可视化数据
        visualization_data = {
            "daily_chart": {
                "type": "stacked_bar",
                "title": "每日路程分类统计",
                "data": [
                    {
                        "date": daily.date,
                        "short_trips": daily.short_trips,
                        "medium_trips": daily.medium_trips,
                        "long_trips": daily.long_trips,
                        "short_percentage": daily.short_percentage,
                        "medium_percentage": daily.medium_percentage,
                        "long_percentage": daily.long_percentage
                    }
                    for daily in analysis_result.daily_classifications
                ]
            },
            "pie_chart": {
                "type": "pie",
                "title": "总体路程分类占比",
                "data": [
                    {
                        "name": "短途 (<4km)",
                        "value": analysis_result.overall_stats.get("overall_short_percentage", 0),
                        "count": analysis_result.overall_stats.get("short_trips_total", 0)
                    },
                    {
                        "name": "中途 (4-8km)",
                        "value": analysis_result.overall_stats.get("overall_medium_percentage", 0),
                        "count": analysis_result.overall_stats.get("medium_trips_total", 0)
                    },
                    {
                        "name": "长途 (>8km)",
                        "value": analysis_result.overall_stats.get("overall_long_percentage", 0),
                        "count": analysis_result.overall_stats.get("long_trips_total", 0)
                    }
                ]
            },
            "trend_chart": {
                "type": "line",
                "title": "路程分类趋势分析",
                "data": {
                    "short_trip_trend": analysis_result.trend_analysis.get("short_trip_trend", "stable"),
                    "medium_trip_trend": analysis_result.trend_analysis.get("medium_trip_trend", "stable"),
                    "long_trip_trend": analysis_result.trend_analysis.get("long_trip_trend", "stable"),
                    "dominant_category": analysis_result.trend_analysis.get("most_common_distance_category", "unknown")
                }
            },
            "statistics_summary": {
                "total_trips": analysis_result.overall_stats.get("total_trips", 0),
                "avg_daily_trips": analysis_result.overall_stats.get("avg_daily_trips", 0),
                "overall_avg_distance": analysis_result.overall_stats.get("overall_avg_distance", 0),
                "analysis_days": len(analysis_result.daily_classifications)
            }
        }

        processing_time = time.time() - start_processing

        logger.info("路程分析", f"路程分析完成，处理时间: {processing_time:.2f}秒", source="API调用", user="用户")

        return TripAnalysisResponse(
            success=True,
            message=f"路程分析完成，共分析了 {analysis_result.overall_stats.get('total_trips', 0)} 个订单",
            analysis_result=analysis_result,
            visualization_data=visualization_data,
            processing_time=processing_time
        )

    except Exception as e:
        logger.error("路程分析", f"路程分析失败: {str(e)}", source="API调用", user="用户")
        logger.error("路程分析", f"错误详情: {traceback.format_exc()}", source="API调用", user="用户")

        return TripAnalysisResponse(
            success=False,
            message=f"路程分析失败: {str(e)}",
            analysis_result=TripAnalysisStatistics(
                time_range={"start": actual_start_time if 'actual_start_time' in locals() else start_time,
                            "end": actual_end_time if 'actual_end_time' in locals() else end_time},
                daily_classifications=[],
                overall_stats={"error": str(e)},
                trend_analysis={}
            ),
            visualization_data={}
        )


@router.post("/road/order-speed-analysis", response_model=OrderSpeedAnalysisResponse)
async def analyze_order_based_road_speed(
        start_time: float = Query(..., description="开始时间戳（UTC）"),
        end_time: float = Query(..., description="结束时间戳（UTC）"),
        request: OrderSpeedAnalysisRequest = None
):
    """
    基于订单的道路速度分析
    利用中短途订单数据中的预估距离与起止时间，计算订单的平均速度
    大数据背景下，大量订单的平均速度可以实时反映道路的拥堵状况
    完成道路速度的可视化展示
    """
    try:
        start_processing = time.time()

        # 默认请求参数
        if request is None:
            request = OrderSpeedAnalysisRequest()

        # 加载数据
        df = data_processor.load_data(start_time, end_time)

        if df.empty:
            return OrderSpeedAnalysisResponse(
                success=False,
                message="未找到符合条件的数据",
                speed_analysis=RoadSpeedAnalysisResult(
                    time_range={"start": start_time, "end": end_time},
                    speed_data=[],
                    heatmap_data=[],
                    congestion_summary={},
                    road_speed_trends=[]
                ),
                visualization_data={}
            )

        # 创建路段分析引擎
        from .road_analysis_engine import RoadAnalysisEngine
        road_engine = RoadAnalysisEngine()

        # 标准化数据列名
        if 'COMMADDR' in df.columns:
            df['vehicle_id'] = df['COMMADDR']
        if 'UTC' in df.columns:
            df['timestamp'] = df['UTC']
        if 'LAT' in df.columns and 'LON' in df.columns:
            df['latitude'] = df['LAT'] / 1e5
            df['longitude'] = df['LON'] / 1e5

        # 进行订单速度分析
        speed_analysis = road_engine.analyze_order_based_road_speed(
            df,
            include_short_medium_only=request.include_short_medium_only,
            spatial_resolution=request.spatial_resolution,
            min_orders_per_location=request.min_orders_per_location,
            congestion_threshold=request.congestion_threshold
        )

        # 生成可视化数据
        visualization_data = {
            "speed_heatmap": {
                "type": "heatmap",
                "title": "道路速度热力图",
                "data": [
                    {
                        "lat": heatmap.lat,
                        "lng": heatmap.lng,
                        "speed": heatmap.speed,
                        "intensity": heatmap.intensity,
                        "order_count": heatmap.order_count,
                        "congestion_level": heatmap.congestion_level
                    }
                    for heatmap in speed_analysis.heatmap_data
                ]
            },
            "congestion_distribution": {
                "type": "pie",
                "title": "拥堵等级分布",
                "data": [
                    {
                        "name": f"{level} (拥堵等级)",
                        "value": info["percentage"],
                        "count": info["count"]
                    }
                    for level, info in speed_analysis.congestion_summary.get("congestion_distribution", {}).items()
                ]
            },
            "speed_trends": {
                "type": "line",
                "title": "24小时道路速度趋势",
                "data": [
                    {
                        "hour": trend["hour"],
                        "avg_speed": trend["avg_speed"],
                        "order_count": trend["order_count"],
                        "is_peak_hour": trend["is_peak_hour"],
                        "speed_category": trend["speed_category"]
                    }
                    for trend in speed_analysis.road_speed_trends
                ]
            },
            "speed_statistics": {
                "overall_avg_speed": speed_analysis.congestion_summary.get("overall_avg_speed", 0),
                "total_analysis_locations": speed_analysis.congestion_summary.get("total_analysis_locations", 0),
                "high_confidence_locations": speed_analysis.congestion_summary.get("high_confidence_locations", 0),
                "total_orders_analyzed": speed_analysis.congestion_summary.get("total_orders_analyzed", 0),
                "speed_range": {
                    "min": speed_analysis.congestion_summary.get("speed_statistics", {}).get("min_speed", 0),
                    "max": speed_analysis.congestion_summary.get("speed_statistics", {}).get("max_speed", 0),
                    "median": speed_analysis.congestion_summary.get("speed_statistics", {}).get("median_speed", 0)
                }
            },
            "congestion_zones": {
                "type": "scatter",
                "title": "拥堵区域分布",
                "data": [
                    {
                        "lat": data.location["lat"],
                        "lng": data.location["lng"],
                        "speed": data.avg_speed,
                        "congestion_level": data.congestion_level,
                        "order_count": data.order_count,
                        "confidence": data.confidence_score
                    }
                    for data in speed_analysis.speed_data
                    if data.congestion_level in ["heavy", "jam"]  # 只显示拥堵区域
                ]
            }
        }

        processing_time = time.time() - start_processing

        logger.info(f"订单速度分析完成，处理时间: {processing_time:.2f}秒")

        return OrderSpeedAnalysisResponse(
            success=True,
            message=f"订单速度分析完成，分析了 {len(speed_analysis.speed_data)} 个位置的速度数据",
            speed_analysis=speed_analysis,
            visualization_data=visualization_data,
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"订单速度分析失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")

        return OrderSpeedAnalysisResponse(
            success=False,
            message=f"订单速度分析失败: {str(e)}",
            speed_analysis=RoadSpeedAnalysisResult(
                time_range={"start": start_time, "end": end_time},
                speed_data=[],
                heatmap_data=[],
                congestion_summary={"error": str(e)},
                road_speed_trends=[]
            ),
            visualization_data={}
        )


class DailyWeatherImpactRequest(BaseModel):
    start_time: float
    end_time: float


class HourlyWeatherImpactResponse(BaseModel):
    hour: int
    weather_condition: str
    temperature: float
    humidity: float
    precipitation: float
    loaded_vehicles: int
    total_vehicles: int
    impact_factor: float
    impact_description: str


class DailyWeatherImpactResponseItem(BaseModel):
    date: str
    hourly_impacts: List[HourlyWeatherImpactResponse]
    daily_summary: Dict[str, Any]


class DailyWeatherImpactResponse(BaseModel):
    success: bool
    message: str
    daily_impacts: List[DailyWeatherImpactResponseItem]


@router.post("/smart-passenger/daily-weather-impact", response_model=DailyWeatherImpactResponse)
async def analyze_daily_weather_impact(request: DailyWeatherImpactRequest):
    """分析每天每小时的天气影响"""
    try:
        # 加载数据
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(request.start_time, request.end_time)
        if df.empty:
            return DailyWeatherImpactResponse(success=False, message="没有可用的交通数据", daily_impacts=[])
        # 获取天气数据
        from .smart_passenger_engine import SmartPassengerEngine
        smart_engine = SmartPassengerEngine()
        weather_data = smart_engine.get_weather_data(request.start_time, request.end_time)
        # 调用分析方法
        daily_impacts = smart_engine.analyze_daily_weather_impact(df, weather_data)
        # 转换为响应结构
        response_items = []
        for d in daily_impacts:
            response_items.append(DailyWeatherImpactResponseItem(
                date=d.date,
                hourly_impacts=[HourlyWeatherImpactResponse(**h.dict()) for h in d.hourly_impacts],
                daily_summary=d.daily_summary
            ))
        return DailyWeatherImpactResponse(success=True, message="分析成功", daily_impacts=response_items)
    except Exception as e:
        return DailyWeatherImpactResponse(success=False, message=f"分析失败: {str(e)}", daily_impacts=[])


@router.get("/road/test-visualization")
async def test_road_visualization():
    """测试路段可视化数据生成"""
    try:
        logger.info("测试路段可视化数据...")

        # 使用固定的测试数据
        test_segments = [
            {
                "segment_id": "test_001",
                "start_point": {"lat": 36.651, "lng": 117.129},
                "end_point": {"lat": 36.655, "lng": 117.135},
                "road_name": "测试路段1",
                "road_type": "urban",
                "avg_speed": 35.5,
                "congestion_level": "moderate"
            }
        ]

        logger.info(f"返回 {len(test_segments)} 条测试路段数据")
        return {
            "success": True,
            "visualization_data": test_segments,
            "message": "测试数据生成成功"
        }

    except Exception as e:
        logger.error(f"测试路段可视化数据时出错: {str(e)}")
        return {
            "success": False,
            "message": f"测试失败: {str(e)}",
            "visualization_data": []
        }


# 缓存管理相关API接口

@router.get("/cache/statistics")
async def get_cache_statistics():
    """获取缓存系统统计信息"""
    try:
        cache = get_traffic_cache()
        stats = cache.get_cache_statistics()

        return {
            "success": True,
            "message": "缓存统计信息获取成功",
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"获取缓存统计时出错: {str(e)}")
        return {
            "success": False,
            "message": f"获取缓存统计失败: {str(e)}",
            "statistics": {}
        }


@router.get("/cache/list")
async def get_cached_analyses():
    """获取所有缓存的分析结果列表"""
    try:
        cache = get_traffic_cache()
        cached_list = cache.get_cached_analysis_list()

        return {
            "success": True,
            "message": f"找到 {len(cached_list)} 个缓存的分析结果",
            "cached_analyses": cached_list
        }

    except Exception as e:
        logger.error(f"获取缓存列表时出错: {str(e)}")
        return {
            "success": False,
            "message": f"获取缓存列表失败: {str(e)}",
            "cached_analyses": []
        }


@router.get("/cache/report/{cache_key}")
async def get_cache_report(cache_key: str):
    """获取指定缓存的可读性报告"""
    try:
        cache = get_traffic_cache()
        report = cache.get_cache_report(cache_key)

        if report:
            return {
                "success": True,
                "message": "缓存报告获取成功",
                "report": report
            }
        else:
            return {
                "success": False,
                "message": "缓存报告不存在或已过期",
                "report": None
            }

    except Exception as e:
        logger.error(f"获取缓存报告时出错: {str(e)}")
        return {
            "success": False,
            "message": f"获取缓存报告失败: {str(e)}",
            "report": None
        }


@router.delete("/cache/{cache_key}")
async def delete_cache_by_key(cache_key: str):
    """删除指定的缓存"""
    try:
        cache = get_traffic_cache()
        deleted = cache.delete_cache(cache_key)

        if deleted:
            return {
                "success": True,
                "message": f"缓存 {cache_key} 删除成功"
            }
        else:
            return {
                "success": False,
                "message": f"缓存 {cache_key} 不存在或删除失败"
            }

    except Exception as e:
        logger.error(f"删除缓存时出错: {str(e)}")
        return {
            "success": False,
            "message": f"删除缓存失败: {str(e)}"
        }


@router.post("/cache/clear")
async def clear_all_cache():
    """清理所有过期缓存"""
    try:
        cache = get_traffic_cache()
        # 触发缓存清理
        cache._cleanup_expired_cache()

        # 获取清理后的统计信息
        stats = cache.get_cache_statistics()

        return {
            "success": True,
            "message": "过期缓存清理完成",
            "statistics_after_cleanup": stats
        }

    except Exception as e:
        logger.error(f"清理缓存时出错: {str(e)}")
        return {
            "success": False,
            "message": f"清理缓存失败: {str(e)}"
        }


# 导入日志路由
from .log import router as log_router

# 注册日志路由
router.include_router(log_router, tags=["交通日志"])


@lru_cache(maxsize=128)
def get_preaggregated_data(date: str, time_resolution: int) -> Optional[Dict[str, Any]]:
    """
    从预聚合数据文件读取数据（带缓存）

    Args:
        date: 日期字符串 (YYYY-MM-DD)
        time_resolution: 时间分辨率 (分钟)

    Returns:
        预聚合数据字典或None
    """
    try:
        # 构建文件路径
        base_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'data', 'preaggregated'
        )
        resolution_dir = f"{time_resolution}min"
        json_filename = f"{date}_{time_resolution}min.json"
        filepath = os.path.join(base_dir, resolution_dir, json_filename)

        if not os.path.exists(filepath):
            return None

        # 读取JSON文件
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    except Exception as e:
        print(f"读取预聚合数据失败: {e}")
        return None


@router.get("/smart-passenger/loaded-vehicles-timeline")
async def get_loaded_vehicles_timeline(
        date: str = Query(..., description="日期 YYYY-MM-DD"),
        time_resolution: int = Query(15, description="时间分辨率(分钟)")
):
    """
    获取指定日期的载客车辆时间线数据（使用预聚合数据）
    展示真实的载客车辆数量变化，而不是估算的订单数量
    """
    try:
        logger.info("载客车辆分析", f"开始获取 {date} 的载客车辆时间线（预聚合）", source="API调用", user="系统")

        # 验证时间分辨率
        if time_resolution not in [15, 30, 60]:
            return {
                "success": False,
                "message": "时间分辨率必须是 15、30 或 60 分钟",
                "data": []
            }

        # 尝试从预聚合数据读取
        preaggregated_data = get_preaggregated_data(date, time_resolution)

        if preaggregated_data:
            print(f"⚡ 使用预聚合数据: {date} - {time_resolution}分钟")
            logger.info("载客车辆分析", f"使用预聚合数据，共 {len(preaggregated_data['data'])} 个时间段",
                        source="API调用", user="系统")

            return {
                "success": True,
                "message": f"成功获取 {date} 的载客车辆时间线数据（预聚合）",
                "date": date,
                "time_resolution": time_resolution,
                "data": preaggregated_data['data'],
                "summary": preaggregated_data['summary'],
                "source": "preaggregated"
            }

        # 如果预聚合数据不存在，回退到实时计算（但会警告）
        print(f"⚠️ 预聚合数据不存在，回退到实时计算: {date} - {time_resolution}分钟")
        logger.warning("载客车辆分析", f"预聚合数据不存在，使用实时计算", source="API调用", user="系统")

        # 解析日期，转换为时间戳
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            start_timestamp = int(date_obj.timestamp())
            end_timestamp = start_timestamp + 24 * 3600  # 24小时
        except ValueError:
            return {
                "success": False,
                "message": "日期格式错误，请使用 YYYY-MM-DD 格式",
                "data": []
            }

        # 加载数据
        data_processor = TrafficDataProcessor()
        df = data_processor.load_data(start_timestamp, end_timestamp)

        if df.empty:
            return {
                "success": False,
                "message": f"没有找到 {date} 的数据",
                "data": []
            }

        # 大幅减少数据量以提高性能，确保API在10秒内响应
        if len(df) > 2000:
            print(f"数据量过大({len(df)}条)，大幅采样到2000条以确保性能")
            df = df.sample(n=2000, random_state=42)

        # 标准化列名
        column_mapping = {
            'COMMADDR': 'vehicle_id',
            'UTC': 'timestamp',
            'lat': 'latitude',
            'lon': 'longitude',
            'SPEED': 'speed',
            'TFLAG': 'tflag',
            'is_occupied': 'is_occupied'
        }

        # 只重命名存在的列，避免重复
        existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_columns)

        # 检查并删除重复列名
        duplicate_columns = df.columns[df.columns.duplicated()].tolist()
        if duplicate_columns:
            df = df.loc[:, ~df.columns.duplicated()]

        # 确保必要的列存在
        required_columns = ['vehicle_id', 'timestamp', 'latitude', 'longitude']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {
                "success": False,
                "message": f"数据缺少必要的列: {missing_columns}",
                "data": []
            }

        # 确保timestamp列是数值类型
        df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])

        # 确保vehicle_id列是字符串类型
        df['vehicle_id'] = df['vehicle_id'].astype(str)

        # 验证时间戳范围
        if df.empty:
            return {
                "success": False,
                "message": f"时间戳转换后没有有效数据",
                "data": []
            }

        # 优化：预先计算载客状态
        if 'is_occupied' in df.columns:
            df['is_loaded'] = df['is_occupied']
        elif 'tflag' in df.columns:
            df['is_loaded'] = df['tflag'] == 268435456
        else:
            df['is_loaded'] = True  # 如果没有载客状态字段，假设所有车辆都载客

        # 按时间窗口统计载客车辆（高性能版本）
        timeline_data = []
        current_time = start_timestamp

        # 大幅减少时间窗口数量以提高性能
        max_windows = 48  # 最多48个时间窗口（24小时 * 2个窗口/小时）
        window_count = 0

        # 预计算时间窗口边界
        time_windows = []
        while current_time < end_timestamp and window_count < max_windows:
            window_end = current_time + (time_resolution * 60)
            time_windows.append((current_time, window_end))
            current_time = window_end
            window_count += 1

        # 批量处理时间窗口
        for start_win, end_win in time_windows:
            # 过滤当前时间窗口的数据
            mask = (df['timestamp'] >= start_win) & (df['timestamp'] < end_win)
            window_data = df[mask]

            if not window_data.empty:
                # 快速统计载客车辆数量
                loaded_vehicles = window_data[window_data['is_loaded'] == True]['vehicle_id'].nunique()
                total_vehicles = window_data['vehicle_id'].nunique()

                # 计算载客率
                occupancy_rate = (loaded_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0

                # 大幅限制位置点数量以提高性能
                loaded_positions = window_data[window_data['is_loaded'] == True][['latitude', 'longitude']].head(
                    20).to_dict('records')

                timeline_data.append({
                    "timestamp": start_win,
                    "time_label": datetime.fromtimestamp(start_win).strftime("%H:%M"),
                    "loaded_vehicles": loaded_vehicles,
                    "total_vehicles": total_vehicles,
                    "occupancy_rate": round(occupancy_rate, 2),
                    "vehicle_positions": loaded_positions
                })

        logger.info("载客车辆分析", f"完成 {date} 的载客车辆分析，共 {len(timeline_data)} 个时间段", source="API调用",
                    user="系统")

        return {
            "success": True,
            "message": f"成功获取 {date} 的载客车辆时间线数据（实时计算）",
            "date": date,
            "time_resolution": time_resolution,
            "data": timeline_data,
            "summary": {
                "total_time_windows": len(timeline_data),
                "max_loaded_vehicles": max([d['loaded_vehicles'] for d in timeline_data]) if timeline_data else 0,
                "avg_occupancy_rate": round(sum([d['occupancy_rate'] for d in timeline_data]) / len(timeline_data),
                                            2) if timeline_data else 0
            },
            "source": "realtime"
        }

    except Exception as e:
        logger.error("载客车辆分析", f"载客车辆时间线分析失败: {str(e)}", source="API调用", user="系统")
        return {
            "success": False,
            "message": f"分析失败: {str(e)}",
            "data": []
        }

class DailyTrafficResponse(BaseModel):
    success: bool
    message: str
    data: List[int]  # 24小时的车辆数数组

class WeeklyTrafficResponse(BaseModel):
    success: bool
    message: str
    data: List[Dict[str, Union[str, int]]]  # 按天的日期和车辆总数

class KeyMetric(BaseModel):
    title: str
    value: str
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
    congestionRate: float
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

# --- 辅助函数 ---
def load_spatial_grid():
    grid_file = Path(os.path.join(os.path.dirname(__file__), 'data', 'indexes', 'spatial_grid_0.001.json'))
    if grid_file.exists():
        with open(grid_file, 'r') as f:
            return json.load(f)
    # 默认网格（示例数据，需替换为实际网格）
    return {
        "1": {"name": "市中心核心区", "bounds": [36.65, 36.67, 117.00, 117.02]},
        "2": {"name": "商业购物区", "bounds": [36.67, 36.69, 117.02, 117.04]},
        "3": {"name": "住宅居民区", "bounds": [36.69, 36.71, 117.04, 117.06]},
        "4": {"name": "工业开发区", "bounds": [36.71, 36.73, 117.06, 117.08]},
        "5": {"name": "文教科研区", "bounds": [36.73, 36.75, 117.08, 117.10]},
        "6": {"name": "交通枢纽区", "bounds": [36.75, 36.77, 117.10, 117.12]},
        "7": {"name": "休闲娱乐区", "bounds": [36.77, 36.79, 117.12, 117.14]}
    }

def calculate_congestion_rate(vehicle_count: int, area_size: float = 1.2321) -> Tuple[float, str]:
    """计算拥堵率和流量等级，面积单位为平方公里"""
    density = vehicle_count / area_size
    congestion_rate = min(density * 100, 100)  # 简单密度公式，需调整
    if congestion_rate >= 80:
        return congestion_rate, "严重拥堵"
    elif congestion_rate >= 60:
        return congestion_rate, "重度拥堵"
    elif congestion_rate >= 40:
        return congestion_rate, "中度拥堵"
    elif congestion_rate >= 20:
        return congestion_rate, "轻度拥堵"
    else:
        return congestion_rate, "基本畅通"

# --- 新增 API 端点 ---
@router.get("/daily", response_model=DailyTrafficResponse)
async def get_daily_traffic(
        date: str = Query(None, description="日期，格式为YYYY-MM-DD，默认为今天")
):
    """获取每日流量趋势（24小时车辆数）- 只读缓存文件"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    cache_file = os.path.join(CACHE_DIR, f'daily_{date}.json')
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        logger.info("流量分析", f"直接返回缓存: {cache_file}")
        return DailyTrafficResponse(**cache_data)
    else:
        logger.error("流量分析", f"未找到缓存文件: {cache_file}")
        return DailyTrafficResponse(
            success=False,
            message=f"未找到缓存文件: {cache_file}，请先运行缓存生成脚本。",
            data=[0] * 24
        )

@router.get("/weekly", response_model=WeeklyTrafficResponse)
async def get_weekly_traffic(
        start_date: str = Query(None, description="周起始日期，格式为YYYY-MM-DD，默认为数据集的起始周")
):
    if not start_date:
        start_date = "2013-09-12"
    # 只允许2013-09-12
    if start_date != "2013-09-12":
        return WeeklyTrafficResponse(
            success=False,
            message="只支持2013-09-12作为起始日期",
            data=[]
        )
    cache_file = os.path.join(CACHE_DIR, f'weekly_{start_date}.json')
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        logger.info("流量分析", f"直接返回缓存: {cache_file}")
        return WeeklyTrafficResponse(**cache_data)
    else:
        logger.error("流量分析", f"未找到缓存文件: {cache_file}")
        return WeeklyTrafficResponse(
            success=False,
            message=f"未找到缓存文件: {cache_file}，请先运行缓存生成脚本。",
            data=[]
        )

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
        date: str = Query(None, description="日期，格式为YYYY-MM-DD，默认为数据集起始日期"),
        period: str = Query("today", description="时间范围：today, week（兼容性参数）")
):
    """获取关键指标（总流量、平均速度、高峰时长、活跃用户）- 使用完整数据统计"""
    # 缓存文件名逻辑
    if date:
        cache_file = os.path.join(CACHE_DIR, f'metrics_{date}.json')
    else:
        # week 模式下用 metrics_week_2013-09-12.json
        cache_file = os.path.join(CACHE_DIR, f'metrics_week_2013-09-12.json')
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        logger.info("流量分析", f"直接返回指标缓存: {cache_file}")
        return MetricsResponse(**cache_data)
    try:
        # 🔧 修复：使用数据集的实际日期范围
        if date:
            # 验证日期是否在数据集范围内
            dataset_start = "2013-09-12"
            dataset_end = "2013-09-18"

            requested_date = datetime.strptime(date, "%Y-%m-%d")
            dataset_start_date = datetime.strptime(dataset_start, "%Y-%m-%d")
            dataset_end_date = datetime.strptime(dataset_end, "%Y-%m-%d")

            if requested_date < dataset_start_date or requested_date > dataset_end_date:
                return MetricsResponse(
                    success=False,
                    message=f"请求的日期超出数据集范围，可用日期：{dataset_start} 到 {dataset_end}",
                    data=[
                        KeyMetric(title="总流量", value="0", trend=0),
                        KeyMetric(title="平均速度", value="0.0km/h", trend=0),
                        KeyMetric(title="高峰时长", value="0.0h", trend=0),
                        KeyMetric(title="活跃用户", value="0", trend=0)
                    ]
                )

            # 使用传入的具体日期
            start_time = datetime.strptime(date, "%Y-%m-%d")
            end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
            hours = 24
            period_desc = f"日期 {date}"
        else:
            # 使用数据集的默认日期而不是当前时间
            if period == "today":
                start_time = datetime.strptime("2013-09-12", "%Y-%m-%d")  # 数据集起始日期
                end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
                hours = 24
                period_desc = "数据集起始日期(2013-09-12)"
            else:  # week
                start_time = datetime.strptime("2013-09-12", "%Y-%m-%d")  # 数据集起始日期
                end_time = start_time + timedelta(days=7) - timedelta(seconds=1)
                hours = 7 * 24
                period_desc = "数据集的完整周(2013-09-12 到 2013-09-18)"

        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())

        logger.info("流量分析", f"查询关键指标: {period_desc} ({start_timestamp} - {end_timestamp})")

        # 🚀 使用新的流量统计加载器计算指标
        metrics_data = traffic_stats_loader.calculate_key_metrics(
            start_timestamp,
            end_timestamp,
            hours
        )

        if not metrics_data["data_available"]:
            logger.warning("流量分析", f"未找到 {period_desc} 的数据")
            return MetricsResponse(
                success=False,
                message=f"未找到{period_desc}的流量数据",
                data=[
                    KeyMetric(title="总流量", value="0", trend=0),
                    KeyMetric(title="平均速度", value="0.0km/h", trend=0),
                    KeyMetric(title="高峰时长", value="0.0h", trend=0),
                    KeyMetric(title="活跃用户", value="0", trend=0)
                ]
            )

        # 📊 构建指标结果
        metrics = [
            KeyMetric(
                title="总流量",
                value=f"{metrics_data['total_vehicles']:,}",
                trend=0
            ),
            KeyMetric(
                title="平均速度",
                value=f"{metrics_data['avg_speed']:.1f}km/h",
                trend=0
            ),
            KeyMetric(
                title="高峰时长",
                value=f"{metrics_data['peak_hours']:.1f}h",
                trend=0
            ),
            KeyMetric(
                title="活跃用户",
                value=f"{metrics_data['unique_vehicles']:,}",
                trend=0
            )
        ]

        # 📈 添加详细的成功消息
        success_message = (
            f"成功获取{period_desc}的关键指标 - "
            f"总流量: {metrics_data['total_vehicles']:,}, "
            f"活跃车辆: {metrics_data['unique_vehicles']:,}, "
            f"平均速度: {metrics_data['avg_speed']:.1f}km/h"
        )

        result = MetricsResponse(
            success=True,
            message=success_message,
            data=convert_numpy_types(metrics)
        )
        # 写入缓存
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result.dict(), f, ensure_ascii=False)
        return result

    except ValueError as ve:
        # 处理日期格式错误
        logger.error("流量分析", f"日期格式错误: {str(ve)}")
        result = MetricsResponse(
            success=False,
            message=f"日期格式错误，请使用YYYY-MM-DD格式: {str(ve)}",
            data=[
                KeyMetric(title="总流量", value="0", trend=0),
                KeyMetric(title="平均速度", value="0.0km/h", trend=0),
                KeyMetric(title="高峰时长", value="0.0h", trend=0),
                KeyMetric(title="活跃用户", value="0", trend=0)
            ]
        )
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result.dict(), f, ensure_ascii=False)
        return result
    except Exception as e:
        logger.error("流量分析", f"关键指标查询失败: {str(e)}")
        logger.error("流量分析", f"错误详情: {traceback.format_exc()}")
        result = MetricsResponse(
            success=False,
            message=f"查询失败: {str(e)}",
            data=[
                KeyMetric(title="总流量", value="0", trend=0),
                KeyMetric(title="平均速度", value="0.0km/h", trend=0),
                KeyMetric(title="高峰时长", value="0.0h", trend=0),
                KeyMetric(title="活跃用户", value="0", trend=0)
            ]
        )
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result.dict(), f, ensure_ascii=False)
        return result

@router.get("/areas", response_model=AreaStatsResponse)
async def get_area_stats(
        date: str = Query(None, description="日期，格式为YYYY-MM-DD"),
        period: str = Query("today", description="时间范围：today, week（兼容性参数）")
):
    """获取区域统计（车辆数、平均速度、拥堵率、流量等级）"""
    try:
        spatial_grid = load_spatial_grid()

        # 🔧 修复：使用传入的日期
        if date:
            start_time = datetime.strptime(date, "%Y-%m-%d")
            end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
            period_desc = f"日期 {date}"
        else:
            start_time = datetime.now()
            if period == "today":
                start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
                period_desc = "今日"
            else:  # week
                start_time = start_time - timedelta(days=start_time.weekday())
                end_time = start_time + timedelta(days=7) - timedelta(seconds=1)
                period_desc = "本周"

        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())

        logger.info("流量分析", f"查询区域统计: {period_desc} ({start_timestamp} - {end_timestamp})")

        # 加载数据
        df = data_processor.load_data(start_timestamp, end_timestamp)

        if df.empty:
            return AreaStatsResponse(
                success=False,
                message="未找到指定时间范围的流量数据",
                data=[]
            )

        # 按区域聚合
        area_data = {grid_id: {"total_vehicles": 0, "total_speed": 0, "count": 0} for grid_id in spatial_grid}

        for _, row in df.iterrows():
            # 正确处理坐标
            lat = row['LAT'] / 1e5 if 'LAT' in row else 0
            lon = row['LON'] / 1e5 if 'LON' in row else 0

            for grid_id, grid in spatial_grid.items():
                min_lat, max_lat, min_lon, max_lon = grid['bounds']
                if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                    area_data[grid_id]['total_vehicles'] += 1
                    # 正确处理速度
                    speed = 0
                    if 'SPEED' in row and pd.notna(row['SPEED']):
                        speed = row['SPEED']
                    elif 'speed' in row and pd.notna(row['speed']):
                        speed = row['speed']
                    area_data[grid_id]['total_speed'] += speed
                    area_data[grid_id]['count'] += 1
                    break

        # 构造结果
        result = []
        for grid_id, data in area_data.items():
            if data['count'] > 0:
                avg_speed = data['total_speed'] / data['count']
                congestion_rate, traffic_level = calculate_congestion_rate(data['total_vehicles'])
                result.append(AreaStat(
                    id=int(grid_id),
                    name=spatial_grid[grid_id]['name'],
                    totalVehicles=data['total_vehicles'],
                    avgSpeed=round(avg_speed, 1),
                    congestionRate=round(congestion_rate, 1),
                    trafficLevel=traffic_level
                ))

        return AreaStatsResponse(
            success=True,
            message=f"成功获取 {period} 的区域统计数据，共 {len(result)} 个区域",
            data=convert_numpy_types(result)
        )
    except Exception as e:
        logger.error("流量分析", f"区域统计查询失败: {str(e)}")
        return AreaStatsResponse(
            success=False,
            message=f"查询失败: {str(e)}",
            data=[]
        )

@router.get("/periods", response_model=PeriodStatsResponse)
async def get_period_stats(
        date: str = Query(None, description="日期，格式为YYYY-MM-DD"),
        period: str = Query("today", description="时间范围：today, week（兼容性参数）")
):
    """获取时间段统计（早高峰、晚高峰、平峰）"""
    try:
        # 🔧 修复：使用传入的日期
        if date:
            start_time = datetime.strptime(date, "%Y-%m-%d")
            days = 1
            period_desc = f"日期 {date}"
        else:
            start_time = datetime.now()
            if period == "today":
                start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
                days = 1
                period_desc = "今日"
            else:  # week
                start_time = start_time - timedelta(days=start_time.weekday())
                days = 7
                period_desc = "本周"

        periods = [
            {"name": "早高峰", "start_hour": 7, "end_hour": 9, "timeRange": "07:00-09:00"},
            {"name": "晚高峰", "start_hour": 17, "end_hour": 19, "timeRange": "17:00-19:00"},
            {"name": "平峰时段", "start_hour": 10, "end_hour": 16, "timeRange": "10:00-16:00"}
        ]

        start_timestamp = int(start_time.timestamp())
        end_timestamp = int((start_time + timedelta(days=days)).timestamp() - 1)

        logger.info("流量分析", f"查询时间段统计: {period_desc} ({start_timestamp} - {end_timestamp})")
        # 加载数据
        df = data_processor.load_data(start_timestamp, end_timestamp)

        if df.empty:
            return PeriodStatsResponse(
                success=False,
                message="未找到指定时间范围的流量数据",
                data=[PeriodStat(
                    name=p['name'],
                    timeRange=p['timeRange'],
                    avgVehicles=0,
                    avgSpeed=0.0,
                    status="畅通",
                    statusClass="bg-green-500/20 text-green-400"
                ) for p in periods]
            )

        # 按时间段聚合
        result = []
        time_col = 'UTC' if 'UTC' in df.columns else 'timestamp'
        df['hour'] = pd.to_datetime(df[time_col], unit='s').dt.hour
        df['date'] = pd.to_datetime(df[time_col], unit='s').dt.date

        for p in periods:
            total_vehicles = 0
            total_speed = 0
            count = 0

            for day in range(days):
                day_start = start_time + timedelta(days=day)
                day_df = df[df['date'] == day_start.date()]
                period_df = day_df[day_df['hour'].between(p['start_hour'], p['end_hour'] - 1)]

                total_vehicles += len(period_df)
                # 正确计算速度
                speed_sum = 0
                if 'SPEED' in period_df.columns:
                    speed_sum = period_df['SPEED'].fillna(0).sum()
                elif 'speed' in period_df.columns:
                    speed_sum = period_df['speed'].fillna(0).sum()
                total_speed += speed_sum
                count += len(period_df) if not period_df.empty else 0

            avg_vehicles = total_vehicles / (days * (p['end_hour'] - p['start_hour'])) if count > 0 else 0
            avg_speed = total_speed / total_vehicles if total_vehicles > 0 else 0
            status = "畅通" if avg_speed > 50 else "拥堵" if avg_speed < 35 else "中度拥堵"
            status_class = (
                "bg-green-500/20 text-green-400" if status == "畅通" else
                "bg-red-500/20 text-red-400" if status == "拥堵" else
                "bg-orange-500/20 text-orange-400"
            )

            result.append(PeriodStat(
                name=p['name'],
                timeRange=p['timeRange'],
                avgVehicles=round(avg_vehicles),
                avgSpeed=round(avg_speed, 1),
                status=status,
                statusClass=status_class
            ))

        return PeriodStatsResponse(
            success=True,
            message=f"成功获取 {period} 的时间段统计数据",
            data=convert_numpy_types(result)
        )
    except Exception as e:
        logger.error("流量分析", f"时间段统计查询失败: {str(e)}")
        return PeriodStatsResponse(
            success=False,
            message=f"查询失败: {str(e)}",
            data=[PeriodStat(
                name=p['name'],
                timeRange=p['timeRange'],
                avgVehicles=0,
                avgSpeed=0.0,
                status="畅通",
                statusClass="bg-green-500/20 text-green-400"
            ) for p in periods]
        )



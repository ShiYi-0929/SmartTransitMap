from fastapi import APIRouter, Query
import pandas as pd
import os
import datetime
from collections import defaultdict # 用于数据聚合

router = APIRouter()


@router.get("/stats")
async def get_traffic_stats():
    """
    获取交通数据统计信息。
    """
    data_dir = os.path.join(os.path.dirname(__file__), '../../data')
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    print("找到文件：", files)
    if not files:
        return {"error": "no csv file"}
    try:
        df = pd.read_csv(os.path.join(data_dir, files[0]), nrows=10, encoding='gbk')
        print("读取成功，行数：", len(df))
        car_set = set(df['COMMADDR'].unique())
        return {
            "车辆总数": len(car_set),
            "轨迹点总数": len(df)
        }
    except Exception as e:
        print("读取出错：", e)
        return {"error": str(e)}


@router.get("/visualization")
async def get_traffic_visualization(
        date: str = Query(None),  # 将日期参数设为可选
        start_time: float = Query(None),  # 新增起始时间参数
        end_time: float = Query(None)  # 新增结束时间参数
):
    """
    获取交通数据可视化所需数据（例如热力图数据）。
    可以根据日期或精确的时间范围返回热力图数据。
    """
    data_dir = os.path.join(os.path.dirname(__file__), '../../data')
    heatmap_data = []

    # 确定时间过滤范围
    filter_start_utc = None
    filter_end_utc = None

    if start_time is not None and end_time is not None:
        filter_start_utc = start_time
        filter_end_utc = end_time
    elif date:
        try:
            # 示例：假设日期格式为 'MMDD' 或 'YYYYMMDD'
            # 您需要根据实际情况调整年份和解析逻辑
            if len(date) == 4:  # MMDD
                year = datetime.datetime.now().year  # 使用当前年份
                month = int(date[:2])
                day = int(date[2:])
            elif len(date) == 8:  # YYYYMMDD
                year = int(date[:4])
                month = int(date[4:6])
                day = int(date[6:])
            else:
                return {"error": "Invalid date format. Expected 'MMDD' or 'YYYYMMDD'."}

            start_dt = datetime.datetime(year, month, day, 0, 0, 0)
            end_dt = datetime.datetime(year, month, day, 23, 59, 59)
            filter_start_utc = start_dt.timestamp()
            filter_end_utc = end_dt.timestamp()

        except ValueError:
            return {"error": "Invalid date format. Expected 'MMDD' or 'YYYYMMDD'."}
    else:
        return {"error": "Either 'date' or 'start_time' and 'end_time' must be provided."}

    for fname in os.listdir(data_dir):
        if fname.endswith('.csv'):
            df = pd.read_csv(os.path.join(data_dir, fname))

            # 过滤指定时间范围的数据
            if filter_start_utc is not None and filter_end_utc is not None:
                df_filtered = df[(df['UTC'] >= filter_start_utc) & (df['UTC'] <= filter_end_utc)]
            else:
                df_filtered = df  # 如果没有时间范围，则不过滤

            # TODO: 实现“上客数量”的逻辑。
            # 这需要您的CSV数据中有一个字段能够指示“上客事件”。
            # 假设这里只是简单地统计在时间范围内每个位置点的出现次数作为权重，
            # 或者如果数据点本身就代表“上客”，则每个点权重为1。
            # 更精确的“上客数量”可能需要识别车辆在某个位置停止并停留一段时间后的移动。

            # 简单的聚合示例：按经纬度四舍五入聚合计数
            df_filtered['LON_rounded'] = (df_filtered['LON'] / 1e5).round(4)  # 保留4位小数作为简易格点
            df_filtered['LAT_rounded'] = (df_filtered['LAT'] / 1e5).round(4)

            # 统计每个（近似）位置点的数量作为权重
            # 如果是上客点，则只对上客点进行计数
            # current_counts = df_filtered.groupby(['LON_rounded', 'LAT_rounded']).size().reset_index(name='count')
            # 假设所有点都是上客点，或者您有一个列来标识
            for index, row in df_filtered.iterrows():
                heatmap_data.append({
                    'lng': row['LON'] / 1e5,
                    'lat': row['LAT'] / 1e5,
                    'count': 1  # 假设每个轨迹点权重为1，代表一次“活动”或“上客”
                })

    return {"heatmap_data": heatmap_data}


@router.get("/track")
async def get_track(
        start_time: float = Query(...),
        end_time: float = Query(...),
        car_id: str = Query(None)  # 新增car_id参数，可选
):
    """
    按时间段和车辆ID查询车辆轨迹数据。
    """
    data_dir = os.path.join(os.path.dirname(__file__), '../../data')
    all_tracks = []

    # 遍历所有CSV文件
    for fname in os.listdir(data_dir):
        if fname.endswith('.csv'):
            df = pd.read_csv(os.path.join(data_dir, fname))

            # 过滤时间段
            df = df[(df['UTC'] >= start_time) & (df['UTC'] <= end_time)]

            # 如果提供了car_id，则进一步过滤
            if car_id:
                df = df[df['COMMADDR'] == car_id]

            # 按车辆ID分组，并提取轨迹
            for commaddr, group in df.groupby('COMMADDR'):
                track = group[['LON', 'LAT', 'UTC']].to_dict(orient='records')
                all_tracks.append({'car_id': commaddr, 'track': track})
    return all_tracks


@router.get("/orders/analysis")
async def get_orders_analysis(
        start_utc: float = Query(...),
        end_utc: float = Query(...)
):
    """
    根据订单起止时间，分析乘客乘车的距离与时间分布。
    返回订单耗时、路程的分布数据，以及按时段（如小时）聚合的订单数量。
    """
    data_dir = os.path.join(os.path.dirname(__file__), '../../data')
    all_orders_data = []

    for fname in os.listdir(data_dir):
        if fname.endswith('.csv'):
            df = pd.read_csv(os.path.join(data_dir, fname))

            # 假设 CSV 包含 PICKUP_TIME_UTC, DROPOFF_TIME_UTC, DISTANCE_KM, DURATION_MIN
            # 如果没有，需要在此处计算或从其他列推断
            required_cols = [
                'PICKUP_TIME_UTC', 'DROPOFF_TIME_UTC',
                'DISTANCE_KM', 'DURATION_MIN'
            ]
            if not all(col in df.columns for col in required_cols):
                # 示例：如果缺少，尝试计算
                if 'UTC' in df.columns and 'COMMADDR' in df.columns:
                    # 这是一个简化的假设，实际订单数据可能需要更复杂的逻辑来识别
                    # 这里假设每个COMMADDR在时间范围内的第一个点是上车，最后一个点是下车
                    # 这种推断方式非常粗糙，仅为示例，实际应有明确的订单数据

                    # 过滤时间段
                    df_filtered_time = df[(df['UTC'] >= start_utc) & (df['UTC'] <= end_utc)].copy()

                    if df_filtered_time.empty:
                        continue

                    # 假设每个COMMADDR的第一个点是上车，最后一个点是下车来模拟订单
                    # 实际订单数据应该有明确的PICKUP_TIME_UTC和DROPOFF_TIME_UTC
                    for commaddr, group in df_filtered_time.groupby('COMMADDR'):
                        if len(group) < 2:  # 至少需要两个点才能形成“订单”
                            continue

                        first_point = group.iloc[0]
                        last_point = group.iloc[-1]

                        pickup_time = first_point['UTC']
                        dropoff_time = last_point['UTC']
                        duration = (dropoff_time - pickup_time) / 60.0  # 秒转分钟

                        # 简化的距离计算：使用欧氏距离或更精确的Haversine公式
                        # 这里仅为示例，实际应使用地理距离
                        pickup_lon, pickup_lat = first_point['LON'] / 1e5, first_point['LAT'] / 1e5
                        dropoff_lon, dropoff_lat = last_point['LON'] / 1e5, last_point['LAT'] / 1e5
                        distance = ((pickup_lon - dropoff_lon) ** 2 + (
                                    pickup_lat - dropoff_lat) ** 2) ** 0.5 * 100  # 示例距离，需要根据实际坐标单位调整

                        all_orders_data.append({
                            'pickup_time': pickup_time,
                            'duration': duration,
                            'distance': distance
                        })
                else:
                    print(f"警告: 文件 {fname} 缺少必要的订单分析列或无法推断。")
                continue  # 跳过当前文件，继续处理下一个

            # 过滤指定时间范围内的订单
            df_orders_filtered = df[
                (df['PICKUP_TIME_UTC'] >= start_utc) &
                (df['DROPOFF_TIME_UTC'] <= end_utc)
                ].copy()  # 使用copy避免SettingWithCopyWarning

            if df_orders_filtered.empty:
                continue

            for index, row in df_orders_filtered.iterrows():
                all_orders_data.append({
                    'pickup_time': row['PICKUP_TIME_UTC'],
                    'duration': row['DURATION_MIN'],
                    'distance': row['DISTANCE_KM']
                })

    if not all_orders_data:
        return {"error": "在指定时间范围内没有找到订单数据。", "data": {}}

    df_all_orders = pd.DataFrame(all_orders_data)

    # 1. 耗时与路程分布 (直方图数据)
    duration_bins = [0, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 360, 720, 1440]  # 示例分钟区间
    distance_bins = [0, 1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 100, 200]  # 示例公里区间

    duration_counts, _ = pd.cut(df_all_orders['duration'], bins=duration_bins, right=False,
                                include_lowest=True).value_counts(sort=False).align(
        pd.IntervalIndex.from_breaks(duration_bins, closed='left'), fill_value=0)
    distance_counts, _ = pd.cut(df_all_orders['distance'], bins=distance_bins, right=False,
                                include_lowest=True).value_counts(sort=False).align(
        pd.IntervalIndex.from_breaks(distance_bins, closed='left'), fill_value=0)

    duration_distribution = [{"range": str(interval), "count": count} for interval, count in duration_counts.items()]
    distance_distribution = [{"range": str(interval), "count": count} for interval, count in distance_counts.items()]

    # 2. 订单时段分布 (按小时聚合)
    df_all_orders['pickup_datetime'] = pd.to_datetime(df_all_orders['pickup_time'], unit='s')
    df_all_orders['hour'] = df_all_orders['pickup_datetime'].dt.hour
    time_segment_distribution = df_all_orders['hour'].value_counts().sort_index().to_dict()
    # 确保所有小时都有数据，没有的补0
    full_hour_distribution = {h: time_segment_distribution.get(h, 0) for h in range(24)}
    time_segment_distribution_list = [{"hour": h, "count": full_hour_distribution[h]} for h in
                                      sorted(full_hour_distribution.keys())]

    return {
        "duration_distribution": duration_distribution,
        "distance_distribution": distance_distribution,
        "time_segment_distribution": time_segment_distribution_list,
        "raw_orders_for_scatter": df_all_orders[['duration', 'distance']].to_dict(orient='records')  # 用于散点图
    }
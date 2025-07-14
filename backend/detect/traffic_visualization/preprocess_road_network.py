#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
路网数据预处理脚本
将CSV格式的路网数据预处理并保存为pickle格式，以加快后续读取速度
"""

import os
import pandas as pd
import pickle
import logging
from typing import List, Dict, Any
import time
from .models import RoadSegment

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def preprocess_road_network(csv_path: str = None, output_path: str = None) -> List[RoadSegment]:
    """
    预处理路网数据并保存为pickle文件
    
    Args:
        csv_path: CSV文件路径，如果为None则使用默认路径
        output_path: 输出pickle文件路径，如果为None则使用默认路径
        
    Returns:
        处理后的路段对象列表
    """
    try:
        start_time = time.time()
        
        # 如果未指定路径，使用默认路径
        if csv_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(current_dir, 'data', 'jn_FX.csv')
        
        if output_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            cache_dir = os.path.join(current_dir, 'data', 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            output_path = os.path.join(cache_dir, 'road_network.pkl')
        
        logger.info(f"从 {csv_path} 加载路网数据...")
        
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        logger.info(f"加载了 {len(df)} 条路段数据")
        
        # 转换为RoadSegment对象列表
        segments = []
        for _, row in df.iterrows():
            segment_id = str(row['ID'])
            start_point = {'lat': row['Start_Y'], 'lng': row['Start_X']}
            end_point = {'lat': row['END_Y'], 'lng': row['END_X']}
            
            # 确定道路类型（简单分类）
            length = row['Length']
            road_type = classify_road_type_by_length(length)
            
            # 创建路段对象
            segment = RoadSegment(
                segment_id=segment_id,
                start_point=start_point,
                end_point=end_point,
                segment_length=length / 1000,  # 转换为公里
                road_type=road_type,
                road_name=f"Road_{segment_id}"
            )
            segments.append(segment)
        
        # 保存为pickle文件
        with open(output_path, 'wb') as f:
            pickle.dump(segments, f)
        
        processing_time = time.time() - start_time
        logger.info(f"成功预处理并保存 {len(segments)} 条路段到 {output_path}，耗时 {processing_time:.2f} 秒")
        
        return segments
        
    except Exception as e:
        logger.error(f"预处理路网数据时出错: {str(e)}")
        return []

def load_preprocessed_road_network(pickle_path: str = None) -> List[RoadSegment]:
    """
    从预处理的pickle文件加载路网数据
    
    Args:
        pickle_path: pickle文件路径，如果为None则使用默认路径
        
    Returns:
        路段对象列表
    """
    try:
        start_time = time.time()
        
        # 如果未指定路径，使用默认路径
        if pickle_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            pickle_path = os.path.join(current_dir, 'data', 'cache', 'road_network.pkl')
        
        # 检查文件是否存在
        if not os.path.exists(pickle_path):
            logger.warning(f"预处理文件 {pickle_path} 不存在，将重新生成")
            return preprocess_road_network(output_path=pickle_path)
        
        # 加载pickle文件
        with open(pickle_path, 'rb') as f:
            segments = pickle.load(f)
        
        processing_time = time.time() - start_time
        logger.info(f"从 {pickle_path} 加载了 {len(segments)} 条路段，耗时 {processing_time:.2f} 秒")
        
        return segments
        
    except Exception as e:
        logger.error(f"加载预处理路网数据时出错: {str(e)}")
        return []

def classify_road_type_by_length(length: float) -> str:
    """根据路段长度简单分类道路类型"""
    if length > 1000:  # 大于1000米
        return "highway"
    elif length > 500:  # 500-1000米
        return "arterial"
    elif length > 200:  # 200-500米
        return "urban"
    else:  # 小于200米
        return "local"

if __name__ == "__main__":
    # 当脚本直接运行时，执行预处理
    preprocess_road_network() 
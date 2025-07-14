#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试路网数据预处理和加载功能
"""

import os
import sys
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_road_network_preprocessing():
    """测试路网数据预处理和加载功能"""
    try:
        # 导入必要的模块
        from detect.traffic_visualization.road_analysis_engine import RoadAnalysisEngine
        from detect.traffic_visualization.preprocess_road_network import preprocess_road_network, load_preprocessed_road_network
        
        # 测试1：直接使用预处理函数生成预处理文件
        logger.info("测试1：使用预处理函数生成预处理文件")
        start_time = time.time()
        segments = preprocess_road_network()
        processing_time = time.time() - start_time
        logger.info(f"预处理完成，共处理 {len(segments)} 条路段，耗时 {processing_time:.2f} 秒")
        
        # 测试2：从预处理文件加载
        logger.info("\n测试2：从预处理文件加载")
        start_time = time.time()
        segments = load_preprocessed_road_network()
        processing_time = time.time() - start_time
        logger.info(f"从预处理文件加载完成，共加载 {len(segments)} 条路段，耗时 {processing_time:.2f} 秒")
        
        # 测试3：使用路段分析引擎加载
        logger.info("\n测试3：使用路段分析引擎加载")
        road_engine = RoadAnalysisEngine()
        start_time = time.time()
        segments = road_engine.load_road_network()
        processing_time = time.time() - start_time
        logger.info(f"使用路段分析引擎加载完成，共加载 {len(segments)} 条路段，耗时 {processing_time:.2f} 秒")
        
        # 输出测试结果
        if segments and len(segments) > 0:
            logger.info("测试成功！")
            # 输出前5条路段信息
            logger.info("前5条路段信息：")
            for i, segment in enumerate(segments[:5]):
                logger.info(f"路段 {i+1}: ID={segment.segment_id}, 长度={segment.segment_length:.2f}km, 类型={segment.road_type}")
        else:
            logger.error("测试失败：未能加载路段数据")
        
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")

if __name__ == "__main__":
    test_road_network_preprocessing() 
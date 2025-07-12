#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版数据分析测试脚本
分析jn0912文件前100行数据，找出数据清洗问题并制定预处理策略
修正了所有缩进错误
"""

import pandas as pd
import numpy as np
import os

def analyze_sample_data():
    """分析样本数据"""
    print("="*60)
    print("济南交通数据样本分析 (修正版)")
    print("="*60)
    
    # 数据文件路径
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    file_path = os.path.join(data_dir, 'jn0912.csv')
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    print(f"分析文件: {file_path}")
    print(f"文件大小: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
    
    # 读取前100行数据
    print("\n读取前100行数据进行分析...")
    try:
        df_sample = pd.read_csv(file_path, nrows=100)
        print(f"成功读取 {len(df_sample)} 行数据")
    except Exception as e:
        print(f"读取文件失败: {e}")
        return
    
    # 1. 基本信息分析
    print(f"\n{'='*50}")
    print("1. 数据基本信息")
    print(f"{'='*50}")
    print(f"数据形状: {df_sample.shape}")
    print(f"列名: {list(df_sample.columns)}")
    print(f"数据类型:")
    print(df_sample.dtypes)
    
    # 2. 查看前几行原始数据
    print(f"\n{'='*50}")
    print("2. 前5行原始数据")
    print(f"{'='*50}")
    print(df_sample.head().to_string())
    
    # 3. 缺失值分析
    print(f"\n{'='*50}")
    print("3. 缺失值分析")
    print(f"{'='*50}")
    missing_info = df_sample.isnull().sum()
    print("各列缺失值数量:")
    for col, missing_count in missing_info.items():
        missing_rate = missing_count / len(df_sample) * 100
        print(f"  {col}: {missing_count} ({missing_rate:.1f}%)")
    
    # 4. 数据范围分析
    print(f"\n{'='*50}")
    print("4. 数值列数据范围分析")
    print(f"{'='*50}")
    
    numeric_columns = df_sample.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        if not df_sample[col].isnull().all():
            print(f"\n{col} 列统计:")
            print(f"  最小值: {df_sample[col].min()}")
            print(f"  最大值: {df_sample[col].max()}")
            print(f"  平均值: {df_sample[col].mean():.2f}")
            print(f"  中位数: {df_sample[col].median()}")
            print(f"  标准差: {df_sample[col].std():.2f}")
            
            # 检查特殊值
            zero_count = (df_sample[col] == 0).sum()
            print(f"  零值数量: {zero_count} ({zero_count/len(df_sample)*100:.1f}%)")
    
    # 5. 坐标数据特殊分析
    print(f"\n{'='*50}")
    print("5. 坐标数据特殊分析")
    print(f"{'='*50}")
    
    if 'LAT' in df_sample.columns and 'LON' in df_sample.columns:
        # 原始坐标
        print("原始坐标范围:")
        print(f"  LAT: {df_sample['LAT'].min()} ~ {df_sample['LAT'].max()}")
        print(f"  LON: {df_sample['LON'].min()} ~ {df_sample['LON'].max()}")
        
        # 转换后坐标 (修正：除以100,000)
        df_sample['lat_converted'] = df_sample['LAT'] / 100000.0
        df_sample['lon_converted'] = df_sample['LON'] / 100000.0
        
        print("\n转换后坐标范围:")
        print(f"  纬度: {df_sample['lat_converted'].min():.6f} ~ {df_sample['lat_converted'].max():.6f}")
        print(f"  经度: {df_sample['lon_converted'].min():.6f} ~ {df_sample['lon_converted'].max():.6f}")
        
        # 检查坐标是否在济南市范围内
        jinan_lat_range = (36.0, 37.0)
        jinan_lon_range = (116.5, 117.5)
        
        lat_valid = ((df_sample['lat_converted'] >= jinan_lat_range[0]) & 
                     (df_sample['lat_converted'] <= jinan_lat_range[1])).sum()
        lon_valid = ((df_sample['lon_converted'] >= jinan_lon_range[0]) & 
                     (df_sample['lon_converted'] <= jinan_lon_range[1])).sum()
        
        print(f"\n济南市坐标范围验证:")
        print(f"  纬度在范围内的记录: {lat_valid}/{len(df_sample)} ({lat_valid/len(df_sample)*100:.1f}%)")
        print(f"  经度在范围内的记录: {lon_valid}/{len(df_sample)} ({lon_valid/len(df_sample)*100:.1f}%)")
        
        both_valid = ((df_sample['lat_converted'] >= jinan_lat_range[0]) & 
                      (df_sample['lat_converted'] <= jinan_lat_range[1]) &
                      (df_sample['lon_converted'] >= jinan_lon_range[0]) & 
                      (df_sample['lon_converted'] <= jinan_lon_range[1])).sum()
        
        print(f"  坐标完全在济南市范围内: {both_valid}/{len(df_sample)} ({both_valid/len(df_sample)*100:.1f}%)")
    
    # 6. 时间戳分析
    print(f"\n{'='*50}")
    print("6. 时间戳分析")
    print(f"{'='*50}")
    
    if 'UTC' in df_sample.columns:
        print("时间戳范围:")
        print(f"  最小UTC: {df_sample['UTC'].min()}")
        print(f"  最大UTC: {df_sample['UTC'].max()}")
        
        # 转换为可读时间
        df_sample['datetime'] = pd.to_datetime(df_sample['UTC'], unit='s')
        print(f"  最早时间: {df_sample['datetime'].min()}")
        print(f"  最晚时间: {df_sample['datetime'].max()}")
        
        # 检查时间范围是否合理（修正：基于实际数据调整）
        target_start = pd.to_datetime('2013-09-11 00:00:00')  # 数据显示从9月11日开始
        target_end = pd.to_datetime('2013-09-19 00:00:00')
        
        time_valid = ((df_sample['datetime'] >= target_start) & 
                      (df_sample['datetime'] <= target_end)).sum()
        
        print(f"  在目标时间范围内的记录: {time_valid}/{len(df_sample)} ({time_valid/len(df_sample)*100:.1f}%)")
        
        # 显示实际时间范围和目标范围的比较
        print(f"  目标时间范围: {target_start} ~ {target_end}")
        print(f"  实际时间范围: {df_sample['datetime'].min()} ~ {df_sample['datetime'].max()}")
    
    # 7. 速度数据分析
    print(f"\n{'='*50}")
    print("7. 速度数据分析")
    print(f"{'='*50}")
    
    if 'SPEED' in df_sample.columns:
        print("原始速度统计 (cm/s):")
        print(f"  范围: {df_sample['SPEED'].min()} ~ {df_sample['SPEED'].max()}")
        print(f"  平均: {df_sample['SPEED'].mean():.2f}")
        
        # 转换为km/h
        df_sample['speed_kmh'] = df_sample['SPEED'] * 0.036
        print(f"\n转换后速度统计 (km/h):")
        print(f"  范围: {df_sample['speed_kmh'].min():.2f} ~ {df_sample['speed_kmh'].max():.2f}")
        print(f"  平均: {df_sample['speed_kmh'].mean():.2f}")
        
        # 合理速度范围检查
        reasonable_speed = ((df_sample['speed_kmh'] >= 0) & 
                           (df_sample['speed_kmh'] <= 120)).sum()
        print(f"  合理速度范围(0-120km/h)内的记录: {reasonable_speed}/{len(df_sample)} ({reasonable_speed/len(df_sample)*100:.1f}%)")
    
    # 8. TFLAG分析
    print(f"\n{'='*50}")
    print("8. TFLAG字段分析")
    print(f"{'='*50}")
    
    if 'TFLAG' in df_sample.columns:
        tflag_counts = df_sample['TFLAG'].value_counts()
        print("TFLAG值分布:")
        for value, count in tflag_counts.items():
            print(f"  {value}: {count} ({count/len(df_sample)*100:.1f}%)")
        
        # 载客状态
        occupied = (df_sample['TFLAG'] == 268435456).sum()
        print(f"\n载客状态分析:")
        print(f"  载客记录(TFLAG=268435456): {occupied}/{len(df_sample)} ({occupied/len(df_sample)*100:.1f}%)")
    
    # 9. 综合数据质量评估
    print(f"\n{'='*50}")
    print("9. 综合数据质量评估")
    print(f"{'='*50}")
    
    # 模拟原清洗逻辑，看看哪一步出问题
    test_df = df_sample.copy()
    print(f"原始数据量: {len(test_df)}")
    
    # 检查必要列
    required_columns = ['COMMADDR', 'UTC', 'LAT', 'LON', 'SPEED', 'TFLAG']
    missing_cols = [col for col in required_columns if col not in test_df.columns]
    if missing_cols:
        print(f"❌ 缺少必要列: {missing_cols}")
        return
    else:
        print(f"✅ 所有必要列都存在")
    
    # 缺失值处理
    before_na = len(test_df)
    test_df = test_df.dropna(subset=required_columns)
    after_na = len(test_df)
    print(f"缺失值处理: {before_na} -> {after_na} (保留率: {after_na/before_na*100:.1f}%)")
    
    if len(test_df) == 0:
        print("❌ 缺失值处理后数据为空！")
        return
    
    # 数据类型转换
    try:
        test_df['UTC'] = pd.to_numeric(test_df['UTC'], errors='coerce')
        test_df['LAT'] = pd.to_numeric(test_df['LAT'], errors='coerce')
        test_df['LON'] = pd.to_numeric(test_df['LON'], errors='coerce')
        test_df['SPEED'] = pd.to_numeric(test_df['SPEED'], errors='coerce')
        test_df['TFLAG'] = pd.to_numeric(test_df['TFLAG'], errors='coerce')
        
        before_convert = len(test_df)
        test_df = test_df.dropna(subset=['UTC', 'LAT', 'LON', 'SPEED', 'TFLAG'])
        after_convert = len(test_df)
        print(f"数据类型转换: {before_convert} -> {after_convert} (保留率: {after_convert/before_convert*100:.1f}%)")
        
        if len(test_df) == 0:
            print("❌ 数据类型转换后数据为空！")
            return
            
    except Exception as e:
        print(f"❌ 数据类型转换失败: {e}")
        return
    
    # 坐标处理 (修正版)
    test_df['lat'] = test_df['LAT'] / 100000.0
    test_df['lon'] = test_df['LON'] / 100000.0
    
    before_coord = len(test_df)
    test_df = test_df[
        (test_df['lat'] >= 36.0) & (test_df['lat'] <= 37.0) &
        (test_df['lon'] >= 116.5) & (test_df['lon'] <= 117.5)
    ]
    after_coord = len(test_df)
    print(f"坐标范围过滤: {before_coord} -> {after_coord} (保留率: {after_coord/before_coord*100:.1f}%)")
    
    if len(test_df) == 0:
        print("❌ 坐标范围过滤后数据为空！")
        print("尝试检查更宽松的坐标范围...")
        
        # 尝试更宽松的范围检查
        wider_lat_range = (30.0, 40.0)  # 更宽的纬度范围
        wider_lon_range = (110.0, 120.0)  # 更宽的经度范围
        
        # 重新加载测试数据
        test_df_wider = df_sample.copy()
        test_df_wider['lat'] = test_df_wider['LAT'] / 100000.0
        test_df_wider['lon'] = test_df_wider['LON'] / 100000.0
        
        wider_valid = ((test_df_wider['lat'] >= wider_lat_range[0]) & 
                      (test_df_wider['lat'] <= wider_lat_range[1]) &
                      (test_df_wider['lon'] >= wider_lon_range[0]) & 
                      (test_df_wider['lon'] <= wider_lon_range[1])).sum()
        
        print(f"更宽松范围内的有效记录: {wider_valid}/{len(df_sample)}")
        print(f"实际坐标范围: 纬度 {test_df_wider['lat'].min():.3f}~{test_df_wider['lat'].max():.3f}, "
              f"经度 {test_df_wider['lon'].min():.3f}~{test_df_wider['lon'].max():.3f}")
        
        if wider_valid == 0:
            print("❌ 即使使用更宽松的范围，仍然没有有效数据")
            print("建议检查坐标转换逻辑或数据源")
        else:
            print("✅ 更宽松的范围可以保留数据，建议调整坐标验证范围")
        return
    
    # 时间范围过滤 (修正版)
    start_time = 1378857600  # 2013-09-11 00:00:00 UTC (修正)
    end_time = 1379548800    # 2013-09-19 00:00:00 UTC
    
    before_time = len(test_df)
    test_df = test_df[
        (test_df['UTC'] >= start_time) & (test_df['UTC'] <= end_time)
    ]
    after_time = len(test_df)
    print(f"时间范围过滤: {before_time} -> {after_time} (保留率: {after_time/before_time*100:.1f}%)")
    
    if len(test_df) == 0:
        print("❌ 时间范围过滤后数据为空！")
        print("实际时间戳与目标范围不匹配，需要调整时间范围")
        
        # 显示实际时间戳范围用于调试
        original_timestamps = df_sample['UTC']
        print(f"实际时间戳范围: {original_timestamps.min()} ~ {original_timestamps.max()}")
        print(f"目标时间戳范围: {start_time} ~ {end_time}")
        print(f"时间戳差异: 目标起始比实际起始{'早' if start_time < original_timestamps.min() else '晚'} "
              f"{abs(start_time - original_timestamps.min())} 秒")
        return
    
    # 速度范围过滤
    test_df['speed_kmh'] = test_df['SPEED'] * 0.036
    before_speed = len(test_df)
    test_df = test_df[
        (test_df['speed_kmh'] >= 0) & (test_df['speed_kmh'] <= 120)
    ]
    after_speed = len(test_df)
    print(f"速度范围过滤: {before_speed} -> {after_speed} (保留率: {after_speed/before_speed*100:.1f}%)")
    
    print(f"\n✅ 最终保留数据: {len(test_df)}/{len(df_sample)} (总保留率: {len(test_df)/len(df_sample)*100:.1f}%)")
    
    # 10. 推荐的预处理策略
    print(f"\n{'='*50}")
    print("10. 推荐的预处理策略")
    print(f"{'='*50}")
    
    print("基于分析结果，推荐以下预处理策略:")
    print("1. ✅ 保留所有必要列的检查")
    print("2. ✅ 修正坐标转换：除以100,000而不是1,000,000")
    print("3. ✅ 调整时间范围：从2013-09-11开始而不是2013-09-12")
    print("4. ✅ 保持速度验证：0-120km/h范围合理")
    print("5. ✅ 保持TFLAG载客状态验证")
    print("6. 🔧 建议济南市坐标范围：纬度36.0-37.0，经度116.5-117.5")
    print("7. 🔧 建议分块大小：50,000行以提高稳定性")
    
    # 如果有成功保留的数据，显示预期保留率
    if len(test_df) > 0:
        expected_retention = len(test_df) / len(df_sample) * 100
        print(f"\n📊 基于样本分析，预期整体数据保留率: {expected_retention:.1f}%")
        if expected_retention > 50:
            print("✅ 保留率良好，可以进行完整文件处理")
        elif expected_retention > 20:
            print("⚠️ 保留率一般，建议进一步优化过滤条件")
        else:
            print("❌ 保留率过低，需要重新检查预处理逻辑")
    else:
        print("\n❌ 样本数据全部被过滤，需要修正预处理策略后再试")

if __name__ == "__main__":
    analyze_sample_data()
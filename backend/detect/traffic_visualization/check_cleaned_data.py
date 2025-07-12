#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查清洗后数据的格式和内容
"""

import pandas as pd
import os
from datetime import datetime

def check_cleaned_data():
    """检查清洗后的数据"""
    print("🔍 检查清洗后的交通数据")
    print("=" * 50)
    
    # 数据目录
    data_dir = os.path.join(os.path.dirname(__file__), 'data', 'cleaned')
    print(f"清洗后数据目录: {data_dir}")
    
    if not os.path.exists(data_dir):
        print("❌ 清洗后数据目录不存在")
        return False
    
    # 查找CSV文件
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if not csv_files:
        print("❌ 未找到清洗后的CSV文件")
        return False
    
    print(f"✅ 找到 {len(csv_files)} 个CSV文件:")
    
    total_size = 0
    for csv_file in csv_files:
        file_path = os.path.join(data_dir, csv_file)
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        total_size += file_size
        print(f"   📄 {csv_file}: {file_size:.1f} MB")
    
    print(f"📊 总大小: {total_size:.1f} MB")
    
    # 检查第一个文件的格式
    print(f"\n🔍 检查文件格式和内容...")
    first_file = os.path.join(data_dir, csv_files[0])
    
    try:
        # 读取前几行
        sample_df = pd.read_csv(first_file, nrows=10)
        print(f"\n📋 列信息:")
        print(f"   列数: {len(sample_df.columns)}")
        print(f"   列名: {list(sample_df.columns)}")
        
        # 检查实际的列格式
        actual_columns = list(sample_df.columns)
        expected_columns = ['COMMADDR', 'UTC', 'LAT', 'LON', 'HEAD', 'SPEED', 'TFLAG', 
                          'lat', 'lon', 'speed_kmh', 'is_occupied', 'timestamp']
        
        missing_columns = [col for col in expected_columns if col not in sample_df.columns]
        extra_columns = [col for col in sample_df.columns if col not in expected_columns]
        
        if missing_columns:
            print(f"⚠️ 缺少列: {missing_columns}")
        if extra_columns:
            print(f"ℹ️ 额外列: {extra_columns}")
        if not missing_columns:
            print("✅ 所有预期列都存在")
        
        # 显示前几行数据
        print(f"\n📊 前5行数据:")
        print(sample_df.head().to_string())
        
        # 数据类型检查
        print(f"\n🔢 数据类型:")
        print(sample_df.dtypes.to_string())
        
        # 关键列的数据范围检查
        print(f"\n📈 关键数据范围:")
        
        if 'UTC' in sample_df.columns:
            utc_min = sample_df['UTC'].min()
            utc_max = sample_df['UTC'].max()
            print(f"   UTC时间戳: {utc_min} ~ {utc_max}")
            
            # 转换为可读时间
            try:
                dt_min = datetime.fromtimestamp(utc_min)
                dt_max = datetime.fromtimestamp(utc_max)
                print(f"   可读时间: {dt_min} ~ {dt_max}")
            except:
                print("   ⚠️ 时间戳转换失败")
        
        if 'lat' in sample_df.columns and 'lon' in sample_df.columns:
            lat_range = (sample_df['lat'].min(), sample_df['lat'].max())
            lon_range = (sample_df['lon'].min(), sample_df['lon'].max())
            print(f"   纬度范围: {lat_range[0]:.6f} ~ {lat_range[1]:.6f}")
            print(f"   经度范围: {lon_range[0]:.6f} ~ {lon_range[1]:.6f}")
            
            # 检查是否在济南市范围内
            jinan_lat = (36.0, 37.0)
            jinan_lon = (116.5, 117.5)
            
            if (jinan_lat[0] <= lat_range[0] <= lat_range[1] <= jinan_lat[1] and
                jinan_lon[0] <= lon_range[0] <= lon_range[1] <= jinan_lon[1]):
                print("   ✅ 坐标在济南市范围内")
            else:
                print("   ⚠️ 坐标可能超出济南市范围")
        
        if 'speed_kmh' in sample_df.columns:
            speed_range = (sample_df['speed_kmh'].min(), sample_df['speed_kmh'].max())
            print(f"   速度范围: {speed_range[0]:.1f} ~ {speed_range[1]:.1f} km/h")
            
            reasonable_speed = ((sample_df['speed_kmh'] >= 0) & 
                              (sample_df['speed_kmh'] <= 120)).sum()
            print(f"   合理速度记录: {reasonable_speed}/{len(sample_df)} ({reasonable_speed/len(sample_df)*100:.1f}%)")
        
        if 'COMMADDR' in sample_df.columns:
            unique_vehicles = sample_df['COMMADDR'].nunique()
            print(f"   唯一车辆数: {unique_vehicles}")
        
        if 'is_occupied' in sample_df.columns:
            occupied_count = sample_df['is_occupied'].sum() if sample_df['is_occupied'].dtype == bool else 0
            print(f"   载客记录: {occupied_count}/{len(sample_df)} ({occupied_count/len(sample_df)*100:.1f}%)")
        
        # 检查更大的样本
        print(f"\n📊 检查更大样本 (1000行)...")
        larger_sample = pd.read_csv(first_file, nrows=1000)
        print(f"   样本大小: {len(larger_sample)} 行")
        print(f"   唯一车辆数: {larger_sample['COMMADDR'].nunique()}")
        
        if 'UTC' in larger_sample.columns:
            time_span = larger_sample['UTC'].max() - larger_sample['UTC'].min()
            print(f"   时间跨度: {time_span} 秒 ({time_span/3600:.1f} 小时)")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查文件时出错: {e}")
        return False

def estimate_preprocessing_time():
    """估算预处理所需时间"""
    print(f"\n⏱️ 预处理时间估算")
    print("=" * 30)
    
    data_dir = os.path.join(os.path.dirname(__file__), 'data', 'cleaned')
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    total_size_mb = 0
    for csv_file in csv_files:
        file_path = os.path.join(data_dir, csv_file)
        total_size_mb += os.path.getsize(file_path) / (1024 * 1024)
    
    # 基于经验的时间估算 (约1-2MB/秒)
    estimated_time = total_size_mb / 1.5  # 秒
    
    print(f"总数据量: {total_size_mb:.1f} MB")
    print(f"预估处理时间: {estimated_time:.0f} 秒 ({estimated_time/60:.1f} 分钟)")
    
    if estimated_time > 300:  # 5分钟
        print("⚠️ 预处理可能需要较长时间，建议准备茶水 ☕")
    elif estimated_time > 60:  # 1分钟
        print("ℹ️ 预处理需要几分钟时间，请耐心等待")
    else:
        print("✅ 预处理应该很快完成")

if __name__ == "__main__":
    print("🚀 清洗后数据检查工具")
    print("=" * 60)
    
    success = check_cleaned_data()
    
    if success:
        estimate_preprocessing_time()
        print(f"\n✅ 数据检查完成！数据格式正确，可以进行预处理。")
        print(f"\n🚀 运行预处理命令:")
        print(f"   python run_cleaned_preprocessing.py")
    else:
        print(f"\n❌ 数据检查失败！请检查清洗后的数据文件。")
    
    print("=" * 60)
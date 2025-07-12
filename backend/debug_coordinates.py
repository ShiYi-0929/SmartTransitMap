#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试坐标数据脚本
"""

import pandas as pd
import os

def debug_coordinates():
    """调试坐标数据"""
    
    # 检查预处理数据
    data_dir = "backend/detect/traffic_visualization/data/processed"
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.endswith('.parquet')]
        if files:
            # 读取第一个文件的样本数据
            file_path = os.path.join(data_dir, files[0])
            df = pd.read_parquet(file_path)
            
            print(f"📁 预处理数据文件: {files[0]}")
            print(f"📊 总记录数: {len(df)}")
            print(f"📋 列名: {list(df.columns)}")
            
            # 检查前几行数据
            print("\n🔍 前5行原始数据:")
            print(df[['LAT', 'LON', 'UTC', 'COMMADDR']].head())
            
            # 检查坐标范围
            lat_min, lat_max = df['LAT'].min(), df['LAT'].max()
            lon_min, lon_max = df['LON'].min(), df['LON'].max()
            
            print(f"\n📍 原始坐标范围:")
            print(f"   LAT: {lat_min} ~ {lat_max}")
            print(f"   LON: {lon_min} ~ {lon_max}")
            
            # 测试不同的转换方法
            print(f"\n🧮 坐标转换测试:")
            
            # 方法1: 除以1e5 (100,000)
            lat_1e5 = df['LAT'].iloc[0] / 1e5
            lon_1e5 = df['LON'].iloc[0] / 1e5
            print(f"   除以1e5:  LAT={lat_1e5:.6f}, LON={lon_1e5:.6f}")
            
            # 方法2: 除以1e6 (1,000,000)  
            lat_1e6 = df['LAT'].iloc[0] / 1e6
            lon_1e6 = df['LON'].iloc[0] / 1e6
            print(f"   除以1e6:  LAT={lat_1e6:.6f}, LON={lon_1e6:.6f}")
            
            # 济南市的大致坐标范围
            print(f"\n🏢 济南市坐标范围参考:")
            print(f"   纬度: 36.40 ~ 36.90")
            print(f"   经度: 116.80 ~ 117.50")
            
            # 判断哪个更合理
            if 36.40 <= lat_1e5 <= 36.90 and 116.80 <= lon_1e5 <= 117.50:
                print(f"✅ 除以1e5的结果在济南市范围内")
            else:
                print(f"❌ 除以1e5的结果不在济南市范围内")
                
            if 36.40 <= lat_1e6 <= 36.90 and 116.80 <= lon_1e6 <= 117.50:
                print(f"✅ 除以1e6的结果在济南市范围内")
            else:
                print(f"❌ 除以1e6的结果不在济南市范围内")
                
            return True
    
    # 检查清洗数据
    cleaned_dir = "backend/detect/traffic_visualization/data/cleaned"
    if os.path.exists(cleaned_dir):
        files = [f for f in os.listdir(cleaned_dir) if f.endswith('.csv')]
        if files:
            file_path = os.path.join(cleaned_dir, files[0])
            df = pd.read_csv(file_path, nrows=5)
            
            print(f"\n📁 清洗数据文件: {files[0]}")
            print(f"📋 列名: {list(df.columns)}")
            print("\n🔍 前5行清洗数据:")
            print(df)
            
            return True
    
    print("❌ 未找到数据文件")
    return False

if __name__ == "__main__":
    debug_coordinates()
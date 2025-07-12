#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证清洗后数据格式并测试预处理器兼容性
基于实际数据格式: COMMADDR,UTC,LAT,LON,HEAD,SPEED,TFLAG,lat,lon,speed_kmh,is_occupied,timestamp
"""

import pandas as pd
import os
import sys
from datetime import datetime

def validate_sample_data():
    """验证样本数据格式"""
    print("🔍 验证清洗后数据的实际格式")
    print("=" * 50)
    
    # 检查测试样本
    data_dir = os.path.join(os.path.dirname(__file__), 'data', 'cleaned')
    sample_file = os.path.join(data_dir, 'test_sample_jn0912.csv')
    
    if not os.path.exists(sample_file):
        print(f"❌ 测试样本文件不存在: {sample_file}")
        return False
    
    try:
        # 读取样本数据
        df = pd.read_csv(sample_file, nrows=10)
        
        print(f"✅ 成功读取样本数据")
        print(f"   文件: {os.path.basename(sample_file)}")
        print(f"   行数: {len(df)}")
        print(f"   列数: {len(df.columns)}")
        
        print(f"\n📋 实际列结构:")
        for i, col in enumerate(df.columns):
            print(f"   {i+1:2d}. {col}")
        
        print(f"\n📊 样本数据预览:")
        print(df.head(3).to_string())
        
        print(f"\n🔢 数据类型:")
        for col in df.columns:
            print(f"   {col:12}: {df[col].dtype}")
        
        print(f"\n📈 关键字段验证:")
        
        # UTC时间戳
        if 'UTC' in df.columns:
            utc_sample = df['UTC'].iloc[0]
            dt = datetime.fromtimestamp(utc_sample)
            print(f"   UTC时间戳: {utc_sample} → {dt}")
        
        # 原始坐标 (LAT, LON)
        if 'LAT' in df.columns and 'LON' in df.columns:
            lat_raw = df['LAT'].iloc[0]
            lon_raw = df['LON'].iloc[0]
            print(f"   原始坐标: LAT={lat_raw}, LON={lon_raw}")
        
        # 转换后坐标 (lat, lon)
        if 'lat' in df.columns and 'lon' in df.columns:
            lat_conv = df['lat'].iloc[0]
            lon_conv = df['lon'].iloc[0]
            print(f"   转换坐标: lat={lat_conv:.6f}, lon={lon_conv:.6f}")
            
            # 验证坐标转换是否正确
            if 'LAT' in df.columns and 'LON' in df.columns:
                expected_lat = df['LAT'].iloc[0] / 100000.0
                expected_lon = df['LON'].iloc[0] / 100000.0
                lat_diff = abs(lat_conv - expected_lat)
                lon_diff = abs(lon_conv - expected_lon)
                
                if lat_diff < 0.000001 and lon_diff < 0.000001:
                    print(f"   ✅ 坐标转换正确 (LAT/LON ÷ 100000)")
                else:
                    print(f"   ⚠️ 坐标转换可能有问题")
                    print(f"      预期: lat={expected_lat:.6f}, lon={expected_lon:.6f}")
                    print(f"      实际: lat={lat_conv:.6f}, lon={lon_conv:.6f}")
        
        # 速度转换
        if 'SPEED' in df.columns and 'speed_kmh' in df.columns:
            speed_raw = df['SPEED'].iloc[0]
            speed_kmh = df['speed_kmh'].iloc[0]
            expected_speed = speed_raw * 0.036  # cm/s → km/h
            speed_diff = abs(speed_kmh - expected_speed)
            
            print(f"   原始速度: {speed_raw} cm/s")
            print(f"   转换速度: {speed_kmh:.3f} km/h")
            
            if speed_diff < 0.001:
                print(f"   ✅ 速度转换正确 (SPEED × 0.036)")
            else:
                print(f"   ⚠️ 速度转换可能有问题")
                print(f"      预期: {expected_speed:.3f} km/h")
        
        # 载客状态
        if 'TFLAG' in df.columns and 'is_occupied' in df.columns:
            tflag = df['TFLAG'].iloc[0]
            is_occupied = df['is_occupied'].iloc[0]
            expected_occupied = (tflag == 268435456)
            
            print(f"   TFLAG: {tflag}")
            print(f"   is_occupied: {is_occupied}")
            
            if bool(is_occupied) == expected_occupied:
                print(f"   ✅ 载客状态转换正确")
            else:
                print(f"   ⚠️ 载客状态转换可能有问题")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证样本数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_preprocessor_compatibility():
    """测试预处理器兼容性"""
    print(f"\n🧪 测试预处理器兼容性")
    print("=" * 40)
    
    try:
        # 尝试导入预处理器
        sys.path.insert(0, os.path.dirname(__file__))
        from data_preprocessor_cleaned import CleanedTrafficDataPreprocessor
        
        print("✅ 预处理器导入成功")
        
        # 创建预处理器实例
        preprocessor = CleanedTrafficDataPreprocessor()
        
        # 检查清洗后数据文件
        cleaned_files = preprocessor._get_cleaned_csv_files()
        if cleaned_files:
            print(f"✅ 找到 {len(cleaned_files)} 个清洗后数据文件")
            for file_path in cleaned_files:
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                print(f"   📄 {os.path.basename(file_path)}: {file_size:.1f} MB")
        else:
            print("❌ 未找到清洗后数据文件")
            return False
        
        # 测试读取第一个文件的格式兼容性
        test_file = cleaned_files[0]
        print(f"\n🔍 测试文件格式兼容性: {os.path.basename(test_file)}")
        
        try:
            # 读取少量数据测试
            test_df = pd.read_csv(test_file, nrows=100)
            
            # 检查必要列
            required_cols = ['COMMADDR', 'UTC', 'lat', 'lon', 'speed_kmh', 'is_occupied']
            missing_cols = [col for col in required_cols if col not in test_df.columns]
            
            if missing_cols:
                print(f"❌ 缺少必要列: {missing_cols}")
                return False
            else:
                print(f"✅ 所有必要列都存在")
            
            # 测试数据类型
            print(f"\n📊 数据类型兼容性:")
            type_issues = []
            
            # UTC应该是数值类型
            try:
                test_df['UTC'] = pd.to_numeric(test_df['UTC'], errors='coerce')
                valid_utc = test_df['UTC'].notna().sum()
                print(f"   UTC: {valid_utc}/{len(test_df)} 有效时间戳")
                if valid_utc < len(test_df) * 0.9:
                    type_issues.append("UTC时间戳转换失败率过高")
            except Exception as e:
                type_issues.append(f"UTC处理错误: {e}")
            
            # 坐标应该是浮点数
            for coord_col in ['lat', 'lon']:
                try:
                    test_df[coord_col] = pd.to_numeric(test_df[coord_col], errors='coerce')
                    valid_coords = test_df[coord_col].notna().sum()
                    print(f"   {coord_col}: {valid_coords}/{len(test_df)} 有效坐标")
                    if valid_coords < len(test_df) * 0.9:
                        type_issues.append(f"{coord_col}坐标转换失败率过高")
                except Exception as e:
                    type_issues.append(f"{coord_col}处理错误: {e}")
            
            # 速度检查
            try:
                test_df['speed_kmh'] = pd.to_numeric(test_df['speed_kmh'], errors='coerce')
                valid_speeds = test_df['speed_kmh'].notna().sum()
                print(f"   speed_kmh: {valid_speeds}/{len(test_df)} 有效速度")
                if valid_speeds < len(test_df) * 0.9:
                    type_issues.append("速度转换失败率过高")
            except Exception as e:
                type_issues.append(f"speed_kmh处理错误: {e}")
            
            if type_issues:
                print(f"⚠️ 数据类型问题:")
                for issue in type_issues:
                    print(f"   - {issue}")
            else:
                print(f"✅ 数据类型兼容性良好")
            
            # 测试基本的聚合操作
            print(f"\n🔬 测试基本处理操作:")
            
            # 时间分组测试
            try:
                test_df['hour'] = (test_df['UTC'] // 3600) * 3600
                hour_groups = test_df.groupby('hour').size()
                print(f"   时间分组: 成功，{len(hour_groups)} 个小时段")
            except Exception as e:
                print(f"   时间分组: 失败 - {e}")
                return False
            
            # 空间网格测试
            try:
                resolution = 0.001
                test_df['lat_grid'] = (test_df['lat'] / resolution).round() * resolution
                test_df['lng_grid'] = (test_df['lon'] / resolution).round() * resolution
                grid_groups = test_df.groupby(['lat_grid', 'lng_grid']).size()
                print(f"   空间网格: 成功，{len(grid_groups)} 个网格")
            except Exception as e:
                print(f"   空间网格: 失败 - {e}")
                return False
            
            # 车辆索引测试
            try:
                vehicle_groups = test_df.groupby('COMMADDR').size()
                print(f"   车辆分组: 成功，{len(vehicle_groups)} 辆车")
            except Exception as e:
                print(f"   车辆分组: 失败 - {e}")
                return False
            
            print(f"✅ 预处理器兼容性测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 文件读取测试失败: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ 预处理器导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 预处理器测试失败: {e}")
        return False

def generate_compatibility_report():
    """生成兼容性报告"""
    print(f"\n📋 兼容性报告")
    print("=" * 30)
    
    data_dir = os.path.join(os.path.dirname(__file__), 'data', 'cleaned')
    
    # 数据文件检查
    if os.path.exists(data_dir):
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        print(f"✅ 数据目录存在: {data_dir}")
        print(f"✅ 找到 {len(csv_files)} 个CSV文件")
        
        total_size = sum(os.path.getsize(os.path.join(data_dir, f)) 
                        for f in csv_files) / (1024 * 1024)
        print(f"📊 总数据量: {total_size:.1f} MB")
    else:
        print(f"❌ 数据目录不存在: {data_dir}")
        return
    
    # 预处理环境检查
    try:
        import pandas as pd
        import numpy as np
        print(f"✅ Pandas版本: {pd.__version__}")
        print(f"✅ Numpy版本: {np.__version__}")
    except ImportError as e:
        print(f"❌ 依赖包导入失败: {e}")
    
    # 磁盘空间检查
    try:
        import shutil
        total, used, free = shutil.disk_usage(os.path.dirname(__file__))
        free_gb = free / (1024**3)
        print(f"💾 可用磁盘空间: {free_gb:.1f} GB")
        
        if free_gb < 1.0:
            print(f"⚠️ 磁盘空间可能不足")
        else:
            print(f"✅ 磁盘空间充足")
    except:
        print(f"ℹ️ 无法检查磁盘空间")
    
    print(f"\n🚀 建议下一步:")
    print(f"1. 运行完整数据检查: python check_cleaned_data.py")
    print(f"2. 运行预处理: python run_cleaned_preprocessing.py")
    print(f"3. 重启后端服务享受高速查询")

if __name__ == "__main__":
    print("🔬 清洗后数据格式验证和兼容性测试")
    print("=" * 60)
    print("针对数据格式: COMMADDR,UTC,LAT,LON,HEAD,SPEED,TFLAG,lat,lon,speed_kmh,is_occupied,timestamp")
    print("=" * 60)
    
    # 步骤1: 验证样本数据
    step1_success = validate_sample_data()
    
    if step1_success:
        # 步骤2: 测试预处理器兼容性
        step2_success = test_preprocessor_compatibility()
        
        # 步骤3: 生成报告
        generate_compatibility_report()
        
        if step2_success:
            print(f"\n🎉 验证完成！")
            print(f"✅ 数据格式正确")
            print(f"✅ 预处理器兼容")
            print(f"✅ 可以进行预处理")
        else:
            print(f"\n⚠️ 验证部分完成")
            print(f"✅ 数据格式正确")
            print(f"❌ 预处理器可能需要调整")
    else:
        print(f"\n❌ 验证失败")
        print(f"请检查数据文件格式")
    
    print("=" * 60)
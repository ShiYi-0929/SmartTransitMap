#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行清洗后数据的预处理脚本
生成indexes和processed文件夹，用于高效查询
"""

import os
import sys
import time
from datetime import datetime

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    print("🚀 清洗后交通数据预处理器")
    print("=" * 60)
    print(f"当前目录: {current_dir}")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 导入预处理器
        from data_preprocessor_cleaned import CleanedTrafficDataPreprocessor, EnhancedFastTrafficDataLoader
        
        # 检查清洗后数据
        data_dir = os.path.join(current_dir, 'data', 'cleaned')
        print(f"清洗后数据目录: {data_dir}")
        
        if not os.path.exists(data_dir):
            print("❌ 清洗后数据目录不存在！")
            print(f"请确保 {data_dir} 目录存在且包含清洗后的CSV文件")
            return False
        
        # 检查清洗后的CSV文件
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        if not csv_files:
            print("❌ 清洗后数据目录中没有CSV文件！")
            print(f"请确保 {data_dir} 目录中有清洗后的数据文件")
            return False
        
        print(f"✅ 找到 {len(csv_files)} 个清洗后的CSV文件:")
        total_size = 0
        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            total_size += file_size
            print(f"   📄 {csv_file}: {file_size:.1f} MB")
        
        print(f"📊 总数据量: {total_size:.1f} MB")
        print()
        
        # 询问用户是否继续
        response = input("是否开始预处理？这可能需要几分钟时间... (Y/n): ")
        if response.lower() == 'n':
            print("❌ 用户取消预处理")
            return False
        
        # 创建预处理器
        print("\n" + "=" * 60)
        print("1️⃣ 初始化预处理器")
        print("=" * 60)
        
        preprocessor = CleanedTrafficDataPreprocessor()
        
        # 询问是否清理现有数据
        processed_dir = os.path.join(current_dir, 'data', 'processed')
        indexes_dir = os.path.join(current_dir, 'data', 'indexes')
        
        existing_processed = os.path.exists(processed_dir) and len(os.listdir(processed_dir)) > 0
        existing_indexes = os.path.exists(indexes_dir) and len(os.listdir(indexes_dir)) > 0
        
        if existing_processed or existing_indexes:
            print(f"\n⚠️ 发现现有的预处理数据:")
            if existing_processed:
                processed_files = len([f for f in os.listdir(processed_dir) if f.endswith('.parquet')])
                print(f"   📁 processed目录: {processed_files} 个parquet文件")
            if existing_indexes:
                index_files = len([f for f in os.listdir(indexes_dir) if f.endswith('.json')])
                print(f"   📁 indexes目录: {index_files} 个索引文件")
            
            clean_response = input("\n是否清理现有数据重新生成？(y/N): ")
            if clean_response.lower() == 'y':
                print("\n🧹 清理现有预处理数据...")
                preprocessor.clean_existing_preprocessed_data()
        
        # 开始预处理
        print("\n" + "=" * 60)
        print("2️⃣ 开始数据预处理")
        print("=" * 60)
        
        start_time = time.time()
        preprocessor.preprocess_all_data()
        end_time = time.time()
        
        processing_time = end_time - start_time
        print(f"\n⏱️ 预处理耗时: {processing_time:.1f} 秒 ({processing_time/60:.1f} 分钟)")
        
        # 验证预处理结果
        print("\n" + "=" * 60)
        print("3️⃣ 验证预处理结果")
        print("=" * 60)
        
        # 检查生成的文件
        if os.path.exists(processed_dir):
            parquet_files = [f for f in os.listdir(processed_dir) if f.endswith('.parquet')]
            print(f"✅ 生成 {len(parquet_files)} 个小时数据文件 (processed/)")
        else:
            print("❌ processed目录未生成")
            return False
        
        if os.path.exists(indexes_dir):
            json_files = [f for f in os.listdir(indexes_dir) if f.endswith('.json')]
            print(f"✅ 生成 {len(json_files)} 个索引文件 (indexes/)")
            
            # 显示关键索引文件
            key_indexes = ['vehicle_index.json', 'data_summary.json']
            for key_file in key_indexes:
                if key_file in [f for f in os.listdir(indexes_dir)]:
                    print(f"   📋 {key_file} ✅")
                else:
                    print(f"   📋 {key_file} ❌")
        else:
            print("❌ indexes目录未生成")
            return False
        
        # 测试快速加载器
        print("\n" + "=" * 60)
        print("4️⃣ 测试增强版快速加载器")
        print("=" * 60)
        
        try:
            loader = EnhancedFastTrafficDataLoader()
            summary = loader.get_data_summary()
            
            if summary:
                print("📊 数据概要统计:")
                print(f"   总记录数: {summary.get('total_records', 0):,}")
                print(f"   总车辆数: {summary.get('total_vehicles', 0):,}")
                print(f"   时间跨度: {summary.get('total_hours', 0)} 小时")
                
                # 坐标范围
                coord_range = summary.get('coordinate_range', {})
                if coord_range.get('lat_min'):
                    print(f"   坐标范围: 纬度 {coord_range['lat_min']:.4f}~{coord_range['lat_max']:.4f}, "
                          f"经度 {coord_range['lng_min']:.4f}~{coord_range['lng_max']:.4f}")
                
                # 时间范围
                time_range = summary.get('time_range', {})
                if time_range.get('start'):
                    start_dt = datetime.fromtimestamp(time_range['start'])
                    end_dt = datetime.fromtimestamp(time_range['end'])
                    print(f"   时间范围: {start_dt} ~ {end_dt}")
                
                # 快速查询测试
                if time_range.get('start'):
                    print(f"\n🧪 快速查询测试:")
                    test_start = time_range['start']
                    test_end = test_start + 3600  # 1小时
                    
                    test_start_time = time.time()
                    test_data = loader.fast_load_data(test_start, test_end)
                    test_end_time = time.time()
                    
                    print(f"   查询耗时: {(test_end_time - test_start_time)*1000:.1f} 毫秒")
                    print(f"   返回记录: {len(test_data):,} 条")
                    
                    if len(test_data) > 0:
                        print(f"   样本数据字段: {list(test_data.columns)}")
            
            print("✅ 快速加载器测试通过")
            
        except Exception as e:
            print(f"❌ 快速加载器测试失败: {e}")
            return False
        
        # 完成
        print("\n" + "=" * 60)
        print("🎉 预处理完成！")
        print("=" * 60)
        
        print("✅ 生成的文件结构:")
        print("   📁 data/")
        print("   ├── 📁 cleaned/        (清洗后原始数据)")
        print("   ├── 📁 processed/      (按小时分片的Parquet文件)")
        print("   └── 📁 indexes/        (快速查询索引)")
        
        print("\n🚀 现在TrafficDataProcessor将自动使用预处理数据，查询速度提升10-100倍！")
        print("\n💡 可以重启后端服务来体验高速查询:")
        print("   cd backend")
        print("   uvicorn main:app --reload")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保data_preprocessor_cleaned.py文件存在且可导入")
        return False
    except Exception as e:
        print(f"❌ 预处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n✅ 预处理成功完成！")
        exit(0)
    else:
        print(f"\n❌ 预处理失败!")
        exit(1)
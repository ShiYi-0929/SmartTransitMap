#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版交通数据清洗脚本
基于数据分析结果修正了坐标转换和时间范围问题
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

class FixedTrafficDataCleaner:
    """修正版交通数据清洗器"""
    
    def __init__(self, data_dir=None):
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        else:
            self.data_dir = data_dir
        
        # 创建清洗后数据的输出目录
        self.cleaned_dir = os.path.join(self.data_dir, 'cleaned')
        os.makedirs(self.cleaned_dir, exist_ok=True)
        
        print(f"数据目录: {self.data_dir}")
        print(f"清洗后数据目录: {self.cleaned_dir}")
        
        # 基于分析结果的修正参数
        self.coordinate_divisor = 100000.0  # 修正：应该除以100,000
        self.jinan_lat_range = (36.0, 37.0)  # 济南市纬度范围
        self.jinan_lon_range = (116.5, 117.5)  # 济南市经度范围
        
        # 修正时间范围 - 基于实际数据分析
        # 数据显示是2013-09-11开始，比预期早一天
        self.start_time = 1378915200  # 2013-09-11 16:00:00 UTC (调整后)
        self.end_time = 1379548800    # 2013-09-19 00:00:00 UTC
    
    def test_small_sample(self, filename, sample_size=1000):
        """测试小样本数据清洗效果"""
        print(f"="*60)
        print(f"测试小样本清洗: {filename} (前{sample_size}行)")
        print(f"="*60)
        
        input_path = os.path.join(self.data_dir, filename)
        
        try:
            # 读取小样本
            df_sample = pd.read_csv(input_path, nrows=sample_size)
            print(f"读取样本数据: {len(df_sample)} 行")
            
            # 应用清洗
            cleaned_df = self.clean_data_chunk(df_sample)
            
            retention_rate = len(cleaned_df) / len(df_sample) * 100
            print(f"\n样本清洗结果:")
            print(f"  原始: {len(df_sample)} 行")
            print(f"  清洗后: {len(cleaned_df)} 行")
            print(f"  保留率: {retention_rate:.1f}%")
            
            if len(cleaned_df) > 0:
                print(f"\n清洗后数据预览:")
                print(cleaned_df[['COMMADDR', 'UTC', 'lat', 'lon', 'speed_kmh', 'is_occupied']].head())
                
                # 保存小样本测试结果
                test_output = os.path.join(self.cleaned_dir, f"test_sample_{filename}")
                cleaned_df.to_csv(test_output, index=False)
                print(f"\n测试样本已保存到: {test_output}")
            else:
                print("❌ 清洗后无数据，需要进一步调整策略")
            
            return len(cleaned_df) > 0
            
        except Exception as e:
            print(f"测试失败: {e}")
            return False
    
    def process_all_files(self):
        """处理所有jn开头的CSV文件"""
        print("="*60)
        print("开始批量数据清洗处理 (修正版)")
        print("="*60)
        
        # 找到所有需要处理的文件
        files_to_process = []
        for filename in os.listdir(self.data_dir):
            if filename.startswith('jn09') and filename.endswith('.csv'):
                if any(day in filename for day in ['12', '13', '14', '15', '16', '17', '18']):
                    files_to_process.append(filename)
        
        files_to_process.sort()
        print(f"找到 {len(files_to_process)} 个文件需要处理:")
        for filename in files_to_process:
            print(f"  - {filename}")
        
        # 先测试第一个文件的小样本
        if files_to_process:
            print(f"\n先测试第一个文件的小样本...")
            test_success = self.test_small_sample(files_to_process[0], 1000)
            
            if not test_success:
                print("❌ 小样本测试失败，请检查清洗策略")
                return
            
            print("✅ 小样本测试成功，继续处理完整文件...")
        
        # 逐个处理文件
        total_stats = {
            'total_files': len(files_to_process),
            'processed_files': 0,
            'total_original_records': 0,
            'total_cleaned_records': 0,
            'total_removed_records': 0
        }
        
        for filename in files_to_process:
            print(f"\n{'='*60}")
            print(f"正在处理: {filename}")
            print(f"{'='*60}")
            
            file_stats = self.process_single_file(filename)
            if file_stats:
                total_stats['processed_files'] += 1
                total_stats['total_original_records'] += file_stats['original_records']
                total_stats['total_cleaned_records'] += file_stats['cleaned_records']
                total_stats['total_removed_records'] += file_stats['removed_records']
        
        # 输出总体统计
        self.print_summary_stats(total_stats)
    
    def process_single_file(self, filename):
        """处理单个文件"""
        input_path = os.path.join(self.data_dir, filename)
        output_path = os.path.join(self.cleaned_dir, f"cleaned_{filename}")
        
        try:
            print(f"加载文件: {filename}")
            print(f"文件大小: {os.path.getsize(input_path) / (1024*1024):.1f} MB")
            
            # 分块读取大文件
            chunk_size = 50000  # 5万行一批（减小以提高稳定性）
            cleaned_chunks = []
            total_original = 0
            total_processed = 0
            
            print("开始分块处理...")
            
            for chunk_idx, chunk in enumerate(pd.read_csv(input_path, chunksize=chunk_size)):
                print(f"  处理第 {chunk_idx + 1} 批数据，共 {len(chunk)} 行...")
                
                total_original += len(chunk)
                
                # 清洗当前块
                cleaned_chunk = self.clean_data_chunk(chunk)
                
                if not cleaned_chunk.empty:
                    cleaned_chunks.append(cleaned_chunk)
                    total_processed += len(cleaned_chunk)
                
                print(f"    批次 {chunk_idx + 1}: {len(chunk)} -> {len(cleaned_chunk)} 行 "
                      f"(保留率: {len(cleaned_chunk)/len(chunk)*100:.1f}%)")
            
            # 合并所有清洗后的数据块
            if cleaned_chunks:
                print("合并清洗后的数据...")
                final_df = pd.concat(cleaned_chunks, ignore_index=True)
                
                # 最终去重
                print("执行最终去重...")
                before_dedup = len(final_df)
                final_df = final_df.drop_duplicates(
                    subset=['COMMADDR', 'UTC', 'LAT', 'LON'], 
                    keep='first'
                )
                after_dedup = len(final_df)
                
                print(f"去重: {before_dedup} -> {after_dedup} 行")
                
                # 按车辆和时间排序
                print("最终排序...")
                final_df = final_df.sort_values(['COMMADDR', 'UTC'])
                
                # 保存清洗后的数据
                print(f"保存清洗后的数据到: {output_path}")
                final_df.to_csv(output_path, index=False)
                
                # 返回统计信息
                stats = {
                    'original_records': total_original,
                    'cleaned_records': len(final_df),
                    'removed_records': total_original - len(final_df),
                    'removal_rate': (total_original - len(final_df)) / total_original * 100
                }
                
                self.print_file_stats(filename, stats)
                return stats
            else:
                print("警告: 清洗后没有有效数据")
                return None
                
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def clean_data_chunk(self, chunk):
        """修正版数据块清洗"""
        try:
            original_count = len(chunk)
            
            # 1. 检查必要列是否存在
            required_columns = ['COMMADDR', 'UTC', 'LAT', 'LON', 'SPEED', 'TFLAG']
            missing_columns = [col for col in required_columns if col not in chunk.columns]
            
            if missing_columns:
                print(f"    警告: 缺少必要列: {missing_columns}")
                return pd.DataFrame()
            
            # 2. 处理缺失值
            before_na = len(chunk)
            chunk = chunk.dropna(subset=required_columns)
            after_na = len(chunk)
            
            if before_na != after_na:
                print(f"      移除缺失值: {before_na} -> {after_na} 行")
            
            if chunk.empty:
                return chunk
            
            # 3. 数据类型转换和验证
            try:
                # 确保数值列为数值类型
                chunk['UTC'] = pd.to_numeric(chunk['UTC'], errors='coerce')
                chunk['LAT'] = pd.to_numeric(chunk['LAT'], errors='coerce')
                chunk['LON'] = pd.to_numeric(chunk['LON'], errors='coerce')
                chunk['SPEED'] = pd.to_numeric(chunk['SPEED'], errors='coerce')
                chunk['TFLAG'] = pd.to_numeric(chunk['TFLAG'], errors='coerce')
                
                # 移除转换失败的行
                chunk = chunk.dropna(subset=['UTC', 'LAT', 'LON', 'SPEED', 'TFLAG'])
            except Exception as e:
                print(f"      数据类型转换失败: {e}")
                return pd.DataFrame()
            
            # 4. 修正的坐标数据处理
            print(f"    处理坐标数据 (修正版)...")
            
            # 修正的坐标转换：除以100,000而不是1,000,000
            chunk['lat'] = chunk['LAT'] / self.coordinate_divisor
            chunk['lon'] = chunk['LON'] / self.coordinate_divisor
            
            # 济南市坐标范围验证（使用修正后的范围）
            before_coord = len(chunk)
            chunk = chunk[
                (chunk['lat'] >= self.jinan_lat_range[0]) & (chunk['lat'] <= self.jinan_lat_range[1]) &
                (chunk['lon'] >= self.jinan_lon_range[0]) & (chunk['lon'] <= self.jinan_lon_range[1])
            ]
            after_coord = len(chunk)
            
            if before_coord != after_coord:
                print(f"      坐标范围过滤: {before_coord} -> {after_coord} 行")
            
            # 5. 修正的时间戳验证
            print(f"    验证时间戳 (修正版)...")
            
            before_time = len(chunk)
            chunk = chunk[
                (chunk['UTC'] >= self.start_time) & (chunk['UTC'] <= self.end_time)
            ]
            after_time = len(chunk)
            
            if before_time != after_time:
                print(f"      时间范围过滤: {before_time} -> {after_time} 行")
            
            # 6. 速度数据验证
            print(f"    验证速度数据...")
            
            # 速度转换 (cm/s -> km/h)
            chunk['speed_kmh'] = chunk['SPEED'] * 0.036
            
            before_speed = len(chunk)
            chunk = chunk[
                (chunk['speed_kmh'] >= 0) & (chunk['speed_kmh'] <= 150)  # 稍微放宽速度限制
            ]
            after_speed = len(chunk)
            
            if before_speed != after_speed:
                print(f"      速度范围过滤: {before_speed} -> {after_speed} 行")
            
            # 7. 载客状态处理
            chunk['is_occupied'] = chunk['TFLAG'] == 268435456
            
            # 8. 添加时间戳转换
            chunk['timestamp'] = pd.to_datetime(chunk['UTC'], unit='s')
            
            # 9. 移除明显的重复记录（在块内去重）
            before_dedup = len(chunk)
            chunk = chunk.drop_duplicates(
                subset=['COMMADDR', 'UTC', 'LAT', 'LON'], 
                keep='first'
            )
            after_dedup = len(chunk)
            
            if before_dedup != after_dedup:
                print(f"      块内去重: {before_dedup} -> {after_dedup} 行")
            
            retention_rate = len(chunk) / original_count * 100 if original_count > 0 else 0
            print(f"    清洗完成: {original_count} -> {len(chunk)} 行 "
                  f"(保留率: {retention_rate:.1f}%)")
            
            return chunk
            
        except Exception as e:
            print(f"    清洗数据块时出错: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def print_file_stats(self, filename, stats):
        """打印单个文件的统计信息"""
        print(f"\n文件 {filename} 清洗统计:")
        print(f"  原始记录数: {stats['original_records']:,}")
        print(f"  清洗后记录数: {stats['cleaned_records']:,}")
        print(f"  移除记录数: {stats['removed_records']:,}")
        print(f"  数据保留率: {100 - stats['removal_rate']:.1f}%")
        print(f"  数据移除率: {stats['removal_rate']:.1f}%")
    
    def print_summary_stats(self, total_stats):
        """打印总体统计信息"""
        print(f"\n{'='*60}")
        print("数据清洗总体统计 (修正版)")
        print(f"{'='*60}")
        print(f"处理文件数: {total_stats['processed_files']}/{total_stats['total_files']}")
        print(f"原始总记录数: {total_stats['total_original_records']:,}")
        print(f"清洗后总记录数: {total_stats['total_cleaned_records']:,}")
        print(f"移除总记录数: {total_stats['total_removed_records']:,}")
        
        if total_stats['total_original_records'] > 0:
            retention_rate = total_stats['total_cleaned_records'] / total_stats['total_original_records'] * 100
            print(f"总体数据保留率: {retention_rate:.1f}%")
            print(f"总体数据移除率: {100 - retention_rate:.1f}%")
        
        print(f"\n清洗后的文件保存在: {self.cleaned_dir}")
        print("="*60)

def main():
    """主函数"""
    print("济南交通数据清洗工具 (修正版)")
    print("修正了坐标转换和时间范围问题")
    print("="*60)
    
    # 创建数据清洗器
    cleaner = FixedTrafficDataCleaner()
    
    # 开始处理
    start_time = datetime.now()
    print(f"开始时间: {start_time}")
    
    try:
        cleaner.process_all_files()
        
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\n处理完成!")
        print(f"结束时间: {end_time}")
        print(f"总耗时: {duration}")
        
    except KeyboardInterrupt:
        print("\n用户中断处理")
    except Exception as e:
        print(f"\n处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
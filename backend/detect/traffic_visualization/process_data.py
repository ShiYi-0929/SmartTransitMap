import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class CSVAnalyzer:
    def __init__(self, data_folder='data'):
        self.data_folder = data_folder
        self.csv_files = []
        self.dataframes = {}
        
    def find_csv_files(self):
        """查找data文件夹中的所有CSV文件"""
        # 获取当前脚本的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"当前脚本目录: {current_dir}")
        
        # 尝试多种可能的路径
        possible_paths = [
            os.path.join(current_dir, self.data_folder),
            os.path.join(current_dir, '..', '..', '..', 'backend', 'detect', 'traffic_visualization', 'data'),
            os.path.join(current_dir, '..', 'data'),
            os.path.join(current_dir, '..', '..', 'data'),
            os.path.join(current_dir, '..', '..', '..', 'data'),
            self.data_folder  # 相对于运行目录
        ]
        
        # 检查哪个路径存在
        data_path = None
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            print(f"检查路径: {abs_path}")
            if os.path.exists(abs_path):
                data_path = abs_path
                print(f"找到data文件夹: {data_path}")
                break
        
        if data_path is None:
            print("错误: 找不到data文件夹")
            print("请确保data文件夹存在，或者修改路径")
            return []
        
        # 查找CSV文件
        csv_pattern = os.path.join(data_path, '*.csv')
        self.csv_files = glob.glob(csv_pattern)
        
        print(f"在 {data_path} 中找到 {len(self.csv_files)} 个CSV文件:")
        for file in self.csv_files:
            print(f"  - {os.path.basename(file)}")
        
        # 如果没有找到CSV文件，显示文件夹内容
        if len(self.csv_files) == 0:
            print(f"\n{data_path} 文件夹内容:")
            try:
                for item in os.listdir(data_path):
                    item_path = os.path.join(data_path, item)
                    if os.path.isfile(item_path):
                        print(f"  文件: {item}")
                    elif os.path.isdir(item_path):
                        print(f"  文件夹: {item}/")
            except Exception as e:
                print(f"  无法列出文件夹内容: {e}")
        
        return self.csv_files
    
    def get_file_info(self, file_path):
        """获取文件基本信息"""
        try:
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            print(f"\n文件: {os.path.basename(file_path)}")
            print(f"大小: {file_size_mb:.2f} MB")
            return file_size_mb
        except Exception as e:
            print(f"获取文件信息时出错: {e}")
            return 0
    
    def read_csv_sample(self, file_path, sample_size=1000):
        """读取CSV文件的样本数据"""
        try:
            filename = os.path.basename(file_path)
            print(f"\n正在分析文件: {filename}")
            
            # 先读取少量行来了解结构
            sample_df = pd.read_csv(file_path, nrows=sample_size)
            
            # 尝试读取全部数据获取总行数
            try:
                # 使用chunksize来处理大文件
                total_rows = 0
                chunk_size = 10000
                for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                    total_rows += len(chunk)
                
                print(f"总行数: {total_rows:,}")
            except:
                print("无法获取总行数（文件可能过大）")
                total_rows = "未知"
            
            return sample_df, total_rows
            
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")
            return None, 0
    
    def analyze_dataframe(self, df, filename, total_rows=None):
        """分析DataFrame的详细信息"""
        print(f"\n{'='*50}")
        print(f"文件分析报告: {filename}")
        print(f"{'='*50}")
        
        # 基本信息
        print(f"数据维度: {df.shape}")
        print(f"列数: {df.shape[1]}")
        if total_rows:
            print(f"总行数: {total_rows}")
        print(f"样本行数: {df.shape[0]}")
        
        # 列信息
        print(f"\n列名和数据类型:")
        for i, (col, dtype) in enumerate(zip(df.columns, df.dtypes)):
            print(f"  {i+1:2d}. {col:<30} ({dtype})")
        
        # 数据类型统计
        print(f"\n数据类型分布:")
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  {dtype}: {count} 列")
        
        # 缺失值统计
        print(f"\n缺失值统计:")
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            missing_percent = (missing_data / len(df)) * 100
            for col in missing_data[missing_data > 0].index:
                print(f"  {col}: {missing_data[col]} ({missing_percent[col]:.1f}%)")
        else:
            print("  无缺失值")
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(f"\n数值列统计 (前5行样本):")
            print(df[numeric_cols].describe())
        
        # 分类列统计
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            print(f"\n分类列信息:")
            for col in categorical_cols:
                unique_count = df[col].nunique()
                print(f"  {col}: {unique_count} 个唯一值")
                if unique_count <= 10:
                    print(f"    值: {list(df[col].unique())}")
        
        # 前几行数据预览
        print(f"\n前5行数据预览:")
        print(df.head())
        
        return {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': dict(df.dtypes),
            'missing_values': dict(missing_data),
            'numeric_columns': list(numeric_cols),
            'categorical_columns': list(categorical_cols),
            'total_rows': total_rows
        }
    
    def analyze_all_files(self, sample_size=1000):
        """分析所有CSV文件"""
        self.find_csv_files()
        
        if not self.csv_files:
            print("在data文件夹中没有找到CSV文件")
            return
        
        analysis_results = {}
        
        for file_path in self.csv_files:
            filename = os.path.basename(file_path)
            
            # 获取文件大小
            file_size = self.get_file_info(file_path)
            
            # 读取和分析数据
            df_sample, total_rows = self.read_csv_sample(file_path, sample_size)
            
            if df_sample is not None:
                analysis_results[filename] = self.analyze_dataframe(
                    df_sample, filename, total_rows
                )
                self.dataframes[filename] = df_sample
        
        # 生成总结报告
        self.generate_summary_report(analysis_results)
        
        return analysis_results
    
    def generate_summary_report(self, analysis_results):
        """生成总结报告"""
        print(f"\n{'='*60}")
        print("总结报告")
        print(f"{'='*60}")
        
        print(f"分析了 {len(analysis_results)} 个CSV文件:")
        
        for filename, info in analysis_results.items():
            print(f"\n{filename}:")
            print(f"  - 维度: {info['shape']}")
            print(f"  - 总行数: {info['total_rows']}")
            print(f"  - 数值列: {len(info['numeric_columns'])}")
            print(f"  - 分类列: {len(info['categorical_columns'])}")
            print(f"  - 缺失值: {sum(info['missing_values'].values())}")
    
    def load_specific_file(self, filename, chunk_size=None):
        """加载特定文件（支持分块加载）"""
        # 如果csv_files为空，先查找文件
        if not self.csv_files:
            self.find_csv_files()
        
        # 在找到的文件中搜索
        file_path = None
        for csv_file in self.csv_files:
            if os.path.basename(csv_file) == filename:
                file_path = csv_file
                break
        
        if file_path is None:
            print(f"文件不存在: {filename}")
            print(f"可用的文件: {[os.path.basename(f) for f in self.csv_files]}")
            return None
        
        try:
            if chunk_size:
                print(f"以分块方式加载 {filename} (chunk_size={chunk_size})")
                return pd.read_csv(file_path, chunksize=chunk_size)
            else:
                print(f"加载整个文件 {filename}")
                return pd.read_csv(file_path)
        except Exception as e:
            print(f"加载文件时出错: {e}")
            return None
    
    def process_large_file(self, filename, processing_function, chunk_size=10000):
        """处理大型CSV文件的通用方法"""
        # 如果csv_files为空，先查找文件
        if not self.csv_files:
            self.find_csv_files()
        
        # 在找到的文件中搜索
        file_path = None
        for csv_file in self.csv_files:
            if os.path.basename(csv_file) == filename:
                file_path = csv_file
                break
        
        if file_path is None:
            print(f"文件不存在: {filename}")
            print(f"可用的文件: {[os.path.basename(f) for f in self.csv_files]}")
            return None
        
        results = []
        chunk_count = 0
        
        try:
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                chunk_count += 1
                print(f"处理第 {chunk_count} 块数据...")
                
                # 应用处理函数
                result = processing_function(chunk)
                if result is not None:
                    results.append(result)
            
            print(f"处理完成，共处理 {chunk_count} 个数据块")
            return results
            
        except Exception as e:
            print(f"处理文件时出错: {e}")
            return None

# 使用示例
def main():
    # 创建分析器实例
    analyzer = CSVAnalyzer('data')
    
    # 分析所有CSV文件
    results = analyzer.analyze_all_files(sample_size=1000)
    
    # 如果需要加载特定文件进行进一步分析
    # df = analyzer.load_specific_file('jn0912.csv')
    
    # 如果文件太大，可以分块处理
    # def process_chunk(chunk):
    #     # 在这里定义你的处理逻辑
    #     return chunk.describe()
    # 
    # analyzer.process_large_file('jn0912.csv', process_chunk, chunk_size=5000)

if __name__ == "__main__":
    main()
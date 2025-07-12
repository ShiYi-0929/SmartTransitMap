import pandas as pd
import os
import joblib # 用于数据缓存
from tqdm import tqdm # 用于显示进度条，特别是处理大数据时
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TrafficDataCleaner:
    def __init__(self, raw_data_path, processed_data_path, cache_suffix='_cleaned.pkl'):
        """
        初始化数据清洗器。
        :param raw_data_path: 原始数据文件所在的目录。
        :param processed_data_path: 清洗后数据保存的目录。
        :param cache_suffix: 缓存文件的后缀名。
        """
        self.raw_data_dir = raw_data_path
        self.processed_data_dir = processed_data_path
        self.cache_suffix = cache_suffix
        
        # 确保处理后数据目录存在
        os.makedirs(self.processed_data_dir, exist_ok=True)
        
        self.df = None # 用于存储加载和清洗后的DataFrame

    def _load_raw_data(self, file_name):
        """
        从指定文件加载原始数据。
        假定原始数据是CSV格式。
        :param file_name: 原始数据文件名。
        :return: pandas DataFrame
        """
        file_path = os.path.join(self.raw_data_dir, file_name)
        logging.info(f"正在从 {file_path} 加载原始数据...")
        try:
            # 假设CSV文件以逗号分隔，且包含标题行
            df = pd.read_csv(file_path)
            logging.info(f"原始数据加载成功，共 {df.shape[0]} 行，{df.shape[1]} 列。")
            return df
        except FileNotFoundError:
            logging.error(f"错误：文件 {file_path} 未找到。请检查路径。")
            return None
        except pd.errors.EmptyDataError:
            logging.error(f"错误：文件 {file_path} 为空或没有可解析的数据。")
            return None
        except Exception as e:
            logging.error(f"加载数据时发生未知错误: {e}")
            return None

    def clean_data(self, raw_file_name):
        """
        执行数据清洗流程。
        :param raw_file_name: 原始数据文件名。
        :return: 清洗后的 pandas DataFrame
        """
        # 构建缓存文件路径
        base_name = os.path.splitext(raw_file_name)[0] # 获取不带扩展名的文件名
        cache_file_path = os.path.join(self.processed_data_dir, base_name + self.cache_suffix)

        # 检查是否存在缓存文件
        if os.path.exists(cache_file_path):
            logging.info(f"检测到缓存文件：{cache_file_path}。正在加载处理后的数据...")
            self.df = joblib.load(cache_file_path)
            logging.info(f"已从缓存加载数据，共 {self.df.shape[0]} 行。")
            return self.df

        logging.info(f"未检测到 {raw_file_name} 的缓存文件，开始进行数据清洗...")
        self.df = self._load_raw_data(raw_file_name)

        if self.df is None:
            logging.error(f"数据加载失败，跳过 {raw_file_name} 的清洗。")
            return None # 数据加载失败，直接返回

        initial_rows = self.df.shape[0]

        # 1. 重命名列（如果需要，请根据你的实际列名进行调整）
        # self.df.rename(columns={'latitude_field': 'LAT', 'longitude_field': 'LON'}, inplace=True)
        
        # 2. 数据类型转换
        logging.info("正在进行数据类型转换...")
        # 强制转换为数值类型，无法转换的变为NaN
        for col in ['LAT', 'LON', 'SPEED', 'HEAD']: 
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            else:
                logging.warning(f"警告：列 '{col}' 不存在于数据中，跳过类型转换。")

        # 将UTC转换为datetime对象，并处理转换错误
        if 'UTC' in self.df.columns:
            # 假设UTC是Unix时间戳（秒）
            self.df['UTC'] = pd.to_datetime(self.df['UTC'], errors='coerce', unit='s') 
        else:
            logging.warning("警告：列 'UTC' 不存在于数据中，时间戳处理跳过。")
            
        # 确保COMMADDR是字符串类型，防止后续合并或分组问题
        if 'COMMADDR' in self.df.columns:
            self.df['COMMADDR'] = self.df['COMMADDR'].astype(str)
        else:
            logging.warning("警告：列 'COMMADDR' 不存在于数据中，车辆ID处理跳过。")

        # --- 处理经纬度放大问题 ---
        logging.info("正在处理经纬度放大问题...")
        if 'LAT' in self.df.columns:
            # 假设 LAT 乘以了 10^6
            self.df['LAT'] = self.df['LAT'] / 10**6 
        else:
            logging.warning("警告：LAT 列不存在，无法处理经纬度放大。")
            
        if 'LON' in self.df.columns:
            # 假设 LON 乘以了 10^5
            self.df['LON'] = self.df['LON'] / 10**5
        else:
            logging.warning("警告：LON 列不存在，无法处理经纬度放大。")
        # --- 经纬度放大问题处理结束 ---

        # --- 处理 SPEED 单位转换 ---
        logging.info("正在将 SPEED 从 cm/s 转换为 km/h...")
        if 'SPEED' in self.df.columns:
            # 1 cm/s = 0.036 km/h
            self.df['SPEED_KMPH'] = self.df['SPEED'] * 0.036
            logging.info("SPEED 转换完成，新列为 'SPEED_KMPH'。")
        else:
            logging.warning("警告：SPEED 列不存在，跳过速度单位转换。")


        #处理 TFLAG 列
        logging.info("正在处理 TFLAG 列，转换为载客/空车状态...")
        if 'TFLAG' in self.df.columns:
            # 将 TFLAG 转换为整数类型，以便进行准确比较
            self.df['TFLAG'] = pd.to_numeric(self.df['TFLAG'], errors='coerce').fillna(-1).astype(int)
            
            # 定义映射关系
            # 假设 268435456 为载客，0 为空车
            # 请根据实际情况调整这些值！
            tflag_mapping = {
                268435456: '载客',
                0: '空车'
            }
            # 使用 apply 来进行转换，对于未知的 TFLAG 值，设置为 '未知'
            self.df['CAR_STATUS'] = self.df['TFLAG'].apply(lambda x: tflag_mapping.get(x, '未知'))
            logging.info("TFLAG 转换完成，新列为 'CAR_STATUS'。")
            
            # 可以选择删除原始的 TFLAG 列或保留
            # self.df.drop('TFLAG', axis=1, inplace=True)
        else:
            logging.warning("警告：TFLAG 列不存在，跳过载客状态处理。")
        # --- TFLAG 列处理结束 ---


        # 3. 处理缺失值 (核心字段)
        critical_columns = ['LAT', 'LON', 'UTC', 'COMMADDR'] 
        
        logging.info("正在处理关键字段缺失值...")
        rows_before_dropna = self.df.shape[0]
        
        existing_critical_columns = [col for col in critical_columns if col in self.df.columns]
        if not existing_critical_columns:
            logging.error("错误：没有找到任何关键列（LAT, LON, UTC, COMMADDR）来检查缺失值。请检查列名。")
            return None 

        self.df.dropna(subset=existing_critical_columns, inplace=True)
        dropped_rows_na = rows_before_dropna - self.df.shape[0]
        logging.info(f"因关键字段缺失删除了 {dropped_rows_na} 行数据。当前数据量：{self.df.shape[0]} 行。")

        # 4. 处理重复样本
        logging.info("正在处理重复样本...")
        rows_before_deduplicate = self.df.shape[0]
        
        # 完全重复的行
        self.df.drop_duplicates(inplace=True)
        dropped_rows_full_dup = rows_before_deduplicate - self.df.shape[0]
        logging.info(f"因完全重复删除了 {dropped_rows_full_dup} 行数据。当前数据量：{self.df.shape[0]} 行。")

        # 基于关键字段的重复 (同一辆车同一时间同一位置的重复记录)
        if all(col in self.df.columns for col in ['COMMADDR', 'UTC', 'LAT', 'LON']):
            rows_before_key_dup = self.df.shape[0]
            self.df.drop_duplicates(subset=['COMMADDR', 'UTC', 'LAT', 'LON'], inplace=True)
            dropped_rows_key_dup = rows_before_key_dup - self.df.shape[0]
            logging.info(f"因 (COMMADDR, UTC, LAT, LON) 键重复删除了 {dropped_rows_key_dup} 行数据。当前数据量：{self.df.shape[0]} 行。")
        else:
            logging.warning("警告：无法执行基于关键字段的重复删除，因为某些关键列不存在。")

        # 5. 处理异常数据
        logging.info("正在处理异常地理坐标...")
        rows_before_coord_clean = self.df.shape[0]
        if 'LAT' in self.df.columns and 'LON' in self.df.columns:
            # 过滤掉超出地理范围的坐标
            self.df = self.df[
                (self.df['LAT'] >= -90) & (self.df['LAT'] <= 90) &
                (self.df['LON'] >= -180) & (self.df['LON'] <= 180)
            ]
            dropped_rows_coord = rows_before_coord_clean - self.df.shape[0]
            logging.info(f"因异常地理坐标删除了 {dropped_rows_coord} 行数据。当前数据量：{self.df.shape[0]} 行。")
        else:
            logging.warning("警告：无法处理异常地理坐标，因为 'LAT' 或 'LON' 列不存在。")

        logging.info("正在处理异常时间戳...")
        rows_before_time_clean = self.df.shape[0]
        if 'UTC' in self.df.columns:
            # 过滤掉无效时间戳 (NaN) 和未来时间戳 (可选)
            self.df = self.df[self.df['UTC'].notna()]
            # 如果需要，可以添加过滤未来时间戳的逻辑，例如：
            # self.df = self.df[self.df['UTC'] <= pd.Timestamp.now(tz='UTC')]
        dropped_rows_time = rows_before_time_clean - self.df.shape[0]
        logging.info(f"因无效时间戳删除了 {dropped_rows_time} 行数据。当前数据量：{self.df.shape[0]} 行。")
        # 没有 else 分支，因为在前面已经有对 UTC 列不存在的警告了。

        # 6. 数据排序 (非常重要，尤其是对于轨迹分析)
        logging.info("正在按车辆ID和时间戳排序数据...")
        if all(col in self.df.columns for col in ['COMMADDR', 'UTC']):
            self.df.sort_values(by=['COMMADDR', 'UTC'], inplace=True)
            logging.info("数据排序完成。")
        else:
            logging.warning("警告：无法按 'COMMADDR' 和 'UTC' 排序，因为其中一个或两个列不存在。")

        final_rows = self.df.shape[0]
        total_dropped_rows = initial_rows - final_rows
        logging.info(f"数据清洗完成！")
        logging.info(f"原始数据行数: {initial_rows}")
        logging.info(f"清洗后数据行数: {final_rows}")
        logging.info(f"共删除行数: {total_dropped_rows}")

        # 保存处理后的数据到缓存
        logging.info(f"正在保存清洗后的数据到缓存：{cache_file_path}")
        joblib.dump(self.df, cache_file_path)
        logging.info("数据已保存。")

        return self.df

# 主执行块
if __name__ == "__main__":
    # 获取当前脚本的绝对路径
    current_script_path = os.path.abspath(__file__)
    
    # 获取当前脚本所在的目录 (即：...\traffic_visualization)
    current_script_dir = os.path.dirname(current_script_path)
    
    # data 目录是当前脚本目录的一个子目录。
    raw_data_dir = os.path.join(current_script_dir, 'data', 'raw')
    processed_data_dir = os.path.join(current_script_dir, 'data', 'processed')
    
    logging.info(f"预期原始数据目录: {raw_data_dir}")
    logging.info(f"预期处理后数据目录: {processed_data_dir}")

    cleaner = TrafficDataCleaner(raw_data_dir, processed_data_dir)
    
    # 获取 raw_data_dir 下所有的 CSV 文件
    csv_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        logging.warning(f"在目录 {raw_data_dir} 中未找到任何 CSV 文件。请确保文件存在。")
    else:
        logging.info(f"找到以下 CSV 文件进行处理: {csv_files}")
        for file_name in sorted(csv_files): # 排序以确保处理顺序一致
            logging.info(f"\n--- 开始处理文件: {file_name} ---")
            cleaned_df = cleaner.clean_data(raw_file_name=file_name)

            if cleaned_df is not None and not cleaned_df.empty:
                logging.info(f"文件 {file_name} 清洗后的数据预览 (前5行):")
                print(cleaned_df.head())
            elif cleaned_df is not None and cleaned_df.empty:
                logging.warning(f"文件 {file_name} 清洗后数据集为空，请检查原始数据和清洗逻辑。")
            else:
                logging.error(f"文件 {file_name} 数据清洗失败或未返回有效数据。")
            logging.info(f"--- 文件 {file_name} 处理完成 ---\n")
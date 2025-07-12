"""
测试真实天气数据集成
验证济南天气数据的读取和处理功能
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smart_passenger_engine import SmartPassengerEngine

def test_weather_data_reading():
    """测试天气数据读取功能"""
    print("=== 测试真实天气数据集成 ===")
    
    # 创建智能客运分析引擎
    engine = SmartPassengerEngine()
    
    # 济南天气数据的时间范围：2013/9/12 0:00:00 到 2013/9/18 23:00:00
    start_date = datetime(2013, 9, 12, 0, 0, 0)
    end_date = datetime(2013, 9, 18, 23, 0, 0)
    
    start_timestamp = start_date.timestamp()
    end_timestamp = end_date.timestamp()
    
    print(f"查询时间范围: {start_date} 到 {end_date}")
    print(f"时间戳范围: {start_timestamp} 到 {end_timestamp}")
    
    # 获取天气数据
    weather_data = engine.get_weather_data(start_timestamp, end_timestamp)
    
    print(f"\n获取到 {len(weather_data)} 条天气数据")
    
    if weather_data:
        print("\n前5条天气数据:")
        for i, weather in enumerate(weather_data[:5]):
            dt = datetime.fromtimestamp(weather.timestamp)
            print(f"{i+1}. {dt}: {weather.temperature}°C, {weather.humidity}%, "
                  f"{weather.precipitation}mm, {weather.wind_speed}风力, "
                  f"天气: {engine.weather_type_mapping[weather.weather_type]['name']}")
        
        # 统计天气类型分布
        weather_types = {}
        for weather in weather_data:
            weather_type = weather.weather_type
            weather_types[weather_type] = weather_types.get(weather_type, 0) + 1
        
        print(f"\n天气类型分布:")
        for weather_type, count in weather_types.items():
            name = engine.weather_type_mapping[weather_type]['name']
            percentage = (count / len(weather_data)) * 100
            print(f"- {name}: {count}条 ({percentage:.1f}%)")
        
        # 温度统计
        temperatures = [w.temperature for w in weather_data]
        print(f"\n温度统计:")
        print(f"- 最高温度: {max(temperatures):.1f}°C")
        print(f"- 最低温度: {min(temperatures):.1f}°C")
        print(f"- 平均温度: {sum(temperatures)/len(temperatures):.1f}°C")
        
        # 湿度统计
        humidities = [w.humidity for w in weather_data]
        print(f"\n湿度统计:")
        print(f"- 最高湿度: {max(humidities):.1f}%")
        print(f"- 最低湿度: {min(humidities):.1f}%")
        print(f"- 平均湿度: {sum(humidities)/len(humidities):.1f}%")
        
        # 降水统计
        precipitations = [w.precipitation for w in weather_data]
        rainy_days = len([p for p in precipitations if p > 0])
        print(f"\n降水统计:")
        print(f"- 有降水时段: {rainy_days}个 ({(rainy_days/len(weather_data)*100):.1f}%)")
        print(f"- 最大降水: {max(precipitations):.1f}mm")
        if rainy_days > 0:
            avg_precip = sum([p for p in precipitations if p > 0]) / rainy_days
            print(f"- 平均降水: {avg_precip:.1f}mm")
    
    else:
        print("❌ 未能获取到天气数据")
        return False
    
    print("\n✅ 天气数据集成测试完成")
    return True

def test_weather_classification():
    """测试天气分类算法"""
    print("\n=== 测试天气分类算法 ===")
    
    engine = SmartPassengerEngine()
    
    # 测试不同天气条件的分类
    test_cases = [
        {"temp": 25, "humidity": 50, "precip": 0, "wind": 2, "expected": "sunny"},
        {"temp": 20, "humidity": 85, "precip": 0, "wind": 1, "expected": "cloudy"},
        {"temp": 18, "humidity": 95, "precip": 0, "wind": 1, "expected": "foggy"},
        {"temp": 22, "humidity": 80, "precip": 1.0, "wind": 3, "expected": "light_rain"},
        {"temp": 19, "humidity": 90, "precip": 8.0, "wind": 5, "expected": "heavy_rain"},
    ]
    
    print("天气分类测试:")
    for i, case in enumerate(test_cases, 1):
        classified = engine._classify_weather_type(
            case["temp"], case["humidity"], case["precip"], case["wind"]
        )
        expected_name = engine.weather_type_mapping[case["expected"]]["name"]
        actual_name = engine.weather_type_mapping[classified]["name"]
        
        status = "✅" if classified == case["expected"] else "❌"
        print(f"{i}. {case['temp']}°C, {case['humidity']}%, {case['precip']}mm -> "
              f"预期: {expected_name}, 实际: {actual_name} {status}")
    
    print("\n✅ 天气分类测试完成")

def test_weather_file_direct():
    """直接测试天气文件读取"""
    print("\n=== 直接测试天气文件读取 ===")
    
    # 获取天气数据文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    weather_file_path = os.path.join(current_dir, 'data', 'jn_weather_c.csv')
    
    print(f"天气文件路径: {weather_file_path}")
    print(f"文件是否存在: {os.path.exists(weather_file_path)}")
    
    if os.path.exists(weather_file_path):
        try:
            df = pd.read_csv(weather_file_path)
            print(f"文件读取成功，共 {len(df)} 行数据")
            print(f"列名: {list(df.columns)}")
            print(f"时间范围: {df['Time_new'].iloc[0]} 到 {df['Time_new'].iloc[-1]}")
            
            print("\n前3行数据:")
            print(df.head(3).to_string())
            
            # 数据质量检查
            print(f"\n数据质量检查:")
            print(f"- 缺失值: {df.isnull().sum().sum()}")
            print(f"- 温度范围: {df['Temperature'].min():.1f}°C 到 {df['Temperature'].max():.1f}°C")
            print(f"- 湿度范围: {df['Humidity'].min():.1f}% 到 {df['Humidity'].max():.1f}%")
            print(f"- 风速范围: {df['Wind_Speed'].min():.1f} 到 {df['Wind_Speed'].max():.1f}")
            print(f"- 降水范围: {df['Precip'].min():.1f}mm 到 {df['Precip'].max():.1f}mm")
            
        except Exception as e:
            print(f"❌ 文件读取失败: {e}")
            return False
    else:
        print("❌ 天气数据文件不存在")
        return False
    
    print("\n✅ 天气文件读取测试完成")
    return True

if __name__ == "__main__":
    print("开始测试真实天气数据集成...")
    
    # 1. 直接测试文件读取
    file_test = test_weather_file_direct()
    
    # 2. 测试天气数据读取功能
    if file_test:
        weather_test = test_weather_data_reading()
        
        # 3. 测试天气分类算法
        test_weather_classification()
    
    print("\n🎉 所有测试完成！") 
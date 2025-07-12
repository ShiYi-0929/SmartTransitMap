# 智能客运监控模块

## 功能概述

智能客运监控模块专注于分析天气对客流量的影响以及载客出租车的动态需求监控。该模块通过智能分析算法，深度挖掘天气变化与客流量的关联关系，同时实时监控城区内载客出租车数量，为交通管理部门提供精准的决策支持。

**✨ 新增特性**: 现已集成真实的济南市天气数据 (2013/9/12 - 2013/9/18)，提供更准确的天气影响分析。

## 核心特点

### 1. 智能化分析架构
- **真实天气数据集成**: 使用济南市2013年9月12日至18日的真实天气数据
- **载客车辆识别**: 基于轨迹特征智能识别载客状态和空载状态
- **关联分析引擎**: 深度分析天气条件与客流变化的因果关系
- **动态监控系统**: 以当前时段为起点的实时载客车辆数量监控
- **预测分析能力**: 基于历史数据和天气预报进行客流预测

### 2. 真实天气数据源
- **数据文件**: `backend/detect/traffic_visualization/data/jn_weather_c.csv`
- **时间范围**: 2013年9月12日00:00 至 2013年9月18日23:00 (共168小时)
- **数据频率**: 每小时一条记录
- **数据字段**:
  - `Time_new`: 时间 (YYYY-MM-DD HH:MM)
  - `Temperature`: 温度 (摄氏度)
  - `Humidity`: 湿度 (%)
  - `Wind_Speed`: 风速
  - `Precip`: 降水量 (mm)

### 3. 天气数据特征分析
基于真实济南天气数据的特征：
- **温度范围**: 16.1°C - 33.9°C
- **湿度范围**: 26% - 100%
- **降水情况**: 无降水记录 (2013年9月12-18日为晴好天气)
- **风速范围**: 0 - 11级

### 4. 天气条件分类算法
基于真实天气数据优化的分类逻辑：
```python
def _classify_weather_type(temperature, humidity, precipitation, wind_speed):
    if precipitation > 5.0:      # 大雨
        return 'heavy_rain'
    elif precipitation > 0.5:    # 小雨
        return 'light_rain'
    elif humidity > 90 and wind_speed < 2:  # 雾天
        return 'foggy'
    elif humidity > 80:          # 阴天
        return 'cloudy'
    else:                        # 晴天
        return 'sunny'
```

### 5. 多维度客流分析
- **天气影响分析**: 定量分析不同天气条件对客流量的影响程度
- **载客需求监控**: 实时监控载客出租车vs订单需求的供需关系
- **时空分布分析**: 客流在时间和空间维度的分布规律
- **高峰时段识别**: 自动识别客流高峰期和需求热点区域

## 天气数据集成详情

### 数据读取流程
1. **主要数据源**: 优先读取真实的济南天气数据文件
2. **时间匹配**: 根据查询时间范围匹配对应的天气记录
3. **数据转换**: 将CSV数据转换为WeatherData模型
4. **备用方案**: 如果真实数据不可用，自动切换到模拟天气数据

### 天气类型映射
基于济南9月份天气特征优化的映射：
```python
weather_type_mapping = {
    'sunny': {'level': 1, 'name': '晴天', 'description': '阳光充足，适宜出行'},
    'cloudy': {'level': 2, 'name': '阴天', 'description': '多云天气，对出行影响较小'},
    'light_rain': {'level': 3, 'name': '小雨', 'description': '小雨天气，略微增加出行需求'},
    'heavy_rain': {'level': 4, 'name': '大雨', 'description': '降雨较大，显著影响出行'},
    'snow': {'level': 5, 'name': '雪天', 'description': '雪天出行，需求大幅增加'},
    'foggy': {'level': 4, 'name': '雾天', 'description': '能见度低，影响出行安全'}
}
```

### 能见度估算算法
基于湿度和降水量计算能见度：
```python
def _estimate_visibility(humidity, precipitation):
    base_visibility = 20.0  # 基础能见度20km
    humidity_factor = max(0.3, (100 - humidity) / 100)  # 湿度影响因子
    
    # 降水影响因子
    if precipitation > 5:    precip_factor = 0.2
    elif precipitation > 1:  precip_factor = 0.5
    elif precipitation > 0:  precip_factor = 0.8
    else:                    precip_factor = 1.0
    
    return max(0.5, min(20.0, base_visibility * humidity_factor * precip_factor))
```

## API接口说明

### 1. 智能客运监控分析接口
```
POST /api/smart-passenger/analysis
```
**请求参数**:
- `analysis_type`: 分析类型 (comprehensive/weather_impact/taxi_demand/correlation)
- `include_weather`: 是否包含天气分析
- `include_taxi_analysis`: 是否包含出租车分析
- `min_passenger_threshold`: 最小客流阈值
- `weather_correlation`: 是否进行天气关联分析
- `time_resolution`: 时间分辨率（分钟）

**响应数据**:
- 智能客运统计数据
- 基于真实天气数据的影响分析结果
- 出租车供需分析
- 处理时间统计

### 2. 天气影响分析接口
```
POST /api/smart-passenger/weather-impact
```
**功能**: 专门分析天气变化对客流量的影响
**特色**: 使用真实济南天气数据进行分析
**响应数据**:
- 各种天气条件的影响分析
- 天气与客流的相关性矩阵
- 真实天气统计数据
- 预测数据（可选）

### 3. 出租车需求分析接口
```
POST /api/smart-passenger/taxi-demand
```
**功能**: 动态监控载客出租车数量和需求情况
**响应数据**:
- 供需分析结果
- 实时状态监控
- 需求热点可视化
- 需求预测（可选）

### 4. 客运可视化数据接口
```
POST /api/smart-passenger/visualization
```
**功能**: 生成客流热力图、天气关联图表、出租车需求地图等
**响应数据**:
- 客流热力图数据
- 基于真实天气数据的关联图表
- 出租车需求地图数据
- 时间序列数据

### 5. 实时客运监控接口
```
GET /api/smart-passenger/real-time
```
**功能**: 获取当前时段的实时客流和载客车辆状态
**响应数据**:
- 实时客流统计
- 载客车辆状态
- 供需状态指标

## 天气数据使用示例

### 真实天气数据查询
```python
from .smart_passenger_engine import SmartPassengerEngine

# 创建分析引擎
engine = SmartPassengerEngine()

# 查询济南天气数据的时间范围
start_time = datetime(2013, 9, 12, 0, 0, 0).timestamp()
end_time = datetime(2013, 9, 18, 23, 0, 0).timestamp()

# 获取真实天气数据
weather_data = engine.get_weather_data(start_time, end_time)

# 分析天气特征
for weather in weather_data[:5]:
    print(f"{datetime.fromtimestamp(weather.timestamp)}: "
          f"{weather.temperature}°C, {weather.humidity}%, "
          f"天气类型: {engine.weather_type_mapping[weather.weather_type]['name']}")
```

### 天气影响分析
```python
# 识别客流数据
passenger_flows = engine.identify_passenger_vehicles(trajectory_data)

# 分析天气对客流的影响
weather_impact = engine.analyze_weather_impact(passenger_flows, weather_data)

for impact in weather_impact:
    print(f"天气条件: {impact.weather_condition}")
    print(f"影响程度: {impact.impact_percentage:.1f}%")
    print(f"相关系数: {impact.correlation_coefficient:.3f}")
```

## 数据兼容性

### 时间范围处理
- **匹配范围**: 如果查询时间在2013/9/12-18范围内，使用真实数据
- **超出范围**: 如果查询时间超出真实数据范围，使用前24小时数据进行演示
- **备用方案**: 如果文件不存在或读取失败，自动切换到模拟数据

### 数据格式转换
```python
# CSV格式 -> WeatherData模型
weather_df = pd.read_csv('jn_weather_c.csv')
weather_df['timestamp'] = pd.to_datetime(weather_df['Time_new']).astype(int) / 10**9

weather_data = WeatherData(
    timestamp=row['timestamp'],
    temperature=row['Temperature'],
    humidity=row['Humidity'],
    precipitation=row['Precip'],
    wind_speed=row['Wind_Speed'],
    visibility=estimated_visibility,
    weather_type=classified_type,
    weather_level=weather_level
)
```

## 技术特性

### 1. 智能化特征
- **真实数据驱动**: 基于真实济南天气数据的机器学习模型
- **异常检测**: 自动识别异常的客流模式
- **预测分析**: 结合历史天气数据预测客流变化
- **自适应阈值**: 根据真实天气特征自动调整判定阈值

### 2. 实时性保障
- **数据缓存**: 天气数据智能缓存，提高查询效率
- **增量更新**: 增量数据处理，提高效率
- **并发处理**: 支持多用户并发天气数据访问

### 3. 数据质量保障
- **数据验证**: 真实天气数据质量验证
- **缺失值处理**: 智能填补缺失的天气数据
- **异常值检测**: 识别和处理异常天气数据点

## 配置说明

### 天气数据文件配置
```python
# 天气数据文件路径
weather_file_path = 'backend/detect/traffic_visualization/data/jn_weather_c.csv'

# 数据字段映射
csv_fields = {
    'Time_new': '时间字段',
    'Temperature': '温度(°C)',
    'Humidity': '湿度(%)',
    'Wind_Speed': '风速',
    'Precip': '降水量(mm)'
}
```

### 天气分类阈值
```python
weather_classification_thresholds = {
    'heavy_rain': 5.0,      # 大雨降水阈值(mm)
    'light_rain': 0.5,      # 小雨降水阈值(mm)
    'foggy_humidity': 90,    # 雾天湿度阈值(%)
    'foggy_wind': 2,        # 雾天风速阈值
    'cloudy_humidity': 80   # 阴天湿度阈值(%)
}
```

## 故障排除

### 真实天气数据相关问题
1. **文件不存在**: 确认`jn_weather_c.csv`文件在正确位置
2. **时间范围不匹配**: 系统会自动使用演示数据
3. **数据格式错误**: 检查CSV文件格式和字段名
4. **编码问题**: 确保CSV文件使用UTF-8编码

### 性能优化
- 天气数据缓存时间：1小时
- 批量读取优化：支持大时间范围查询
- 内存管理：及时释放不需要的天气数据

## 未来扩展

### 天气数据增强
- 集成更多城市的真实天气数据
- 支持实时天气API接入
- 增加空气质量、风向等更多天气因子
- 支持天气预报数据集成

### 分析算法优化
- 基于真实数据训练深度学习模型
- 多元回归分析天气对客流的影响
- 时间序列预测模型
- 异常天气事件影响分析

该智能客运监控模块现已集成真实的济南市天气数据，为天气对客流影响的分析提供了更加准确和可靠的数据基础，大大提升了分析结果的可信度和实用性。 
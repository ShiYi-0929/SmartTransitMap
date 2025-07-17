# 路段和道路时空数据可视化展示

## 功能概述

路段分析模块专注于道路层面的交通数据分析，支持展示不同路段的通行状况、速度分布、距离统计等指标。该模块采用数据处理与可视化分离的架构设计，便于支持多种路段类型和统计方式。

## 核心特点

### 1. 模块化设计
- **数据模型层**: 定义路段、交通数据、统计指标等数据结构
- **分析引擎层**: 实现路段分析算法和统计计算
- **数据处理层**: 负责数据转换和聚合处理
- **API服务层**: 提供RESTful接口
- **前端可视化层**: 地图展示和图表分析

### 2. 多维度分析
- **综合分析**: 包含速度、流量、拥堵等全方位指标
- **速度分析**: 专注于速度分布和变化趋势
- **流量分析**: 分析交通流量模式和峰值
- **拥堵分析**: 识别瓶颈路段和拥堵原因

### 3. 路段类型支持
- **高速公路**: 自由流速度80km/h，容量2000veh/h/lane
- **主干道**: 自由流速度50km/h，容量1200veh/h/lane  
- **城市道路**: 自由流速度40km/h，容量800veh/h/lane
- **支路**: 自由流速度30km/h，容量600veh/h/lane

## API接口说明

### 1. 路段分析接口
```
POST /api/road/analysis
```
**请求参数**:
- `analysis_type`: 分析类型 (comprehensive/speed/flow/congestion)
- `segment_types`: 路段类型过滤 (highway/arterial/urban/local/all)
- `aggregation_level`: 聚合级别 (segment/road/network)
- `min_vehicles`: 最小车辆数阈值

**响应数据**:
- 路段统计数据
- 速度分布信息
- 交通流量模式
- 瓶颈路段识别

### 2. 路段信息接口
```
GET /api/road/segments
```
返回系统识别的所有路段基础信息

### 3. 交通数据接口
```
POST /api/road/traffic
```
获取指定时间范围内的路段交通状况数据

### 4. 可视化数据接口
```
POST /api/road/visualization
```
生成用于地图展示的路段可视化数据

### 5. 路网指标接口
```
GET /api/road/metrics
```
返回路网的综合性能指标和统计信息

## 核心算法

### 1. 路段提取算法
- 基于轨迹数据自动识别路段
- 计算路段长度和几何属性
- 根据距离和速度分类道路类型

### 2. 交通状态分析
- 15分钟时间窗口聚合
- 计算平均速度、流量、密度
- 基于速度比例确定拥堵等级

### 3. 统计指标计算
- 峰值/非峰值流量分析
- 自由流速度估算
- 通行能力利用率评估
- 效率评分计算

### 4. 瓶颈识别算法
- 效率评分 < 50分
- 容量利用率 > 80%
- 拥堵时间 > 4小时
- 平均速度 < 20km/h

## 可视化功能

### 1. 地图可视化
- 路段颜色编码显示
- 支持多种可视化类型（速度/流量/拥堵/效率）
- 交互式地图操作
- Canvas降级显示支持

### 2. 统计图表
- 速度分布柱状图
- 24小时流量模式曲线
- 拥堵指数趋势
- 路段详情表格

### 3. 性能指标
- 实时统计卡片
- 路网整体指标
- 瓶颈路段列表
- 数据导出功能

## 技术特性

### 1. 架构分离
- 分析算法与渲染完全解耦
- 支持多种渲染模式切换
- 独立的数据处理管道

### 2. 性能优化
- 分块数据加载
- 空间索引优化
- 时间窗口聚合
- 结果缓存机制

### 3. 扩展性
- 支持新增路段类型
- 可配置分析参数
- 插件化算法架构
- 多种数据源接入

## 使用示例

### 前端调用
```javascript
import { performRoadAnalysis } from '@/api/traffic'

// 执行综合路段分析
const result = await performRoadAnalysis({
  analysis_type: 'comprehensive',
  segment_types: ['highway', 'arterial'],
  min_vehicles: 10
})

// 获取可视化数据
const vizData = await getRoadVisualizationData({
  visualization_type: 'speed',
  time_range: { start: startTime, end: endTime }
})
```

### 后端扩展
```python
from .road_analysis_engine import RoadAnalysisEngine

# 创建分析引擎
engine = RoadAnalysisEngine()

# 提取路段
segments = engine.extract_road_segments(trajectory_data)

# 分析交通数据
traffic_data = engine.analyze_road_traffic(trajectory_data, segments)

# 计算统计指标
stats = engine.calculate_segment_statistics(traffic_data, time_range)
```

## 配置说明

### 道路类型配置
```python
road_type_configs = {
    'highway': {
        'free_flow_speed': 80,  # km/h
        'capacity_per_lane': 2000,  # vehicles/hour/lane
        'default_lanes': 3
    },
    # ... 其他类型
}
```

### 拥堵阈值配置
```python
congestion_thresholds = {
    'free': 0.3,      # 自由流：< 30% 容量
    'moderate': 0.6,   # 缓慢：30-60% 容量
    'heavy': 0.8,      # 拥堵：60-80% 容量
    'jam': 1.0         # 严重拥堵：> 80% 容量
}
```

## 故障排除

### 常见问题
1. **数据为空**: 检查时间范围和车辆数阈值设置
2. **地图不显示**: 确认高德地图API加载，或使用Canvas模式
3. **分析缓慢**: 减少时间范围或增加车辆数阈值
4. **路段过少**: 降低最小车辆数要求

### 性能调优
- 调整时间窗口大小（默认15分钟）
- 设置合适的空间分辨率
- 使用数据缓存机制
- 限制同时分析的路段数量

## 未来扩展

### 计划功能
- 实时路段状态监控
- 路段间关联分析
- 预测性拥堵预警
- 路网优化建议

### 技术升级
- 机器学习拥堵预测
- 图数据库路网存储
- 分布式计算支持
- 云端数据同步 
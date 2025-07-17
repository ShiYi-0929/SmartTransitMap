"""
时空数据聚类算法引擎
支持多种聚类算法：DBSCAN、K-means、层次聚类等
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from sklearn.cluster import DBSCAN, KMeans, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import math
from abc import ABC, abstractmethod

class ClusteringAlgorithm(ABC):
    """聚类算法抽象基类"""
    
    @abstractmethod
    def fit(self, data: np.ndarray, **kwargs) -> np.ndarray:
        """执行聚类并返回标签"""
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """返回算法名称"""
        pass
    
    @abstractmethod
    def get_default_params(self) -> Dict[str, Any]:
        """返回默认参数"""
        pass

class DBSCANAlgorithm(ClusteringAlgorithm):
    """DBSCAN密度聚类算法"""
    
    def __init__(self):
        self.model = None
        
    def fit(self, data: np.ndarray, eps: float = 0.01, min_samples: int = 5, **kwargs) -> np.ndarray:
        """
        执行DBSCAN聚类
        
        Args:
            data: 二维数组，每行是一个数据点 [lat, lng, weight?]
            eps: 邻域半径
            min_samples: 核心点的最小邻居数
        """
        # 对于地理坐标，使用特殊的距离度量
        if data.shape[1] >= 2:
            # 转换经纬度为适合聚类的格式
            coords = data[:, :2]  # lat, lng
            
            # 如果有权重，考虑权重
            if data.shape[1] > 2:
                weights = data[:, 2]
                # 重复数据点根据权重
                expanded_coords = []
                for i, (coord, weight) in enumerate(zip(coords, weights)):
                    repeat_count = max(1, int(weight))
                    expanded_coords.extend([coord] * repeat_count)
                coords = np.array(expanded_coords)
            
            self.model = DBSCAN(eps=eps, min_samples=min_samples, metric='haversine')
            
            # 将经纬度转换为弧度用于haversine距离
            coords_rad = np.radians(coords)
            labels = self.model.fit_predict(coords_rad)
            
            # 如果扩展了数据，需要映射回原始数据
            if data.shape[1] > 2:
                original_labels = []
                idx = 0
                for weight in weights:
                    repeat_count = max(1, int(weight))
                    # 取这个权重组中的多数标签
                    group_labels = labels[idx:idx+repeat_count]
                    unique, counts = np.unique(group_labels, return_counts=True)
                    original_labels.append(unique[np.argmax(counts)])
                    idx += repeat_count
                labels = np.array(original_labels)
                
        else:
            self.model = DBSCAN(eps=eps, min_samples=min_samples)
            labels = self.model.fit_predict(data)
            
        return labels
    
    def get_algorithm_name(self) -> str:
        return "DBSCAN"
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "eps": 0.01,  # 约1km的经纬度距离
            "min_samples": 5
        }

class KMeansAlgorithm(ClusteringAlgorithm):
    """K-Means聚类算法"""
    
    def __init__(self):
        self.model = None
        
    def fit(self, data: np.ndarray, n_clusters: int = 8, **kwargs) -> np.ndarray:
        """
        执行K-Means聚类
        
        Args:
            data: 二维数组，每行是一个数据点
            n_clusters: 聚类数量
        """
        # 如果数据点数少于聚类数，调整聚类数
        n_clusters = min(n_clusters, len(data))
        
        if data.shape[1] >= 2:
            # 对地理坐标进行标准化
            coords = data[:, :2]
            scaler = StandardScaler()
            coords_scaled = scaler.fit_transform(coords)
            
            # 如果有权重，使用sample_weight
            sample_weight = None
            if data.shape[1] > 2:
                sample_weight = data[:, 2]
            
            self.model = KMeans(
                n_clusters=n_clusters, 
                random_state=42, 
                n_init=10
            )
            
            labels = self.model.fit_predict(coords_scaled, sample_weight=sample_weight)
        else:
            self.model = KMeans(n_clusters=n_clusters, random_state=42)
            labels = self.model.fit_predict(data)
            
        return labels
    
    def get_algorithm_name(self) -> str:
        return "K-Means"
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "n_clusters": 8
        }

class HierarchicalAlgorithm(ClusteringAlgorithm):
    """层次聚类算法"""
    
    def __init__(self):
        self.model = None
        
    def fit(self, data: np.ndarray, n_clusters: int = 8, linkage: str = 'ward', **kwargs) -> np.ndarray:
        """
        执行层次聚类
        
        Args:
            data: 二维数组，每行是一个数据点
            n_clusters: 聚类数量
            linkage: 链接方法
        """
        n_clusters = min(n_clusters, len(data))
        
        if data.shape[1] >= 2:
            coords = data[:, :2]
            scaler = StandardScaler()
            coords_scaled = scaler.fit_transform(coords)
            
            self.model = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage=linkage
            )
            labels = self.model.fit_predict(coords_scaled)
        else:
            self.model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
            labels = self.model.fit_predict(data)
            
        return labels
    
    def get_algorithm_name(self) -> str:
        return "Hierarchical"
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "n_clusters": 8,
            "linkage": "ward"
        }

class ClusteringEngine:
    """聚类引擎主类，管理多种聚类算法"""
    
    def __init__(self):
        self.algorithms = {
            "dbscan": DBSCANAlgorithm(),
            "kmeans": KMeansAlgorithm(),
            "hierarchical": HierarchicalAlgorithm()
        }
        
    def get_available_algorithms(self) -> List[str]:
        """获取可用的聚类算法列表"""
        return list(self.algorithms.keys())
    
    def get_algorithm_params(self, algorithm_name: str) -> Dict[str, Any]:
        """获取算法的默认参数"""
        if algorithm_name in self.algorithms:
            return self.algorithms[algorithm_name].get_default_params()
        return {}
    
    def cluster_data(
        self, 
        data: List[Dict[str, float]], 
        algorithm: str = "dbscan",
        params: Dict[str, Any] = None,
        include_weights: bool = True
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        对数据进行聚类
        
        Args:
            data: 数据点列表，每个点包含 lat, lng, 可选的 weight
            algorithm: 聚类算法名称
            params: 算法参数
            include_weights: 是否包含权重信息
            
        Returns:
            labels: 聚类标签数组
            metrics: 聚类质量指标
        """
        if not data:
            return np.array([]), {}
            
        if params is None:
            params = {}
            
        # 转换数据格式
        if include_weights and all('weight' in point for point in data):
            data_array = np.array([
                [point['lat'], point['lng'], point.get('weight', 1.0)]
                for point in data
            ])
        else:
            data_array = np.array([
                [point['lat'], point['lng']]
                for point in data
            ])
        
        # 执行聚类
        if algorithm not in self.algorithms:
            raise ValueError(f"未知的聚类算法: {algorithm}")
            
        clustering_algo = self.algorithms[algorithm]
        
        # 合并默认参数和用户参数
        default_params = clustering_algo.get_default_params()
        final_params = {**default_params, **params}
        
        labels = clustering_algo.fit(data_array, **final_params)
        
        # 计算聚类质量指标
        metrics = self._calculate_clustering_metrics(data_array[:, :2], labels)
        metrics['algorithm'] = algorithm
        metrics['parameters'] = final_params
        
        return labels, metrics
    
    def _calculate_clustering_metrics(self, data: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
        """计算聚类质量指标"""
        metrics = {
            "n_clusters": len(set(labels)) - (1 if -1 in labels else 0),
            "n_noise": list(labels).count(-1),
            "n_points": len(labels)
        }
        
        # 只有当有多个聚类时才计算轮廓系数
        if metrics["n_clusters"] > 1 and metrics["n_noise"] < len(labels):
            try:
                # 过滤噪声点
                valid_mask = labels != -1
                if np.sum(valid_mask) > 1:
                    valid_data = data[valid_mask]
                    valid_labels = labels[valid_mask]
                    
                    if len(set(valid_labels)) > 1:
                        metrics["silhouette_score"] = silhouette_score(valid_data, valid_labels)
                        metrics["calinski_harabasz_score"] = calinski_harabasz_score(valid_data, valid_labels)
            except Exception as e:
                print(f"计算聚类指标时出错: {e}")
                
        return metrics
    
    def analyze_clusters(
        self, 
        data: List[Dict[str, float]], 
        labels: np.ndarray,
        cluster_type: str = "hotspot"
    ) -> List[Dict[str, Any]]:
        """
        分析聚类结果，生成聚类描述
        
        Args:
            data: 原始数据点
            labels: 聚类标签
            cluster_type: 聚类类型标识
            
        Returns:
            聚类分析结果列表
        """
        clusters = []
        unique_labels = set(labels)
        
        for cluster_id in unique_labels:
            if cluster_id == -1:  # 跳过噪声点
                continue
                
            # 获取属于此聚类的点
            cluster_mask = labels == cluster_id
            cluster_points = [data[i] for i in range(len(data)) if cluster_mask[i]]
            
            if not cluster_points:
                continue
                
            # 计算聚类中心
            center_lat = np.mean([p['lat'] for p in cluster_points])
            center_lng = np.mean([p['lng'] for p in cluster_points])
            
            # 计算总权重和密度
            total_weight = sum(p.get('weight', 1.0) for p in cluster_points)
            
            # 计算聚类范围（标准差作为半径的估计）
            if len(cluster_points) > 1:
                lat_std = np.std([p['lat'] for p in cluster_points])
                lng_std = np.std([p['lng'] for p in cluster_points])
                cluster_radius = math.sqrt(lat_std**2 + lng_std**2)
                density = total_weight / (math.pi * cluster_radius**2) if cluster_radius > 0 else total_weight
            else:
                density = total_weight
                
            cluster_info = {
                "cluster_id": int(cluster_id),
                "center_lat": center_lat,
                "center_lng": center_lng,
                "points": [
                    {
                        "lat": p['lat'], 
                        "lng": p['lng'], 
                        "weight": p.get('weight', 1.0)
                    } for p in cluster_points
                ],
                "point_count": len(cluster_points),
                "total_weight": total_weight,
                "density": density,
                "cluster_type": cluster_type
            }
            
            clusters.append(cluster_info)
        
        # 按密度排序
        clusters.sort(key=lambda x: x['density'], reverse=True)
        
        return clusters
    
    def optimize_clustering_params(
        self, 
        data: List[Dict[str, float]], 
        algorithm: str = "dbscan",
        param_ranges: Dict[str, List] = None
    ) -> Dict[str, Any]:
        """
        优化聚类参数，寻找最佳参数组合
        
        Args:
            data: 数据点
            algorithm: 聚类算法
            param_ranges: 参数范围字典
            
        Returns:
            最佳参数和对应的指标
        """
        if param_ranges is None:
            if algorithm == "dbscan":
                param_ranges = {
                    "eps": [0.005, 0.01, 0.015, 0.02, 0.025],
                    "min_samples": [3, 5, 7, 10]
                }
            elif algorithm == "kmeans":
                param_ranges = {
                    "n_clusters": [3, 5, 8, 10, 12, 15]
                }
            else:
                param_ranges = {
                    "n_clusters": [3, 5, 8, 10, 12, 15]
                }
        
        best_score = -1
        best_params = {}
        best_metrics = {}
        
        # 生成参数组合
        from itertools import product
        
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        
        for param_combination in product(*param_values):
            params = dict(zip(param_names, param_combination))
            
            try:
                labels, metrics = self.cluster_data(data, algorithm, params)
                
                # 使用轮廓系数作为优化目标
                score = metrics.get("silhouette_score", -1)
                
                # 如果没有轮廓系数，使用其他指标
                if score == -1:
                    n_clusters = metrics.get("n_clusters", 0)
                    n_noise = metrics.get("n_noise", len(data))
                    if n_clusters > 0:
                        score = n_clusters / max(1, n_noise + 1)  # 简单的评分函数
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    best_metrics = metrics
                    
            except Exception as e:
                print(f"参数组合 {params} 出错: {e}")
                continue
        
        return {
            "best_params": best_params,
            "best_score": best_score,
            "best_metrics": best_metrics,
            "algorithm": algorithm
        } 
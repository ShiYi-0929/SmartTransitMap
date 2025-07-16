from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import threading
import time
from pydantic import BaseModel
import csv
import os

router = APIRouter()

# 全局日志存储 - 使用线程安全的列表
import queue
log_queue = queue.Queue()
real_logs = []
log_lock = threading.Lock()

LOG_CSV_PATH = os.path.join(os.path.dirname(__file__), "traffic_logs.csv")

# 日志记录器类
class TrafficLogger:
    """交通系统日志记录器"""
    
    @staticmethod
    def log(level: str, log_type: str, module: str, message: str, 
            source: str = "交通监控系统", user: str = "系统", 
            details: Optional[Dict[str, Any]] = None, stack: Optional[str] = None):
        """记录日志"""
        log_entry = {
            "id": f"traffic_log_{int(time.time() * 1000)}",
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "type": log_type,
            "module": module,
            "message": message,
            "source": source,
            "user": user,
            "details": details or {},
            "stack": stack
        }
        
        with log_lock:
            real_logs.insert(0, log_entry)  # 插入到开头
            # 保持最多1000条日志
            if len(real_logs) > 1000:
                real_logs.pop()
        
        # 同时放入队列供实时监控使用
        log_queue.put(log_entry)
        
        # 新增：写入CSV文件
        try:
            file_exists = os.path.isfile(LOG_CSV_PATH)
            with open(LOG_CSV_PATH, "a", newline='', encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=log_entry.keys())
                if not file_exists:
                    writer.writeheader()
                row = log_entry.copy()
                row["details"] = json.dumps(row["details"], ensure_ascii=False)
                row["stack"] = row["stack"] or ""
                writer.writerow(row)
        except Exception as e:
            print(f"写入日志CSV失败: {e}")
        
        return log_entry
    
    @staticmethod
    def info(module: str, message: str, **kwargs):
        """记录信息日志"""
        return TrafficLogger.log("info", "system", module, message, **kwargs)
    
    @staticmethod
    def warning(module: str, message: str, **kwargs):
        """记录警告日志"""
        return TrafficLogger.log("warning", "system", module, message, **kwargs)
    
    @staticmethod
    def error(module: str, message: str, **kwargs):
        """记录错误日志"""
        return TrafficLogger.log("error", "system", module, message, **kwargs)
    
    @staticmethod
    def traffic(module: str, message: str, **kwargs):
        """记录交通相关日志"""
        return TrafficLogger.log("info", "traffic", module, message, **kwargs)
    
    @staticmethod
    def anomaly(module: str, message: str, **kwargs):
        """记录异常检测日志"""
        return TrafficLogger.log("warning", "anomaly", module, message, **kwargs)
    
    @staticmethod
    def performance(module: str, message: str, **kwargs):
        """记录性能相关日志"""
        return TrafficLogger.log("info", "performance", module, message, **kwargs)

# 创建全局日志记录器实例
logger = TrafficLogger()

# 初始化一些系统启动日志
logger.info("系统管理", "交通监控日志系统启动", source="系统启动")
logger.info("交通监控", "日志记录器初始化完成", source="系统启动")

@router.get("/logs")
async def get_traffic_logs(
    level: Optional[str] = Query(None, description="日志级别"),
    log_type: Optional[str] = Query(None, description="日志类型"),
    module: Optional[str] = Query(None, description="模块名称"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    view_type: Optional[str] = Query(None, description="视图类型"),  # 新增
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    查询交通监控日志接口。
    支持按级别、类型、模块、时间范围、视图类型过滤，支持分页。
    """
    try:
        with log_lock:
            filtered_logs = real_logs.copy()
        
        # 按级别过滤
        if level and level != "all":
            filtered_logs = [log for log in filtered_logs if log["level"] == level]
        
        # 按类型过滤
        if log_type and log_type != "all":
            filtered_logs = [log for log in filtered_logs if log["type"] == log_type]
        
        # 按模块过滤
        if module:
            filtered_logs = [log for log in filtered_logs if module in log["module"]]
        
        # 按视图类型过滤（details.view_type）
        if view_type:
            filtered_logs = [
                log for log in filtered_logs
                if log.get("details", {}).get("view_type") == view_type
            ]
        
        # 按时间范围过滤
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                filtered_logs = [
                    log for log in filtered_logs 
                    if start_dt <= datetime.fromisoformat(log["timestamp"]) <= end_dt
                ]
            except ValueError:
                pass
        
        # 计算分页
        total = len(filtered_logs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_logs = filtered_logs[start_idx:end_idx]
        
        return {
            "logs": paginated_logs,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交通日志失败: {str(e)}")

@router.get("/logs/stats")
async def get_traffic_log_stats():
    """
    获取交通日志统计信息。
    """
    try:
        with log_lock:
            stats = {
                "error_count": len([log for log in real_logs if log["level"] == "error"]),
                "warning_count": len([log for log in real_logs if log["level"] == "warning"]),
                "info_count": len([log for log in real_logs if log["level"] == "info"]),
                "debug_count": len([log for log in real_logs if log["level"] == "debug"]),
                "total_count": len(real_logs)
            }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.delete("/logs")
async def clear_traffic_logs():
    """
    清空所有交通日志。
    """
    try:
        with log_lock:
            real_logs.clear()
        
        logger.info("系统管理", "所有交通日志已清空", source="用户操作")
        return {"message": "交通日志已清空"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空交通日志失败: {str(e)}")

@router.post("/logs")
async def add_traffic_log(log_data: dict):
    """
    添加新交通日志。
    """
    try:
        new_log = logger.log(
            level=log_data.get("level", "info"),
            log_type=log_data.get("type", "system"),
            module=log_data.get("module", "交通监控"),
            message=log_data.get("message", ""),
            source=log_data.get("source", "手动添加"),
            user=log_data.get("user", "系统"),
            details=log_data.get("details") or {},
            stack=log_data.get("stack") or ""
        )
        
        return {"message": "交通日志添加成功", "log": new_log}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加交通日志失败: {str(e)}")

class AlertRequest(BaseModel):
    message: str

@router.post("/alert")
async def send_traffic_alert(request: AlertRequest):
    """
    发送交通告警接口。
    """
    try:
        alert_log = logger.anomaly(
            module="交通告警系统",
            message=f"交通告警: {request.message}",
            source="交通告警推送",
            details={"alert_type": "traffic", "priority": "medium"}
        )
        
        return {"message": f"交通告警已发送：{request.message}", "alert_id": alert_log["id"]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送交通告警失败: {str(e)}")

# 导出日志记录器供其他模块使用
__all__ = ['logger', 'TrafficLogger'] 
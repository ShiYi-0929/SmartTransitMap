# from fastapi import APIRouter, UploadFile, File, HTTPException
# from fastapi.responses import JSONResponse
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from detect.inference import predict_disease
from .traffic_visualization.service import router as traffic_router
from .road_detection.service import router as road_router
from .face_recognition.service import router as face_router

import shutil
import os
import uuid
from datetime import datetime

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 创建主路由
api_router = APIRouter()

# 注册各模块的路由
api_router.include_router(traffic_router, prefix="/traffic", tags=["交通数据可视化"])
api_router.include_router(road_router, prefix="/road", tags=["道路检测"])
api_router.include_router(face_router, prefix="/face", tags=["人脸识别"])

@api_router.post("/detect")
async def detect_disease(file: UploadFile = File(...)):
    # 1. 获取文件信息
    filename = file.filename
    if filename is None:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".mp4"]:
        raise HTTPException(status_code=400, detail="仅支持图像或视频（.jpg/.png/.mp4）")

    # 2. 生成唯一文件名，防止重名覆盖
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, unique_name)

    # 3. 保存文件到服务器
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 4. 调用模型识别
    predict_result = predict_disease(save_path)

    # 5. 返回识别结果
    return JSONResponse(content={
        "status": "success",
        "original_filename": filename,
        "saved_path": save_path,
        "results": predict_result["result"],
        "message": "病害识别成功"
    })

@api_router.get("/trend")
async def get_trend_data():
    """获取统计趋势数据"""
    return JSONResponse(content={
        "status": "success",
        "todayDetections": 23,
        "totalDamages": 40,
        "damageTypes": [
            {"name": "裂缝", "count": 15},
            {"name": "坑洞", "count": 8},
            {"name": "破损", "count": 12},
            {"name": "其他", "count": 5}
        ],
        "message": "获取统计数据成功"
    })

@api_router.get("/logs")
async def get_logs():
    """获取操作日志"""
    current_time = datetime.now()
    return JSONResponse(content={
        "status": "success",
        "logs": [
            {
                "id": 1,
                "action": "图像检测完成",
                "operator": "系统",
                "timestamp": current_time.isoformat()
            },
            {
                "id": 2,
                "action": "上传图像文件",
                "operator": "用户",
                "timestamp": (current_time.timestamp() - 300) * 1000  # 5分钟前
            },
            {
                "id": 3,
                "action": "病害识别",
                "operator": "系统",
                "timestamp": (current_time.timestamp() - 600) * 1000  # 10分钟前
            }
        ],
        "message": "获取日志成功"
    })

@api_router.get("/alarm")
async def get_alarm_data():
    """获取告警数据"""
    return JSONResponse(content={
        "status": "success",
        "alarms": [
            {
                "id": 1,
                "level": "high",
                "message": "检测到严重路面破损",
                "location": "主干道 KM 15+200",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": 2,
                "level": "medium",
                "message": "路面裂缝需要关注",
                "location": "辅路 KM 8+500",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "message": "获取告警数据成功"
    })

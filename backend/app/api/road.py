from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from database import models
from app.core.security import get_current_user

router = APIRouter()

@router.post("/detect")
async def detect_road_damage(file: UploadFile = File(...)):
    """
    路面病害检测接口：上传路面图片，返回检测结果。
    """
    # TODO: 实现路面病害检测模型推理
    return {"msg": "路面病害检测结果（示例）"}

@router.get("/result/{task_id}")
async def get_detection_result(task_id: str):
    """
    查询检测结果接口。
    """
    # TODO: 查询检测任务结果
    return {"task_id": task_id, "result": "检测结果（示例）"}

@router.get("/statistics", summary="路面病害统计（占位）")
async def get_road_statistics(db: Session = Depends(get_db), current_user: models.UserInfo = Depends(get_current_user)):
    return {"total": 0, "pothole": 0, "crack": 0}

@router.get("/repair-tasks", summary="维修任务列表（占位）")
async def get_repair_tasks(db: Session = Depends(get_db), current_user: models.UserInfo = Depends(get_current_user)):
    return []

@router.get("/logs", summary="路面检测日志（占位）")
async def get_road_logs(db: Session = Depends(get_db), current_user: models.UserInfo = Depends(get_current_user)):
    return []

@router.get("/records", summary="路面病害记录列表（占位）")
async def get_road_records(db: Session = Depends(get_db), current_user: models.UserInfo = Depends(get_current_user)):
    """
    提供给前端 Road.vue 的占位接口，返回空列表以避免 404。
    """
    return [] 
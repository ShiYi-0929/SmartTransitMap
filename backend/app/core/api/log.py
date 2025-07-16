from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import shutil
from datetime import datetime
from fastapi import Response
from sqlalchemy import or_, String

from database.database import get_db
from database import models
from app.core.security import get_current_user

router = APIRouter()

# 定义媒体文件存储目录
MEDIA_DIR = "backend/system_log_media"
os.makedirs(MEDIA_DIR, exist_ok=True)


# --- Pydantic Schemas for data validation ---
from pydantic import BaseModel

class LogBase(BaseModel):
    logtype: str
    description: Optional[str] = None

class LogCreate(LogBase):
    pass

class LogInDB(BaseModel):
    id: int
    userID: int
    username: str
    logtype: str
    description: Optional[str]
    timestamp: str
    screenshot_url: Optional[str] = None
    video_url: Optional[str] = None

    class Config:
        orm_mode = True


# --- Logic for creating a log entry (can be called from other modules) ---
async def create_log_entry(
    db: Session,
    user_id: int,
    logtype: str,
    description: Optional[str],
    screenshot: Optional[bytes] = None,
    video: Optional[bytes] = None
) -> LogInDB:
    """
    Creates a system log entry in the database and saves associated media.
    This is a reusable helper function.
    """
    # For unknown users (e.g., failed face recognition), use a placeholder.
    if user_id == -1:
        username = "Unknown"
    else:
        user = db.query(models.UserInfo).filter(models.UserInfo.userID == user_id).first()
        if not user:
            print(f"Log creation failed: User with ID {user_id} not found.")
            # To avoid crashing, we can either raise an error or log with a placeholder.
            # Let's use a placeholder for robustness.
            username = f"User_ID_{user_id}_NotFound"
        else:
            username = user.username

    db_log = models.SystemLog(
        userID=user_id,
        username=username,
        logtype=logtype,
        description=description,
        timestamp=datetime.now()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    log_id = db_log.id
    screenshot_url = None
    video_url = None

    if screenshot:
        ss_filename = f"{log_id}_screenshot.png"
        ss_path = os.path.join(MEDIA_DIR, ss_filename)
        with open(ss_path, "wb") as buffer:
            buffer.write(screenshot)
        screenshot_url = f"/api/log/media/{ss_filename}"

    if video:
        vid_filename = f"{log_id}_video.webm"
        vid_path = os.path.join(MEDIA_DIR, vid_filename)
        with open(vid_path, "wb") as buffer:
            buffer.write(video)
        video_url = f"/api/log/media/{vid_filename}"
    
    return LogInDB(
        id=db_log.id,
        userID=db_log.userID,
        username=db_log.username,
        logtype=db_log.logtype,
        description=db_log.description,
        timestamp=db_log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        screenshot_url=screenshot_url,
        video_url=video_url
    )


# --- API Endpoints ---

@router.post("/", response_model=LogInDB, summary="创建一条新的系统日志")
async def create_log(
    logtype: str = Form(...),
    description: Optional[str] = Form(None),
    screenshot: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.UserInfo = Depends(get_current_user)
):
    """
    创建一条新的系统日志，包含操作元数据和可选的截图/视频文件。
    """
    screenshot_bytes = await screenshot.read() if screenshot else None
    video_bytes = await video.read() if video else None

    log_entry = await create_log_entry(
        db=db,
        user_id=current_user.userID,
        logtype=logtype,
        description=description,
        screenshot=screenshot_bytes,
        video=video_bytes
    )
    
    if not log_entry:
         raise HTTPException(status_code=500, detail="Failed to create log entry")

    return log_entry

@router.get("/", response_model=List[LogInDB], summary="获取系统日志列表")
async def get_logs(
    db: Session = Depends(get_db),
    current_user: models.UserInfo = Depends(get_current_user),
    search: Optional[str] = None
):
    """
    获取系统日志列表。
    - 管理员可以查看所有日志。
    - 认证用户只能查看自己的日志。
    - 支持通过用户名/ID/日志类型进行搜索。
    """
    if current_user.user_class == "管理员":
        query = db.query(models.SystemLog)
    else: # 认证用户或普通用户
        query = db.query(models.SystemLog).filter(models.SystemLog.userID == current_user.userID)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.SystemLog.username.ilike(search_term),
                models.SystemLog.logtype.ilike(search_term),
                models.SystemLog.userID.cast(String).ilike(search_term)
            )
        )

    logs = query.order_by(models.SystemLog.timestamp.desc()).all()
    
    # 为每条日志构建媒体URL并格式化响应
    results = []
    for log in logs:
        screenshot_url = None
        video_url = None
        
        ss_filename = f"{log.id}_screenshot.png"
        vid_filename = f"{log.id}_video.webm"
        
        ss_path = os.path.join(MEDIA_DIR, ss_filename)
        if os.path.exists(ss_path):
            screenshot_url = f"/api/log/media/{ss_filename}"
            
        vid_path = os.path.join(MEDIA_DIR, vid_filename)
        if os.path.exists(vid_path):
            video_url = f"/api/log/media/{vid_filename}"
            
        results.append(
            LogInDB(
                id=log.id,
                userID=log.userID,
                username=log.username,
                logtype=log.logtype,
                description=log.description,
                timestamp=log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "N/A",
                screenshot_url=screenshot_url,
                video_url=video_url
            )
        )
        
    return results


@router.get("/media/{filename}", summary="获取日志相关的媒体文件")
async def get_log_media(filename: str):
    """
    提供对存储在服务器上的截图或视频文件的访问。
    """
    file_path = os.path.join(MEDIA_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件未找到")
    return FileResponse(file_path)


@router.put("/{log_id}", response_model=LogInDB, summary="更新日志描述（仅管理员）")
async def update_log_description(
    log_id: int,
    description: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: models.UserInfo = Depends(get_current_user)
):
    if current_user.user_class != "管理员":
        raise HTTPException(status_code=403, detail="权限不足")
    db_log = db.query(models.SystemLog).filter(models.SystemLog.id == log_id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="日志未找到")
    db_log.description = description
    db.commit()
    db.refresh(db_log)

    # 构建返回
    ss_filename = f"{log_id}_screenshot.png"
    vid_filename = f"{log_id}_video.webm"
    screenshot_url = f"/api/log/media/{ss_filename}" if os.path.exists(os.path.join(MEDIA_DIR, ss_filename)) else None
    video_url = f"/api/log/media/{vid_filename}" if os.path.exists(os.path.join(MEDIA_DIR, vid_filename)) else None

    return LogInDB(
        id=db_log.id,
        userID=db_log.userID,
        username=db_log.username,
        logtype=db_log.logtype,
        description=db_log.description,
        timestamp=db_log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if db_log.timestamp else "N/A",
        screenshot_url=screenshot_url,
        video_url=video_url,
    )


@router.delete("/{log_id}", status_code=204, summary="删除一条系统日志")
async def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: models.UserInfo = Depends(get_current_user)
):
    """
    删除一条系统日志及其关联的媒体文件（仅限管理员）。
    """
    if current_user.user_class != "管理员":
        raise HTTPException(status_code=403, detail="权限不足")

    db_log = db.query(models.SystemLog).filter(models.SystemLog.id == log_id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="日志未找到")

    # 删除关联的媒体文件
    ss_path = os.path.join(MEDIA_DIR, f"{log_id}_screenshot.png")
    vid_path = os.path.join(MEDIA_DIR, f"{log_id}_video.webm")
    if os.path.exists(ss_path):
        os.remove(ss_path)
    if os.path.exists(vid_path):
        os.remove(vid_path)

    # 删除数据库记录
    db.delete(db_log)
    db.commit()

    return Response(status_code=204) 
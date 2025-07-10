# from fastapi import APIRouter, UploadFile, File, HTTPException
# from fastapi.responses import JSONResponse
# from detect.inference import predict_disease
#
# import shutil
# import os
# import uuid
#
# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
#
# router = APIRouter()
#
# @router.post("/detect")
# async def detect_disease(file: UploadFile = File(...)):
#     # 1. 获取文件信息
#     filename = file.filename
#     ext = os.path.splitext(filename)[1].lower()
#     if ext not in [".jpg", ".jpeg", ".png", ".mp4"]:
#         raise HTTPException(status_code=400, detail="仅支持图像或视频（.jpg/.png/.mp4）")
#
#     # 2. 生成唯一文件名，防止重名覆盖
#     unique_name = f"{uuid.uuid4().hex}{ext}"
#     save_path = os.path.join(UPLOAD_DIR, unique_name)
#
#     # 3. 保存文件到服务器
#     with open(save_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#
#     # 4. 调用模型识别
#     predict_result = predict_disease(save_path)
#
#     # 5. 返回识别结果
#     return JSONResponse(content={
#         "status": "success",
#         "original_filename": filename,
#         "saved_path": save_path,
#         "results": predict_result["result"],
#         "message": "病害识别成功"
#     })


from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from detect.inference import predict_disease
from .traffic_visualization.service import router as traffic_router
from .road_detection.service import router as road_router
from .face_recognition.service import router as face_router

import shutil
import os
import uuid

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

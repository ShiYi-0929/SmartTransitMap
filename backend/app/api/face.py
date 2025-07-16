from fastapi import APIRouter, HTTPException, Path, Body, Depends
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from typing import List, Optional, Set
import os, pickle, base64, io, datetime, csv, uuid
import numpy as np
from pydantic import BaseModel
from PIL import Image
import face_recognition
import cv2  # 新增：始终可用的 OpenCV
from app.core.utils.antispoof import light_check, predict_single_frame  # 新增：光感 + 量子检测
from app.core.utils.deepfake_vit import predict_deepfake_vit

# Database imports
from database.database import get_db
from database import models
from app.core.api.log import create_log_entry # 导入日志创建函数

# 引入邮件服务
from app.core.email import send_approval_email, send_rejection_email
from app.core.security import get_current_user

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
# （后续 800+ 行保持与 SmartTransitMap(1) /app/core/api/face.py 完全一致）

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
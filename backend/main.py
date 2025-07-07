from fastapi import FastAPI
from app.api import user, face, road, traffic, log

app = FastAPI(
    title="SmartTransitMap 后端API",
    description="智能交通与路面病害检测平台后端",
    version="1.0.0"
)

# 路由注册
app.include_router(user.router, prefix="/api/user", tags=["用户与认证"])
app.include_router(face.router, prefix="/api/face", tags=["人脸识别"])
app.include_router(road.router, prefix="/api/road", tags=["路面病害检测"])
app.include_router(traffic.router, prefix="/api/traffic", tags=["交通数据"])
app.include_router(log.router, prefix="/api/log", tags=["日志与告警"]) 
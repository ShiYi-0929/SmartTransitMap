from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from detect.routes import router as detect_router
from app.api import user, log, road, traffic, face # Import all routers

app = FastAPI()

# --- 配置 CORS 中间件 ---
# 允许所有来源，所有方法，所有头，这在开发环境中很常见
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 包含所有 API 路由 ---
app.include_router(detect_router, prefix="/api", tags=["detect"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(log.router, prefix="/api/log", tags=["log"])
app.include_router(road.router, prefix="/api/road", tags=["road"])
app.include_router(traffic.router, prefix="/api/traffic", tags=["traffic"])
app.include_router(face.router, prefix="/api/face", tags=["face"])

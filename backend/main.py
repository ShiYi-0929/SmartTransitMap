# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from detect.routes import router as detect_router
# from app.api import user, log, road, traffic, face # Import all routers
#
# app = FastAPI()
#
# # --- 配置 CORS 中间件 ---
# # 允许所有来源，所有方法，所有头，这在开发环境中很常见
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # --- 包含所有 API 路由 ---
# app.include_router(detect_router, prefix="/api", tags=["detect"])
# app.include_router(user.router, prefix="/api/user", tags=["user"])
# app.include_router(log.router, prefix="/api/log", tags=["log"])
# app.include_router(road.router, prefix="/api/road", tags=["road"])
# app.include_router(traffic.router, prefix="/api/traffic", tags=["traffic"])
# app.include_router(face.router, prefix="/api/face", tags=["face"])


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from detect.routes import api_router as detect_router
from app.api import user, log, road, face # Import all routers
import uvicorn

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
app.include_router(face.router, prefix="/api/face", tags=["face"])


print("\n=== API 路由列表 ===")
for route in app.routes:
    print(route.path)

if __name__ == "__main__":
    print("\n=== 启动服务器 ===")
    print("监听地址: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
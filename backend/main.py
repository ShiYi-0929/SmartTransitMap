from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from detect.routes import router as detect_router
# 修正导入路径，使用 app.core.api 中的完整路由
from app.core.api import user, log, road, traffic, face, admin
from database.database import Base, engine
from app.core.utils.antispoof import load_model as load_antispoof_model
from app.core.utils.deepfake_vit import load_deepfake_vit_model


app = FastAPI()

# --- 配置 CORS 中间件 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 包含所有 API 路由 ---
# 包含检测模块的路由
app.include_router(detect_router, prefix="/detect", tags=["detect"])

# 包含核心业务模块的路由
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(log.router, prefix="/api/log", tags=["log"])
app.include_router(road.router, prefix="/api/road", tags=["road"])
app.include_router(traffic.router, prefix="/api/traffic", tags=["traffic"])
app.include_router(face.router, prefix="/api/face", tags=["face"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# --- 应用初始化 ---
# 创建所有数据库表
@app.on_event("startup")
async def startup_event():
    """应用启动时加载所有模型"""
    print("开始加载所有模型...")
    load_antispoof_model() # 加载量子反欺诈模型
    load_deepfake_vit_model() # 加载新的ViT深度伪造检测模型
    print("所有模型加载完成。")


# --- 启动服务 ---
if __name__ == "__main__":
    import uvicorn
    print("启动 FastAPI 服务...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_road_detection():
    """道路检测测试端点"""
    return {"message": "Road detection service is working!", "status": "ok"}

@router.post("/detect")
async def detect_road():
    """道路检测功能 - 待实现"""
    return {
        "status": "success",
        "message": "道路检测功能暂未实现",
        "data": None
    }

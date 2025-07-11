from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_face_recognition():
    """人脸识别测试端点"""
    return {"message": "Face recognition service is working!", "status": "ok"}

@router.post("/recognize")
async def recognize_face():
    """人脸识别功能 - 待实现"""
    return {
        "status": "success",
        "message": "人脸识别功能暂未实现",
        "data": None
    }

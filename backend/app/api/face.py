from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/register")
async def register_face(user_id: str, file: UploadFile = File(...)):
    """
    人脸录入接口：上传用户人脸图片，进行注册。
    """
    # TODO: 实现人脸特征提取与存储
    return {"msg": f"用户 {user_id} 人脸录入成功（示例）"}

@router.post("/verify")
async def verify_face(user_id: str, file: UploadFile = File(...)):
    """
    人脸识别接口：上传图片，验证是否为指定用户。
    """
    # TODO: 实现人脸识别与比对
    return {"msg": f"用户 {user_id} 人脸识别结果（示例）"} 
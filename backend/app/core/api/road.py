from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/detect")
async def detect_road_damage(file: UploadFile = File(...)):
    """
    路面病害检测接口：上传路面图片，返回检测结果。
    """
    # TODO: 实现路面病害检测模型推理
    return {"msg": "路面病害检测结果（示例）"}

@router.get("/result/{task_id}")
async def get_detection_result(task_id: str):
    """
    查询检测结果接口。
    """
    # TODO: 查询检测任务结果
    return {"task_id": task_id, "result": "检测结果（示例）"} 
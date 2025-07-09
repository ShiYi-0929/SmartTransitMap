import os, pickle, base64, io
from typing import List

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

# 如果您更倾向于调用已有 dlib 代码，可在此替换为自定义特征提取函数。
import face_recognition  # pip install face_recognition

ENC_FILE = "encodings.pkl"

app = FastAPI(title="Face Recognition API")

# 允许所有来源跨域，方便前端本地调试
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_db() -> List[dict]:
    if os.path.exists(ENC_FILE):
        with open(ENC_FILE, "rb") as f:
            return pickle.load(f)
    return []


def save_db(db: List[dict]):
    with open(ENC_FILE, "wb") as f:
        pickle.dump(db, f)


known_faces: List[dict] = load_db()  # 每项: {"name": str, "enc": np.ndarray}


class RegisterBody(BaseModel):
    name: str
    image: str  # dataURL base64 格式，如: data:image/png;base64,xxxx


class VerifyBody(BaseModel):
    image: str


def dataurl_to_ndarray(data_url: str) -> np.ndarray:
    """将 dataURL(base64) 转换为 RGB ndarray"""
    try:
        header, b64data = data_url.split(",", 1)
    except ValueError:
        raise HTTPException(400, "图片格式不正确，需为 dataURL")
    img_bytes = base64.b64decode(b64data)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)


@app.get("/")
async def root():
    return {"status": "running", "faces_in_db": len(known_faces)}


@app.post("/register")
async def register(body: RegisterBody):
    img = dataurl_to_ndarray(body.image)
    encs = face_recognition.face_encodings(img)
    if not encs:
        raise HTTPException(400, "未检测到人脸")
    known_faces.append({"name": body.name, "enc": encs[0]})
    save_db(known_faces)
    return {"msg": "ok", "faces_in_db": len(known_faces)}


@app.post("/verify")
async def verify(body: VerifyBody):
    img = dataurl_to_ndarray(body.image)
    encs = face_recognition.face_encodings(img)
    if not encs:
        raise HTTPException(400, "未检测到人脸")
    if not known_faces:
        return {"result": "unknown"}

    q_enc = encs[0]
    distances = face_recognition.face_distance([k["enc"] for k in known_faces], q_enc)
    idx = int(np.argmin(distances))
    match_name = known_faces[idx]["name"] if distances[idx] < 0.5 else "unknown"
    return {
        "result": match_name,
        "distance": float(distances[idx]),
        "threshold": 0.5,
    }


# 运行方式: uvicorn backend.app:app --reload --port 8000 
import os, pickle, base64, io, datetime, csv, uuid
from typing import List, Optional, Set

import numpy as np
from fastapi import FastAPI, HTTPException, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

# 如果您更倾向于调用已有 dlib 代码，可在此替换为自定义特征提取函数。
import face_recognition  # pip install face_recognition

ENC_FILE = "encodings.pkl"
CSV_FILE = "faces.csv"
# 静态目录使用绝对路径，避免启动目录影响
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "faces_images")
ENC_FILE = os.path.join(BASE_DIR, "encodings.pkl")
CSV_FILE = os.path.join(BASE_DIR, "faces.csv")

# 确保图片目录存在
os.makedirs(IMAGES_DIR, exist_ok=True)

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


# 便捷函数：从磁盘重新加载已知人脸到内存
def load_known_faces():
    global known_faces
    known_faces = load_db()


# known_faces: 每项 {"id": str, "name": str, "enc": np.ndarray}
# 兼容旧数据（无 id），启动时为其补一个 uuid
tmp_faces = load_db()
known_faces: List[dict] = []
for item in tmp_faces:
    if "id" not in item:
        item["id"] = uuid.uuid4().hex
    known_faces.append(item)

# ---------------- CSV 辅助函数 -----------------


def upsert_csv(person_id: str, name: str, filename: str):
    """插入或更新 CSV 记录，images 列保存所有文件名(逗号分隔)"""
    rows = []
    found = False
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("id") == person_id:
                    imgs = row.get("images", "").split(",") if row.get("images") else []
                    imgs.append(filename)
                    # 更新代表照为最新，更新 images 列
                    row.update({"name": name, "image": filename, "images": ",".join(imgs)})
                    found = True
                rows.append(row)

    if not found:
        rows.append({"id": person_id, "name": name, "image": filename, "images": filename})

    # 重写文件
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "image", "images"])
        writer.writeheader()
        writer.writerows(rows)


def read_csv_records() -> List[dict]:
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = []
        for row in reader:
            img_file = row.get("image", "")
            img_url = f"/images/{img_file}" if img_file else ""
            records.append({
                "id": row.get("id", ""),
                "name": row.get("name", ""),
                "image": img_url,
                "images": row.get("images", "")  # 原始文件名列表（逗号分隔）
            })
        return records


class RegisterBody(BaseModel):
    name: str
    person_id: Optional[str] = None  # 已存在用户的唯一ID
    # 兼容老版本：单张图片
    image: Optional[str] = None  # dataURL base64
    images: Optional[List[str]] = None


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
    # 1. 收集需要处理的图片列表
    if body.images:
        img_list = body.images
    elif body.image:
        img_list = [body.image]
    else:
        raise HTTPException(400, "缺少 image 或 images 字段")

    # ------------------ ID 处理 ------------------
    # 姓名字段不再使用，统一使用用户 ID
    # 必须提供 person_id（用户ID）
    if not body.person_id:
        raise HTTPException(400, "person_id (用户ID) 必填")

    person_id = body.person_id

    # name 一律保存为 person_id，保证前端显示一致
    effective_name = person_id

    encodings = []
    # 用第一张图片做 UI 预览 & 保存文件
    first_img_b64 = img_list[0]

    # ---- 使用 dlib 裁切人脸有效区域，并基于裁切结果计算特征 ----
    cropped_arrays = []  # 保存裁剪后的 ndarray 供后续写文件

    for data_url in img_list:
        img = dataurl_to_ndarray(data_url)

        # 查找所有人脸 (top, right, bottom, left)
        locations = face_recognition.face_locations(img)

        if locations:
            # 取面积最大的那张脸
            areas = [(b - t) * (r - l) for t, r, b, l in locations]
            top, right, bottom, left = locations[int(np.argmax(areas))]
            face_img = img[top:bottom, left:right].copy()
        else:
            # 若未检测到人脸，退回使用整张
            face_img = img

        cropped_arrays.append(face_img)

        h, w, _ = face_img.shape
        # 提供整张框坐标，避免 dlib 类型错误
        encs = face_recognition.face_encodings(face_img, [(0, w, h, 0)])
        if encs:
            encodings.append(encs[0])

    # 2. 保存所有照片文件
    file_names = []
    timestamp_prefix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    for idx, arr in enumerate(cropped_arrays):
        fname = f"{timestamp_prefix}_{idx}_{uuid.uuid4().hex[:6]}.png"
        fp = os.path.join(IMAGES_DIR, fname)
        Image.fromarray(arr).save(fp)
        file_names.append(fname)

    # 代表照取第一张
    filename = file_names[0]

    # 3. 处理特征：如果有多张，则取平均
    face_saved = False
    if encodings:
        avg_enc = np.mean(encodings, axis=0)
        updated = False
        for k in known_faces:
            if k["id"] == person_id:
                k["enc"] = (k["enc"] + avg_enc) / 2
                k["name"] = effective_name  # 姓名即 ID
                updated = True
                break

        if not updated:
            known_faces.append({"id": person_id, "name": effective_name, "enc": avg_enc})
        save_db(known_faces)
        face_saved = True

    # 4. 记录 CSV - 逐张追加（name 统一用 ID）
    for fn in file_names:
        upsert_csv(person_id, effective_name, fn)

    return {
        "msg": "ok",
        "faces_in_db": len(known_faces),
        "face_saved": face_saved,
        "images_received": len(img_list),
        "person_id": person_id,
    }


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
    match_id = known_faces[idx]["id"] if distances[idx] < 0.5 else None
    return {
        "result": match_name,
        "person_id": match_id,
        "distance": float(distances[idx]),
        "threshold": 0.5,
    }


# -------- 获取已录入姓名列表 --------


@app.get("/faces")
async def list_faces():
    return {"faces": read_csv_records()}

# -------- 静态文件挂载 --------

from fastapi.staticfiles import StaticFiles

app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# ----------------- 删除功能 -----------------

def rewrite_csv(records_to_keep: List[dict]):
    """用保留的记录重写CSV文件"""
    if not records_to_keep:
        # 如果全部删除，则直接删除文件
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        return
    
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "image", "images"])
        writer.writeheader()
        # image 字段只保留文件名
        writer.writerows([
            {
                "id": r["id"],
                "name": r["name"],
                "image": os.path.basename(r["image"].replace("/images/", "")),
                "images": r.get("images", "")
            }
            for r in records_to_keep
        ])

@app.delete("/faces/{person_id}")
async def delete_face(person_id: str = Path(..., description="要删除用户的唯一ID")):
    global known_faces
    
    # 1. 从 CSV 中查找并准备删除
    all_records = read_csv_records()
    record_to_delete = None
    records_to_keep_csv = []
    for r in all_records:
        if r.get("id") == person_id:
            record_to_delete = r
        else:
            records_to_keep_csv.append(r)

    if not record_to_delete:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 2. 从 .pkl (known_faces) 中删除
    known_faces = [face for face in known_faces if face["id"] != person_id]
    save_db(known_faces)

    # 3. 删除该用户的全部图片文件（代表照 image 以及 images 列表中的其余图片）
    filenames: Set[str] = set()

    # (1) 代表照
    image_rep = record_to_delete.get("image", "")
    if image_rep:
        filenames.add(os.path.basename(image_rep))

    # (2) images 字段可能包含多张，以逗号分隔
    imgs_field = record_to_delete.get("images", "")
    if imgs_field:
        for fn in [s.strip() for s in imgs_field.split(",") if s.strip()]:
            filenames.add(os.path.basename(fn))

    # 执行删除
    for fn in filenames:
        fp = os.path.join(IMAGES_DIR, fn)
        if os.path.exists(fp):
            try:
                os.remove(fp)
            except OSError:
                pass
    
    # 4. 重写 CSV 文件
    rewrite_csv(records_to_keep_csv)

    return {"msg": f"用户已删除", "person_id": person_id}

# -------- 清空全部人脸数据 --------

@app.delete("/faces")
async def delete_all_faces():
    """删除已录入的全部人脸数据（内存、encodings.pkl、CSV、图片）。"""
    global known_faces

    # 1. 清空内存
    known_faces = []
    save_db(known_faces)  # 这一步会把 encodings.pkl 重写为空

    # 2. 删除 encodings.pkl 文件
    if os.path.exists(ENC_FILE):
        try:
            os.remove(ENC_FILE)
        except OSError:
            pass

    # 3. 删除 CSV 文件
    if os.path.exists(CSV_FILE):
        try:
            os.remove(CSV_FILE)
        except OSError:
            pass

    # 4. 删除所有图片文件
    if os.path.exists(IMAGES_DIR):
        for fname in os.listdir(IMAGES_DIR):
            fp = os.path.join(IMAGES_DIR, fname)
            if os.path.isfile(fp):
                try:
                    os.remove(fp)
                except OSError:
                    pass

    return {"msg": "所有人脸数据已清空"}

# 运行方式: uvicorn backend.app:app --reload --port 8000 

@app.get("/faces/{person_id}/images")
async def list_person_images(person_id: str):
    records = read_csv_records()
    for r in records:
        if r["id"] == person_id:
            imgs = r.get("images", "")
            files = [f.strip() for f in imgs.split(",") if f.strip()]
            urls = [f"/images/{fn}" for fn in files]
            return {"images": urls}
    raise HTTPException(404, "用户不存在") 

# ### 新接口：更新姓名 ###


@app.put("/faces/{person_id}")
async def update_face_name(person_id: str, name: str = Body(..., embed=True)):
    """更新指定用户姓名"""
    # 更新内存
    updated = False
    for k in known_faces:
        if k["id"] == person_id:
            k["name"] = name
            updated = True
            break
    if updated:
        save_db(known_faces)

    # 更新 CSV
    if os.path.exists(CSV_FILE):
        rows = []
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("id") == person_id:
                    row["name"] = name
                rows.append(row)
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name", "image", "images"])
            writer.writeheader()
            writer.writerows(rows)

    if not updated:
        raise HTTPException(404, "用户不存在")
    return {"msg": "姓名已更新", "person_id": person_id, "name": name}


# ### 新接口：删除指定图片 ###


@app.delete("/faces/{person_id}/images/{filename}")
async def delete_person_image(person_id: str, filename: str):
    """删除某人的一张图片"""
    # 1. 删除硬盘文件
    safe_name = os.path.basename(filename)
    filepath = os.path.join(IMAGES_DIR, safe_name)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass

    # 2. 更新 CSV 行 images/image
    if not os.path.exists(CSV_FILE):
        raise HTTPException(404, "记录不存在")

    rows = []
    target_row = None
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id") == person_id:
                imgs = row.get("images", "").split(",") if row.get("images") else []
                imgs = [img for img in imgs if img != safe_name]
                row["images"] = ",".join(imgs)
                # 代表照 image 字段：若删除的是代表照，则改用第一张或空
                if row.get("image") == safe_name:
                    row["image"] = imgs[0] if imgs else ""
                target_row = row
            rows.append(row)

    if target_row is None:
        raise HTTPException(404, "用户不存在")

    # 如果全部图片被删光，可保留行但 image 为空
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "image", "images"])
        writer.writeheader()
        writer.writerows(rows)

    load_known_faces()  # Reload faces after deleting an entry
    return {"msg": "图片已删除", "remaining": target_row.get("images", "")} 

class CheckFaceBody(BaseModel):
    image: str


@app.post("/check_face_in_frame")
async def check_face_in_frame(body: CheckFaceBody):
    """检查单张图片中的人脸是否在中心区域"""
    try:
        img_array = dataurl_to_ndarray(body.image)
        # RGBA to RGB
        if img_array.shape[2] == 4:
            img_array = img_array[:, :, :3]

        face_locations = face_recognition.face_locations(img_array)

        if not face_locations:
            return {"in_frame": False, "reason": "no_face_detected"}

        # 使用最大的人脸进行判断
        face_areas = [(bottom - top) * (right - left) for top, right, bottom, left in face_locations]
        top, right, bottom, left = face_locations[np.argmax(face_areas)]

        face_center_x = (left + right) / 2
        face_center_y = (top + bottom) / 2

        h, w, _ = img_array.shape
        center_box_left = w * 0.2
        center_box_right = w * 0.8
        center_box_top = h * 0.2
        center_box_bottom = h * 0.8

        in_horizontal = center_box_left < face_center_x < center_box_right
        in_vertical = center_box_top < face_center_y < center_box_bottom

        return {"in_frame": in_horizontal and in_vertical}

    except Exception as e:
        print(f"Error in check_face_in_frame: {e}")
        return {"in_frame": False, "reason": "server_error"} 

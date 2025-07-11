from fastapi import APIRouter, HTTPException, Path, Body, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Optional, Set
import os, pickle, base64, io, datetime, csv, uuid
import numpy as np
from pydantic import BaseModel
from PIL import Image
import face_recognition  # 依赖 dlib

router = APIRouter()

# ---- 路径与持久化文件 ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "..", "faces_data")
IMAGES_DIR = os.path.join(DATA_DIR, "faces_images")
ENC_FILE = os.path.join(DATA_DIR, "encodings.pkl")
CSV_FILE = os.path.join(DATA_DIR, "faces.csv")

os.makedirs(IMAGES_DIR, exist_ok=True)

# ----------------- 工具函数 -----------------

def load_db() -> List[dict]:
    if os.path.exists(ENC_FILE):
        with open(ENC_FILE, "rb") as f:
            return pickle.load(f)
    return []

def save_db(db: List[dict]):
    with open(ENC_FILE, "wb") as f:
        pickle.dump(db, f)

def upsert_csv(person_id: str, name: str, filename: str):
    rows = []
    found = False
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("id") == person_id:
                    imgs = row.get("images", "").split(",") if row.get("images") else []
                    imgs.append(filename)
                    row.update({"name": name, "image": filename, "images": ",".join(imgs)})
                    found = True
                rows.append(row)
    if not found:
        rows.append({"id": person_id, "name": name, "image": filename, "images": filename})
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
                "images": row.get("images", "")
            })
        return records

# ----------------- 数据模型 -----------------
class RegisterBody(BaseModel):
    name: str
    person_id: Optional[str] = None
    image: Optional[str] = None
    images: Optional[List[str]] = None

class VerifyBody(BaseModel):
    image: str

class CheckFaceBody(BaseModel):
    image: str

# ----------------- 内存加载 -----------------
_tmp_faces = load_db()
known_faces: List[dict] = []
for item in _tmp_faces:
    if "id" not in item:
        item["id"] = uuid.uuid4().hex
    known_faces.append(item)

# ----------------- 辅助函数 -----------------

def dataurl_to_ndarray(data_url: str) -> np.ndarray:
    try:
        header, b64data = data_url.split(",", 1)
    except ValueError:
        raise HTTPException(400, "图片格式不正确，需为 dataURL")
    img_bytes = base64.b64decode(b64data)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)

# ----------------- API -----------------
@router.get("/")
async def root():
    return {"status": "running", "faces_in_db": len(known_faces)}

@router.get("/images/{filename}")
async def get_image(filename: str):
    safe_name = os.path.basename(filename)
    filepath = os.path.join(IMAGES_DIR, safe_name)
    if not os.path.exists(filepath):
        raise HTTPException(404, "图片不存在")
    return FileResponse(filepath)

@router.post("/register")
async def register(body: RegisterBody):
    if body.images:
        img_list = body.images
    elif body.image:
        img_list = [body.image]
    else:
        raise HTTPException(400, "缺少 image 或 images 字段")

    if not body.person_id:
        raise HTTPException(400, "person_id (用户ID) 必填")
    person_id = body.person_id
    effective_name = person_id

    encodings = []
    cropped_arrays = []
    for data_url in img_list:
        img = dataurl_to_ndarray(data_url)
        locations = face_recognition.face_locations(img)
        if locations:
            areas = [(b - t) * (r - l) for t, r, b, l in locations]
            top, right, bottom, left = locations[int(np.argmax(areas))]
            face_img = img[top:bottom, left:right].copy()
        else:
            face_img = img
        cropped_arrays.append(face_img)
        h, w, _ = face_img.shape
        encs = face_recognition.face_encodings(face_img, [(0, w, h, 0)])
        if encs:
            encodings.append(encs[0])

    file_names = []
    timestamp_prefix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    for idx, arr in enumerate(cropped_arrays):
        fname = f"{timestamp_prefix}_{idx}_{uuid.uuid4().hex[:6]}.png"
        fp = os.path.join(IMAGES_DIR, fname)
        Image.fromarray(arr).save(fp)
        file_names.append(fname)
    filename = file_names[0]

    face_saved = False
    if encodings:
        avg_enc = np.mean(encodings, axis=0)
        updated = False
        for k in known_faces:
            if k["id"] == person_id:
                k["enc"] = (k["enc"] + avg_enc) / 2
                k["name"] = effective_name
                updated = True
                break
        if not updated:
            known_faces.append({"id": person_id, "name": effective_name, "enc": avg_enc})
        save_db(known_faces)
        face_saved = True

    for fn in file_names:
        upsert_csv(person_id, effective_name, fn)

    return {
        "msg": "ok",
        "faces_in_db": len(known_faces),
        "face_saved": face_saved,
        "images_received": len(img_list),
        "person_id": person_id,
    }

@router.post("/verify")
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

@router.get("/faces")
async def list_faces():
    return {"faces": read_csv_records()}

# ---- 删除与更新 ----

def rewrite_csv(records_to_keep: List[dict]):
    if not records_to_keep:
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        return
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "image", "images"])
        writer.writeheader()
        writer.writerows([
            {
                "id": r["id"],
                "name": r["name"],
                "image": os.path.basename(r["image"].replace("/images/", "")),
                "images": r.get("images", "")
            } for r in records_to_keep
        ])

@router.delete("/faces/{person_id}")
async def delete_face(person_id: str = Path(...)):
    global known_faces
    all_records = read_csv_records()
    record_to_delete = None
    records_to_keep_csv = []
    for r in all_records:
        if r.get("id") == person_id:
            record_to_delete = r
        else:
            records_to_keep_csv.append(r)
    if not record_to_delete:
        raise HTTPException(404, "用户不存在")
    known_faces = [face for face in known_faces if face["id"] != person_id]
    save_db(known_faces)
    filenames: Set[str] = set()
    if record_to_delete.get("image"):
        filenames.add(os.path.basename(record_to_delete["image"]))
    imgs_field = record_to_delete.get("images", "")
    if imgs_field:
        for fn in [s.strip() for s in imgs_field.split(",") if s.strip()]:
            filenames.add(os.path.basename(fn))
    for fn in filenames:
        fp = os.path.join(IMAGES_DIR, fn)
        if os.path.exists(fp):
            try:
                os.remove(fp)
            except OSError:
                pass
    rewrite_csv(records_to_keep_csv)
    return {"msg": "用户已删除", "person_id": person_id}

@router.delete("/faces")
async def delete_all_faces():
    global known_faces
    known_faces = []
    save_db(known_faces)
    if os.path.exists(ENC_FILE):
        try:
            os.remove(ENC_FILE)
        except OSError:
            pass
    if os.path.exists(CSV_FILE):
        try:
            os.remove(CSV_FILE)
        except OSError:
            pass
    if os.path.exists(IMAGES_DIR):
        for fname in os.listdir(IMAGES_DIR):
            fp = os.path.join(IMAGES_DIR, fname)
            if os.path.isfile(fp):
                try:
                    os.remove(fp)
                except OSError:
                    pass
    return {"msg": "所有人脸数据已清空"}

@router.get("/faces/{person_id}/images")
async def list_person_images(person_id: str):
    records = read_csv_records()
    for r in records:
        if r["id"] == person_id:
            files = [f.strip() for f in r.get("images", "").split(",") if f.strip()]
            urls = [f"/images/{fn}" for fn in files]
            return {"images": urls}
    raise HTTPException(404, "用户不存在")

@router.put("/faces/{person_id}")
async def update_face_name(person_id: str, name: str = Body(..., embed=True)):
    updated = False
    for k in known_faces:
        if k["id"] == person_id:
            k["name"] = name
            updated = True
            break
    if updated:
        save_db(known_faces)
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

@router.delete("/faces/{person_id}/images/{filename}")
async def delete_person_image(person_id: str, filename: str):
    safe_name = os.path.basename(filename)
    filepath = os.path.join(IMAGES_DIR, safe_name)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass
    if not os.path.exists(CSV_FILE):
        raise HTTPException(404, "记录不存在")
    rows = []
    target_row = None
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id") == person_id:
                target_row = row
            rows.append(row)
    if not target_row:
        raise HTTPException(404, "用户不存在")
    imgs = target_row.get("images", "").split(",") if target_row.get("images") else []
    imgs = [i for i in imgs if os.path.basename(i) != safe_name]
    target_row["images"] = ",".join(imgs)
    target_row["image"] = imgs[0] if imgs else ""
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "image", "images"])
        writer.writeheader()
        writer.writerows(rows)
    return {"msg": "图片已删除"}

@router.post("/check_face_in_frame")
async def check_face_in_frame(body: CheckFaceBody):
    img = dataurl_to_ndarray(body.image)
    encs = face_recognition.face_encodings(img)
    in_frame = bool(encs)
    return {"in_frame": in_frame} 
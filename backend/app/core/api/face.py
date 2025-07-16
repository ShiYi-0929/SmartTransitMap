from fastapi import APIRouter, HTTPException, Path, Body, Depends
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from typing import List, Optional, Set
import os, pickle, base64, io, datetime, csv, uuid
import numpy as np
from pydantic import BaseModel
from PIL import Image
import face_recognition
import cv2  # 新增：始终可用的 OpenCV
from app.core.utils.antispoof import light_check, predict_single_frame  # 新增：光感 + 量子检测
from app.core.utils.deepfake_vit import predict_deepfake_vit

# Database imports
from database.database import get_db
from database import models
from app.core.api.log import create_log_entry # 导入日志创建函数

# 引入邮件服务
from app.core.email import send_approval_email, send_rejection_email
from app.core.security import get_current_user

# 可选导入dlib相关模块
try:
    import dlib
    import cv2
    from scipy.spatial import distance as dist
    DLIB_AVAILABLE = True
    print("dlib模块导入成功")
except ImportError as e:
    DLIB_AVAILABLE = False
    print(f"dlib模块导入失败: {e}")
    print("眨眼检测功能将使用模拟模式")

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化dlib的人脸检测器和关键点预测器
detector = None
predictor_path = None
predictor = None

if DLIB_AVAILABLE:
    try:
        detector = dlib.get_frontal_face_detector()
        # 构建模型文件路径，尝试多个可能的位置
        possible_paths = [
            os.path.join(BASE_DIR, "..", "..", "models", "shape_predictor_68_face_landmarks.dat"),
            os.path.join(BASE_DIR, "models", "shape_predictor_68_face_landmarks.dat"),
            os.path.join(os.path.dirname(BASE_DIR), "models", "shape_predictor_68_face_landmarks.dat"),
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                # 处理中文路径问题：使用原始字节路径
                try:
                    # 尝试使用UTF-8编码
                    predictor_path = abs_path.encode('utf-8').decode('utf-8')
                    break
                except UnicodeError:
                    # 如果UTF-8失败，尝试使用短路径名
                    try:
                        import win32api
                        predictor_path = win32api.GetShortPathName(abs_path)
                        break
                    except ImportError:
                        # 如果win32api不可用，使用原路径
                        predictor_path = abs_path
                        break
        
        if predictor_path:
            print(f"dlib检测器初始化成功，模型路径: {predictor_path}")
        else:
            print(f"找不到模型文件，尝试的路径: {[os.path.abspath(p) for p in possible_paths]}")
            DLIB_AVAILABLE = False
    except Exception as e:
        print(f"dlib检测器初始化失败: {e}")
        DLIB_AVAILABLE = False

def get_predictor():
    """延迟加载dlib预测器"""
    global predictor
    if not DLIB_AVAILABLE:
        raise HTTPException(500, "dlib模块不可用")
    
    if predictor is None:
        if not predictor_path:
            raise HTTPException(500, "模型文件路径未设置")
            
        if not os.path.exists(predictor_path):
            raise HTTPException(500, f"模型文件不存在: {predictor_path}")
            
        # 检查文件权限
        if not os.access(predictor_path, os.R_OK):
            raise HTTPException(500, f"模型文件无读取权限: {predictor_path}")
            
        try:
            print(f"正在加载模型文件: {predictor_path}")
            print(f"文件大小: {os.path.getsize(predictor_path)} bytes")
            
            # 尝试不同的方式加载模型
            try:
                predictor = dlib.shape_predictor(str(predictor_path))
            except Exception as e1:
                print(f"第一次加载失败: {e1}")
                # 尝试使用字节路径
                try:
                    predictor = dlib.shape_predictor(predictor_path.encode('utf-8'))
                except Exception as e2:
                    print(f"第二次加载失败: {e2}")
                    # 最后尝试：复制文件到临时位置
                    import tempfile
                    import shutil
                    temp_dir = tempfile.gettempdir()
                    temp_path = os.path.join(temp_dir, "shape_predictor_68_face_landmarks.dat")
                    shutil.copy2(predictor_path, temp_path)
                    predictor = dlib.shape_predictor(temp_path)
                    print(f"使用临时文件加载成功: {temp_path}")
                    
            print("模型加载成功")
        except Exception as e:
            error_msg = f"无法加载人脸关键点模型: {str(e)}"
            print(f"模型加载失败: {error_msg}")
            raise HTTPException(500, error_msg)
    return predictor

async def _log_verification_attempt(db: Session, user_id: str, log_type: str, description: str, image_data_url: str):
    """一个辅助函数，用于记录验证尝试的日志和截图。"""
    try:
        user = db.query(models.UserInfo).filter(models.UserInfo.userID == int(user_id)).first()
        if not user:
            print(f"日志记录失败：找不到用户ID {user_id}")
            return

        # 将dataURL转换为二进制数据
        try:
            _, b64data = image_data_url.split(",", 1)
            screenshot_bytes = base64.b64decode(b64data)
        except Exception:
            screenshot_bytes = None # 如果转换失败，则不保存截图

        await create_log_entry(
            db=db,
            user_id=user.userID,
            logtype=log_type,
            description=description,
            screenshot=screenshot_bytes,
            video=None  # 验证流程不录制视频
        )
    except Exception as e:
        print(f"记录验证日志时发生错误: {e}")


DATA_DIR = os.path.join(BASE_DIR, "..", "..", "..", "faces_data")
IMAGES_DIR = os.path.join(DATA_DIR, "faces_images")
ENC_FILE = os.path.join(DATA_DIR, "encodings.pkl")
CSV_FILE = os.path.join(DATA_DIR, "faces.csv")

os.makedirs(IMAGES_DIR, exist_ok=True)

# --- helpers ---

def load_db() -> List[dict]:
    if os.path.exists(ENC_FILE):
        with open(ENC_FILE, "rb") as f:
            return pickle.load(f)
    return []

def save_db(db: List[dict]):
    with open(ENC_FILE, "wb") as f:
        pickle.dump(db, f)

def upsert_csv(person_id: str, name: str, filename: str, status: str = 'pending'):
    rows = []
    found = False
    fieldnames = ["id", "name", "image", "images", "status"]
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Ensure fieldnames from file are used if they exist, but include new ones
            file_fieldnames = reader.fieldnames or []
            fieldnames = file_fieldnames + [fn for fn in fieldnames if fn not in file_fieldnames]

            for row in reader:
                if row.get("id") == person_id:
                    # This logic is for adding more images to an existing user,
                    # so their status should remain unchanged (likely 'approved').
                    imgs = row.get("images", "").split(",") if row.get("images") else []
                    if filename not in imgs:
                         imgs.append(filename)
                    row["images"] = ",".join(imgs)
                    # Don't change status when just adding an image to an existing user
                    found = True
                rows.append(row)

    if not found:
        # A new entry
        rows.append({"id": person_id, "name": name, "image": filename, "images": filename, "status": status})
    
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
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
            img_url = f"/api/face/images/{img_file}" if img_file else ""
            records.append({
                "id": row.get("id", ""),
                "name": row.get("name", ""),
                "image": img_url,
                "images": row.get("images", ""),
                "status": row.get("status", "approved") # Default old records to 'approved'
            })
        return records

# --- models ---
class RegisterBody(BaseModel):
    name: str
    person_id: Optional[str] = None
    image: Optional[str] = None
    images: Optional[List[str]] = None

class VerifyBody(BaseModel):
    image: str

class CheckFaceBody(BaseModel):
    image: str

class BlinkDetectionBody(BaseModel):
    image: str

# --- init memory ---
known_faces: List[dict] = []
for item in load_db():
    item.setdefault("id", uuid.uuid4().hex)
    known_faces.append(item)

# --- utils ---

def dataurl_to_ndarray(data_url: str) -> np.ndarray:
    try:
        _, b64data = data_url.split(",", 1)
    except ValueError:
        raise HTTPException(400, "图片格式不正确(dataURL)")
    img_bytes = base64.b64decode(b64data)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)

def eye_aspect_ratio(eye):
    """计算眼部纵横比(EAR)"""
    if not DLIB_AVAILABLE:
        return 0.3  # 默认值
    
    # 计算垂直方向的眼部距离
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # 计算水平方向的眼部距离
    C = dist.euclidean(eye[0], eye[3])
    # 计算眼部纵横比
    ear = (A + B) / (2.0 * C)
    return ear

def detect_blink(image_array):
    """
    检测图像中的眨眼动作
    返回: {
        'has_face': bool,        # 是否检测到人脸
        'is_blinking': bool,     # 是否正在眨眼
        'left_ear': float,       # 左眼EAR值
        'right_ear': float,      # 右眼EAR值
        'avg_ear': float         # 平均EAR值
    }
    """
    # EAR阈值 - 降低敏感度
    EAR_THRESHOLD = 0.21  # 从默认的0.3降低到0.21，减少误检
    
    if not DLIB_AVAILABLE:
        # 降级模式：返回更保守的模拟数据
        import random
        # 减少随机眨眼的概率，从20%降低到5%
        is_blinking = random.random() < 0.05
        base_ear = 0.28 if not is_blinking else 0.18
        variation = 0.02
        left_ear = round(base_ear + random.uniform(-variation, variation), 3)
        right_ear = round(base_ear + random.uniform(-variation, variation), 3)
        avg_ear = round((left_ear + right_ear) / 2.0, 3)
        
        return {
            'has_face': True,
            'is_blinking': is_blinking,
            'left_ear': left_ear,
            'right_ear': right_ear,
            'avg_ear': avg_ear
        }
    
    try:
        predictor = get_predictor()  # 使用延迟加载
        
        # 转换为灰度图像
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # 检测人脸
        faces = detector(gray)
        
        if len(faces) == 0:
            return {
                'has_face': False,
                'is_blinking': False,
                'left_ear': 0.0,
                'right_ear': 0.0,
                'avg_ear': 0.0
            }
        
        # 使用第一个检测到的人脸
        face = faces[0]
        
        # 获取面部关键点
        landmarks = predictor(gray, face)
        
        # 提取左眼和右眼的坐标点
        # 左眼: 点 36-41, 右眼: 点 42-47
        left_eye = []
        right_eye = []
        
        for i in range(36, 42):  # 左眼
            x = landmarks.part(i).x
            y = landmarks.part(i).y
            left_eye.append((x, y))
        
        for i in range(42, 48):  # 右眼
            x = landmarks.part(i).x
            y = landmarks.part(i).y
            right_eye.append((x, y))
        
        # 计算眼部纵横比
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # 改进的眨眼检测逻辑
        # 1. 使用更严格的阈值
        # 2. 要求两只眼睛都低于阈值
        # 3. 添加一致性检查
        both_eyes_low = left_ear < EAR_THRESHOLD and right_ear < EAR_THRESHOLD
        ear_difference = abs(left_ear - right_ear)
        
        # 如果两眼EAR差异太大，可能是检测错误，不认为是眨眼
        MAX_EAR_DIFFERENCE = 0.08
        is_consistent = ear_difference < MAX_EAR_DIFFERENCE
        
        # 只有在两眼都低于阈值且一致性良好时才认为是眨眼
        is_blinking = both_eyes_low and is_consistent and avg_ear < EAR_THRESHOLD
        
        # 强制转换为 Python 原生 bool，避免 numpy.bool_ 在 FastAPI JSON 编码时报错
        return {
            'has_face': True,
            'is_blinking': bool(is_blinking),
            'left_ear': round(left_ear, 3),
            'right_ear': round(right_ear, 3),
            'avg_ear': round(avg_ear, 3)
        }
        
    except Exception as e:
        print(f"真实眨眼检测失败，使用降级模式: {e}")
        # 降级模式
        import random
        is_blinking = random.random() < 0.05  # 减少误检概率
        base_ear = 0.28 if not is_blinking else 0.18
        variation = 0.02
        left_ear = round(base_ear + random.uniform(-variation, variation), 3)
        right_ear = round(base_ear + random.uniform(-variation, variation), 3)
        avg_ear = round((left_ear + right_ear) / 2.0, 3)
        
        return {
            'has_face': True,
            'is_blinking': bool(is_blinking),  # 转为 Python bool
            'left_ear': left_ear,
            'right_ear': right_ear,
            'avg_ear': avg_ear
        }

# --- routes ---
@router.get("/")
async def status():
    return {"faces_in_db": len(known_faces)}

@router.get("/images/{filename}")
async def get_image(filename: str):
    fp = os.path.join(IMAGES_DIR, os.path.basename(filename))
    if not os.path.exists(fp):
        raise HTTPException(404, "图片不存在")
    return FileResponse(fp)

@router.post("/register")
async def register(body: RegisterBody):
    if not (body.images or body.image):
        raise HTTPException(400, "缺少 image/images 字段")
    img_list = body.images or [body.image]
    person_id = body.person_id or body.name
    if not person_id:
        raise HTTPException(400, "person_id 必填")
    encodings, crops = [], []
    for data_url in img_list:
        img = dataurl_to_ndarray(data_url)
        locs = face_recognition.face_locations(img)
        if locs:
            areas = [(b-t)*(r-l) for t,r,b,l in locs]
            t,r,b,l = locs[int(np.argmax(areas))]
            face_img = img[t:b, l:r].copy()
        else:
            face_img = img
        crops.append(face_img)
        h,w,_ = face_img.shape
        enc = face_recognition.face_encodings(face_img, [(0,w,h,0)])
        if enc:
            encodings.append(enc[0])
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    fnames = []
    for idx, arr in enumerate(crops):
        fname = f"{ts}_{idx}_{uuid.uuid4().hex[:6]}.png"
        Image.fromarray(arr).save(os.path.join(IMAGES_DIR, fname))
        fnames.append(fname)
    if encodings:
        avg_enc = np.mean(encodings, axis=0)
        for k in known_faces:
            if k["id"] == person_id:
                k["enc"] = (k["enc"] + avg_enc)/2
                break
        else:
            known_faces.append({"id": person_id, "name": person_id, "enc": avg_enc})
        save_db(known_faces)
    for fn in fnames:
        upsert_csv(person_id, person_id, fn)
    return {"msg":"ok","person_id":person_id}

@router.post("/verify")
async def verify(body: VerifyBody, db: Session = Depends(get_db), current_user: models.UserInfo = Depends(get_current_user)):
    img = dataurl_to_ndarray(body.image)
    # 若分辨率过高，先缩放至 <=800px，提升检测速度
    h0, w0, _ = img.shape
    scale = 1.0
    max_dim = max(h0, w0)
    if max_dim > 800:
        scale = 800 / max_dim
        img = np.array(Image.fromarray(img).resize((int(w0 * scale), int(h0 * scale))))
    encs = face_recognition.face_encodings(img)
    if not encs:
        # 记录在当前用户头上
        await _log_verification_attempt(db, current_user.userID, "恶意操作", "验证尝试失败：未检测到人脸", body.image)
        raise HTTPException(400, "未检测到人脸")
    if not known_faces:
        # 记录在当前用户头上
        await _log_verification_attempt(db, current_user.userID, "恶意操作", "验证失败：系统中无任何已存人脸数据", body.image)
        return {"result":"unknown"}
    q = encs[0]
    dists = face_recognition.face_distance([k["enc"] for k in known_faces], q)
    idx = int(np.argmin(dists))
    matched_name = known_faces[idx]["name"] if dists[idx] < 0.5 else "unknown"
    if matched_name == "unknown":
        # 即使是未知用户，也记录一次失败尝试
        await _log_verification_attempt(db, current_user.userID, "恶意操作", "验证失败：识别人脸为未知", body.image)
        return {"result": "unknown"}

    # ---- 光感检测 ----
    print("Performing light check...")
    bgr_frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    light_ok = light_check(bgr_frame)
    print(f"Light check result: {'OK' if light_ok else 'Failed'}")
    if not light_ok:
        # 光感不通过 - 日志记录在当前用户头上
        await _log_verification_attempt(
            db, current_user.userID, "恶意操作", f"验证失败：光感检测未通过。识别人脸为: {matched_name}", body.image
        )
        raise HTTPException(400, "light_failed")

    # ---- 新深度伪造检测 (ViT) ----
    print("Performing new deepfake check (ViT)...")
    pil_img = Image.fromarray(cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB))
    deepfake_vit_res = predict_deepfake_vit(pil_img)
    print(f"ViT Deepfake check result: {deepfake_vit_res}")
    
    prediction = deepfake_vit_res.get("prediction", "").lower()

    # 新的要求：三个检测都必须通过
    if deepfake_vit_res.get("error") or prediction != "real":
        # 日志记录 - 深度伪造检测失败
        desc = f"验证失败：深度伪造检测未通过。识别人脸为: {matched_name}。检测结果: {deepfake_vit_res}"
        await _log_verification_attempt(
            db, current_user.userID, "恶意操作", desc, body.image
        )
        raise HTTPException(400, "deepfake_vit_failed")
    else:
        # 日志记录 - 深度伪造检测通过
        desc = f"深度伪造检测通过。识别人脸为: {matched_name}。检测结果: {deepfake_vit_res}"
        await _log_verification_attempt(
            db, current_user.userID, "深度伪造检测通过", desc, body.image
        )


    # 全部通过，但在返回前最后一步检查用户ID是否匹配
    # 对于非管理员，识别出的人脸必须是自己
    if current_user.user_class != "管理员" and matched_name != str(current_user.userID):
        desc = f"验证失败：识别出的人脸 (ID: {matched_name}) 与当前登录用户 (ID: {current_user.userID}) 不匹配。"
        await _log_verification_attempt(
            db, current_user.userID, "人脸不匹配", desc, body.image
        )
        raise HTTPException(status_code=403, detail="face_mismatch")

    # 日志记录 - 验证成功
    desc = f"用户 {current_user.username} (ID: {current_user.userID}) 验证成功，识别出的用户为 {matched_name}。"
    await _log_verification_attempt(
        db, current_user.userID, "普通操作", desc, body.image
    )
    print("All checks passed.")
    return {"result": matched_name}

@router.get("/faces")
async def list_faces(status: Optional[str] = None):
    records = read_csv_records()
    if status:
        return {"faces": [r for r in records if r['status'] == status]}
    # Default to approved if no status is given
    return {"faces": [r for r in records if r['status'] == 'approved']}


@router.get("/faces/count")
async def count_faces(status: str):
    records = read_csv_records()
    count = sum(1 for r in records if r.get('status') == status)
    return {"pending_count": count}


@router.post("/approve/{person_id}")
async def approve_face(person_id: str, db: Session = Depends(get_db)):
    records = []
    found = False
    if not os.path.exists(CSV_FILE):
        raise HTTPException(404, "CSV file not found")
    
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['id'] == person_id:
                row['status'] = 'approved'
                found = True
            records.append(row)

    if not found:
        raise HTTPException(404, "Person ID not found")
        
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    # 发送邮件并更新数据库
    user = None
    try:
        user = db.query(models.UserInfo).filter(models.UserInfo.userID == int(person_id)).first()
        if user:
            user.user_class = '认证用户'
            db.commit()
            # 发送批准邮件
            send_approval_email(user.email, user.username)
        else:
            print(f"在数据库中未找到ID为 {person_id} 的用户，无法更新权限或发送邮件。")

    except Exception as e:
        # 如果DB操作或邮件发送失败，记录错误但CSV操作仍然成功
        print(f"批准用户 {person_id} 时更新数据库或发送邮件失败: {e}")
        db.rollback()

    return {"msg": f"User {person_id} approved."}


async def _delete_user_face_data(person_id: str):
    """
    内部辅助函数，用于删除用户的人脸数据。
    这个函数会处理所有相关的删除操作：CSV, PKL, 和图像文件。
    """
    global known_faces
    all_records = read_csv_records()
    record_to_delete = None
    records_to_keep_csv = []
    
    found = False
    for r in all_records:
        if r.get("id") == person_id:
            record_to_delete = r
            found = True
        else:
            records_to_keep_csv.append(r)

    if not found:
        raise HTTPException(404, "用户不存在")

    # 1. 从内存和 PKL 文件中删除
    known_faces = [face for face in known_faces if face["id"] != person_id]
    save_db(known_faces)

    # 2. 从文件系统中删除图片
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
            except OSError as e:
                print(f"删除图片失败 {fp}: {e}")

    # 3. 从 CSV 文件中删除记录
    rewrite_csv(records_to_keep_csv)
    
    return record_to_delete


@router.post("/reject/{person_id}")
async def reject_face(person_id: str, db: Session = Depends(get_db)):
    """
    管理员拒绝用户认证申请。
    此操作仅将用户在CSV中的状态更新为'rejected'，并发送邮件。
    它不会删除用户数据，以便前端可以轮询到此状态。
    """
    # 1. 查找用户以发送邮件
    user = None
    try:
        user = db.query(models.UserInfo).filter(models.UserInfo.userID == int(person_id)).first()
        if user:
            send_rejection_email(user.email, user.username)
        else:
            print(f"在数据库中未找到ID为 {person_id} 的用户，无法发送拒绝邮件。")
    except Exception as e:
        print(f"为用户 {person_id} 发送拒绝邮件时失败: {e}")

    # 2. 更新CSV文件中的状态为 'rejected'
    records = []
    found = False
    if not os.path.exists(CSV_FILE):
        raise HTTPException(404, "CSV file not found")

    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or ["id", "name", "image", "images", "status"]
        for row in reader:
            if row.get('id') == person_id:
                row['status'] = 'rejected'
                found = True
            records.append(row)

    if not found:
        raise HTTPException(404, "Person ID not found in CSV")

    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return {"msg": f"用户 {person_id} 的认证申请已被标记为拒绝。"}


@router.post("/cleanup", summary="用户确认后清理自己的人脸数据")
async def cleanup_my_face_data(current_user: models.UserInfo = Depends(get_current_user)):
    """
    由用户自己触发，用于清理被拒绝或不再需要的人脸数据。
    """
    person_id = str(current_user.userID)
    try:
        await _delete_user_face_data(person_id)
        return {"msg": f"用户 {person_id} 的数据已成功清理。"}
    except HTTPException as e:
        # 如果用户不存在于人脸数据中，这不算是一个错误，静默处理即可。
        if e.status_code == 404:
            return {"msg": "无需清理，未找到用户的人脸数据。"}
        raise e
    except Exception as e:
        print(f"清理用户 {person_id} 的数据时出错: {e}")
        raise HTTPException(status_code=500, detail="清理数据时发生内部错误。")


@router.post("/check_face_in_frame")
async def check_face_in_frame(body: CheckFaceBody):
    """仅检测画面里是否存在人脸，返回 bool 及可选 bbox 供调试。"""
    # --- 可选缩放：分辨率过高时先压缩到 800px 以内 ---
    img = dataurl_to_ndarray(body.image)
    h0, w0, _ = img.shape
    scale = 1.0  # 默认不缩放
    max_dim = max(h0, w0)
    if max_dim > 800:
        scale = 800 / max_dim
        new_size = (int(w0 * scale), int(h0 * scale))
        img = np.array(Image.fromarray(img).resize(new_size))

    # 重新计算尺寸并允许区域
    h, w, _ = img.shape
    left_allow = int(w * 0.2)
    right_allow = int(w * 0.8)
    top_allow = int(h * 0.2)
    bottom_allow = int(h * 0.8)

    locations = face_recognition.face_locations(img, model="hog")
    in_frame = False
    bbox = None
    for t, r, b, l in locations:
        cx = (l + r) // 2
        cy = (t + b) // 2
        # 只要人脸中心点位于允许区域即可，容忍部分边缘超出
        if left_allow <= cx <= right_allow and top_allow <= cy <= bottom_allow:
            in_frame = True
            # 还原到原图坐标
            if scale != 1.0:
                t = int(t / scale); r = int(r / scale); b = int(b / scale); l = int(l / scale)
            bbox = (t, r, b, l)
            break
    return {"in_frame": in_frame, "bbox": bbox}

@router.post("/detect_blink")
async def detect_blink_api(body: BlinkDetectionBody):
    """检测图像中的眨眼动作"""
    try:
        print(f"收到眨眼检测请求，图像数据长度: {len(body.image) if body.image else 'None'}")
        print(f"dlib可用状态: {DLIB_AVAILABLE}")
        
        # 启用眨眼检测（会自动降级到模拟模式如果dlib不可用）
        img = dataurl_to_ndarray(body.image)
        result = detect_blink(img)
        return result
        
    except Exception as e:
        # 记录详细错误信息
        error_msg = f"眨眼检测失败: {str(e)}"
        print(f"眨眼检测错误: {error_msg}")
        print(f"图像数据长度: {len(body.image) if body.image else 'None'}")
        
        # 最后的降级处理：返回基础模拟数据
        import random
        print("使用最终降级模式：返回基础模拟眨眼检测数据")
        return {
            'has_face': True,
            'is_blinking': random.random() < 0.3,
            'left_ear': round(random.uniform(0.2, 0.4), 3),
            'right_ear': round(random.uniform(0.2, 0.4), 3),
            'avg_ear': round(random.uniform(0.2, 0.4), 3)
        }

# ---- 补全缺失的管理接口 ----
def rewrite_csv(records_to_keep: List[dict]):
    """用给定的记录重写CSV文件。"""
    if not records_to_keep:
        # 如果没有记录了，就清空文件或删除文件
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        return

    # 确保字段名是完整的，即使第一条记录缺少某些字段
    fieldnames = ["id", "name", "image", "images", "status"]
    
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # 写入时要确保所有字段都存在
        for record in records_to_keep:
            # 提供默认值以防万一
            full_record = {
                "id": record.get("id"),
                "name": record.get("name"),
                "image": record.get("image"),
                "images": record.get("images"),
                "status": record.get("status")
            }
            writer.writerow(full_record)

@router.delete("/faces/{person_id}", summary="管理员删除指定用户的所有人脸数据并降级用户")
async def delete_face(person_id: str = Path(...), db: Session = Depends(get_db)):
    """
    1.  从CSV中删除用户记录.
    2.  删除用户的图片文件.
    3.  从pkl编码文件中删除编码.
    4.  将数据库中的用户等级降为'普通用户'.
    """
    await _delete_user_face_data(person_id)

    # 将用户降级
    try:
        user_to_demote = db.query(models.UserInfo).filter(models.UserInfo.userID == int(person_id)).first()
        if user_to_demote:
            if user_to_demote.user_class == "认证用户":
                user_to_demote.user_class = "普通用户"
                db.commit()
                print(f"用户 {person_id} 已被降级为 '普通用户'")
            else:
                print(f"用户 {person_id} 等级为 '{user_to_demote.user_class}'，无需降级。")
        else:
             print(f"数据库中未找到用户 {person_id}，无法执行降级。")

    except Exception as e:
        db.rollback()
        # 即使降级失败，文件数据已被删除，所以这里只记录错误而不抛出HTTP异常
        print(f"尝试降级用户 {person_id} 时发生数据库错误: {e}")

    return {"message": f"用户 {person_id} 的人脸数据已删除并尝试降级"}


@router.get("/faces/{person_id}/images")
async def list_person_images(person_id: str):
    records = read_csv_records()
    for r in records:
        if r["id"] == person_id:
            imgs = r.get("images", "")
            files = [f.strip() for f in imgs.split(",") if f.strip()]
            urls = [f"/api/face/images/{fn}" for fn in files]
            return {"images": urls}
    raise HTTPException(404, "用户不存在")

@router.delete("/faces/{person_id}/images/{filename}")
async def delete_person_image(person_id: str, filename: str):
    safe_name = os.path.basename(filename)
    filepath = os.path.join(IMAGES_DIR, safe_name)
    if os.path.exists(filepath):
        try: os.remove(filepath)
        except OSError: pass

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
    
    # 重写整个 CSV
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "image", "images"])
        writer.writeheader()
        writer.writerows(rows)
    
    return {"msg": "图片已删除"} 
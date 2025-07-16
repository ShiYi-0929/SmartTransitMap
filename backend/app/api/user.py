from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import random, smtplib, time
from email.mime.text import MIMEText
from sqlalchemy import func
from typing import List

from database.database import get_db
from database import models
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
)
from app.core.config import (
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SENDER_EMAIL,
)

# 额外：从 face 模块读取注册状态
try:
    from app.core.api.face import read_csv_records
except Exception:
    # 避免循环依赖或初始化问题
    def read_csv_records():
        return []

router = APIRouter()

# 内存验证码缓存 {email: {code, timestamp}}
verification_codes = {}

# ----- Pydantic Schemas -----
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    code: str

class UserLogin(BaseModel):
    userID: int
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserUpdate(BaseModel):
    username: str
    email: EmailStr

class UserInDB(BaseModel):
    userID: int
    username: str
    email: EmailStr
    user_class: str

class UserStatus(BaseModel):
    user_class: str
    face_registration_status: str

class EmailSchema(BaseModel):
    email: EmailStr

class VerifyCodeSchema(BaseModel):
    email: EmailStr
    code: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    code: str

class ResetPasswordSchema(BaseModel):
    email: EmailStr
    code: str
    new_password: str

class LoginByCodeSchema(BaseModel):
    email: EmailStr
    code: str

# ----- Helper -----

def _send_verification_code(email: str) -> None:
    code = "".join(random.choices("0123456789", k=6))
    msg = MIMEText(f"您的验证码是: {code} (有效期5分钟)", "plain", "utf-8")
    msg["From"] = SENDER_EMAIL
    msg["To"] = email
    msg["Subject"] = "邮箱验证码"
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.sendmail(SENDER_EMAIL, [email], msg.as_string())
    server.quit()
    verification_codes[email] = {"code": code, "timestamp": time.time()}


def _verify_code(email: str, code: str):
    data = verification_codes.get(email)
    if not data or data["code"] != code:
        raise HTTPException(400, "验证码错误或已失效")
    if time.time() - data["timestamp"] > 300:
        del verification_codes[email]
        raise HTTPException(400, "验证码已过期，请重新获取")

# ----- Endpoints -----

@router.get("/users/me", response_model=UserInDB)
async def read_users_me(current_user: models.UserInfo = Depends(get_current_user)):
    return current_user

@router.get("/users/me/status", response_model=UserStatus)
async def get_user_status(current_user: models.UserInfo = Depends(get_current_user)):
    face_status = "not_registered"
    user_id_str = str(current_user.userID)
    for rec in read_csv_records():
        if rec.get("id") == user_id_str:
            face_status = rec.get("status", "unknown")
            break
    return {"user_class": current_user.user_class, "face_registration_status": face_status}

@router.put("/users/me", response_model=UserInDB)
async def update_user_me(user_update: UserUpdate, db: Session = Depends(get_db), current_user: models.UserInfo = Depends(get_current_user)):
    if user_update.email != current_user.email:
        if db.query(models.UserInfo).filter(models.UserInfo.email == user_update.email).first():
            raise HTTPException(400, "该邮箱已被注册")
    current_user.username = user_update.username
    current_user.email = user_update.email
    db.commit(); db.refresh(current_user)
    return current_user

@router.post("/users/me/change-password")
async def change_password_loggedin(data: PasswordChange, db: Session = Depends(get_db), current_user: models.UserInfo = Depends(get_current_user)):
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(400, "旧密码不正确")
    _verify_code(current_user.email, data.code)
    current_user.password = get_password_hash(data.new_password)
    db.commit(); del verification_codes[current_user.email]
    return {"message": "密码修改成功"}

@router.post("/register")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    _verify_code(user_data.email, user_data.code)
    if db.query(models.UserInfo).filter(models.UserInfo.email == user_data.email).first():
        del verification_codes[user_data.email]
        raise HTTPException(400, "该邮箱已被注册")
    max_id = db.query(func.max(models.UserInfo.userID)).scalar() or 10000
    new_user = models.UserInfo(
        userID=max_id + 1,
        username=user_data.username,
        password=get_password_hash(user_data.password),
        email=user_data.email,
        user_class="普通用户",
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    del verification_codes[user_data.email]
    return {"message": "注册成功", "userID": new_user.userID, "username": new_user.username}

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.UserInfo).filter(models.UserInfo.userID == form_data.userID).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(401, "用户ID或密码不正确")
    access_token = create_access_token({"sub": str(user.userID)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-by-code", response_model=Token)
async def login_by_verification_code(data: LoginByCodeSchema, db: Session = Depends(get_db)):
    _verify_code(data.email, data.code)
    user = db.query(models.UserInfo).filter(models.UserInfo.email == data.email).first()
    if not user:
        raise HTTPException(404, "用户不存在，请先注册")
    access_token = create_access_token({"sub": str(user.userID)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/send-verification-code")
async def send_verification_code(data: EmailSchema):
    _send_verification_code(data.email)
    return {"message": "验证码发送成功，请检查邮箱"}

@router.post("/reset-password")
async def reset_password_via_email(data: ResetPasswordSchema, db: Session = Depends(get_db)):
    _verify_code(data.email, data.code)
    user = db.query(models.UserInfo).filter(models.UserInfo.email == data.email).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    user.password = get_password_hash(data.new_password)
    db.commit(); del verification_codes[data.email]
    return {"message": "密码已重置，请使用新密码登录"}

@router.get("/ping")
async def ping():
    return {"message": "pong"}

@router.get("/list", summary="管理员获取用户列表")
async def list_users(db: Session = Depends(get_db), current_user: models.UserInfo = Depends(get_current_user)):
    if current_user.user_class != "管理员":
        raise HTTPException(403, "权限不足")
    users = db.query(models.UserInfo).all()
    return [
        {
            "userID": u.userID,
            "username": u.username,
            "email": u.email,
            "user_class": u.user_class,
        }
        for u in users
    ] 
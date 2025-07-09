from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import random
import smtplib
from email.mime.text import MIMEText
import time

# 数据库和安全相关导入
from app.database.database import get_db
from app.database import models
from app.core.security import create_access_token, verify_password, get_password_hash

router = APIRouter()

# --- SMTP 配置 ---
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USERNAME = "2743631775@qq.com"
SMTP_PASSWORD = "bizegtvuywvkdgdj"
SENDER_EMAIL = "2743631775@qq.com"

# --- 内存存储 ---
verification_codes = {} # 用于存储邮箱验证码

# --- Pydantic 数据模型 (Schemas) ---
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class EmailSchema(BaseModel):
    email: EmailStr

class VerifyCodeSchema(BaseModel):
    email: EmailStr
    code: str

class ResetPasswordSchema(BaseModel):
    email: EmailStr
    code: str
    new_password: str

# --- API 端点 (Endpoints) ---

@router.post("/register", summary="新用户注册")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    创建新用户，并将加密后的密码存入数据库。
    """
    # 检查邮箱是否已存在
    db_user_by_email = db.query(models.UserInfo).filter(models.UserInfo.email == user_data.email).first()
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="该邮箱已被注册")
    
    # 检查用户名是否已存在
    db_user_by_username = db.query(models.UserInfo).filter(models.UserInfo.username == user_data.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="该用户名已被使用")

    # 对密码进行哈希加密
    print(f"--- 注册诊断 ---")
    print(f"收到的用户名: {user_data.username}")
    print(f"收到的密码: {user_data.password}")
    hashed_password = get_password_hash(user_data.password)
    print(f"生成的哈希密码: {hashed_password}")
    
    # 创建新的用户实例
    new_user = models.UserInfo(
        username=user_data.username,
        password=hashed_password,
        email=user_data.email,
        user_class="普通用户"  # 默认用户类型
    )
    
    # 添加到数据库会话并提交
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"成功将用户 '{new_user.username}' 存入数据库。")
    print(f"------------------")

    return {"message": "注册成功", "username": new_user.username}


@router.post("/login", response_model=Token, summary="用户登录")
async def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户使用用户名和密码登录以获取 JWT access token.
    已更新为使用哈希密码验证。
    """
    print(f"--- 登录诊断 ---")
    print(f"收到的登录用户名: {form_data.username}")
    # 从数据库中查找用户
    user = db.query(models.UserInfo).filter(models.UserInfo.username == form_data.username).first()
    
    if not user:
        print(f"数据库中未找到用户: '{form_data.username}'")
        print(f"------------------")
        raise HTTPException(
            status_code=401, # 使用 401 Unauthorized 更合适
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"在数据库中找到用户: '{user.username}'")
    print(f"从数据库获取的哈希密码: {user.password}")
    print(f"收到的待验证密码: {form_data.password}")

    # 检查密码是否正确
    is_password_correct = verify_password(form_data.password, user.password)
    print(f"密码验证结果 (verify_password): {is_password_correct}")

    if not is_password_correct:
        print(f"密码验证失败。")
        print(f"------------------")
        raise HTTPException(
            status_code=401,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"密码验证成功。正在创建Token...")
    print(f"------------------")
    # 用户验证成功，创建 access token
    access_token = create_access_token(subject=user.username)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/send_code", summary="发送邮箱验证码")
async def send_verification_code(data: EmailSchema):
    email = data.email
    code = str(random.randint(100000, 999999))
    
    # 存储验证码和当前时间戳
    verification_codes[email] = {"code": code, "timestamp": time.time()}
    print(f"为 {email} 生成的验证码是: {code}")

    try:
        msg = MIMEText(f"您好，您的验证码是：{code}。该验证码5分钟内有效，请勿泄露给他人。如非本人操作，请联系管理人员。联系方式：23301054@bjtu.edu.cn", 'plain', 'utf-8')
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg['Subject'] = "您的验证码 - 智能交通平台"
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, [email], msg.as_string())
        server.quit()
        return {"message": "验证码发送成功，请注意查收。"}
    except Exception as e:
        print(f"邮件发送失败: {e}")
        raise HTTPException(status_code=500, detail=f"邮件服务器配置错误或发送失败: {e}")


@router.post("/verify_code", summary="验证邮箱验证码")
async def verify_code(data: VerifyCodeSchema):
    """
    验证用户提交的验证码是否正确且在有效期内。
    """
    stored_data = verification_codes.get(data.email)
    
    if not stored_data:
        raise HTTPException(status_code=400, detail="验证码错误或已失效")

    # 检查时间是否超过5分钟 (300秒)
    if time.time() - stored_data["timestamp"] > 300:
        if data.email in verification_codes:
            del verification_codes[data.email]
        raise HTTPException(status_code=400, detail="验证码已过期，请重新获取")

    if stored_data["code"] != data.code:
        raise HTTPException(status_code=400, detail="验证码不正确")

    # 验证成功后，删除验证码，防止重复使用
    if data.email in verification_codes:
        del verification_codes[data.email]
    
    return {"message": "验证成功"}


@router.post("/reset_password", summary="通过邮件重置密码")
async def reset_password_via_email(data: ResetPasswordSchema, db: Session = Depends(get_db)):
    """
    验证邮箱和验证码，然后重置用户密码。
    """
    # 步骤 1: 在后端严格验证验证码
    stored_data = verification_codes.get(data.email)
    
    if not stored_data:
        raise HTTPException(status_code=400, detail="验证码错误或已失效")

    if time.time() - stored_data["timestamp"] > 300: # 5分钟有效期
        if data.email in verification_codes:
            del verification_codes[data.email]
        raise HTTPException(status_code=400, detail="验证码已过期，请重新获取")

    if stored_data["code"] != data.code:
        raise HTTPException(status_code=400, detail="验证码不正确")

    # 步骤 2: 查找用户
    user = db.query(models.UserInfo).filter(models.UserInfo.email == data.email).first()
    if not user:
        # 出于安全考虑，不明确提示邮箱是否存在，防止被用于探测注册用户
        raise HTTPException(status_code=404, detail="操作失败，请稍后重试")

    # 步骤 3: 更新密码
    hashed_password = get_password_hash(data.new_password)
    user.password = hashed_password
    db.commit()

    # 验证成功后，立即删除验证码，防止被重复使用
    if data.email in verification_codes:
        del verification_codes[data.email]

    return {"message": "密码重置成功！"}


@router.get("/ping", summary="服务探活")
async def ping():
    """
    一个简单的端点，用于检查服务是否在线。
    """
    return {"message": "pong"} 
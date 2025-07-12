from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import random
import smtplib
from email.mime.text import MIMEText
import time
from sqlalchemy import func
# The string module is no longer needed
# import string

# 数据库和安全相关导入
from database.database import get_db
from database import models
from app.core.security import create_access_token, verify_password, get_password_hash, get_current_user
from app.core.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL

router = APIRouter()

# 在文件顶部或合适的位置初始化一个全局字典来存储验证码
verification_codes = {}

# --- Pydantic 数据模型 (Schemas) ---
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    code: str # Add verification code to registration schema

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

# --- API 端点 (Endpoints) ---

@router.get("/users/me", response_model=UserInDB, summary="获取当前用户信息")
async def read_users_me(current_user: models.UserInfo = Depends(get_current_user)):
    return UserInDB(
        userID=current_user.userID,
        username=current_user.username,
        email=current_user.email,
        user_class=current_user.user_class,
    )

@router.put("/users/me", response_model=UserInDB, summary="更新当前用户信息")
async def update_user_me(user_update: UserUpdate, db: Session = Depends(get_db), current_user: models.UserInfo = Depends(get_current_user)):
    # 检查新邮箱是否已被占用
    if user_update.email != current_user.email:
        existing_user = db.query(models.UserInfo).filter(models.UserInfo.email == user_update.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="该邮箱已被注册")

    # 更新用户信息
    current_user.username = user_update.username
    current_user.email = user_update.email
    db.commit()
    db.refresh(current_user)

    return UserInDB(
        userID=current_user.userID,
        username=current_user.username,
        email=current_user.email,
        user_class=current_user.user_class,
    )

@router.post("/users/me/change-password", summary="登录状态下修改密码")
async def change_password_loggedin(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.UserInfo = Depends(get_current_user)
):
    # 1. 验证旧密码
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="旧密码不正确")

    # 2. 验证邮箱验证码 (从内存中)
    stored_data = verification_codes.get(current_user.email)
    if not stored_data or stored_data["code"] != data.code:
        raise HTTPException(status_code=400, detail="验证码错误或已失效")
    
    # 检查验证码是否过期
    if time.time() - stored_data["timestamp"] > 300: # 5分钟有效期
        del verification_codes[current_user.email]
        raise HTTPException(status_code=400, detail="验证码已过期，请重新获取")

    # 3. 更新密码
    current_user.password = get_password_hash(data.new_password)
    db.commit()

    # 4. 删除用过的验证码
    del verification_codes[current_user.email]

    return {"message": "密码修改成功"}


@router.post("/register", summary="新用户注册")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    验证验证码，然后创建新用户。
    """
    # 1. 验证邮箱验证码 (从内存中)
    stored_data = verification_codes.get(user_data.email)
    if not stored_data or stored_data["code"] != user_data.code:
        raise HTTPException(status_code=400, detail="验证码错误或已失效")
    
    # 检查验证码是否过期
    if time.time() - stored_data["timestamp"] > 300: # 5分钟有效期
        if user_data.email in verification_codes:
            del verification_codes[user_data.email]
        raise HTTPException(status_code=400, detail="验证码已过期，请重新获取")

    # 2. 检查邮箱是否已存在
    db_user_by_email = db.query(models.UserInfo).filter(models.UserInfo.email == user_data.email).first()
    if db_user_by_email:
        # 验证码用过一次后就应失效
        if user_data.email in verification_codes:
            del verification_codes[user_data.email]
        raise HTTPException(status_code=400, detail="该邮箱已被注册")

    # 3. 创建新用户
    max_id_result = db.query(func.max(models.UserInfo.userID)).first()
    new_id = (max_id_result[0] or 10000) + 1 # 如果没有用户，从10001开始

    hashed_password = get_password_hash(user_data.password)
    
    new_user = models.UserInfo(
        userID=new_id,
        username=user_data.username,
        password=hashed_password,
        email=user_data.email,
        user_class="普通用户"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 4. 注册成功后，删除用过的验证码
    if user_data.email in verification_codes:
        del verification_codes[user_data.email]

    # 5. 发送包含账户信息的欢迎邮件
    try:
        email_body = f"""
        尊敬的 {new_user.username}，您好！

        欢迎注册智能交通管理系统。您的账户已成功创建。
        以下是您的登录信息，请妥善保管：

        登录ID: {new_user.userID}
        用户名: {new_user.username}
        您设置的密码: {user_data.password}

        请使用您的登录ID和密码进行登录。
        如有任何疑问，请联系我们。

        祝您使用愉快！

        智能交通管理系统团队
        """
        msg = MIMEText(email_body, 'plain', 'utf-8')
        msg['From'] = SENDER_EMAIL
        msg['To'] = new_user.email
        msg['Subject'] = "欢迎注册！您的智能交通管理系统账户信息"
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, [new_user.email], msg.as_string())
        server.quit()
        print(f"成功向 {new_user.email} 发送了账户信息邮件。")
    except Exception as e:
        print(f"警告: 用户 {new_user.userID} 注册成功，但账户信息邮件发送失败: {e}")
        # 注意：这里我们只打印警告，不抛出异常，因为主注册流程已经成功。
    
    return {"message": "注册成功", "userID": new_user.userID, "username": new_user.username}


@router.post("/login", response_model=Token, summary="用户登录")
async def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户使用ID和密码登录以获取 JWT access token.
    """
    print(f"--- 登录诊断 ---")
    print(f"收到的登录ID: {form_data.userID}")
    # 从数据库中查找用户
    user = db.query(models.UserInfo).filter(models.UserInfo.userID == form_data.userID).first()
    
    if not user:
        print(f"数据库中未找到ID为: '{form_data.userID}' 的用户")
        print(f"------------------")
        raise HTTPException(
            status_code=401,
            detail="用户ID或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"在数据库中找到用户: '{user.username}' (ID: {user.userID})")
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
            detail="用户ID或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"密码验证成功。正在为用户ID {user.userID} 创建Token...")
    print(f"------------------")
    # 用户验证成功，创建 access token
    access_token = create_access_token(subject=user.userID)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login-by-code", response_model=Token, summary="邮箱验证码登录")
async def login_by_verification_code(data: LoginByCodeSchema, db: Session = Depends(get_db)):
    """
    用户使用邮箱和验证码登录以获取 JWT access token.
    """
    # 1. 验证邮箱验证码
    stored_data = verification_codes.get(data.email)
    if not stored_data or stored_data["code"] != data.code:
        raise HTTPException(status_code=401, detail="验证码错误或已失效")
    
    if time.time() - stored_data["timestamp"] > 300: # 5分钟有效期
        if data.email in verification_codes:
            del verification_codes[data.email]
        raise HTTPException(status_code=401, detail="验证码已过期，请重新获取")

    # 2. 查找用户
    user = db.query(models.UserInfo).filter(models.UserInfo.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="该邮箱未注册")

    # 3. 登录成功，创建 token
    access_token = create_access_token(subject=user.userID)
    
    # 4. 删除用过的验证码
    if data.email in verification_codes:
        del verification_codes[data.email]

    return {"access_token": access_token, "token_type": "bearer"}


# 1. 修正路径以匹配前端调用
# 2. 移除用户存在性检查，以支持新用户注册
@router.post("/send-verification-code", summary="发送邮箱验证码（用于注册或验证）")
async def send_verification_code(data: EmailSchema):
    email = data.email

    # 注册时用户不存在，所以移除这里的存在性检查
    # user = db.query(models.UserInfo).filter(models.UserInfo.email == data.email).first()
    # if not user:
    #     raise HTTPException(status_code=404, detail="该邮箱尚未注册，请先完成注册。")

    code = str(random.randint(100000, 999999))
    
    # 存储验证码和当前时间戳
    verification_codes[email] = {"code": code, "timestamp": time.time()}
    print(f"为 {email} 生成的验证码是: {code}")

    try:
        msg = MIMEText(f"智能交通与路面病害检测平台\n\n尊敬的用户您好，您的验证码是：{code}。该验证码5分钟内有效，请勿泄露给他人。如非本人操作，请联系管理人员。联系方式：23301053@bjtu.edu.cn或23301054@bjtu.edu.cn", 'plain', 'utf-8')
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg['Subject'] = "您的验证码 - 智能交通与路面病害检测平台"
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, [email], msg.as_string())
        server.quit()
        return {"message": "验证码发送成功，请注意查收。"}
    except Exception as e:
        print(f"邮件发送失败: {e}")
        raise HTTPException(status_code=500, detail=f"邮件服务器配置错误或发送失败: {e}")


# This endpoint is now redundant and will be removed.
# @router.post("/verify_code", summary="验证邮箱验证码")
# async def verify_code(data: VerifyCodeSchema):
#     """
#     验证用户提交的验证码是否正确且在有效期内。
#     """
#     stored_data = verification_codes.get(data.email)
    
#     if not stored_data:
#         raise HTTPException(status_code=400, detail="验证码错误或已失效")

#     # 检查时间是否超过5分钟 (300秒)
#     if time.time() - stored_data["timestamp"] > 300:
#         if data.email in verification_codes:
#             del verification_codes[data.email]
#         raise HTTPException(status_code=400, detail="验证码已过期，请重新获取")

#     if stored_data["code"] != data.code:
#         raise HTTPException(status_code=400, detail="验证码不正确")

#     # 验证成功后，删除验证码，防止重复使用
#     if data.email in verification_codes:
#         del verification_codes[data.email]
    
#     return {"message": "验证成功"}


@router.post("/reset-password", summary="通过邮件重置密码")
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


# The /send-temporary-password endpoint is being removed as requested.


@router.get("/ping", summary="服务探活")
async def ping():
    """
    一个简单的服务探活端点。
    """
    return {"ping": "pong"} 
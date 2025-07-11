from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import models
from database.database import get_db
# 引入密码哈希校验
from app.core.security import create_access_token, verify_password

router = APIRouter()

class UserLogin(BaseModel):
    userID: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=Token, summary="用户登录")
async def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.UserInfo).filter(models.UserInfo.userID == int(form_data.userID)).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户名不存在")
    # 兼容明文或 bcrypt 哈希两种情况
    if not (verify_password(form_data.password, user.password) or form_data.password == user.password):
        raise HTTPException(status_code=400, detail="密码不正确")
    access_token = create_access_token(subject=user.userID)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "userID": user.userID,
        "username": user.username,
        "user_class": user.user_class,
    }


# --- 获取当前用户信息 ---

@router.get("/users/me")
async def get_current_user_profile(current_user: models.UserInfo = Depends(create_access_token.__globals__["get_current_user"])):
    """返回当前认证用户信息。依赖于 Authorization Bearer token。"""
    return {
        "userID": current_user.userID,
        "username": current_user.username,
        "user_class": current_user.user_class,
        "email": current_user.email,
    }

# 其他接口保留 
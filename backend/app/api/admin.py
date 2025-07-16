from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from pydantic import BaseModel
from typing import List

from database.database import get_db
from database import models
from app.core.security import get_current_user
from app.core.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL

router = APIRouter()

ADMIN_EMAILS = ["23301053@bjtu.edu.cn", "23301054@bjtu.edu.cn"]

class ApplyInfo(BaseModel):
    applyID: int
    userID: int
    username: str
    result: int

    class Config:
        from_attributes = True

# 后续 150+ 行维持与 SmartTransitMap(1) 相同，实现全部管理员接口 ... 
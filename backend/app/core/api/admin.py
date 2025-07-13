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

@router.get("/applications/pending", response_model=List[ApplyInfo], summary="获取待处理的申请列表")
async def get_pending_applications(
    db: Session = Depends(get_db),
    current_user: models.UserInfo = Depends(get_current_user)
):
    if current_user.user_class != '管理员':
        raise HTTPException(status_code=403, detail="只有管理员才能访问此资源")
    
    pending_apps = db.query(models.Apply).filter(models.Apply.result == 0).all()
    return pending_apps

@router.get("/applications/processed", response_model=List[ApplyInfo], summary="获取已处理的申请列表")
async def get_processed_applications(
    db: Session = Depends(get_db),
    current_user: models.UserInfo = Depends(get_current_user)
):
    if current_user.user_class != '管理员':
        raise HTTPException(status_code=403, detail="只有管理员才能访问此资源")
    
    processed_apps = db.query(models.Apply).filter(models.Apply.result.in_([1, 2])).all()
    return processed_apps

@router.put("/applications/{apply_id}", summary="处理升级申请")
async def process_application(
    apply_id: int = Path(..., title="申请ID", ge=1),
    approve: bool = True, # True for approve, False for reject
    db: Session = Depends(get_db),
    current_user: models.UserInfo = Depends(get_current_user)
):
    if current_user.user_class != '管理员':
        raise HTTPException(status_code=403, detail="只有管理员才能执行此操作")

    application = db.query(models.Apply).filter(models.Apply.applyID == apply_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="未找到指定的申请记录")

    if application.result != 0:
        raise HTTPException(status_code=400, detail="该申请已被处理，请勿重复操作")

    if approve:
        application.result = 1
        # 找到对应的用户并更新其权限
        user_to_upgrade = db.query(models.UserInfo).filter(models.UserInfo.userID == application.userID).first()
        if user_to_upgrade:
            # 确保只有认证用户可以被提升为管理员
            if user_to_upgrade.user_class == '认证用户':
                user_to_upgrade.user_class = '管理员'
            else:
                # 如果用户已经是管理员或其它状态，可以选择不操作或记录日志
                pass # Or raise HTTPException if this is an invalid state
    else:
        application.result = 2
    
    db.commit()
    
    return {"message": f"申请ID {apply_id} 已处理完毕。"}

@router.delete("/applications/{apply_id}", summary="删除单条已处理的申请记录")
async def delete_application(
    apply_id: int = Path(..., title="申请ID", ge=1),
    db: Session = Depends(get_db),
    current_user: models.UserInfo = Depends(get_current_user)
):
    if current_user.user_class != '管理员':
        raise HTTPException(status_code=403, detail="只有管理员才能执行此操作")

    application_to_delete = db.query(models.Apply).filter(models.Apply.applyID == apply_id).first()
    
    if not application_to_delete:
        raise HTTPException(status_code=404, detail="未找到指定的申请记录")
    
    if application_to_delete.result == 0:
        raise HTTPException(status_code=400, detail="不能删除待处理的申请")

    db.delete(application_to_delete)
    db.commit()
    
    return {"message": f"申请ID {apply_id} 已被删除。"}

@router.post("/applications/processed/clear", summary="清空所有已处理的申请记录")
async def clear_processed_applications(
    db: Session = Depends(get_db),
    current_user: models.UserInfo = Depends(get_current_user)
):
    if current_user.user_class != '管理员':
        raise HTTPException(status_code=403, detail="只有管理员才能执行此操作")
    
    num_deleted = db.query(models.Apply).filter(models.Apply.result.in_([1, 2])).delete(synchronize_session=False)
    db.commit()
    
    if num_deleted == 0:
        return {"message": "没有已处理的申请可供清除。"}
        
    return {"message": f"成功清除 {num_deleted} 条已处理的申请记录。"}


@router.post("/apply-for-admin", summary="申请成为管理员")
async def apply_for_admin_role(
    db: Session = Depends(get_db),
    current_user: models.UserInfo = Depends(get_current_user)
):
    if current_user.user_class != '认证用户':
        raise HTTPException(status_code=403, detail="只有认证用户才能申请成为管理员")
    
    # 检查是否已有待处理的申请
    existing_application = db.query(models.Apply).filter(
        models.Apply.userID == current_user.userID,
        models.Apply.result == 0
    ).first()

    if existing_application:
        raise HTTPException(status_code=400, detail="您已有待处理的申请，请勿重复提交。")

    # 创建新的申请记录
    new_application = models.Apply(
        userID=current_user.userID,
        username=current_user.username,
        result=0  # 0 for pending
    )
    db.add(new_application)
    db.commit()

    # 发送邮件通知管理员
    try:
        msg = MIMEText(f"智能交通与路面病害检测平台\n\n管理员您好，\n\n用户 {current_user.username} (ID: {current_user.userID}, 邮箱: {current_user.email}) 正在申请将权限从 ‘认证用户’ 升级为 ‘管理员’。\n\n请登录管理后台进行审核。\n\n此邮件为系统自动发送，请勿直接回复。", 'plain', 'utf-8')
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(ADMIN_EMAILS)
        msg['Subject'] = f"权限升级申请 - 用户 {current_user.username} (ID: {current_user.userID})"

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, ADMIN_EMAILS, msg.as_string())
        server.quit()
        return {"message": "您的申请已提交，请等待管理员审核。"}
    except Exception as e:
        print(f"邮件发送失败: {e}")
        # Even if email fails, the application is in the DB.
        # We might want to handle this more gracefully.
        return {"message": "您的申请已提交，但邮件通知管理员失败。请放心，我们已记录您的申请。"} 
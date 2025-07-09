from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import random
import smtplib
from email.mime.text import MIMEText

router = APIRouter()

# --- 占位符和配置 ---
# 在生产环境中，应使用更安全的方式管理这些配置，例如环境变量
SMTP_SERVER = "smtp.qq.com"  # QQ邮箱的SMTP服务器
SMTP_PORT = 465                   # QQ邮箱推荐使用SSL加密的端口 465
SMTP_USERNAME = "2743631775@qq.com"#邮箱地址
SMTP_PASSWORD = "bizegtvuywvkdgdj" # <--- 在这里填入您在QQ邮箱设置中生成的授权码
SENDER_EMAIL = "2743631775@qq.com"

# 临时存储验证码的地方。在生产环境中，应使用 Redis 或其他缓存数据库。
verification_codes = {}

class EmailSchema(BaseModel):
    email: EmailStr

@router.post("/send_code", summary="发送邮箱验证码")
async def send_verification_code(data: EmailSchema):
    """
    生成一个6位数的验证码，发送到指定的邮箱，并临时存储。
    """
    email = data.email
    code = str(random.randint(100000, 999999))
    
    # 存储验证码，关联到邮箱
    verification_codes[email] = code
    print(f"为 {email} 生成的验证码是: {code} (仅用于测试，实际应通过邮件发送)")

    # --- 发送邮件的逻辑 (使用 SMTP_SSL) ---
    # 请注意：以下代码需要您填写真实的SMTP配置才能工作
    try:
        msg = MIMEText(f"您好，您的验证码是：{code}。该验证码5分钟内有效，请勿泄露给他人。", 'plain', 'utf-8')
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg['Subject'] = "您的验证码 - 智能交通平台"

        # 使用 SMTP_SSL
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        # server.starttls() # SMTP_SSL不需要这行
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, [email], msg.as_string())
        server.quit()

        return {"message": "验证码发送成功，请注意查收。"}
    except Exception as e:
        print(f"邮件发送失败: {e}")
        # 即便邮件发送失败，为了不让恶意用户探测邮箱是否存在，仍然返回通用成功信息。
        # 但在生产环境中，需要有更完善的错误处理和监控。
        # 在这个演示中，我们抛出异常以便调试。
        raise HTTPException(
            status_code=500, 
            detail=f"邮件服务器配置错误或发送失败: {e}"
        )

@router.get("/ping")
async def ping():
    return {"msg": "pong"} 
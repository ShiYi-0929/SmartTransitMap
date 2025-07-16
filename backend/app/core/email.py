import smtplib
from email.mime.text import MIMEText
from email.header import Header
from app.core.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL


def send_email(receiver_email: str, subject: str, content: str):
    try:
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = SENDER_EMAIL
        message['To'] = receiver_email
        message['Subject'] = Header(subject, 'utf-8')

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, [receiver_email], message.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


def send_approval_email(receiver_email: str, username: str):
    subject = "【智能交通平台】认证状态更新：审核已通过"
    content = f"尊敬的 {username} 用户您好：\n\n您的人脸认证已通过。\n\n此邮件为系统自动发送，请勿直接回复。"
    return send_email(receiver_email, subject, content)


def send_rejection_email(receiver_email: str, username: str):
    subject = "【智能交通平台】认证状态更新：审核未通过"
    content = f"尊敬的 {username} 用户您好：\n\n很遗憾，您的人脸认证未通过。\n\n此邮件为系统自动发送，请勿直接回复。"
    return send_email(receiver_email, subject, content) 
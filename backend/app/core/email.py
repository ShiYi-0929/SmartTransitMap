import smtplib
from email.mime.text import MIMEText
from email.header import Header
from app.core.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL

def send_email(receiver_email: str, subject: str, content: str):
    """
    发送邮件的通用函数。
    
    :param receiver_email: 收件人邮箱地址
    :param subject: 邮件主题
    :param content: 邮件正文 (纯文本)
    """
    try:
        # 创建一个MIMEText对象，指定邮件类型为plain，编码为utf-8
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = SENDER_EMAIL
        message['To'] = receiver_email
        message['Subject'] = Header(subject, 'utf-8')

        # 使用SMTP_SSL连接到QQ邮箱的SMTP服务器
        # SMTP_SSL是smtplib的子类，它在建立连接时就使用SSL加密
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        
        # 登录邮箱
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        # 发送邮件
        server.sendmail(SENDER_EMAIL, [receiver_email], message.as_string())
        
        # 关闭连接
        server.quit()
        
        print(f"邮件已成功发送至 {receiver_email}")
        return True
    except smtplib.SMTPException as e:
        print(f"邮件发送失败: {e}")
        return False
    except Exception as e:
        print(f"发送邮件时发生未知错误: {e}")
        return False

def send_approval_email(receiver_email: str, username: str):
    """发送认证通过的邮件"""
    subject = "【智能交通平台】认证状态更新：审核已通过"
    content = f"""尊敬的 {username} 用户您好：

恭喜！您在智能交通与路面病害检测平台提交的人脸认证申请已经通过管理员审核。

您现在可以作为“认证用户”登录并使用平台的全部功能。为了使权限生效，请您退出当前账号并重新登录。

感谢您的使用和支持！

此邮件为系统自动发送，请勿直接回复。
"""
    return send_email(receiver_email, subject, content)

def send_rejection_email(receiver_email: str, username: str):
    """发送认证被拒绝的邮件"""
    subject = "【智能交通平台】认证状态更新：审核未通过"
    content = f"""尊敬的 {username} 用户您好：

我们很遗憾地通知您，您在智能交通与路面病害检测平台提交的人脸认证申请未能通过管理员审核。

这可能是由于您上传的照片不清晰、非正面、或不符合我们的认证标准。

您可以尝试重新进行人脸录入，我们建议您：
1. 确保在光线充足的环境下进行拍摄。
2. 保持面部正对摄像头，无遮挡物。
3. 按照系统提示完成所有角度的拍摄。

如果您有任何疑问，请联系平台管理员。

此邮件为系统自动发送，请勿直接回复。
"""
    return send_email(receiver_email, subject, content) 
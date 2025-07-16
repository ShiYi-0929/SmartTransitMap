import os
from urllib.parse import quote_plus

# --- 数据库配置 ---
# 请根据您的本地MySQL环境修改以下信息
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_USER = os.environ.get("DB_USER", "root") # 通常是 'root'
DB_PASSWORD = os.environ.get("DB_PASSWORD", "237466") # 请确保这里是您正确的密码
DB_NAME = os.environ.get("DB_NAME", "user")

# SQLAlchemy 数据库连接URL
# 格式: 'mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>?charset=<charset>'
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=gb2312"

# --- JWT 安全配置 ---
SECRET_KEY = "a_very_secret_key_that_should_be_changed" # 用于签名JWT的密钥，生产环境请务必修改
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300 # Token有效期（分钟）

# --- SMTP 邮件服务配置 ---
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USERNAME = "2743631775@qq.com"
SMTP_PASSWORD = "bizegtvuywvkdgdj"  # 这是授权码，不是邮箱密码
SENDER_EMAIL = "2743631775@qq.com" 
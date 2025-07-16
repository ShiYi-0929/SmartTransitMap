from sqlalchemy import Column, String
from .database import Base

class UserInfo(Base):
    __tablename__ = "userinfo"

    # 根据 user.sql 文件定义列
    # 注意：我们将 email 设置为主键，因为它在您的SQL中是主键
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), primary_key=True, nullable=False)
    # 在Python中 'class' 是关键字，我们使用 'user_class' 作为属性名
    user_class = Column("class", String(255), nullable=False) 
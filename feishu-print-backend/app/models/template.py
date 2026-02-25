from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # 用户ID，NULL表示系统模板
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    template_type = Column(String(20), default='normal', nullable=False)  # 'normal' 或 'ai'
    is_system = Column(Boolean, default=False, nullable=False)  # 是否为系统模版
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # 关联用户
    user = relationship("User", backref="templates")

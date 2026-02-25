from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class MembershipPlan(Base):
    """
    会员计划配置（用于定价页展示、创建订单定价、后台改价持久化）

    price / original_price 单位：分
    """

    __tablename__ = "membership_plans"

    id = Column(String(32), primary_key=True)  # 'pro' | 'team'（也可扩展）
    name = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)  # 分
    original_price = Column(Integer, nullable=True)  # 分
    duration_days = Column(Integer, nullable=False, default=30)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())









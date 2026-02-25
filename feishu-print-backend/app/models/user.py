from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    feishu_user_id = Column(String(64), unique=True, nullable=False, index=True)
    tenant_key = Column(String(64), nullable=True, index=True)
    nickname = Column(String(100), nullable=True)
    security_level = Column(String(20), default="medium")  # low, medium, high
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联会员信息
    membership = relationship("Membership", back_populates="user", uselist=False)


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    plan_type = Column(SQLEnum('free', 'pro', 'team', name='plantype'), default='free')
    expires_at = Column(DateTime, nullable=True)  # NULL表示永久或免费版
    
    # 使用限制
    pdf_exports_used = Column(Integer, default=0)  # 本月PDF导出次数
    ai_generates_used = Column(Integer, default=0)  # 本月AI生成次数（会重置）
    ai_generates_total = Column(Integer, default=0)  # 历史AI生成总次数（永不重置）
    usage_reset_at = Column(DateTime, server_default=func.now())  # 使用次数重置时间
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联用户
    user = relationship("User", back_populates="membership")


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_type = Column(SQLEnum('free', 'pro', 'team', name='plantype'), nullable=False)
    plan_name = Column(String(50), nullable=True)  # 计划名称（如：专业版、团队版）
    amount = Column(Integer, nullable=False)  # 金额（分）
    original_price = Column(Integer, nullable=True)  # 原价（分）
    discount_price = Column(Integer, nullable=True, default=0)  # 优惠金额（分）
    status = Column(SQLEnum('PENDING', 'PAID', 'CANCELLED', 'REFUNDED', name='orderstatus'), default='PENDING')
    expires_at = Column(DateTime, nullable=True)  # 订单过期时间
    paid_at = Column(DateTime, nullable=True)  # 支付时间
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联用户
    user = relationship("User", backref="orders")


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(12), unique=True, nullable=False, index=True)
    plan_type = Column(SQLEnum('free', 'pro', 'team', name='plantype'), nullable=False)
    duration_days = Column(Integer, nullable=False)  # 有效期天数
    max_uses = Column(Integer, default=1)  # 最大使用次数
    used_count = Column(Integer, default=0)  # 已使用次数
    # is_active = Column(Integer, default=1)  # 暂时注释：数据库表中不存在该列
    expires_at = Column(DateTime, nullable=True)  # 邀请码过期时间
    created_at = Column(DateTime, server_default=func.now())
    # updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  # 暂时注释：数据库表中不存在该列


class UserActivity(Base):
    """用户活动日志（用于安全审计）"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    feishu_user_id = Column(String(64), index=True)
    ip_address = Column(String(45), index=True)
    user_agent = Column(String(500), nullable=True)
    client_fingerprint = Column(String(500), nullable=True)
    action = Column(String(50), index=True)  # init, check_permission, use_feature等
    security_level = Column(String(20), nullable=True)  # low, medium, high
    created_at = Column(DateTime, server_default=func.now(), index=True)

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class TeamRole(str, enum.Enum):
    OWNER = "owner"      # 团队所有者
    ADMIN = "admin"      # 管理员
    MEMBER = "member"    # 普通成员


class InviteStatus(str, enum.Enum):
    PENDING = "pending"      # 待接受
    ACCEPTED = "accepted"    # 已接受
    REJECTED = "rejected"    # 已拒绝
    EXPIRED = "expired"      # 已过期


class Team(Base):
    """团队表"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    max_members = Column(Integer, default=5)  # 最大成员数
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    templates = relationship("TeamTemplate", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    """团队成员表"""
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(TeamRole), default=TeamRole.MEMBER)
    joined_at = Column(DateTime, server_default=func.now())

    # 关联
    team = relationship("Team", back_populates="members")
    user = relationship("User")


class TeamInvite(Base):
    """团队邀请表"""
    __tablename__ = "team_invites"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invitee_feishu_id = Column(String(64), nullable=True)  # 被邀请人飞书ID（为空表示通用邀请码）
    status = Column(SQLEnum(InviteStatus), default=InviteStatus.PENDING)
    invite_code = Column(String(32), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # 关联
    team = relationship("Team")
    inviter = relationship("User")


class TeamTemplate(Base):
    """团队共享模版表"""
    __tablename__ = "team_templates"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    shared_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    can_edit = Column(Boolean, default=False)  # 是否允许团队成员编辑
    created_at = Column(DateTime, server_default=func.now())

    # 关联
    team = relationship("Team", back_populates="templates")
    template = relationship("Template")
    shared_by = relationship("User")

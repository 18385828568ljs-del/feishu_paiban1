from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging
from app.database import get_db
from app.models.user import User, Membership, PlanType, UserActivity
from app.auth import create_access_token, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user", tags=["user"])


# 会员计划配置
PLAN_LIMITS = {
    "free": {
        "pdf_exports": 10,  # 每月10次
        "ai_generates": 5,  # 每月5次
        "signature": False,  # 不支持电子签名
        "premium_templates": False,  # 不支持高级模板
    },
    "pro": {
        "pdf_exports": 500,  # 每月500次
        "ai_generates": 50,  # 每月50次
        "signature": True,
        "premium_templates": False,  # 不支持高级模板
    },
    "team": {
        "pdf_exports": -1,  # 无限
        "ai_generates": 200,  # 每月200次
        "signature": True,
        "premium_templates": True,  # 支持高级模板
    },
}


class UserInitRequest(BaseModel):
    feishu_user_id: str
    tenant_key: Optional[str] = None
    nickname: Optional[str] = None
    client_fingerprint: Optional[str] = None  # 客户端指纹


class UserInitResponse(BaseModel):
    user: dict
    session_token: str  # JWT Session Token


class UserResponse(BaseModel):
    id: int
    feishu_user_id: str
    nickname: Optional[str]
    plan_type: str
    expires_at: Optional[datetime]
    pdf_exports_used: int
    pdf_exports_limit: int
    ai_generates_used: int
    ai_generates_limit: int
    can_use_signature: bool
    can_use_premium_templates: bool

    class Config:
        from_attributes = True


class CheckPermissionRequest(BaseModel):
    feishu_user_id: str
    feature: str  # 'pdf_export', 'ai_generate', 'signature', 'premium_templates'


class CheckPermissionResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    remaining: Optional[int] = None


class UseFeatureRequest(BaseModel):
    feishu_user_id: str
    feature: str  # 'pdf_export', 'ai_generate'


def reset_usage_if_needed(membership: Membership, db: Session):
    """如果已过月重置周期，重置使用次数"""
    now = datetime.now()
    if membership.usage_reset_at:
        # 检查是否需要重置（当前月份与 usage_reset_at 的月份不同）
        if now.month != membership.usage_reset_at.month or now.year != membership.usage_reset_at.year:
            membership.pdf_exports_used = 0
            membership.ai_generates_used = 0
            membership.usage_reset_at = now
            db.commit()


async def verify_request_security(request: Request) -> dict:
    """多重安全验证（不调用飞书API）"""
    security_checks = {
        "origin_valid": False,
        "referer_valid": False,
        "user_agent_valid": False,
        "risk_level": "high"
    }
    
    # 1. 检查 Origin/Referer
    origin = request.headers.get("origin", "")
    referer = request.headers.get("referer", "")
    
    allowed_domains = ["feishu.cn", "larksuite.com", "localhost", "127.0.0.1"]
    
    if any(domain in origin for domain in allowed_domains):
        security_checks["origin_valid"] = True
    
    if any(domain in referer for domain in allowed_domains):
        security_checks["referer_valid"] = True
    
    # 2. 检查 User-Agent（排除明显的脚本请求）
    user_agent = request.headers.get("user-agent", "").lower()
    
    # 飞书客户端的 User-Agent 通常包含这些特征
    valid_agents = ["mozilla", "chrome", "safari", "feishu", "lark", "edge", "firefox"]
    invalid_agents = ["curl", "python", "postman", "httpie", "wget", "java"]
    
    if any(agent in user_agent for agent in valid_agents) and \
       not any(agent in user_agent for agent in invalid_agents):
        security_checks["user_agent_valid"] = True
    
    # 3. 计算风险等级
    valid_count = sum([
        security_checks["origin_valid"],
        security_checks["referer_valid"],
        security_checks["user_agent_valid"]
    ])
    
    if valid_count >= 2:
        security_checks["risk_level"] = "low"
    elif valid_count == 1:
        security_checks["risk_level"] = "medium"
    else:
        security_checks["risk_level"] = "high"
    
    return security_checks


@router.post("/init", response_model=UserInitResponse)
async def init_user(request: Request, user_data: UserInitRequest, db: Session = Depends(get_db)):
    """
    初始化用户（混合模式）
    - 不需要飞书授权弹窗
    - 通过多重验证判断请求合法性
    - 颁发 JWT Session Token
    """
    try:
        # 1. 多重安全验证
        security_checks = await verify_request_security(request)
        
        # 高风险请求：拒绝
        if security_checks["risk_level"] == "high":
            logger.warning(
                f"高风险请求被拒绝: {user_data.feishu_user_id}, "
                f"IP: {request.client.host}, "
                f"Origin: {request.headers.get('origin', 'N/A')}, "
                f"Referer: {request.headers.get('referer', 'N/A')}, "
                f"User-Agent: {request.headers.get('user-agent', 'N/A')}"
            )
            raise HTTPException(
                status_code=403,
                detail="请求来源不合法，请在飞书客户端中使用"
            )
        
        # 2. 频率限制检查（防止批量攻击）
        # 注意：只统计 init 操作，避免误伤正常用户
        recent_init_activities = db.query(UserActivity).filter(
            UserActivity.ip_address == request.client.host,
            UserActivity.action == "init",
            UserActivity.created_at > datetime.now() - timedelta(minutes=5)
        ).count()
        
        # 5分钟内最多50次初始化（放宽限制，避免测试时被误伤）
        if recent_init_activities > 50:
            logger.warning(f"频率限制触发: IP {request.client.host}, 5分钟内初始化 {recent_init_activities} 次")
            raise HTTPException(
                status_code=429,
                detail="请求过于频繁，请稍后再试"
            )
        
        # 3. 创建或更新用户
        user = db.query(User).filter(User.feishu_user_id == user_data.feishu_user_id).first()
        
        if not user:
            # 创建新用户
            user = User(
                feishu_user_id=user_data.feishu_user_id,
                tenant_key=user_data.tenant_key,
                nickname=user_data.nickname,
                security_level=security_checks["risk_level"]
            )
            db.add(user)
            db.flush()
            
            # 创建免费会员
            membership = Membership(
                user_id=user.id,
                plan_type="free"
            )
            db.add(membership)
            db.commit()
            db.refresh(user)
            
            logger.info(f"新用户创建: {user_data.feishu_user_id}, 风险等级: {security_checks['risk_level']}")
        else:
            # 更新用户信息
            if user_data.nickname:
                user.nickname = user_data.nickname
            if user_data.tenant_key:
                user.tenant_key = user_data.tenant_key
            # 更新安全等级
            user.security_level = security_checks["risk_level"]
            db.commit()
        
        # 4. 记录活动日志
        activity = UserActivity(
            feishu_user_id=user_data.feishu_user_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "")[:500],
            client_fingerprint=user_data.client_fingerprint[:500] if user_data.client_fingerprint else None,
            action="init",
            security_level=security_checks["risk_level"]
        )
        db.add(activity)
        db.commit()
        
        # 5. 检查并重置使用次数
        if user.membership:
            reset_usage_if_needed(user.membership, db)
        
        # 6. 颁发 JWT Session Token（7天有效期）
        session_token = create_access_token(
            data={
                "sub": user.feishu_user_id,
                "user_id": user.id,
                "tenant_key": user.tenant_key,
                "role": "user",
                "security_level": security_checks["risk_level"]
            },
            expires_delta=timedelta(days=7)
        )
        
        # 7. 返回用户信息和 token
        membership = user.membership
        plan_limits = PLAN_LIMITS.get(membership.plan_type, PLAN_LIMITS["free"])
        
        return UserInitResponse(
            user={
                "id": user.id,
                "feishu_user_id": user.feishu_user_id,
                "nickname": user.nickname,
                "plan_type": membership.plan_type,
                "expires_at": membership.expires_at.isoformat() if membership.expires_at else None,
                "pdf_exports_used": membership.pdf_exports_used,
                "pdf_exports_limit": plan_limits["pdf_exports"],
                "ai_generates_used": membership.ai_generates_used,
                "ai_generates_limit": plan_limits["ai_generates"],
                "can_use_signature": plan_limits["signature"],
                "can_use_premium_templates": plan_limits["premium_templates"],
            },
            session_token=session_token
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"初始化用户失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"初始化用户失败: {str(e)}")


@router.get("/status/{feishu_user_id}", response_model=UserResponse)
async def get_user_status(feishu_user_id: str, db: Session = Depends(get_db)):
    """获取用户会员状态"""
    user = db.query(User).filter(User.feishu_user_id == feishu_user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查并重置使用次数
    if user.membership:
        reset_usage_if_needed(user.membership, db)
    
    membership = user.membership
    plan_limits = PLAN_LIMITS.get(membership.plan_type, PLAN_LIMITS["free"])
    
    return UserResponse(
        id=user.id,
        feishu_user_id=user.feishu_user_id,
        nickname=user.nickname,
        plan_type=membership.plan_type,
        expires_at=membership.expires_at,
        pdf_exports_used=membership.pdf_exports_used,
        pdf_exports_limit=plan_limits["pdf_exports"],
        ai_generates_used=membership.ai_generates_used,
        ai_generates_limit=plan_limits["ai_generates"],
        can_use_signature=plan_limits["signature"],
        can_use_premium_templates=plan_limits["premium_templates"],
    )


@router.post("/check-permission", response_model=CheckPermissionResponse)
async def check_permission(request: CheckPermissionRequest, db: Session = Depends(get_db)):
    """检查用户是否有权限使用某功能"""
    user = db.query(User).filter(User.feishu_user_id == request.feishu_user_id).first()
    
    if not user or not user.membership:
        return CheckPermissionResponse(allowed=False, reason="用户不存在")
    
    membership = user.membership
    reset_usage_if_needed(membership, db)
    
    # 检查会员是否过期
    now = datetime.now()
    if membership.expires_at and membership.expires_at < now and membership.plan_type != "free":
        # 会员已过期，降级为免费版
        membership.plan_type = "free"
        membership.expires_at = None
        db.commit()
    
    plan_limits = PLAN_LIMITS.get(membership.plan_type, PLAN_LIMITS["free"])
    
    if request.feature == "pdf_export":
        limit = plan_limits["pdf_exports"]
        if limit == -1:  # 无限
            return CheckPermissionResponse(allowed=True, remaining=-1)
        remaining = limit - membership.pdf_exports_used
        if remaining > 0:
            return CheckPermissionResponse(allowed=True, remaining=remaining)
        else:
            return CheckPermissionResponse(
                allowed=False, 
                reason=f"PDF导出次数已用完（{limit}次/月），请升级会员",
                remaining=0
            )
    
    elif request.feature == "ai_generate":
        limit = plan_limits["ai_generates"]
        if limit == -1:  # 无限
            return CheckPermissionResponse(allowed=True, remaining=-1)
        remaining = limit - membership.ai_generates_used
        if remaining > 0:
            return CheckPermissionResponse(allowed=True, remaining=remaining)
        else:
            return CheckPermissionResponse(
                allowed=False, 
                reason=f"AI生成次数已用完（{limit}次/月），请升级会员",
                remaining=0
            )
    
    elif request.feature == "signature":
        if plan_limits["signature"]:
            return CheckPermissionResponse(allowed=True)
        else:
            return CheckPermissionResponse(allowed=False, reason="当前会员不支持电子签名功能")
    
    elif request.feature == "premium_templates":
        if plan_limits["premium_templates"]:
            return CheckPermissionResponse(allowed=True)
        else:
            return CheckPermissionResponse(allowed=False, reason="当前会员不支持高级模板，请升级会员")
    
    return CheckPermissionResponse(allowed=False, reason="未知功能")


@router.post("/use-feature")
async def use_feature(request: UseFeatureRequest, db: Session = Depends(get_db)):
    """记录功能使用（消耗次数）"""
    try:
        user = db.query(User).filter(User.feishu_user_id == request.feishu_user_id).first()
        
        if not user or not user.membership:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        membership = user.membership
        reset_usage_if_needed(membership, db)
        
        if request.feature == "pdf_export":
            membership.pdf_exports_used += 1
        elif request.feature == "ai_generate":
            membership.ai_generates_used += 1
            membership.ai_generates_total += 1  # 历史总次数，永不重置
        else:
            raise HTTPException(status_code=400, detail="未知功能")
        
        db.commit()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"记录功能使用失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"记录功能使用失败: {str(e)}")

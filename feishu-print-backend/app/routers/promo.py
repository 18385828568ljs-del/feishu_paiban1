from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import random
import string
from app.database import get_db
from app.models.user import User, Membership, PromoCode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/promo", tags=["promo"])


class GeneratePromoRequest(BaseModel):
    plan_type: str  # 'free', 'pro', 'team'
    duration_days: int = 30  # 有效期天数
    max_uses: int = 1  # 最大使用次数
    expires_at: Optional[datetime] = None  # 邀请码过期时间


class PromoCodeResponse(BaseModel):
    id: int
    code: str
    plan_type: str
    duration_days: int
    max_uses: int
    used_count: int
    is_active: int
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class RedeemPromoRequest(BaseModel):
    code: str
    feishu_user_id: str


def generate_promo_code() -> str:
    """生成12位邀请码"""
    # 使用大写字母和数字，排除容易混淆的字符（0, O, I, 1）
    chars = string.ascii_uppercase.replace('O', '').replace('I', '') + string.digits.replace('0', '').replace('1', '')
    return ''.join(random.choices(chars, k=12))


def update_membership(user: User, plan_type: str, duration_days: int, db: Session):
    """更新会员信息（升级或续期）"""
    membership = user.membership
    if not membership:
        # 创建会员信息
        membership = Membership(
            user_id=user.id,
            plan_type=plan_type
        )
        db.add(membership)
        db.flush()
    
    now = datetime.now()
    
    # 判断是续期还是升级
    if membership.plan_type == plan_type and membership.expires_at and membership.expires_at > now:
        # 续期：同类型会员且未过期，在现有过期时间基础上增加天数
        membership.expires_at = membership.expires_at + timedelta(days=duration_days)
    else:
        # 升级：不同类型或已过期，覆盖类型，从当前时间开始计算有效期
        membership.plan_type = plan_type
        membership.expires_at = now + timedelta(days=duration_days)
    
    db.commit()
    return membership


@router.post("/generate", response_model=PromoCodeResponse)
async def generate_promo(request: GeneratePromoRequest, db: Session = Depends(get_db)):
    """生成邀请码（管理员功能）"""
    try:
        # 验证计划类型
        valid_plans = ['free', 'pro', 'team']
        if request.plan_type not in valid_plans:
            raise HTTPException(status_code=400, detail="无效的会员计划类型")
        
        # 生成唯一邀请码
        max_attempts = 10
        for _ in range(max_attempts):
            code = generate_promo_code()
            existing = db.query(PromoCode).filter(PromoCode.code == code).first()
            if not existing:
                break
        else:
            raise HTTPException(status_code=500, detail="生成邀请码失败，请重试")
        
        # 创建邀请码
        promo_code = PromoCode(
            code=code,
            plan_type=request.plan_type,
            duration_days=request.duration_days,
            max_uses=request.max_uses,
            is_active=1,
            expires_at=request.expires_at
        )
        db.add(promo_code)
        db.commit()
        db.refresh(promo_code)
        
        return PromoCodeResponse(
            id=promo_code.id,
            code=promo_code.code,
            plan_type=promo_code.plan_type,
            duration_days=promo_code.duration_days,
            max_uses=promo_code.max_uses,
            used_count=promo_code.used_count,
            is_active=promo_code.is_active,
            expires_at=promo_code.expires_at,
            created_at=promo_code.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"生成邀请码失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成邀请码失败: {str(e)}")


@router.post("/redeem")
async def redeem_promo(request: RedeemPromoRequest, db: Session = Depends(get_db)):
    """兑换邀请码"""
    try:
        # 获取邀请码
        promo_code = db.query(PromoCode).filter(PromoCode.code == request.code.upper()).first()
        if not promo_code:
            return {"success": False, "message": "邀请码不存在"}
        
        # 检查是否激活
        if promo_code.is_active != 1:
            return {"success": False, "message": "邀请码已禁用"}
        
        # 检查是否过期
        now = datetime.now()
        if promo_code.expires_at and promo_code.expires_at < now:
            return {"success": False, "message": "邀请码已过期"}
        
        # 检查是否已用完
        if promo_code.used_count >= promo_code.max_uses:
            return {"success": False, "message": "邀请码已用完"}
        
        # 获取用户
        user = db.query(User).filter(User.feishu_user_id == request.feishu_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 更新会员信息
        update_membership(user, promo_code.plan_type, promo_code.duration_days, db)
        
        # 更新邀请码使用次数
        promo_code.used_count += 1
        db.commit()
        
        return {"success": True, "message": "兑换成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"兑换邀请码失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"兑换邀请码失败: {str(e)}")


@router.get("/list")
async def list_promos(db: Session = Depends(get_db)):
    """获取邀请码列表（管理员功能）"""
    promo_codes = db.query(PromoCode).order_by(PromoCode.created_at.desc()).all()
    
    return {
        "promo_codes": [
            {
                "id": pc.id,
                "code": pc.code,
                "plan_type": pc.plan_type,
                "duration_days": pc.duration_days,
                "max_uses": pc.max_uses,
                "used_count": pc.used_count,
                "is_active": pc.is_active,
                "expires_at": pc.expires_at.isoformat() if pc.expires_at else None,
                "created_at": pc.created_at.isoformat()
            }
            for pc in promo_codes
        ]
    }


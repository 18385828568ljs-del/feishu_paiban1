from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import random
import string
from app.database import get_db
from app.models.user import User, Membership, Order, PromoCode, OrderStatus
from app.models.admin import Admin
from app.models.feedback import Feedback
from app.models.plan import MembershipPlan
from app.auth import create_access_token, get_current_admin
from app.routers import payment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ==================== 请求/响应模型 ====================

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[dict] = None


class UserListResponse(BaseModel):
    items: List[dict]
    total: int


class UpdateMembershipRequest(BaseModel):
    plan_type: str
    duration_days: int


class PlanInfo(BaseModel):
    id: str
    name: str
    price: int
    original_price: Optional[int] = None
    duration_days: int


class UpdatePlanRequest(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    original_price: Optional[int] = None
    duration_days: Optional[int] = None


# ==================== 登录接口 ====================

class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str


@router.post("/login", response_model=LoginResponse)
async def admin_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    admin = db.query(Admin).filter(Admin.username == login_data.username).first()
    
    if admin and admin.is_active and admin.check_password(login_data.password):
        # 创建JWT令牌
        token = create_access_token({
            "sub": admin.username,
            "username": admin.username,
            "nickname": admin.nickname,
            "role": "admin"
        })
        return LoginResponse(
            success=True,
            message="登录成功",
            token=token,
            user={"username": admin.username, "nickname": admin.nickname, "role": "admin"}
        )
    return LoginResponse(success=False, message="用户名或密码错误")


@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db)):
    """修改管理员密码"""
    admin = db.query(Admin).filter(Admin.username == request.username).first()
    
    if not admin:
        return {"success": False, "message": "用户不存在"}
    
    if not admin.check_password(request.old_password):
        return {"success": False, "message": "当前密码错误"}
    
    if len(request.new_password) < 6:
        return {"success": False, "message": "新密码长度不能少于6位"}
    
    # 更新密码
    admin.set_password(request.new_password)
    db.commit()
    
    return {"success": True, "message": "密码修改成功"}


# ==================== 会员计划管理 ====================


@router.get("/plans", response_model=List[PlanInfo])
async def get_membership_plans(
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    """
    获取当前会员计划配置

    当前实现从数据库 membership_plans 读取；若数据库为空则回退到默认配置。
    """
    plans = payment._get_plans_from_db(db)
    return [PlanInfo(**plan) for plan in plans]


@router.put("/plans/{plan_id}")
async def update_membership_plan(
    plan_id: str,
    request: UpdatePlanRequest,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    """
    更新指定会员计划的价格或时长

    仅修改传入字段，不传的字段保持不变。
    """
    plan = db.query(MembershipPlan).filter(MembershipPlan.id == plan_id).first()
    if not plan:
        # 允许后台新增计划（最常见是 pro/team 已存在；这里兼容缺失时创建）
        plan = MembershipPlan(id=plan_id, name=request.name or plan_id, price=request.price or 0, duration_days=request.duration_days or 30)
        db.add(plan)

    if request.name is not None:
        plan.name = request.name
    if request.price is not None:
        plan.price = request.price
    if request.original_price is not None:
        plan.original_price = request.original_price
    if request.duration_days is not None:
        plan.duration_days = request.duration_days

    db.commit()
    db.refresh(plan)

    data = {
        "id": plan.id,
        "name": plan.name,
        "price": int(plan.price),
        "original_price": int(plan.original_price) if plan.original_price is not None else None,
        "duration_days": int(plan.duration_days),
    }
    return {"success": True, "message": "会员计划已更新", "data": data}


# ==================== 统计接口 ====================

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """获取统计数据"""
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    # 用户统计
    total_users = db.query(func.count(User.id)).scalar() or 0
    new_users_today = db.query(func.count(User.id)).filter(User.created_at >= today_start).scalar() or 0
    
    # 订单统计
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    orders_today = db.query(func.count(Order.id)).filter(Order.created_at >= today_start).scalar() or 0
    
    # 收入统计（只统计已支付的订单，金额单位是分，需要转换为元）
    total_revenue = db.query(func.sum(Order.amount)).filter(Order.status == "PAID").scalar() or 0
    revenue_today = db.query(func.sum(Order.amount)).filter(
        Order.status == "PAID",
        Order.paid_at >= today_start
    ).scalar() or 0
    
    # AI 生成次数统计（汇总所有用户的历史总次数）
    total_ai_generates = db.query(func.sum(Membership.ai_generates_total)).scalar() or 0
    
    # 邀请码统计
    promo_usages = db.query(func.sum(PromoCode.used_count)).scalar() or 0
    # 暂时统计所有邀请码数量（is_active字段不存在）
    active_promos = db.query(func.count(PromoCode.id)).scalar() or 0
    
    # 最新用户（使用 joinedload 预加载 membership 避免 N+1 查询）
    from sqlalchemy.orm import joinedload
    recent_users = db.query(User).options(joinedload(User.membership)).order_by(desc(User.created_at)).limit(5).all()
    
    # 最新订单
    recent_orders = db.query(Order).options(joinedload(Order.user)).order_by(desc(Order.created_at)).limit(5).all()
    
    # 7天趋势数据
    user_trend = []
    revenue_trend = []
    trend_days = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        # 当天新用户数
        day_users = db.query(func.count(User.id)).filter(
            User.created_at >= day_start,
            User.created_at <= day_end
        ).scalar() or 0
        user_trend.append(day_users)
        
        # 当天收入（已支付订单）
        day_revenue = db.query(func.sum(Order.amount)).filter(
            Order.status == "PAID",
            Order.paid_at >= day_start,
            Order.paid_at <= day_end
        ).scalar() or 0
        revenue_trend.append(float(day_revenue) / 100.0 if day_revenue else 0)  # 转换为元
        
        # 日期标签
        trend_days.append(day.strftime("%m/%d"))
    
    return {
        "overview": {
            "totalUsers": total_users,
            "newUsersToday": new_users_today,
            "totalOrders": total_orders,
            "ordersToday": orders_today,
            "totalRevenue": float(total_revenue) / 100.0 if total_revenue else 0,  # 转换为元
            "revenueToday": float(revenue_today) / 100.0 if revenue_today else 0,  # 转换为元
            "totalAiGenerates": int(total_ai_generates),
            "promoUsages": int(promo_usages),
            "activePromos": int(active_promos)
        },
        "recentUsers": [
            {
                "id": u.id,
                "nickname": u.nickname,
                "plan_type": u.membership.plan_type if u.membership else "free",
                "created_at": u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else ""
            }
            for u in recent_users
        ],
        "recentOrders": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "plan_name": {
                    "free": "免费版",
                    "pro": "专业版",
                    "team": "团队版"
                }.get(o.plan_type, o.plan_type),
                "amount": float(o.amount) / 100.0 if o.amount else 0,  # 转换为元
                "status": o.status
            }
            for o in recent_orders
        ],
        "userTrend": user_trend,
        "revenueTrend": revenue_trend,
        "trendDays": trend_days
    }


# ==================== 用户管理 ====================

@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = 1,
    pageSize: int = 20,
    search: Optional[str] = None,
    planType: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.nickname.contains(search)) | 
            (User.feishu_user_id.contains(search))
        )
    
    if planType:
        query = query.join(Membership).filter(Membership.plan_type == planType)
    
    total = query.count()
    users = query.order_by(desc(User.created_at)).offset((page - 1) * pageSize).limit(pageSize).all()
    
    return UserListResponse(
        items=[
            {
                "id": u.id,
                "feishu_user_id": u.feishu_user_id,
                "nickname": u.nickname,
                "plan_type": u.membership.plan_type if u.membership else "free",
                "expires_at": u.membership.expires_at.isoformat() if u.membership and u.membership.expires_at else None,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ],
        total=total
    )


@router.put("/users/{user_id}/membership")
async def update_user_membership(
    user_id: int,
    request: UpdateMembershipRequest,
    db: Session = Depends(get_db)
):
    """修改用户会员等级"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        membership = user.membership
        if not membership:
            membership = Membership(user_id=user.id)
            db.add(membership)
        
        membership.plan_type = request.plan_type
        
        # 计算到期时间
        now = datetime.now()
        if membership.expires_at and membership.expires_at > now:
            base_time = membership.expires_at
        else:
            base_time = now
        
        membership.expires_at = base_time + timedelta(days=request.duration_days)
        db.commit()
        
        return {"success": True, "message": "会员等级已更新"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新用户会员等级失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新用户会员等级失败: {str(e)}")


# ==================== 反馈管理 ====================

@router.get("/feedbacks")
async def get_feedbacks(db: Session = Depends(get_db)):
    """获取反馈列表"""
    feedbacks = db.query(Feedback).order_by(desc(Feedback.created_at)).all()
    
    return {
        "items": [
            {
                "id": f.id,
                "user_id": f.user_id,
                "content": f.content,
                "contact": f.contact,
                "is_read": f.is_read,
                "reply": f.reply,
                "created_at": f.created_at.isoformat() if f.created_at else None
            }
            for f in feedbacks
        ]
    }


@router.put("/feedbacks/{feedback_id}/read")
async def mark_feedback_read(feedback_id: int, db: Session = Depends(get_db)):
    """标记反馈为已读"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    feedback.is_read = True
    db.commit()
    
    return {"success": True, "message": "已标记为已读"}


@router.delete("/feedbacks/{feedback_id}")
async def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """删除反馈"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    db.delete(feedback)
    db.commit()
    
    return {"success": True, "message": "删除成功"}


# ==================== 订单管理 ====================

class OrderListResponse(BaseModel):
    items: List[dict]
    total: int


@router.get("/orders", response_model=OrderListResponse)
async def get_orders(
    page: int = 1,
    pageSize: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取订单列表"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(Order).options(joinedload(Order.user))
    
    if search:
        query = query.join(User).filter(
            (Order.order_no.contains(search)) |
            (User.nickname.contains(search)) |
            (User.feishu_user_id.contains(search))
        )
    
    if status:
        query = query.filter(Order.status == status)
    
    total = query.count()
    orders = query.order_by(desc(Order.created_at)).offset((page - 1) * pageSize).limit(pageSize).all()
    
    return OrderListResponse(
        items=[
            {
                "id": o.id,
                "order_no": o.order_no,
                "user_id": o.user_id,
                "user_nickname": o.user.nickname if o.user else None,
                "user_feishu_id": o.user.feishu_user_id if o.user else None,
                "plan_type": o.plan_type,
                "amount": o.amount,
                "status": o.status,
                "expires_at": o.expires_at.isoformat() if o.expires_at else None,
                "paid_at": o.paid_at.isoformat() if o.paid_at else None,
                "created_at": o.created_at.isoformat() if o.created_at else None
            }
            for o in orders
        ],
        total=total
    )


# ==================== 邀请码管理 ====================

class CreatePromoRequest(BaseModel):
    plan_type: str
    duration_days: int
    max_uses: int = 1
    expires_days: Optional[int] = None  # 邀请码有效期天数，None表示永久有效


@router.get("/promos")
async def get_promos(db: Session = Depends(get_db)):
    """获取邀请码列表"""
    promos = db.query(PromoCode).order_by(desc(PromoCode.created_at)).all()
    
    return {
        "items": [
            {
                "id": p.id,
                "code": p.code,
                "plan_type": p.plan_type,
                "duration_days": p.duration_days,
                "max_uses": p.max_uses,
                "used_count": p.used_count,
                "is_active": 1,  # 暂时固定为1（数据库无此字段）
                "expires_at": p.expires_at.isoformat() if p.expires_at else None,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in promos
        ]
    }


def generate_promo_code() -> str:
    """生成12位邀请码"""
    # 使用大写字母和数字，排除容易混淆的字符（0, O, I, 1）
    chars = string.ascii_uppercase.replace('O', '').replace('I', '') + string.digits.replace('0', '').replace('1', '')
    return ''.join(random.choices(chars, k=12))


@router.post("/promos")
async def create_promo(request: CreatePromoRequest, db: Session = Depends(get_db)):
    """创建邀请码"""
    try:
        # 验证计划类型
        valid_plans = ['free', 'pro', 'team']
        if request.plan_type not in valid_plans:
            raise HTTPException(status_code=400, detail="无效的会员计划类型")
        
        # 生成唯一邀请码
        max_attempts = 10
        code = None
        for _ in range(max_attempts):
            generated_code = generate_promo_code()
            existing = db.query(PromoCode).filter(PromoCode.code == generated_code).first()
            if not existing:
                code = generated_code
                break
        
        if not code:
            raise HTTPException(status_code=500, detail="生成邀请码失败，请重试")
        
        # 计算过期时间
        expires_at = None
        if request.expires_days:
            expires_at = datetime.now() + timedelta(days=request.expires_days)
        
        # 创建邀请码（移除is_active，数据库无此字段）
        promo_code = PromoCode(
            code=code,
            plan_type=request.plan_type,
            duration_days=request.duration_days,
            max_uses=request.max_uses,
            expires_at=expires_at
        )
        db.add(promo_code)
        db.commit()
        db.refresh(promo_code)
        
        return {
            "success": True,
            "message": "邀请码创建成功",
            "data": {
                "id": promo_code.id,
                "code": promo_code.code,
                "plan_type": promo_code.plan_type,
                "duration_days": promo_code.duration_days,
                "max_uses": promo_code.max_uses,
                "used_count": promo_code.used_count,
                "is_active": 1,  # 暂时固定为1
                "expires_at": promo_code.expires_at.isoformat() if promo_code.expires_at else None,
                "created_at": promo_code.created_at.isoformat() if promo_code.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建邀请码失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建邀请码失败: {str(e)}")


@router.put("/promos/{promo_id}/toggle")
async def toggle_promo(promo_id: int, db: Session = Depends(get_db)):
    """启用/禁用邀请码（功能暂时禁用，数据库无is_active字段）"""
    promo = db.query(PromoCode).filter(PromoCode.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="邀请码不存在")
    
    # 暂时无法切换状态，因为数据库无is_active字段
    return {"success": True, "message": "功能暂时不可用", "is_active": 1}


@router.delete("/promos/{promo_id}")
async def delete_promo(promo_id: int, db: Session = Depends(get_db)):
    """删除邀请码"""
    promo = db.query(PromoCode).filter(PromoCode.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="邀请码不存在")
    
    db.delete(promo)
    db.commit()
    
    return {"success": True, "message": "删除成功"}

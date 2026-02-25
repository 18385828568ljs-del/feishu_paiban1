from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import random
import string
from app.database import get_db
from app.models.user import User, Membership, Order, OrderStatus
from app.models.plan import MembershipPlan
from app.services.yungouos import yungouos_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payment", tags=["payment"])

# 默认会员计划配置（数据库不可用时兜底）
DEFAULT_PLANS = [
    {
        "id": "pro",
        "name": "专业版",
        "price": 2900,  # 29元（分）
        "original_price": 5900,
        "duration_days": 30
    },
    {
        "id": "team",
        "name": "团队版",
        "price": 9900,  # 99元（分）
        "original_price": 19900,
        "duration_days": 30
    }
]

def _get_plans_from_db(db: Session) -> List[dict]:
    """
    从数据库读取会员计划；如果表不存在/查询失败，回退到默认配置。
    """
    try:
        rows = db.query(MembershipPlan).order_by(MembershipPlan.id.asc()).all()
        if not rows:
            return DEFAULT_PLANS
        return [
            {
                "id": r.id,
                "name": r.name,
                "price": int(r.price),
                "original_price": int(r.original_price) if r.original_price is not None else None,
                "duration_days": int(r.duration_days),
            }
            for r in rows
        ]
    except Exception:
        return DEFAULT_PLANS


class CreateOrderRequest(BaseModel):
    feishu_user_id: str
    plan_type: str  # 'pro' or 'team'


class OrderResponse(BaseModel):
    id: int
    order_no: str
    plan_type: str
    amount: int
    status: str
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class NativePayResponse(BaseModel):
    qr_code_url: str  # 二维码URL
    order_no: str


def generate_order_no() -> str:
    """生成订单号：ORD{日期时间}{6位随机码}"""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD{date_str}{random_str}"


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


@router.get("/plans")
async def get_plans(db: Session = Depends(get_db)):
    """获取会员计划列表"""
    return {"plans": _get_plans_from_db(db)}


@router.post("/create-order", response_model=OrderResponse)
async def create_order(request: CreateOrderRequest, db: Session = Depends(get_db)):
    """创建订单"""
    try:
        # 验证计划类型
        plans = _get_plans_from_db(db)
        plan = next((p for p in plans if p["id"] == request.plan_type), None)
        if not plan:
            raise HTTPException(status_code=400, detail="无效的会员计划类型")
        
        # 获取用户
        user = db.query(User).filter(User.feishu_user_id == request.feishu_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 生成订单号
        order_no = generate_order_no()
        
        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=user.id,
            plan_type=request.plan_type,
            plan_name=plan["name"],  # 设置计划名称
            amount=plan["price"],
            original_price=plan.get("original_price"),  # 设置原价
            discount_price=(plan.get("original_price") or 0) - plan["price"],  # 优惠金额 = 原价 - 实际价格
            status="PENDING",  # 使用大写值匹配数据库枚举
            expires_at=datetime.now() + timedelta(days=7)  # 订单有效期7天
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return OrderResponse(
            id=order.id,
            order_no=order.order_no,
            plan_type=order.plan_type,
            amount=order.amount,
            status=order.status,
            expires_at=order.expires_at,
            created_at=order.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建订单失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")


async def _create_alipay_native_pay(request: CreateOrderRequest, db: Session):
    """创建支付宝扫码支付订单（内部实现，不对外暴露路由）"""
    try:
        # 验证计划类型
        plans = _get_plans_from_db(db)
        plan = next((p for p in plans if p["id"] == request.plan_type), None)
        if not plan:
            raise HTTPException(status_code=400, detail="无效的会员计划类型")
        
        # 获取用户
        user = db.query(User).filter(User.feishu_user_id == request.feishu_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 生成订单号
        order_no = generate_order_no()
        
        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=user.id,
            plan_type=request.plan_type,
            plan_name=plan["name"],
            amount=plan["price"],
            original_price=plan.get("original_price"),
            discount_price=(plan.get("original_price") or 0) - plan["price"],
            status="PENDING",
            expires_at=datetime.now() + timedelta(days=7)
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # 调用YunGouOs创建支付订单
        try:
            pay_result = await yungouos_service.create_native_pay(
                order_no=order_no,
                amount=plan["price"],
                subject=f"{plan['name']}会员"
            )
            
            # 解析返回的二维码URL（根据实际API响应格式调整）
            qr_code_url = ""
            if isinstance(pay_result, dict):
                # 可能的字段名：qr_code, code_url, qr_url, pay_url等
                qr_code_url = (
                    pay_result.get("qr_code") or 
                    pay_result.get("code_url") or 
                    pay_result.get("qr_url") or 
                    pay_result.get("pay_url") or
                    pay_result.get("data", {}).get("qr_code") or
                    ""
                )
            
            if not qr_code_url:
                logger.error(f"YunGouOs返回结果中未找到二维码URL: {pay_result}")
                raise HTTPException(status_code=500, detail="支付接口返回异常，未获取到二维码")
            
            return NativePayResponse(
                qr_code_url=qr_code_url,
                order_no=order_no
            )
        except Exception as e:
            # 支付接口调用失败，更新订单状态
            order.status = "CANCELLED"
            db.commit()
            logger.error(f"创建支付订单失败: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"创建支付订单失败: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建支付订单异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建支付订单失败: {str(e)}")


# === 新对外接口（与前端约定）===
# 创建订单: POST /api/payment/alipay/create
@router.post("/alipay/create", response_model=NativePayResponse)
async def alipay_create(request: CreateOrderRequest, db: Session = Depends(get_db)):
    """
    创建支付宝/YunGouOS 扫码支付订单（对外统一入口）。

    返回结构与旧接口保持一致（旧接口路由已移除）。
    """
    return await _create_alipay_native_pay(request=request, db=db)


@router.post("/alipay/notify")
async def alipay_notify(request: Request, db: Session = Depends(get_db)):
    """支付宝支付回调通知"""
    try:
        # 获取回调参数（可能是form-data或JSON格式）
        form_data = await request.form()
        params = {k: v for k, v in form_data.items()}
        
        # 如果没有form数据，尝试JSON
        if not params:
            try:
                json_data = await request.json()
                params = json_data
            except:
                pass
        
        logger.info(f"收到支付回调: {params}")
        
        # 验证签名
        if not yungouos_service.verify_notify(params):
            logger.error(f"支付回调签名验证失败: {params}")
            return {"code": "FAIL", "msg": "签名验证失败"}
        
        # 获取订单号
        order_no = params.get("out_trade_no") or params.get("order_no")
        if not order_no:
            logger.error(f"回调参数中缺少订单号: {params}")
            return {"code": "FAIL", "msg": "缺少订单号"}
        
        # 查询订单
        order = db.query(Order).filter(Order.order_no == order_no).first()
        if not order:
            logger.error(f"订单不存在: {order_no}")
            return {"code": "FAIL", "msg": "订单不存在"}
        
        # 检查订单状态（幂等性处理）
        if order.status == "PAID":
            logger.info(f"订单已支付，忽略重复回调: {order_no}")
            return {"code": "SUCCESS", "msg": "订单已处理"}
        
        if order.status == "CANCELLED":
            logger.warning(f"订单已取消，无法支付: {order_no}")
            return {"code": "FAIL", "msg": "订单已取消"}
        
        # 检查支付状态（根据YunGouOs回调参数调整）
        pay_status = params.get("status") or params.get("trade_status") or params.get("pay_status")
        if pay_status not in ["SUCCESS", "success", "PAID", "paid", "1"]:
            logger.warning(f"支付状态异常: {pay_status}, 订单: {order_no}")
            return {"code": "FAIL", "msg": f"支付状态异常: {pay_status}"}
        
        # 验证金额（可选，但建议做）
        pay_amount = params.get("total_fee") or params.get("amount") or params.get("money")
        if pay_amount:
            try:
                pay_amount_int = int(float(pay_amount))
                if pay_amount_int != order.amount:
                    logger.error(f"支付金额不匹配: 订单{order.amount}分, 回调{pay_amount_int}分")
                    return {"code": "FAIL", "msg": "支付金额不匹配"}
            except:
                pass
        
        # 获取计划信息
        plans = _get_plans_from_db(db)
        plan = next((p for p in plans if p["id"] == order.plan_type), None)
        if not plan:
            logger.error(f"无效的会员计划: {order.plan_type}")
            return {"code": "FAIL", "msg": "无效的会员计划"}
        
        # 获取用户
        user = db.query(User).filter(User.id == order.user_id).first()
        if not user:
            logger.error(f"用户不存在: {order.user_id}")
            return {"code": "FAIL", "msg": "用户不存在"}
        
        # 更新订单状态
        order.status = "PAID"
        order.paid_at = datetime.now()
        
        # 更新会员信息
        update_membership(user, order.plan_type, plan["duration_days"], db)
        
        db.commit()
        
        logger.info(f"订单支付成功: {order_no}")
        return {"code": "SUCCESS", "msg": "处理成功"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"处理支付回调失败: {str(e)}", exc_info=True)
        return {"code": "FAIL", "msg": f"处理失败: {str(e)}"}


# 查询进度: GET /api/payment/alipay/query
@router.get("/alipay/query")
async def alipay_query(order_no: str, db: Session = Depends(get_db)):
    """
    查询支付进度（对外统一入口）。

    参数:
    - order_no: 商户订单号
    """
    return await _get_order_status(order_no=order_no, db=db)


async def _get_order_status(order_no: str, db: Session):
    """查询订单状态（内部实现，不对外暴露路由）"""
    try:
        order = db.query(Order).filter(Order.order_no == order_no).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 如果订单还是待支付状态，可以主动查询一次支付平台
        if order.status == "PENDING":
            try:
                query_result = await yungouos_service.query_order(order_no)
                # 根据查询结果更新订单状态（根据实际API响应格式调整）
                if isinstance(query_result, dict):
                    pay_status = (
                        query_result.get("status") or 
                        query_result.get("trade_status") or 
                        query_result.get("pay_status") or
                        query_result.get("data", {}).get("status") or
                        ""
                    )
                    if pay_status in ["SUCCESS", "success", "PAID", "paid", "1"]:
                        # 订单已支付，更新状态
                        plans = _get_plans_from_db(db)
                        plan = next((p for p in plans if p["id"] == order.plan_type), None)
                        if plan:
                            user = db.query(User).filter(User.id == order.user_id).first()
                            if user:
                                order.status = "PAID"
                                order.paid_at = datetime.now()
                                update_membership(user, order.plan_type, plan["duration_days"], db)
                                db.commit()
            except Exception as e:
                logger.warning(f"查询订单状态失败: {str(e)}")
                # 查询失败不影响返回当前状态
        
        return {
            "order_no": order.order_no,
            "status": order.status.lower() if order.status else "pending",
            "paid_at": order.paid_at.isoformat() if order.paid_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询订单状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询订单状态失败: {str(e)}")


@router.get("/orders")
async def get_orders(feishu_user_id: str, db: Session = Depends(get_db)):
    """获取订单列表"""
    user = db.query(User).filter(User.feishu_user_id == feishu_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
    
    return {
        "orders": [
            {
                "id": order.id,
                "order_no": order.order_no,
                "plan_type": order.plan_type,
                "amount": order.amount,
                "status": order.status,
                "expires_at": order.expires_at.isoformat() if order.expires_at else None,
                "paid_at": order.paid_at.isoformat() if order.paid_at else None,
                "created_at": order.created_at.isoformat()
            }
            for order in orders
        ]
    }


from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.template import Template as TemplateModel
from ..models.user import User
from ..schemas.template import Template, TemplateCreate, TemplateUpdate
from ..auth import get_current_user_optional

router = APIRouter(
    prefix="/api/templates",
    tags=["templates"]
)

@router.get("/", response_model=List[Template])
def get_templates(
    search: Optional[str] = Query(None, description="搜索关键词，支持按模板名称搜索"),
    template_type: Optional[str] = Query(None, description="模板类型：'normal' 或 'ai'"),
    owner: Optional[str] = Query(None, description="所有者过滤：'me' 表示只返回当前用户的模板"),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """获取模板列表（用户自己的模板 + 系统模板）"""
    import logging
    logger = logging.getLogger(__name__)
    
    user = None
    if current_user:
        user = db.query(User).filter(User.feishu_user_id == current_user["sub"]).first()
    
    # 如果请求 owner=me，只返回当前用户自己的非系统模板
    if owner == 'me':
        if not user:
            return []
        query = db.query(TemplateModel).filter(
            TemplateModel.is_system == False,
            (TemplateModel.owner_id == user.id) | (TemplateModel.owner_id == None)
        )
    else:
        # 基础查询：系统模板对所有人可见
        query = db.query(TemplateModel).filter(TemplateModel.is_system == True)
        
        # 如果用户已登录，还要包含用户自己的模板
        if user:
            # 查询条件：系统模板 OR 用户自己的模板 OR owner_id为NULL的非系统模板（兼容旧数据）
            query = db.query(TemplateModel).filter(
                (TemplateModel.is_system == True) | 
                (TemplateModel.owner_id == user.id) |
                ((TemplateModel.owner_id == None) & (TemplateModel.is_system == False))
            )
        else:
            if current_user:
                logger.warning(f"[get_templates] 未找到用户: {current_user.get('sub')}")
    
    if search:
        # 按模板名称模糊搜索
        search_filter = TemplateModel.name.ilike(f"%{search}%")
        query = query.filter(search_filter)
    
    if template_type:
        # 按模板类型过滤
        query = query.filter(TemplateModel.template_type == template_type)
    
    templates = query.order_by(TemplateModel.id).all()
    
    return templates

from ..models.team import TeamTemplate, TeamMember

@router.get("/{template_id}", response_model=Template)
def get_template(
    template_id: int,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """获取单个模板（系统模板 / 用户自己的模板 / 团队共享给用户的模板）"""
    template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 检查权限
    if template.is_system:
        return template

    if not current_user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    user = db.query(User).filter(User.feishu_user_id == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=403, detail="用户不存在")

    # 1. 检查是否为所有者
    if template.owner_id == user.id:
        return template
        
    # 2. 检查是否为团队共享模板
    # 查询是否存在一条共享记录：该模板被分享到了某个团队，且当前用户是该团队成员
    shared_access = db.query(TeamTemplate).join(
        TeamMember, TeamTemplate.team_id == TeamMember.team_id
    ).filter(
        TeamTemplate.template_id == template_id,
        TeamMember.user_id == user.id
    ).first()
    
    if shared_access:
        return template

    raise HTTPException(status_code=403, detail="无权访问此模板")

@router.post("/", response_model=Template)
def create_template(
    template: TemplateCreate,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """创建新模板（自动关联到当前用户）"""
    try:
        # 获取用户ID
        user = None
        if current_user:
            user = db.query(User).filter(User.feishu_user_id == current_user["sub"]).first()
        
        # 检查模板名称是否已存在
        if user:
            # 检查用户自己的模板中是否有重名
            existing = db.query(TemplateModel).filter(
                TemplateModel.owner_id == user.id,
                TemplateModel.name == template.name
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"模板名称 '{template.name}' 已存在，请使用其他名称")
        else:
            # 未登录用户，检查系统模板中是否有重名
            existing = db.query(TemplateModel).filter(
                TemplateModel.is_system == True,
                TemplateModel.name == template.name
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"模板名称 '{template.name}' 已存在，请使用其他名称")
        
        template_dict = template.dict()
        # 设置 owner_id（如果用户已登录）
        template_dict['owner_id'] = user.id if user else None
        # 用户创建的模版，确保is_system为False
        template_dict['is_system'] = False
        
        db_template = TemplateModel(**template_dict)
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建模板失败: {str(e)}")

@router.put("/{template_id}", response_model=Template)
def update_template(
    template_id: int, 
    template: TemplateUpdate,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """更新模板（只能更新自己的模板）"""
    try:
        db_template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
        if not db_template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        # 禁止修改系统模板
        if db_template.is_system:
            raise HTTPException(status_code=403, detail="系统模板不能修改")
        
        # 检查权限：只能修改自己的模板
        if not current_user:
            raise HTTPException(status_code=401, detail="需要登录")
        
        user = db.query(User).filter(User.feishu_user_id == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=403, detail="用户不存在")
        
        # 允许修改：owner_id 匹配，或 owner_id 为空（兼容旧数据，自动认领）
        if db_template.owner_id is None:
            db_template.owner_id = user.id
        elif db_template.owner_id != user.id:
            raise HTTPException(status_code=403, detail="无权修改此模板")
        
        for key, value in template.dict(exclude_none=True).items():
            setattr(db_template, key, value)
        
        db.commit()
        db.refresh(db_template)
        return db_template
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新模板失败: {str(e)}")

@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """删除模板（只能删除自己的模板）"""
    try:
        db_template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
        if not db_template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        # 禁止删除系统模板
        if db_template.is_system:
            raise HTTPException(status_code=403, detail="系统模板不能删除")
        
        # 检查权限：只能删除自己的模板
        if not current_user:
            raise HTTPException(status_code=401, detail="需要登录")
        
        user = db.query(User).filter(User.feishu_user_id == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=403, detail="用户不存在")
        
        # 允许删除：owner_id 匹配，或 owner_id 为空（兼容旧数据）
        if db_template.owner_id is not None and db_template.owner_id != user.id:
            raise HTTPException(status_code=403, detail="无权删除此模板")
        
        db.delete(db_template)
        db.commit()
        return {"success": True, "message": "模板已删除"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除模板失败: {str(e)}")

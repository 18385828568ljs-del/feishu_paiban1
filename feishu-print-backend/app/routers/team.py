from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import secrets
import logging
from app.database import get_db
from app.models.user import User, Membership, PlanType
from app.models.team import Team, TeamMember, TeamInvite, TeamTemplate, TeamRole, InviteStatus
from app.models.template import Template

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/team", tags=["team"])


# ==================== 请求/响应模型 ====================

class CreateTeamRequest(BaseModel):
    name: str
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    max_members: int
    member_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class TeamMemberResponse(BaseModel):
    id: int
    user_id: int
    feishu_user_id: str
    nickname: Optional[str]
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class InviteMemberRequest(BaseModel):
    invitee_feishu_id: Optional[str] = None  # 可选，为空时生成通用邀请码


class InviteResponse(BaseModel):
    invite_code: str
    expires_at: datetime


class AcceptInviteRequest(BaseModel):
    feishu_user_id: str
    invite_code: str


class ShareTemplateRequest(BaseModel):
    template_id: int
    can_edit: bool = False


class TeamTemplateResponse(BaseModel):
    id: int
    template_id: int
    template_name: str
    shared_by_nickname: Optional[str]
    can_edit: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateMemberRoleRequest(BaseModel):
    role: str  # 'admin' or 'member'


# ==================== 辅助函数 ====================

def get_user_by_feishu_id(db: Session, feishu_user_id: str) -> User:
    user = db.query(User).filter(User.feishu_user_id == feishu_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


def check_team_permission(db: Session, user: User, team: Team, require_admin: bool = False):
    """检查用户是否有团队权限"""
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team.id,
        TeamMember.user_id == user.id
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="您不是该团队成员")
    
    if require_admin and member.role == TeamRole.MEMBER:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    return member


# ==================== 团队管理 API ====================

@router.post("/create", response_model=TeamResponse)
async def create_team(
    request: CreateTeamRequest,
    feishu_user_id: str,
    db: Session = Depends(get_db)
):
    """创建团队"""
    try:
        user = get_user_by_feishu_id(db, feishu_user_id)
        
        # 检查用户是否已拥有团队
        existing_team = db.query(Team).filter(Team.owner_id == user.id).first()
        if existing_team:
            raise HTTPException(status_code=400, detail="您已拥有一个团队")
        
        # 创建团队
        team = Team(
            name=request.name,
            description=request.description,
            owner_id=user.id,
            max_members=5
        )
        db.add(team)
        db.flush()
        
        # 将创建者添加为团队所有者
        owner_member = TeamMember(
            team_id=team.id,
            user_id=user.id,
            role=TeamRole.OWNER
        )
        db.add(owner_member)
        db.commit()
        db.refresh(team)
        
        return TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            owner_id=team.owner_id,
            max_members=team.max_members,
            member_count=1,
            created_at=team.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建团队失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建团队失败: {str(e)}")


@router.get("/my-team", response_model=Optional[TeamResponse])
async def get_my_team(feishu_user_id: str, db: Session = Depends(get_db)):
    """获取我所在的团队"""
    user = get_user_by_feishu_id(db, feishu_user_id)
    
    # 查找用户所在的团队
    member = db.query(TeamMember).filter(TeamMember.user_id == user.id).first()
    if not member:
        return None
    
    team = member.team
    member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
    
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        owner_id=team.owner_id,
        max_members=team.max_members,
        member_count=member_count,
        created_at=team.created_at
    )


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def get_team_members(
    team_id: int,
    feishu_user_id: str,
    db: Session = Depends(get_db)
):
    """获取团队成员列表"""
    user = get_user_by_feishu_id(db, feishu_user_id)
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    check_team_permission(db, user, team)
    
    from sqlalchemy.orm import joinedload
    members = db.query(TeamMember).options(joinedload(TeamMember.user)).filter(TeamMember.team_id == team_id).all()
    
    result = []
    for member in members:
        result.append(TeamMemberResponse(
            id=member.id,
            user_id=member.user_id,
            feishu_user_id=member.user.feishu_user_id,
            nickname=member.user.nickname,
            role=member.role.value,
            joined_at=member.joined_at
        ))
    
    return result


# ==================== 成员邀请 API ====================

@router.post("/{team_id}/invite", response_model=InviteResponse)
async def invite_member(
    team_id: int,
    request: InviteMemberRequest,
    feishu_user_id: str,
    db: Session = Depends(get_db)
):
    """邀请成员加入团队"""
    user = get_user_by_feishu_id(db, feishu_user_id)
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    check_team_permission(db, user, team, require_admin=True)
    
    # 检查团队人数限制
    member_count = db.query(TeamMember).filter(TeamMember.team_id == team_id).count()
    if member_count >= team.max_members:
        raise HTTPException(status_code=400, detail=f"团队成员已达上限（{team.max_members}人）")
    
    # 如果指定了被邀请人，检查是否已在团队中
    if request.invitee_feishu_id:
        invitee = db.query(User).filter(User.feishu_user_id == request.invitee_feishu_id).first()
        if invitee:
            existing_member = db.query(TeamMember).filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id == invitee.id
            ).first()
            if existing_member:
                raise HTTPException(status_code=400, detail="该用户已是团队成员")
    
    # 创建邀请（如果 invitee_feishu_id 为空，则为通用邀请码）
    invite_code = secrets.token_urlsafe(16)
    invite = TeamInvite(
        team_id=team_id,
        inviter_id=user.id,
        invitee_feishu_id=request.invitee_feishu_id,
        invite_code=invite_code,
        expires_at=datetime.now() + timedelta(days=7)
    )
    db.add(invite)
    db.commit()
    
    return InviteResponse(
        invite_code=invite_code,
        expires_at=invite.expires_at
    )


@router.post("/accept-invite")
async def accept_invite(request: AcceptInviteRequest, db: Session = Depends(get_db)):
    """接受团队邀请"""
    try:
        user = get_user_by_feishu_id(db, request.feishu_user_id)
        
        # 查找邀请（支持通用邀请码和指定用户的邀请码）
        invite = db.query(TeamInvite).filter(
            TeamInvite.invite_code == request.invite_code,
            TeamInvite.status == InviteStatus.PENDING
        ).first()
        
        if not invite:
            raise HTTPException(status_code=404, detail="邀请不存在或已失效")
        
        # 如果邀请码指定了用户，检查是否匹配
        if invite.invitee_feishu_id and invite.invitee_feishu_id != request.feishu_user_id:
            raise HTTPException(status_code=403, detail="此邀请码不是为您生成的")
        
        if invite.expires_at < datetime.now():
            invite.status = InviteStatus.EXPIRED
            db.commit()
            raise HTTPException(status_code=400, detail="邀请已过期")
        
        # 检查用户是否已在其他团队
        existing_member = db.query(TeamMember).filter(TeamMember.user_id == user.id).first()
        if existing_member:
            raise HTTPException(status_code=400, detail="您已在其他团队中，请先退出当前团队")
        
        # 检查团队人数
        team = invite.team
        member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
        if member_count >= team.max_members:
            raise HTTPException(status_code=400, detail="团队成员已满")
        
        # 加入团队
        member = TeamMember(
            team_id=team.id,
            user_id=user.id,
            role=TeamRole.MEMBER
        )
        db.add(member)
        
        invite.status = InviteStatus.ACCEPTED
        db.commit()
        
        return {"success": True, "team_name": team.name}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"接受邀请失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"接受邀请失败: {str(e)}")


@router.delete("/{team_id}/members/{member_id}")
async def remove_member(
    team_id: int,
    member_id: int,
    feishu_user_id: str,
    db: Session = Depends(get_db)
):
    """移除团队成员"""
    try:
        user = get_user_by_feishu_id(db, feishu_user_id)
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="团队不存在")
        
        operator = check_team_permission(db, user, team, require_admin=True)
        
        member = db.query(TeamMember).filter(
            TeamMember.id == member_id,
            TeamMember.team_id == team_id
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")
        
        if member.role == TeamRole.OWNER:
            raise HTTPException(status_code=400, detail="无法移除团队所有者")
        
        db.delete(member)
        db.commit()
        
        return {"success": True, "message": "已成功移除成员"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"移除成员失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"移除成员失败: {str(e)}")


@router.post("/{team_id}/leave")
async def leave_team(team_id: int, feishu_user_id: str, db: Session = Depends(get_db)):
    """退出团队"""
    try:
        user = get_user_by_feishu_id(db, feishu_user_id)
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="团队不存在")
        
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user.id
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="您不是该团队成员")
        
        if member.role == TeamRole.OWNER:
            raise HTTPException(status_code=400, detail="团队所有者无法退出，请先转让团队或解散团队")
        
        db.delete(member)
        db.commit()
        
        return {"success": True, "message": "已成功退出团队"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"退出团队失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"退出团队失败: {str(e)}")


@router.put("/{team_id}/members/{member_id}/role")
async def update_member_role(
    team_id: int,
    member_id: int,
    request: UpdateMemberRoleRequest,
    feishu_user_id: str,
    db: Session = Depends(get_db)
):
    """更新成员角色"""
    try:
        user = get_user_by_feishu_id(db, feishu_user_id)
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="团队不存在")
        
        operator = check_team_permission(db, user, team)
        if operator.role != TeamRole.OWNER:
            raise HTTPException(status_code=403, detail="只有团队所有者可以更改成员角色")
        
        member = db.query(TeamMember).filter(
            TeamMember.id == member_id,
            TeamMember.team_id == team_id
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")
        
        if member.role == TeamRole.OWNER:
            raise HTTPException(status_code=400, detail="无法更改所有者角色")
        
        if request.role == "admin":
            member.role = TeamRole.ADMIN
        elif request.role == "member":
            member.role = TeamRole.MEMBER
        else:
            raise HTTPException(status_code=400, detail="无效的角色")
        
        db.commit()
        
        return {"success": True, "message": "成员角色已更新"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新成员角色失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新成员角色失败: {str(e)}")


@router.delete("/{team_id}/dissolve")
async def dissolve_team(
    team_id: int,
    feishu_user_id: str,
    db: Session = Depends(get_db)
):
    """解散团队（仅团队所有者可以操作）"""
    try:
        user = get_user_by_feishu_id(db, feishu_user_id)
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="团队不存在")
        
        # 检查是否为团队所有者
        if team.owner_id != user.id:
            raise HTTPException(status_code=403, detail="只有团队所有者可以解散团队")
        
        # 验证用户确实是团队成员（双重检查）
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user.id,
            TeamMember.role == TeamRole.OWNER
        ).first()
        
        if not member:
            raise HTTPException(status_code=403, detail="您不是该团队的所有者")
        
        # 先删除所有相关的邀请记录（避免外键约束错误）
        db.query(TeamInvite).filter(TeamInvite.team_id == team_id).delete()
        
        # 删除团队（级联删除会同时删除所有成员和共享模板）
        db.delete(team)
        db.commit()
        
        return {"success": True, "message": "团队已成功解散"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"解散团队失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"解散团队失败: {str(e)}")


@router.post("/{team_id}/transfer-ownership")
async def transfer_ownership(
    team_id: int,
    new_owner_member_id: int,
    feishu_user_id: str,
    db: Session = Depends(get_db)
):
    """转让团队所有权"""
    try:
        user = get_user_by_feishu_id(db, feishu_user_id)
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="团队不存在")
        
        # 检查是否为团队所有者
        if team.owner_id != user.id:
            raise HTTPException(status_code=403, detail="只有团队所有者可以转让所有权")
        
        # 查找新所有者成员
        new_owner_member = db.query(TeamMember).filter(
            TeamMember.id == new_owner_member_id,
            TeamMember.team_id == team_id
        ).first()
        
        if not new_owner_member:
            raise HTTPException(status_code=404, detail="新所有者成员不存在")
        
        if new_owner_member.user_id == user.id:
            raise HTTPException(status_code=400, detail="不能将所有权转让给自己")
        
        # 更新团队所有者
        team.owner_id = new_owner_member.user_id
        
        # 更新成员角色：原所有者变为管理员，新所有者变为所有者
        old_owner_member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user.id
        ).first()
        
        if old_owner_member:
            old_owner_member.role = TeamRole.ADMIN
        
        new_owner_member.role = TeamRole.OWNER
        
        db.commit()
        
        return {"success": True, "message": "团队所有权已成功转让"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"转让所有权失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"转让所有权失败: {str(e)}")


# ==================== 模版共享 API ====================

@router.post("/{team_id}/templates/share")
async def share_template(
    team_id: int,
    request: ShareTemplateRequest,
    feishu_user_id: str,
    db: Session = Depends(get_db)
):
    """共享模版到团队"""
    user = get_user_by_feishu_id(db, feishu_user_id)
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    check_team_permission(db, user, team)
    
    # 检查模版是否存在
    template = db.query(Template).filter(Template.id == request.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模版不存在")
    
    # 检查是否已共享
    existing = db.query(TeamTemplate).filter(
        TeamTemplate.team_id == team_id,
        TeamTemplate.template_id == request.template_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该模版已共享到团队")
    
    # 共享模版
    team_template = TeamTemplate(
        team_id=team_id,
        template_id=request.template_id,
        shared_by_id=user.id,
        can_edit=request.can_edit
    )
    db.add(team_template)
    db.commit()
    
    return {"success": True}


@router.get("/{team_id}/templates", response_model=List[TeamTemplateResponse])
async def get_team_templates(
    team_id: int,
    feishu_user_id: str,
    db: Session = Depends(get_db)
):
    """获取团队共享模版列表"""
    user = get_user_by_feishu_id(db, feishu_user_id)
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    check_team_permission(db, user, team)
    
    from sqlalchemy.orm import joinedload
    team_templates = db.query(TeamTemplate).options(
        joinedload(TeamTemplate.shared_by),
        joinedload(TeamTemplate.template)
    ).filter(TeamTemplate.team_id == team_id).all()
    
    result = []
    for tt in team_templates:
        result.append(TeamTemplateResponse(
            id=tt.id,
            template_id=tt.template_id,
            template_name=tt.template.name,
            shared_by_nickname=tt.shared_by.nickname,
            can_edit=tt.can_edit,
            created_at=tt.created_at
        ))
    
    return result


@router.delete("/{team_id}/templates/{team_template_id}")
async def unshare_template(
    team_id: int,
    team_template_id: int,
    feishu_user_id: str,
    db: Session = Depends(get_db)
):
    """取消共享模版"""
    user = get_user_by_feishu_id(db, feishu_user_id)
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    check_team_permission(db, user, team, require_admin=True)
    
    team_template = db.query(TeamTemplate).filter(
        TeamTemplate.id == team_template_id,
        TeamTemplate.team_id == team_id
    ).first()
    
    if not team_template:
        raise HTTPException(status_code=404, detail="共享记录不存在")
    
    db.delete(team_template)
    db.commit()
    
    return {"success": True}

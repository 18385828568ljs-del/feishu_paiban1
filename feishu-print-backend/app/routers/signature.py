from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import secrets

from ..database import get_db
from ..models.signature import Signature

router = APIRouter(prefix="/api/signatures", tags=["signatures"])

class SignatureCreate(BaseModel):
    template_id: Optional[int] = None
    record_id: Optional[str] = None
    signer_name: str
    signer_email: Optional[str] = None
    document_title: Optional[str] = None
    document_html: Optional[str] = None
    expires_hours: int = 72

class SignatureSubmit(BaseModel):
    signature_data: str

class SignatureResponse(BaseModel):
    id: int
    template_id: Optional[int]
    record_id: Optional[str]
    signer_name: str
    signer_email: Optional[str]
    document_title: Optional[str]
    document_html: Optional[str]
    signature_data: Optional[str]
    signed_at: Optional[datetime]
    status: str
    token: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=SignatureResponse)
def create_signature(request: SignatureCreate, db: Session = Depends(get_db)):
    """创建签名请求"""
    try:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=request.expires_hours)
        
        signature = Signature(
            template_id=request.template_id,
            record_id=request.record_id,
            signer_name=request.signer_name,
            signer_email=request.signer_email,
            document_title=request.document_title,
            document_html=request.document_html,
            token=token,
            expires_at=expires_at,
            status="pending"
        )
        
        db.add(signature)
        db.commit()
        db.refresh(signature)
        
        return signature
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建签名请求失败: {str(e)}")

@router.get("/token/{token}", response_model=SignatureResponse)
def get_signature_by_token(token: str, db: Session = Depends(get_db)):
    """通过token获取签名请求"""
    try:
        signature = db.query(Signature).filter(Signature.token == token).first()
        
        if not signature:
            raise HTTPException(status_code=404, detail="签名请求不存在")
        
        if signature.status == "expired" or datetime.now() > signature.expires_at:
            signature.status = "expired"
            db.commit()
            raise HTTPException(status_code=400, detail="签名链接已过期")
        
        return signature
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取签名请求失败: {str(e)}")

@router.put("/token/{token}", response_model=SignatureResponse)
def submit_signature(token: str, request: SignatureSubmit, db: Session = Depends(get_db)):
    """提交签名"""
    try:
        signature = db.query(Signature).filter(Signature.token == token).first()
        
        if not signature:
            raise HTTPException(status_code=404, detail="签名请求不存在")
        
        if signature.status == "signed":
            raise HTTPException(status_code=400, detail="已签名，无需重复签名")
        
        if signature.status == "expired" or datetime.now() > signature.expires_at:
            signature.status = "expired"
            db.commit()
            raise HTTPException(status_code=400, detail="签名链接已过期")
        
        signature.signature_data = request.signature_data
        signature.signed_at = datetime.now()
        signature.status = "signed"
        
        db.commit()
        db.refresh(signature)
        
        return signature
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"提交签名失败: {str(e)}")

@router.get("/{signature_id}", response_model=SignatureResponse)
def get_signature(signature_id: int, db: Session = Depends(get_db)):
    """获取签名详情"""
    signature = db.query(Signature).filter(Signature.id == signature_id).first()
    
    if not signature:
        raise HTTPException(status_code=404, detail="签名不存在")
    
    return signature

@router.get("/")
def list_signatures(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取签名列表"""
    signatures = db.query(Signature).offset(skip).limit(limit).all()
    return signatures

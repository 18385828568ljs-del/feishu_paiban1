from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models.feedback import Feedback

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


class FeedbackCreate(BaseModel):
    content: str
    contact: Optional[str] = None
    user_id: Optional[int] = None


class FeedbackResponse(BaseModel):
    success: bool
    message: str


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackCreate, db: Session = Depends(get_db)):
    """提交反馈"""
    if not request.content or len(request.content.strip()) < 5:
        return FeedbackResponse(success=False, message="反馈内容至少需要5个字符")
    
    feedback = Feedback(
        user_id=request.user_id,
        content=request.content.strip(),
        contact=request.contact
    )
    db.add(feedback)
    db.commit()
    
    return FeedbackResponse(success=True, message="感谢您的反馈！")

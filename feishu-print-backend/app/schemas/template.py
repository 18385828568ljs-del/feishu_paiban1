from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TemplateBase(BaseModel):
    name: str
    content: str
    template_type: Optional[str] = 'normal'  # 'normal' 或 'ai'
    is_system: Optional[bool] = False  # 是否为系统模版

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    template_type: Optional[str] = None
    is_system: Optional[bool] = None

class Template(TemplateBase):
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

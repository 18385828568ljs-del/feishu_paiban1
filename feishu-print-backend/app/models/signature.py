from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from ..database import Base
import enum

class SignatureStatus(str, enum.Enum):
    pending = "pending"
    signed = "signed"
    expired = "expired"

class Signature(Base):
    __tablename__ = "signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, nullable=True)
    record_id = Column(String(255), nullable=True)
    signer_name = Column(String(100), nullable=False)
    signer_email = Column(String(255), nullable=True)
    document_title = Column(String(255), nullable=True)
    document_html = Column(Text, nullable=True)
    signature_data = Column(Text, nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="pending")
    token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from app.core.logger import get_logger

logger = get_logger(service="conversation")

class DialogueType(enum.Enum):
    NORMAL = "普通对话"
    DEEP_THINKING = "深度思考"
    WEB_SEARCH = "联网检索"
    RAG = "RAG 问答"

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    status = Column(String(20), default="ongoing")
    dialogue_type = Column(Enum(DialogueType), nullable=False)
    
    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan") 

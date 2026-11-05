from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class TaskItem(Base):
    """任务数据模型（用于展示 Remote Agent 异步重构与测试）"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending", index=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

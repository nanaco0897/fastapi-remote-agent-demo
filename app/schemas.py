from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SystemStatus(BaseModel):
    platform: str
    python_version: str
    memory_usage_mb: float

class TaskStats(BaseModel):
    total: int
    by_status: Dict[str, int]

class MetricsResponse(BaseModel):
    status: str
    uptime_seconds: float
    start_time: datetime
    system: SystemStatus
    tasks: TaskStats

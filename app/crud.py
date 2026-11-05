from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import TaskItem
from app.schemas import TaskCreate, TaskUpdate

async def create_task(db: AsyncSession, task_in: TaskCreate) -> TaskItem:
    task = TaskItem(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status or "pending"
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

async def get_task(db: AsyncSession, task_id: int) -> Optional[TaskItem]:
    result = await db.execute(select(TaskItem).where(TaskItem.id == task_id))
    return result.scalar_one_or_none()

async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[TaskItem]:
    result = await db.execute(
        select(TaskItem).offset(skip).limit(limit).order_by(TaskItem.id.desc())
    )
    return list(result.scalars().all())

async def update_task(db: AsyncSession, task_id: int, task_in: TaskUpdate) -> Optional[TaskItem]:
    task = await get_task(db, task_id)
    if not task:
        return None
    
    update_data = task_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(task, field, val)
        
    await db.commit()
    await db.refresh(task)
    return task

async def delete_task(db: AsyncSession, task_id: int) -> bool:
    task = await get_task(db, task_id)
    if not task:
        return False
    await db.delete(task)
    await db.commit()
    return True

async def get_task_metrics(db: AsyncSession) -> Dict[str, Any]:
    """获取任务总量及按状态分组统计"""
    total_result = await db.execute(select(func.count(TaskItem.id)))
    total_tasks = total_result.scalar_one() or 0

    status_result = await db.execute(
        select(TaskItem.status, func.count(TaskItem.id)).group_by(TaskItem.status)
    )
    by_status = {status: count for status, count in status_result.all()}

    return {
        "total": total_tasks,
        "by_status": by_status
    }

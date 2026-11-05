from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, Base, get_db
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app import crud

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 异步初始化数据表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 优雅释放连接池
    await engine.dispose()

app = FastAPI(
    title="Antigravity Remote Agent Demo API",
    description="示例一演示项目：全异步重构、自动化测试与高并发接口",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
async def health_check():
    """健康检查路由（用于 Remote Agent 自动化就绪探针）"""
    return {
        "status": "healthy",
        "engine": "async-sqlite",
        "environment": "antigravity-remote-agent-ready"
    }

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_new_task(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    """创建新任务"""
    return await crud.create_task(db, task_in)

@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
async def list_tasks(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    """查询任务列表"""
    return await crud.get_tasks(db, skip=skip, limit=limit)

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task_by_id(task_id: int, db: AsyncSession = Depends(get_db)):
    """获取指定任务详情"""
    task = await crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_existing_task(task_id: int, task_in: TaskUpdate, db: AsyncSession = Depends(get_db)):
    """更新任务"""
    task = await crud.update_task(db, task_id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
async def delete_existing_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """删除任务"""
    deleted = await crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return None

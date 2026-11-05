import os
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import Base, get_db

TEST_DB_FILE = "test_runner.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30}
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def setup_test_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_health_check():
    """验证健康检查探针"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["engine"] == "async-sqlite"

@pytest.mark.asyncio
async def test_task_crud_lifecycle():
    """验证任务完整的创建、查询、更新与删除生命周期"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. 创建任务
        create_res = await client.post(
            "/tasks",
            json={"title": "Remote Agent Task", "description": "Cloud execution demo"}
        )
        assert create_res.status_code == 201
        created = create_res.json()
        task_id = created["id"]
        assert created["title"] == "Remote Agent Task"
        assert created["status"] == "pending"

        # 2. 查询详情
        get_single = await client.get(f"/tasks/{task_id}")
        assert get_single.status_code == 200
        assert get_single.json()["title"] == "Remote Agent Task"

        # 3. 更新状态
        update_res = await client.put(
            f"/tasks/{task_id}",
            json={"status": "completed"}
        )
        assert update_res.status_code == 200
        assert update_res.json()["status"] == "completed"

        # 4. 删除任务
        del_res = await client.delete(f"/tasks/{task_id}")
        assert del_res.status_code == 204

        # 5. 确认已不存在
        get_after_del = await client.get(f"/tasks/{task_id}")
        assert get_after_del.status_code == 404

@pytest.mark.asyncio
async def test_batch_task_creation():
    """验证批量顺序写入与查询完整性"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for i in range(5):
            res = await client.post(
                "/tasks",
                json={"title": f"Batch Task #{i}", "description": f"Worker payload {i}"}
            )
            assert res.status_code == 201

        list_res = await client.get("/tasks?limit=100")
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 5

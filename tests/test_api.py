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

@pytest.mark.asyncio
async def test_metrics_endpoint():
    """验证 /metrics 性能监控接口输出系统状态与动态任务统计"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. 验证空库状态下的指标与系统基础信息
        res = await client.get("/metrics")
        assert res.status_code == 200
        data = res.json()

        assert data["status"] == "healthy"
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0
        assert "start_time" in data

        # 系统状态指标验证
        system_info = data["system"]
        assert "platform" in system_info
        assert "python_version" in system_info
        assert isinstance(system_info["memory_usage_mb"], (int, float))
        assert system_info["memory_usage_mb"] > 0

        # 初始任务统计验证
        task_info = data["tasks"]
        assert task_info["total"] == 0
        assert task_info["by_status"] == {}

        # 2. 写入不同状态的任务并验证聚合统计
        await client.post("/tasks", json={"title": "Pending Task 1", "status": "pending"})
        await client.post("/tasks", json={"title": "Pending Task 2", "status": "pending"})
        create_res3 = await client.post("/tasks", json={"title": "Completed Task 1", "status": "completed"})
        task3_id = create_res3.json()["id"]

        metrics_res2 = await client.get("/metrics")
        assert metrics_res2.status_code == 200
        data2 = metrics_res2.json()

        assert data2["tasks"]["total"] == 3
        assert data2["tasks"]["by_status"]["pending"] == 2
        assert data2["tasks"]["by_status"]["completed"] == 1

        # 3. 状态变更后再次核验
        await client.put(f"/tasks/{task3_id}", json={"status": "archived"})
        metrics_res3 = await client.get("/metrics")
        assert metrics_res3.status_code == 200
        data3 = metrics_res3.json()

        assert data3["tasks"]["total"] == 3
        assert data3["tasks"]["by_status"]["pending"] == 2
        assert data3["tasks"]["by_status"].get("completed", 0) == 0
        assert data3["tasks"]["by_status"]["archived"] == 1

        # 4. 删除任务后核验
        await client.delete(f"/tasks/{task3_id}")
        metrics_res4 = await client.get("/metrics")
        assert metrics_res4.status_code == 200
        data4 = metrics_res4.json()

        assert data4["tasks"]["total"] == 2
        assert data4["tasks"]["by_status"]["pending"] == 2
        assert "archived" not in data4["tasks"]["by_status"]

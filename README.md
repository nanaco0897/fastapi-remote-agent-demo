# Antigravity Remote Agent 示例项目 (FastAPI 异步微服务)

本仓库是配合 **Google Antigravity 官方文档 [antigravity.google/docs/remote-agents](https://antigravity.google.com)** 打造的**示例一：Web 端全脱机工作流（GitHub 仓库深度重构）** 标准演示套件。

项目提供了一个生产级的异步 FastAPI + SQLAlchemy 2.0 + SQLite 系统，配备完整的端到端自动化测试门禁、异步 CRUD 路由，以及专供 Remote Agent 执行的提示词模版。

---

## 📁 项目目录结构

```text
fastapi-remote-agent-demo/
├── .antigravity/
│   └── task.md                     # Remote Agent 自动化任务定义与 Prompt 模版
├── app/
│   ├── __init__.py
│   ├── database.py                 # SQLAlchemy 异步引擎 (aiosqlite) 与 Session 依赖
│   ├── models.py                   # ORM 数据模型 (TaskItem)
│   ├── schemas.py                  # Pydantic v2 请求与响应定义
│   ├── crud.py                     # 异步 CRUD 业务逻辑
│   └── main.py                     # FastAPI 路由、中间件与生命周期配置
├── tests/
│   └── test_api.py                 # Pytest 异步测试套件 (健康探针/CRUD/批量测试)
├── pytest.ini                      # Pytest 异步执行配置
├── requirements.txt                # 运行依赖规范
├── simulate_remote_agent_run.py    # 本地一键仿真云端 Remote Agent 执行流程
└── README.md                       # 说明文档
```

---

## 🚀 示例一实战流程：通过 Google Antigravity Web 端运行 Remote Agent

### 第一步：将本示例推送到您的 GitHub
1. 在 GitHub 上新建一个仓库（例如 `fastapi-remote-agent-demo`）；
2. 在本地执行推送：
   ```bash
   cd /Users/bin/.gemini/antigravity/scratch/fastapi-remote-agent-demo
   git init
   git add .
   git commit -m "Initial commit of Remote Agent Demo"
   git branch -M main
   git remote add origin https://github.com/<your-username>/fastapi-remote-agent-demo.git
   git push -u origin main
   ```

### 第二步：在 Antigravity Web 端创建 Remote Agent 沙盒
1. 打开浏览器访问 [antigravity.google.com](https://antigravity.google.com)；
2. 点击右上角 **New Project**；
3. 选择 **Remote Agent** 模式（运行在 Google 托管的隔离云容器中）；
4. 选择您刚推送的 GitHub 仓库并关联 `main` 分支。

### 第三步：下发 Prompt 指令（全脱机自治执行）
在 Web 界面对话框中，将 [`.antigravity/task.md`](file:///Users/bin/.gemini/antigravity/scratch/fastapi-remote-agent-demo/.antigravity/task.md) 中的指令粘贴发送：

```text
你好！请在当前云端 Remote Agent 沙盒中对本仓库进行自动化升级：
1. 请运行测试套件确保当前所有测试用例正常通过；
2. 为 FastAPI 服务新增一个 `/metrics` 性能监控端点，能够统计服务启动时间与内存运行概况；
3. 在 `tests/test_api.py` 中补充针对 `/metrics` 的单元测试；
4. 再次运行 `pytest -v tests/` 确保所有测试 100% 绿色通过；
5. 新建分支 `feature/cloud-metrics` 并提交代码变更，输出详细的改动报告。
整个过程请在云端自主执行到底，即使我断开网络连接也不要中断。
```

### 第四步：合盖离线与断开
* 发送指令后，Remote Agent 会在 Google 官方云端容器中自主拉取依赖、运行测试、修改代码；
* 此时您可以直接**合上电脑休眠、关闭浏览器、或者断开网络**；
* 云端任务会持续推进直至完成，不受本地网络和电力状态影响。

### 第五步：手机/多端随时查看与接力
* 在手机浏览器打开 [antigravity.google.com](https://antigravity.google.com)；
* 查看 Remote Agent 的执行进度、终端输出日志、自动化生成的测试报告与 Git Diff；
* 满意后一键指令合入主分支。

---

## 💻 本地极速验证

在未推送 GitHub 之前，您也可以在本地通过内置的仿真脚本提前体验 Remote Agent 执行过程：

```bash
cd /Users/bin/.gemini/antigravity/scratch/fastapi-remote-agent-demo
python3 simulate_remote_agent_run.py
```

或直接通过 `uv` 运行完整测试套件：
```bash
uv run --with-requirements requirements.txt pytest -v tests/
```

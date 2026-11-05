# Google Antigravity Remote Agent 自动化任务定义

本文件定义了在 [antigravity.google.com](https://antigravity.google.com) 或 `agy --remote-agent` 中执行的云端全脱机重构任务。

---

## 任务目标 (Objective)
在 Google 托管的隔离云端沙盒环境中，对当前 FastAPI 异步任务系统进行性能增强、健康度验证与自动化测试全覆盖：
1. 检查并确保项目环境与依赖处于最新就绪状态；
2. 扩充并发测试用例并执行 `pytest` 自动化测试套件；
3. 新增 `/metrics` 接口输出系统指标（如请求计数、运行时间）；
4. 确保所有修改通过自动化门禁，并在云端提交 Git 分支。

---

## 云端自主执行流程指令 (Agent Execution Steps)

```bash
# 步骤 1：安装依赖
pip install -r requirements.txt

# 步骤 2：执行回归测试套件验证初始状态
pytest -v tests/

# 步骤 3：在 app/main.py 中增加 /metrics 监控端点
# 步骤 4：在 tests/test_api.py 中补充监控端点与高负载测试
# 步骤 5：重新运行 pytest 确认 100% 通过

# 步骤 6：生成独立分支并提交
git checkout -b feature/cloud-metrics
git commit -am "feat: add /metrics probe and async benchmark suite"
```

---

## 粘贴至 Web 端对话框的 Prompt 指令模版

```text
你好！请在当前云端 Remote Agent 沙盒中对本仓库进行自动化升级：
1. 请运行测试套件确保当前所有测试用例正常通过；
2. 为 FastAPI 服务新增一个 `/metrics` 性能监控端点，能够统计服务启动时间与内存运行概况；
3. 在 `tests/test_api.py` 中补充针对 `/metrics` 的单元测试；
4. 再次运行 `pytest -v tests/` 确保所有测试 100% 绿色通过；
5. 新建分支 `feature/cloud-metrics` 并提交代码变更，输出详细的改动报告。
整个过程请在云端自主执行到底，即使我断开网络连接也不要中断。
```

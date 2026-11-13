# 学术论文助手 Agent (Based on OpenManus)

这是一个基于 OpenManus 源码进行二次开发的垂直领域 Agent。旨在解决大语言模型在长对话处理学术论文时容易“跑偏”，以及容易“幻觉调用工具”的问题。

## ✨ 核心工程改造点（面试重点）

1. **分层 Memory 机制**：重写 `PaperAgent.think()` 方法。摒弃全量上下文堆叠，仅保留最近 6 条对话，并动态注入论文摘要和用户偏好。有效避免长对话中注意力被稀释导致的跑偏。
2. **工具调用门控 (Tool Gating)**：在代码层加入前置路由与 Prompt 约束。当用户输入涉及“引用/查证”时，强制注入 Prompt 要求调用搜索工具；当涉及“总结”时，抑制重复解析，提升工具调用的确定性。
3. **外部计划状态机 (External Plan State)**：引入 `PlanManager` 维护独立的 Markdown 任务清单。代码层在工具调用成功后自动将进度打勾（`[✓]`）。每轮 `think()` 将清单注入 System Prompt，让模型始终拥有全局坐标，对抗多轮任务跑偏。
4. **死循环兜底防御**：解决模型仅输出文本导致 ReAct 循环卡死的问题。通过构造 `SimpleNamespace` 伪造 `terminate` 工具调用，安全中断任务流，避免 Agent 陷入死循环。

## 🛠️ 项目结构
- `app/agent/paper_agent.py`: 核心 Agent 逻辑（包含重写的 `think()` 和门控逻辑）
- `app/agent/plan_manager.py`: 外部计划状态机管理器
- `app/tool/mock_paper_tool.py`: 论文解析与引用搜索的 Mock 工具

## 🚀 快速运行
1. 配置环境（参考 OpenManus 官方指南，需 Python 3.12）。
2. 在 `config/config.toml` 中填入你的 LLM API Key（推荐 DeepSeek）。
3. 激活环境并运行：
```bash
python main.py

from app.agent.toolcall import ToolCallAgent
from app.tool import ToolCollection
from app.tool.terminate import Terminate
from app.tool.python_execute import PythonExecute
from app.tool.mock_paper_tool import MockPaperParser, MockCitationSearch
from app.agent.plan_manager import PlanManager
from app.schema import Message
from types import SimpleNamespace


class PaperAgent(ToolCallAgent):
    name: str = "PaperAgent"
    description: str = "学术论文助手，负责解析论文、总结内容、查证引用"
    system_prompt: str = "你是一个学术论文助手，负责解析论文、总结内容、查证引用。"
    
    # 注册所有的工具
    available_tools: ToolCollection = ToolCollection(
        PythonExecute(),
        MockPaperParser(),
        MockCitationSearch(),
        Terminate(),
    )

    @classmethod
    async def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.plan_manager = PlanManager()
        return instance

    async def think(self) -> bool:
        user_input = ""
        for msg in reversed(self.memory.messages):
            if msg.role == "user":
                user_input = msg.content or ""
                break

        # 1. 动态拼接 System Prompt（加入计划清单）
        current_system_prompt = self.system_prompt + "\n\n【当前状态】用户尚未上传论文。"
        
        # 注入外部计划
        current_plan = self.plan_manager.get_plan()
        current_system_prompt += f"\n\n【当前任务计划（请参照此清单执行，不要跑偏）】\n{current_plan}\n"

        # 【门控规则】
        citation_keywords = ["引用", "参考文献", "相关工作", "查证", "citation"]
        if any(kw in user_input for kw in citation_keywords):
            current_system_prompt += "\n【强制规则】用户询问引用/参考文献。你必须调用 search_citation 工具，不得凭记忆回答。"
        
        if "总结" in user_input:
            current_system_prompt += "\n【抑制规则】如果需要总结，请优先使用已有信息，无需调用 parse_paper 再次解析。"

        # 2. 只取最近 6 条对话
        recent_messages = self.memory.messages[-6:]
        messages_for_llm = [{"role": "system", "content": current_system_prompt}]
        for msg in recent_messages:
            messages_for_llm.append(msg.to_dict())

        # 3. 调用大模型
        response = await self.llm.ask_tool(
            messages=messages_for_llm,
            tools=self.available_tools.to_params(),
            tool_choice="auto",
        )

        # 4. 保存回答（转字典绕过 Pydantic）
        if response.content or response.tool_calls:
            dict_tool_calls = []
            if response.tool_calls:
                for tc in response.tool_calls:
                    dict_tool_calls.append({
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    })
            self.memory.add_message(
                Message(role="assistant", content=response.content or "", tool_calls=dict_tool_calls)
            )

        self.tool_calls = response.tool_calls or []

        # 5. 【动态更新计划清单】如果调用了特定工具，自动打勾
        if self.tool_calls:
            for tc in self.tool_calls:
                if tc.function.name == "parse_paper":
                    self.plan_manager.mark_done("解析论文 PDF")
                elif tc.function.name == "search_citation":
                    self.plan_manager.mark_done("识别核心参考文献")

        # 6. 【兜底】强制结束
        if response.content and not response.tool_calls:
            print("【Debug】模型只回答了文本，强制结束任务。")
            fake_function = SimpleNamespace(name="terminate", arguments='{"status": "success"}')
            fake_tool_call = SimpleNamespace(id="auto_terminate", type="function", function=fake_function)
            self.tool_calls = [fake_tool_call]

        return len(self.tool_calls) > 0
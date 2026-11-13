from pathlib import Path

class PlanManager:
    def __init__(self, file_path="paper_memory/plan.md"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text(
                "# 执行计划\n"
                "- [ ] 解析论文 PDF\n"
                "- [ ] 生成全文摘要\n"
                "- [ ] 识别核心参考文献\n"
                "- [ ] 等待用户提问\n",
                encoding="utf-8"
            )

    def get_plan(self) -> str:
        return self.file_path.read_text(encoding="utf-8")

    def mark_done(self, step_name: str):
        content = self.get_plan()
        content = content.replace(f"- [ ] {step_name}", f"- [✓] {step_name}")
        self.file_path.write_text(content, encoding="utf-8")
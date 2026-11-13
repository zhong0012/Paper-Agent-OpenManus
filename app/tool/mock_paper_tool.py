from app.tool.base import BaseTool

class MockPaperParser(BaseTool):
    name: str = "parse_paper"
    description: str = "解析用户上传的论文 PDF，返回结构化摘要信息"
    parameters: dict = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "PDF 文件路径"}
        },
        "required": ["file_path"]
    }

    async def execute(self, file_path: str = "", **kwargs) -> str:
        # 模拟返回解析后的 JSON 数据
        return '{"title": "Attention Is All You Need", "sections": ["Introduction", "Model", "Experiments"], "key_refs": ["Vaswani 2017", "Devlin 2018"]}'


class MockCitationSearch(BaseTool):
    name: str = "search_citation"
    description: str = "搜索论文中引用的参考文献，查证其真实信息"
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "要搜索的文献关键词"}
        },
        "required": ["query"]
    }

    async def execute(self, query: str = "", **kwargs) -> str:
        # 模拟返回搜索到的引用结果
        return '{"results": [{"title": "BERT", "year": 2018, "venue": "NAACL"}]}'
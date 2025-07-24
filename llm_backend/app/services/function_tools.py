from typing import List, Dict, Any, Callable
import json
from dataclasses import dataclass

@dataclass
class FunctionTool:
    """函数工具定义"""
    name: str
    description: str
    parameters: Dict
    handler: Callable

class ToolRegistry:
    """工具注册中心"""
    def __init__(self):
        self._tools: Dict[str, FunctionTool] = {}
    
    def register(self, tool: FunctionTool):
        """注册工具"""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> FunctionTool:
        """获取工具"""
        return self._tools.get(name)
    
    def get_tools_definition(self) -> List[Dict]:
        """获取工具定义列表(用于API调用)"""
        return [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
        } for tool in self._tools.values()]
    
    async def execute_tool(self, name: str, arguments: str) -> Any:
        """执行工具"""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        
        args = json.loads(arguments)
        return await tool.handler(**args) 
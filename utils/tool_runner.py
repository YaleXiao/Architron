import logging

logger = logging.getLogger("architron")


class ToolRunner:
    def __init__(self, session):
        self._session = session
        self._artifacts = {}
        self.tools = []
        self.tool_to_session = {}
        self.tools_config = []

    async def setup(self):
        tools_resp = await self._session.list_tools()
        self.tools = tools_resp.tools
        for tool in tools_resp.tools:
            self.tool_to_session[tool.name] = self._session
        self.tools_config = self._generate_tools_config()

    def _generate_tools_config(self):
        """根据 MCP 服务器提供的工具生成 OpenAI 格式的工具配置"""
        tools_config = []
        for tool in self.tools:
            tool_config = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            tools_config.append(tool_config)
        return tools_config

    def get_tools_config(self):
        """获取动态生成的工具配置"""
        return self.tools_config

    async def run_all(self, content):
        results = []
        for block in content:
            if block.type == "tool_use":
                result = await self._run_one(block)
                results.append(result)
        return results

    async def _run_one(self, block):
        session = self.tool_to_session.get(block.name)
        if not session:
            return {
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": f"Tool {block.name} not found",
                "is_error": True,
            }
        try:
            logger.debug(
                f"[ToolRunner] Calling tool {block.name} with input: {block.input}"
            )
            logger.debug(f"[ToolRunner] Input type: {type(block.input)}")
            if isinstance(block.input, dict):
                logger.debug(f"[ToolRunner] Input keys: {list(block.input.keys())}")
                if "code" in block.input:
                    logger.debug(f"[ToolRunner] Code to execute: {block.input['code']}")
            resp = await session.call_tool(block.name, block.input)
            content = resp.content[0].text if resp.content else ""
            logger.debug(f"[ToolRunner] Tool {block.name} returned: {content}")
            self._artifacts[block.id] = content
            return {
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": content,
            }
        except Exception as e:
            logger.error(f"[ToolRunner] Error calling tool {block.name}: {e}")
            return {
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(e),
                "is_error": True,
            }

    def get_artifacts(self):
        return self._artifacts

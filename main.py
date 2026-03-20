import anyio
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp import StdioServerParameters
from agents.sub_agents.sub_agent import SubAgent
from config import MCP_SERVERS


async def main():
    server = MCP_SERVERS[0]
    server_params = StdioServerParameters(
        command=server["command"], args=server["args"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            agent = SubAgent(session=session)
            await agent.setup()
            await agent.chat()


anyio.run(main)

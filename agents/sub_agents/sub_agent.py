import os
import json
import logging
from utils.llm_client import LLMClient, TextBlock, ToolUseBlock
from utils.tool_runner import ToolRunner
from utils.rag import RAG
from utils.schema import TaskInput, TaskOutput, AgentCapability
from config import (
    CONFIG,
    PROVIDER,
    TOOLS,
    RAG_DIRECTORIES,
    RAG_EXTENSIONS,
    RAG_EXCLUDE,
    RAG_FORCE_REINDEX,
    SYSTEM_PROMPT,
)

logger = logging.getLogger("architron")


def content_to_openai_message(content: list) -> dict:
    """Convert content blocks to OpenAI assistant message format."""
    text_parts = []
    tool_calls = []
    for block in content:
        if isinstance(block, TextBlock):
            text_parts.append(block.text)
        elif isinstance(block, ToolUseBlock):
            tool_calls.append(
                {
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": json.dumps(block.input),
                    },
                }
            )
    msg = {"role": "assistant"}
    if text_parts:
        msg["content"] = "".join(text_parts)
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return msg


class SubAgent:
    def __init__(self, session):
        self.llm_client = LLMClient()
        self.tool_runner = ToolRunner(session)
        self.rag = RAG()
        if self.rag.is_empty() or RAG_FORCE_REINDEX:
            self.rag.scan_and_index(RAG_DIRECTORIES, RAG_EXTENSIONS, RAG_EXCLUDE)

    async def setup(self):
        await self.tool_runner.setup()

    async def run(self, task_input: TaskInput) -> TaskOutput:
        try:
            messages = [{"role": "user", "content": task_input.instruction}]
            if task_input.use_rag:
                rag_result = self.rag.query(task_input.instruction)
                if rag_result.strip():
                    messages[0]["content"] = (
                        f"Context:\n{rag_result}\n\nQuestion:\n{task_input.instruction}"
                    )

            MAX_ITERATIONS = 10
            for _ in range(MAX_ITERATIONS):
                # 使用动态获取的工具配置
                tools_config = self.tool_runner.get_tools_config()
                response = self.llm_client.create(
                    messages, tools=tools_config, system=SYSTEM_PROMPT
                )
                if response["stop_reason"] == "end_turn":
                    return TaskOutput(
                        task_id=task_input.task_id,
                        status="done",
                        result=response["text"],
                        artifacts=self.tool_runner.get_artifacts(),
                    )
                elif response["stop_reason"] == "tool_use":
                    tool_results = await self.tool_runner.run_all(response["content"])
                    messages.append(content_to_openai_message(response["content"]))
                    for result in tool_results:
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": result["tool_use_id"],
                                "content": result["content"],
                            }
                        )
                else:
                    break
            return TaskOutput(
                task_id=task_input.task_id,
                status="error",
                result="Max iterations exceeded",
                artifacts=self.tool_runner.get_artifacts(),
            )
        except Exception as e:
            return TaskOutput(
                task_id=task_input.task_id,
                status="error",
                result=str(e),
                artifacts=self.tool_runner.get_artifacts(),
            )

    async def chat(self):
        messages = []
        while True:
            user_input = input("You: ")
            if user_input.lower() == "quit":
                break
            # Create TaskInput with RAG enabled by default
            task_input = TaskInput(
                task_id="chat",
                instruction=user_input,
                use_rag=True  # Enable RAG by default
            )
            # Use run method to process input with RAG
            output = await self.run(task_input)
            print("Agent: ", output.result)
            # Maintain message history
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": output.result})

    def capability(self) -> AgentCapability:
        skills = (
            [tool.name for tool in self.tool_runner.tools]
            if hasattr(self.tool_runner, "tools")
            else []
        )
        return AgentCapability(
            agent_id="sub_agent",
            name="Sub Agent",
            description="A sub-agent capable of using tools and RAG",
            skills=skills,
        )

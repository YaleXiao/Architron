import json
import re
import logging
from dataclasses import dataclass
from typing import Any, Optional, TypedDict, NotRequired, Literal
from openai import OpenAI
from config import CONFIG, PROVIDER

logger = logging.getLogger("architron")


def fix_json_keys(text: str) -> str:
    """Fix unquoted keys and string values in JSON-like text."""
    text = re.sub(r"(\{|\,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', text)
    text = re.sub(r":\s*([a-zA-Z_][a-zA-Z0-9_]*)(\s*[\,\}\]])", r': "\1"\2', text)
    return text


def parse_tool_calls_from_text(text: str) -> list[dict]:
    """Parse tool calls from text when model outputs JSON instead of using native tool calling."""
    tool_calls = []

    def try_parse_tool_call(json_str: str):
        try:
            data = json.loads(json_str)
            if isinstance(data, dict) and "name" in data and "arguments" in data:
                call_sig = (
                    f"{data['name']}:{json.dumps(data['arguments'], sort_keys=True)}"
                )
                if not any(c.get("sig") == call_sig for c in tool_calls):
                    tool_calls.append(
                        {
                            "id": f"call_{len(tool_calls)}",
                            "name": data["name"],
                            "arguments": json.dumps(data["arguments"]),
                            "sig": call_sig,
                        }
                    )
        except (json.JSONDecodeError, TypeError):
            pass

    patterns = [r"```json\s*([\s\S]*?)\s*```", r"```\s*([\s\S]*?)\s*```"]
    for pattern in patterns:
        for match in re.findall(pattern, text, re.DOTALL):
            try_parse_tool_call(fix_json_keys(match.strip()))

    depth = 0
    start = -1
    for i, c in enumerate(text):
        if c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                json_str = text[start : i + 1]
                try_parse_tool_call(json_str)
                start = -1

    for tc in tool_calls:
        tc.pop("sig", None)
    return tool_calls


@dataclass
class TextBlock:
    type: str = "text"
    text: str = ""


@dataclass
class ToolUseBlock:
    type: str = "tool_use"
    id: str = ""
    name: str = ""
    input: Optional[dict] = None


class LLMClient:
    client: OpenAI

    def __init__(self):
        cfg = CONFIG[PROVIDER]
        if PROVIDER == "ollama":
            base_url = cfg["base_url"]
            if not base_url.endswith("/v1"):
                base_url = base_url.rstrip("/") + "/v1"
            self.client = OpenAI(base_url=base_url, api_key="ollama")
        self.model = cfg["model"]
        self.max_tokens = cfg["max_tokens"]

    def create(self, messages, system=None, tools=None, on_stream=None):
        client = self.client  # type: ignore[assignment]
        logger.debug(
            f"[LLM] Calling ollama with tools={tools is not None}, stream={on_stream is not None}"
        )

        # Prepare messages with system prompt if provided
        final_messages = messages
        if system:
            final_messages = [{"role": "system", "content": system}] + messages

        # Prepare tools (ensure it's a list or None)
        final_tools = tools if tools else []

        if on_stream:
            resp = client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=final_messages,
                tools=final_tools,
                stream=True,
            )
            full_text = ""
            tool_calls = []
            finish = None
            for chunk in resp:
                delta = chunk.choices[0].delta
                if delta.content:
                    # Handle surrogate characters that can't be encoded
                    clean_content = delta.content.encode("utf-8", "ignore").decode(
                        "utf-8"
                    )
                    full_text += clean_content
                    on_stream(clean_content)
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        if tc.function:
                            if tc.index >= len(tool_calls):
                                tool_calls.append(
                                    {
                                        "id": tc.id or f"call_{tc.index}",
                                        "name": tc.function.name or "",
                                        "arguments": tc.function.arguments or "",
                                    }
                                )
                            else:
                                tool_calls[tc.index]["arguments"] += (
                                    tc.function.arguments or ""
                                )
                if chunk.choices[0].finish_reason:
                    finish = chunk.choices[0].finish_reason
                    logger.debug(f"[LLM] Stream finish_reason: {finish}")
            logger.debug(
                f"[LLM] Stream ended, tool_calls count: {len(tool_calls)}, finish: {finish}"
            )
            if full_text:
                text_content = full_text
            else:
                text_content = ""
            if tool_calls:
                content = [
                    ToolUseBlock(
                        id=tc["id"], name=tc["name"], input=json.loads(tc["arguments"])
                    )
                    for tc in tool_calls
                ]
            else:
                content = [TextBlock(text=text_content)]
            return {
                "stop_reason": finish,
                "content": content,
                "text": text_content,
            }
        else:
            resp = client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=final_messages,
                tools=final_tools,
                stream=False,
            )
            choice = resp.choices[0]
            message = choice.message
            # Handle surrogate characters in message content
            raw_content = message.content or ""
            text_content = raw_content.encode("utf-8", "ignore").decode("utf-8")
            if message.tool_calls:
                content = [
                    ToolUseBlock(
                        id=tc.id,
                        name=tc.function.name,
                        input=json.loads(tc.function.arguments),
                    )
                    for tc in message.tool_calls
                ]
                stop_reason = "tool_use"
            else:
                # Check if the text content contains JSON tool calls
                parsed_tool_calls = parse_tool_calls_from_text(text_content)
                if parsed_tool_calls:
                    content = [
                        ToolUseBlock(
                            id=tc["id"],
                            name=tc["name"],
                            input=json.loads(tc["arguments"]),
                        )
                        for tc in parsed_tool_calls
                    ]
                    stop_reason = "tool_use"
                else:
                    content = [TextBlock(text=text_content)]
                    stop_reason = choice.finish_reason
            return {
                "stop_reason": stop_reason,
                "content": content,
                "text": text_content,
            }

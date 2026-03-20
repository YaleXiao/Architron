import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Optional, Callable, Union

from config import CONFIG, PROVIDER
import anthropic
from openai import OpenAI

logger = logging.getLogger("architron")


def fix_json_keys(text: str) -> str:
    """Fix unquoted keys and string values in JSON-like text."""
    text = re.sub(r"(\{|\,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', text)
    text = re.sub(r":\s*([a-zA-Z_][a-zA-Z0-9_]*)(\s*[\,\}\]])", r': "\1"\2', text)
    return text


def parse_tool_calls_from_text(text: str) -> list[dict]:
    """Parse tool calls from text when model outputs JSON instead of using native tool calling."""
    tool_calls = []
    patterns = [
        r"```json\s*([\s\S]*?)\s*```",
        r"```\s*([\s\S]*?)\s*```",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            json_text = fix_json_keys(match.strip())
            if json_text.startswith("{"):
                try:
                    data = json.loads(json_text)
                    if "name" in data and "arguments" in data:
                        call_sig = f"{data['name']}:{json.dumps(data['arguments'], sort_keys=True)}"
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
            for line in json_text.split("\n"):
                line = line.strip()
                if not line or not line.startswith("{"):
                    continue
                try:
                    data = json.loads(line)
                    if "name" in data and "arguments" in data:
                        call_sig = f"{data['name']}:{json.dumps(data['arguments'], sort_keys=True)}"
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
                    continue
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
    client: Union[anthropic.Anthropic, OpenAI]

    def __init__(self):
        cfg = CONFIG[PROVIDER]
        if PROVIDER == "anthropic":
            self.client = anthropic.Anthropic(api_key=cfg["api_key"])
        elif PROVIDER == "ollama":
            base_url = cfg["base_url"]
            if not base_url.endswith("/v1"):
                base_url = base_url.rstrip("/") + "/v1"
            self.client = OpenAI(base_url=base_url, api_key="ollama")
        self.model = cfg["model"]
        self.max_tokens = cfg["max_tokens"]

    def create(self, messages, system=None, tools=None, on_stream=None):
        if PROVIDER == "anthropic":
            client = self.client  # type: ignore[assignment]
            if on_stream:
                with client.messages.stream(  # type: ignore[union-attr]
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system or "",
                    tools=tools or [],
                    messages=messages,
                ) as stream:
                    for text in stream.text_stream:
                        on_stream(text)
                    resp = stream.get_final_message()
            else:
                resp = client.messages.create(  # type: ignore[union-attr]
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system or "",
                    tools=tools or [],
                    messages=messages,
                )
            first_block = resp.content[0] if resp.content else None
            text_content = (
                first_block.text  # type: ignore[union-attr]
                if first_block and hasattr(first_block, "text")
                else ""
            )
            return {
                "stop_reason": resp.stop_reason,
                "content": resp.content,
                "text": text_content,
            }
        elif PROVIDER == "ollama":
            client = self.client  # type: ignore[assignment]
            logger.debug(
                f"[LLM] Calling ollama with tools={tools is not None}, stream={on_stream is not None}"
            )
            resp = client.chat.completions.create(  # type: ignore[union-attr]
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "system", "content": system}] + messages
                if system
                else messages,
                tools=tools,  # type: ignore[arg-type]
                stream=on_stream is not None,
            )
            if on_stream:
                full_text = ""
                content = []
                tool_calls = []
                finish = None
                for chunk in resp:
                    if chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        full_text += text
                        on_stream(text)
                    if chunk.choices[0].delta.tool_calls:
                        for tc in chunk.choices[0].delta.tool_calls:
                            if tc.index >= len(tool_calls):
                                tool_calls.append(
                                    {"id": "", "name": "", "arguments": ""}
                                )
                            if tc.id:
                                tool_calls[tc.index]["id"] = tc.id
                            if tc.function:
                                if tc.function.name:
                                    tool_calls[tc.index]["name"] = tc.function.name
                                if tc.function.arguments:
                                    tool_calls[tc.index]["arguments"] += (
                                        tc.function.arguments
                                    )
                    if chunk.choices[0].finish_reason:
                        finish = chunk.choices[0].finish_reason
                        logger.debug(f"[LLM] Stream finish_reason: {finish}")
                logger.debug(
                    f"[LLM] Stream ended, tool_calls count: {len(tool_calls)}, finish: {finish}"
                )
                if not tool_calls and full_text:
                    parsed = parse_tool_calls_from_text(full_text)
                    if parsed:
                        tool_calls = parsed
                        logger.debug(
                            f"[LLM] Parsed {len(tool_calls)} tool calls from text"
                        )
                if full_text:
                    content.append(TextBlock(text=full_text))
                for tc in tool_calls:
                    content.append(
                        ToolUseBlock(
                            id=tc["id"],
                            name=tc["name"],
                            input=json.loads(tc["arguments"])
                            if tc["arguments"]
                            else {},
                        )
                    )
                return {
                    "stop_reason": "tool_use" if tool_calls else "end_turn",
                    "content": content,
                    "text": full_text,
                }
            else:
                msg = resp.choices[0].message
                finish = resp.choices[0].finish_reason

                content = []
                if msg.content:
                    content.append(TextBlock(text=msg.content))
                if msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        content.append(
                            ToolUseBlock(
                                id=tool_call.id,
                                name=tool_call.function.name,
                                input=json.loads(tool_call.function.arguments),
                            )
                        )
                elif msg.content:
                    parsed = parse_tool_calls_from_text(msg.content)
                    if parsed:
                        for tc in parsed:
                            content.append(
                                ToolUseBlock(
                                    id=tc["id"],
                                    name=tc["name"],
                                    input=json.loads(tc["arguments"]),
                                )
                            )

                has_tool_use = any(isinstance(c, ToolUseBlock) for c in content)
                return {
                    "stop_reason": "tool_use" if has_tool_use else "end_turn",
                    "content": content,
                    "text": msg.content or "",
                }

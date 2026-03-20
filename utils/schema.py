from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TaskInput:
    task_id: str
    instruction: str
    use_rag: bool = False
    context: dict = field(default_factory=dict)
    rag_collection: str = "project_code"


@dataclass
class TaskOutput:
    task_id: str
    status: str
    result: str
    artifacts: dict = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class AgentCapability:
    agent_id: str
    name: str
    description: str
    skills: list

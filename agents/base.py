from dataclasses import dataclass
from typing import Any

@dataclass
class AgentResult:
    ok: bool
    message: str
    payload: dict[str, Any] | None = None
from datetime import datetime, timezone
from uuid import uuid4

def build_event(event_type: str, source: str, payload: dict, trace_id: str | None = None, **keys: object) -> dict:
    return {
        "event_id": str(uuid4()),
        "trace_id": trace_id or str(uuid4()),
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        **keys,
        "payload": payload,
    }

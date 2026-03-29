import json

def dumps(event: dict) -> str:
    return json.dumps(event, default=str)

def loads(raw: str) -> dict:
    return json.loads(raw)

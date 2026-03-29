from __future__ import annotations
import os

def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)

def event_bus_mode() -> str:
    return (os.getenv("EVENT_BUS_MODE", "inmemory") or "inmemory").lower()

def feature_store_mode() -> str:
    return (os.getenv("FEATURE_STORE_MODE", "parquet") or "parquet").lower()

def feature_store_path() -> str:
    return os.getenv("FEATURE_STORE_PATH", "/data/feature_store")

def model_registry_path() -> str:
    return os.getenv("MODEL_REGISTRY_PATH", "/data/current_model.json")

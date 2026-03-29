from __future__ import annotations
from abc import ABC, abstractmethod
from utils.config import feature_store_mode, feature_store_path

class FeatureStoreRepository(ABC):
    @abstractmethod
    def append(self, record: dict) -> dict: ...
    @abstractmethod
    def load(self) -> list[dict]: ...
    @abstractmethod
    def overwrite(self, rows: list[dict]) -> None: ...
    @abstractmethod
    def summary(self) -> dict: ...

def build_feature_store_repository():
    mode = feature_store_mode()
    path = feature_store_path()
    if mode == "delta":
        from .delta_store import DeltaFeatureStoreRepository
        return DeltaFeatureStoreRepository(path=path)
    from .parquet_store import ParquetFeatureStoreRepository
    return ParquetFeatureStoreRepository(path=path)

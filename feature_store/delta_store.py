from pathlib import Path
import pandas as pd
try:
    from deltalake import DeltaTable, write_deltalake
except Exception:
    DeltaTable = None
    write_deltalake = None

class DeltaFeatureStoreRepository:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load_df(self):
        if not self.path.exists() or DeltaTable is None:
            return pd.DataFrame()
        return DeltaTable(str(self.path)).to_pandas()

    def append(self, record: dict) -> dict:
        if write_deltalake is None:
            raise RuntimeError("deltalake package is required for FEATURE_STORE_MODE=delta")
        df = self._load_df()
        pid = str(record.get("patient_id")).strip()
        cid = str(record.get("clinic_id")).strip()
        if not df.empty and {"patient_id","clinic_id"}.issubset(df.columns):
            keys = set(zip(df["patient_id"].astype(str).str.strip(), df["clinic_id"].astype(str).str.strip()))
            if (pid, cid) in keys:
                return {"stored": False, "deduped": True, "patient_id": pid, "clinic_id": cid}
        write_deltalake(str(self.path), pd.DataFrame([record]), mode="append" if self.path.exists() else "overwrite")
        return {"stored": True, "deduped": False, "rows_added": 1}

    def load(self) -> list[dict]:
        df = self._load_df()
        return [] if df.empty else df.to_dict(orient="records")

    def overwrite(self, rows: list[dict]) -> None:
        if write_deltalake is None:
            raise RuntimeError("deltalake package is required for FEATURE_STORE_MODE=delta")
        write_deltalake(str(self.path), pd.DataFrame(rows), mode="overwrite")

    def summary(self) -> dict:
        rows = self.load()
        clinics = sorted({r.get("clinic_id") for r in rows if r.get("clinic_id")})
        labeled = sum(1 for r in rows if r.get("diagnosis") is not None)
        return {"mode": "delta", "path": str(self.path), "n_records": len(rows), "n_labeled": labeled, "clinics": clinics}

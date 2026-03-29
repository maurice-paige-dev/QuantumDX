from pathlib import Path
import pandas as pd

class ParquetFeatureStoreRepository:
    def __init__(self, path: str):
        self.path = Path(path if path.endswith(".parquet") else f"{path}.parquet")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load_df(self):
        if not self.path.exists():
            return pd.DataFrame()
        return pd.read_parquet(self.path)

    def append(self, record: dict) -> dict:
        df = self._load_df()
        pid = str(record.get("patient_id")).strip()
        cid = str(record.get("clinic_id")).strip()
        if not df.empty and {"patient_id","clinic_id"}.issubset(df.columns):
            keys = set(zip(df["patient_id"].astype(str).str.strip(), df["clinic_id"].astype(str).str.strip()))
            if (pid, cid) in keys:
                return {"stored": False, "deduped": True, "patient_id": pid, "clinic_id": cid}
        out = pd.concat([df, pd.DataFrame([record])], ignore_index=True) if not df.empty else pd.DataFrame([record])
        out.to_parquet(self.path, index=False)
        return {"stored": True, "deduped": False, "rows": int(len(out))}

    def load(self) -> list[dict]:
        df = self._load_df()
        return [] if df.empty else df.to_dict(orient="records")

    def overwrite(self, rows: list[dict]) -> None:
        pd.DataFrame(rows).to_parquet(self.path, index=False)

    def summary(self) -> dict:
        rows = self.load()
        clinics = sorted({r.get("clinic_id") for r in rows if r.get("clinic_id")})
        labeled = sum(1 for r in rows if r.get("diagnosis") is not None)
        return {"mode": "parquet", "path": str(self.path), "n_records": len(rows), "n_labeled": labeled, "clinics": clinics}

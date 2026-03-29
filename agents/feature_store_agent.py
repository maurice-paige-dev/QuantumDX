import json
from pathlib import Path
import pandas as pd
from .base import AgentResult


class FeatureStoreAgent:

    def __init__(self, path="feature_store/data.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(exist_ok=True)

    def append(self, record):
        df = self.load()

        if not df.empty and "patient_id" in df.columns:
            if str(record["patient_id"]) in set(df["patient_id"].astype(str).tolist()):
                return AgentResult(True, "Record already present", {"patient_id": record["patient_id"]})

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        return AgentResult(True, "Stored", {"path": str(self.path)})

    def load(self):
        if not self.path.exists():
            return pd.DataFrame()

        rows = [json.loads(l) for l in open(self.path)]
        return pd.DataFrame(rows)

    def attach_label(self, patient_id, diagnosis):
        df = self.load()

        if df.empty:
            return AgentResult(False, "Feature store is empty")

        if patient_id not in set(df["patient_id"].tolist()):
            return AgentResult(False, f"patient_id not found: {patient_id}")

        df.loc[df["patient_id"] == patient_id, "diagnosis"] = int(diagnosis)

        with open(self.path, "w", encoding="utf-8") as f:
            for _, row in df.iterrows():
                f.write(json.dumps(row.to_dict()) + "\n")

        return AgentResult(True, "Diagnosis label attached", {
            "patient_id": patient_id,
            "diagnosis": int(diagnosis)
        })
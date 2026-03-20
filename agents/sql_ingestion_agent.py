from __future__ import annotations

from typing import Any
import pandas as pd

from .base import AgentResult
from .sql_patient_data_agent import SqlPatientDataAgent
from observability import get_logger, monitored, IngestionError


class SqlIngestionAgent:
    def __init__(self, sql_agent: SqlPatientDataAgent) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.sql_agent = sql_agent

    @staticmethod
    def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
        sex_value = row["sex"]
        sex = sex_value if isinstance(sex_value, str) else ("M" if int(sex_value) == 1 else "F")

        return {
            "patient_id": str(row["patient_id"]),
            "clinic_id": row["clinic_id"],
            "age": float(row["age"]),
            "sex": sex,
            "heart_rate": float(row["heart_rate"]),
            "bp_systolic": float(row["bp_systolic"]),
            "bp_diastolic": float(row["bp_diastolic"]),
            "wbc": float(row["wbc"]),
            "platelets": float(row["platelets"]),
            "fever": bool(row["fever"]),
            "muscle_pain": bool(row["muscle_pain"]),
            "jaundice": bool(row["jaundice"]),
            "vomiting": bool(row["vomiting"]),
            "confusion": bool(row["confusion"]),
            "headache": bool(row["headache"]),
            "chills": bool(row["chills"]),
            "rigors": bool(row["rigors"]),
            "nausea": bool(row["nausea"]),
            "diarrhea": bool(row["diarrhea"]),
            "cough": bool(row["cough"]),
            "bleeding": bool(row["bleeding"]),
            "prostration": bool(row["prostration"]),
            "oliguria": bool(row["oliguria"]),
            "anuria": bool(row["anuria"]),
            "conjunctival_suffusion": bool(row["conjunctival_suffusion"]),
            "muscle_tenderness": bool(row["muscle_tenderness"]),
            "diagnosis": None if pd.isna(row.get("diagnosis")) else int(row["diagnosis"]),
        }

    @monitored("SqlIngestionAgent", "ingest_recent_for_user")
    def ingest_recent_for_user(self, pipeline, user_id: str, top: int = 100, trace_id: str | None = None) -> AgentResult:
        try:
            result = self.sql_agent.get_patients_for_user(user_id=user_id, top=top, trace_id=trace_id)
            if not result.ok or not result.payload:
                return result

            records = result.payload["records"]
            loaded = 0
            failures: list[dict[str, str]] = []

            for row in records:
                patient = self._normalize_row(row)
                ingest_result = pipeline.add_patient(patient, trace_id=trace_id)
                if ingest_result.ok:
                    loaded += 1
                else:
                    failures.append({
                        "patient_id": str(row.get("patient_id")),
                        "error": ingest_result.message,
                    })

            return AgentResult(
                True,
                "SQL rows ingested into pipeline",
                {
                    "loaded": loaded,
                    "failed": failures,
                    "clinic_id": result.payload["clinic_id"],
                },
            )
        except Exception as exc:
            raise IngestionError(f"Failed SQL ingestion workflow: {exc}") from exc
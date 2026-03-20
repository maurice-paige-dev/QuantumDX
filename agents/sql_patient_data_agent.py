from __future__ import annotations

from typing import Any

import pandas as pd
import pyodbc

from .base import AgentResult
from .vault_agent import VaultAgent
from observability import get_logger, monitored, SqlIntegrationError


class SqlPatientDataAgent:
    def __init__(self, vault_agent: VaultAgent) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.vault_agent = vault_agent

    @staticmethod
    def _build_connection_string(db_config: dict[str, Any]) -> str:
        driver = db_config.get("driver", "ODBC Driver 18 for SQL Server")
        encrypt = db_config.get("encrypt", "yes")
        trust_server_certificate = db_config.get("trust_server_certificate", "yes")

        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
            f"UID={db_config['username']};"
            f"PWD={db_config['password']};"
            f"Encrypt={encrypt};"
            f"TrustServerCertificate={trust_server_certificate};"
        )

    @monitored("SqlPatientDataAgent", "get_connection")
    def get_connection(self, trace_id: str | None = None) -> AgentResult:
        db_result = self.vault_agent.get_database_config(trace_id=trace_id)
        if not db_result.ok or not db_result.payload:
            return db_result

        try:
            conn_str = self._build_connection_string(db_result.payload)
            conn = pyodbc.connect(conn_str)
            return AgentResult(True, "SQL connection established", {"connection": conn})
        except Exception as exc:
            raise SqlIntegrationError(f"Failed to connect to SQL Server: {exc}") from exc

    @monitored("SqlPatientDataAgent", "get_patients_for_user")
    def get_patients_for_user(self, user_id: str, top: int = 100, trace_id: str | None = None) -> AgentResult:
        user_result = self.vault_agent.get_user_info(user_id, trace_id=trace_id)
        if not user_result.ok or not user_result.payload:
            return user_result

        clinic_id = user_result.payload.get("clinic_id")
        if not clinic_id:
            return AgentResult(False, f"No clinic_id found for user {user_id}")

        conn_result = self.get_connection(trace_id=trace_id)
        if not conn_result.ok or not conn_result.payload:
            return conn_result

        conn = conn_result.payload["connection"]

        query = """
        SELECT TOP (?)
            patient_id,
            clinic_id,
            age,
            sex,
            heart_rate,
            bp_systolic,
            bp_diastolic,
            wbc,
            platelets,
            fever,
            muscle_pain,
            jaundice,
            vomiting,
            confusion,
            headache,
            chills,
            rigors,
            nausea,
            diarrhea,
            cough,
            bleeding,
            prostration,
            oliguria,
            anuria,
            conjunctival_suffusion,
            muscle_tenderness,
            diagnosis,
            created_at
        FROM dbo.PatientMLDataset
        WHERE clinic_id = ?
        ORDER BY created_at DESC;
        """

        try:
            df = pd.read_sql(query, conn, params=[top, clinic_id])
            return AgentResult(
                True,
                "Patient data retrieved from SQL Server",
                {
                    "user_id": user_id,
                    "clinic_id": clinic_id,
                    "count": int(len(df)),
                    "records": df.to_dict(orient="records"),
                },
            )
        except Exception as exc:
            raise SqlIntegrationError(f"Failed to query patient data: {exc}") from exc
        finally:
            try:
                conn.close()
            except Exception:
                pass
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pyodbc


CSV_PATH = Path(os.getenv("CLEAN_CSV_PATH", "data/patients_lepto_clean.csv"))

CONN_STR = os.getenv(
    "SQLSERVER_CONN_STR",
    (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=QuantumDx;"
        "UID=sa;"
        "PWD=YourPassword;"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    ),
)

DEFAULT_CLINIC_ID = os.getenv("DEFAULT_CLINIC_ID", "default_clinic")

INSERT_SQL = """
INSERT INTO dbo.PatientIntake
(
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
    diagnosis
)
VALUES
(
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)
"""


def sex_to_int(value: str) -> int:
    return 1 if str(value).upper() == "M" else 0


def main() -> None:
    df = pd.read_csv(CSV_PATH)

    if "clinic_id" not in df.columns:
        df["clinic_id"] = DEFAULT_CLINIC_ID

    df["sex"] = df["sex"].apply(sex_to_int)

    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.fast_executemany = True

    rows = []
    for _, r in df.iterrows():
        rows.append((
            str(r["patient_id"]) if "patient_id" in df.columns else None,
            r["clinic_id"],
            int(r["age"]),
            int(r["sex"]),
            int(r["heart_rate"]),
            int(r["bp_systolic"]),
            int(r["bp_diastolic"]),
            int(r["wbc"]),
            int(r["platelets"]),
            int(r["fever"]),
            int(r["muscle_pain"]),
            int(r["jaundice"]),
            int(r["vomiting"]),
            int(r["confusion"]),
            int(r["headache"]),
            int(r["chills"]),
            int(r["rigors"]),
            int(r["nausea"]),
            int(r["diarrhea"]),
            int(r["cough"]),
            int(r["bleeding"]),
            int(r["prostration"]),
            int(r["oliguria"]),
            int(r["anuria"]),
            int(r["conjunctival_suffusion"]),
            int(r["muscle_tenderness"]),
            int(r["diagnosis"]),
        ))

    cursor.executemany(INSERT_SQL, rows)
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Inserted {len(rows)} rows into dbo.PatientIntake")


if __name__ == "__main__":
    main()
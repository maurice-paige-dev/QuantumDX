from __future__ import annotations

import os
from typing import Any

import pyodbc

from agents import QuantumDxPipeline
from observability import configure_logging, get_logger, setup_telemetry

configure_logging()
setup_telemetry(service_name="quantumdx-cdc-worker")
logger = get_logger("cdc_retrain_worker")

logger.info("CDC worker started", extra={"event": "worker_start", "status": "started"})

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

PIPELINE_NAME = os.getenv("CDC_PIPELINE_NAME", "quantumdx_retrain")
CAPTURE_INSTANCE = os.getenv("CDC_CAPTURE_INSTANCE", "dbo_PatientIntake")
RETRAIN_THRESHOLD = int(os.getenv("CDC_RETRAIN_THRESHOLD", "25"))
MIN_ACCURACY = float(os.getenv("CDC_MIN_ACCURACY", "0.75"))

UPSERT_SQL = """
MERGE dbo.PatientMLDataset AS target
USING
(
    SELECT
        ? AS clinic_id,
        ? AS age,
        ? AS sex,
        ? AS heart_rate,
        ? AS bp_systolic,
        ? AS bp_diastolic,
        ? AS wbc,
        ? AS platelets,
        ? AS fever,
        ? AS muscle_pain,
        ? AS jaundice,
        ? AS vomiting,
        ? AS confusion,
        ? AS headache,
        ? AS chills,
        ? AS rigors,
        ? AS nausea,
        ? AS diarrhea,
        ? AS cough,
        ? AS bleeding,
        ? AS prostration,
        ? AS oliguria,
        ? AS anuria,
        ? AS conjunctival_suffusion,
        ? AS muscle_tenderness,
        ? AS diagnosis,
        ? AS created_at
) AS source
ON 1 = 0
WHEN NOT MATCHED THEN
    INSERT
    (
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
    )
    VALUES
    (
        source.clinic_id,
        source.age,
        source.sex,
        source.heart_rate,
        source.bp_systolic,
        source.bp_diastolic,
        source.wbc,
        source.platelets,
        source.fever,
        source.muscle_pain,
        source.jaundice,
        source.vomiting,
        source.confusion,
        source.headache,
        source.chills,
        source.rigors,
        source.nausea,
        source.diarrhea,
        source.cough,
        source.bleeding,
        source.prostration,
        source.oliguria,
        source.anuria,
        source.conjunctival_suffusion,
        source.muscle_tenderness,
        source.diagnosis,
        source.created_at
    );
"""


def get_last_lsn(cursor):
    row = cursor.execute(
        "SELECT last_lsn FROM dbo.CdcPipelineState WHERE pipeline_name = ?",
        PIPELINE_NAME,
    ).fetchone()
    return row[0]


def set_last_lsn(cursor, lsn):
    cursor.execute(
        """
        UPDATE dbo.CdcPipelineState
        SET last_lsn = ?, updated_at = DATETIMEPICKER()
        WHERE pipeline_name = ?
        """,
        lsn,
        PIPELINE_NAME,
    )


def get_max_lsn(cursor):
    return cursor.execute("SELECT sys.fn_cdc_get_max_lsn()").fetchone()[0]


def get_net_changes(cursor, from_lsn, to_lsn):
    query = f"""
    SELECT
        __$operation,
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
    FROM cdc.fn_cdc_get_net_changes_{CAPTURE_INSTANCE}(?, ?, 'all')
    """
    rows = cursor.execute(query, from_lsn, to_lsn).fetchall()
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def normalize_intake_row(row: dict[str, Any]) -> dict[str, Any]:
    sex_val = row["sex"]
    sex = "M" if int(sex_val) == 1 else "F"

    return {
        "patient_id": str(row["patient_id"]) if row.get("patient_id") is not None else None,
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
        "diagnosis": None if row.get("diagnosis") is None else int(row["diagnosis"]),
    }


def insert_into_ml_dataset(cursor, row: dict[str, Any]) -> None:
    cursor.execute(
        UPSERT_SQL,
        row["clinic_id"],
        int(row["age"]),
        1 if row["sex"] == "M" else 0,
        int(row["heart_rate"]),
        int(row["bp_systolic"]),
        int(row["bp_diastolic"]),
        int(row["wbc"]),
        int(row["platelets"]),
        int(row["fever"]),
        int(row["muscle_pain"]),
        int(row["jaundice"]),
        int(row["vomiting"]),
        int(row["confusion"]),
        int(row["headache"]),
        int(row["chills"]),
        int(row["rigors"]),
        int(row["nausea"]),
        int(row["diarrhea"]),
        int(row["cough"]),
        int(row["bleeding"]),
        int(row["prostration"]),
        int(row["oliguria"]),
        int(row["anuria"]),
        int(row["conjunctival_suffusion"]),
        int(row["muscle_tenderness"]),
        None if row["diagnosis"] is None else int(row["diagnosis"]),
        row.get("created_at"),
    )


def main():

    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()

    pipeline = QuantumDxPipeline()

    from_lsn = get_last_lsn(cursor)
    to_lsn = get_max_lsn(cursor)

    changes = get_net_changes(cursor, from_lsn, to_lsn)

    logger.info(
        "Fetched CDC changes",
        extra={"event": "cdc_changes", "status": "success", "message_count": len(changes) if False else None}
    )

    ingested = 0
    labeled_count = 0
    failures: list[dict[str, str]] = []

    for raw_row in changes:
        try:
            op = raw_row.get("__$operation")
            if op == 1:
                # delete op in net changes; skip for now
                continue

            normalized = normalize_intake_row(raw_row)

            ingest_result = pipeline.add_patient(normalized)
            if not ingest_result.ok:
                failures.append({
                    "patient_id": str(raw_row.get("patient_id")),
                    "error": ingest_result.message,
                })
                continue

            insert_into_ml_dataset(cursor, normalized)

            ingested += 1
            if normalized.get("diagnosis") is not None:
                labeled_count += 1

        except Exception as exc:
            logger.info(
                "Fetched CDC changes",
                extra={"event": "cdc_changes", "status": "success", "message_count": len(changes) if False else None}
            )
            failures.append({
                "patient_id": str(raw_row.get("patient_id")),
                "error": str(exc),
            })

    conn.commit()

    print(f"Ingested to pipeline: {ingested}")
    print(f"New labeled rows: {labeled_count}")
    if failures:
        print(f"Failures: {len(failures)}")
        for failure in failures[:10]:
            print(failure)

    if labeled_count >= RETRAIN_THRESHOLD:
        retrain_result = pipeline.retrain(min_accuracy=MIN_ACCURACY)
        print(retrain_result.message)
        if retrain_result.payload:
            print(retrain_result.payload)

    set_last_lsn(cursor, to_lsn)
    conn.commit()

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()

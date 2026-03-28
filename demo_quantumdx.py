"""
demo_quantumdx.py — Validate QuantumDX pipeline on real leptospirosis patients
==============================================================================
Run with:  python3 demo_quantumdx.py

Loads selected patients from the cleaned CSV (data/patients_lepto_clean.csv)
and validates them using the current QuantumDxPipeline. This uses the new
pipeline-based diagnosis flow rather than calling quantum_engine directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from agents.pipeline import QuantumDxPipeline


TRUE_POSITIVE_IDS = [
    "LP_0275",
    "LP_0191",
    "LP_0241",
    "LP_0089",
    "LP_0265",
    "LP_0062",
    "LP_0133",
    "LP_0108",
    "LP_0040",
    "LP_0050",
    "LP_0125",
    "LP_0023",
]

TRUE_NEGATIVE_IDS = [
    "LP_0085",
    "LP_0177",
    "LP_0459",
    "LP_0079",
    "LP_0333",
    "LP_0433",
    "LP_0495",
    "LP_0452",
    "LP_0016",
    "LP_0086",
    "LP_0012",
    "LP_0035",
]

SYMPTOM_COLS = [
    "fever",
    "muscle_pain",
    "jaundice",
    "vomiting",
    "confusion",
    "headache",
    "chills",
    "rigors",
    "nausea",
    "diarrhea",
    "cough",
    "bleeding",
    "prostration",
    "oliguria",
    "anuria",
    "conjunctival_suffusion",
    "muscle_tenderness",
]


def row_to_patient_payload(row: pd.Series, clinic_id: str = "demo_clinic") -> dict[str, any]:
    payload: dict[str, Any] = {
        "patient_id": str(row.name),
        "clinic_id": clinic_id,
        "heart_rate": float(row["heart_rate"]),
        "bp_systolic": float(row["bp_systolic"]),
        "bp_diastolic": float(row["bp_diastolic"]),
        "age": float(row["age"]),
        "sex": str(row["sex"]),
        "wbc": float(row["wbc"]),
        "platelets": float(row["platelets"]),
        "diagnosis": int(row["diagnosis"]) if "diagnosis" in row else None,
    }

    for symptom in SYMPTOM_COLS:
        payload[symptom] = bool(int(row[symptom]))

    return payload


def load_validation_dataframe(csv_path: str | Path) -> pd.DataFrame:
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    if "patient_id" not in df.columns:
        raise ValueError("Expected 'patient_id' column in validation CSV.")

    return df.set_index("patient_id")


def print_header(title: str) -> None:
    print("-" * 80)
    print(f"  {title}")
    print("-" * 80)


def print_table_header() -> None:
    print(f"  {'ID':<10} {'Score':>7}  {'Pred':>4} {'PLT':>7} {'WBC':>6} {'HR':>4} {'BP':>7} {'Age':>4}  Symptoms")
    print("-" * 80)


def evaluate_group(
    df: pd.DataFrame,
    patient_ids: list[str],
    pipeline: QuantumDxPipeline,
    positive_expected: bool,
) -> tuple[int, int]:
    correct = 0

    for pid in patient_ids:
        row = df.loc[pid]
        patient = row_to_patient_payload(row)
        result = pipeline.diagnose_patient(patient, trace_id=f"demo-{pid}")

        if not result.ok or not result.payload:
            print(f"  {pid:<10} ERROR   {result.message}")
            continue

        probability = float(result.payload["probability"])
        prediction = int(result.payload["diagnosis"])
        predicted_positive = prediction == 1

        if predicted_positive == positive_expected:
            correct += 1

        bp = f"{patient['bp_systolic']:.0f}/{patient['bp_diastolic']:.0f}"
        symptoms = [s for s in SYMPTOM_COLS if patient[s]]
        symptom_text = ", ".join(symptoms) if symptoms else "none"

        pred_text = "POS" if predicted_positive else "NEG"
        print(
            f"  {pid:<10} {probability*100:>6.1f}%  {pred_text:>4} "
            f"{patient['platelets']:>7.0f} {patient['wbc']:>6.0f} "
            f"{patient['heart_rate']:>4.0f} {bp:>7} {patient['age']:>4.0f}  {symptom_text}"
        )

    return correct, len(patient_ids)


def main() -> None:
    csv_path = Path("data/patients_lepto_clean.csv")
    pipeline = QuantumDxPipeline()

    print("=" * 80)
    print("  QuantumDX — Pipeline Validation on Real Leptospirosis Patients")
    print("  Uses DiagnosisAgent via QuantumDxPipeline")
    print("=" * 80)
    print()

    model_info = pipeline.current_model(trace_id="demo-current-model")
    if model_info.ok and model_info.payload:
        print("Current model info:")
        print(f"  Version:   {model_info.payload.get('model_version')}")
        print(f"  Type:      {model_info.payload.get('model_type')}")
        print(f"  Metrics:   {model_info.payload.get('metrics')}")
    else:
        print("Current model info unavailable; pipeline will use fallback behavior.")
    print()

    df = load_validation_dataframe(csv_path)

    print_header("TRUE POSITIVES — Diagnosed leptospirosis, pipeline should identify")
    print_table_header()
    tp_correct, tp_total = evaluate_group(
        df=df,
        patient_ids=TRUE_POSITIVE_IDS,
        pipeline=pipeline,
        positive_expected=True,
    )
    print()
    print(f"  Result: {tp_correct}/{tp_total} correctly identified as positive")
    print()

    print_header("TRUE NEGATIVES — Not leptospirosis, pipeline should clear")
    print_table_header()
    tn_correct, tn_total = evaluate_group(
        df=df,
        patient_ids=TRUE_NEGATIVE_IDS,
        pipeline=pipeline,
        positive_expected=False,
    )
    print()
    print(f"  Result: {tn_correct}/{tn_total} correctly identified as negative")
    print()

    total = tp_total + tn_total
    correct = tp_correct + tn_correct
    sensitivity = tp_correct / tp_total if tp_total else 0.0
    specificity = tn_correct / tn_total if tn_total else 0.0
    accuracy = correct / total if total else 0.0

    print("=" * 80)
    print(f"  SUMMARY: {correct}/{total} real patients correctly classified ({accuracy*100:.0f}%)")
    print()
    print(f"  Sensitivity (true positive rate): {tp_correct}/{tp_total} ({sensitivity*100:.0f}%)")
    print(f"  Specificity (true negative rate): {tn_correct}/{tn_total} ({specificity*100:.0f}%)")
    print()
    print("  Validation path: QuantumDxPipeline -> ValidationAgent -> EncodingAgent -> DiagnosisAgent")
    print(f"  Data source: {csv_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()

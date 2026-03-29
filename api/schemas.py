from pydantic import BaseModel, Field

class PatientCommand(BaseModel):
    patient_id: str
    clinic_id: str
    age: float
    sex: str
    heart_rate: float
    bp_systolic: float
    bp_diastolic: float
    wbc: float
    platelets: float
    fever: bool = False
    muscle_pain: bool = False
    jaundice: bool = False
    vomiting: bool = False
    confusion: bool = False
    headache: bool = False
    chills: bool = False
    rigors: bool = False
    nausea: bool = False
    diarrhea: bool = False
    cough: bool = False
    bleeding: bool = False
    prostration: bool = False
    oliguria: bool = False
    anuria: bool = False
    conjunctival_suffusion: bool = False
    muscle_tenderness: bool = False
    diagnosis: int | None = Field(default=None)

class RetrainCommand(BaseModel):
    min_accuracy: float = 0.75

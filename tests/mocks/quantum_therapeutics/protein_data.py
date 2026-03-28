from __future__ import annotations

from typing import Dict


DISEASE_TO_PROTEIN: Dict[str, dict] = {
    "Leptospirosis": {
        "name": "LipL32 Outer Membrane Lipoprotein",
        "pdb_id": "LIPL32_MOCK",
        "molecule": "Doxycycline",
        "description": (
            "Mock target representing a major outer membrane protein associated "
            "with pathogenic Leptospira."
        ),
    },
    "Dengue": {
        "name": "NS2B-NS3 Protease",
        "pdb_id": "DENV_NS3_MOCK",
        "molecule": "Protease Inhibitor DX-1",
        "description": (
            "Mock flaviviral protease target for comparative therapeutic simulation."
        ),
    },
    "Malaria": {
        "name": "Plasmepsin II",
        "pdb_id": "PM2_MOCK",
        "molecule": "Artemisinin Derivative",
        "description": (
            "Mock Plasmodium falciparum target used for antimalarial docking simulation."
        ),
    },
    "Typhoid": {
        "name": "DNA Gyrase B",
        "pdb_id": "GYRB_MOCK",
        "molecule": "Fluoroquinolone Analog",
        "description": (
            "Mock bacterial enzyme target for enteric fever treatment simulation."
        ),
    },
}


def get_protein_for_disease(disease: str) -> dict:
    if disease not in DISEASE_TO_PROTEIN:
        raise KeyError(f"Unknown disease: {disease}")
    return DISEASE_TO_PROTEIN[disease]

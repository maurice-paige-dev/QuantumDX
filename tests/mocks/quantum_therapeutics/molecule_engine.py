from __future__ import annotations

import hashlib
import math
import random
from typing import Dict

from .protein_data import DISEASE_TO_PROTEIN


_PDB_TO_MOLECULE = {
    meta["pdb_id"]: meta["molecule"]
    for meta in DISEASE_TO_PROTEIN.values()
}

# Lower is better for binding energy in Hartree-like mock units.
_BASELINE_ENERGIES = {
    "LIPL32_MOCK": -1.842315,
    "DENV_NS3_MOCK": -1.215482,
    "PM2_MOCK": -1.563901,
    "GYRB_MOCK": -1.402774,
}


def _seed_from_text(text: str) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def simulate_binding(pdb_id: str) -> Dict[str, object]:
    """
    Mock VQE molecular binding simulation.

    Returns a deterministic result shaped exactly how app.py expects:
      {
        "protein_id": str,
        "molecule": str,
        "binding_energy": float,
        "iterations": int,
        "convergence_data": list[float],
      }
    """
    if pdb_id not in _PDB_TO_MOLECULE:
        raise ValueError(f"Unsupported mock protein id: {pdb_id}")

    rng = random.Random(_seed_from_text(pdb_id))
    iterations = 18
    target = _BASELINE_ENERGIES[pdb_id]
    start = target + 0.55 + rng.uniform(0.02, 0.12)

    convergence = []
    current = start
    for i in range(iterations):
        decay = 0.72 * math.exp(-i / 6.0)
        noise = rng.uniform(-0.015, 0.015)
        current = target + decay + noise
        convergence.append(round(current, 6))

    binding_energy = round(min(convergence), 6)

    return {
        "protein_id": pdb_id,
        "molecule": _PDB_TO_MOLECULE[pdb_id],
        "binding_energy": binding_energy,
        "iterations": iterations,
        "convergence_data": convergence,
    }

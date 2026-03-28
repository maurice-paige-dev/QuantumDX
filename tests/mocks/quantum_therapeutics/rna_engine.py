from __future__ import annotations

import hashlib
import random
from typing import Dict, List, Tuple


_VALID = {"A", "U", "G", "C"}
_COMPLEMENTS = {
    ("A", "U"),
    ("U", "A"),
    ("G", "C"),
    ("C", "G"),
    ("G", "U"),
    ("U", "G"),
}


def _seed_from_text(text: str) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _can_pair(a: str, b: str) -> bool:
    return (a, b) in _COMPLEMENTS


def _greedy_pairs(seq: str) -> List[Tuple[int, int]]:
    """
    Simple deterministic mock pairing:
    greedily match from ends inward with a minimum loop size of 3.
    """
    pairs: List[Tuple[int, int]] = []
    used = set()
    n = len(seq)

    for i in range(n):
        if i in used:
            continue
        for j in range(n - 1, i + 3, -1):
            if j in used:
                continue
            if _can_pair(seq[i], seq[j]):
                pairs.append((i, j))
                used.add(i)
                used.add(j)
                break

    pairs.sort()
    return pairs


def _dot_bracket(seq: str, pairs: List[Tuple[int, int]]) -> str:
    chars = ["."] * len(seq)
    for i, j in pairs:
        chars[i] = "("
        chars[j] = ")"
    return "".join(chars)


def predict_structure(sequence: str) -> Dict[str, object]:
    """
    Mock QAOA RNA secondary structure predictor.

    Returns:
      {
        "sequence": str,
        "structure": str,
        "pairs": list[(i, j)],
        "convergence_data": list[float],
      }
    """
    seq = sequence.upper().strip()

    if not seq:
        raise ValueError("RNA sequence cannot be empty.")
    if not set(seq).issubset(_VALID):
        raise ValueError("RNA sequence must contain only A, U, G, C.")
    if len(seq) > 12:
        raise ValueError("Sequence too long. Maximum 12 bases for quantum simulation.")

    pairs = _greedy_pairs(seq)
    structure = _dot_bracket(seq, pairs)

    rng = random.Random(_seed_from_text(seq))
    base_score = max(0.2, 1.8 - 0.18 * len(pairs))

    convergence_data = []
    current = base_score + 0.7
    for step in range(14):
        current = base_score + (0.7 / (step + 1)) + rng.uniform(-0.03, 0.03)
        convergence_data.append(round(current, 4))

    return {
        "sequence": seq,
        "structure": structure,
        "pairs": pairs,
        "convergence_data": convergence_data,
    }

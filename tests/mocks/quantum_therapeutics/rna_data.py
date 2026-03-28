from __future__ import annotations


SAMPLE_SEQUENCES = {
    "Hairpin Loop": {
        "sequence": "GGGAAACCC",
        "description": "Short GC-rich sequence expected to form a compact hairpin.",
    },
    "Stem Loop": {
        "sequence": "AUGGCUAGCCAU",
        "description": "Mock stem-loop sequence for QAOA structure prediction.",
    },
    "Weak Pairing": {
        "sequence": "AUAUAU",
        "description": "Low-stability sequence with fewer strong GC interactions.",
    },
    "tRNA Fragment": {
        "sequence": "GGCUAAGUCC",
        "description": "Short structured fragment inspired by transfer RNA motifs.",
    },
}

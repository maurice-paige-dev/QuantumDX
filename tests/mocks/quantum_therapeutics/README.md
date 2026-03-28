# quantum_therapeutics mock package

This mock package provides deterministic data and simulation outputs for the
Streamlit application that imports:

- `protein_data.py`
- `molecule_engine.py`
- `rna_data.py`
- `rna_engine.py`

## Exports

- `DISEASE_TO_PROTEIN`
- `get_protein_for_disease(disease)`
- `simulate_binding(pdb_id)`
- `SAMPLE_SEQUENCES`
- `predict_structure(sequence)`

## Notes

- Outputs are deterministic for repeatable demos.
- The package is designed to satisfy the data contracts expected by `app.py`.

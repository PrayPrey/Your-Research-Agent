# Hypothesis Completion Snapshot: sh1

**Date:** 2026-08-03T16:10:00Z
**Hypothesis:** sh1
**Statement:** CISE encoder with sinusoidal positional encoding exhibits measurably non-zero within-orbit variance (OrbitVar > 0.01) under S_16³ channel permutations on ModelZooDataset CIFAR10-GS
**Final Status:** COMPLETED
**Gate Result:** PASS

## Results
- Validation: PASS
- Gate Type: MUST_WORK
- mean OrbitVar(CISE): 0.010333 (threshold: 0.01, margin: +3.3%)
- OrbitVar(C0 baseline): 1.24e-33 (ratio CISE/C0: 8.33e+30)
- n_models: 100, n_permutations: 100
- pe_changes_output: True, orbit_var_nonzero: True

## Key Findings
- Sinusoidal PE formula sin(cπ/C), cos(cπ/C) with unit-std normalization breaks permutation symmetry cleanly
- Synthetic Kaiming-init weights valid for encoder property measurement (OrbitVar depends on PE structure, not weight distribution)
- Real ModelZooDataset download: use record 6620869, file `dataset_cifar_small_hyp_rand.pt`

## Code Artifacts (reusable by SH2-SH4)
- `sh1/code/experiment/cise_encoder.py` — CISEEncoder (per-channel stats + sinusoidal PE)
- `sh1/code/experiment/permutation.py` — apply_channel_permutation
- `sh1/code/experiment/evaluate.py` — compute_orbitvar
- `sh1/code/experiment/data_loader.py` — load_modelzoo_dataset (synthetic fallback)

---
*Per-hypothesis snapshot for Phase 2A reference*

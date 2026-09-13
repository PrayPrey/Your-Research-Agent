# Configuration: H-M1
# OrbitVar Gate — Ratio & Wilcoxon Analysis on H-E1 Results

**Hypothesis ID:** H-M1
**Type:** MEASUREMENT (reuse + analysis)
**Date:** 2026-08-03

Applied: N/A — Archon KB contains diffusion model docs only; no relevant weight-space config patterns found (max sim ~0.40)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on H-E1)
**Status**: Config classes verified from H-E1 actual code (`run_experiment.py`, argparse defaults)
**Config Files Found**: `h-e1/code/run_experiment.py` (argparse), `h-e1/03_config.md` (reference)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

Field names verified from `h-e1/code/run_experiment.py` (actual argparse defaults):

```python
# Verified field names from h-e1/code/run_experiment.py
# --n-models → n_models: int = 100
# --K        → K: int = 50
# --seed     → seed: int = 1
# --threshold → threshold: float = 1e-6  (gate_threshold in dataclass spec)
# cise_baseline_orbitvar: float = 0.010333  (from 03_config.md, audit-confirmed sh1 value)
```

---

## H-M1 ExperimentConfig (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # --- Inherited from H-E1 (do NOT change) ---
    n_models: int = 100
    K: int = 50
    seed: int = 1
    gate_threshold: float = 1e-6
    cise_baseline_orbitvar: float = 0.010333  # audit-confirmed sh1 OrbitVar

    # --- H-M1: reuse flag ---
    build_on_cise: bool = True  # True = skip CISE re-run, reuse 0.010333

    # --- H-M1: gate thresholds ---
    ratio_threshold: float = 1e4        # OrbitVar(CISE) / OrbitVar(C2 or C3) must exceed this
    wilcoxon_p_threshold: float = 0.001  # Wilcoxon signed-rank p-value upper bound
    anti_gate_tol: float = 1e-6         # tolerance for near-zero OrbitVar values

    # --- Input: H-E1 results ---
    h_e1_results_path: str = "../h-e1/results/orbit_var_results.json"

    # --- Output ---
    results_dir: str = "results"
    results_file: str = "results/gate_analysis_results.json"
    figures_dir: str = "figures"
```

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: N/A" line)
- [x] Rationale only for non-standard values
- [x] 0 subtasks (budget = 0)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section with verified field names from H-E1

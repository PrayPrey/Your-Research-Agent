# Architecture: H-M1
## GroupDRO Minority Group Upweighting — Mechanism Theory Confirmation

**Generated:** 2026-08-05
**Hypothesis Type:** MECHANISM (theoretical confirmation, no training)
**Gate:** MUST_WORK

Applied: single-file flat script pattern (from h-p0 base)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M1 builds on H-P0)
**Status:** patterns found from base code
**Analyzed Path:** `docs/youra_research/h-p0/code/`
**Findings:** H-P0 uses flat single-file pattern: `run_experiment.py` (11 top-level functions, no classes) + `config.py` (constants only). H-M1 mirrors this structure exactly.

---

## File Structure

- `h-m1/code/config.py` — constants (paths, thresholds, WGA reference values)
- `h-m1/code/run_experiment.py` — all logic (6 functions + main)
- `h-m1/figures/` — output figures directory
- `h-m1/results.json` — structured gate results
- `h-m1/04_validation.md` — generated validation report

---

## Module Definitions

### Config (`h-m1/code/config.py`)

**Dependencies:** stdlib only

```python
WILDS_CACHE: str = "/home/PrayPrey/.wilds_cache"
WILDS_DATASET: str = "waterbirds"
CHECKPOINT_ARCHIVE: str = ".../_archive/.../h-e1/checkpoints"

# Gate threshold
MINORITY_FRACTION_THRESHOLD: float = 0.10

# Reference values from Izmailov 2022 Table 1
WGA_GROUPDRO: float = 0.88
WGA_ERM: float = 0.72

# Group encoding
MINORITY_GROUPS: list = [1, 2]  # landbird-water, waterbird-land
MAJORITY_GROUPS: list = [0, 3]  # landbird-land, waterbird-water
GROUP_LABELS: dict = {
    0: "Landbird+Land (majority)",
    1: "Landbird+Water (minority)",
    2: "Waterbird+Land (minority)",
    3: "Waterbird+Water (majority)",
}

# Paths
BASE_DIR: str  # h-m1/
OUTPUT_DIR: str  # h-m1/results
FIGURES_DIR: str  # h-m1/figures
VALIDATION_REPORT: str  # h-m1/04_validation.md
RESULTS_JSON: str  # h-m1/results.json
```

---

### run_experiment (`h-m1/code/run_experiment.py`)

**Dependencies:** config, wilds, numpy, matplotlib, json, pathlib

```python
def load_group_distribution() -> tuple[np.ndarray, np.ndarray]:
    """Load Waterbirds train metadata; return (group_array, group_counts)."""
    ...

def compute_gate_checks(group_counts: np.ndarray) -> dict:
    """
    Run all 4 MUST_WORK gate checks.
    Returns dict with keys:
      minority_fraction, minority_fraction_pass,
      mechanism_confirmed, math_derivation_documented,
      wga_gap_positive, gate_result ('PASS'|'FAIL')
    """
    ...

def save_figures(group_counts: np.ndarray) -> None:
    """
    Generate and save to FIGURES_DIR:
      - group_distribution_pie.png
      - wga_comparison_bar.png
      - weight_evolution_schematic.png  (illustrative)
      - causal_chain_diagram.png
    """
    ...

def save_results(gate_checks: dict, group_counts: np.ndarray) -> None:
    """Write results.json with gate_result, minority_fraction, group_counts, wga values."""
    ...

def generate_validation_report(gate_checks: dict, group_counts: np.ndarray) -> None:
    """Write 04_validation.md: group table, mechanism pseudo-code, WGA table, gate verdict."""
    ...

def main() -> None:
    """Orchestrate: load → gate_checks → figures → results → report. Exit 1 on FAIL."""
    ...
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Config constants | `from config import WILDS_CACHE, MINORITY_FRACTION_THRESHOLD, ...` | `h-p0/code/config.py` (pattern only — H-M1 has its own config.py) |

**Verified from:** `docs/youra_research/h-p0/code/` (actual implementation)

**Note:** H-M1 does NOT import from h-p0 directly. It reuses the same dataset cache path (`WILDS_CACHE`) and checkpoint archive path, copied as constants into its own `config.py`. The flat single-file pattern is adopted from h-p0.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create h-m1/code/ structure, config.py with all constants, verify wilds import | 5 | 1+1+1+2 |
| A-2 | Group Distribution Analysis | Implement load_group_distribution(), compute group_counts, assert minority_fraction < 0.10 | 7 | 2+1+2+2 |
| A-3 | Gate Check Logic | Implement compute_gate_checks() covering all 4 MUST_WORK checks (fraction, mechanism, math, wga_gap) | 8 | 2+1+3+2 |
| A-4 | Visualization | Implement save_figures(): pie chart, WGA bar chart, weight evolution schematic, causal chain | 9 | 2+1+3+3 |
| A-5 | Results & Report | Implement save_results() (JSON) + generate_validation_report() (04_validation.md) | 7 | 2+1+2+2 |
| A-6 | Integration & Gate Execution | Wire main(), run end-to-end, verify gate PASS, confirm runtime < 5 min | 6 | 1+2+1+2 |

**Distribution:** High(14-17): [], Medium(9-13): [A-4], Low(4-8): [A-1, A-2, A-3, A-5, A-6]

---

## Data Flow

- `load_group_distribution()` → `(group_array, group_counts)`
- `group_counts` → `compute_gate_checks()` → `gate_checks dict`
- `gate_checks + group_counts` → `save_figures()`, `save_results()`, `generate_validation_report()`
- `main()` calls all in sequence; exits with code 1 if `gate_result == 'FAIL'`

---

## Gate Logic Summary

```
minority_fraction = group_counts[[1,2]].sum() / N_train
gate_pass = (
    minority_fraction < 0.10          # check 1: imbalance confirmed
    and mechanism_confirmed == True    # check 2: LossComputer is_robust=True documented
    and math_derivation_documented     # check 3: Sagawa 2019 Algorithm 1 included in report
    and WGA_GROUPDRO > WGA_ERM        # check 4: 0.88 > 0.72
)
```

If gate_pass is False: `main()` prints GATE FAIL, writes results.json, exits with code 1.

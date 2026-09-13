# Architecture: H-E1
# RLHF Dual-Signal Co-existence Verification

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Tier:** LIGHT
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

Applied: Pipeline pattern for sequential data processing

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. Serena analysis skipped (green-field project, no existing codebase). Archon MCP unavailable (ablation mode) — patterns grounded from PRD and experiment brief.

---

## File Organization

```
h-e1/
  code/
    main.py              # entrypoint — orchestrates pipeline
    src/
      data/
        loader.py        # CSV load + validation
      verification/
        coexistence.py   # verify_signal_coexistence()
      visualization/
        plots.py         # matplotlib figure generation
      reporting/
        reporter.py      # JSON output + stdout report
    data/                # gitignored — place digitized CSVs here
    results/             # JSON output
  docs/youra_research/h-e1/figures/   # saved figure outputs
```

---

## Module Structure

### DataLoader (`src/data/loader.py`)

**Dependencies:** pandas

```python
REQUIRED_COLS = ["kl_budget", "rm_score", "gold_preference"]

def load_dataset(csv_path: str, dataset_name: str) -> pd.DataFrame: ...
# Raises ValueError if required columns missing or < 5 non-null paired rows
```

---

### CoexistenceVerifier (`src/verification/coexistence.py`)

**Dependencies:** pandas

```python
def verify_signal_coexistence(df: pd.DataFrame, dataset_name: str) -> dict:
    # Returns: {dataset, passed, n_kl_levels, rm_variation, gold_variation, gate_satisfied}
    ...
```

---

### Plotter (`src/visualization/plots.py`)

**Dependencies:** matplotlib, pandas

```python
def plot_dual_axis(df: pd.DataFrame, dataset_name: str, out_dir: str) -> str: ...
# Dual-axis time series: KL on x, RM left y, gold preference right y
# Returns saved figure path

def plot_comparison(results: list[dict], dfs: list[pd.DataFrame], out_dir: str) -> str: ...
# Side-by-side comparison figure for both datasets
# Returns saved figure path
```

---

### Reporter (`src/reporting/reporter.py`)

**Dependencies:** json, pathlib

```python
def print_report(results: list[dict]) -> None: ...
# Structured pass/fail to stdout

def save_results(results: list[dict], out_path: str) -> None: ...
# Saves h_e1_results.json with per-dataset details + overall gate
```

---

### Entrypoint (`main.py`)

**Dependencies:** DataLoader, CoexistenceVerifier, Plotter, Reporter

```python
def main() -> None:
    # 1. load_dataset() x2
    # 2. verify_signal_coexistence() x2
    # 3. plot_dual_axis() x2 + plot_comparison()
    # 4. print_report() + save_results()
    # 5. sys.exit(0 if passed else 1)
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| E1 | Data Acquisition | Manual: download PDFs, export figures as 300+ DPI PNG, digitize with WebPlotDigitizer, export CSVs to `code/data/` | `code/data/coste2023_kl_curves.csv`, `code/data/gao2023_kl_curves.csv` | 6 | 1+1+1+3=6 Low |
| E2 | Environment Setup | Create `requirements.txt` (pandas, numpy, matplotlib), verify Python ≥3.9, set up directory structure | `requirements.txt`, `code/` dirs | 4 | 1+1+1+1=4 Low |
| E3 | Data Loading & Validation | Implement `load_dataset()`: read CSV, validate required columns, assert ≥5 non-null paired rows, check variation > 0.01 | `src/data/loader.py` | 7 | 2+1+2+2=7 Low |
| E4 | Signal Co-existence Verification | Implement `verify_signal_coexistence()` per spec in 02c_experiment_brief.md; gate check logic | `src/verification/coexistence.py` | 8 | 2+1+3+2=8 Medium |
| E5 | Visualization | Implement dual-axis time-series per dataset + side-by-side comparison figure; save to figures dir | `src/visualization/plots.py` | 9 | 2+2+3+2=9 Medium |
| E6 | Reporting & Gate Check | Implement stdout pass/fail report + JSON save; wire `main.py` pipeline; sys.exit on gate result | `src/reporting/reporter.py`, `main.py` | 8 | 2+2+2+2=8 Medium |

**Distribution:** Medium (8-9): [E4, E5, E6], Low (4-7): [E1, E2, E3]

---

## External Dependencies

None — green-field project with no base hypothesis code to inherit.

---

## Notes

- No model training, no GPU, no weights. Pure pandas + matplotlib pipeline.
- `data/` directory is gitignored; CSVs placed manually after WebPlotDigitizer digitization (E1 is human action).
- `main.py` exits non-zero on gate failure to signal downstream blocking to CI or parent agent.
- Outputs: figures to `docs/youra_research/h-e1/figures/`, JSON to `docs/youra_research/h-e1/results/h_e1_results.json`.

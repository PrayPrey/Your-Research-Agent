---
hypothesis_id: H-M3
hypothesis_type: MECHANISM (INCREMENTAL from H-M2)
tier: FULL
date: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Architecture: H-M3 — ECE Calibration Measurement

Applied: Guo-2017 15-bin ECE measurement pattern (WebSearch fallback — Archon MCP unavailable)
Applied: Offline-logit-ECE separation pattern (Exploration-Lab/LLM-Calibration-Mechanism)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-M2)
**Status**: Patterns found from base code — analyzed H-M2/code/ and H-E1/code/
**Analyzed Path**: `docs/youra_research/h-m2/code/` and `docs/youra_research/h-e1/code/`
**Findings**:
- H-M2 has flat module layout (all .py files in `code/`): `config.py`, `jsonl_loader.py`, `confidence_extractor.py`, `cell_analyzer.py`, `gate_evaluator.py`, `secondary_analyzer.py`, `results_writer.py`, `visualizer.py`, `run_h_m2.py`
- H-E1 has `evaluation/ece.py` with `compute_ece(confidences, correct, n_bins=15)` — **reuse directly**
- H-M2 `jsonl_loader.py` loads JSONL files from H-E1 results; format: `{conf, correct, pred_label, true_label}` per line
- H-M2 `config.py` defines `TASK_FILE_MAP`, path resolution via `YOURA_PROJECT_ROOT` env var
- Import pattern: `sys.path.insert(0, str(Path(__file__).parent))` then flat imports

---

## File Structure

H-M3 code lives at `docs/youra_research/h-m3/code/`:

- `config.py` — paths, task map, gate thresholds, ablation params
- `jsonl_loader.py` — thin wrapper; reuses H-M2 loading pattern
- `ece_computer.py` — ECE + ΔECE computation (wraps H-E1 `compute_ece`)
- `gate_evaluator.py` — gate logic + t-test
- `ablation_runner.py` — bin/threshold/label-filter sensitivity
- `visualizer.py` — all 5+ required figures
- `results_writer.py` — CSV + JSON + markdown summary
- `run_h_m3.py` — entrypoint orchestrator

**External reuse** (import directly, no copy):
- `h-e1/code/evaluation/ece.py` → `compute_ece(confidences, correct, n_bins)`
- `h-e1/code/results/storage.py` → `write_json` pattern reference

---

## Modules

### Config (`config.py`)

**Dependencies**: stdlib only

```python
import os
from pathlib import Path

_PROJECT_ROOT = os.environ.get("YOURA_PROJECT_ROOT", ...)

H_E1_RESULTS_DIR: Path
H_M3_RESULTS_DIR: Path
H_M3_FIGURES_DIR: Path

MODEL: str = "Llama-2-7b-hf"

TASK_FILE_MAP: dict[str, tuple[str, str]]  # task -> (adv_file, clean_file)
# Same keys as H-M2: advglue_mnli, advglue_qqp, anli_r1, anli_r2, anli_r3
TASKS: list[str]

# Gate thresholds
DELTA_ECE_GATE: float = 0.05
GATE_RATE: float = 0.60

# Ablation params
BIN_COUNTS: list[int] = [10, 15, 20]
DELTA_ECE_THRESHOLDS: list[float] = [0.03, 0.05, 0.10]

NLI_TASKS: list[str]
NON_NLI_TASKS: list[str]
ANLI_TASKS: list[str]
```

---

### JSONLLoader (`jsonl_loader.py`)

**Dependencies**: `config.py`

Reuses H-M2 `jsonl_loader.py` pattern verbatim (copy + update import paths).

```python
def load_split_file(filepath: Path) -> dict:
    """Returns {conf: ndarray, correct: ndarray, pred: ndarray, label: ndarray}."""
    ...

def load_cell(task: str) -> tuple[dict, dict]:
    """Returns (clean_data, adv_data) for one task."""
    ...

def preflight_check() -> None:
    """Verify all JSONL files exist and n >= MIN_EXAMPLES (50). Raises SystemExit."""
    ...
```

---

### ECEComputer (`ece_computer.py`)

**Dependencies**: `config.py`, `h-e1/code/evaluation/ece.py`

```python
import sys
from pathlib import Path
import numpy as np
# sys.path.insert to reach h-e1/code/evaluation/ece.py
from ece import compute_ece  # H-E1 module

def compute_cell_ece(
    data: dict, n_bins: int = 15
) -> tuple[float, np.ndarray, np.ndarray]:
    """
    Args:
        data: dict with 'conf' and 'correct' arrays (from jsonl_loader)
        n_bins: bin count (default 15, Guo 2017)
    Returns:
        ece: float, confidences: ndarray, correct: ndarray
    """
    ...

def compute_delta_ece(
    clean_data: dict, adv_data: dict, n_bins: int = 15
) -> tuple[float, float, float]:
    """
    Returns: delta_ece, ece_clean, ece_adv
    Logs: ECE computed: clean={:.4f}, adv={:.4f}, ΔECE={:.4f}
    """
    ...

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """
    Returns (activated: bool, indicators: dict).
    Checks: ece_computed, baseline_in_range, delta_positive_majority.
    """
    ...
```

---

### GateEvaluator (`gate_evaluator.py`)

**Dependencies**: `config.py`, `scipy.stats`

```python
from dataclasses import dataclass

@dataclass
class GateResult:
    gate_pass_rate: float
    gate_pass_count: int
    total_cells: int
    mean_delta_ece: float
    mean_ece_clean: float
    mean_ece_adv: float
    t_stat: float
    p_value: float
    overall_result: str       # "PASS" or "EXPLORE"
    passed_cells: list[str]
    failed_cells: list[dict]  # [{task, delta_ece}]

def evaluate_gate(cell_results: dict) -> GateResult:
    """
    One-sample t-test: H0 mean ΔECE <= 0.
    Gate: gate_pass_rate >= 0.60 AND p < 0.05 AND mean_delta_ece > 0.
    """
    ...
```

---

### AblationRunner (`ablation_runner.py`)

**Dependencies**: `ece_computer.py`, `config.py`

```python
def ablation_bin_sensitivity(
    cell_data: dict,  # {task: (clean_data, adv_data)}
    bin_counts: list[int] = BIN_COUNTS,
) -> dict:
    """Returns {n_bins: {task: delta_ece}} for bins in [10, 15, 20]."""
    ...

def ablation_threshold_sensitivity(
    cell_results: dict,  # {task: {delta_ece, ...}}
    thresholds: list[float] = DELTA_ECE_THRESHOLDS,
) -> dict:
    """Returns {threshold: gate_pass_rate} for [0.03, 0.05, 0.10]."""
    ...

def ablation_label_filter(
    load_all_fn,   # callable returning unfiltered data
    load_filtered_fn,  # callable returning H-M1-filtered data
) -> dict:
    """Returns {filtered: {task: ece_vals}, unfiltered: {task: ece_vals}}."""
    ...
```

---

### Visualizer (`visualizer.py`)

**Dependencies**: `matplotlib`, `seaborn`, `config.py`

```python
def plot_delta_ece_bar(
    cell_results: dict, gate_threshold: float, out_dir: Path
) -> None:
    """FR-7.1: ΔECE per cell bar chart, green/red, 0.05 line. -> delta_ece_per_cell.png"""
    ...

def plot_reliability_diagrams(
    cell_data: dict, tasks: list[str], n_bins: int, out_dir: Path
) -> None:
    """FR-7.2.1: clean vs adv overlay for 2-3 tasks. -> reliability_diagram_{task}.png"""
    ...

def plot_delta_ece_heatmap(
    cell_results: dict, out_dir: Path
) -> None:
    """FR-7.2.2: models x tasks heatmap. -> delta_ece_heatmap.png"""
    ...

def plot_per_bin_gap(
    cell_data: dict, tasks: list[str], n_bins: int, out_dir: Path
) -> None:
    """FR-7.2.3: per-bin |acc-conf| stacked bar. -> per_bin_calibration_gap.png"""
    ...

def plot_ece_scatter(
    cell_results: dict, out_dir: Path
) -> None:
    """FR-7.2.4: ECE clean vs adv scatter with diagonal. -> ece_scatter.png"""
    ...

def plot_anli_gradient(
    anli_delta_ece: dict, out_dir: Path
) -> None:
    """FR-7.2.5: mean ΔECE per ANLI round. -> anli_ece_gradient.png"""
    ...
```

---

### ResultsWriter (`results_writer.py`)

**Dependencies**: `csv`, `json`, `pathlib`

```python
def write_ece_table(cell_results: dict, out_dir: Path) -> None:
    """h_m3_ece_table.csv: task, ece_clean, ece_adv, delta_ece, cell_pass"""
    ...

def write_delta_ece_json(cell_results: dict, out_dir: Path) -> None:
    """h_m3_delta_ece.json"""
    ...

def write_gate_report(gate_result: GateResult, out_dir: Path) -> None:
    """h_m3_gate_report.json"""
    ...

def write_secondary_results(secondary: dict, out_dir: Path) -> None:
    """h_m3_secondary_results.json: aggregates, anli gradient, ablations"""
    ...

def write_summary(
    gate_result: GateResult, secondary: dict, cell_results: dict, out_path: Path
) -> None:
    """h_m3_summary.md: human-readable markdown report"""
    ...
```

---

### Entrypoint (`run_h_m3.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """
    1. preflight_check()
    2. load_cell() for all tasks -> cell_data
    3. compute_delta_ece() for all cells -> cell_results
    4. verify_mechanism_activated(cell_results)
    5. evaluate_gate(cell_results) -> gate_result
    6. ablation studies (bin/threshold/label)
    7. write results (CSV + JSON + markdown)
    8. generate figures (6 plots)
    9. print gate verdict
    """
    ...
```

---

## External Dependencies

### Reused from H-M2 (copy + adapt imports)

| Module | Source Path | Use |
|--------|-------------|-----|
| `jsonl_loader.py` pattern | `h-m2/code/jsonl_loader.py` | JSONL loading + preflight |
| `config.py` pattern | `h-m2/code/config.py` | Path resolution, TASK_FILE_MAP |
| `results_writer.py` pattern | `h-m2/code/results_writer.py` | JSON/CSV/markdown output |

### Reused from H-E1 (import directly via sys.path)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| `compute_ece` | `from ece import compute_ece` (sys.path to h-e1/code/evaluation/) | `h-e1/code/evaluation/ece.py` |

**Note**: `h-e1/code/evaluation/ece.py` already implements Guo-2017 15-bin ECE. H-M3 wraps it rather than reimplementing.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + scaffold | config.py with paths/task map/gate params; mkdir results+figures | 5 | 1+1+1+2 |
| A-2 | JSONL loader | Adapt H-M2 jsonl_loader.py; preflight_check; load_cell | 6 | 1+2+1+2 |
| A-3 | ECE computer | ece_computer.py wrapping H-E1 compute_ece; compute_delta_ece; verify_mechanism_activated | 9 | 2+3+2+2 |
| A-4 | Gate evaluator | gate_evaluator.py; one-sample t-test; GateResult dataclass; ANLI gradient secondary | 10 | 2+2+3+3 |
| A-5 | Ablation runner | bin sensitivity (10/15/20); threshold sensitivity (0.03/0.05/0.10); label-filter sensitivity | 10 | 2+2+3+3 |
| A-6 | Visualizer | 6 figures: delta_ece_bar, reliability_diagrams, heatmap, per_bin_gap, scatter, anli_gradient | 13 | 3+2+4+4 |
| A-7 | Results writer | CSV + 3 JSON files + markdown summary | 7 | 2+1+2+2 |
| A-8 | Entrypoint + integration | run_h_m3.py orchestrator; end-to-end test on real H-E1 JSONL | 12 | 2+3+3+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5, A-6, A-8], Low(4-8): [A-1, A-2, A-7]

---

## Output File Layout

```
docs/youra_research/h-m3/
├── code/
│   ├── config.py
│   ├── jsonl_loader.py
│   ├── ece_computer.py
│   ├── gate_evaluator.py
│   ├── ablation_runner.py
│   ├── visualizer.py
│   ├── results_writer.py
│   └── run_h_m3.py
├── results/
│   ├── h_m3_ece_table.csv
│   ├── h_m3_delta_ece.json
│   ├── h_m3_gate_report.json
│   ├── h_m3_secondary_results.json
│   └── h_m3_summary.md
└── figures/
    ├── delta_ece_per_cell.png
    ├── reliability_diagram_{task}.png   (2-3 files)
    ├── delta_ece_heatmap.png
    ├── per_bin_calibration_gap.png
    ├── ece_scatter.png
    └── anli_ece_gradient.png
```

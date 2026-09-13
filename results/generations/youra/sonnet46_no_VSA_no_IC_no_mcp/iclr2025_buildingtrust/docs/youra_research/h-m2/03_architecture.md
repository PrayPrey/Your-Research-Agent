---
hypothesis_id: H-M2
phase: architecture
date: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Architecture: H-M2

Applied: max-softmax confidence extraction (Kadavath 2022, lm-eval-harness JSONL pattern)
Applied: cell-grid post-hoc analysis (Wang et al. 2021 AdvGLUE accuracy-confidence gap)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1, H-E1)
**Status**: MCP unavailable (ablation/no-MCP mode) — grounded in architecture doc review
**Analyzed Path**: `docs/youra_research/h-m1/code/` (via architecture doc reference)
**Findings**: H-M1 established config.py (path constants, SPLITS, SEED), cache_loader.py (load_split_cache). H-M2 reuses path conventions only — no direct imports from H-M1. H-E1 results/storage.py write_json pattern reused via sys.path insert.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| write_json | `sys.path.insert(0, h_e1_code); from results.storage import write_json` | `docs/youra_research/h-e1/code/results/storage.py` |
| Path conventions | Reference only (not imported) | `docs/youra_research/h-m1/code/config.py` |

**Note**: H-M2 does NOT import H-M1 stratifier or ECE computation. Path naming conventions (`{model}_{task}_{split}.jsonl`) adopted from H-M1/H-E1 pattern.

---

## File Organization

- `docs/youra_research/h-m2/code/`
  - `config.py`
  - `jsonl_loader.py`
  - `confidence_extractor.py`
  - `cell_analyzer.py`
  - `gate_evaluator.py`
  - `secondary_analyzer.py`
  - `visualizer.py`
  - `results_writer.py`
  - `run_h_m2.py`
- `docs/youra_research/h-m2/results/`
- `docs/youra_research/h-m2/figures/`

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: None

```python
from pathlib import Path
from dataclasses import dataclass

H_E1_RESULTS_DIR: Path  # docs/youra_research/h-e1/results/
H_M2_RESULTS_DIR: Path  # docs/youra_research/h-m2/results/
H_M2_FIGURES_DIR: Path  # docs/youra_research/h-m2/figures/
H_E1_CODE_DIR: Path     # docs/youra_research/h-e1/code/

MODELS: list[str]  # ["llama2-7b-base", "llama2-7b-chat", "llama2-13b-chat", "mistral-7b-instruct"]
TASKS: list[str]   # ["advglue_mnli", "advglue_qqp", "anli_r1", "anli_r2", "anli_r3"]
SPLITS: list[str]  # ["clean", "adversarial"]

DELTA_ACC_GATE: float    # -0.10
CONF_WRONG_GATE: float   # 0.70
GATE_RATE: float         # 0.60
TOTAL_CELLS: int         # 20

NLI_TASKS: list[str]    # ["advglue_mnli", "anli_r1", "anli_r2", "anli_r3"]
NON_NLI_TASKS: list[str]  # ["advglue_qqp"]
```

---

### JsonlLoader (`code/jsonl_loader.py`)

**Dependencies**: config

```python
def load_cell_jsonl(model: str, task: str, split: str) -> list[dict]: ...
    # Returns list of dicts with keys: resps, target, acc
    # Raises FileNotFoundError with diagnostic message if missing

def preflight_check() -> None: ...
    # Verifies all 40 JSONL files exist and have >=200 examples
    # Logs file counts; raises SystemExit on missing files
```

---

### ConfidenceExtractor (`code/confidence_extractor.py`)

**Dependencies**: None (numpy, scipy.special.softmax)

```python
from dataclasses import dataclass

@dataclass
class CellStats:
    accuracy: float
    mean_conf_wrong: float | None
    mean_conf_correct: float | None
    n_wrong: int
    n_total: int

def extract_cell_stats(examples: list[dict]) -> CellStats: ...
    # softmax over resps log-likelihoods -> probs -> argmax pred
    # Logs degenerate logit warning if std(probs) < 0.01
```

---

### CellAnalyzer (`code/cell_analyzer.py`)

**Dependencies**: jsonl_loader, confidence_extractor, config

```python
from dataclasses import dataclass

@dataclass
class DeltaStats:
    model: str
    task: str
    accuracy_clean: float
    accuracy_adv: float
    delta_acc: float
    conf_wrong_clean: float | None
    conf_wrong_adv: float | None
    conf_correct_adv: float | None
    delta_conf_wrong: float | None
    cell_pass: bool

def compute_delta_stats(
    model: str, task: str,
    clean_stats: CellStats, adv_stats: CellStats
) -> DeltaStats: ...

def run_all_cells() -> dict[tuple[str, str], DeltaStats]: ...
    # Iterates 4 models x 5 tasks; loads clean+adv JSONL; computes DeltaStats
```

---

### GateEvaluator (`code/gate_evaluator.py`)

**Dependencies**: cell_analyzer, config

```python
from dataclasses import dataclass

@dataclass
class GateResult:
    gate_pass_rate: float
    gate_pass_count: int
    total_cells: int
    passed_cells: list[tuple[str, str]]
    failed_cells: list[dict]   # {model, task, failure_reason}
    overall_result: str        # "PASS" or "EXPLORE"
    mean_delta_acc: float
    mean_conf_wrong_adv: float

def evaluate_gate(cell_results: dict[tuple[str, str], DeltaStats]) -> GateResult: ...
```

---

### SecondaryAnalyzer (`code/secondary_analyzer.py`)

**Dependencies**: cell_analyzer, config

```python
def base_vs_chat_comparison(
    cell_results: dict[tuple[str, str], DeltaStats]
) -> dict: ...
    # Returns per-task delta_acc for llama2-7b-base vs llama2-7b-chat; mean across tasks

def anli_gradient(
    cell_results: dict[tuple[str, str], DeltaStats]
) -> dict: ...
    # Returns mean delta_acc per ANLI round (r1, r2, r3) across 4 models

def confidence_delta_analysis(
    cell_results: dict[tuple[str, str], DeltaStats]
) -> dict: ...
    # Returns mean delta_conf_wrong across all cells

def ablation_threshold_sensitivity(
    cell_results: dict[tuple[str, str], DeltaStats]
) -> dict: ...
    # A1: delta_acc<=-0.05, A2: delta_acc<=-0.15, A3: conf_wrong>=0.60
    # Returns gate_pass_rate for each variant

def ablation_task_subset(
    cell_results: dict[tuple[str, str], DeltaStats]
) -> dict: ...
    # NLI-only (16 cells) vs non-NLI (4 cells) gate_pass_rate

def ablation_model_size(
    cell_results: dict[tuple[str, str], DeltaStats]
) -> dict: ...
    # 7B models vs 13B model: mean delta_acc and mean conf_wrong_adv
```

---

### Visualizer (`code/visualizer.py`)

**Dependencies**: cell_analyzer, gate_evaluator, config (matplotlib, seaborn)

```python
def plot_gate_metrics(
    cell_results: dict, gate_result: GateResult, out_dir: Path
) -> None: ...
    # figures/gate_metrics_per_cell.png — grouped bars ΔAcc+conf_wrong per cell

def plot_accuracy_scatter(
    cell_results: dict, out_dir: Path
) -> None: ...
    # figures/accuracy_scatter.png — clean vs adv accuracy per model, bubble=conf_wrong

def plot_confidence_distributions(
    cell_results: dict, out_dir: Path
) -> None: ...
    # figures/confidence_distributions.png — per-model histogram of conf_wrong_adv

def plot_delta_acc_heatmap(
    cell_results: dict, out_dir: Path
) -> None: ...
    # figures/delta_acc_heatmap.png — 4x5 heatmap annotated with PASS/FAIL

def plot_anli_gradient(
    anli_stats: dict, out_dir: Path
) -> None: ...
    # figures/anli_gradient.png — bar chart mean ΔAcc per R1/R2/R3

def plot_base_vs_chat(
    comparison_stats: dict, out_dir: Path
) -> None: ...
    # figures/base_vs_chat_comparison.png — grouped bars ΔAcc by model
```

---

### ResultsWriter (`code/results_writer.py`)

**Dependencies**: cell_analyzer, gate_evaluator, secondary_analyzer, config

```python
def write_main_results(
    cell_results: dict[tuple[str, str], DeltaStats], out_dir: Path
) -> None: ...
    # results/h_m2_results.json — all 20 cell stats

def write_gate_report(gate_result: GateResult, out_dir: Path) -> None: ...
    # results/h_m2_gate_report.json

def write_secondary_results(secondary: dict, out_dir: Path) -> None: ...
    # results/h_m2_secondary_results.json

def write_summary(
    gate_result: GateResult, secondary: dict, out_path: Path
) -> None: ...
    # docs/h_m2_summary.md — human-readable gate result + top findings
```

---

### Entrypoint (`code/run_h_m2.py`)

**Dependencies**: all modules

```python
def main() -> None: ...
    # 1. preflight_check()
    # 2. cell_results = run_all_cells()
    # 3. gate_result = evaluate_gate(cell_results)
    # 4. secondary = {base_vs_chat, anli_gradient, conf_delta, ablations}
    # 5. write_main_results / write_gate_report / write_secondary_results / write_summary
    # 6. plot_* (all 6 figures)
    # 7. log gate_pass_rate and PASS/EXPLORE verdict

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | config.py, dirs, preflight_check | 6 | 1+1+2+2 |
| A-2 | JSONL Loader | load_cell_jsonl, preflight_check, format validation | 8 | 2+1+3+2 |
| A-3 | Confidence Extractor | CellStats, softmax extraction, degenerate logit warn | 9 | 2+1+4+2 |
| A-4 | Cell Analyzer | DeltaStats, run_all_cells, delta computations | 11 | 3+3+3+2 |
| A-5 | Gate Evaluator | GateResult, per-cell gate logic, aggregate | 9 | 2+2+3+2 |
| A-6 | Secondary Analyzer | 6 analysis functions, ablation sets | 13 | 3+3+4+3 |
| A-7 | Visualizer | 6 figures, matplotlib/seaborn, color coding | 14 | 3+2+5+4 |
| A-8 | Results Writer | 4 output files, JSON + markdown | 8 | 2+3+2+1 |
| A-9 | Entrypoint + Integration | run_h_m2.py wiring, E2E test | 10 | 2+4+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-7], Medium(9-13): [A-3, A-4, A-5, A-6, A-9], Low(4-8): [A-1, A-2, A-8]

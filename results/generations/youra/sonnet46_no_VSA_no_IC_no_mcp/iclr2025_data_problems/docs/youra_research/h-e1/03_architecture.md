# Architecture: H-E1
# Deduplication Benchmark Signature — Existence Verification

**Hypothesis:** H-E1 (EXISTENCE)
**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr

Applied: Pipeline-Script Architecture (each stage is independent and restartable)
Applied: Results-First Caching (lm-eval JSON results saved before any downstream processing)
Applied: Fail-Fast Mechanism Verification (pre-flight check before full evaluation)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New evaluation scripts from scratch. Pipeline uses standard public APIs (lm-eval CLI, HuggingFace transformers) with well-documented interfaces. No semantic analysis needed.

---

## Overview

H-E1 is a pure evaluation pipeline — no model training. Five independent scripts orchestrate: checkpoint resolution, lm-eval execution, results parsing, statistical testing, and visualization/reporting. Each script reads/writes JSON files so any stage can be rerun in isolation.

---

## File Organization

```
docs/youra_research/h-e1/
├── code/
│   ├── resolve_checkpoints.py     # FR-1: compute token-matched steps → checkpoint_map.json
│   ├── run_evaluation.py          # FR-2: shell out to lm_eval CLI for all 8 models
│   ├── parse_results.py           # FR-3: extract acc,none → results_matrix.json
│   ├── statistical_tests.py       # FR-4+5: paired t-test + mechanism verification
│   ├── visualize.py               # FR-6: 4 figures
│   ├── generate_report.py         # FR-7: write 04_validation.md
│   └── requirements.txt
├── checkpoint_map.json
├── results/
│   └── pythia-{size}-{corpus}-step{N}.json
├── results_matrix.json
├── statistical_results.json
├── figures/
│   ├── differential_bar.png
│   ├── scaling_plot.png
│   ├── paired_scatter.png
│   └── pvalue_heatmap.png
└── 04_validation.md
```

---

## Module Structure

### resolve_checkpoints (`code/resolve_checkpoints.py`)

**Dependencies**: json, pathlib

```python
BATCH_TOKENS: int = 2_097_152
DEDUP_FINAL_STEP: int = 143_000
SIZES: list[str] = ["160m", "410m", "1b", "6.9b"]

def step_to_tokens(step: int) -> int: ...
def find_matched_pile_step(target_tokens: int, batch_tokens: int) -> int: ...
def build_checkpoint_map() -> dict: ...
def main() -> None: ...  # writes checkpoint_map.json
```

### run_evaluation (`code/run_evaluation.py`)

**Dependencies**: subprocess, json, pathlib, checkpoint_map.json

```python
BENCHMARKS: list[str] = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
FEWSHOT: dict[str, int] = {"mmlu": 5, "hellaswag": 0, "arc_challenge": 25, "winogrande": 5}

def build_lmeval_cmd(model_id: str, revision: str, output_path: str) -> list[str]: ...
def evaluate_model(model_id: str, revision: str, output_dir: str) -> None: ...
def main() -> None: ...  # runs 8 model × benchmark evaluations; skips if output exists
```

### parse_results (`code/parse_results.py`)

**Dependencies**: json, pathlib, results/*.json

```python
def load_accuracy(result_path: str, task: str) -> float: ...
    # returns result["results"][task]["acc,none"]
def build_accuracy_matrix(results_dir: str, checkpoint_map: dict) -> dict: ...
    # returns accuracy[size][corpus][benchmark]
def main() -> None: ...  # writes results_matrix.json
```

### statistical_tests (`code/statistical_tests.py`)

**Dependencies**: scipy.stats, numpy, json, results_matrix.json

```python
ALPHA: float = 0.05
N_TESTS: int = 4
CORRECTED_ALPHA: float = 0.0125  # Bonferroni

def verify_mechanism_activation(matrix: dict) -> bool: ...
    # raises RuntimeError if all |delta| < 0.001
def paired_ttest_per_benchmark(matrix: dict) -> dict: ...
    # returns {benchmark: {t_stat, p_value, mean_diff, significant}}
def main() -> None: ...  # writes statistical_results.json
```

### visualize (`code/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy, json, results_matrix.json, statistical_results.json

```python
def plot_differential_bar(matrix: dict, stats: dict, out: str) -> None: ...
def plot_scaling(matrix: dict, out: str) -> None: ...
def plot_paired_scatter(matrix: dict, out: str) -> None: ...
def plot_pvalue_heatmap(stats: dict, out: str) -> None: ...
def main() -> None: ...  # writes figures/*.png
```

### generate_report (`code/generate_report.py`)

**Dependencies**: json, pathlib, statistical_results.json

```python
def gate_passed(stats: dict) -> bool: ...
    # True if any benchmark significant at >= 2 model sizes
def format_report(stats: dict, checkpoint_map: dict) -> str: ...
def main() -> None: ...  # writes 04_validation.md
```

---

## Epic Tasks

#### Epic E1: Checkpoint Resolution
- **Description**: Compute token-count-matched Pile step for each model size; write checkpoint_map.json with step numbers, token counts, and mismatch percentage
- **Output**: `checkpoint_map.json`
- **Complexity**: 6/20 (Module_Size:1 + Dependencies:1 + Algorithm:2 + Integration:2)

#### Epic E2: Evaluation Pipeline
- **Description**: Shell out to lm_eval CLI for all 8 model variants × 4 benchmarks; resume-safe (skip existing JSON outputs); handle float16 + device_map=auto
- **Output**: `results/pythia-{size}-{corpus}-step{N}.json` (32 files)
- **Complexity**: 10/20 (Module_Size:2 + Dependencies:3 + Algorithm:2 + Integration:3)

#### Epic E3: Results Parsing
- **Description**: Parse all 32 lm-eval JSON outputs; extract acc,none per task; construct accuracy[size][corpus][benchmark] matrix
- **Output**: `results_matrix.json`
- **Complexity**: 6/20 (Module_Size:1 + Dependencies:2 + Algorithm:1 + Integration:2)

#### Epic E4: Statistical Testing + Mechanism Verification
- **Description**: Pre-flight check (verify_mechanism_activation); paired t-test per benchmark across 4 model sizes; Bonferroni correction; gate condition evaluation
- **Output**: `statistical_results.json`
- **Complexity**: 7/20 (Module_Size:2 + Dependencies:2 + Algorithm:2 + Integration:1)

#### Epic E5: Visualization
- **Description**: 4 figures: differential bar chart, scaling plot, paired scatter, p-value heatmap; significance stars on bar chart
- **Output**: `figures/*.png` (4 files)
- **Complexity**: 6/20 (Module_Size:2 + Dependencies:2 + Algorithm:1 + Integration:1)

#### Epic E6: Validation Report
- **Description**: Evaluate gate condition (≥1 benchmark p<0.0125 at ≥2 sizes); write PASS/FAIL report with exact p-values and direction summary
- **Output**: `04_validation.md`
- **Complexity**: 5/20 (Module_Size:1 + Dependencies:1 + Algorithm:1 + Integration:2)

**Distribution**: High(10): [E2], Medium(6-7): [E1, E3, E4, E5], Low(5): [E6]

**Total task budget**: 6 epics — within LIGHT tier (≤15 tasks)

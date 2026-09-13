---
title: "Architecture: H-E1 - Alignment-Induced Brier Reliability Overconfidence"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: Phase 3
date: 2026-03-14
tier: LIGHT
---

Applied: minimal-evaluation-pipeline (no domain match in KB; green-field specification)

# Architecture: H-E1 — Alignment-Induced Brier Reliability Overconfidence

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis code. No existing src/ or code/ directories.

---

## Overview

Evaluation-only pipeline. No model training. lm-eval-harness CLI produces per-item log-prob JSON; custom Python scripts compute Brier decomposition, ECE, bootstrap CI, and gate evaluation.

**Data Flow**:
- `run_evaluation.sh` → `results/{model_id}/samples_mmlu*.jsonl`
- `calibration_analysis.py` → `results/calibration_results.json`
- `verify_gate.py` → `results/gate_result.json` + `04_validation.md`
- `plot_results.py` → `figures/*.png`

---

## File Structure

```
h-e1/
├── run_evaluation.sh
├── calibration_analysis.py
├── plot_results.py
├── verify_gate.py
├── results/
│   ├── {model_id}/           # lm-eval JSON output per model
│   ├── calibration_results.json
│   └── gate_result.json
└── figures/
    ├── delta_reliability_bar.png
    ├── calibration_curves.png
    ├── ece_heatmap.png
    ├── brier_decomposition.png
    └── bootstrap_ci_distributions.png
```

---

## Module Definitions

### EvaluationRunner (`run_evaluation.sh`)

**Dependencies**: lm-eval-harness v0.4.11, CUDA_VISIBLE_DEVICES env

Shell script; no Python interface. Iterates over 9 model IDs, calls `lm_eval` CLI with `--log_samples`.

Key variables hardcoded:
- MODEL_IDS: array of 9 checkpoint strings (3 base + 6 aligned)
- OUTPUT_BASE: `./results/`
- BATCH_SIZE: 8 (retried at 4 on OOM)
- NUM_FEWSHOT: 0

---

### CalibrationAnalysis (`calibration_analysis.py`)

**Dependencies**: numpy, scipy.special.softmax, json, csv, argparse

```python
MODELS = [
    "pythia-1.4b-base", "pythia-1.4b-sft", "pythia-1.4b-dpo", "pythia-1.4b-ppo",
    "pythia-2.8b-base", "pythia-2.8b-sft", "pythia-2.8b-dpo", "pythia-2.8b-ppo",
    "pythia-6.9b-base", "pythia-6.9b-sft", "pythia-6.9b-dpo", "pythia-6.9b-ppo",
]
N_BINS: int = 15
N_BOOTSTRAP: int = 1000
SEED: int = 42
RESULTS_DIR: str = "./results"

def load_lmeval_samples(model_id: str, results_dir: str) -> tuple[np.ndarray, np.ndarray]:
    """Parse lm-eval --log_samples JSONL; return (logprobs: (N,4), y_true: (N,))."""
    ...

def compute_brier_decomposition(
    y_true: np.ndarray,      # (N,) int labels 0-3
    y_prob: np.ndarray,      # (N, 4) softmax probs
    n_bins: int = N_BINS,
) -> tuple[float, float, float]:
    """Returns (reliability, resolution, uncertainty) per Murphy 1973."""
    ...

def compute_ece(
    y_true: np.ndarray,      # (N,) int labels 0-3
    y_prob: np.ndarray,      # (N, 4) softmax probs
    n_bins: int = N_BINS,
) -> float:
    """Top-1 confidence ECE per Guo et al. 2017."""
    ...

def compute_delta_reliability(
    base_logprobs: np.ndarray,    # (N, 4)
    aligned_logprobs: np.ndarray, # (N, 4)
    y_true: np.ndarray,           # (N,)
    n_bins: int = N_BINS,
    n_bootstrap: int = N_BOOTSTRAP,
    seed: int = SEED,
) -> tuple[float, float, float]:
    """Returns (delta_reliability, ci_lower, ci_upper)."""
    ...

def run_analysis(results_dir: str = RESULTS_DIR) -> dict:
    """
    Entry point. Load all models, compute metrics, save calibration_results.json.
    Returns results_dict: {model_id: {ece, brier_rel, brier_res, brier_unc,
                                      delta_rel, ci_lower, ci_upper}}
    """
    ...

if __name__ == "__main__":
    # argparse: --results-dir, --smoke-test (1 model, 10 items)
    ...
```

---

### GateVerifier (`verify_gate.py`)

**Dependencies**: json, argparse, pathlib

```python
GATE_CONDITION = {"method": ["ppo", "dpo"], "min_sizes_passing": 2}
SIZES = ["1.4b", "2.8b", "6.9b"]
ALIGNMENTS = ["sft", "dpo", "ppo"]

def evaluate_gate(results: dict) -> dict:
    """
    Check MUST_WORK gate: delta_rel > 0 AND ci_lower > 0 for PPO or DPO in >=2/3 sizes.
    Returns {gate: 'PASS'|'FAIL', method: 'PPO'|'DPO'|'BOTH'|'NONE',
             sizes_passing: [...], failure_mode: str|None}
    """
    ...

def generate_validation_report(
    results: dict,
    gate_result: dict,
    output_path: str = "04_validation.md",
) -> None:
    """Write 04_validation.md: gate result, per-model metrics table, key findings."""
    ...

if __name__ == "__main__":
    # argparse: --results-dir
    ...
```

---

### Plotter (`plot_results.py`)

**Dependencies**: matplotlib, numpy, json, argparse

```python
FIGURES_DIR: str = "./figures"

def plot_delta_reliability_bar(results: dict, out_dir: str = FIGURES_DIR) -> None:
    """Grouped bar chart: ΔBrier reliability with 95% CI per size × alignment."""
    ...

def plot_calibration_curves(results: dict, out_dir: str = FIGURES_DIR) -> None:
    """3×3 reliability diagram grid: base vs SFT/DPO/PPO per size."""
    ...

def plot_ece_heatmap(results: dict, out_dir: str = FIGURES_DIR) -> None:
    """3 sizes × 4 conditions ECE heatmap."""
    ...

def plot_brier_decomposition(results: dict, out_dir: str = FIGURES_DIR) -> None:
    """Stacked bar: reliability / resolution / uncertainty per model."""
    ...

def plot_bootstrap_ci_distributions(results: dict, out_dir: str = FIGURES_DIR) -> None:
    """Bootstrap delta distributions with 95% CI bands."""
    ...

if __name__ == "__main__":
    # argparse: --results-dir, --figures-dir
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Verify checkpoints & run lm-eval | Resolve Li et al. 2024 HuggingFace model IDs (Risk R1); write run_evaluation.sh; smoke-test 1 model 10 items; full 9-model eval run | 14 | 3+3+4+4 |
| A-2 | Implement Brier decomposition + ECE | calibration_analysis.py: load_lmeval_samples parser, compute_brier_decomposition (Murphy 1973), compute_ece (Guo 2017), unit smoke test on synthetic data | 13 | 3+3+4+3 |
| A-3 | Bootstrap CI + delta computation | compute_delta_reliability with n=1000 bootstrap percentile CI; save calibration_results.json; CSV summary log | 11 | 3+3+3+2 |
| A-4 | Gate evaluation + validation report | verify_gate.py: evaluate_gate logic; generate_validation_report writing 04_validation.md with metrics table and failure analysis | 9 | 2+2+3+2 |
| A-5 | Visualization | plot_results.py: all 5 figures (delta bar mandatory; calibration curves, ECE heatmap, Brier stacked bar, bootstrap CI distributions) | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-1], Medium(9-13): [A-2, A-3, A-4], Low(4-8): [A-5]

---

## Execution Order

1. A-1 (lm-eval runs) — prerequisite for all downstream
2. A-2 + A-3 (calibration_analysis.py) — sequential within file
3. A-4 (gate + report) — requires calibration_results.json
4. A-5 (figures) — requires calibration_results.json

---

## Key Constants

| Constant | Value | Source |
|----------|-------|--------|
| N_BINS | 15 | Murphy 1973 / Guo 2017 |
| N_BOOTSTRAP | 1000 | Phase 2B spec |
| SEED | 42 | NFR-1 |
| BATCH_SIZE | 8 (fallback 4) | NFR-2 |
| NUM_FEWSHOT | 0 | FR-1.2 |
| MMLU task | `mmlu` | lm-eval-harness |

---

*Generated: Phase 3 Architecture Agent*
*Hypothesis: H-E1 (EXISTENCE, FOUNDATION, LIGHT tier)*

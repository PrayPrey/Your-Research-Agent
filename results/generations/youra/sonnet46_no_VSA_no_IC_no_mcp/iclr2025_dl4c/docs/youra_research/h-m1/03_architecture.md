---
title: "Architecture: H-M1 — SFT Signal Void at Hard Difficulty"
hypothesis_id: H-M1
hypothesis_type: MECHANISM
tier: FULL
date: "2026-08-26"
author: yoon303@ust.ac.kr
---

Applied: Flat-script analysis pattern (no abstractions, one file per concern)
Applied: Results-file decoupling pattern (each script reads/writes JSON independently)
Applied: bigcode-harness subprocess delegation pattern (evaluation via shell-out, not Python import)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 extends H-E1)
**Status**: H-E1 is green-field (Phase 4 not yet run) — architecture spec used as source of truth
**Analyzed Path**: `docs/youra_research/h-e1/code/` (not yet materialized; referenced via 03_architecture.md)
**Findings**: H-E1 defines flat scripts: data_utils.py, reward.py, train_sft.py, train_rlef.py, evaluate.py, analyze.py. H-M1 reuses the SFT checkpoint and evaluate.py shell-out pattern. No new training required.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From H-E1 Architecture Spec)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| evaluate (harness runner) | shell-out pattern only — not imported | `h-e1/code/evaluate.py` |
| SFT checkpoint | `./checkpoints/h-e1/sft_checkpoint` | filesystem path |
| requirements.txt | inherited + no new deps | `h-e1/code/requirements.txt` |

**Verified from**: `docs/youra_research/h-e1/03_architecture.md` (actual code not yet written)

H-M1 does NOT import H-E1 Python modules. It reuses the SFT checkpoint path and the bigcode-harness shell-out pattern. All H-M1 scripts are standalone.

---

## Module Structure

### analyze_sft_lcb (`code/analyze_sft_lcb.py`)

**Dependencies**: subprocess, json, pathlib (stdlib only)

```python
def run_lcb_hard_eval(
    checkpoint_path: str,
    harness_dir: str,
    output_path: str,
) -> dict:
    """Shell out to bigcode-evaluation-harness for LCB-Hard.
    Returns parsed JSON with livecodebench pass@1."""
    ...

def extract_lcb_hard_pass1(results_json_path: str) -> float:
    """Read harness output JSON, return pass@1 float."""
    ...

def check_gate(pass1: float, threshold: float = 0.60) -> dict:
    """Returns {'signal_void_confirmed': bool, 'pass1': float, 'margin': float}."""
    ...
```

### analyze_sft_loss (`code/analyze_sft_loss.py`)

**Dependencies**: torch, transformers, datasets, numpy, json, tqdm

```python
def load_model_and_tokenizer(checkpoint_path: str, device: str = "cuda"):
    """Returns (model, tokenizer) from local checkpoint."""
    ...

def compute_per_example_loss(
    model, tokenizer, example: dict, max_length: int = 2048, device: str = "cuda"
) -> float:
    """Forward pass, returns cross-entropy loss for one APPS example."""
    ...

def compute_difficulty_stratified_loss(
    checkpoint_path: str,
    dataset_name: str = "codeparrot/apps",
    split: str = "train",
    output_path: str = "results/h-m1_apps_difficulty_loss.json",
    max_examples_per_bucket: int = 500,
    device: str = "cuda",
) -> dict:
    """Returns {'introductory': float, 'interview': float, 'competition': float, 'counts': dict}."""
    ...
```

### check_apps_coverage (`code/check_apps_coverage.py`)

**Dependencies**: subprocess, datasets, json, tqdm, tempfile (stdlib + datasets)

```python
def check_solution_passes(solution: str, test_cases: list[dict], timeout: float = 5.0) -> bool:
    """Execute solution against test cases in subprocess. Returns True if all pass."""
    ...

def compute_coverage(
    dataset_name: str = "codeparrot/apps",
    difficulty: str = "competition",
    output_path: str = "results/h-m1_apps_hard_coverage.json",
    max_problems: int = None,
) -> dict:
    """Returns {'total': int, 'solvable': int, 'coverage_pct': float, 'difficulty': str}."""
    ...
```

### aggregate_results (`code/aggregate_results.py`)

**Dependencies**: json, pathlib (stdlib only)

```python
def load_all_results(results_dir: str) -> dict:
    """Loads h-m1_sft_lcb_hard.json, h-m1_apps_difficulty_loss.json, h-m1_apps_hard_coverage.json."""
    ...

def verify_signal_void_mechanism(results: dict) -> tuple[bool, dict]:
    """Primary: pass1 < 0.60. Secondary: competition_loss > introductory_loss.
    Returns (success, indicators_dict)."""
    ...

def write_signal_void_analysis(indicators: dict, output_path: str = "results/signal_void_analysis.json") -> None:
    """Writes combined gate decision + all indicators to JSON."""
    ...
```

### make_figures (`code/make_figures.py`)

**Dependencies**: matplotlib, seaborn, json, pathlib, numpy

```python
def plot_gate_metrics(lcb_results: dict, figures_dir: str) -> None:
    """Bar chart: SFT pass@1 vs 60% threshold on LCB-Hard."""
    ...

def plot_difficulty_gradient(lcb_results: dict, figures_dir: str) -> None:
    """Line chart: SFT pass@1 across HumanEval → MBPP → LCB-Easy → LCB-Medium → LCB-Hard."""
    ...

def plot_apps_difficulty_loss(loss_results: dict, figures_dir: str) -> None:
    """Bar chart: mean SFT loss per APPS difficulty bucket, annotated with sample counts."""
    ...

def plot_apps_coverage(coverage_results: dict, figures_dir: str) -> None:
    """Stacked bar: solvable vs unsolvable APPS-Competition problems."""
    ...

def make_all(results_dir: str, figures_dir: str) -> None:
    """Entry point: loads all results JSONs, calls all 4 plot functions."""
    ...
```

---

## File Organization

```
docs/youra_research/h-m1/
├── 02c_experiment_brief.md
├── 03_prd.md
├── 03_architecture.md
├── figures/
│   ├── gate_metrics.png
│   ├── difficulty_gradient.png
│   ├── apps_difficulty_loss.png
│   └── apps_coverage.png
└── code/
    ├── analyze_sft_lcb.py
    ├── analyze_sft_loss.py
    ├── check_apps_coverage.py
    ├── aggregate_results.py
    ├── make_figures.py
    └── requirements.txt

checkpoints/
└── h-e1/
    └── sft_checkpoint/    (reused from H-E1, no new training)

results/h-m1/
├── h-m1_sft_lcb_hard.json
├── h-m1_apps_difficulty_loss.json
├── h-m1_apps_hard_coverage.json
└── signal_void_analysis.json
```

---

## Module Dependencies

```
analyze_sft_lcb    → writes h-m1_sft_lcb_hard.json
analyze_sft_loss   → writes h-m1_apps_difficulty_loss.json
check_apps_coverage → writes h-m1_apps_hard_coverage.json

aggregate_results  ← reads all three JSONs above
                   → writes signal_void_analysis.json

make_figures       ← reads all three JSONs above
                   → writes figures/*.png
```

No circular dependencies. aggregate_results and make_figures are fully decoupled — read only JSON files.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown (Size+Dep+Algo+Integ) |
|----|------|-------------|------------|----------------------------------|
| M1-1 | Project Setup | File structure, requirements.txt (inherit H-E1 deps, no additions), results dirs, harness clone verification | 5 | 1+2+1+1 |
| M1-2 | LCB-Hard Evaluation | Implement analyze_sft_lcb.py: shell-out to bigcode-harness, parse output, check_gate vs 60% threshold | 8 | 2+2+1+3 |
| M1-3 | APPS Loss Stratification | Implement analyze_sft_loss.py: load H-E1 SFT checkpoint, forward-pass per example, stratify by difficulty bucket | 12 | 3+3+3+3 |
| M1-4 | APPS Coverage Check | Implement check_apps_coverage.py: subprocess execution of reference solutions against test cases, per-bucket coverage | 11 | 3+2+3+3 |
| M1-5 | Result Aggregation | Implement aggregate_results.py: load all JSONs, verify_signal_void_mechanism, write signal_void_analysis.json | 7 | 2+2+1+2 |
| M1-6 | Figure Generation | Implement make_figures.py: all 4 figures (gate_metrics, difficulty_gradient, apps_difficulty_loss, apps_coverage) | 9 | 3+2+2+2 |
| M1-7 | Integration Run | End-to-end execution: run all scripts in order, verify gate condition, validate output files exist and parse correctly | 8 | 1+2+1+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M1-3, M1-4, M1-6], Low(4-8): [M1-1, M1-2, M1-5, M1-7]

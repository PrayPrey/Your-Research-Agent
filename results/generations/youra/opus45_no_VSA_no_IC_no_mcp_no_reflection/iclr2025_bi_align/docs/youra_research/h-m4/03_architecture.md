# Architecture: H-M4 (MECHANISM, SHOULD_WORK)

**Hypothesis:** Under bidirectional training, IFEval (explicit) gains transfer to TruthfulQA/BBQ (implicit) safety gains.

Applied: eval-harness-wrapper-pattern (lm-eval-harness HFLM wrapper per checkpoint, reused from safety-eval architectures)
Applied: baseline-vs-treatment-gate-pattern (max-baseline delta threshold, reused from H-M1/M3 gate style)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m3, checkpoints + infra source)
**Status:** patterns found from base code — H-M4 is pure evaluation (no training), reuses H-M3 checkpoint layout and config dataclass style only
**Analyzed Path:** `h-m3/code/`
**Findings:**
- H-M3 checkpoints are written to `{output_dir}/{name}/checkpoints/step_{total_steps}` (see `alpha_sweep.py:34`), NOT the flat `checkpoints/b1_sft` style paths shown in the H-M4 PRD — H-M4 must resolve actual checkpoint dirs via a `CHECKPOINT_PATHS` mapping built from H-M3's `output_dir` layout, not assume flat paths.
- `config.py` dataclass style (`@dataclass` plain classes, module-level constant dicts like `ALPHA_SWEEP_CONFIGS`) is the established convention — H-M4 config follows the same flat-dataclass-plus-dict-of-presets pattern.
- No existing TruthfulQA/BBQ/lm-eval-harness code in h-m3 — `safety_eval.py` and `transfer_analysis.py` are entirely new for H-M4.
- H-M3's `evaluate.py` `run_checkpoint_eval` pattern (load checkpoint path string, return result dict) is the interface convention to mirror for the new safety evaluator.

---

## External Dependencies (Base Hypothesis)

### Checkpoint Resolution (From Actual H-M3 Code)

| Model | Logical Name (PRD) | Actual Path Pattern (H-M3) |
|-------|--------------------|-----------------------------|
| B2 (helpfulness RLHF) | `checkpoints/b2_helpfulness_rlhf` | `h-m3/code/checkpoints/B2/checkpoints/step_1000` |
| T1-T4 | `checkpoints/t{n}_alpha{a}` | `h-m3/code/checkpoints/T{n}/checkpoints/step_1000` |
| B1 (SFT-only) | `checkpoints/b1_sft` | not produced by H-M3 sweep — must exist from H-M1 SFT stage or base model; resolve via `CHECKPOINT_PATHS` override |
| B3 (quality-only) | `checkpoints/b3_quality_rlhf` | not produced by H-M3 sweep — separate checkpoint, resolve via `CHECKPOINT_PATHS` override |

**Verified from**: `h-m3/code/alpha_sweep.py` (actual implementation, not PRD path strings)

**Note:** `CHECKPOINT_PATHS: dict[str, str]` in `config.py` is the single source of truth; B1/B3 paths are external inputs (not derivable from H-M3 code) — fail fast with `FileNotFoundError` if missing rather than guessing.

---

## File Structure

```
h-m4/code/
├── config.py             # CHECKPOINT_PATHS dict, TASKS list, thresholds
├── safety_eval.py         # lm-eval-harness wrapper: evaluate_all(), per-model results
├── transfer_analysis.py    # gate verification + IFEval/safety correlation
├── visualize.py              # bar chart, correlation scatter, BBQ breakdown
└── run_experiment.py           # entrypoint: load configs -> eval -> analyze -> plot
```

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

CHECKPOINT_PATHS: dict[str, str] = {
    "b1": "checkpoints/b1_sft",
    "b2": "h-m3/code/checkpoints/B2/checkpoints/step_1000",
    "b3": "checkpoints/b3_quality_rlhf",
    "t1": "h-m3/code/checkpoints/T1/checkpoints/step_1000",
    "t2": "h-m3/code/checkpoints/T2/checkpoints/step_1000",
    "t3": "h-m3/code/checkpoints/T3/checkpoints/step_1000",
    "t4": "h-m3/code/checkpoints/T4/checkpoints/step_1000",
}

TASKS: list[str] = ["truthfulqa_mc1", "truthfulqa_mc2", "bbq"]
GATE_THRESHOLD_PP: float = 2.0
BASELINES: list[str] = ["b1", "b2", "b3"]
TREATMENTS: list[str] = ["t1", "t2", "t3", "t4"]

@dataclass
class EvalConfig:
    batch_size: int = 8
    device: str = "cuda"
    bootstrap_n: int = 1000
    seed: int = 42
```

### Safety Evaluator (`safety_eval.py`)

**Dependencies**: lm-eval (pip), config

```python
def resolve_checkpoint(name: str, checkpoint_paths: dict[str, str]) -> str:
    """Raise FileNotFoundError if path missing (esp. b1/b3 not from H-M3 sweep)."""
    ...

def evaluate_model(name: str, path: str, cfg: "EvalConfig", tasks: list[str]) -> dict[str, float]:
    """Wrap HFLM + evaluator.simple_evaluate; extract acc per task."""
    ...

def evaluate_all(checkpoint_paths: dict[str, str], cfg: "EvalConfig") -> dict[str, dict[str, float]]:
    """Loop evaluate_model over all 7 models. Returns {name: {task: acc}}."""
    ...

def bootstrap_ci(scores: list[float], n_bootstrap: int = 1000, ci: float = 0.95) -> tuple[float, float]:
    """Percentile bootstrap CI for a metric's per-item scores."""
    ...
```

### Transfer Analysis (`transfer_analysis.py`)

**Dependencies**: scipy, config, safety_eval results

```python
def verify_gate(results: dict, baselines: list[str], treatments: list[str],
                 threshold_pp: float = 2.0) -> dict:
    """Per-metric: baseline_max, best_treatment, improvement_pp, pass. gate_pass = any metric passes."""
    ...

def statistical_significance(t_scores: list[float], b_scores: list[float], alpha: float = 0.05) -> dict:
    """Two-tailed t-test, returns t_statistic/p_value/significant."""
    ...

def correlate_transfer(ifeval_gains: dict[str, float], safety_gains: dict[str, float]) -> dict:
    """Pearson r between IFEval Δ (from H-M2) and safety Δ per treatment. Returns r/p_value/interpretation/significant."""
    ...
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, transfer_analysis/safety_eval outputs

```python
def plot_gate_bar(results: dict, out_dir: str) -> None:
    """Required: T1-T4 vs B1-B3 bar chart on TruthfulQA MC1 and BBQ, with 95% CI error bars."""
    ...

def plot_correlation_scatter(ifeval_gains: dict, safety_gains: dict, out_dir: str) -> None:
    """IFEval Δ (x) vs Safety Δ (y) scatter with regression line."""
    ...

def plot_bbq_category_breakdown(results: dict, out_dir: str) -> None:
    """Per-category (9 demographic) accuracy heatmap or grouped bar, model x category."""
    ...
```

### Entrypoint (`run_experiment.py`)

**Dependencies**: config, safety_eval, transfer_analysis, visualize

```python
def main(checkpoint_paths: dict[str, str] = None, ifeval_gains: dict[str, float] = None) -> dict:
    """Load configs -> evaluate_all -> verify_gate -> correlate_transfer -> plots. Returns full results dict, prints PASS/FAIL."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M4-1 | Checkpoint resolution | `resolve_checkpoint`: map logical names to actual H-M3 paths, fail-fast on missing B1/B3 | 5 | 1+2+1+1 |
| M4-2 | lm-eval-harness wrapper | `evaluate_model`/`evaluate_all`: HFLM wrapper, simple_evaluate call, extract MC1/MC2/BBQ acc for 7 models | 10 | 3+3+2+2 |
| M4-3 | Bootstrap CI | `bootstrap_ci`: percentile bootstrap (n=1000) for accuracy metrics | 4 | 1+1+1+1 |
| M4-4 | Gate verification | `verify_gate`: baseline_max vs best_T per metric, ≥2pp threshold, gate_pass aggregation | 6 | 2+2+1+1 |
| M4-5 | Statistical significance | `statistical_significance`: two-tailed t-test T* vs baselines, α=0.05 | 4 | 1+1+1+1 |
| M4-6 | Correlation analysis | `correlate_transfer`: Pearson r between IFEval gains (H-M2 input) and safety gains, significance | 7 | 2+3+1+1 |
| M4-7 | Gate bar chart | `plot_gate_bar`: T1-T4 vs B1-B3 on TruthfulQA MC1 + BBQ with CI error bars | 6 | 2+1+1+2 |
| M4-8 | Correlation + BBQ figures | `plot_correlation_scatter`, `plot_bbq_category_breakdown` | 7 | 3+1+1+2 |
| M4-9 | Experiment orchestration | `run_experiment.main`: wire all modules, PoC cost-guard (subset prompts option), print gate result | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M4-2, M4-9], Low(4-8): [M4-1, M4-3, M4-4, M4-5, M4-6, M4-7, M4-8]

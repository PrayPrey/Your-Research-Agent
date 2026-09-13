# Configuration: H-M4

Applied: eval-harness-wrapper-pattern config style (flat dataclass + module-level constant dicts)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m3)
**Status**: config classes verified from base code (h-m3/code/config.py, alpha_sweep.py) — H-M4 is pure evaluation, no training config to inherit beyond checkpoint path convention
**Config Files Found**: `h-m3/code/config.py` (dataclass + dict-of-presets pattern), `h-m3/code/alpha_sweep.py` (checkpoint output layout: `{output_dir}/{name}/checkpoints/step_{total_steps}`)
**Pattern Used**: dataclass + dict (matches h-m3 convention; NOT inheriting a base dataclass since H-M4 has no training hyperparameters)

---

## M4-1/M4-2: Checkpoint Resolution & Eval Wrapper [Complexity: 15, Budget: 15]

**Applied**: Verified actual H-M3 checkpoint paths (not PRD's flat `checkpoints/b1_sft` style) — see architecture.md External Dependencies table.

### Configuration (Python Dataclass + Dict)

```python
from dataclasses import dataclass

CHECKPOINT_PATHS: dict[str, str] = {
    "b1": "checkpoints/b1_sft",                                  # external — not from H-M3 sweep
    "b2": "h-m3/code/checkpoints/B2/checkpoints/step_1000",
    "b3": "checkpoints/b3_quality_rlhf",                          # external — not from H-M3 sweep
    "t1": "h-m3/code/checkpoints/T1/checkpoints/step_1000",
    "t2": "h-m3/code/checkpoints/T2/checkpoints/step_1000",
    "t3": "h-m3/code/checkpoints/T3/checkpoints/step_1000",
    "t4": "h-m3/code/checkpoints/T4/checkpoints/step_1000",
}

TASKS: list[str] = ["truthfulqa_mc1", "truthfulqa_mc2", "bbq"]
BASELINES: list[str] = ["b1", "b2", "b3"]
TREATMENTS: list[str] = ["t1", "t2", "t3", "t4"]

@dataclass
class EvalConfig:
    batch_size: int = 8
    device: str = "cuda"
    bootstrap_n: int = 1000
    seed: int = 42
```

**Non-standard**: `b1`/`b3` paths are placeholders — `resolve_checkpoint()` MUST raise `FileNotFoundError` if these don't exist on disk (fail-fast, not silently substitute another checkpoint).

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M4-1-1 | resolve_checkpoint | Look up name in `CHECKPOINT_PATHS`, verify path exists, raise `FileNotFoundError` if missing |
| C-M4-1-2 | evaluate_model | HFLM(pretrained=path, batch_size, device) + `evaluator.simple_evaluate(tasks=TASKS)`, extract acc per task |
| C-M4-1-3 | evaluate_all | Loop `evaluate_model` over all 7 `CHECKPOINT_PATHS` entries, collect `{name: {task: acc}}` |
| C-M4-1-4 | error handling | Wrap per-model eval in try/except, log + re-raise on missing checkpoint |

---

## M4-3: Bootstrap CI [Complexity: 4, Budget: 4]

**Applied**: Standard percentile bootstrap, no KB search needed.

### Configuration

```python
@dataclass
class BootstrapConfig:
    n_bootstrap: int = 1000
    ci: float = 0.95
    seed: int = 42
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M4-3-1 | bootstrap_ci | Resample per-item scores `n_bootstrap` times, return (lower, upper) percentile bounds |

---

## M4-4: Gate Verification [Complexity: 6, Budget: 6]

**Applied**: baseline-vs-treatment-gate-pattern (reused from H-M1/M3).

### Configuration

```python
GATE_THRESHOLD_PP: float = 2.0
GATE_METRICS: list[str] = ["truthfulqa_mc1", "truthfulqa_mc2", "bbq"]
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M4-4-1 | per-metric baseline_max | `max(results[b][metric] for b in BASELINES)` |
| C-M4-4-2 | per-metric best_treatment | `max(results[t][metric] for t in TREATMENTS)`, compute improvement_pp |
| C-M4-4-3 | per-metric pass flag | `improvement_pp >= GATE_THRESHOLD_PP` |
| C-M4-4-4 | gate_pass aggregation | `any(metric pass)` across GATE_METRICS |

---

## M4-5: Statistical Significance [Complexity: 4, Budget: 4]

### Configuration

```python
@dataclass
class SignificanceConfig:
    alpha: float = 0.05
    test: str = "ttest_ind"  # two-tailed
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M4-5-1 | statistical_significance | `scipy.stats.ttest_ind(t_scores, b_scores)`, return t_stat/p_value/significant |

---

## M4-6: Correlation Analysis [Complexity: 7, Budget: 7]

**Note**: `ifeval_gains` is an external input from H-M2 (not computed in H-M4), passed into `run_experiment.main()`.

### Configuration

```python
@dataclass
class CorrelationConfig:
    alpha: float = 0.05  # significance threshold for Pearson p-value
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M4-6-1 | assemble ifeval_gains | Accept as external dict param `{t1..t4: float}` from H-M2 results |
| C-M4-6-2 | assemble safety_gains | `results[t][metric] - results["b2"][metric]` per treatment |
| C-M4-6-3 | pearsonr | `scipy.stats.pearsonr(ifeval_gains.values(), safety_gains.values())` |
| C-M4-6-4 | interpretation | "positive"/"negative"/"none" from sign of r, significant if p < alpha |

---

## M4-7: Gate Bar Chart [Complexity: 6, Budget: 6]

### Configuration

```python
@dataclass
class PlotConfig:
    figsize: tuple[int, int] = (10, 6)
    dpi: int = 150
    out_dir: str = "h-m4/figures"
    ci_alpha: float = 0.3  # error bar transparency
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M4-7-1 | data prep | Gather per-model TruthfulQA MC1 + BBQ acc with CI bounds |
| C-M4-7-2 | bar layout | Grouped bars: 7 models x 2 metrics |
| C-M4-7-3 | error bars | 95% CI from `bootstrap_ci` as yerr |
| C-M4-7-4 | save | `plt.savefig(f"{out_dir}/gate_bar.png", dpi=dpi)` |

---

## M4-8: Correlation + BBQ Figures [Complexity: 7, Budget: 7]

### Configuration

```python
BBQ_CATEGORIES: list[str] = [
    "age", "disability_status", "gender_identity", "nationality",
    "physical_appearance", "race_ethnicity", "religion",
    "sexual_orientation", "socioeconomic_status",
]
```

**Non-standard**: category list hardcoded per BBQ paper (Parrish et al. 2022) 9-category taxonomy — required for per-category breakdown plot.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M4-8-1 | scatter data | ifeval_gains (x) vs safety_gains (y) per treatment |
| C-M4-8-2 | regression line | `np.polyfit` degree-1 fit overlay |
| C-M4-8-3 | bbq heatmap | model x `BBQ_CATEGORIES` accuracy grid |
| C-M4-8-4 | save both | `{out_dir}/correlation_scatter.png`, `{out_dir}/bbq_breakdown.png` |

---

## M4-9: Experiment Orchestration [Complexity: 8, Budget: 8]

### Configuration

```python
@dataclass
class ExperimentConfig:
    eval_cfg: EvalConfig = None          # defaults to EvalConfig()
    bootstrap_cfg: BootstrapConfig = None
    sig_cfg: SignificanceConfig = None
    poc_subset_n: int | None = None      # if set, subsample prompts for cost-guard PoC run
```

**Non-standard**: `poc_subset_n` — cost-guard for PoC runs (BBQ ~58k examples is expensive); when set, evaluator subsamples that many examples per task instead of full dataset.

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M4-9-1 | wire pipeline | `evaluate_all` → `verify_gate` → `correlate_transfer` → plot functions |
| C-M4-9-2 | PoC cost guard | If `poc_subset_n` set, pass subset limit into `evaluate_model` (lm-eval `limit` param) |
| C-M4-9-3 | print result | Print PASS/FAIL per `verify_h_m4`-style gate summary, return full results dict |

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m3/code/config.py (ACTUAL CODE) — pattern only, no fields inherited
# H-M4 has no training hyperparameters; only checkpoint output layout convention is reused:
#   {output_dir}/{name}/checkpoints/step_{total_steps}
# CHECKPOINT_PATHS above is built directly from this observed layout (see alpha_sweep.py:34).
```

**Verified from**: `h-m3/code/alpha_sweep.py`, `h-m3/code/config.py`

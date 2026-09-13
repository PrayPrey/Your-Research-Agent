# Config: H-M3 (Objective x Length F1 Retention, 2x3 Factorial)

**Applied**: No direct KB match for MOHAWK/CAB distillation config — reused H-M2 dataclass + scipy/statsmodels stats conventions instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m2/code/ exists)
**Status**: Serena had no active project registered for this cwd; verified `AnalysisConfig` field names/defaults via direct Read of `h-m2/code/config.py` (actual implementation, not spec).
**Config Files Found**: `h-m2/code/config.py` (`AnalysisConfig` dataclass)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m2/code/config.py (ACTUAL CODE, verified)
@dataclass
class AnalysisConfig:
    teacher_name: str = "microsoft/phi-1_5"
    mohawk_name: str = "goombalab/phi-mamba"
    cab_name: str = "wph6/CAB"
    teacher_dim: int = 2048
    dataset_name: str = "allenai/c4"
    dataset_config: str = "en"
    batch_size: int = 8
    seed: int = 42
    device: str = "cuda"
    dtype: str = "float16"
    output_dir: str = "results"
    figures_dir: str = "figures"
```

**Note**: H-M2's actual `model.py` used `state-spaces/mamba-1.4b-hf` as proxy for both `mohawk_name`/`cab_name` fields (real checkpoints unusable — no mamba-ssm CUDA build). H-M3 does NOT import H-M2 loaders; no real distillation training code exists to reuse. Only field-naming/dataclass style carried over.

---

## C-1/C-2/C-3/C-4/C-5/C-6/C-7: ExperimentConfig (shared, single dataclass)

```python
@dataclass
class ExperimentConfig:
    teacher_name: str = "microsoft/phi-1_5"
    student_base_name: str = "state-spaces/mamba-1.4b-hf"  # proxy, per H-M2 finding
    teacher_dim: int = 2048

    train_dataset: str = "allenai/c4"
    train_dataset_config: str = "en"
    tokens_per_condition: int = 1_500_000_000  # scaled down via --smoke flag for PoC
    checkpoint_every_tokens: int = 500_000_000

    lengths: List[int] = field(default_factory=lambda: [4096, 16384, 32768])
    objectives: List[str] = field(default_factory=lambda: ["mohawk", "cab"])

    lr: float = 3e-4
    weight_decay: float = 0.1
    batch_size: int = 4
    grad_accum: int = 8
    dtype: str = "bfloat16"
    seed: int = 42

    longbench_tasks: List[str] = field(default_factory=lambda: [
        "narrativeqa", "qasper", "multifieldqa_en", "hotpotqa",
        "2wikimqa", "musique", "triviaqa"])
    samples_per_task: int = 200  # ~1400 total, full LongBench test splits

    checkpoint_dir: str = "checkpoints"
    output_dir: str = "results"
    figures_dir: str = "figures"
```

Non-standard: `tokens_per_condition=1.5B` and `checkpoint_every_tokens=500M` are PRD-specified, not tuning defaults.

### Subtasks [0/0 — out of budget scope, see C-8/C-9 below]
Config/training/data/eval subtasks (C-1 through C-7) share the single `ExperimentConfig` above; no separate config subtasks allocated within this budget.

---

## C-8: 2x3 ANOVA + t-test statistical analysis [Complexity: 11, Budget: 2]

**Applied**: scipy/statsmodels stats module pattern, reused from H-M2 `analysis.py` (`compute_slope`) convention.

### Configuration (extends ExperimentConfig — no new dataclass, use module-level constants)

```python
# stats.py constants
ANOVA_FORMULA: str = "f1 ~ C(objective) * C(length)"
SIGNIFICANCE_ALPHA: float = 0.05

# Gate thresholds (from PRD FR-6 / Section 6.3)
GATE_P2_LENGTH: int = 16384
GATE_P2_MIN_DIFF: float = 3.0   # CAB - MOHAWK F1 points at 16K
GATE_P3_LENGTH: int = 32768
GATE_P3_MIN_DIFF: float = 5.0   # CAB - MOHAWK F1 points at 32K
CI_CONFIDENCE: float = 0.95
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-8-1 | Two-way ANOVA | `run_two_way_anova`: statsmodels `ols(ANOVA_FORMULA)` + `anova_lm(typ=2)` -> objective_p, length_p, interaction_p |
| C-8-2 | Per-length t-test + gate | `per_length_ttest` (scipy `ttest_ind`, 95% CI) at each length; `evaluate_gate` checks `interaction_p < SIGNIFICANCE_ALPHA` and diffs vs `GATE_P2_MIN_DIFF`/`GATE_P3_MIN_DIFF` |

---

## C-9: Visualization suite [Complexity: 8, Budget: 3]

**Applied**: matplotlib/seaborn standard plotting defaults, no KB pattern match.

### Configuration

```python
# visualize.py constants
FIGURE_DPI: int = 150
FIGURE_SIZE: Tuple[int, int] = (8, 5)
CI_ERROR_BARS: float = 0.95
PALETTE: Dict[str, str] = field(default_factory=lambda: {"mohawk": "#d62728", "cab": "#1f77b4"})
REQUIRED_FIGURES: List[str] = field(default_factory=lambda: [
    "f1_retention_bars.png", "interaction_plot.png"])
OPTIONAL_FIGURES: List[str] = field(default_factory=lambda: [
    "per_task_breakdown.png", "effect_size_heatmap.png"])
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-9-1 | F1 retention bar chart (required) | `plot_f1_retention_bars`: X=length, grouped bars MOHAWK/CAB, 95% CI error bars |
| C-9-2 | Interaction plot (required) | `plot_interaction`: line plot MOHAWK vs CAB across 3 lengths, annotate crossover |
| C-9-3 | Optional figures | `plot_per_task_breakdown`, `plot_effect_size_heatmap` — skip if budget/time constrained (optional per PRD FR-7) |

---

## Summary

- Single `ExperimentConfig` dataclass covers C-1 through C-7 (training/data/eval), consistent with H-M2's single-dataclass pattern.
- C-8/C-9 use module-level constants (not new dataclasses) since values are fixed thresholds from PRD, not tunable hyperparameters — avoids config sprawl.
- Total budget used: 5/5 subtasks (2 for C-8, 3 for C-9), per allocation.

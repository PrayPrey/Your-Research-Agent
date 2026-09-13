# Configuration: h-c1

**Type**: CONDITION | **Gate**: SHOULD_WORK

Applied: dataclass config pattern (reused from h-e1; KB search returned no relevant new hits, fallback to prior validated pattern)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from actual h-e1 code (`docs/youra_research/h-e1/code/config.py`), read directly (Serena project not active for this workspace; direct file read used per architecture's own fallback)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dataclass (Python)

---

## Inherited Configuration (Base Hypothesis)

All fields below are copied **unmodified** from h-e1 (verified from actual code, not specs). h-c1 reuses `MODELS`, `MODEL_HF_IDS`, `RANKS`, `SEEDS`, `TARGET_MODULES`, `TrainConfig`, `LoRAConfig`, `AnalysisConfig` as-is.

```python
# From: h-e1/code/config.py (ACTUAL CODE — copy into h-c1/code/config.py unmodified)
MODELS: dict[str, float] = {
    "pythia-1b": 1.0e9,
    "pythia-2.8b": 2.8e9,
    "pythia-6.9b": 6.9e9,
    "pythia-12b": 1.2e10,
}

MODEL_HF_IDS: dict[str, str] = {
    "pythia-1b": "EleutherAI/pythia-1b",
    "pythia-2.8b": "EleutherAI/pythia-2.8b",
    "pythia-6.9b": "EleutherAI/pythia-6.9b",
    "pythia-12b": "EleutherAI/pythia-12b",
}

RANKS: list[int] = [4, 8, 16, 32, 64, 128]
SEEDS: list[int] = [42, 1337, 2024]
TARGET_MODULES: list[str] = ["query_key_value"]


@dataclass
class TrainConfig:
    epochs: int = 3
    lr: float = 1e-4
    batch_size: int = 8
    grad_accum: int = 4
    warmup_steps: int = 100
    max_length: int = 384          # h-c1 overrides to 512 (HotpotQA multi-doc context, per PRD FR-1)
    lr_scheduler: str = "linear"
    grad_clip: float = 1.0
    gradient_checkpointing: bool = True


@dataclass
class LoRAConfig:
    rank: int = 16
    alpha_multiplier: int = 2
    dropout: float = 0.05
    target_modules: list[str] = field(default_factory=lambda: TARGET_MODULES)


@dataclass
class AnalysisConfig:
    n_bootstrap: int = 1000
    alpha_ci: float = 0.95
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

---

## C-1: Verify + copy h-e1 artifacts [Complexity: 4]

No new config — reuses `MODELS`, `RANKS`, `SEEDS`, `TrainConfig`, `AnalysisConfig` above unmodified.

### Subtasks [0/0 used]
(within 0-subtask budget — no decomposition)

---

## C-2 to C-4: HotpotQA data pipeline / train-eval / sweep driver [Complexity: 8/10/7]

**Applied**: h-e1 `TrainConfig` reused, `max_length` overridden per PRD FR-1

### Configuration (Python Dataclass)

```python
@dataclass
class Paths:
    results_dir: str = "results"
    figures_dir: str = "figures"
    checkpoint_dir: str = "checkpoints"
    rank_sweep_csv: str = "results/h-c1_rank_sweep.csv"
    optimal_ranks_csv: str = "results/h-c1_optimal_ranks.csv"
    scaling_fit_json: str = "results/h-c1_scaling_fit.json"
    comparison_json: str = "results/h-c1_cross_task_comparison.json"
    dual_plot_png: str = "figures/h-c1_dual_scaling_plot.png"
    h_e1_scaling_fit_json: str = "../h-e1/code/results/h-e1_scaling_fit.json"


@dataclass
class HotpotDataConfig:
    dataset_name: str = "hotpotqa/hotpot_qa"
    dataset_config: str = "distractor"
    max_length: int = 512          # overrides h-e1 TrainConfig.max_length=384 (multi-doc context)
```

Use `TrainConfig(max_length=512)` when instantiating for h-c1 training runs (all other fields default from h-e1).

### Subtasks [0/0 used]
(within 0-subtask budget — no decomposition)

---

## C-5: r_opt + scaling fit (HotpotQA) [Complexity: 3]

No new config — reuses `AnalysisConfig` (n_bootstrap=1000, alpha_ci=0.95) above unmodified, targets `Paths.rank_sweep_csv`.

### Subtasks [0/0 used]

---

## C-6: Cross-task comparison [Complexity: 5]

### Configuration (Python Dataclass)

```python
@dataclass
class ComparisonConfig:
    alpha_diff_threshold: float = 0.15   # PRD FR-10 pass/fail criterion
    require_ci_overlap: bool = True
```

### Subtasks [0/0 used]

---

## C-7: Dual visualization [Complexity: 6]

No new config — reuses `Paths.dual_plot_png` and `ComparisonConfig.alpha_diff_threshold` above.

### Subtasks [0/0 used]

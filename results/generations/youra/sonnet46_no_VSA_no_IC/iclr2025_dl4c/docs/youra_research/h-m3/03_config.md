---
hypothesis_id: h-m3
type: MECHANISM
base_hypothesis: h-m2
generated_at: 2026-08-21
author: yoon303@etri.re.kr
---

# Config: H-M3 — Proxy Temporal Stability

Applied: Standard dataclass with verified H-M2 field names from actual code

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (direct file read — Serena project not active)
**Config Files Found**: `docs/youra_research/h-m2/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

Verified from `docs/youra_research/h-m2/code/config.py`:

```python
# ACTUAL H-M2 fields (verified)
@dataclass
class H_M2Config:
    profiling_json: str = "docs/youra_research/h-e1/results/mbpp_variance_profile.json"
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    mbpp_dataset_id: str = "google-research-datasets/mbpp"
    mbpp_subset: str = "full"
    mbpp_split: str = "train"
    k: int = 50
    seed: int = 42
    learning_rate: float = 5e-7       # H-M3 changes to 1e-6
    num_generations: int = 4
    generation_batch_size: int = 4
    max_steps: int = 50               # H-M3 changes to 200
    beta: float = 0.0
    logging_steps: int = 1
    use_vllm: bool = False
    save_steps: List[int] = [10, 20, 50]
    max_new_tokens: int = 512         # H-M3 renames → max_completion_length = 1024
    exec_timeout: float = 5.0
    gate_checkpoints: List[int] = [10, 20, 50]
    gap_threshold_pp: float = 0.05
    results_dir: str = "docs/youra_research/h-m2/results"
    figures_dir: str = "docs/youra_research/h-m2/figures"
    min_trl_version: str = "0.15.0"
```

**Field name note**: H-M2 uses `max_new_tokens` (int=512). This maps to `max_completion_length` in TRL GRPOConfig. H-M3 config renames this field to `max_completion_length` directly to avoid the mismatch.

---

## A-1: H_M3Config [Complexity: 5, Budget: 5]

Applied: Standard PyTorch/TRL dataclass defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class H_M3Config:
    # Inputs from H-E1
    profiling_json: str = "docs/youra_research/h-e1/results/mbpp_variance_profile.json"

    # Model
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"

    # Dataset
    mbpp_dataset_id: str = "google-research-datasets/mbpp"
    mbpp_subset: str = "full"
    mbpp_split: str = "train"
    k: int = 50
    seed: int = 42

    # GRPO Training — warm-start changes from H-M2
    max_steps: int = 200              # was 50: extended to observe temporal dynamics
    learning_rate: float = 1e-6      # was 5e-7: doubled to ensure nonzero rewards
    max_completion_length: int = 1024 # was max_new_tokens=512: renamed + doubled for richer completions

    # Same as H-M2
    num_generations: int = 4
    generation_batch_size: int = 4
    beta: float = 0.0
    logging_steps: int = 1
    use_vllm: bool = False
    exec_timeout: float = 5.0

    # Gate evaluation
    gate_checkpoints: List[int] = field(default_factory=lambda: [10, 20, 50])
    gap_threshold_pp: float = 0.05

    # Early-stop: check after first N steps if warm-start produced nonzero rewards
    early_stop_check_steps: int = 50  # non-standard: matches H-M2 max_steps for fair comparison point

    # Output
    results_dir: str = "docs/youra_research/h-m3/results"
    figures_dir: str = "docs/youra_research/h-m3/figures"

    min_trl_version: str = "0.15.0"

    def __post_init__(self):
        assert self.k == 50
        assert self.num_generations == self.generation_batch_size == 4
        assert self.logging_steps == 1
        assert self.beta == 0.0
        assert len(self.gate_checkpoints) > 0
        assert self.max_steps >= self.early_stop_check_steps
```

### Hyperparameter Rationale (Warm-Start Changes)

| Param | H-M2 | H-M3 | Rationale |
|-------|------|------|-----------|
| `max_steps` | 50 | 200 | H-M2 cold-started: no signal in 50 steps. 200 gives model time to learn nonzero rewards and enables temporal analysis |
| `learning_rate` | 5e-7 | 1e-6 | Conservative doubling; still in safe range for instruct model fine-tuning. Faster initial reward acquisition |
| `max_completion_length` | 512 | 1024 | Longer completions increase probability of passing test cases; reduces cold-start risk |
| `early_stop_check_steps` | N/A | 50 | Matches H-M2 budget; if still cold at step 50 → same failure mode as H-M2 → early exit |

### Sensitivity Ranges

| Param | Conservative | Default (H-M3) | Aggressive |
|-------|-------------|----------------|------------|
| `learning_rate` | 5e-7 (H-M2) | 1e-6 | 3e-6 |
| `max_completion_length` | 512 | 1024 | 2048 |
| `max_steps` | 100 | 200 | 500 |
| `early_stop_check_steps` | 20 | 50 | 100 |

Different scenario thresholds: if `learning_rate > 3e-6`, risk reward hacking / training instability. If `max_completion_length < 512`, cold-start risk returns.

### Subtasks [2/5 used for A-1]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Write H_M3Config dataclass | Implement config.py with __post_init__ asserts |
| C-1-2 | Write h_m3_config.yaml | YAML file loadable for experiment tracking |

---

## A-5: Extend visualize.py [Complexity: 10, Budget: 2]

Applied: Standard matplotlib figure layout

### C-5-1: Figure Layout — plot_gap_trajectory_200

```python
# Fig 2: gap = frac_rnd - frac_var over all logged steps (up to 200)
# Layout specs:
PLOT_GAP_TRAJECTORY = {
    "figsize": (10, 5),
    "title": "Proxy Stability: Gap Trajectory Over Training Steps",
    "xlabel": "Training Step",
    "ylabel": "Gap (frac_zero_std: random-50 − variance-50)",
    "xlim": (0, 200),           # full warm-start budget on x-axis
    "hline_y": 0.0,             # reference line at gap=0
    "hline_color": "black",
    "hline_linestyle": "--",
    "hline_linewidth": 1.0,
    "fill_condition": "gap < 0",  # red fill when gap negative (variance-50 worse)
    "fill_color": "red",
    "fill_alpha": 0.2,
    "line_color": "steelblue",
    "line_linewidth": 1.5,
    "filename": "gap_trajectory_200.png",
    "dpi": 150,
}
```

Implementation note: use `ax.fill_between(steps, gap_values, 0, where=[g < 0 for g in gap_values], color="red", alpha=0.2)`.

### C-5-2: Figure Layout — plot_gap_retention_bar

```python
# Fig 4: bar chart at steps 10, 20, 50; annotate P2 threshold
PLOT_GAP_RETENTION_BAR = {
    "figsize": (6, 5),
    "title": "Gap at Checkpoints (P2 Retention Threshold: gap_50/gap_10 ≥ 0.5)",
    "xlabel": "Training Step",
    "ylabel": "Gap (frac_zero_std: random-50 − variance-50)",
    "xticks": [10, 20, 50],
    "bar_color": "steelblue",
    "bar_width": 6,
    # P2 threshold annotation: horizontal line at gap_10 * 0.5
    # (computed at runtime, not a fixed y value)
    "p2_hline_color": "orange",
    "p2_hline_linestyle": "--",
    "p2_hline_label": "P2 threshold (gap_50/gap_10 = 0.5)",
    "p2_hline_linewidth": 1.5,
    "annotate_retention_value": True,  # text box: f"gap_retention={gap_retention:.2f}"
    "filename": "gap_retention_bar.png",
    "dpi": 150,
}
```

Implementation note: `p2_line_y = gap_at_10 * 0.5` computed from args; draw only if `gap_at_10 > 0`.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | plot_gap_trajectory_200 layout | 200-step x-axis, gap=0 hline, red fill for gap<0 region |
| C-5-2 | plot_gap_retention_bar layout | Bars at steps 10,20,50 with P2 threshold annotation at gap_10*0.5 |

---

## Experiment YAML Config

```yaml
# h_m3_config.yaml — loadable for experiment tracking
# Load with: import yaml; cfg_dict = yaml.safe_load(open("h_m3_config.yaml"))
# Then: cfg = H_M3Config(**cfg_dict)

hypothesis_id: h-m3
profiling_json: docs/youra_research/h-e1/results/mbpp_variance_profile.json
model_id: deepseek-ai/deepseek-coder-7b-instruct-v1.5
mbpp_dataset_id: google-research-datasets/mbpp
mbpp_subset: full
mbpp_split: train
k: 50
seed: 42

# Warm-start changes from H-M2
max_steps: 200
learning_rate: 1.0e-6
max_completion_length: 1024

# Same as H-M2
num_generations: 4
generation_batch_size: 4
beta: 0.0
logging_steps: 1
use_vllm: false
exec_timeout: 5.0

# Gate evaluation
gate_checkpoints: [10, 20, 50]
gap_threshold_pp: 0.05
early_stop_check_steps: 50

# Output
results_dir: docs/youra_research/h-m3/results
figures_dir: docs/youra_research/h-m3/figures
min_trl_version: "0.15.0"
```

**Validation**: `H_M3Config(**yaml.safe_load(...))` will trigger `__post_init__` asserts. `gate_checkpoints` must be passed as a list — YAML list syntax `[10, 20, 50]` maps correctly to Python list.

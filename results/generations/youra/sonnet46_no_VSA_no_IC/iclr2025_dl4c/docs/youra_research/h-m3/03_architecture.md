---
hypothesis_id: h-m3
type: MECHANISM
base_hypothesis: h-m2
generated_at: 2026-08-21
author: yoon303@etri.re.kr
---

# Architecture: H-M3 — Proxy Temporal Stability

Applied: incremental-extension (config-only changes + analysis extension, max reuse from H-M2)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (direct file read — Serena project not active)
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: H-M2 has 6 modules (config, dataset, reward, train, analyze, visualize, run_experiment). `run_grpo()` accepts `H_M2Config` dataclass and returns `list` (log_history). `analyze.py` has `extract_frac_zero_std()` and `compute_gate_metrics()`. All import via flat `from config import H_M2Config` (no package structure — files run from their own directory with `sys.path.insert`).

---

## File Organization

H-M3 code lives at `docs/youra_research/h-m3/code/`.

- `config.py` — NEW: `H_M3Config` dataclass (warm-start params)
- `dataset.py` — COPY from H-M2 (reuse as-is)
- `reward.py` — COPY from H-M2 (reuse as-is)
- `train.py` — MODIFY from H-M2: add early-stop logic to `run_grpo()`
- `analyze.py` — EXTEND from H-M2: add `compute_gap_trajectory()`, `verify_warm_start_succeeded()`
- `visualize.py` — EXTEND from H-M2: add `plot_gap_trajectory_200()`, `plot_gap_retention_bar()`; update titles to H-M3
- `run_experiment.py` — MODIFY from H-M2: orchestrate warm-start runs + early-stop + new JSON schema

---

## Module Definitions

### H_M3Config (`config.py`)

**Dependencies**: stdlib only

```python
@dataclass
class H_M3Config:
    profiling_json: str = "docs/youra_research/h-e1/results/mbpp_variance_profile.json"
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    mbpp_dataset_id: str = "google-research-datasets/mbpp"
    mbpp_subset: str = "full"
    mbpp_split: str = "train"
    k: int = 50
    seed: int = 42
    # Warm-start changes from H-M2
    max_steps: int = 200          # was 50
    learning_rate: float = 1e-6   # was 5e-7
    max_completion_length: int = 1024  # was 512 (field name change: max_new_tokens→max_completion_length)
    # Same as H-M2
    num_generations: int = 4
    generation_batch_size: int = 4
    beta: float = 0.0
    logging_steps: int = 1
    use_vllm: bool = False
    exec_timeout: float = 5.0
    gate_checkpoints: list = field(default_factory=lambda: [10, 20, 50])
    early_stop_check_steps: int = 50  # check cold-start after first N steps
    results_dir: str = "docs/youra_research/h-m3/results"
    figures_dir: str = "docs/youra_research/h-m3/figures"
    min_trl_version: str = "0.15.0"

    def __post_init__(self): ...
```

---

### dataset.py

COPY from `docs/youra_research/h-m2/code/dataset.py` verbatim.

Key interface (unchanged):
```python
def load_mbpp_subsets(cfg: H_M3Config) -> tuple:
    # returns (variance_50_ds, random_50_ds, variance_50_ids, random_50_ids)
    ...
```

---

### reward.py

COPY from `docs/youra_research/h-m2/code/reward.py` verbatim.

Key interface (unchanged):
```python
def make_execution_reward(timeout: float = 5.0) -> callable: ...
```

---

### train.py (`train.py`)

**Dependencies**: config, reward, transformers, trl

MODIFY from H-M2. Change: add early-stop check after `early_stop_check_steps`; rename `max_new_tokens` → `max_completion_length` in `build_grpo_config`.

```python
def build_grpo_config(cfg: H_M3Config, output_dir: str, condition: str) -> GRPOConfig: ...

def run_grpo(
    cfg: H_M3Config,
    dataset: Dataset,
    output_dir: str,
    condition: str,
) -> tuple[list, bool]:
    """
    Run GRPO with warm-start config. Returns (log_history, early_stopped).
    Early-stops if frac_reward_zero_std == 1.0 for all first early_stop_check_steps steps.
    """
    ...
```

---

### analyze.py (`analyze.py`)

**Dependencies**: config, numpy

EXTEND from H-M2. Keep `extract_frac_zero_std()` and `compute_gate_metrics()` unchanged. Add:

```python
def verify_warm_start_succeeded(
    log_history_var50: list,
    log_history_rnd50: list,
) -> tuple[bool, dict]:
    """Returns (warm_start_ok, {max_reward_var50, max_reward_rnd50})."""
    ...

def compute_gap_trajectory(
    frac_var: list,
    frac_rnd: list,
    log_steps: list[int],
) -> tuple[dict, float, float, float, float]:
    """
    Returns (gap_by_step, gap_at_10, gap_at_20, gap_at_50, gap_retention).
    gap_by_step: {step: frac_rnd[step] - frac_var[step]}
    gap_retention: gap_at_50 / gap_at_10 if gap_at_10 > 0 else 0.0
    """
    ...

def save_results(
    cfg: H_M3Config,
    warm_start_ok: bool,
    gap_by_step: dict,
    gap_at_10: float,
    gap_at_20: float,
    gap_at_50: float,
    gap_retention: float,
    frac_var: list,
    frac_rnd: list,
    variance_50_ids: list,
    random_50_ids: list,
    gate_passed: bool,
    p1_pass: bool,
    p2_pass: bool,
    max_rewards: dict,
) -> None:
    """Write gate_results.json per FR-12 schema."""
    ...
```

---

### visualize.py (`visualize.py`)

**Dependencies**: config, matplotlib, numpy

EXTEND from H-M2. Keep `plot_gate_bar_chart()` (update title to H-M3). Keep `plot_reward_std_histogram()`. Rename/extend:

```python
def plot_gate_bar_chart(gate_metrics: dict, figures_dir: str) -> None: ...  # title → H-M3

def plot_per_condition_curves(frac_var: list, frac_rnd: list, figures_dir: str) -> None:
    """Fig 3: two lines over all logged steps (up to 200). Replaces plot_learning_curves."""
    ...

def plot_gap_trajectory_200(
    gap_by_step: dict,
    figures_dir: str,
) -> None:
    """Fig 2: line plot gap=frac_rnd-frac_var over all steps. Red fill if gap<0."""
    ...

def plot_gap_retention_bar(
    gap_at_10: float,
    gap_at_20: float,
    gap_at_50: float,
    gap_retention: float,
    figures_dir: str,
) -> None:
    """Fig 4: bar at steps 10,20,50 annotated with P2 retention threshold."""
    ...

def generate_all_figures(
    cfg: H_M3Config,
    gate_metrics: dict,
    gap_by_step: dict,
    gap_at_10: float,
    gap_at_20: float,
    gap_at_50: float,
    gap_retention: float,
    frac_var: list,
    frac_rnd: list,
    log_var: list,
    log_rnd: list,
) -> None: ...
```

---

### run_experiment.py (`run_experiment.py`)

**Dependencies**: config, dataset, train, analyze, visualize

MODIFY from H-M2. Orchestrates warm-start runs + early-stop + new analysis flow.

```python
def main(cfg: H_M3Config = None) -> dict: ...

if __name__ == "__main__":
    gate = main()
    sys.exit(0 if gate.get("gate_passed") else 1)
```

Flow:
1. Env validate (TRL version, CUDA, H-E1 JSON)
2. `load_mbpp_subsets(cfg)`
3. `run_grpo(cfg, variance_50_ds, ...)` → `(log_var, early_stopped_var)`
4. `run_grpo(cfg, random_50_ds, ...)` → `(log_rnd, early_stopped_rnd)`
5. `verify_warm_start_succeeded(log_var, log_rnd)` → if False: log EXPLORE, save results, exit 1
6. `extract_frac_zero_std(log_var/rnd)` → `frac_var`, `frac_rnd`
7. `compute_gap_trajectory(...)` → gap metrics
8. `compute_gate_metrics(...)` → checkpoint means (P1 uses per-step gap, not cumulative mean)
9. `save_results(...)`
10. `generate_all_figures(...)`
11. Print gate report

---

## External Dependencies (Base Hypothesis)

| Module | What | File Location |
|--------|------|---------------|
| dataset.py | `load_mbpp_subsets` | `docs/youra_research/h-m2/code/dataset.py` — COPY verbatim |
| reward.py | `make_execution_reward` | `docs/youra_research/h-m2/code/reward.py` — COPY verbatim |

**Import style** (verified from H-M2 actual code): flat imports, no package prefix.
```python
from config import H_M3Config
from dataset import load_mbpp_subsets
from train import run_grpo
from analyze import extract_frac_zero_std, compute_gap_trajectory, verify_warm_start_succeeded, save_results
from visualize import generate_all_figures
```
Run via: `cd docs/youra_research/h-m3/code && python run_experiment.py`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | H_M3Config | New config dataclass with warm-start params | 5 | 2+1+1+1 |
| A-2 | Copy dataset+reward | Copy H-M2 dataset.py and reward.py verbatim | 3 | 1+1+1+0 |
| A-3 | Modify train.py | Add early-stop logic; fix max_completion_length field name | 8 | 2+2+2+2 |
| A-4 | Extend analyze.py | Add verify_warm_start_succeeded, compute_gap_trajectory, update save_results | 10 | 3+2+3+2 |
| A-5 | Extend visualize.py | Add 3 new plot functions (gap_trajectory_200, gap_retention_bar, per_condition_curves); update titles | 10 | 3+1+3+3 |
| A-6 | Modify run_experiment.py | New orchestration flow: warm-start check, EXPLORE early-exit, new analysis calls | 11 | 3+2+3+3 |
| A-7 | Integration test | End-to-end smoke test with mock log_history; verify gate JSON schema | 8 | 2+2+2+2 |
| A-8 | Full experiment run | Execute both GRPO conditions on H100; validate warm_start_ok; report gate | 14 | 3+3+4+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-8], Medium(9-13): [A-4, A-5, A-6], Low(4-8): [A-1, A-2, A-3, A-7]

---

## Notes

- `compute_gate_metrics()` in H-M2 computes **cumulative mean** frac over 0..N steps. H-M3 PRD requires **per-step** gap at exact steps 10, 20, 50. `compute_gap_trajectory()` handles this; `compute_gate_metrics()` kept for backward-compatible bar chart in Fig 1.
- `max_new_tokens` in H-M2 config maps to `max_completion_length` in `GRPOConfig`. H-M3 config field named `max_completion_length` directly to match TRL API.
- Early-stop: after first `early_stop_check_steps` (=50) logged steps, if `frac_reward_zero_std == 1.0` for all entries → call `verify_warm_start_succeeded` → if False, save partial results, print EXPLORE finding, `sys.exit(1)`.

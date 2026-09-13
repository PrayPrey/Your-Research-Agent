# Architecture: H-M1

**Hypothesis**: Ratio vs Binary Reward Policy Target Shift in GRPO Training
**Type**: MECHANISM (INCREMENTAL extending H-E1)
**Date**: 2026-08-31

Applied: GRPO-trl flat-module pattern with sys.path sibling imports

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (H-E1)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 has flat structure — `config.py`, `data.py`, `rewards.py`, `train.py`, `evaluate.py`, `analyze.py`. Imports via `sys.path.insert(0, os.path.dirname(__file__))` pattern. `make_reward_fn` factory in rewards.py wraps binary/ratio functions for trl GRPOTrainer. `GradNormCallback` logs grad_norm, mean_reward, std_reward to CSV.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| GRPOConfig | `from config import GRPOConfig, load_config` | `h-e1/code/config.py` |
| build_dataset | `from data import build_dataset` | `h-e1/code/data.py` |
| make_reward_fn | `from rewards import make_reward_fn` | `h-e1/code/rewards.py` |
| binary_reward | `from rewards import binary_reward` | `h-e1/code/rewards.py` |
| ratio_reward | `from rewards import ratio_reward` | `h-e1/code/rewards.py` |
| execute_code | `from rewards import execute_code` | `h-e1/code/rewards.py` |
| load_checkpoint | `from evaluate import load_checkpoint` | `h-e1/code/evaluate.py` |
| generate_completion | `from evaluate import generate_completion` | `h-e1/code/evaluate.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

---

## File Structure

- `docs/youra_research/h-m1/code/`
  - `config.py` — HM1Config extending H-E1 GRPOConfig
  - `train.py` — 1000-step training with multi-checkpoint save
  - `eval_humaneval.py` — HumanEval pass@1 over 164 problems
  - `eval_mbpp.py` — MBPP pass@1 over 374 problems
  - `eval_apps_allpass.py` — APPS validation all-pass rate (500 problems)
  - `analyze.py` — Bootstrap CI + verify_h_m1_mechanism
  - `visualize.py` — 4 mandatory figures
  - `run_experiment.py` — End-to-end orchestrator

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: h-e1/code/config.py

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
from config import GRPOConfig as BaseGRPOConfig

class HM1Config(BaseGRPOConfig):
    def __init__(self): ...
    # num_train_steps: int = 1000
    # checkpoint_steps: list[int] = [200, 400, 600, 800, 1000]
    # humaneval_eval_steps: list[int] = [200, 400, 600, 800, 1000]
    # mbpp_eval_steps: list[int] = [1000]
    # apps_allpass_eval_steps: list[int] = [1000]
    # apps_val_size: int = 500
    # bootstrap_n: int = 1000

def load_hm1_config() -> HM1Config: ...
```

---

### Train (`code/train.py`)

**Dependencies**: HM1Config, h-e1 data.py, h-e1 rewards.py, h-e1 train.py (GradNormCallback pattern)

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
from data import build_dataset
from rewards import make_reward_fn

class FractionPartialCallback:
    """Logs fraction of rewards in (0,1) every 50 steps. Alerts if < 0.05 at step 200."""
    def __init__(self, output_csv: str, condition: str) -> None: ...
    def on_log(self, args, state, control, logs=None, **kwargs) -> None: ...

def run_training_condition(
    condition: str,        # "binary" | "ratio"
    config: HM1Config,
    output_dir: str,
) -> dict: ...
# Returns: {step: checkpoint_path} for each checkpoint_step
# Saves: training_log_{condition}.csv with columns:
#   global_step, grad_norm, mean_reward, std_reward, fraction_partial_correct
```

---

### HumanEval Evaluator (`code/eval_humaneval.py`)

**Dependencies**: h-e1 evaluate.py

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
from evaluate import load_checkpoint, generate_completion

def evaluate_humaneval(
    checkpoint_path: str,
    max_new_tokens: int = 512,
) -> float: ...
# Returns: pass@1 float [0,1] over 164 HumanEval problems
# Dataset: load_dataset("openai_humaneval", split="test")
# Execution: evaluate.load("code_eval"), k=[1], num_workers=4

def batch_evaluate_humaneval(
    checkpoint_paths: dict,   # {step: checkpoint_path}
    condition: str,
) -> dict: ...
# Returns: {step: pass@1}
```

---

### MBPP Evaluator (`code/eval_mbpp.py`)

**Dependencies**: h-e1 evaluate.py

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
from evaluate import load_checkpoint, generate_completion

def evaluate_mbpp(
    checkpoint_path: str,
    max_new_tokens: int = 512,
) -> float: ...
# Returns: pass@1 float over 374 MBPP test problems
# Dataset: load_dataset("google-research-datasets/mbpp", split="test")
```

---

### APPS All-Pass Evaluator (`code/eval_apps_allpass.py`)

**Dependencies**: h-e1 rewards.py (execute_code), h-e1 evaluate.py

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
from rewards import execute_code
from evaluate import load_checkpoint, generate_completion

def evaluate_apps_allpass(
    checkpoint_path: str,
    n_problems: int = 500,
    max_new_tokens: int = 512,
) -> float: ...
# Returns: fraction of problems where ALL test cases pass
# Dataset: codeparrot/apps split="validation", stratified first n_problems

def get_per_problem_pass_rates(
    checkpoint_path: str,
    n_problems: int = 500,
    max_new_tokens: int = 512,
) -> list[float]: ...
# Returns: [k/n per problem] — used in Figure 3 and Figure 4
```

---

### Statistical Analyzer (`code/analyze.py`)

**Dependencies**: numpy, scipy

```python
import numpy as np

def bootstrap_ci(
    ratio_problem_scores: list[float],
    binary_problem_scores: list[float],
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
) -> tuple[float, float, float]: ...
# Returns: (mean_gap, ci_lower, ci_upper)
# ponytail: paired bootstrap on per-problem scores; upgrade to permutation test if n<30

def verify_h_m1_mechanism(
    ratio_humaneval_pass1: float,
    binary_humaneval_pass1: float,
    ratio_apps_allpass: float,
    binary_apps_allpass: float,
    bootstrap_ci_lower: float,
) -> dict: ...
# Returns: {gate_satisfied, p1_humaneval_gap, p2_policy_shift,
#           mechanism_confirmed, result: "GATE_SATISFIED"|"GATE_FAILED"}

def check_ratio_degeneracy(rewards_per_group: list[float]) -> bool: ...
# Returns True if all rewards in {0.0, 1.0} (ratio degenerated to binary)

def check_gradient_health(grad_norm: float, threshold: float = 10.0) -> bool: ...
# Returns True if healthy (grad_norm < threshold)

def compile_results(
    humaneval_curves: dict,    # {condition: {step: pass@1}}
    mbpp_results: dict,        # {condition: pass@1}
    apps_allpass: dict,        # {condition: allpass_rate}
    per_problem_rates: dict,   # {condition: [float]}
    mechanism_result: dict,
) -> dict: ...
# Returns: merged results dict for JSON serialization
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: matplotlib, compile_results output

```python
import matplotlib.pyplot as plt

def plot_gate_metrics(
    results: dict,
    ci_lower: float,
    ci_upper: float,
    output_path: str,
) -> None: ...
# Figure 1: side-by-side bars HumanEval pass@1 + APPS all-pass, both conditions
# Error bars: 95% CI on HumanEval gap

def plot_learning_curves(
    humaneval_curves: dict,   # {condition: {step: pass@1}}
    output_path: str,
) -> None: ...
# Figure 2: HumanEval pass@1 vs step [0,200,400,600,800,1000], both conditions

def plot_pass_rate_distribution(
    per_problem_rates: dict,  # {condition: [float]}
    output_path: str,
) -> None: ...
# Figure 3: histogram of per-problem k/n pass rates — binary vs ratio

def plot_policy_scatter(
    binary_rates: list[float],
    ratio_rates: list[float],
    output_path: str,
) -> None: ...
# Figure 4: scatter (binary_pass_rate, ratio_pass_rate) per APPS-val problem

def save_all_figures(results: dict, figures_dir: str) -> None: ...
# Calls all four plot functions, saves to figures_dir
```

---

### Orchestrator (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
# CLI: --conditions [binary ratio], --resume_from_step INT, --output_dir STR
# Pipeline:
#   1. load_hm1_config()
#   2. run_training_condition("binary", ...) -> binary_checkpoints
#   3. run_training_condition("ratio", ...) -> ratio_checkpoints
#   4. batch_evaluate_humaneval(binary_checkpoints, "binary")
#   5. batch_evaluate_humaneval(ratio_checkpoints, "ratio")
#   6. evaluate_mbpp for both at step 1000
#   7. evaluate_apps_allpass + get_per_problem_pass_rates for both at step 1000
#   8. bootstrap_ci on per-problem HumanEval scores
#   9. verify_h_m1_mechanism(...)
#  10. compile_results(...)
#  11. save_all_figures(results, "docs/youra_research/h-m1/figures/")
#  12. save results to results/h_m1_results.json

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config | HM1Config extending BaseGRPOConfig; add checkpoint_steps, eval schedules, apps_val_size, bootstrap_n | 6 | 1+2+1+2 |
| A-2 | Training Loop | Extend H-E1 train.py to 1000 steps; FractionPartialCallback; checkpoint save at [200,400,600,800,1000]; training_log CSV | 12 | 3+3+3+3 |
| A-3 | HumanEval Evaluator | eval_humaneval.py: 164 problems greedy decode, code_eval metric; batch_evaluate_humaneval over checkpoint dict | 11 | 3+2+3+3 |
| A-4 | MBPP Evaluator | eval_mbpp.py: 374 problems greedy decode, pass@1; reuses generate_completion from H-E1 | 8 | 2+2+2+2 |
| A-5 | APPS All-Pass Evaluator | eval_apps_allpass.py: 500 stratified APPS-val problems; all-pass fraction + per-problem k/n rates for figures | 12 | 3+2+4+3 |
| A-6 | Statistical Analyzer | analyze.py: bootstrap_ci, verify_h_m1_mechanism, failure checks (degeneracy, grad health), compile_results | 13 | 3+2+5+3 |
| A-7 | Visualizer | visualize.py: 4 required figures (gate metrics bar, learning curves, distribution histogram, policy scatter) | 10 | 2+2+3+3 |
| A-8 | Orchestrator | run_experiment.py: end-to-end pipeline; CLI with --resume_from_step; results JSON output | 11 | 2+4+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-5, A-6, A-7, A-8], Low(4-8): [A-1, A-4]

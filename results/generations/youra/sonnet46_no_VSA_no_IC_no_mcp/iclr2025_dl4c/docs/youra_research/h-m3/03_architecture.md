# Architecture: h-m3 — RLEF-Binary vs RLEF-Fraction Comparative Study

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Type:** MECHANISM (INCREMENTAL, base: h-m2 / h-E1)

Applied: reuse-first incremental extension pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-E1 + h-m2)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/` and `docs/youra_research/h-m2/code/`
**Findings**: h-E1 has `reward.py` with `fraction_reward_fn`, `config.py` with `TrainingConfig/GRPOConfig`, `train_rlef.py`, `evaluate.py`, `data_utils.py`. h-m2 has `difficulty_reward_callback.py` with `DifficultyRewardCallback` and `verify_mechanism_activated`. h-m3 adds only `reward_binary.py` + `train_rlef_binary.py` + `compare.py`.

---

## File Organization

```
docs/youra_research/h-m3/code/
├── reward_binary.py          # NEW: binary_reward_fn + verify_reward_formulation_active
├── train_rlef_binary.py      # NEW: GRPO training run with binary reward
├── compare.py                # NEW: multi-benchmark evaluation + bootstrap test + figures
├── config.py                 # NEW: h-m3 config (inherits h-E1 hyperparams, override paths)
└── run_experiment.sh         # NEW: orchestration script

docs/youra_research/h-m3/figures/  # output directory
```

**REUSED (no copy — sys.path import from h-E1):**
- `h-e1/code/reward.py` → `fraction_reward_fn`
- `h-e1/code/data_utils.py` → APPS loading
- `h-e1/code/evaluate.py` → benchmark evaluation harness
- `h-e1/code/grpo_trainer.py` → GRPOTrainer wrapper
- `h-e1/code/config.py` → TrainingConfig, GRPOConfig

---

## Module Definitions

### BinaryReward (`reward_binary.py`)

**Dependencies**: h-e1/reward.py (`_execute_code`)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "h-e1" / "code"))

from reward import _execute_code

def binary_reward_fn(
    completions: list[str],
    prompts: list[str],
    metadata: list[dict],
    **kwargs,
) -> list[float]: ...
    # 1.0 if all test cases pass, else 0.0

def verify_reward_formulation_active(
    fraction_rewards: list[float],
    binary_rewards: list[float],
    threshold: float = 0.01,
) -> tuple[bool, dict]: ...
    # returns (activated, indicators) — log every 50 steps
```

---

### BinaryTrainer (`train_rlef_binary.py`)

**Dependencies**: h-e1/grpo_trainer.py, h-e1/data_utils.py, h-e1/config.py, reward_binary.py, config.py

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "h-e1" / "code"))

from grpo_trainer import build_grpo_trainer
from data_utils import load_apps_dataset
from reward import fraction_reward_fn
from reward_binary import binary_reward_fn, verify_reward_formulation_active
from config import H_M3_Config

def train_rlef_binary(cfg: H_M3_Config) -> Path:
    """Train RLEF-Binary from SFT checkpoint; returns checkpoint path."""
    ...

if __name__ == "__main__":
    train_rlef_binary(H_M3_Config())
```

---

### CompareEvaluator (`compare.py`)

**Dependencies**: h-e1/evaluate.py, config.py

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "h-e1" / "code"))

from evaluate import run_bigcode_eval, run_lcb_eval

def evaluate_all_models(
    sft_path: str,
    fraction_path: str,
    binary_path: str,
    cfg,
) -> dict[str, dict[str, float]]:
    """Returns {model: {benchmark: pass@1}}."""
    ...

def bootstrap_delta_test(
    fraction_results: list[float],
    binary_results: list[float],
    sft_results: list[float],
    n_bootstrap: int = 10000,
    seed: int = 42,
) -> tuple[float, float, list[float]]:
    """Returns (p_value, observed_diff, bootstrap_diffs)."""
    ...

def generate_figures(results: dict, output_dir: Path) -> None:
    """Generates all 5 required figures to output_dir."""
    ...

if __name__ == "__main__":
    ...
```

---

### Config (`config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass
from pathlib import Path

H_E1_CODE = Path(__file__).parents[2] / "h-e1" / "code"

@dataclass
class H_M3_Config:
    # Model
    sft_checkpoint: str = str(H_E1_CODE / "checkpoints" / "sft")
    fraction_checkpoint: str = str(H_E1_CODE / "checkpoints" / "rlef_fraction")
    binary_checkpoint_dir: str = "checkpoints/rlef_binary"
    # Training (must match h-E1 RLEF-Fraction exactly)
    lr: float = 1e-6
    batch_size: int = 4
    grad_accum: int = 4
    num_generations: int = 8
    max_new_tokens: int = 512
    warmup_steps: int = 100
    seed: int = 42
    # Monitoring
    verify_interval_steps: int = 50
    checkpoint_interval_steps: int = 250
    # Output
    figures_dir: str = "docs/youra_research/h-m3/figures"
    results_dir: str = "results"
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| fraction_reward_fn | `from reward import fraction_reward_fn` | `h-e1/code/reward.py` |
| _execute_code | `from reward import _execute_code` | `h-e1/code/reward.py` |
| load_apps_dataset | `from data_utils import load_apps_dataset` | `h-e1/code/data_utils.py` |
| run_bigcode_eval | `from evaluate import run_bigcode_eval` | `h-e1/code/evaluate.py` |
| run_lcb_eval | `from evaluate import run_lcb_eval` | `h-e1/code/evaluate.py` |
| build_grpo_trainer | `from grpo_trainer import build_grpo_trainer` | `h-e1/code/grpo_trainer.py` |
| TrainingConfig | `from config import TrainingConfig` | `h-e1/code/config.py` |
| GRPOConfig | `from config import GRPOConfig` | `h-e1/code/config.py` |
| DifficultyRewardCallback | `from difficulty_reward_callback import DifficultyRewardCallback` | `h-m2/code/difficulty_reward_callback.py` |

**Verified from**: `docs/youra_research/h-e1/code/` and `docs/youra_research/h-m2/code/` (actual implementations)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & scaffold | Create h-m3/code/, config.py, verify h-E1 checkpoint paths exist | 5 | 1+1+1+2 |
| A-2 | Binary reward function | Implement binary_reward_fn reusing _execute_code from h-E1 | 8 | 2+2+2+2 |
| A-3 | Mechanism activation verifier | verify_reward_formulation_active + per-50-step logging in training loop | 7 | 2+1+2+2 |
| A-4 | RLEF-Binary training run | train_rlef_binary.py wiring GRPOTrainer with binary_reward_fn; checkpoint every 250 steps | 12 | 3+3+3+3 |
| A-5 | Multi-benchmark evaluation | evaluate_all_models() calling bigcode-harness + LCB harness for 3 models × 5 benchmarks | 13 | 3+3+3+4 |
| A-6 | Bootstrap hypothesis test | bootstrap_delta_test() for Δ_Fraction > Δ_Binary at LCB-Hard (p < 0.05) | 9 | 2+2+3+2 |
| A-7 | Figures | generate_figures(): bar chart + reward trajectory + heatmap + difficulty interaction + nonzero histogram | 10 | 3+1+3+3 |
| A-8 | Orchestration & null result doc | run_experiment.sh + results summary with mechanism analysis for EXPLORE path | 7 | 2+1+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-6, A-7], Low(4-8): [A-1, A-2, A-3, A-8]

---
title: "Architecture: H-M2 — RLEF-Fraction Non-Zero Reward Signal at Hard Difficulty"
hypothesis_id: H-M2
hypothesis_type: MECHANISM
date: "2026-08-26"
author: yoon303@ust.ac.kr
---

Applied: TRL TrainerCallback reward monitoring pattern (web knowledge fallback)

# Architecture: H-M2

## Executive Summary

H-M2 is a **post-hoc log analysis**, not a new training pipeline. The H-E1 `SimpleGRPOTrainer` already logs per-step rewards by difficulty bucket to `logs/reward_monitoring.jsonl` (see `grpo_trainer.py` lines 259–267). No re-training or callback injection is needed.

New work = two files only:
- `difficulty_reward_callback.py` — `DifficultyRewardCallback` (kept for future live-callback use + TRL version check logic)
- `analyze_reward_fractions.py` — reads H-E1 JSONL logs, computes non-zero fractions, emits JSON + 4 figures

The H-E1 training script (`train_rlef.py`) is **not modified** — its logs already contain what H-M2 needs.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Patterns found from actual H-E1 code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: `SimpleGRPOTrainer.train()` already accumulates rewards by difficulty (`intro`, `interview`, `competition`) and writes per-step JSONL to `logs/reward_monitoring.jsonl`. Fields logged: `step`, `intro_reward`, `interview_reward`, `competition_reward`. The existing `RewardMonitorCallback` in `train_rlef.py` is dead code (trainer is not TRL GRPOTrainer). H-M2 analysis is purely post-hoc against the existing log file.

**Critical note**: H-E1 uses difficulty keys `"intro"` (not `"introductory"`). Analysis script must use `"intro"` to match.

---

## Module Structure

### DifficultyRewardCallback (`code/difficulty_reward_callback.py`)

**Dependencies**: transformers, numpy, collections

```python
from collections import defaultdict
from transformers import TrainerCallback, TrainerState, TrainerControl
import numpy as np

class DifficultyRewardCallback(TrainerCallback):
    """Live callback — use only if re-running training with TRL >= 0.7."""
    def __init__(self, difficulty_field: str = "difficulty"): ...
    def on_step_end(self, args, state: TrainerState, control: TrainerControl,
                    rewards=None, metadata=None, **kwargs) -> None: ...
    def compute_fractions(self) -> dict[str, float]: ...
    def log_summary(self) -> dict[str, float]: ...

def verify_trl_version() -> bool:
    """Returns True if trl >= 0.7 (live callback viable).""" ...

def verify_mechanism_activated(callback: DifficultyRewardCallback) -> tuple[bool, dict]: ...
```

### RewardFractionAnalyzer (`code/analyze_reward_fractions.py`)

**Dependencies**: json, pathlib, numpy, matplotlib

```python
def load_reward_log(log_path: str) -> list[dict]: ...
    # Reads logs/reward_monitoring.jsonl; each record has step + {intro,interview,competition}_reward

def compute_nonzero_fractions(records: list[dict], threshold: float = 0.0) -> dict[str, float]:
    # Returns {"intro": float, "interview": float, "competition": float}
    # nonzero = reward > threshold (reward is mean fraction per step, so >0 means any test passed) ...

def compute_step_series(records: list[dict]) -> dict[str, list]:
    # Returns {"steps": [...], "intro": [...], "interview": [...], "competition": [...]} ...

def save_results(fractions: dict, counts: dict, output_path: str) -> None:
    # Writes reward_fractions.json with gate_result, monotonicity_holds ...

def plot_bar_chart(fractions: dict, output_dir: str) -> None:
    # Figure 1: bar chart per bucket vs 0.10 threshold line ...

def plot_step_series(series: dict, output_dir: str) -> None:
    # Figure 2: non-zero fraction vs training step, 3 curves ...

def plot_reward_histogram(records: list[dict], output_dir: str) -> None:
    # Figure 3: reward distribution histogram per bucket ...

def plot_correlation(fractions: dict, output_dir: str) -> None:
    # Figure 4: difficulty bucket index vs mean fraction scatter ...

def main(log_path: str, results_dir: str, figures_dir: str) -> None: ...

if __name__ == "__main__":
    main(
        log_path="../../h-e1/code/logs/reward_monitoring.jsonl",
        results_dir="../results/",
        figures_dir="../figures/",
    ) ...
```

---

## File Organization

```
docs/youra_research/h-m2/
  code/
    difficulty_reward_callback.py   # new — live callback + verify utils
    analyze_reward_fractions.py     # new — post-hoc analysis + figures
  results/
    reward_fractions.json           # output
  figures/
    fig1_nonzero_fraction_bar.png
    fig2_nonzero_fraction_step.png
    fig3_reward_histogram.png
    fig4_correlation_scatter.png
```

H-E1 files (read-only, not modified):
```
docs/youra_research/h-e1/code/
  grpo_trainer.py          # SimpleGRPOTrainer — already logs by difficulty
  train_rlef.py            # training entry point — not modified
  logs/
    reward_monitoring.jsonl  # PRIMARY INPUT for H-M2 analysis
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| SimpleGRPOTrainer | `sys.path` + `from grpo_trainer import SimpleGRPOTrainer` | `h-e1/code/grpo_trainer.py` |
| fraction_reward_fn | `from reward import fraction_reward_fn` | `h-e1/code/reward.py` |
| load_apps_train | `from data_utils import load_apps_train` | `h-e1/code/data_utils.py` |

**Note**: H-M2 does NOT import these — analysis is post-hoc from JSONL. Listed for reference only.

**Verified from**: `docs/youra_research/h-e1/code/` actual implementation.

**Log file input**: `docs/youra_research/h-e1/code/logs/reward_monitoring.jsonl`
- Format: `{"step": int, "intro_reward": float|null, "interview_reward": float|null, "competition_reward": float|null}`
- Note: Keys use `intro` not `introductory` — match exactly in analysis script.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Verify H-E1 logs | Check `reward_monitoring.jsonl` exists and has competition records | 4 | 1+1+1+1 |
| A-2 | Implement DifficultyRewardCallback | TRL callback class + `verify_mechanism_activated` + TRL version check | 8 | 2+2+2+2 |
| A-3 | Implement `load_reward_log` + `compute_nonzero_fractions` | Parse JSONL, compute per-bucket fractions, detect non-zero | 7 | 2+1+2+2 |
| A-4 | Implement `save_results` | Write `reward_fractions.json` with gate result + monotonicity | 5 | 1+1+1+2 |
| A-5 | Figure 1 — bar chart | Non-zero fraction per bucket vs 0.10 threshold line | 6 | 1+1+2+2 |
| A-6 | Figures 2–4 — step series, histogram, correlation | Three additional diagnostic figures | 8 | 2+1+3+2 |
| A-7 | Integration test + gate assertion | Run `analyze_reward_fractions.py`, assert `competition > 0.10` | 5 | 1+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7]

**Total complexity**: 43/140

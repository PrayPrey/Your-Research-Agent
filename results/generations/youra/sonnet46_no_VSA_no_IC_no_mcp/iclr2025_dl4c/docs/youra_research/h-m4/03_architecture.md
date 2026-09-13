# Architecture: h-m4
# RLEF-Fraction Monotonic Difficulty Scaling + 1.3B Scale Sanity Check

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Type:** MECHANISM (INCREMENTAL from h-m3/h-e1)

Applied: dataclass-config pattern (from h-e1/config.py)
Applied: sys.path injection for cross-hypothesis imports (from h-m3/config.py)
Applied: bootstrap Bernoulli simulation for point-estimate CI (from h-m3/compare.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental from h-e1 + h-m3)
**Status**: patterns found from base code (Glob + Read used; Serena MCP unavailable)
**Analyzed Path**: `docs/youra_research/h-e1/code/` and `docs/youra_research/h-m3/code/`
**Findings**: h-e1 has `reward.py::fraction_reward_fn(completions, prompts, metadata)` — actual signature differs from PRD pseudo-code (takes `metadata` dict with `test_cases`, not `problems` dict with `input_output`). h-m3/compare.py has `generate_figures`, `bootstrap_delta_test`, `evaluate_all_models`, and `save_results_csv` — all reusable as patterns. h-e1/config.py uses nested dataclasses; h-m3/config.py uses flat H_M3_Config dataclass.

---

## File Organization

```
docs/youra_research/h-m4/
  code/
    config.py          # H_M4_Config dataclass (new, minimal)
    reanalyze.py       # 7B re-analysis: load h-e1 deltas, bootstrap pseudo-groups, JT test
    train_1_3b.py      # 1.3B SFT + RLEF-Fraction training (inherits h-e1 reward.py)
    evaluate_1_3b.py   # 1.3B multi-benchmark evaluation (wraps bigcode + LCB)
    analyze.py         # JT test, verify_monotonicity, delta_ratio, visualizations
    run_experiment.py  # Orchestration: calls all modules in order
  figures/             # Output figures (4 required)
  results/             # JSON results output
```

**Total new files: 6** (all minimal; maximum reuse from h-e1 via sys.path injection)

---

## External Dependencies (Base Hypothesis)

### Module Paths (Verified from Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| fraction_reward_fn | `sys.path.insert(0, H_E1_CODE); from reward import fraction_reward_fn` | `h-e1/code/reward.py` |
| TrainingConfig | `from config import TrainingConfig, GRPOConfig, ExperimentConfig` | `h-e1/code/config.py` |
| DATA_CONFIG | `from config import DATA_CONFIG, EVAL_CONFIG` | `h-e1/code/config.py` |
| generate_figures (pattern) | Reference only — h-m4 has own generate_figures | `h-m3/code/compare.py` |

**h-e1 result files:**
| Data | Path |
|------|------|
| Experiment results JSON | `docs/youra_research/h-e1/code/results/h-e1/experiment_results.json` |
| Validation report | `docs/youra_research/h-e1/04_validation.md` |
| SFT checkpoint | `docs/youra_research/h-e1/code/checkpoints/sft_baseline/` |
| RLEF-Fraction checkpoint | `docs/youra_research/h-e1/code/checkpoints/rlef_fraction/` |

**Verified from**: `docs/youra_research/h-e1/code/` and `docs/youra_research/h-m3/code/`

---

## Module Definitions

### H_M4_Config (`code/config.py`)

**Dependencies**: none (stdlib dataclasses only)

```python
import sys
from dataclasses import dataclass
from pathlib import Path

H_E1_CODE = Path(__file__).parents[3] / "h-e1" / "code"
if str(H_E1_CODE) not in sys.path:
    sys.path.insert(0, str(H_E1_CODE))

@dataclass
class H_M4_Config:
    # 1.3B model
    model_name_1_3b: str = "deepseek-ai/deepseek-coder-1.3b-base"
    sft_1_3b_dir: str = "checkpoints/sft_1_3b"
    rlef_1_3b_dir: str = "checkpoints/rlef_fraction_1_3b"

    # 7B checkpoints (inherited from h-e1)
    sft_7b_checkpoint: str = str(H_E1_CODE / "checkpoints" / "sft_baseline")
    rlef_fraction_7b_checkpoint: str = str(H_E1_CODE / "checkpoints" / "rlef_fraction")
    he1_results_json: str = str(H_E1_CODE / "results" / "h-e1" / "experiment_results.json")

    # SFT 1.3B training
    sft_lr: float = 2e-5
    sft_batch_size: int = 8
    sft_grad_accum: int = 4
    sft_epochs: int = 3
    sft_max_length: int = 2048
    sft_warmup_ratio: float = 0.1

    # RLEF 1.3B training (GRPO)
    rlef_lr: float = 1e-5
    rlef_batch_size: int = 4
    rlef_grad_accum: int = 8
    rlef_epochs: int = 3
    num_generations: int = 8
    max_prompt_length: int = 512
    max_completion_length: int = 1024
    max_new_tokens: int = 512
    warmup_ratio: float = 0.1

    # Evaluation
    n_samples: int = 20
    temperature: float = 0.2
    lcb_release: str = "release_v4"

    # Statistical
    n_bootstrap: int = 5000
    bootstrap_seed: int = 1
    seed: int = 1

    # Output
    figures_dir: str = str(Path(__file__).parents[1] / "figures")
    results_dir: str = str(Path(__file__).parent / "results")
    logs_dir: str = str(Path(__file__).parent / "logs")
```

---

### ReanalyzeModule (`code/reanalyze.py`)

**Dependencies**: H_M4_Config, h-e1 results JSON

```python
import json
import numpy as np
from pathlib import Path
from config import H_M4_Config

BENCHMARK_ORDER = ["humaneval", "mbpp", "lcb_easy", "lcb_medium", "lcb_hard"]

def load_he1_delta_values(cfg: H_M4_Config) -> dict[str, float]:
    """Load Δ(RLEF-Fraction, SFT) per benchmark from h-e1 results JSON.
    Returns: {"humaneval": Δ, "mbpp": Δ, "lcb_easy": Δ, "lcb_medium": Δ, "lcb_hard": Δ}
    """
    ...

def bootstrap_pseudo_groups(
    delta_point: float,
    n_problems: int,
    pass_rate: float,
    n_bootstrap: int = 5000,
    seed: int = 1,
) -> list[float]:
    """Bootstrap Bernoulli samples to construct pseudo-group distribution for JT test.
    Returns list of bootstrapped Δ estimates (length n_bootstrap).
    """
    ...

def build_jt_groups(
    deltas_7b: dict[str, float],
    pass_rates_sft: dict[str, float],
    problem_counts: dict[str, int],
    cfg: H_M4_Config,
) -> list[list[float]]:
    """Construct 5 pseudo-group distributions (one per benchmark) for JT test.
    Returns list of 5 lists, ordered by difficulty.
    """
    ...
```

---

### Train1_3B (`code/train_1_3b.py`)

**Dependencies**: H_M4_Config, h-e1 reward.py (fraction_reward_fn)

```python
import sys
from pathlib import Path
from config import H_M4_Config

# fraction_reward_fn imported via sys.path injection at module level

def train_sft_1_3b(cfg: H_M4_Config) -> str:
    """SFT fine-tune deepseek-coder-1.3b-base on APPS train split.
    Returns path to saved checkpoint.
    """
    ...

def train_rlef_1_3b(cfg: H_M4_Config, sft_checkpoint: str) -> str:
    """GRPO fine-tune 1.3B SFT checkpoint with fraction_reward_fn.
    Logs verify_fraction_reward_active every 50 steps.
    Returns path to saved checkpoint.
    """
    ...

def verify_fraction_reward_active(
    rewards: list[float],
    threshold: float = 0.01,
) -> tuple[bool, dict]:
    """Returns (activated: bool, stats: dict) with mean_reward, nonzero_fraction."""
    ...
```

---

### Evaluate1_3B (`code/evaluate_1_3b.py`)

**Dependencies**: H_M4_Config

```python
import json
import subprocess
from pathlib import Path
from config import H_M4_Config

def run_bigcode_eval(
    checkpoint_path: str,
    model_tag: str,
    cfg: H_M4_Config,
) -> dict[str, float]:
    """Run bigcode-evaluation-harness for HumanEval + MBPP.
    Returns {"humaneval": pass@1, "mbpp": pass@1}.
    """
    ...

def run_lcb_eval(
    checkpoint_path: str,
    model_tag: str,
    cfg: H_M4_Config,
) -> dict[str, float]:
    """Run LiveCodeBench harness (release_v4) for Easy/Medium/Hard.
    Returns {"lcb_easy": pass@1, "lcb_medium": pass@1, "lcb_hard": pass@1}.
    """
    ...

def evaluate_model(
    checkpoint_path: str,
    model_tag: str,
    cfg: H_M4_Config,
) -> dict[str, float]:
    """Run all 5 benchmarks. Returns merged dict with all 5 keys."""
    ...
```

---

### Analyze (`code/analyze.py`)

**Dependencies**: H_M4_Config, scipy, numpy, matplotlib, seaborn

```python
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu, norm
from config import H_M4_Config

BENCHMARK_ORDER = ["humaneval", "mbpp", "lcb_easy", "lcb_medium", "lcb_hard"]
DIFFICULTY_LABEL = {
    "humaneval": "HumanEval", "mbpp": "MBPP",
    "lcb_easy": "LCB-Easy", "lcb_medium": "LCB-Med", "lcb_hard": "LCB-Hard",
}

def jonckheere_terpstra(
    groups: list[list[float]],
) -> tuple[float, float]:
    """JT test via pairwise Mann-Whitney U sum. Returns (z_stat, p_value)."""
    ...

def verify_monotonicity(
    deltas: dict[str, float],
) -> tuple[bool, list[float]]:
    """Check weak non-decreasing trend. Returns (is_monotone, ordered_deltas)."""
    ...

def compute_delta_ratio_1_3b(
    rlef_results: dict[str, float],
    sft_results: dict[str, float],
) -> tuple[float, dict[str, float]]:
    """Returns (delta_lcb_hard / delta_humaneval, full_delta_dict)."""
    ...

def bootstrap_ci(
    pass_rate: float,
    n_problems: int,
    n_bootstrap: int = 5000,
    seed: int = 1,
    ci: float = 0.95,
) -> tuple[float, float]:
    """Bootstrap 95% CI for a pass@1 point estimate. Returns (ci_lo, ci_hi)."""
    ...

def generate_figures(
    deltas_7b: dict[str, float],
    deltas_1_3b: dict[str, float],
    results_7b: dict[str, dict],   # {"sft": {bm: p1}, "rlef_fraction": {bm: p1}}
    results_1_3b: dict[str, dict],
    jt_z: float,
    jt_p: float,
    cfg: H_M4_Config,
) -> None:
    """Generate and save all 4 figures to cfg.figures_dir.
    Fig 1: Bar chart Δ 7B+1.3B with CI error bars (required).
    Fig 2: Monotonicity line plot with JT p-value annotation.
    Fig 3: Absolute pass@1 heatmap (4 rows × 5 benchmarks).
    Fig 4: Scale comparison panel (7B vs 1.3B Δ side-by-side).
    """
    ...
```

---

### Orchestration (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
import json
from pathlib import Path
from config import H_M4_Config
from reanalyze import load_he1_delta_values, build_jt_groups
from train_1_3b import train_sft_1_3b, train_rlef_1_3b
from evaluate_1_3b import evaluate_model
from analyze import (
    jonckheere_terpstra, verify_monotonicity,
    compute_delta_ratio_1_3b, generate_figures,
)

def run_track_7b(cfg: H_M4_Config) -> dict:
    """Track 1: Zero-training 7B re-analysis.
    Returns {"deltas": ..., "jt_z": ..., "jt_p": ..., "is_monotone": ...}.
    """
    ...

def run_track_1_3b(cfg: H_M4_Config) -> dict:
    """Track 2: 1.3B SFT + RLEF-Fraction training + evaluation.
    Returns {"sft_results": ..., "rlef_results": ..., "delta_ratio": ...}.
    """
    ...

def main() -> None:
    """Run both tracks, compute gates, save results JSON, generate figures."""
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + project setup | H_M4_Config dataclass; sys.path injection; directory scaffolding | 5 | 1+1+1+2 |
| A-2 | 7B delta extraction | load_he1_delta_values from experiment_results.json; fallback parse from 04_validation.md | 8 | 2+2+2+2 |
| A-3 | Bootstrap pseudo-groups | Bernoulli simulation for JT group distributions; bootstrap_ci for error bars | 10 | 2+2+3+3 |
| A-4 | JT test + monotonicity | jonckheere_terpstra (manual pairwise Mann-Whitney U); verify_monotonicity | 12 | 3+2+4+3 |
| A-5 | 1.3B SFT training | train_sft_1_3b; APPS loading (reuse h-e1 DATA_CONFIG); checkpoint save + sanity check | 13 | 3+3+4+3 |
| A-6 | 1.3B RLEF-Fraction training | train_rlef_1_3b; import fraction_reward_fn from h-e1; verify_fraction_reward_active logging | 14 | 3+4+4+3 |
| A-7 | 1.3B evaluation | run_bigcode_eval + run_lcb_eval; parse JSON outputs; compute_delta_ratio_1_3b | 12 | 3+3+3+3 |
| A-8 | Visualization | generate_figures (4 figures); seaborn heatmap; annotate JT p-value | 10 | 2+2+3+3 |
| A-9 | Orchestration + gate reporting | run_experiment.py; both tracks; results JSON; gate pass/fail; null-result handling | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-6], Medium(9-13): [A-3, A-4, A-5, A-7, A-8, A-9], Low(4-8): [A-1, A-2]

---

## Key Interface Notes for Phase 4

- `fraction_reward_fn` actual signature is `(completions, prompts, metadata, **kwargs)` — `metadata` is a list of dicts with key `"test_cases"` (not `"input_output"` as in PRD pseudo-code). Trust the code.
- h-e1 `experiment_results.json` key layout: top-level `"deltas"` dict with keys like `"delta_humaneval"`, `"delta_mbpp"`, `"delta_lcb_easy"`, `"delta_lcb_medium"`, `"delta_lcb_hard"` — verify before using.
- JT test requires pseudo-group *distributions*, not point scalars — bootstrap_pseudo_groups must be called before jonckheere_terpstra.
- Gate conditions: JT p < 0.05 AND Z > 0 (positive trend); delta_ratio >= 1.0. Both can fail independently (EXPLORE path for each).
- figures_dir: `docs/youra_research/h-m4/figures/` (absolute from repo root; use `Path(__file__).parents[1] / "figures"` in config).

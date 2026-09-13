---
hypothesis_id: h-m4
type: MECHANISM
phase: 3_architecture
generated_at: 2026-08-21
author: yoon303@etri.re.kr
base_hypothesis: h-m2
---

# Architecture: H-M4 — EvalPlus Checkpoint Evaluation

Applied: checkpoint-evaluation-loop pattern (EvalPlus CLI + subprocess runner)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2)
**Status**: Actual code read directly from `docs/youra_research/h-m2/code/`
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: H-M2 uses flat import paths (`from config import H_M2Config`). `train.py` has `run_grpo()` and `build_grpo_config()`. `save_strategy="no"` in current `build_grpo_config` — fallback training MUST override this to `"steps"` with `save_steps`. H_M2Config already has `save_steps: List[int] = [10, 20, 50]` field.

---

## File Structure

```
docs/youra_research/h-m4/code/
├── evaluate.py        # EvalPlus runner — core new module
├── metrics.py         # pass@1 computation and gate checks
├── visualize.py       # 4 figures (FR-10)
├── run_experiment.py  # main orchestrator
└── config.py          # H-M4 paths and eval parameters
```

Fallback training reuses H-M2 code via sys.path injection (no copy needed).

---

## Module Definitions

### Config (`docs/youra_research/h-m4/code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class H_M4Config:
    # Evaluation
    dataset: str = "humaneval"
    n_samples: int = 8
    temperature: float = 0.8
    backend: str = "hf"

    # Checkpoints (FR-3)
    baseline_model: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    h_m2_results_dir: str = "docs/youra_research/h-m2/results"
    conditions: List[str] = field(default_factory=lambda: ["variance50", "random50", "full374"])
    steps: List[str] = field(default_factory=lambda: ["step_10", "step_20", "step_50"])

    # Gate thresholds
    p1_improvement_pp: float = 0.02
    p1_gap_pp: float = 0.01
    p3_efficiency: float = 0.80

    # Output
    results_dir: str = "docs/youra_research/h-m4/results"
    figures_dir: str = "docs/youra_research/h-m4/figures"
    eval_output_root: str = "docs/youra_research/h-m4/eval_cache"

    # H-M2 code path (for fallback training)
    h_m2_code_dir: str = "docs/youra_research/h-m2/code"

    def checkpoint_path(self, condition: str, step: str) -> str:
        """Returns checkpoint dir for (condition, step); step_0 returns baseline_model."""
        if step == "step_0":
            return self.baseline_model
        step_num = step.replace("step_", "checkpoint-")
        return f"{self.h_m2_results_dir}/{condition}/{step_num}"

    def checkpoint_exists(self, condition: str, step: str) -> bool: ...
```

---

### CheckpointVerifier (`docs/youra_research/h-m4/code/evaluate.py` — top section)

**Dependencies**: Config

```python
def verify_checkpoints(cfg: H_M4Config) -> Dict[str, List[str]]:
    """
    Returns {condition: [missing_step, ...]} for steps requiring checkpoints.
    step_0 (baseline) always passes — uses HuggingFace Hub model.
    """
    ...

def run_fallback_training(cfg: H_M4Config, missing: Dict[str, List[str]]) -> None:
    """
    Injects h-m2 code dir into sys.path, imports train/dataset/reward/config,
    re-runs GRPO with save_strategy='steps' and save_steps=10 for missing conditions.
    """
    ...
```

---

### EvalPlusRunner (`docs/youra_research/h-m4/code/evaluate.py` — main section)

**Dependencies**: Config

```python
def generate_samples(
    checkpoint_path: str,
    condition: str,
    step: str,
    cfg: H_M4Config,
) -> str:
    """
    Runs: python -m evalplus.codegen --model {checkpoint_path}
          --dataset humaneval --backend hf --n_samples 8 --temperature 0.8
          --root {eval_output_root}/{condition}/{step}
    Returns output_dir path.
    Skips if samples.jsonl already exists (resume-safe).
    """
    ...

def evaluate_samples(output_dir: str) -> float:
    """
    Runs: python -m evalplus.evaluate --dataset humaneval --samples {output_dir}/samples.jsonl
    Parses 'humaneval_plus pass@1: X.XXXX' from stdout.
    Returns pass@1 as float.
    """
    ...

def parse_pass_at_1(stdout: str) -> float:
    """Extract pass@1 float from evalplus.evaluate stdout."""
    ...

def run_all_evaluations(cfg: H_M4Config) -> Dict[str, Dict[str, float]]:
    """
    Evaluates all (condition × step) pairs.
    Evaluates step_0 (frozen baseline) ONCE, reuses value for all conditions.
    Returns: {condition: {step: pass@1_float}}
    """
    ...
```

---

### MetricsComputer (`docs/youra_research/h-m4/code/metrics.py`)

**Dependencies**: Config

```python
def compute_metrics(
    pass_at_1: Dict[str, Dict[str, float]],
    cfg: H_M4Config,
) -> dict:
    """
    Computes improvement, gap_vs_random50, efficiency_ratio.
    Returns gate_results dict matching FR-9 JSON schema.
    Fields: gate_passed, p1_pass, p3_pass, baseline_pass_at_1,
            pass_at_1, improvement, gap_vs_random50_at_50,
            efficiency_ratio, thresholds, n_samples_per_problem,
            n_problems, dataset.
    """
    ...

def save_gate_results(results: dict, cfg: H_M4Config) -> None:
    """Writes gate_results.json to cfg.results_dir."""
    ...

def print_gate_summary(results: dict) -> None:
    """Prints FR-8 asserts + human-readable gate summary to stdout."""
    ...
```

---

### Visualizer (`docs/youra_research/h-m4/code/visualize.py`)

**Dependencies**: Config, metrics output

```python
def plot_improvement_bar(results: dict, cfg: H_M4Config) -> str:
    """Fig 1: Bar chart — improvement (pp) at step 50, all 3 conditions.
    Horizontal lines at p1_improvement_pp and p1_gap_pp thresholds.
    Saves to cfg.figures_dir/fig1_improvement_bar.png. Returns path."""
    ...

def plot_learning_curves(results: dict, cfg: H_M4Config) -> str:
    """Fig 2: Line plot — pass@1 improvement trajectory steps 10/20/50.
    Saves to cfg.figures_dir/fig2_learning_curves.png. Returns path."""
    ...

def plot_pass_at_1_heatmap(results: dict, cfg: H_M4Config) -> str:
    """Fig 3: Heatmap — pass@1 at (condition × step), 3×4 grid.
    Saves to cfg.figures_dir/fig3_heatmap.png. Returns path."""
    ...

def plot_mechanistic_scatter(results: dict, h_m2_gate_results_path: str, cfg: H_M4Config) -> str:
    """Fig 4: Scatter — frac_reward_zero_std (from H-M2 gate_results.json) vs
    pass@1 improvement per condition. Loads H-M2 log data internally.
    Saves to cfg.figures_dir/fig4_scatter.png. Returns path."""
    ...

def generate_all_figures(results: dict, cfg: H_M4Config) -> List[str]:
    """Calls all 4 plot functions. Returns list of saved paths."""
    ...
```

---

### Orchestrator (`docs/youra_research/h-m4/code/run_experiment.py`)

**Dependencies**: Config, evaluate, metrics, visualize

```python
def main() -> None:
    """
    1. Load H_M4Config
    2. verify_checkpoints() → if missing → run_fallback_training()
    3. run_all_evaluations() → pass_at_1 dict
    4. compute_metrics() + save_gate_results() + print_gate_summary()
    5. generate_all_figures()
    6. Print final gate verdict
    """
    ...

if __name__ == "__main__":
    main()
```

---

## External Dependencies (Base Hypothesis)

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation)

| Module | Import Path (via sys.path injection) | File Location |
|--------|--------------------------------------|---------------|
| H_M2Config | `from config import H_M2Config` | `h-m2/code/config.py` |
| run_grpo | `from train import run_grpo, build_grpo_config` | `h-m2/code/train.py` |
| make_execution_reward | `from reward import make_execution_reward` | `h-m2/code/reward.py` |
| build_mbpp_dataset | `from dataset import build_mbpp_dataset` | `h-m2/code/dataset.py` |

**Note**: H-M2 `build_grpo_config` sets `save_strategy="no"`. Fallback training must pass `save_strategy="steps"` override or patch locally. Simplest: copy the GRPOConfig construction inline in `run_fallback_training()`.

**Checkpoint path convention** (verified from H_M2Config):
- `docs/youra_research/h-m2/results/{condition}/checkpoint-{N}`
- e.g., `docs/youra_research/h-m2/results/variance50/checkpoint-10`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Install evalplus, verify imports, create output dirs | 5 | 1+1+1+2 |
| A-2 | Config Module | H_M4Config with checkpoint_path() and checkpoint_exists() | 6 | 2+1+1+2 |
| A-3 | Checkpoint Verifier | verify_checkpoints() across all conditions/steps | 7 | 2+2+1+2 |
| A-4 | EvalPlus Sample Generation | generate_samples() with resume-safe skip logic | 10 | 3+2+2+3 |
| A-5 | EvalPlus Evaluation + Parsing | evaluate_samples() + parse_pass_at_1() | 9 | 3+1+2+3 |
| A-6 | Full Eval Loop | run_all_evaluations() — step_0 once, reuse for all conditions | 8 | 2+2+2+2 |
| A-7 | Metrics Computation | compute_metrics() with P1/P3 gate logic + save_gate_results() | 10 | 3+2+3+2 |
| A-8 | Visualization — 4 Figures | All 4 plot functions per FR-10 | 11 | 3+2+3+3 |
| A-9 | Fallback Training | run_fallback_training() via sys.path injection into H-M2 code | 12 | 3+3+3+3 |
| A-10 | Orchestrator | run_experiment.py main() wiring all modules | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-7, A-8, A-9], Low(4-8): [A-1, A-2, A-3, A-6, A-10]

**Total complexity**: 86

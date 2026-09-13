# Architecture: h-m3

**Hypothesis:** Condition B (execution+mypy, k=5) achieves higher pass@1 than Condition A (execution-only, k=5) on MBPP+ (378) and HumanEval+ (164) with GPT-4o-mini.

Archon MCP unavailable — domain knowledge applied.
Applied: iterative-repair-loop pattern, subprocess-mypy pattern, multi-seed statistical comparison pattern

---

## Codebase Analysis (Serena) (Direct Read)

**Project Type**: base_hypothesis (extending h-m2)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: h-m2 has `config.py` (dataclass), `repair_loop.py` (run_condition_a/b, run_mypy), `analysis.py` (compute_differential), `visualize.py` (generate_all_figures), `run.py` (main). Imports shared utilities from `h-e1/code/pipeline.py` (`extract_code`, `generate_solution`, `evaluate_solution`, `load_problems`, `MYPY_FLAGS`). h-m3 extends this with: multi-seed loops, MBPP+ dataset, token-count logging, Welch's t-test on per-problem deltas, 5 new figures.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| extract_code | `from pipeline import extract_code` | `h-e1/code/pipeline.py` |
| generate_solution | `from pipeline import generate_solution` | `h-e1/code/pipeline.py` |
| evaluate_solution | `from pipeline import evaluate_solution` | `h-e1/code/pipeline.py` |
| load_problems | `from pipeline import load_problems` | `h-e1/code/pipeline.py` |
| MYPY_FLAGS | `from pipeline import MYPY_FLAGS` | `h-e1/code/pipeline.py` |
| run_mypy | reuse from h-m2 (copied + extended) | `h-m2/code/repair_loop.py` |

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation)

---

## File Organization

```
docs/youra_research/h-m3/
├── code/
│   ├── config.py          # ExperimentConfig dataclass + YAML loading
│   ├── repair_loop.py     # run_condition_a/b with token logging + multi-seed
│   ├── analysis.py        # compute_pass_at_1, welch_test, confound_analysis
│   ├── visualize.py       # generate_all_figures (5 figures)
│   └── run.py             # main() orchestrator, checkpoint, multi-seed loop
├── results/
│   ├── checkpoint.json
│   ├── condition_a_results.jsonl
│   ├── condition_b_results.jsonl
│   └── analysis.json
└── figures/
    ├── f1_pass_at_1_comparison.png
    ├── f2_repair_trajectory.png
    ├── f3_delta_distribution.png
    ├── f4_mypy_error_by_round.png
    └── f5_token_count_comparison.png
```

---

## Module Definitions

### ExperimentConfig (`code/config.py`)

**Dependencies**: dataclasses, pathlib, yaml

```python
@dataclass
class ExperimentConfig:
    model: str = "gpt-4o-mini"
    initial_temperature: float = 0.8
    repair_temperature: float = 0.0
    max_tokens: int = 2048
    k_max: int = 5
    seeds: list = field(default_factory=lambda: [42, 123, 456])
    datasets: list = field(default_factory=lambda: ["mbpp+", "humaneval+"])
    mypy_flags: list = field(default_factory=lambda: [
        "--ignore-missing-imports", "--no-strict-optional", "--no-error-summary"
    ])
    mypy_timeout: int = 10
    max_retries: int = 3
    retry_base_delay: float = 1.0
    results_dir: str = "docs/youra_research/h-m3/results"
    figures_dir: str = "docs/youra_research/h-m3/figures"
    checkpoint_path: str = "docs/youra_research/h-m3/results/checkpoint.json"

def load_config(yaml_path: str | None = None) -> ExperimentConfig: ...
```

---

### RepairLoop (`code/repair_loop.py`)

**Dependencies**: openai, subprocess, tempfile, pathlib, pipeline (h-e1), logging

```python
# Imports from h-e1 pipeline (verified paths)
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent / "h-e1/code"))
from pipeline import extract_code, generate_solution, evaluate_solution, load_problems, MYPY_FLAGS

def run_mypy(code: str, flags: list, timeout: int) -> tuple[int, str]:
    """Return (error_count, stdout).""" ...

def _count_tokens(text: str) -> int:
    """Approximate token count via len(text.split()) * 1.3.""" ...

def _build_prompt_a(problem: dict, prev_solution: str, exec_feedback: str) -> str: ...

def _build_prompt_b(problem: dict, prev_solution: str,
                    exec_feedback: str, mypy_stdout: str) -> str: ...

def _llm_repair(client, prompt: str, cfg: "ExperimentConfig") -> tuple[str, int]:
    """Return (repaired_code, prompt_token_count).""" ...

def run_condition_a(client, task_id: str, problem: dict,
                    seed: int, cfg: "ExperimentConfig") -> dict:
    """
    Returns {task_id, condition, seed, initial_code, rounds, final_passed}
    rounds: [{round, exec_passed, prompt_tokens}]
    """
    ...

def run_condition_b(client, task_id: str, problem: dict,
                    seed: int, cfg: "ExperimentConfig") -> dict:
    """
    Returns {task_id, condition, seed, initial_code, rounds, final_passed}
    rounds: [{round, exec_passed, mypy_error_count, mypy_triggered, prompt_tokens}]
    """
    ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies**: scipy, numpy

```python
import numpy as np
from scipy import stats

def compute_pass_at_1_per_round(results: list[dict]) -> dict:
    """
    Aggregate pass@1 per round across problems and seeds.
    Returns {dataset: {condition: {round_k: float}}}
    """
    ...

def compute_per_problem_delta(
    results_a: list[dict], results_b: list[dict]
) -> np.ndarray:
    """Per-problem mean_{seeds,rounds} pass@1(B) - pass@1(A).""" ...

def welch_test(deltas: np.ndarray) -> dict:
    """Returns {t_stat, p_value, mean_delta, ci_95, n}.""" ...

def confound_analysis(results_a: list[dict], results_b: list[dict]) -> dict:
    """
    Compute mean token delta per round (CondB - CondA).
    Returns {mean_token_delta_per_round: float, token_delta_by_round: dict}
    """
    ...

def compute_summary(results_a: list[dict], results_b: list[dict],
                    dataset: str) -> dict:
    """
    Full analysis dict: pass@1 per condition, welch_test, confound,
    mechanism_activated, mypy_triggered_fraction, gate_passed.
    """
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, numpy

```python
def plot_f1_bar_comparison(summary: dict, figures_dir: pathlib.Path) -> None:
    """F1: Bar chart pass@1 CondA vs B on MBPP+ and HumanEval+ with std error bars.""" ...

def plot_f2_repair_trajectory(results_a: list, results_b: list,
                               dataset: str, figures_dir: pathlib.Path) -> None:
    """F2: Line plot mean pass@1 per round k=0..5, CondA/B/Baseline.""" ...

def plot_f3_delta_distribution(deltas: np.ndarray, figures_dir: pathlib.Path) -> None:
    """F3: Histogram of per-problem (B-A) deltas on MBPP+.""" ...

def plot_f4_mypy_error_by_round(results_b: list, figures_dir: pathlib.Path) -> None:
    """F4: Line plot mean mypy error count per round k for CondB.""" ...

def plot_f5_token_count(confound: dict, figures_dir: pathlib.Path) -> None:
    """F5: Bar chart mean prompt tokens per round CondA vs B.""" ...

def generate_all_figures(summary: dict, results_a: list, results_b: list,
                          deltas: np.ndarray, figures_dir: pathlib.Path) -> None: ...
```

---

### Run (`code/run.py`)

**Dependencies**: config, repair_loop, analysis, visualize, openai, json, logging

```python
def _load_checkpoint(path: pathlib.Path) -> dict: ...
def _save_checkpoint(path: pathlib.Path, data: dict) -> None: ...

def main() -> None:
    """
    1. Load config
    2. For each dataset × seed: run CondA and CondB repair loops (with checkpointing)
    3. compute_summary for each dataset
    4. Save JSONL results + analysis.json + gate_result.json
    5. generate_all_figures
    6. Assert mechanism activated (mypy_triggered_count > 0)
    7. Log gate result (MUST_WORK: p < 0.05 AND delta >= 0.01 on MBPP+)
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & Setup | ExperimentConfig dataclass + YAML loading + dir structure | 6 | 2+1+1+2 |
| A-2 | Repair Loop Core | run_condition_a/b with token logging; extend h-m2 repair_loop | 14 | 4+3+4+3 |
| A-3 | Multi-Seed Orchestrator | run.py main: loop over datasets × seeds, checkpoint, gate assert | 13 | 3+3+3+4 |
| A-4 | Statistical Analysis | compute_per_problem_delta, welch_test, confound_analysis | 12 | 3+2+4+3 |
| A-5 | MBPP+ Integration | Verify load_problems("mbpp+") works via h-e1 pipeline; adapt if needed | 9 | 2+3+2+2 |
| A-6 | Visualization | 5 figures: bar/line/histogram/line/bar via matplotlib | 11 | 3+2+3+3 |
| A-7 | Results Logging | Structured JSONL + analysis.json + gate_result.json output | 7 | 2+2+1+2 |
| A-8 | Unit Tests | test_repair_loop.py: mypy mock, token count, prompt build; test_analysis.py: welch on known deltas | 10 | 2+2+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-4, A-5, A-6, A-8], Low(4-8): [A-1, A-7]

---

## Key Schema: Round Record

**Condition A round record:**
```json
{"round": 1, "exec_passed": false, "prompt_tokens": 312}
```

**Condition B round record:**
```json
{"round": 1, "exec_passed": false, "mypy_error_count": 2, "mypy_triggered": true, "prompt_tokens": 408}
```

**Top-level result record:**
```json
{
  "task_id": "mbpp/1",
  "dataset": "mbpp+",
  "condition": "B",
  "seed": 42,
  "initial_code": "...",
  "rounds": [...],
  "final_passed": true,
  "initial_mypy_errors": 2
}
```

---

## Notes for Phase 4 Coder

- `load_problems("mbpp+")` — verify this works in h-e1's `pipeline.py`; MBPP+ was excluded from h-m2 (see h-m2 config `benchmark: "humaneval+"`), so MBPP+ path in h-e1 pipeline must be confirmed.
- `generate_solution` in h-e1 takes `(client, problem, seed)` — seed controls temperature=0.8 call repetition (not OpenAI seed param directly; may need adaptation for multi-seed).
- Token count: use approximate method (`_count_tokens`) to avoid tiktoken dependency; flag with `# ponytail: approx token count, swap tiktoken if exact billing needed`.
- Checkpoint structure must handle `(dataset, seed, condition, task_id)` composite key.
- mypy must be installed in the experiment environment (`pip install mypy`).

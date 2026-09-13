---
hypothesis_id: H-M2
phase: 3
date: 2026-08-26
author: yoon303@ust.ac.kr
---

# Logic: H-M2 — Mypy Feedback Specificity for Type-Related Failures

Applied: [INFERRED] iterative-repair-loop with checkpoint/resume (Archon MCP unavailable)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis extension
**Status**: API signatures verified from actual code (Serena MCP unavailable — files read directly)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**:
- `repair_loop_condition_b(client, task_id, problem, benchmark, seed, k_max)` → `list`
- `run_mypy_with_output(code, timeout)` → `tuple[bool, int, str]`
- `_build_repair_prompt(problem, prev_solution, exec_feedback, mypy_stdout)` → `str`
- `_generate_repair(client, prompt, max_tokens, max_retries, base_delay)` → `str`
- `run_all_benchmarks(client, benchmarks, seed, k_max)` → `list`
- `generate_solution(client, problem, seed)` — from h-e1/pipeline.py
- `evaluate_solution(task_id, solution, problem)` — from h-e1/pipeline.py
- `extract_code(raw)` — from h-e1/pipeline.py
- `load_problems(benchmark)` — from h-e1/pipeline.py

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code — h-m1/code/repair_loop.py)

```python
# From: h-m1/code/repair_loop.py (ACTUAL CODE)

def run_mypy_with_output(code: str, timeout: int = 10) -> tuple:
    """Run mypy; return (has_error: bool, error_count: int, mypy_stdout: str)."""
    ...

def repair_loop_condition_b(
    client: OpenAI,
    task_id: str,
    problem: dict,
    benchmark: str,
    seed: int = 42,
    k_max: int = 5,
) -> list:
    """Returns list of {task_id, benchmark, round, mypy_error_count, exec_passed, ...}"""
    ...
```

```python
# From: h-e1/code/pipeline.py (via h-m1 sys.path)

def generate_solution(client: OpenAI, problem: dict, seed: int) -> str: ...
def evaluate_solution(task_id: str, solution: str, problem: dict) -> bool: ...
def extract_code(raw: str) -> str: ...
def load_problems(benchmark: str) -> dict: ...  # {task_id: problem_dict}
MYPY_FLAGS: list[str]  # ["--ignore-missing-imports", "--no-strict-optional"]
```

**Verified from**: `docs/youra_research/h-m1/code/repair_loop.py` (actual implementation)

---

## A-4: condition_a_runner.py [Complexity: 14, Budget: 4 subtasks]

Applied: [INFERRED] iterative-repair-loop with checkpoint/resume

### API Signatures

```python
"""Condition A (execution-only) repair loop — no mypy in prompt."""

import json
import logging
import pathlib
import sys
import time
from openai import OpenAI

# sys.path setup mirrors h-m1/code/run.py lines 13-15
_h_e1_path = str(pathlib.Path(__file__).parent.parent.parent / "h-e1/code")
_h_m1_path = str(pathlib.Path(__file__).parent.parent.parent / "h-m1/code")
for _p in [_h_m1_path, _h_e1_path]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pipeline import generate_solution, evaluate_solution, extract_code, load_problems
from config import Config

logger = logging.getLogger(__name__)


def build_condition_a_repair_prompt(
    problem: dict,
    prev_solution: str,
    exec_feedback: str,
) -> str:
    """Execution-only prompt — mypy section explicitly omitted vs Condition B."""
    ...


def _generate_repair_a(
    client: OpenAI,
    prompt: str,
    max_tokens: int = 2048,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> str:
    """GPT-4o-mini at temperature=0.0 with exponential backoff. Returns extracted code."""
    ...


def run_condition_a_problem(
    problem: dict,
    task_id: str,
    client: OpenAI,
    cfg: Config,
) -> list[dict]:
    """Run k=1..5 repair loop for one problem under Condition A.

    Returns: [{task_id, round_k, exec_passed, condition: "A"}]
    """
    ...


def run_condition_a_benchmark(
    problems: dict,
    benchmark: str,
    cfg: Config,
    client: OpenAI,
    checkpoint_path: str,
) -> dict:
    """Run Condition A for all problems in benchmark with checkpoint/resume.

    Returns: {task_id: [{round_k, exec_passed}]}
    """
    ...
```

### Pseudo-code

**build_condition_a_repair_prompt:**
```
problem_prompt = problem.get("prompt", problem.get("text", ""))
return "\n".join([
    f"Problem: {problem_prompt}", "",
    "Previous solution:", prev_solution, "",
    "Execution feedback:",
    exec_feedback or "(no execution output)", "",
    "Please fix the above errors and provide a corrected solution.",
    "Return ONLY the complete Python function implementation, no explanation.",
])
# NOTE: no "Type checker (mypy) feedback" section — that is the Condition A/B difference
```

**run_condition_a_problem:**
```
solution = generate_solution(client, problem, cfg.seed)
if not solution: return []

records = []
for k in 1..cfg.k_max:
    exec_passed = evaluate_solution(task_id, solution, problem)
    exec_feedback = "" if exec_passed else "Execution failed: test cases did not pass."
    records.append({task_id, round_k=k, exec_passed, condition="A"})
    logger.info(f"[Cond A] problem={task_id} round={k} exec_passed={exec_passed}")
    if exec_passed: break
    if k < cfg.k_max:
        prompt = build_condition_a_repair_prompt(problem, solution, exec_feedback)
        solution = _generate_repair_a(client, prompt, ...)  # raises on exhausted retries
return records
```

**run_condition_a_benchmark (checkpoint/resume):**
```
completed = _load_checkpoint(checkpoint_path)  # {task_id: [{...}]}
results = dict(completed)
total = len(problems)

for i, (task_id, problem) in enumerate(problems.items()):
    if task_id in results: continue  # resume skip
    try:
        records = run_condition_a_problem(problem, task_id, client, cfg)
        results[task_id] = records
        _save_checkpoint(checkpoint_path, results)  # write after each problem
    except Exception as e:
        logger.error(f"Skipping {task_id}: {e}")
    if i % 20 == 0:
        logger.info(f"[{benchmark}] {i}/{total} problems complete")

return results

# _load_checkpoint: read JSONL if exists, else return {}
# _save_checkpoint: overwrite JSONL with all results (small enough; ~164 problems)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | prompt builder | `build_condition_a_repair_prompt` — execution-only, no mypy |
| L-4-2 | repair generator | `_generate_repair_a` with exponential backoff |
| L-4-3 | per-problem loop | `run_condition_a_problem` k=1..5 with early exit |
| L-4-4 | benchmark runner | `run_condition_a_benchmark` with checkpoint/resume |

---

## A-7: run.py [Complexity: 10, Budget: 1 subtask]

Applied: [INFERRED] orchestrator pattern (mirrors h-m1/code/run.py structure)

### API Signatures

```python
"""H-M2 experiment entry point."""

import json
import logging
import os
import pathlib
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# sys.path: h-e1 first, then h-m1, then h-m2 (h-m2 takes precedence)
_base = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(_base / "h-e1/code"))
sys.path.insert(0, str(_base / "h-m1/code"))
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from openai import OpenAI
from config import Config
from load_condition_b import load_h_m1_results, extract_initial_mypy_errors, extract_cond_b_pass_at_k
from category_labeling import label_problems, verify_labels
from condition_a_runner import run_condition_a_benchmark
from analysis import compute_differential, verify_mechanism
from visualize import plot_gate_metrics, plot_repair_rates_4bar, plot_round_curves, plot_heatmap
from pipeline import load_problems


def main() -> None:
    """Orchestrate H-M2: load Cond B, label, run Cond A, analyze, visualize, persist."""
    ...


if __name__ == "__main__":
    main()
```

### Pseudo-code

```
main():
  cfg = Config()
  api_key = os.environ.get("OPENAI_API_KEY") or load_dotenv()
  if not api_key: sys.exit(1)
  client = OpenAI(api_key=api_key)

  results_dir = pathlib.Path(cfg.results_dir); results_dir.mkdir(parents=True, exist_ok=True)
  figures_dir = pathlib.Path(cfg.figures_dir); figures_dir.mkdir(parents=True, exist_ok=True)

  # 1. Load Condition B (H-M1 results)
  h_m1_records = load_h_m1_results(cfg.h_m1_results)
  initial_mypy = extract_initial_mypy_errors(h_m1_records)
  cond_b_pass = extract_cond_b_pass_at_k(h_m1_records, k=cfg.k_max)

  # 2. Label problems (use H-M1 mypy data only)
  failing_ids = {tid for tid, passed in cond_b_pass.items() if not passed}
  # Also include any that failed initial — derive from h_m1_records round=1 exec_passed=False
  labels = label_problems(initial_mypy, failing_task_ids=failing_ids)
  verify_labels(labels, expected_type_count=20)
  with open(results_dir / "category_labels.json", "w") as f:
      json.dump(labels, f, indent=2)

  # 3. Run Condition A — HumanEval+
  he_problems = load_problems("humaneval+")
  he_ckpt = str(results_dir / "condition_a_humaneval.jsonl")
  cond_a_he = run_condition_a_benchmark(he_problems, "humaneval+", cfg, client, he_ckpt)

  # 4. Run Condition A — MBPP+ (secondary control)
  mbpp_problems = load_problems("mbpp+")
  mbpp_ckpt = str(results_dir / "condition_a_mbpp.jsonl")
  cond_a_mbpp = run_condition_a_benchmark(mbpp_problems, "mbpp+", cfg, client, mbpp_ckpt)

  # 5. Compute differential analysis
  results = compute_differential(cond_a_he, cond_b_pass, labels, k=cfg.k_max)
  activated = verify_mechanism(results)

  # 6. Persist summary
  with open(results_dir / "summary.json", "w") as f:
      json.dump(results, f, indent=2)

  # 7. Generate figures
  plot_gate_metrics(results, str(figures_dir))
  plot_repair_rates_4bar(results, str(figures_dir))
  plot_round_curves(cond_a_he, h_m1_records, labels, str(figures_dir))
  plot_heatmap(results, str(figures_dir))

  logger.info(f"H-M2 complete. Gate passed: {results['gate_passed']}")
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | orchestration | `main()` — wire all modules, 7-step pipeline, persist outputs |

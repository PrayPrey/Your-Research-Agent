---
hypothesis_id: H-Z1
phase: 3
type: architecture
base_hypothesis: H-E1
date: 2026-08-26
---

# Architecture: H-Z1 — Z3 Formal Counterexample Feedback for LLM Code Repair

Applied: CEGIS (Counterexample-Guided Inductive Synthesis) loop pattern (LLM-CEGIS-Repair, AAAI 2025)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Patterns found from base code (Read tool used)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 has `pipeline.py` (monolithic: load, generate, evaluate, mypy), `config.py` (dataclass), `visualize.py`, `run.py`. Key reusable functions: `load_problems`, `generate_solution`, `evaluate_solution`, `run_mypy`, `extract_code`, `extract_error_categories`.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_problems | `from h_e1.pipeline import load_problems` | `h-e1/code/pipeline.py` |
| generate_solution | `from h_e1.pipeline import generate_solution` | `h-e1/code/pipeline.py` |
| evaluate_solution | `from h_e1.pipeline import evaluate_solution` | `h-e1/code/pipeline.py` |
| run_mypy | `from h_e1.pipeline import run_mypy` | `h-e1/code/pipeline.py` |
| extract_code | `from h_e1.pipeline import extract_code` | `h-e1/code/pipeline.py` |

**Note**: H-Z1 code lives in `docs/youra_research/h-z1/code/`. Import paths use `sys.path.insert` to reach h-e1/code at runtime rather than package install.

---

## File Structure

```
docs/youra_research/h-z1/code/
├── config.py          # ExperimentConfig for H-Z1 (extends H-E1 config)
├── z3_utils.py        # Z3 spec generation, validation, CE extraction
├── repair_loop.py     # Condition B and Condition C repair loops
├── run.py             # Entry point: curate → validate → repair → report
└── visualize.py       # Figures (gate bar chart + 3 autonomous figures)
```

Results and figures go to:
```
docs/youra_research/h-z1/results/
docs/youra_research/h-z1/figures/
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: stdlib only

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Z1Config:
    # Inherited from H-E1 (same values)
    model: str = "gpt-4o-mini"
    gen_temperature: float = 0.8
    repair_temperature: float = 0.0
    max_tokens: int = 2048
    seed: int = 42
    mypy_timeout: int = 30
    mypy_flags: list = field(default_factory=lambda: ["--ignore-missing-imports", "--no-strict-optional"])
    # H-Z1 new
    k_repair_rounds: int = 5
    z3_timeout: int = 10
    min_valid_z3_specs: int = 30
    results_dir: Path = Path("docs/youra_research/h-z1/results")
    figures_dir: Path = Path("docs/youra_research/h-z1/figures")
    h_e1_code_dir: Path = Path("docs/youra_research/h-e1/code")
```

---

### Z3Utils (`code/z3_utils.py`)

**Dependencies**: z3-solver, openai, evalplus (via h-e1 pipeline)

```python
from openai import OpenAI
from typing import Optional

class Z3SpecResult:
    task_id: str
    spec_code: str           # Python code string using z3-solver
    valid: bool
    reject_reason: Optional[str]

def generate_z3_spec(problem: dict, client: OpenAI) -> str:
    """Call GPT-4o-mini (temp=0.0) to generate Z3 spec code for problem."""
    ...

def validate_z3_spec(spec_code: str, problem: dict, expected_outputs: dict) -> Z3SpecResult:
    """Execute spec against canonical solution test inputs; reject if false negative."""
    ...

def extract_z3_counterexample(spec_code: str, candidate_solution: str,
                               problem: dict, timeout: int = 10) -> Optional[dict]:
    """Run Z3; if sat return {input_var: value} witness dict, else None.
    Returns None on timeout or z3 error (graceful degradation)."""
    ...

def curate_arithmetic_subset(problems: dict) -> dict:
    """Filter HumanEval+ to arithmetic-heavy problems per curation criteria."""
    ...
```

---

### RepairLoop (`code/repair_loop.py`)

**Dependencies**: z3_utils, h-e1 pipeline functions (via sys.path), openai

```python
from openai import OpenAI
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class RoundResult:
    round_num: int
    passed: bool
    exec_feedback: str
    mypy_feedback: str
    z3_ce: Optional[dict]     # None for Condition B or when no CE found

@dataclass
class ProblemResult:
    task_id: str
    condition: str            # "B" or "C"
    passed: bool
    rounds_to_pass: int       # k+1 if never passed
    final_solution: str
    z3_ce_found_count: int    # always 0 for Condition B

def repair_loop_b(problem: dict, initial_solution: str,
                  client: OpenAI, cfg) -> ProblemResult:
    """k=5 rounds: execute → mypy → repair (no Z3)."""
    ...

def repair_loop_c(problem: dict, initial_solution: str,
                  spec_code: str, client: OpenAI, cfg) -> ProblemResult:
    """k=5 rounds: execute → mypy → Z3 CE → repair (with Z3)."""
    ...

def build_repair_prompt_b(problem: dict, solution: str,
                           exec_fb: str, mypy_fb: str) -> str: ...

def build_repair_prompt_c(problem: dict, solution: str,
                           exec_fb: str, mypy_fb: str,
                           z3_ce: Optional[dict]) -> str: ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, json

```python
from pathlib import Path

def plot_gate_metrics(summary: dict, figures_dir: Path) -> None:
    """Bar chart: pass@1 Condition B vs C. Saves gate_metrics.png."""
    ...

def plot_z3_funnel(counts: dict, figures_dir: Path) -> None:
    """Stacked bar: curated → spec generated → spec validated → used."""
    ...

def plot_per_round_curve(b_results: list, c_results: list, figures_dir: Path) -> None:
    """Line chart: cumulative pass@1 per repair round k=1..5, B vs C."""
    ...

def plot_ce_found_rate(c_results: list, figures_dir: Path) -> None:
    """Histogram: z3_ce_found_count distribution across problems."""
    ...
```

---

### Run (`code/run.py`)

**Dependencies**: all above modules, pathlib, json, logging

```python
def main() -> None:
    """
    1. Load HumanEval+ via h-e1 load_problems
    2. curate_arithmetic_subset
    3. generate_z3_spec + validate_z3_spec for each curated problem
    4. Assert subset_size >= cfg.min_valid_z3_specs
    5. Generate initial solutions (seed=42, temp=0.8) — shared for B and C
    6. Run repair_loop_b and repair_loop_c for each validated problem
    7. Compute summary metrics and save results
    8. Generate all figures
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Tag |
|----|------|-------------|------------|-----|
| E1 | Project setup & config | Create h-z1/code/, config.py, sys.path wiring to h-e1, requirements check (z3-solver import) | 6 (2+1+1+2) | setup |
| E2 | Arithmetic subset curation | Implement `curate_arithmetic_subset` with 5-criteria filter; log accepted/rejected per task_id | 8 (2+2+2+2) | data-pipeline |
| E3 | Z3 spec generation & validation | `generate_z3_spec` (LLM call) + `validate_z3_spec` (exec against canonical solution + EvalPlus test inputs); save validated_subset.json | 14 (3+3+4+4) | model |
| E4 | Z3 counterexample extraction | `extract_z3_counterexample`: exec spec code + candidate in sandbox, add `Not(expected)`, call `solver.check()`, extract `solver.model()` with timeout guard | 13 (3+3+4+3) | model |
| E5 | Condition B repair loop | `repair_loop_b`: k=5 rounds of evaluate→mypy→repair prompt→LLM; reuse h-e1 `evaluate_solution`, `run_mypy`, `generate_solution` | 10 (2+3+2+3) | training |
| E6 | Condition C repair loop | `repair_loop_c`: identical to B + Z3 CE step each round; graceful fallback to B-prompt on Z3 timeout | 11 (2+3+3+3) | training |
| E7 | Results aggregation & persistence | Compute pass@1_B, pass@1_C, delta, secondary metrics; write condition_b/c_results.jsonl, summary.json | 7 (2+2+1+2) | evaluation |
| E8 | Visualization & run.py orchestration | All 4 figures + run.py end-to-end orchestration; gate check assertion | 8 (2+2+2+2) | experiment |

**Distribution**: High(12-17): [E3, E4, E6], Medium(8-11): [E2, E5, E7, E8], Low(4-7): [E1]

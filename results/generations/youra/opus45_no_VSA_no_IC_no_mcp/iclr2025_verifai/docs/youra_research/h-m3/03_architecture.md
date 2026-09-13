# Architecture: H-M3 (Fix Specificity Inverted-U)

**Type:** MECHANISM | **Tier:** FULL | **Applied:** Scaffolding-level ablation pattern (parametrized hint generator + within-subject repeated measures)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** Actual code found and read directly (Serena MCP unavailable — used direct file read as fallback, per CRITICAL RULE to trust actual code over specs)
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:** H-E1 code implements `StructuredError`/`parse_compiler_output` (errors.py), `format_structured_prompt` (prompts.py), `repair_problem`/`execute_and_check` (repair_loop.py), `generate_code`/`load_hf_model` (models.py), `run_benchmark` (evaluate.py), and `CONFIG` dict (config.py). H-M3 reuses these directly and adds a fix-specificity hint layer inserted into the repair loop's prompt-building step.

---

## Module Structure

### FixHintGenerator (`hints.py`)

**Dependencies**: errors.StructuredError

```python
from dataclasses import dataclass
from errors import StructuredError

@dataclass
class HintAnalysis:
    general_strategy: str
    specific_pattern: str
    exact_fix: str

def analyze_error(error: StructuredError, source_code: str) -> HintAnalysis: ...
def generate_hint(error: StructuredError, source_code: str, level: int) -> str: ...
```

### Prompt Extension (`prompts.py` — extend existing)

**Dependencies**: errors.StructuredError, hints.generate_hint

```python
def format_leveled_prompt(error: StructuredError, original_code: str, level: int) -> str: ...
# reuses format_structured_prompt() layout + injects "## Fix Guidance" section
```

### Repair Loop Extension (`repair_loop.py` — extend existing)

**Dependencies**: prompts.format_leveled_prompt, models.generate_code, config.CONFIG

```python
def repair_problem_leveled(model_ref, tokenizer, problem: dict, fix_level: int,
                            max_attempts: int = None, is_openai: bool = False) -> dict: ...
# same contract as repair_problem(); returns {"passed", "attempts_used", "error_types_seen", "first_iter_success"}
```

### Experiment Runner (`experiment.py`)

**Dependencies**: repair_loop.repair_problem_leveled, models.load_hf_model, config.CONFIG, evaluate.load_benchmark_problems

```python
def run_level_sweep(model_name: str, benchmark: str, levels: list, n_reps: int = 3) -> list[dict]: ...
# within-subject: same error_id run across all levels, order randomized (seeded)
def collect_error_instances(model_name: str, benchmark: str) -> list[dict]: ...
# Stage 1: generate + run initial code, keep failures as repairable error instances
```

### Statistical Analysis (`analysis.py`)

**Dependencies**: pandas, statsmodels, scipy.stats

```python
import pandas as pd

def build_results_dataframe(records: list[dict]) -> pd.DataFrame: ...
def fit_quadratic_contrast(df: pd.DataFrame) -> dict: ...
# success ~ level + level^2 + (1|error_id) + (1|model); returns {"quad_coef","quad_pval","peak_level"}
def check_gate_criteria(fit_result: dict, df: pd.DataFrame) -> dict: ...
```

### Visualization (`visualize.py` — extend existing pattern)

**Dependencies**: matplotlib, seaborn, analysis.build_results_dataframe

```python
def plot_gate_metrics(df) -> str: ...          # required: bar chart, level vs success rate
def plot_inverted_u_curve(df, fit_result) -> str: ...
def plot_model_heatmap(df) -> str: ...
def plot_error_type_breakdown(df) -> str: ...
def plot_iterations_per_level(df) -> str: ...
```

### Config (`config.py` — extend existing CONFIG dict)

```python
CONFIG.update({
    "fix_levels": [0, 1, 2, 3],
    "n_repetitions": 3,
    "level_order_seed": 42,
    "target_error_instances": 500,
})
```

### Entry Point (`run_poc.py` — extend existing pattern)

```python
def main(): ...
# orchestrates: collect_error_instances -> run_level_sweep -> build_results_dataframe
#               -> fit_quadratic_contrast -> check_gate_criteria -> plot_* -> save results.json
```

---

## External Dependencies (Base Hypothesis H-E1)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| StructuredError, parse_compiler_output | `from errors import StructuredError, parse_compiler_output` | `h-e1/code/errors.py` |
| format_structured_prompt | `from prompts import format_structured_prompt` | `h-e1/code/prompts.py` |
| execute_and_check, extract_code_block, initial_prompt, repair_problem | `from repair_loop import execute_and_check, extract_code_block, initial_prompt, repair_problem` | `h-e1/code/repair_loop.py` |
| generate_code, load_hf_model | `from models import generate_code, load_hf_model` | `h-e1/code/models.py` |
| CONFIG, OPENAI_API_KEY | `from config import CONFIG, OPENAI_API_KEY` | `h-e1/code/config.py` |
| load_benchmark_problems | `from evaluate import load_benchmark_problems` | `h-e1/code/evaluate.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, read directly — matches 03_architecture.md intent, no drift found)

**Note**: H-M3 code directory copies/imports these H-E1 modules unchanged (errors.py, models.py, repair_loop.py base functions, config.py base keys, evaluate.py) and adds hints.py, analysis.py, and extends prompts.py/repair_loop.py/config.py/visualize.py/run_poc.py as above.

---

## File Organization

```
h-m3/code/
├── config.py          (extended from H-E1)
├── errors.py          (reused from H-E1, unchanged)
├── models.py          (reused from H-E1, unchanged)
├── prompts.py         (extended: + format_leveled_prompt)
├── hints.py           (new: FixHintGenerator logic)
├── repair_loop.py      (extended: + repair_problem_leveled)
├── evaluate.py         (reused: load_benchmark_problems)
├── experiment.py       (new: level sweep orchestration)
├── analysis.py         (new: quadratic contrast stats)
├── visualize.py        (extended: 5 figure functions)
└── run_poc.py          (extended: main orchestration)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Hint Generator | Implement `hints.py`: analyze_error + generate_hint for 4 levels | 10 | 3+2+3+2 |
| A-2 | Prompt Extension | Add `format_leveled_prompt` to prompts.py, integrate hint text | 6 | 2+2+1+1 |
| A-3 | Repair Loop Extension | Add `repair_problem_leveled` to repair_loop.py, track first-iter success | 9 | 2+3+2+2 |
| A-4 | Error Instance Collection | Implement `collect_error_instances`: generate code, run tests, filter failures, stratify by error type | 11 | 3+3+3+2 |
| A-5 | Level Sweep Orchestration | Implement `run_level_sweep`: within-subject randomized order, 3 reps, 3 models × 2 benchmarks | 13 | 3+4+3+3 |
| A-6 | Statistical Analysis | Implement `build_results_dataframe`, `fit_quadratic_contrast` (mixedlm), `check_gate_criteria` | 12 | 3+3+4+2 |
| A-7 | Visualization Suite | Implement 5 plot functions (gate bar chart, inverted-U curve, heatmap, error-type breakdown, iterations) | 8 | 3+1+2+2 |
| A-8 | Config & Integration | Extend CONFIG, wire main() in run_poc.py end-to-end, save results.json | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3, A-4, A-5, A-6], Low(4-8): [A-2, A-7, A-8]

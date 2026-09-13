# Logic: H-M3 (Fix Specificity Inverted-U)

**Type:** MECHANISM | **Budget:** 12 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** API signatures verified from actual H-E1 code (direct file read; Serena MCP unavailable in this environment, used as fallback per CRITICAL RULE)
**Analyzed Path:** `docs/youra_research/h-e1/code/` (errors.py, prompts.py, repair_loop.py, models.py, config.py, evaluate.py)
**Relevant Symbols:** `StructuredError`, `parse_compiler_output`, `format_structured_prompt`, `execute_and_check`, `extract_code_block`, `initial_prompt`, `repair_problem`, `generate_code`, `load_hf_model`, `CONFIG`, `load_benchmark_problems`

**Drift found**: None — 03_architecture.md's import list matches actual code exactly. All signatures below copied from real implementation, not from any spec.

---

## External Dependencies (Base Hypothesis H-E1, verified from actual code)

```python
# From: h-e1/code/errors.py
@dataclass
class StructuredError:
    line_number: int
    error_type: str
    error_message: str
    code_context: List[str]

def parse_compiler_output(raw_output: str, source_code: str) -> StructuredError: ...

# From: h-e1/code/prompts.py
def format_structured_prompt(error: StructuredError, original_code: str) -> str: ...

# From: h-e1/code/repair_loop.py
def execute_and_check(code: str, problem: Dict) -> Tuple[bool, str]: ...
def extract_code_block(text: str) -> str: ...
def initial_prompt(problem: Dict) -> str: ...
def repair_problem(model_ref, tokenizer, problem: Dict, use_structured: bool,
                    max_attempts: int = None, is_openai: bool = False) -> Dict: ...
# returns {"passed": bool, "attempts_used": int, "error_types_seen": List[str]}

# From: h-e1/code/models.py
def load_hf_model(model_id: str) -> Tuple[Any, Any]: ...  # (model, tokenizer), cached
def generate_code(model_ref, tokenizer, prompt: str, is_openai: bool = False,
                   max_new_tokens: int = None, temperature: float = None) -> str: ...

# From: h-e1/code/config.py
CONFIG: dict  # keys: models, openai_models, benchmarks, benchmark_datasets,
              # max_repair_attempts=5, exec_timeout_sec=3.0, temperature=0.0, seed=42

# From: h-e1/code/evaluate.py
def load_benchmark_problems(benchmark: str) -> List[Dict]: ...
# raises ValueError (unknown benchmark) / RuntimeError (empty result)
```

**Note**: `problem["entry_point"]` and `problem["test"]` keys are guaranteed present by `load_benchmark_problems` filter.

---

## A-1: Hint Generator (`hints.py`) [Complexity: 10, Budget: 10]

**Applied**: KB pattern — rule-based template generator over structured error taxonomy (no ML/embedding, deterministic per error_type)

### API Signatures

```python
from dataclasses import dataclass
from typing import Dict
from errors import StructuredError

@dataclass
class HintAnalysis:
    general_strategy: str   # level-1 text
    specific_pattern: str   # level-2 text
    exact_fix: str          # level-3 text

# error_type -> (strategy_template, pattern_template) keyed lookup table
ERROR_HINT_TEMPLATES: Dict[str, Dict[str, str]]

def analyze_error(error: StructuredError, source_code: str) -> HintAnalysis:
    """Derive 3 hint tiers from error_type + code_context. No LLM call."""
    ...

def generate_hint(error: StructuredError, source_code: str, level: int) -> str:
    """level 0 -> "" ; 1 -> general_strategy ; 2 -> specific_pattern ; 3 -> exact_fix."""
    ...
```

### Pseudo-code

```
analyze_error(error, source_code):
    template = ERROR_HINT_TEMPLATES.get(error.error_type, ERROR_HINT_TEMPLATES["UnknownError"])
    general_strategy = template["strategy"]                      # e.g. "check boundary conditions"
    specific_pattern = template["pattern"].format(line=error.line_number)  # e.g. "use try-except for IndexError near line {line}"
    exact_fix = build_exact_fix(error, source_code)               # line-specific patch suggestion string
    return HintAnalysis(general_strategy, specific_pattern, exact_fix)

build_exact_fix(error, source_code):
    target_line = source_code.split('\n')[error.line_number - 1] if valid else ""
    return f"Change line {error.line_number} to: {heuristic_patch(target_line, error.error_type)}"

generate_hint(error, source_code, level):
    if level == 0: return ""
    analysis = analyze_error(error, source_code)
    return {1: analysis.general_strategy, 2: analysis.specific_pattern, 3: analysis.exact_fix}[level]
```

### Subtasks [4/10 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | HintAnalysis dataclass + template table | Static dict for IndexError/TypeError/SyntaxError/NameError/ValueError/UnknownError |
| L-1-2 | analyze_error | Template lookup + build_exact_fix heuristic |
| L-1-3 | generate_hint level dispatch | level->field mapping incl. level 0 empty string |
| L-1-4 | Self-check | assert-based demo() covering all 4 levels x 2 error types |

---

## A-2: Prompt Extension (`prompts.py`) [Complexity: 6, Budget: 6]

**Applied**: Standard PyTorch/string-template extension — reuse existing layout, inject one section

### API Signatures

```python
from errors import StructuredError
from hints import generate_hint

def format_leveled_prompt(error: StructuredError, original_code: str, level: int) -> str:
    """format_structured_prompt() layout + '## Fix Guidance' section (empty at level 0)."""
    ...
```

### Pseudo-code

```
format_leveled_prompt(error, original_code, level):
    base = format_structured_prompt(error, original_code)  # reuse H-E1 layout verbatim
    hint = generate_hint(error, original_code, level)
    if not hint: return base
    guidance = f"\n## Fix Guidance\n{hint}\n"
    return base.replace("Provide the corrected complete code:",
                         guidance + "\nProvide the corrected complete code:")
```

### Subtasks [2/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | format_leveled_prompt | Insert Fix Guidance section, level 0 = no-op |
| L-2-2 | Self-check | assert level0 output == format_structured_prompt output; level>0 contains "Fix Guidance" |

---

## A-3: Repair Loop Extension (`repair_loop.py`) [Complexity: 9, Budget: 9]

**Applied**: Standard PyTorch — loop mirrors `repair_problem`, swaps prompt builder, adds first-iter tracking

### API Signatures

```python
from typing import Dict, List
from errors import parse_compiler_output
from prompts import format_leveled_prompt
from models import generate_code
from config import CONFIG

def repair_problem_leveled(model_ref, tokenizer, problem: Dict, fix_level: int,
                            max_attempts: int = None, is_openai: bool = False) -> Dict:
    """Same contract as repair_problem(). Returns dict below."""
    ...
```

### Tensor / Return Shapes

| Field | Type | Note |
|-------|------|------|
| passed | bool | final pass/fail |
| attempts_used | int | 0 if passed on initial gen |
| error_types_seen | List[str] | one entry per repair iteration |
| first_iter_success | bool | True iff passed after exactly attempt 1 (attempts_used == 1) |

### Pseudo-code

```
repair_problem_leveled(model_ref, tokenizer, problem, fix_level, max_attempts=None, is_openai=False):
    max_attempts = max_attempts or CONFIG["max_repair_attempts"]
    error_types_seen = []
    prompt = initial_prompt(problem)
    code = extract_code_block(generate_code(model_ref, tokenizer, prompt, is_openai))
    passed, raw_error = execute_and_check(code, problem)
    if passed:
        return {"passed": True, "attempts_used": 0, "error_types_seen": [], "first_iter_success": False}

    for attempt in range(1, max_attempts + 1):
        err = parse_compiler_output(raw_error, code)
        error_types_seen.append(err.error_type)
        repair_prompt = format_leveled_prompt(err, code, fix_level)
        code = extract_code_block(generate_code(model_ref, tokenizer, repair_prompt, is_openai))
        passed, raw_error = execute_and_check(code, problem)
        if passed:
            return {"passed": True, "attempts_used": attempt, "error_types_seen": error_types_seen,
                     "first_iter_success": attempt == 1}
    return {"passed": False, "attempts_used": max_attempts, "error_types_seen": error_types_seen,
             "first_iter_success": False}
```

### Subtasks [3/9 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | repair_problem_leveled core loop | Mirror repair_problem, use format_leveled_prompt(fix_level) |
| L-3-2 | first_iter_success tracking | Set flag only when attempts_used==1 |
| L-3-3 | Self-check | assert on synthetic model_ref stub: level0 loop terminates, dict keys present |

---

## A-4: Error Instance Collection (`experiment.py`) [Complexity: 11, Budget: 11]

**Applied**: Standard PyTorch — stage-1 generation/filter pipeline, stratified sample cap

### API Signatures

```python
from typing import Dict, List
from evaluate import load_benchmark_problems
from models import load_hf_model, generate_code
from repair_loop import extract_code_block, execute_and_check, initial_prompt, parse_compiler_output
from config import CONFIG

def collect_error_instances(model_name: str, benchmark: str) -> List[Dict]:
    """Generate initial code per problem, keep failures. Returns list of error instance dicts."""
    ...
```

### Tensor / Return Shapes

| Field | Type | Note |
|-------|------|------|
| error_id | str | f"{benchmark}_{problem_idx}" |
| problem | Dict | original problem dict |
| initial_code | str | failing generated code |
| error_type | str | from parse_compiler_output |

### Pseudo-code

```
collect_error_instances(model_name, benchmark):
    problems = load_benchmark_problems(benchmark)
    is_openai = model_name in CONFIG["openai_models"]
    model_ref, tokenizer = (None, None) if is_openai else load_hf_model(model_name)
    instances = []
    for i, problem in enumerate(problems):
        code = extract_code_block(generate_code(model_ref, tokenizer, initial_prompt(problem), is_openai))
        passed, raw_error = execute_and_check(code, problem)
        if not passed:
            err = parse_compiler_output(raw_error, code)
            instances.append({"error_id": f"{benchmark}_{i}", "problem": problem,
                               "initial_code": code, "error_type": err.error_type})
        if len(instances) >= CONFIG["target_error_instances"]:
            break
    return instances
```

### Subtasks [3/11 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Generate + check loop | Reuse initial_prompt/execute_and_check, cap at target_error_instances |
| L-4-2 | Error type stratification hook | Tag error_type via parse_compiler_output for later stratified sampling |
| L-4-3 | Self-check | assert list of dicts has required keys; empty benchmark -> empty list, no crash |

---

## A-5: Level Sweep Orchestration (`experiment.py`) [Complexity: 13, Budget: 12]

**Applied**: KB pattern — within-subject repeated-measures with seeded per-subject randomization (Latin-square-free simple shuffle)

### API Signatures

```python
import random
from typing import List, Dict
from repair_loop import repair_problem_leveled
from models import load_hf_model
from config import CONFIG

def run_level_sweep(model_name: str, benchmark: str, levels: List[int], n_reps: int = 3) -> List[Dict]:
    """Run all levels per error instance, order randomized per error_id (seeded). Returns flat record list."""
    ...
```

### Tensor / Return Shapes (per record)

| Field | Type | Note |
|-------|------|------|
| error_id | str | ties repeated-measures rows together |
| model | str | model_name |
| benchmark | str | benchmark name |
| level | int | fix specificity level |
| rep | int | repetition index 0..n_reps-1 |
| passed | bool | from repair_problem_leveled |
| attempts_used | int | |
| first_iter_success | bool | |
| error_type | str | instance's stratified error type |

### Pseudo-code

```
run_level_sweep(model_name, benchmark, levels, n_reps=3):
    instances = collect_error_instances(model_name, benchmark)
    is_openai = model_name in CONFIG["openai_models"]
    model_ref, tokenizer = (None, None) if is_openai else load_hf_model(model_name)
    rng = random.Random(CONFIG["level_order_seed"])
    records = []
    for inst in instances:
        for rep in range(n_reps):
            order = levels[:]
            rng.shuffle(order)             # seeded, deterministic across runs given same seed+call order
            for level in order:
                result = repair_problem_leveled(model_ref, tokenizer, inst["problem"], level,
                                                 is_openai=is_openai)
                records.append({"error_id": inst["error_id"], "model": model_name,
                                 "benchmark": benchmark, "level": level, "rep": rep,
                                 "error_type": inst["error_type"], **result})
    return records
```

### Subtasks [4/12 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Instance + model setup | collect_error_instances + load_hf_model / openai branch |
| L-5-2 | Seeded per-instance-per-rep shuffle | rng.shuffle(order) using CONFIG["level_order_seed"] |
| L-5-3 | Level loop + record assembly | Call repair_problem_leveled, flatten into record dict |
| L-5-4 | Self-check | assert len(records) == len(instances)*n_reps*len(levels); all levels present per (error_id,rep) |

---

## A-6: Statistical Analysis (`analysis.py`) [Complexity: 12, Budget: 12]

**Applied**: KB pattern — mixed-effects logistic/linear polynomial contrast via statsmodels MixedLM

### API Signatures

```python
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from typing import Dict

def build_results_dataframe(records: List[Dict]) -> pd.DataFrame: ...
# columns: error_id, model, benchmark, level, rep, passed, attempts_used, first_iter_success, error_type
# passed cast to int for regression

def fit_quadratic_contrast(df: pd.DataFrame) -> Dict:
    """success ~ level + level^2, random intercepts (1|error_id), (1|model).
    Returns {"quad_coef": float, "quad_pval": float, "peak_level": int}."""
    ...

def check_gate_criteria(fit_result: Dict, df: pd.DataFrame) -> Dict:
    """Returns {"gate_passed": bool, "quad_negative": bool, "quad_significant": bool,
                "peak_at_1_or_2": bool, "level1_2_beat_0": bool, "level1_2_beat_3": bool}."""
    ...
```

### Pseudo-code

```
build_results_dataframe(records):
    df = pd.DataFrame(records)
    df["success"] = df["passed"].astype(int)
    return df

fit_quadratic_contrast(df):
    df = df.copy()
    df["level_sq"] = df["level"] ** 2
    # statsmodels MixedLM: single random-effect grouping (error_id); model effect added as fixed dummy
    # since statsmodels mixedlm supports one grouping factor -> group by error_id, add model as fixed covariate
    md = smf.mixedlm("success ~ level + level_sq + C(model)", df, groups=df["error_id"])
    fit = md.fit(reml=False)
    quad_coef = fit.params["level_sq"]
    quad_pval = fit.pvalues["level_sq"]
    means = df.groupby("level")["success"].mean()
    peak_level = int(means.idxmax())
    return {"quad_coef": quad_coef, "quad_pval": quad_pval, "peak_level": peak_level}

check_gate_criteria(fit_result, df):
    means = df.groupby("level")["success"].mean()
    quad_negative = fit_result["quad_coef"] < 0
    quad_significant = fit_result["quad_pval"] < 0.05
    peak_at_1_or_2 = fit_result["peak_level"] in (1, 2)
    mid = max(means.get(1, 0), means.get(2, 0))
    level1_2_beat_0 = mid > means.get(0, 0)
    level1_2_beat_3 = mid > means.get(3, 0)
    gate_passed = quad_negative and quad_significant and peak_at_1_or_2
    return {"gate_passed": gate_passed, "quad_negative": quad_negative,
            "quad_significant": quad_significant, "peak_at_1_or_2": peak_at_1_or_2,
            "level1_2_beat_0": level1_2_beat_0, "level1_2_beat_3": level1_2_beat_3}
```

### Subtasks [4/12 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | build_results_dataframe | records -> DataFrame, success column |
| L-6-2 | fit_quadratic_contrast | MixedLM with level+level_sq fixed, error_id random group |
| L-6-3 | check_gate_criteria | Primary + secondary gate checks per PRD Section 6 |
| L-6-4 | Self-check | assert on synthetic inverted-U data: quad_coef<0, peak_level in {1,2} |

---

## A-7: Visualization Suite (`visualize.py`) [Complexity: 8, Budget: 8]

**Applied**: Standard matplotlib/seaborn — reuse H-E1 save-to-file pattern

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict

def plot_gate_metrics(df: pd.DataFrame) -> str: ...          # bar: level vs mean success rate
def plot_inverted_u_curve(df: pd.DataFrame, fit_result: Dict) -> str: ...  # scatter + quadratic fit line
def plot_model_heatmap(df: pd.DataFrame) -> str: ...          # rows=model, cols=level, cell=success rate
def plot_error_type_breakdown(df: pd.DataFrame) -> str: ...   # grouped bar: error_type x level
def plot_iterations_per_level(df: pd.DataFrame) -> str: ...   # box/violin: attempts_used by level (passed only)
```

All return saved PNG file path under `CONFIG["figures_dir"]`.

### Subtasks [2/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | 5 plot functions | Each: groupby -> matplotlib/seaborn chart -> savefig -> return path |
| L-7-2 | Self-check | assert each function returns existing file path on synthetic df |

---

## A-8: Config & Integration (`config.py`, `run_poc.py`) [Complexity: 7, Budget: 7]

**Applied**: Standard PyTorch — extend CONFIG dict, orchestrate pipeline end-to-end

### API Signatures

```python
# config.py
CONFIG.update({
    "fix_levels": [0, 1, 2, 3],
    "n_repetitions": 3,
    "level_order_seed": 42,
    "target_error_instances": 500,
})

# run_poc.py
def main() -> None: ...
```

### Pseudo-code

```
main():
    all_records = []
    for model_name in CONFIG["models"]:
        for benchmark in CONFIG["benchmarks"]:
            all_records += run_level_sweep(model_name, benchmark, CONFIG["fix_levels"], CONFIG["n_repetitions"])
    df = build_results_dataframe(all_records)
    fit_result = fit_quadratic_contrast(df)
    gate = check_gate_criteria(fit_result, df)
    figs = {
        "gate_metrics": plot_gate_metrics(df),
        "inverted_u": plot_inverted_u_curve(df, fit_result),
        "model_heatmap": plot_model_heatmap(df),
        "error_breakdown": plot_error_type_breakdown(df),
        "iterations": plot_iterations_per_level(df),
    }
    json.dump({"fit_result": fit_result, "gate": gate, "figures": figs},
              open(CONFIG["results_path"], "w"), indent=2)
```

### Subtasks [2/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | CONFIG.update + main() orchestration | Wire full pipeline, write results.json |
| L-8-2 | Self-check | assert results.json written with fit_result/gate/figures keys after main() on tiny synthetic run |

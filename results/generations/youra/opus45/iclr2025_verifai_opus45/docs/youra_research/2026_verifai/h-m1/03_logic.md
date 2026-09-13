# Logic: H-M1 — Granularity Effect on Repair Success

**Applied**: Standard scipy one-way ANOVA pattern, subprocess execution pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified by direct file read (Serena project activation returned error; files read manually)
**Analyzed Path**: `docs/youra_research/20260330_verifai/h-e1/code/`
**Relevant Symbols**:
- `CodeGenerator.__init__(self, config: ExperimentConfig)` — takes ExperimentConfig, not RepairConfig
- `CodeGenerator.load(self) -> None` — lazy model load, must call before generate()
- `CodeGenerator.generate(self, prompt: str) -> str` — single param `prompt`, returns extracted code
- `execute_code(code: str, tests: list[str], timeout: int = 10) -> tuple[ErrorCategory, Optional[str]]`
- `categorize_stderr(returncode: int, stderr: str) -> ErrorCategory`

---

## External Dependencies API

### API Signatures (From Actual H-E1 Code)

```python
# From: h-e1/code/model.py (ACTUAL CODE)
class CodeGenerator:
    def __init__(self, config: ExperimentConfig):
        """Initialize; call load() before generate()."""
        ...

    def load(self) -> None:
        """Load tokenizer and model (float16, device_map='auto')."""
        ...

    def generate(self, prompt: str) -> str:
        """Single inference. Returns extracted code string."""
        # Extracts between [BEGIN]/[DONE] markers
        ...

# From: h-e1/code/executor.py (ACTUAL CODE)
def execute_code(
    code: str,
    tests: list[str],      # ← parameter name is 'tests', not 'test_list'
    timeout: int = 10,
) -> tuple[ErrorCategory, Optional[str]]:
    """Returns (ErrorCategory, stderr|None)."""
    ...
```

**Verified from**: `h-e1/code/model.py`, `h-e1/code/executor.py` (actual implementation)

**Critical Notes**:
- `CodeGenerator` takes `ExperimentConfig` (H-E1). H-M1 must build a compatible config object or subclass.
- `generate()` uses `[BEGIN]/[DONE]` markers — repair prompts should include these markers.
- `execute_code` param is `tests`, not `test_list`.
- `generate_batch()` calls `format_prompt()` from H-E1 data.py — do NOT use for repair; call `generate()` directly with custom prompt.

---

## A-5: Repair Pipeline [Complexity: 14, Budget: 4 subtasks]

**Applied**: Standard checkpoint/resume pattern

### API Signatures

```python
# repair.py
import sys
sys.path.insert(0, "../h-e1/code")
from model import CodeGenerator
from config import ExperimentConfig as H_E1_Config

from config import RepairConfig
from feedback import construct_repair_prompt
from executor import execute_and_verify

def run_repair_experiment(
    runtime_cases: list[dict],      # [{task_id, generated_code, category, stderr}]
    mbpp_index: dict[int, dict],    # {task_id: {text, test_list}}
    generator: CodeGenerator,
    config: RepairConfig,
) -> list[dict]:
    """Run 304 cases × 5 granularity levels = 1,520 repair attempts.

    Returns list of {task_id, granularity, repaired_code, success, execution_time}.
    Checkpoints after each case (5 results at a time).
    """
    ...

def load_checkpoint(checkpoint_path: str) -> list[dict]:
    """Load partial results; return [] if file missing."""
    ...

def save_checkpoint(results: list[dict], checkpoint_path: str) -> None:
    """Persist results list to JSON checkpoint."""
    ...

def _build_h_e1_config(repair_config: RepairConfig) -> H_E1_Config:
    """Build H-E1 ExperimentConfig from RepairConfig for CodeGenerator init."""
    ...
```

### Pseudo-code (non-trivial loop with checkpoint/resume)

```
checkpoint_path = config.results_dir + "/checkpoint.json"
results = load_checkpoint(checkpoint_path)
done_keys = {(r["task_id"], r["granularity"]) for r in results}

for case in runtime_cases:
    task_id = case["task_id"]
    task_info = mbpp_index.get(task_id)
    if task_info is None: continue
    error_info = parse_error_info(case["stderr"] or "")

    for granularity in GRANULARITY_LEVELS:
        if (task_id, granularity) in done_keys: continue

        prompt = construct_repair_prompt(
            case["generated_code"], task_info["text"], error_info, granularity
        )
        t0 = time.time()
        repaired_code = generator.generate(prompt)
        elapsed = time.time() - t0

        success = execute_and_verify(repaired_code, task_info["test_list"])
        results.append({
            "task_id": task_id,
            "granularity": granularity,
            "repaired_code": repaired_code,
            "success": success,
            "execution_time": elapsed,
        })

    save_checkpoint(results, checkpoint_path)  # after all 5 granularities per case

return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | _build_h_e1_config | Map RepairConfig fields to ExperimentConfig for CodeGenerator |
| L-5-2 | checkpoint load/save | load_checkpoint / save_checkpoint JSON helpers |
| L-5-3 | repair loop core | Outer case loop + inner granularity loop with done_keys skip |
| L-5-4 | execute_and_verify | Binary wrapper: calls execute_code, returns bool (all tests pass) |

---

## A-6: ANOVA Analysis [Complexity: 11, Budget: 2 subtasks]

**Applied**: scipy.stats.f_oneway, eta-squared formula (SS_between / SS_total)

### API Signatures

```python
# analyze.py
import numpy as np
from scipy.stats import f_oneway
from config import GRANULARITY_LEVELS

def aggregate_by_granularity(results: list[dict]) -> dict[str, list[int]]:
    """Group binary success values by granularity.

    Returns: {"G0": [0,1,...], "G1": [...], ..., "G4": [...]}
    """
    ...

def run_anova(groups: dict[str, list[int]]) -> dict:
    """One-way ANOVA across 5 granularity groups.

    Returns:
        {
          "f_statistic": float,
          "p_value": float,
          "eta_squared": float,       # SS_between / SS_total
          "gate_passed": bool,        # p_value < anova_alpha
          "success_rates": {G0..G4: float},
          "n_per_group": int,
        }
    """
    ...
```

### Pseudo-code

```
groups_list = [np.array(groups[g]) for g in GRANULARITY_LEVELS]
f_stat, p_value = f_oneway(*groups_list)

all_data = np.concatenate(groups_list)
grand_mean = np.mean(all_data)
ss_total = np.sum((all_data - grand_mean) ** 2)
ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups_list)
eta_squared = ss_between / ss_total if ss_total > 0 else 0.0

success_rates = {g: float(np.mean(groups[g])) for g in GRANULARITY_LEVELS}
gate_passed = bool(p_value < config.anova_alpha)  # default 0.05
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | aggregate_by_granularity | Dict grouping from flat results list |
| L-6-2 | run_anova | f_oneway + eta_squared computation + gate |

---

## A-7: Tukey HSD Post-hoc [Complexity: 10, Budget: 2 subtasks]

**Applied**: scipy.stats.tukey_hsd (available since scipy 1.8)

### API Signatures

```python
# analyze.py (continued)
from scipy.stats import tukey_hsd

def run_posthoc(groups: dict[str, list[int]]) -> dict:
    """Tukey HSD pairwise comparisons across all granularity pairs.

    Returns pairwise dict only if called (caller checks ANOVA p < 0.05):
        {
          "G0_vs_G1": {"statistic": float, "p_value": float, "significant": bool},
          "G0_vs_G2": {...},
          ...  # C(5,2) = 10 pairs
        }
    """
    ...
```

### Pseudo-code

```
groups_list = [np.array(groups[g], dtype=float) for g in GRANULARITY_LEVELS]
tukey_result = tukey_hsd(*groups_list)

pairwise = {}
for i, g1 in enumerate(GRANULARITY_LEVELS):
    for j, g2 in enumerate(GRANULARITY_LEVELS):
        if i >= j: continue
        key = f"{g1}_vs_{g2}"
        pairwise[key] = {
            "statistic": float(tukey_result.statistic[i, j]),
            "p_value": float(tukey_result.pvalue[i, j]),
            "significant": bool(tukey_result.pvalue[i, j] < 0.05),
        }
return pairwise
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | run_posthoc | scipy.stats.tukey_hsd call + pairwise dict construction |
| L-7-2 | integration guard | Caller in train.py: only call run_posthoc if metrics["gate_passed"] |

---

## Key Interface Contracts

| Variable | Type | Note |
|----------|------|------|
| runtime_cases | list[dict] | {task_id, generated_code, category, stderr} from H-E1 |
| mbpp_index | dict[int, dict] | {task_id: {text, test_list}} |
| groups | dict[str, list[int]] | {"G0": [0,1,...], ..., "G4": [...]} each len=304 |
| repair result | dict | {task_id, granularity, repaired_code, success, execution_time} |
| ANOVA output | dict | {f_statistic, p_value, eta_squared, gate_passed, success_rates, n_per_group} |
| posthoc output | dict | 10 pairs: "Gi_vs_Gj" -> {statistic, p_value, significant} |

## Construct Repair Prompt Note

The H-E1 `CodeGenerator.generate()` extracts code between `[BEGIN]` and `[DONE]` markers.
`construct_repair_prompt` must include these markers in the output template:

```python
# feedback.py — construct_repair_prompt return template (end of prompt):
"Please provide the corrected code.\n[BEGIN]\n"
# Model should output corrected code then [DONE]
```

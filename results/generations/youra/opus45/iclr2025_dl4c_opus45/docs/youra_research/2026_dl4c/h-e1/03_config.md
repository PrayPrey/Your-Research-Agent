# Config: H-E1 - Alignment-Induced Error Type Divergence

**Hypothesis Type**: EXISTENCE | **Gate**: MUST_WORK
**Generated**: 2026-03-24

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

Applied: Standard Python dataclass pattern (single fixed config for EXISTENCE PoC)

---

## A-3: Execution & Error Capture [Complexity: 12, Budget: 4 subtasks]

**Applied**: Standard EXISTENCE PoC - single fixed config, no grid

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Models
    rl_model_id: str = "Salesforce/codet5-large-ntp-py"
    dpo_model_id: str = "codellama/CodeLlama-7b-Instruct-hf"

    # Generation (from CodeRL paper, Le et al. 2022)
    temperature: float = 0.8
    top_p: float = 0.95
    max_new_tokens: int = 512
    # Non-standard: n_samples=10 matches CodeRL evaluation protocol (pass@10)
    n_samples: int = 10
    seed: int = 42

    # Execution
    # Non-standard: timeout=5 matches EvalPlus default; FR-3.2 specifies 3-5s
    timeout: int = 5

    # Paths
    output_dir: str = "outputs"
    figures_dir: str = "figures"

    # Statistical thresholds (from Phase 2B success criteria)
    chi2_p_threshold: float = 0.05
    cramers_v_threshold: float = 0.05


CONFIG = ExperimentConfig()
```

### YAML Schema

```yaml
experiment_config:
  rl_model_id:
    type: str
    default: "Salesforce/codet5-large-ntp-py"
  dpo_model_id:
    type: str
    default: "codellama/CodeLlama-7b-Instruct-hf"
  temperature:
    type: float
    default: 0.8
  top_p:
    type: float
    default: 0.95
  max_new_tokens:
    type: int
    default: 512
  n_samples:
    type: int
    default: 10
  seed:
    type: int
    default: 42
  timeout:
    type: int
    default: 5
    unit: seconds
  output_dir:
    type: str
    default: "outputs"
  figures_dir:
    type: str
    default: "figures"
  chi2_p_threshold:
    type: float
    default: 0.05
  cramers_v_threshold:
    type: float
    default: 0.05
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | EvalPlus sandbox setup | Configure execution environment, verify evalplus import and sandbox isolation |
| C-3-2 | Timeout handling | Wrap execution with timeout=5 per EvalPlus default; catch TimeoutError as runtime error |
| C-3-3 | Error trace capture | Capture full traceback string on failure; store None on PASS |
| C-3-4 | Results persistence | Save execution results to outputs/execution_results.json with schema {task_id, model, sample_idx, status, error_trace} |

---

## A-4: Error Classification & Statistics [Complexity: 10, Budget: 4 subtasks]

**Applied**: Standard EXISTENCE PoC - ICSE 2025 taxonomy, fixed thresholds from Phase 2B

### Configuration (Python Dataclass)

Same `ExperimentConfig` as A-3 (shared config). Statistical thresholds:

```python
# Accessed from CONFIG instance in analyze.py
chi2_p_threshold: float = 0.05   # p < 0.05 for significance
cramers_v_threshold: float = 0.05  # V > 0.05 for small-medium effect
```

Error category constants (fixed taxonomy - not tunable):

```python
ERROR_CATEGORIES = ["syntax", "runtime", "assertion"]

SYNTAX_ERRORS = ["syntaxerror", "indentationerror"]
RUNTIME_ERRORS = [
    "typeerror", "nameerror", "attributeerror",
    "indexerror", "keyerror", "valueerror",
    "zerodivisionerror", "recursionerror", "timeout"
]
ASSERTION_ERRORS = ["assertionerror", "expected"]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Error classifier | Implement classify_error(error_trace) using ICSE 2025 taxonomy constants above |
| C-4-2 | Contingency table | Build 2x3 numpy array from RL/DPO failure classifications; exclude PASS samples |
| C-4-3 | Chi-square + Cramers V | Run scipy.stats.chi2_contingency; compute V = sqrt(chi2 / (n * (min(r,c)-1))); compare against thresholds |
| C-4-4 | Direction check + metrics save | Check rl_prop < dpo_prop for syntax+runtime; save all metrics to outputs/metrics.json with gate_pass boolean |

---

## Full Config Reference (code/config.py)

Single config class used across all modules:

```python
from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    # Models
    rl_model_id: str = "Salesforce/codet5-large-ntp-py"
    dpo_model_id: str = "codellama/CodeLlama-7b-Instruct-hf"

    # Generation (from CodeRL paper, Le et al. 2022)
    temperature: float = 0.8
    top_p: float = 0.95
    max_new_tokens: int = 512
    n_samples: int = 10   # CodeRL evaluation protocol (pass@10)
    seed: int = 42

    # Execution
    timeout: int = 5      # EvalPlus default (seconds)

    # Paths
    output_dir: str = "outputs"
    figures_dir: str = "figures"

    # Statistical thresholds (Phase 2B success criteria)
    chi2_p_threshold: float = 0.05
    cramers_v_threshold: float = 0.05


CONFIG = ExperimentConfig()
```

---

*Generated by Phase 3 Config Agent | Anonymous Research Pipeline*
*Hypothesis: H-E1 | Type: EXISTENCE | Gate: MUST_WORK*

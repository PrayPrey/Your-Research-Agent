# Architecture: H-E1 (EVAF Existence PoC)

**Type**: EXISTENCE (PoC) — minimal architecture, 4-8 Epic tasks
**Applied**: RLTF-style unit test execution harness (subprocess + timeout gating)
**Applied**: HumanEval standard evaluation protocol (bigcode-evaluation-harness pattern, 3.0s/test timeout)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing codebase, no base hypothesis
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure

```
h-e1/code/
├── data.py          # HumanEval loading + baseline-failure filtering
├── model.py         # CodeT5-770M baseline + CodeLlama-7b-Instruct feedback gen
├── gating.py         # Code extraction + sandboxed unit test execution
├── metrics.py         # Accept rate / coverage / rejection breakdown
├── visualize.py        # 3 required figures (matplotlib)
├── train.py           # Orchestrates: load -> baseline -> EVAF -> metrics -> figures
└── config.py          # Fixed config (model ids, temp, timeout, seed)
```

---

## Modules

### DataLoader (`data.py`)

**Dependencies**: config.py

```python
def load_humaneval() -> Dataset: ...  # openai_humaneval, split="test"
def extract_problem(item: dict) -> dict: ...  # {task_id, prompt, entry_point, test, canonical_solution}
```

### BaselineModel (`model.py`)

**Dependencies**: config.py

```python
class BaselineModel:
    def __init__(self, model_id: str = "Salesforce/codet5-large"): ...
    def generate(self, prompt: str) -> str: ...  # deterministic, seeded
```

### FeedbackModel (`model.py`)

**Dependencies**: config.py

```python
class FeedbackModel:
    def __init__(self, model_id: str = "codellama/CodeLlama-7b-Instruct-hf",
                 temperature: float = 0.2, max_tokens: int = 512): ...
    def critique(self, problem: dict, failing_code: str) -> str: ...  # raw AI response
```

### Gating (`gating.py`)

**Dependencies**: model.py (output only, no import)

```python
def extract_code_from_response(response: str) -> str | None: ...  # ```python fenced block
def run_unit_tests(code: str, test_code: str, entry_point: str, timeout: float = 3.0) -> dict: ...
    # -> {"all_passed": bool, "error": str | None}
def evaf_gate(problem: dict, failing_code: str, feedback_model: "FeedbackModel") -> dict: ...
    # -> {"accepted": bool, "suggestion": str|None, "has_code_suggestion": bool, "rejection_reason": str|None}
```

### Metrics (`metrics.py`)

**Dependencies**: gating.py (consumes result dicts)

```python
def compute_metrics(results: list[dict]) -> dict: ...
    # -> {"accept_rate": float, "coverage": float, "rejection_breakdown": Counter}
```

### Visualization (`visualize.py`)

**Dependencies**: metrics.py

```python
def plot_gate_metrics(metrics: dict, out_path: str) -> None: ...       # bar chart, 20-60% target zone (required)
def plot_accept_distribution(results: list[dict], out_path: str) -> None: ...  # histogram
def plot_rejection_breakdown(metrics: dict, out_path: str) -> None: ...     # pie chart
```

### Orchestration (`train.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # 1. load_humaneval()
    # 2. BaselineModel.generate() per problem -> filter to failing (~80-120)
    # 3. evaf_gate() per failing problem -> results list
    # 4. compute_metrics(results)
    # 5. plot_gate_metrics / plot_accept_distribution / plot_rejection_breakdown
    # 6. save results.json + metrics.json to {hypothesis_folder}/results/
```

### Config (`config.py`)

```python
BASELINE_MODEL_ID = "Salesforce/codet5-large"
FEEDBACK_MODEL_ID = "codellama/CodeLlama-7b-Instruct-hf"
TEMPERATURE = 0.2
MAX_TOKENS = 512
TEST_TIMEOUT_S = 3.0
SEED = 42
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup + config | Project skeleton, config.py, dependency install | 4 | 1+1+1+1 |
| A-2 | Data loading | HumanEval load + problem extraction | 5 | 2+1+1+1 |
| A-3 | Baseline model | CodeT5-770M load + generate + failure filtering | 9 | 3+2+3+1 |
| A-4 | Feedback model | CodeLlama-7b-Instruct load + critique generation | 9 | 3+2+3+1 |
| A-5 | Execution gating | Code extraction + sandboxed subprocess test runner | 13 | 4+2+4+3 |
| A-6 | EVAF pipeline integration | Wire baseline -> feedback -> gating in train.py | 10 | 2+4+2+2 |
| A-7 | Metrics computation | accept_rate, coverage, rejection breakdown | 5 | 2+1+1+1 |
| A-8 | Visualization + reporting | 3 required figures, results/metrics JSON output | 7 | 3+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5, A-6], Low(4-8): [A-1, A-2, A-7, A-8]

---

## Notes

- No training loop — inference-only pipeline (per PRD FR-1 to FR-5).
- Sandboxing (NFR-3): run `run_unit_tests` via `subprocess.run` with `timeout=3.0`, restricted environment, no network/filesystem writes (ponytail: subprocess timeout only, add `seccomp`/container isolation if untrusted code risk increases).
- Single fixed config, no ablation modules — EXISTENCE tier.

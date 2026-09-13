# Architecture: H-E1 (Static Analysis Tool Coverage Validation)

**Type**: EXISTENCE (PoC) | **Gate**: MUST_WORK

Applied: subprocess-wrapper-with-timeout-pattern (KB match low-relevance; using standard practice: subprocess.run + timeout + try/except)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure (Minimal - EXISTENCE)

- `code/dataset.py` - load HumanEval + MBPP, extract + validate samples
- `code/sa_tools.py` - pylint/mypy/radon subprocess wrappers
- `code/run.py` - main loop: iterate samples, run tools, aggregate, write results
- `code/config.py` - fixed config (timeouts, paths, dataset sizes)
- `requirements.txt` - pinned versions

No `model.py`/`evaluate.py` split needed — this experiment has no model, just tool invocation + aggregation.

---

## Module Interfaces

### config.py

```python
TIMEOUT_SEC: int = 30
HUMANEVAL_N: int = 164
MBPP_N: int = 500
RESULTS_DIR: str = "results"
```

### dataset.py (`code/dataset.py`)

**Dependencies**: config, datasets (HF), ast

```python
@dataclass
class Sample:
    task_id: str
    source: str  # dataset origin: "humaneval" | "mbpp"
    code: str

def load_humaneval() -> list[Sample]: ...
def load_mbpp() -> list[Sample]: ...
def validate_syntax(sample: Sample) -> bool: ...  # ast.parse
def load_all_samples() -> list[Sample]: ...  # combines + filters invalid, len==664
```

### sa_tools.py (`code/sa_tools.py`)

**Dependencies**: subprocess, json, tempfile, config

```python
@dataclass
class ToolResult:
    success: bool
    metric: float | int | None
    error: str | None

def run_pylint(code_path: str, timeout: int = 30) -> ToolResult: ...
def run_mypy(code_path: str, timeout: int = 30) -> ToolResult: ...
def run_radon(code_path: str, timeout: int = 30) -> ToolResult: ...
def run_sa_tool(tool: str, code_path: str, timeout: int = 30) -> ToolResult: ...  # dispatch
```

### run.py (`code/run.py`)

**Dependencies**: dataset, sa_tools, json, pathlib

```python
def write_temp_file(sample: Sample) -> str: ...  # returns path, UTF-8
def process_sample(sample: Sample) -> dict: ...  # runs all 3 tools, returns per-sample record
def aggregate(records: list[dict]) -> dict: ...  # valid_rates, min_valid_rate, pass
def main() -> None: ...  # orchestrates full run, writes 3 result JSON files
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & config | Project skeleton, requirements.txt, config.py | 5 | 1+1+1+2 |
| A-2 | Dataset loading | HumanEval clone/parse + MBPP HF load + extraction | 9 | 3+3+2+1 |
| A-3 | Syntax validation | ast.parse filter, ensure 664 valid samples | 4 | 1+1+1+1 |
| A-4 | Pylint wrapper | subprocess + JSON parse + timeout + error capture | 7 | 2+1+2+2 |
| A-5 | Mypy wrapper | subprocess + JSON parse + timeout + error capture | 7 | 2+1+2+2 |
| A-6 | Radon wrapper | subprocess cc --json + avg complexity calc | 7 | 2+1+2+2 |
| A-7 | Run loop & aggregation | Main orchestration, temp files, aggregate metrics, write 3 output JSONs | 10 | 3+3+2+2 |
| A-8 | Full run + pass/fail check | Execute on 664 samples, verify ≥95% thresholds, produce summary | 6 | 1+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-7], Low(4-8): [A-1, A-3, A-4, A-5, A-6, A-8]

---

## External Dependencies

None — green-field, no base hypothesis code to reuse.

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (Applied line only)
- [x] Interface-only module code
- [x] 8 Epic tasks (within 4-8 EXISTENCE range) with complexity
- [x] Codebase Analysis section included (green-field)
- [x] Total length < 500 lines

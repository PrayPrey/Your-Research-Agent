# Architecture: H-E1 (EXISTENCE / PoC)

**Applied**: Archon unavailable — proceeding with brief-specified patterns (stdlib traceback + regex extraction).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis or existing codebase.

---

## File Structure

```
h-e1/code/
├── config.py
├── model.py
├── train.py       # data prep + signal generation (no real "training")
├── evaluate.py
└── figures/        # output PNGs
```

---

## Module Definitions

### config.py

**Dependencies**: none

```python
DATASET_HUMANEVAL = "openai/openai_humaneval"
DATASET_MBPP = "mbpp"
SAMPLE_SIZE = 100
CONDITIONS = ["C1", "C2", "C3", "C4", "C5", "C6"]
EXTRACTION_RATE_TARGET = 0.95
LLM_TEMP = 0.7
MAX_TRUNCATE_FRAMES = 3
RANDOM_SEED = 42
OUTPUT_DIR = "results"
FIGURES_DIR = "figures"
```

### model.py

**Dependencies**: config

```python
import re
from dataclasses import dataclass

@dataclass
class ASComponents:
    AS_loc: int
    AS_state: int
    AS_causal: int
    def is_valid(self) -> bool: ...

FILE_LINE_PATTERN: re.Pattern
VARIABLE_VALUE_PATTERN: re.Pattern
TRACEBACK_FRAME_PATTERN: re.Pattern

def extract_AS_loc(signal_text: str) -> int: ...
def extract_AS_state(signal_text: str) -> int: ...
def extract_AS_causal(signal_text: str) -> int: ...
def extract_all_components(signal_text: str) -> ASComponents: ...

def truncate_trace(trace_output: str, max_frames: int) -> str: ...
def mask_values(trace_output: str) -> str: ...
def extract_error_only(error_output: str) -> str: ...
def extract_syntax_error(error_output: str) -> str: ...
def generate_signal_variants(error_output: str, trace_output: str) -> dict: ...
```

### train.py

**Dependencies**: config, model

```python
def load_datasets() -> list[dict]: ...
def generate_buggy_code(problem: dict, temp: float) -> str: ...
def run_pytest_capture(problem: dict, code: str) -> tuple[str, str]:
    """Returns (error_output, trace_output) for a failing case."""
    ...
def sample_failures(problems: list[dict], n: int, seed: int) -> list[dict]:
    """Stratified sample by error type."""
    ...
def build_signal_dataset() -> list[dict]:
    """For each of 100 failures, generate 6 signal variants.
    Returns list of {problem_id, condition, signal_text}."""
    ...
def main() -> None: ...
```

### evaluate.py

**Dependencies**: config, model, train

```python
def compute_extraction_rate(results: list) -> dict[str, float]:
    """Per-component extraction rate."""
    ...
def verify_ordering(results_by_condition: dict) -> bool: ...
def compute_correlation_matrix(results: list) -> "np.ndarray": ...
def plot_extraction_rate_bar(rates: dict, out_path: str) -> None: ...
def plot_component_boxplots(results_by_condition: dict, out_path: str) -> None: ...
def plot_extraction_heatmap(results_by_condition: dict, out_path: str) -> None: ...
def plot_correlation_matrix(corr: "np.ndarray", out_path: str) -> None: ...
def main() -> None:
    """Load signals -> extract -> compute metrics -> save figures + CSV -> print PoC pass/fail."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load HumanEval+MBPP, generate buggy code, run pytest, stratified sample 100 failures | 12 | 4+3+3+2 |
| A-2 | Signal generation | Implement 6 condition variants (truncate/mask/error-only/syntax) | 8 | 3+2+2+1 |
| A-3 | AS extractors | Regex-based extract_AS_loc/state/causal + ASComponents dataclass | 7 | 2+1+3+1 |
| A-4 | Evaluation + metrics | Extraction rate, ordering check, correlation matrix | 6 | 2+2+1+1 |
| A-5 | Visualization + PoC gate | 4 figures, CSV export, pass/fail summary | 5 | 2+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1], Low(4-8): [A-2, A-3, A-4, A-5]

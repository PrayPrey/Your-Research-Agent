# Architecture: H-M1 (MECHANISM)

**Applied**: LLM-as-judge reconstruction evaluation pattern

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena MCP unavailable this session; read H-E1 code directly via file tools instead.
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 exposes `StructuredError` dataclass + `parse_compiler_output(raw_output, source_code)` in `errors.py`, `CONFIG` dict + `OPENAI_API_KEY` in `config.py`, and `generate_code(...)` OpenAI/HF wrapper with retry/backoff in `models.py`. No `data/error_pairs.json` exists yet in H-E1 output — H-M1 must include a task to build it from H-E1 run artifacts (or regenerate via `errors.py` + `prompts.py` on stored raw/structured pairs).

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| StructuredError, parse_compiler_output | `from errors import StructuredError, parse_compiler_output` | `h-e1/code/errors.py` |
| CONFIG, OPENAI_API_KEY | `from config import CONFIG, OPENAI_API_KEY` | `h-e1/code/config.py` |
| format_structured_prompt | `from prompts import format_structured_prompt` | `h-e1/code/prompts.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

Copy these three files verbatim into `h-m1/code/` (no package reuse across hypothesis folders) rather than adding cross-folder sys.path hacks.

## File Organization

- `h-m1/code/errors.py` (copied from H-E1)
- `h-m1/code/config.py` (new, M1-specific)
- `h-m1/code/judge.py`
- `h-m1/code/reconstruction.py`
- `h-m1/code/build_pairs.py`
- `h-m1/code/evaluate.py`
- `h-m1/code/visualize.py`
- `h-m1/code/run_poc.py`
- `h-m1/data/error_pairs.json` (generated)

## Modules

### config.py (`h-m1/code/config.py`)

**Dependencies**: none

```python
CONFIG = {
    "judge_model": "gpt-4",  # or "claude-3-sonnet-20240229"
    "judge_provider": "openai",  # "openai" | "anthropic"
    "temperature": 0.0,
    "max_tokens": 500,
    "fields": ["error_type", "line_number", "message", "context"],
    "min_samples": 500,
    "accuracy_threshold": 0.95,
    "pass_rate_threshold": 0.90,
    "max_retries": 5,
    "backoff_base_sec": 2.0,
    "error_pairs_path": "data/error_pairs.json",
    "results_path": "outputs/results.json",
    "figures_dir": "outputs/figures/",
}
```

### build_pairs.py (`h-m1/code/build_pairs.py`)

**Dependencies**: errors.py (StructuredError)

```python
def load_or_build_error_pairs(h_e1_data_dir: str, out_path: str) -> list[dict]:
    """Load h-e1/data/error_pairs.json if present, else derive from
    h-e1 experiment.log / results.json raw+structured error strings."""
    ...

def save_pairs(pairs: list[dict], out_path: str) -> None: ...
```

### judge.py (`h-m1/code/judge.py`)

**Dependencies**: config.py

```python
class JudgeLLM:
    def __init__(self, provider: str, model: str, temperature: float, max_tokens: int): ...
    def extract(self, prompt: str) -> dict: ...  # JSON field dict, retry+backoff on rate limit

def build_extraction_prompt(structured_error: str, fields: list[str]) -> str: ...
```

### reconstruction.py (`h-m1/code/reconstruction.py`)

**Dependencies**: errors.py (parse_compiler_output), judge.py

```python
class ReconstructionTest:
    def __init__(self, judge: JudgeLLM, fields: list[str]): ...
    def extract_from_raw(self, raw_error: str, source_code: str) -> dict: ...
    def extract_from_structured(self, structured_error: str) -> dict: ...
    def compute_accuracy(self, original: dict, reconstructed: dict) -> float: ...
    def run(self, error_pairs: list[dict]) -> dict: ...  # {mean_accuracy, per_sample, per_field, pass}
```

### evaluate.py (`h-m1/code/evaluate.py`)

**Dependencies**: reconstruction.py

```python
def compute_reconstruction_metrics(original_list: list[dict], reconstructed_list: list[dict],
                                    fields: list[str]) -> dict: ...
def per_error_type_breakdown(pairs: list[dict], results: dict) -> dict: ...
def gate_check(metrics: dict, acc_thresh: float, pass_thresh: float) -> bool: ...
```

### visualize.py (`h-m1/code/visualize.py`)

**Dependencies**: config.py

```python
def plot_gate_comparison(metrics: dict, out_path: str = None) -> None: ...
def plot_per_field_accuracy(metrics: dict, out_path: str = None) -> None: ...
def plot_accuracy_by_error_type(breakdown: dict, out_path: str = None) -> None: ...
```

### run_poc.py (`h-m1/code/run_poc.py`)

**Dependencies**: all above

```python
def main() -> None:
    """Load pairs -> run ReconstructionTest -> compute metrics ->
    gate_check -> save results.json -> generate figures."""
    ...
```

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Port H-E1 infra | Copy errors.py; write config.py | 5 | 2+1+1+1 |
| M-2 | Build error pairs dataset | Load/derive error_pairs.json (>=500 samples) from H-E1 outputs | 10 | 3+3+2+2 |
| M-3 | Implement JudgeLLM | OpenAI/Anthropic client with retry+backoff, JSON extraction prompt | 9 | 2+3+2+2 |
| M-4 | Implement ReconstructionTest | extract_from_raw/structured, compute_accuracy, run loop | 10 | 3+2+3+2 |
| M-5 | Implement evaluate.py metrics | mean/std/pass_rate, per-field, per-error-type breakdown | 8 | 2+2+2+2 |
| M-6 | Implement visualize.py | gate comparison, per-field, per-error-type figures | 7 | 2+1+2+2 |
| M-7 | Implement run_poc.py orchestration | wire pipeline end-to-end, save results | 8 | 2+3+1+2 |
| M-8 | Gate verification + logging | mechanism_log_message, verify_reconstruction_mechanism assertions | 5 | 1+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-2, M-3, M-4, M-5], Low(4-8): [M-1, M-6, M-7, M-8]

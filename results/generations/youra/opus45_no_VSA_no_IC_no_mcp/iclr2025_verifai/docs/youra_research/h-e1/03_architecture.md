# Architecture: h-e1 (EXISTENCE / PoC)

**Applied**: Structured error format pattern (StructuredError dataclass + prompt formatters, from experiment brief KB research)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch, single PoC comparing structured vs raw error prompts for code repair.

---

## File Structure

```
h-e1/code/
  config.py       # fixed config: models, datasets, repair attempts
  errors.py       # StructuredError + parse_compiler_output
  prompts.py       # format_structured_prompt, format_raw_prompt
  models.py        # model/tokenizer loading + generate_code (HF + OpenAI)
  repair_loop.py   # execute-test-repair loop, pass@1 tracking
  evaluate.py       # evalplus integration, metrics aggregation
  visualize.py       # figure generation
  train.py           # entrypoint: runs full comparison, saves results
```

---

## Modules

### StructuredError / Parser (`errors.py`)

**Dependencies**: none (stdlib `re`, `dataclasses`)

```python
@dataclass
class StructuredError:
    line_number: int
    error_type: str
    error_message: str
    code_context: list[str]

def parse_compiler_output(raw_output: str, source_code: str) -> StructuredError: ...
```

### Prompt Formatters (`prompts.py`)

**Dependencies**: errors.StructuredError

```python
def format_structured_prompt(error: StructuredError, original_code: str) -> str: ...
def format_raw_prompt(raw_output: str, original_code: str) -> str: ...
```

### Model Loading + Generation (`models.py`)

**Dependencies**: transformers, openai, config.py

```python
def load_hf_model(model_id: str) -> tuple: ...  # (model, tokenizer)
def generate_code(model_ref, tokenizer, prompt: str, is_openai: bool = False) -> str: ...
```

### Repair Loop (`repair_loop.py`)

**Dependencies**: errors.py, prompts.py, models.py, evalplus (execution)

```python
def execute_and_check(code: str, problem: dict) -> tuple[bool, str]:  # (passed, raw_error)
def repair_problem(model_ref, tokenizer, problem: dict, use_structured: bool,
                    max_attempts: int = 5, is_openai: bool = False) -> dict: ...
    # returns {passed, attempts_used, error_types_seen}
```

### Evaluation (`evaluate.py`)

**Dependencies**: repair_loop.py, evalplus

```python
def run_benchmark(model_name: str, benchmark: str, use_structured: bool) -> dict: ...
    # returns {pass_at_1, repair_success_rate, avg_attempts, error_breakdown}
def aggregate_results(all_results: list[dict]) -> dict: ...
```

### Visualization (`visualize.py`)

**Dependencies**: matplotlib, evaluate.py output

```python
def plot_gate_comparison(results: dict, out_path: str) -> None: ...  # required figure
def plot_repair_success(results: dict, out_path: str) -> None: ...
def plot_repair_iterations(results: dict, out_path: str) -> None: ...
def plot_error_type_heatmap(results: dict, out_path: str) -> None: ...
def plot_benchmark_comparison(results: dict, out_path: str) -> None: ...
```

### Config (`config.py`)

```python
MODELS = ["codellama/CodeLlama-7b-Instruct-hf", "codellama/CodeLlama-34b-Instruct-hf", "gpt-4"]
BENCHMARKS = ["humaneval", "mbpp"]
MAX_REPAIR_ATTEMPTS = 5
TEMPERATURE = 0.0
MAX_NEW_TOKENS = 512
TIMEOUT_SEC = 3.0
```

### Entrypoint (`train.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # loops models x benchmarks x {structured, raw}, calls evaluate.run_benchmark,
    # aggregates, writes results.json, calls visualize.* functions
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Error parser | Implement StructuredError + parse_compiler_output with regex extraction | 8 | 2+1+3+2 |
| A-2 | Prompt formatters | format_structured_prompt, format_raw_prompt | 4 | 1+1+1+1 |
| A-3 | Data loading | Load HumanEval+/MBPP+ via evalplus/datasets | 5 | 2+2+1+0 |
| A-4 | Model loading | HF model loading (7B/34B) + OpenAI client wrapper | 7 | 2+3+1+1 |
| A-5 | Repair loop | Execute code, capture error, repair iteration (up to 5 attempts) | 10 | 3+2+3+2 |
| A-6 | Evaluation pipeline | evalplus integration, pass@1, repair success rate, error breakdown | 9 | 2+3+2+2 |
| A-7 | Visualization | 5 figures (gate comparison + 4 additional) | 6 | 2+1+1+2 |
| A-8 | Full comparison run | train.py orchestrating models x benchmarks x formats, results.json | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-5, A-6, A-8], Low(4-8): [A-2, A-3, A-4, A-7]

---

## Notes

- No training — inference-only PoC.
- Sequential execution (batch_size=1), temperature=0.0, fixed seeds per NFR-1/NFR-2.
- GPT-4 calls require exponential backoff retry (NFR-3) — implement in `models.generate_code` for `is_openai=True` branch.

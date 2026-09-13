# Architecture: h-e1 (EXISTENCE / PoC)

**Applied**: subprocess-based static-analysis-on-generated-code pattern (pylint JSON reporter, temp-file isolation)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (MCP tools unavailable in this environment; hypothesis folder contains only spec docs, no `code/` directory)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis, no existing `src/` or `code/`.

---

## File Structure (Minimal — EXISTENCE tier)

```
h-e1/code/
  config.py       # fixed config: dataset id, model id, pylint args, gate threshold
  generate.py      # HumanEval loading + LLM solution generation
  analyze.py       # pylint subprocess runner + JSON parsing
  train.py         # main experiment loop (no training; orchestrates gen+analyze+metrics)
  evaluate.py       # metrics computation + gate check + figures
  figures/          # output plots
  results/          # raw generations, pylint outputs, metrics.json
```

## Modules

### config.py (`code/config.py`)

**Dependencies**: none

```python
DATASET_ID = "openai_humaneval"
MODEL_ID = "gpt-3.5-turbo"          # or codellama/CodeLlama-7b-Instruct-hf
TEMPERATURE = 0.0
PYLINT_ARGS = ["--output-format=json", "--disable=C,R"]
PYLINT_TIMEOUT_SEC = 30
GATE_THRESHOLD = 0.30
OUTPUT_DIR = "results/"
FIGURES_DIR = "figures/"
```

### generate.py (`code/generate.py`)

**Dependencies**: config, datasets (HF), openai or transformers

```python
def load_humaneval() -> list[dict]: ...
    # returns list of {task_id, prompt, canonical_solution, test, entry_point}

def generate_solution(prompt: str) -> str: ...
    # calls LLM (API or local), returns generated code string
```

### analyze.py (`code/analyze.py`)

**Dependencies**: config

```python
def run_pylint_analysis(code: str) -> dict: ...
    # returns {total_messages, actionable_count, messages: list[dict]}
    # actionable = type in ('error', 'warning'); temp file cleaned up
```

### train.py (`code/train.py`)

**Dependencies**: config, generate, analyze, evaluate

```python
def run_experiment() -> list[dict]: ...
    # loop: for each of 164 problems -> generate_solution -> run_pylint_analysis
    # returns list of {task_id, actionable_count, messages, warning_codes}
    # saves raw results to results/generations.json, results/pylint_results.json

def main() -> None: ...
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: config, matplotlib

```python
def compute_metrics(results: list[dict]) -> dict: ...
    # warning_rate, avg_warnings, warning_type_distribution, top_10_warning_codes, gate_passed

def plot_gate_metrics(metrics: dict) -> None: ...      # target vs actual bar chart
def plot_warning_distribution(results: list) -> None: ...  # histogram
def plot_warning_type_breakdown(metrics: dict) -> None: ... # pie chart
def plot_top_warning_codes(metrics: dict) -> None: ...  # bar chart

def evaluate() -> dict: ...
    # loads results, calls compute_metrics + all plots, saves results/metrics.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup config + data loading | config.py + load_humaneval() via HF datasets | 5 | 1+1+1+2 |
| A-2 | LLM generation | generate_solution() via API/local model, temp=0 | 8 | 2+2+2+2 |
| A-3 | Pylint analysis module | run_pylint_analysis() subprocess + JSON parse + temp file cleanup | 7 | 2+1+3+1 |
| A-4 | Experiment loop (train.py) | orchestrate 164-problem loop, save raw results | 6 | 2+2+1+1 |
| A-5 | Metrics computation | compute_metrics() warning_rate, distributions, gate check | 5 | 1+1+2+1 |
| A-6 | Visualization | 4 required figures saved to figures/ | 6 | 2+1+1+2 |
| A-7 | End-to-end run + gate report | run full pipeline, verify <30min, write final gate result | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7]

---

## External Dependencies

None — green-field, no base hypothesis code to reuse.

# Architecture: H-E1 ECE Measurability Validation

**Type**: EXISTENCE (PoC, LIGHT tier)
**Applied**: verbalized-confidence extraction + binned ECE (Guo et al. 2017 / Xiong et al. 2023)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis folder exists for h-e1 (root hypothesis).

---

## Component Overview

- `data.py` -> loads TruthfulQA mc1, formats questions
- `prompts.py` -> 5 prompt templates + formatter
- `api_client.py` -> OpenAI call wrapper + disk cache
- `extract.py` -> regex extraction (confidence, answer)
- `metrics.py` -> ECE computation
- `run_experiment.py` -> orchestrates all 5 conditions, saves results
- `visualize.py` -> gate chart + reliability diagrams + ECE bar chart

Data flow:
`data.py` -> items -> `prompts.py` (format per condition) -> `api_client.py` (cached call) -> raw text -> `extract.py` (confidence, answer) -> `run_experiment.py` (assemble results, compute extraction_rate) -> `metrics.py` (ECE per condition) -> `visualize.py` (figures) + results JSON.

---

## Modules

### DataLoader (`data.py`)

**Dependencies**: datasets (HF)

```python
def load_truthfulqa_mc1() -> list[dict]: ...
def format_choices(mc1_targets: dict) -> str: ...
```

### Prompts (`prompts.py`)

**Dependencies**: None

```python
PROMPTS: dict[str, str]  # 5 condition templates
def build_prompt(condition: str, question: str, choices: str) -> str: ...
```

### APIClient (`api_client.py`)

**Dependencies**: openai, DataLoader (item ids for cache keys)

```python
class APIClient:
    def __init__(self, model: str = "gpt-3.5-turbo", cache_path: str = ".cache/responses.jsonl"): ...
    def call(self, prompt: str, cache_key: str) -> str: ...
```

### Extractor (`extract.py`)

**Dependencies**: None (re, stdlib)

```python
def extract_confidence(response_text: str) -> float | None: ...
def extract_answer(response_text: str, num_choices: int) -> str | None: ...
```

### Metrics (`metrics.py`)

**Dependencies**: numpy

```python
def compute_ece(results: list[dict], n_bins: int = 15) -> float: ...
def extraction_rate(n_success: int, n_total: int) -> float: ...
```

### ExperimentRunner (`run_experiment.py`)

**Dependencies**: DataLoader, Prompts, APIClient, Extractor, Metrics

```python
def run_condition(dataset: list[dict], condition: str, client: APIClient) -> tuple[list[dict], float]: ...
def main() -> None:  # loops 5 conditions, writes results/h-e1_results.json
    ...
```

### Visualizer (`visualize.py`)

**Dependencies**: matplotlib, ExperimentRunner output (results JSON)

```python
def plot_gate_metrics(extraction_rates: dict[str, float], out_dir: str) -> None: ...
def plot_reliability_diagram(results: list[dict], condition: str, out_dir: str) -> None: ...
def plot_ece_comparison(ece_by_condition: dict[str, float], out_dir: str) -> None: ...
def plot_failure_breakdown(failures: dict[str, int], out_dir: str) -> None: ...
```

---

## File Structure

```
h-e1/code/
  data.py
  prompts.py
  api_client.py
  extract.py
  metrics.py
  run_experiment.py
  visualize.py
  results/h-e1_results.json
  .cache/responses.jsonl
figures/
  gate_metrics.png
  reliability_<condition>.png
  ece_comparison.png
  failure_breakdown.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load TruthfulQA mc1, format choices | 4 | 1+1+1+1 |
| A-2 | Prompt templates | 5 condition templates + builder | 3 | 1+1+1+0 |
| A-3 | API client + cache | OpenAI wrapper, JSONL disk cache | 6 | 2+1+2+1 |
| A-4 | Confidence extraction | Regex extraction, failure handling | 4 | 1+1+1+1 |
| A-5 | Answer extraction | Regex extraction, letter validation | 3 | 1+1+1+0 |
| A-6 | ECE computation | 15-bin ECE + extraction_rate fn | 5 | 1+1+2+1 |
| A-7 | Experiment orchestration | Run 5 conditions, save results JSON | 7 | 2+2+2+1 |
| A-8 | Visualization | Gate chart, reliability diagrams, ECE bar, failure pie | 6 | 2+1+2+1 |

**Total tasks**: 8 (within LIGHT budget of 15)
**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1,A-3,A-4,A-6,A-7,A-8], VeryLow(1-3): [A-2,A-5]

---

## Notes

- No training; inference-only, 817 x 5 = 4,085 API calls, temperature=0.
- Cache is mandatory to avoid re-billing on reruns (`api_client.py`).
- PoC pass condition: extraction rate >95% all conditions AND ECE in [0,1] for all 5 conditions.

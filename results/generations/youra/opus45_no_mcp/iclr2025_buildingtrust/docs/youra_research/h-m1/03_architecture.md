# Architecture: H-M1 CoT Reasoning Chain Detection

**Type**: MECHANISM (standard tier)
**Applied**: zero-shot CoT elicitation (Kojima et al. 2022) + regex reasoning-chain detection (Wei et al. 2022)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: H-E1 has spec (`03_architecture.md`) but no `code/` directory exists yet (unimplemented) — nothing to analyze with Serena.
**Analyzed Path**: `../h-e1/code/` (not found)
**Findings**: No actual H-E1 code to import from. Reuse H-E1's *design patterns* (cached API client, regex extractor style) as reference only; no cross-hypothesis import dependency.

---

## Component Overview

- `data.py` -> loads TruthfulQA mc2, formats questions/options
- `prompts.py` -> baseline + CoT prompt templates
- `api_client.py` -> OpenAI call wrapper + disk cache + retry/backoff
- `reasoning_detect.py` -> regex reasoning-chain detection, step counting, answer/confidence extraction
- `metrics.py` -> reasoning_presence_rate, mean_step_count, gate comparison
- `run_experiment.py` -> orchestrates baseline + CoT conditions, saves results
- `visualize.py` -> gate bar chart, step histogram, example comparison, pattern pie chart

Data flow:
`data.py` -> items -> `prompts.py` (baseline/CoT template) -> `api_client.py` (cached call) -> raw text -> `reasoning_detect.py` (has_reasoning, step_count, answer, confidence) -> `run_experiment.py` (assemble results per condition) -> `metrics.py` (rates, gate check) -> `visualize.py` (figures) + results JSON.

---

## Modules

### DataLoader (`data.py`)

**Dependencies**: datasets (HF)

```python
def load_truthfulqa_mc2() -> list[dict]: ...
def format_options(mc2_targets: dict) -> tuple[str, list[str]]: ...  # returns formatted str + option letters
```

### Prompts (`prompts.py`)

**Dependencies**: None

```python
def build_baseline_prompt(question: str, options: str) -> str: ...
def build_cot_prompt(question: str, options: str) -> str: ...
```

### APIClient (`api_client.py`)

**Dependencies**: openai

```python
class APIClient:
    def __init__(self, model: str = "gpt-3.5-turbo", cache_path: str = ".cache/responses.jsonl", max_retries: int = 3): ...
    def call(self, prompt: str, cache_key: str) -> str: ...  # exp backoff on rate limit
```

### ReasoningDetector (`reasoning_detect.py`)

**Dependencies**: None (re, stdlib)

```python
def detect_reasoning_chain(text: str) -> bool: ...
def count_reasoning_steps(text: str) -> int: ...
def classify_patterns(text: str) -> dict[str, bool]: ...  # numbered/ordinal/logical for pie chart
def extract_answer(text: str, num_choices: int) -> str | None: ...
def extract_confidence(text: str) -> float | None: ...
```

### Metrics (`metrics.py`)

**Dependencies**: None

```python
def compute_metrics(results: list[dict]) -> dict: ...  # reasoning_presence_rate, mean_step_count
def check_gate(cot_metrics: dict, baseline_metrics: dict) -> dict: ...  # 3 PoC pass conditions
```

### ExperimentRunner (`run_experiment.py`)

**Dependencies**: DataLoader, Prompts, APIClient, ReasoningDetector, Metrics

```python
def run_condition(dataset: list[dict], condition: str, client: APIClient) -> list[dict]: ...
def main() -> None:  # runs baseline + CoT (817x2), writes results/h-m1_results.json
    ...
```

### Visualizer (`visualize.py`)

**Dependencies**: matplotlib, ExperimentRunner output (results JSON)

```python
def plot_gate_metrics(baseline_rate: float, cot_rate: float, out_dir: str) -> None: ...
def plot_step_count_histogram(cot_results: list[dict], out_dir: str) -> None: ...
def plot_example_comparison(baseline_results: list[dict], cot_results: list[dict], out_dir: str) -> None: ...
def plot_pattern_breakdown(cot_results: list[dict], out_dir: str) -> None: ...
```

---

## File Structure

```
h-m1/code/
  data.py
  prompts.py
  api_client.py
  reasoning_detect.py
  metrics.py
  run_experiment.py
  visualize.py
  results/h-m1_results.json
  .cache/responses.jsonl
figures/
  gate_metrics.png
  step_count_histogram.png
  example_comparison.png
  pattern_breakdown.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load TruthfulQA mc2, format options w/ letters | 4 | 1+1+1+1 |
| A-2 | Prompt templates | Baseline + CoT template builders | 2 | 1+0+1+0 |
| A-3 | API client + cache | OpenAI wrapper, JSONL cache, retry/backoff | 6 | 2+1+2+1 |
| A-4 | Reasoning chain detection | Regex detect_reasoning_chain, count_reasoning_steps, classify_patterns | 7 | 2+1+3+1 |
| A-5 | Answer/confidence extraction | Regex extraction, failure handling | 3 | 1+1+1+0 |
| A-6 | Metrics computation | reasoning_presence_rate, mean_step_count, gate check | 4 | 1+1+1+1 |
| A-7 | Experiment orchestration | Run baseline+CoT (1634 calls), save results JSON | 7 | 2+2+2+1 |
| A-8 | Visualization | Gate chart, step histogram, example comparison, pattern pie | 6 | 2+1+2+1 |

**Total tasks**: 8 (within standard budget)
**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1,A-3,A-4,A-6,A-7,A-8], VeryLow(1-3): [A-2,A-5]

---

## Notes

- No training; inference-only, 817 x 2 conditions = 1,634 API calls, temperature=0, max_tokens=1024.
- Cache mandatory to avoid re-billing on reruns (`api_client.py`), same pattern as H-E1.
- PoC pass: `cot_reasoning_rate > 0.90` AND `cot_reasoning_rate - baseline_reasoning_rate > 0.50` AND `cot_mean_step_count > 2.0`.
- No cross-hypothesis code import (H-E1 unimplemented); H-M1 is self-contained green-field code reusing only design conventions.

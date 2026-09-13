# Architecture: H-E1 (EXISTENCE PoC)

**Hypothesis:** Model scale (7B/70B/proprietary) affects FP/FN error ratio in code-correctness judging.
Applied: LLM-as-judge evaluation harness pattern (evalplus + chi-square gate, from experiment brief research)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis or prior codebase.

---

## File Structure (Minimal - EXISTENCE)

```
h-e1/code/
  config.py       # fixed config: models, dataset, thresholds
  data.py         # HumanEval+ loading + solution generation/collection
  judge.py        # LLMJudgeEvaluator: judge_code, _get_verdict, _classify_error
  execute.py      # Docker-sandboxed execution ground truth (evalplus)
  analyze.py      # contingency table + chi-square test
  train.py        # orchestrator: run full pipeline, save results.csv
  evaluate.py     # metrics (FPR/FNR/accuracy) + figures
  figures/        # output plots
```

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
MODELS = {
    "7B": "deepseek-ai/deepseek-coder-7b-instruct",
    "70B": "codellama/CodeLlama-70b-Instruct-hf",
    "proprietary": "gpt-4",
}
TEMPERATURE = 0
MAX_TOKENS = 512
SEED = 1
P_VALUE_THRESHOLD = 0.05
MIN_SAMPLE_SIZE = 500
PROMPT_TEMPLATE = "..."  # zero-shot correctness judgment
```

### Data (`data.py`)

**Dependencies**: config

```python
def load_problems() -> list[dict]: ...          # evalplus.data.get_human_eval_plus()
def get_solutions(problem: dict) -> list[str]: ...  # pre-generated or model-generated
```

### Execute (`execute.py`)

**Dependencies**: data

```python
def run_evalplus(task_id: str, solution: str) -> bool: ...  # Docker sandbox, pass/fail
```

### Judge (`judge.py`)

**Dependencies**: config, execute

```python
class LLMJudgeEvaluator:
    def __init__(self, models: dict, prompt_template: str): ...
    def judge_code(self, problem: dict, solution: str, scale: str) -> dict: ...
    def _get_verdict(self, scale: str, prompt: str) -> bool: ...
    def _classify_error(self, verdict: bool, truth: bool) -> str: ...  # TP|TN|FP|FN
```

### Analyze (`analyze.py`)

**Dependencies**: pandas, scipy

```python
def build_contingency(results: pd.DataFrame) -> pd.DataFrame: ...  # scale x error_type
def chi_square_test(contingency: pd.DataFrame) -> dict: ...  # {chi2, p_value, dof}
def verify_mechanism_active(results: pd.DataFrame) -> bool: ...
```

### Train / Orchestrator (`train.py`)

**Dependencies**: data, judge, analyze

```python
def main() -> None: ...
    # load problems -> get solutions -> for scale in MODELS: judge_code per (problem, solution)
    # -> save results.csv -> build_contingency -> chi_square_test -> save contingency.csv
```

### Evaluate (`evaluate.py`)

**Dependencies**: analyze, matplotlib/seaborn

```python
def compute_scale_metrics(df: pd.DataFrame, scale: str) -> dict: ...  # acc, fpr, fnr
def plot_gate_metric(p_value: float, threshold: float, path: str) -> None: ...
def plot_error_distribution(df: pd.DataFrame, path: str) -> None: ...  # stacked bar
def plot_contingency_heatmap(contingency: pd.DataFrame, path: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load HumanEval+ problems + collect/generate solutions | 8 | 2+2+2+2 |
| A-2 | Execution sandbox | Docker-based evalplus ground truth execution | 10 | 3+2+3+2 |
| A-3 | Judge inference | Implement LLMJudgeEvaluator across 3 scales (vllm x2 + OpenAI) | 14 | 4+4+3+3 |
| A-4 | Error classification | TP/TN/FP/FN classification + results.csv assembly | 6 | 2+1+2+1 |
| A-5 | Statistical analysis | Contingency table + chi-square test + mechanism verification | 9 | 2+2+3+2 |
| A-6 | Orchestration | train.py pipeline wiring all stages end-to-end | 8 | 2+3+1+2 |
| A-7 | Evaluation & figures | Per-scale metrics + 4 required visualizations | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-2, A-5], Low(4-8): [A-1, A-4, A-6, A-7]

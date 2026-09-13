# Logic Spec: H-M1

**Hypothesis:** Judge-execution agreement increases with model scale (7B < 70B < proprietary) with diminishing returns
**Type:** MECHANISM

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - new API design, no base hypothesis or existing codebase to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: Ground Truth Extraction [Complexity: 2, Budget: 2]

**Applied:** Standard PyTorch / evalplus data loading (no direct KB match; using brief's reference impl)

### API Signatures

```python
from evalplus.data import get_human_eval_plus
from evalplus.eval import check_correctness

def load_ground_truth(dataset: str = "humaneval") -> Dict[str, Dict]:
    """Load problems dict: {task_id: {prompt, canonical_solution, test, entry_point}}"""
    ...

def execute_ground_truth(problems: Dict[str, Dict], solutions: Dict[str, str]) -> Dict[str, int]:
    """Run EvalPlus tests. Returns {task_id: 1|0} pass/fail."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_ground_truth | Load HumanEval+ 164 problems via evalplus |
| L-1-2 | execute_ground_truth | Execute candidate solutions, produce pass/fail labels |

---

## A-2: Judge Prompting & Verdict Parsing [Complexity: 3, Budget: 3]

**Applied:** Standard PyTorch (vLLM batched generation) + OpenAI API pattern from brief

### API Signatures

```python
JUDGE_PROMPT = (
    "Given the following Python function and its specification, determine if "
    "the implementation is correct.\n\nFunction:\n{code}\n\nSpecification:\n{prompt}\n\n"
    "Is this implementation correct? Answer only 'correct' or 'incorrect'."
)

def build_judge_prompt(code: str, spec_prompt: str) -> str:
    """Fill JUDGE_PROMPT template."""
    ...

def query_judge_vllm(model_id: str, prompts: List[str], max_tokens: int = 10) -> List[str]:
    """Batched vLLM generation, temp=0. Returns raw text per prompt."""
    ...

def query_judge_openai(model_id: str, prompt: str, max_tokens: int = 10) -> str:
    """Single OpenAI chat completion, temp=0. Returns raw text."""
    ...

def parse_verdict(raw_text: str) -> int:
    """Parse 'correct'/'incorrect' (case-insensitive substring) -> 1|0. Default 0 on ambiguous."""
    ...
```

### Pseudo-code

```
1. for scale in ['7B', '70B', 'proprietary']:
2.     for task_id, problem in problems.items():
3.         prompt = build_judge_prompt(candidate_code[task_id], problem['prompt'])
4.         raw = query_judge_vllm(...) if scale != 'proprietary' else query_judge_openai(...)
5.         judge_verdicts[scale][task_id] = parse_verdict(raw)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | build_judge_prompt / parse_verdict | Prompt template + verdict parsing |
| L-2-2 | query_judge_vllm | 7B/70B local inference via vLLM, temp=0 |
| L-2-3 | query_judge_openai | GPT-4-turbo via OpenAI API, temp=0 |

---

## A-3: Scale Ordering Evaluation [Complexity: 4, Budget: 4]

**Applied:** Standard PyTorch (scipy.stats.kruskal, sklearn.metrics.cohen_kappa_score)

### API Signatures

```python
from typing import Dict, List, TypedDict
import numpy as np
from scipy.stats import kruskal
from sklearn.metrics import cohen_kappa_score, accuracy_score

class ScaleEvalResult(TypedDict):
    accuracies: Dict[str, float]
    kappas: Dict[str, float]
    ordering_satisfied: bool
    diminishing_returns: bool
    diff_7b_70b: float
    diff_70b_prop: float
    kruskal_h: float
    p_value: float

def evaluate_scale_ordering(
    judge_verdicts: Dict[str, Dict[str, int]],
    ground_truth: Dict[str, int],
) -> ScaleEvalResult:
    """
    judge_verdicts: {scale: {task_id: 0|1}}, scale in {'7B','70B','proprietary'}
    ground_truth: {task_id: 0|1} pass/fail from EvalPlus execution
    Returns accuracies, ordering/diminishing-returns flags, Kruskal-Wallis H-test.
    """
    ...

def verify_mechanism(results: ScaleEvalResult) -> bool:
    """Assert ordering, diminishing returns, p < 0.05. Raises AssertionError on failure."""
    ...
```

### Tensor / Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| judge_verdicts | `dict[str, dict[str, int]]` | 3 scales x 164 task_ids |
| ground_truth | `dict[str, int]` | 164 task_ids -> {0,1} |
| scale_groups | `list[list[int]]` len 3, each len 164 | per-task correctness (1=agree) for Kruskal-Wallis |
| accuracies | `dict[str, float]` | 3 scalars in [0,1] |

### Pseudo-code

```
1. for scale in ['7B','70B','proprietary']:
2.     accuracies[scale] = accuracy_score(y_true=[ground_truth[t] for t in task_ids],
                                            y_pred=[judge_verdicts[scale][t] for t in task_ids])
3.     kappas[scale] = cohen_kappa_score(y_true, y_pred)
4. ordering_satisfied = acc['7B'] < acc['70B'] < acc['proprietary']
5. diff1 = acc['70B'] - acc['7B']; diff2 = acc['proprietary'] - acc['70B']
6. diminishing_returns = diff1 > diff2
7. scale_groups = [[1 if verdict==gt else 0 for task] for scale]  # 3 x 164 binary agreement
8. h_stat, p_value = kruskal(*scale_groups)
9. return ScaleEvalResult(...)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | evaluate_scale_ordering | Compute accuracies, kappas, ordering/diminishing-returns checks |
| L-3-2 | Kruskal-Wallis H-test | Statistical test on per-task binary agreement across 3 scales |
| L-3-3 | verify_mechanism | Assertion-based gate check (ordering, diminishing returns, p<0.05) |
| L-3-4 | confusion matrix / error breakdown | TP/TN/FP/FN per scale (links to H-E1 FPR/FNR) |

---

## A-4: Visualization [Complexity: 2, Budget: 2]

**Applied:** Standard PyTorch (matplotlib bar/line charts)

### API Signatures

```python
def plot_gate_metrics(results: ScaleEvalResult, out_path: str) -> None:
    """Bar chart: accuracy by scale tier with error bars (mandatory gate figure)."""
    ...

def plot_diminishing_returns(results: ScaleEvalResult, out_path: str) -> None:
    """Line plot: scale tier (ordinal x) vs accuracy, annotate diff1/diff2."""
    ...

def plot_confusion_matrices(judge_verdicts: dict, ground_truth: dict, out_dir: str) -> None:
    """Per-scale TP/TN/FP/FN grid, 3 subplots."""
    ...

def plot_kappa_by_scale(results: ScaleEvalResult, out_path: str) -> None:
    """Bar chart: Cohen's Kappa per scale tier."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | plot_gate_metrics | Mandatory accuracy-by-scale bar chart -> figures/ |
| L-4-2 | plot_diminishing_returns / plot_confusion_matrices / plot_kappa_by_scale | Additional autonomous figures -> figures/ |

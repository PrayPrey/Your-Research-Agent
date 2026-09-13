# 03_logic.md — H-M1: Token Entropy Captures Epistemic Uncertainty

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design (no existing h-m1/code/ or base hypothesis)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Entropy Computation [Complexity: PoC, Budget: 3]

**Applied**: Standard PyTorch (softmax entropy over vocab logits)

### API Signatures

```python
import torch
from torch import Tensor
from transformers import PreTrainedModel, PreTrainedTokenizer

def compute_response_entropy(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    question: str,
    max_new_tokens: int = 100,
) -> float:
    """Generate a response, return mean per-token entropy (nats)."""
    ...

def generate_response(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    question: str,
    max_new_tokens: int = 100,
) -> tuple[str, Tensor]:
    """Generate greedy response. Returns (text, logits [T, V])."""
    ...

def token_entropy(logits: Tensor) -> Tensor:
    """logits: [T, V] -> entropy: [T]"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, L] | Prompt tokens |
| logits (per step, stacked) | [T, V] | T = generated tokens, V = vocab size (32000 for LLaMA-2) |
| probs | [T, V] | softmax(logits, dim=-1) |
| entropy | [T] | -sum(probs * log(probs), dim=-1) |
| mean_entropy | scalar | entropy.mean().item() |

### Pseudo-code

```
1. input_ids = tokenizer(question, return_tensors="pt").input_ids  # [1, L]
2. out = model.generate(input_ids, max_new_tokens=max_new_tokens,
                         do_sample=False, output_scores=True,
                         return_dict_in_generate=True)
3. logits = torch.stack(out.scores, dim=0).squeeze(1)  # [T, V]
4. probs = torch.softmax(logits, dim=-1)               # [T, V]
5. entropy = -(probs * torch.log(probs + 1e-12)).sum(-1)  # [T]
6. response_text = tokenizer.decode(out.sequences[0][input_ids.shape[1]:], skip_special_tokens=True)
7. return entropy.mean().item()
```

### Subtasks [1/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | compute_response_entropy | Generate + entropy pipeline |

---

## A-2: Correctness Labeling [Complexity: PoC, Budget: 2]

**Applied**: Standard PyTorch / string matching (no KB pattern needed)

### API Signatures

```python
def label_correctness(response: str, correct_answers: list[str]) -> bool:
    """Substring match (case-insensitive) of any correct_answers in response."""
    ...
```

### Pseudo-code

```
1. resp = response.strip().lower()
2. return any(ans.strip().lower() in resp for ans in correct_answers)
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | label_correctness | Substring-match labeling against TruthfulQA correct_answers |

---

## A-3: Statistical Test [Complexity: PoC, Budget: 2]

**Applied**: Standard PyTorch / scipy (Welch's t-test + Cohen's d)

### API Signatures

```python
def test_entropy_uncertainty_link(
    correct_entropies: list[float],
    incorrect_entropies: list[float],
) -> dict:
    """Returns {mean_correct, mean_incorrect, effect_size_d, pvalue, pass}."""
    ...
```

### Pseudo-code

```
1. from scipy import stats
2. mean_c, mean_i = mean(correct_entropies), mean(incorrect_entropies)
3. t_stat, pvalue = stats.ttest_ind(incorrect_entropies, correct_entropies, equal_var=False)
4. pooled_std = sqrt((std(correct_entropies)**2 + std(incorrect_entropies)**2) / 2)
5. effect_size_d = (mean_i - mean_c) / pooled_std
6. pass_flag = (pvalue < 0.05) and (mean_i > mean_c)
7. return {"mean_correct": mean_c, "mean_incorrect": mean_i,
           "effect_size_d": effect_size_d, "pvalue": pvalue, "pass": pass_flag}
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | test_entropy_uncertainty_link | Welch t-test + Cohen's d on entropy groups |

---

## A-4: Visualization [Complexity: PoC, Budget: 2]

**Applied**: Standard PyTorch / matplotlib

### API Signatures

```python
def generate_visualizations(
    correct: list[float],
    incorrect: list[float],
    output_dir: str,
) -> None:
    """Save entropy histogram + boxplot (correct vs incorrect) to output_dir."""
    ...
```

### Pseudo-code

```
1. os.makedirs(output_dir, exist_ok=True)
2. plt.hist(correct, alpha=0.5, label="correct"); plt.hist(incorrect, alpha=0.5, label="incorrect")
3. savefig(output_dir/"entropy_hist.png")
4. plt.boxplot([correct, incorrect], labels=["correct","incorrect"])
5. savefig(output_dir/"entropy_boxplot.png")
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | generate_visualizations | Histogram + boxplot of entropy by correctness |

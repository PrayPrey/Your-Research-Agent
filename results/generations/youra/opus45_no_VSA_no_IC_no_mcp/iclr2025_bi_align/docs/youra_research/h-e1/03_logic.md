# Logic Design: H-E1 (EXISTENCE PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Benchmark Correlation Evaluation [Complexity: Medium, Budget: 1 task]

**Applied**: Standard PyTorch (logit extraction for MC tasks, log-prob scoring for preference tasks)

### API Signatures

```python
import torch
from torch import Tensor
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Tuple
import numpy as np
from scipy.stats import pearsonr

def load_model(model_id: str = "meta-llama/Llama-2-7b-hf", device: str = "cuda"):
    """Load base model + tokenizer, eval mode, fp16."""
    ...

def sequence_logprob(model, tokenizer, prompt: str, continuation: str, device: str) -> float:
    """Sum log P(continuation | prompt) under model. Returns scalar."""
    ...

def eval_truthfulqa_mc1(model, tokenizer, dataset, device: str) -> np.ndarray:
    """MC1: pick highest-logprob choice per question. Returns [N] binary array."""
    ...

def eval_hhh_preference(model, tokenizer, dataset, device: str) -> np.ndarray:
    """Preference: chosen vs rejected logprob. Returns [N] binary array."""
    ...

def compute_correlations(scores: dict) -> dict:
    """Pairwise Pearson r,p over 3 benchmarks. Returns {'a_vs_b': {'r':float,'p':float}}."""
    ...

def gate_check(correlations: dict, threshold: float = 0.5) -> bool:
    """True iff all |r| < threshold."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, L] | Single prompt+continuation, batch=1 (loop over samples) |
| logits | [1, L, V] | V = vocab size (32000 for Llama-2) |
| token_logprobs | [L_cont] | Log-probs of continuation tokens only |
| truthfulqa_scores | [817] | Binary correct/incorrect |
| hhh_helpful_scores | [N_help] | Binary chosen-preferred |
| hhh_harmless_scores | [N_harm] | Binary chosen-preferred |

### Pseudo-code

**sequence_logprob** (shared primitive):
```
1. full_text = prompt + continuation
2. input_ids = tokenize(full_text)                      # [1, L]
3. prompt_len = len(tokenize(prompt))
4. with no_grad: logits = model(input_ids).logits        # [1, L, V]
5. shift logits[:, :-1] vs labels input_ids[:, 1:]        # standard LM shift
6. log_probs = log_softmax(logits, dim=-1)                # [1, L-1, V]
7. cont_log_probs = gather log_probs at labels[prompt_len-1:]  # [L_cont]
8. return sum(cont_log_probs).item()
```

**eval_truthfulqa_mc1** (MC1: exactly 1 correct choice, pick argmax logprob):
```
for each sample in dataset:
    question = sample["question"]
    choices = sample["mc1_targets"]["choices"]     # list[str]
    labels  = sample["mc1_targets"]["labels"]       # list[int], one 1 rest 0
    scores  = [sequence_logprob(model, tok, question, f" {c}", device) for c in choices]
    pred_idx = argmax(scores)
    correct  = 1 if labels[pred_idx] == 1 else 0
    append correct to results
return np.array(results)   # [817]
```

**eval_hhh_preference** (chosen vs rejected from hh-rlhf):
```
for each sample in dataset:
    prompt   = sample["context"] or extract shared prefix from chosen/rejected
    chosen   = sample["chosen"]
    rejected = sample["rejected"]
    lp_chosen   = sequence_logprob(model, tok, prompt, chosen, device)
    lp_rejected = sequence_logprob(model, tok, prompt, rejected, device)
    correct = 1 if lp_chosen > lp_rejected else 0
    append correct to results
return np.array(results)   # [N]
```

**compute_correlations**:
```
benchmarks = ["truthfulqa", "hhh_helpful", "hhh_harmless"]
for (b1, b2) in combinations(benchmarks, 2):
    # NOTE: arrays may differ in length (817 vs N_help vs N_harm)
    # truncate to min length for pairwise Pearson (per-sample alignment not defined across benchmarks)
    n = min(len(scores[b1]), len(scores[b2]))
    r, p = pearsonr(scores[b1][:n], scores[b2][:n])
    correlations[f"{b1}_vs_{b2}"] = {"r": r, "p": p}
return correlations
```

**gate_check**:
```
return all(abs(c["r"]) < threshold for c in correlations.values())
```

### Score Extraction Logic

- All scores are per-sample **binary** (0/1 correctness/preference), not continuous logits — required for Pearson on comparable binary vectors per PRD FR-3/FR-4.
- TruthfulQA: label = 1 iff argmax-logprob choice matches the (single) correct label in `mc1_targets`.
- HHH: label = 1 iff `logprob(chosen) > logprob(rejected)`.
- Correlation is computed on truncated-to-min-length arrays since the three benchmarks have different sample counts (no natural per-question pairing across benchmarks) — this is a known limitation, acceptable for PoC gate check.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A1-1 | Model + logprob primitive | `load_model`, `sequence_logprob` |
| L-A1-2 | Benchmark evaluators | `eval_truthfulqa_mc1`, `eval_hhh_preference` (called twice: helpful/harmless) |
| L-A1-3 | Correlation + gate + viz hooks | `compute_correlations`, `gate_check`, save scores/correlations for figure generation |

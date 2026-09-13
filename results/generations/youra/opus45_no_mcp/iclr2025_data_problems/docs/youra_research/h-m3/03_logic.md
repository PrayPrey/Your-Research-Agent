# Logic Spec: H-M3

**Type:** MECHANISM (inference-only) | **Gate:** r < -0.4 (Pearson)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M2) — but `h-m2/code/` does not exist on disk (no prior implementation found, only specs in `02c_experiment_brief.md`).
**Status:** No actual H-M2 code to verify against. APIs below derived from H-M2's `02c_experiment_brief.md` reference pseudo-code (treated as spec, not verified implementation).
**Analyzed Path:** `h-m2/` (specs only, no `code/` folder present)
**Relevant Symbols:** None found — Phase 4 Coder must implement `extract_hidden_states`, `compute_mps`-equivalent, and checkpoint loading fresh, following signatures below.

---

## A-1: Representation + Confidence Extraction [Complexity: 3, Budget: 3]

**Applied:** Standard PyTorch (`output_hidden_states=True`, softmax over answer tokens)

### API Signatures

```python
import torch
from torch import Tensor
import torch.nn.functional as F
from transformers import PreTrainedModel, PreTrainedTokenizer
from typing import List

def extract_hidden_states(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    texts: List[str],
    device: str = "cuda",
) -> Tensor:
    """Last-layer, last-token hidden states for each text. [N] -> [N, D]"""
    ...

def extract_confidence(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    text: str,
    answer_idx: int,  # token id for correct choice (A/B/C/D letter token)
) -> float:
    """P(correct_answer) via softmax over next-token logits. Returns scalar."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| texts | [N] | item + K=5 paraphrases, N=6 |
| hidden_states | [N, D] | D=4096 for Mistral-7B |
| logits | [1, V] | last-token logits, V=vocab size |
| confidences | [N] | one prob per text |

### Pseudo-code

```
extract_hidden_states(model, tokenizer, texts):
    inputs = tokenizer(texts, padding=True, return_tensors="pt").to(device)
    with no_grad():
        out = model(**inputs, output_hidden_states=True)
        h = out.hidden_states[-1][:, -1, :]   # [N, D]
    return h

extract_confidence(model, tokenizer, text, answer_idx):
    inputs = tokenizer(text, return_tensors="pt").to(device)
    with no_grad():
        logits = model(**inputs).logits[:, -1, :]   # [1, V]
        probs = softmax(logits, dim=-1)
    return probs[0, answer_idx].item()
```

### Subtasks [2/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Batch hidden extraction | Batched forward, padding, last-token pooling |
| L-1-2 | Answer token mapping | Map "A"/"B"/"C"/"D" choice to tokenizer id per item |

---

## A-2: Variance Computation [Complexity: 2, Budget: 2]

**Applied:** Standard PyTorch/NumPy

### API Signatures

```python
import numpy as np

def compute_rep_variance(hidden_states: Tensor) -> float:
    """1 - mean pairwise cosine similarity across [N, D] rows. Returns scalar in [0, 2]."""
    ...

def compute_conf_variance(confidences: np.ndarray) -> float:
    """np.var over [N] confidence scores."""
    ...
```

### Pseudo-code

```
compute_rep_variance(hidden_states):     # [N, D]
    sims = []
    for i in range(N):
        for j in range(i+1, N):
            sims.append(cosine_similarity(hidden_states[i], hidden_states[j]))
    return 1 - mean(sims)

compute_conf_variance(confidences):      # [N]
    return np.var(confidences)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Per-item variance loop | Apply both functions per MMLU item, store (rep_var, conf_var) pairs |

---

## A-3: Correlation Analysis [Complexity: 3, Budget: 3]

**Applied:** scipy.stats (Pearson/Spearman)

### API Signatures

```python
from dataclasses import dataclass
from scipy.stats import pearsonr, spearmanr

@dataclass
class CorrelationResult:
    r_pearson: float
    p_pearson: float
    r_spearman: float
    p_spearman: float
    gate_passes: bool          # r_pearson < -0.4
    cohens_d: float            # high-MPS vs low-MPS conf_var effect size

def analyze_correlation(
    rep_vars: np.ndarray,   # [num_items]
    conf_vars: np.ndarray,  # [num_items]
) -> CorrelationResult:
    ...

def group_comparison(
    rep_vars: np.ndarray,
    conf_vars: np.ndarray,
    threshold: float = None,   # None -> median split
) -> tuple[float, float, float]:
    """Returns (mean_conf_var_high_mps, mean_conf_var_low_mps, cohens_d)."""
    ...
```

### Pseudo-code

```
analyze_correlation(rep_vars, conf_vars):
    r_p, p_p = pearsonr(rep_vars, conf_vars)
    r_s, p_s = spearmanr(rep_vars, conf_vars)
    _, _, d = group_comparison(rep_vars, conf_vars)
    return CorrelationResult(r_p, p_p, r_s, p_s, r_p < -0.4, d)

group_comparison(rep_vars, conf_vars, threshold=None):
    # low rep_var == high MPS (high invariance)
    thresh = threshold or median(rep_vars)
    high_mps_mask = rep_vars <= thresh
    d = cohens_d(conf_vars[~high_mps_mask], conf_vars[high_mps_mask])
    return mean(conf_vars[high_mps_mask]), mean(conf_vars[~high_mps_mask]), d
```

### Subtasks [2/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Correlation + gate check | Pearson/Spearman + threshold r<-0.4 |
| L-3-2 | Group comparison + Cohen's d | Median-split high/low MPS groups |

---

## A-4: Pipeline Orchestration + Figures [Complexity: 4, Budget: 4]

**Applied:** Standard PyTorch + matplotlib

### API Signatures

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_checkpoint(base_model_id: str, adapter_path: str, device: str = "cuda") -> PreTrainedModel:
    """Load base model + LoRA adapter, eval mode, fp16."""
    ...

def run_analysis_pipeline(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    items: List[dict],   # each: {"question": str, "paraphrases": List[str], "answer_idx": int, "subject": str}
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Loop items -> (rep_variances [N_items], conf_variances [N_items], subjects [N_items])."""
    ...

def generate_figures(
    rep_vars: np.ndarray,
    conf_vars: np.ndarray,
    result: CorrelationResult,
    subjects: list[str],
    seeds_results: list[CorrelationResult],  # len=3, seeds 42/123/456
    out_dir: str,
) -> None:
    """Saves: gate_metrics.png, scatter.png, boxplot.png, seed_histogram.png, subject_heatmap.png"""
    ...
```

### Pseudo-code

```
run_analysis_pipeline(model, tokenizer, items):
    rep_vars, conf_vars, subjects = [], [], []
    for item in items:
        texts = [item.question] + item.paraphrases            # [K+1]
        hidden = extract_hidden_states(model, tokenizer, texts)  # [K+1, D]
        confs = [extract_confidence(model, tokenizer, t, item.answer_idx) for t in texts]
        rep_vars.append(compute_rep_variance(hidden))
        conf_vars.append(compute_conf_variance(np.array(confs)))
        subjects.append(item.subject)
    return np.array(rep_vars), np.array(conf_vars), subjects
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Checkpoint loading | Base model + PEFT adapter, fp16, per H-M2 checkpoint paths |
| L-4-2 | Full pipeline loop | Iterate 14,042 items, batch where possible |
| L-4-3 | Multi-seed orchestration | Run pipeline for seeds 42/123/456, aggregate CorrelationResults |
| L-4-4 | Figure generation | 5 required/additional plots to `h-m3/figures/` |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From H-M2 Spec — NOT verified against actual code, none exists)

```python
# Referenced from h-m2/02c_experiment_brief.md pseudo-code (spec only)
def extract_hidden_states(model, tokenizer, texts):
    """[N texts] -> [N, D] last-layer, last-token hidden states."""
    ...

def compute_mps(hidden_states_per_item):
    """Mean pairwise cosine similarity. [N, D] -> scalar."""
    ...
```

**Verified from:** N/A — `h-m2/code/` does not exist. Phase 4 Coder should re-implement `extract_hidden_states` per A-1 above (identical logic) rather than importing missing H-M2 module. If H-M2 code appears before Phase 4, re-run Serena verification.

### Checkpoint Loading (from PRD/brief)

```python
from transformers import AutoModelForCausalLM
from peft import PeftModel
base = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", torch_dtype=torch.float16)
model = PeftModel.from_pretrained(base, "h-m2/checkpoint-verbatim")  # or checkpoint-paraphrase
```

---

## Summary

| Task | Complexity | Budget Used |
|------|-----------|--------------|
| A-1 Extraction | 3 | 2/3 |
| A-2 Variance | 2 | 1/1 |
| A-3 Correlation | 3 | 2/3 |
| A-4 Pipeline+Figures | 4 | 4/4 |

---
hypothesis_id: H-E1
phase: Phase 3
generated: 2026-08-25
author: yoon303@ust.ac.kr
---

# Logic: H-E1 — SE vs TE AUROC Comparison

Applied: Kuhn et al. 2023 SE clustering pattern (bidirectional NLI entailment, logsumexp aggregation)
Applied: Bootstrap AUROC evaluation pattern (stratified resampling, 95% CI)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Semantic Entropy [Complexity: 16, Budget: 4 subtasks]

**Applied**: Kuhn et al. 2023 bidirectional NLI entailment clustering

### API Signatures

```python
# code/compute_se.py
from transformers import pipeline
import numpy as np
from scipy.special import logsumexp
from typing import Optional

def load_nli_model(
    model_id: str = "cross-encoder/nli-deberta-v3-large",
    device: int = 0,
) -> pipeline:
    """Load NLI pipeline. Returns zero-shot-classification pipeline on GPU."""
    ...

def get_semantic_ids(
    strings_list: list[str],   # K samples, e.g. K=10
    nli_pipeline,
) -> list[int]:
    """Bidirectional NLI entailment clustering. Returns cluster id per sample."""
    # Input pairs: K*(K-1) = 90 pairs for K=10
    # NLI output per pair: dict with 'entailment' score in [0, 1]
    ...

def aggregate_log_probs_by_cluster(
    log_probs: np.ndarray,    # shape: (K,)  — per-sample log probs
    semantic_ids: list[int],  # shape: (K,)  — cluster assignments
) -> np.ndarray:
    """logsumexp per cluster. Returns cluster log-probs."""
    # Output shape: (n_clusters,) where n_clusters <= K
    ...

def compute_se_scores(
    questions: list[dict],          # list of {question_id, question, answers}
    samples_map: dict[str, dict],   # {question_id: {samples: list[str], log_probs: list[float]}}
    nli_pipeline,
) -> tuple[list[float], float]:
    """Full SE pipeline. Returns (se_scores, avg_clusters)."""
    # se_scores: list of length N, each scalar float (Shannon entropy over clusters)
    # avg_clusters: mean number of distinct semantic clusters across questions
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| strings_list | (K,) | K=10 stochastic samples per question |
| nli_input_pairs | (K*(K-1), seq_len) | all ordered pairs, K=10 → 90 pairs |
| nli_entailment_scores | (K*(K-1),) | entailment probability per pair |
| log_probs | (K,) | per-sample log probability |
| cluster_log_probs | (n_clusters,) | logsumexp-aggregated, n_clusters <= K |
| se_score | scalar | Shannon entropy: -sum(p * log(p)) over clusters |

### Pseudo-code: `get_semantic_ids`

```
# Kuhn et al. 2023 bidirectional NLI clustering
cluster_ids = [-1] * K
next_cluster = 0

for i in range(K):
    if cluster_ids[i] != -1:
        continue
    cluster_ids[i] = next_cluster
    for j in range(i+1, K):
        if cluster_ids[j] != -1:
            continue
        # bidirectional: both i→j and j→i must entail
        score_ij = nli_pipeline(f"{strings_list[i]} [SEP] {strings_list[j]}")["entailment"]
        score_ji = nli_pipeline(f"{strings_list[j]} [SEP] {strings_list[i]}")["entailment"]
        if score_ij > 0.5 and score_ji > 0.5:
            cluster_ids[j] = next_cluster
    next_cluster += 1

return cluster_ids
```

### Pseudo-code: `compute_se_scores`

```
for q in questions:
    samples = samples_map[q.question_id]["samples"]       # list[str], len K
    log_probs = samples_map[q.question_id]["log_probs"]  # list[float], len K
    log_probs_arr = np.array(log_probs)                  # (K,)

    semantic_ids = get_semantic_ids(samples, nli_pipeline)
    cluster_lp = aggregate_log_probs_by_cluster(log_probs_arr, semantic_ids)  # (n_clusters,)

    # normalize to probabilities
    cluster_lp -= logsumexp(cluster_lp)       # (n_clusters,)
    probs = np.exp(cluster_lp)               # (n_clusters,)
    se = -np.sum(probs * np.log(probs + 1e-9))  # scalar
    se_scores.append(float(se))
    cluster_counts.append(len(set(semantic_ids)))

return se_scores, float(np.mean(cluster_counts))
```

### Subtasks [4/4 used]

| ID | Parent | Subtask | Description |
|----|--------|---------|-------------|
| L-3-1 | A-3 | get_semantic_ids | Bidirectional NLI entailment loop; cluster assignment via greedy union-find style |
| L-3-2 | A-3 | aggregate_log_probs_by_cluster | logsumexp per cluster group; returns (n_clusters,) array |
| L-3-3 | A-3 | compute_se_scores | Full SE pipeline per question; logs avg_clusters |
| L-3-4 | A-3 | load_nli_model | NLI pipeline load with device=0; raises RuntimeError if CUDA unavailable |

---

## A-2: Token Entropy [Complexity: 14, Budget: 3 subtasks]

**Applied**: Standard PyTorch logit extraction + Shannon entropy

### API Signatures

```python
# code/compute_te.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import numpy as np
import os

def load_llama(
    model_id: str = "meta-llama/Llama-2-7b-hf",
    hf_token: Optional[str] = None,  # defaults to os.environ["HF_TOKEN"]
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load Llama-2-7B in float16, device_map=auto. Returns (model, tokenizer)."""
    ...

def compute_single_te(
    question_text: str,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    device: str = "cuda",
    max_new_tokens: int = 50,
) -> float:
    """Greedy decode, extract logits, compute mean per-token Shannon entropy."""
    # Input tokens:  (1, prompt_len)
    # Logits:        (1, prompt_len + gen_len, vocab_size=32000)
    # Output tokens only: logits[:, prompt_len:, :]  shape: (1, gen_len, 32000)
    # Per-token entropy: -sum(p * log(p+1e-9), dim=-1)  shape: (1, gen_len)
    # TE = mean over gen_len  →  scalar float
    ...

def compute_te_scores(
    questions: list[dict],
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    device: str = "cuda",
) -> list[float]:
    """Batched (sequential) TE computation over all questions. Returns list[float] len N."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | (1, prompt_len) | tokenized question |
| logits (full) | (1, prompt_len + gen_len, 32000) | Llama-2-7B vocab |
| logits (gen only) | (1, gen_len, 32000) | sliced at prompt_len |
| probs | (1, gen_len, 32000) | softmax over vocab dim |
| per_token_entropy | (1, gen_len) | -sum(p*log(p+1e-9), dim=-1) |
| te_score | scalar | mean over gen_len |

### Pseudo-code: `compute_single_te`

```
inputs = tokenizer(question_text, return_tensors="pt").to(device)
prompt_len = inputs.input_ids.shape[1]

with torch.no_grad():
    out = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,           # greedy
        return_dict_in_generate=True,
        output_scores=True,
    )
# out.scores: tuple of gen_len tensors, each (1, vocab_size)
scores = torch.stack(out.scores, dim=1)   # (1, gen_len, 32000)
probs = torch.softmax(scores, dim=-1)     # (1, gen_len, 32000)
entropy = -torch.sum(probs * torch.log(probs + 1e-9), dim=-1)  # (1, gen_len)
return float(entropy.mean().item())
```

### Subtasks [3/3 used]

| ID | Parent | Subtask | Description |
|----|--------|---------|-------------|
| L-2-1 | A-2 | load_llama | Float16 load with HF_TOKEN from env; device_map=auto |
| L-2-2 | A-2 | compute_single_te | Greedy decode via output_scores=True; slice prompt tokens before entropy |
| L-2-3 | A-2 | compute_te_scores | Sequential loop over questions with tqdm; returns list[float] |

---

## A-4: Evaluation & Metrics [Complexity: 12, Budget: 2 subtasks]

**Applied**: Bootstrap AUROC evaluation pattern (stratified resampling, 95% CI)

### API Signatures

```python
# code/evaluate.py
import numpy as np
from sklearn.metrics import roc_auc_score

def bootstrap_auroc(
    y_true: np.ndarray,     # shape: (N,)  binary int
    y_score: np.ndarray,    # shape: (N,)  float, negated uncertainty score
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple[float, np.ndarray]:
    """Stratified bootstrap AUROC. Returns (mean_auroc, ci) where ci = [low, high]."""
    # ci shape: (2,)  — [2.5th percentile, 97.5th percentile]
    ...

def verify_mechanism(
    te_scores: list[float],
    se_scores: list[float],
    correctness: list[int],
    avg_clusters: float,
) -> tuple[bool, dict]:
    """Run mechanism assertions. Returns (passed, diagnostics_dict)."""
    # diagnostics_dict keys: avg_clusters, mean_te, n_classes, gap, all_passed
    ...
```

### Pseudo-code: `bootstrap_auroc`

```
rng = np.random.default_rng(seed)
aurocs = []
pos_idx = np.where(y_true == 1)[0]
neg_idx = np.where(y_true == 0)[0]

for _ in range(n_bootstrap):
    # stratified: sample with replacement within each class
    boot_pos = rng.choice(pos_idx, size=len(pos_idx), replace=True)
    boot_neg = rng.choice(neg_idx, size=len(neg_idx), replace=True)
    idx = np.concatenate([boot_pos, boot_neg])
    aurocs.append(roc_auc_score(y_true[idx], y_score[idx]))

aurocs = np.array(aurocs)  # (n_bootstrap,)
return float(np.mean(aurocs)), np.percentile(aurocs, [2.5, 97.5])
```

### Pseudo-code: `verify_mechanism`

```
gap = roc_auc_score(correctness, -np.array(se_scores)) \
    - roc_auc_score(correctness, -np.array(te_scores))

checks = {
    "avg_clusters":  avg_clusters > 1.5,
    "mean_te":       np.mean(te_scores) > 0.0,
    "n_classes":     len(set(correctness)) == 2,
    "gap_sane":      abs(gap) < 0.30,
}
passed = all(checks.values())
diagnostics = {**checks, "gap": gap, "all_passed": passed}
return passed, diagnostics
```

### Subtasks [2/2 used]

| ID | Parent | Subtask | Description |
|----|--------|---------|-------------|
| L-4-1 | A-4 | bootstrap_auroc | Stratified bootstrap with rng.choice per class; returns (mean, ci[2]) |
| L-4-2 | A-4 | verify_mechanism | Four assertion checks; returns bool + diagnostics dict for logging |

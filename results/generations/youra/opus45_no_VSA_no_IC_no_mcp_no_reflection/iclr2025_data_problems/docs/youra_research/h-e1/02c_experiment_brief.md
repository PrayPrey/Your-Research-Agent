# Experiment Brief: h-e1

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Date:** 2026-08-28

---

## 1. Hypothesis Statement

Embedding similarity scores (cosine) between domain samples and task exemplars can be reliably computed using E5-large, producing non-trivial variance across domains (std > 0.05).

---

## 2. Dataset Specification

### 2.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | The Pile (8 domains subset) |
| Type | standard |
| Source | EleutherAI via HuggingFace |
| HF Path | `monology/pile-uncopyrighted` or `EleutherAI/pile` |
| Domains | 8 representative: Pile-CC, Wikipedia, Github, ArXiv, StackExchange, PubMed, Books3, OpenWebText2 |
| Sample Size | 1000 samples per domain (8000 total) |
| Token Length | 512 tokens per sample (truncated/padded) |

### 2.2 Task Exemplars

| Field | Value |
|-------|-------|
| Source | MMLU validation set |
| HF Path | `cais/mmlu` |
| Split | validation |
| Sample Size | Full validation set (~1500 questions) |
| Format | Question + choices concatenated as text |

### 2.3 Data Preparation Steps

1. Load 8 Pile domains via HuggingFace datasets
2. Sample 1000 texts per domain (random seed=42)
3. Truncate each to 512 tokens
4. Load MMLU validation split
5. Format MMLU questions: `"{question} A: {A} B: {B} C: {C} D: {D}"`
6. Cache processed data to `./data/h-e1/`

---

## 3. Model Specification

### 3.1 Embedding Model

| Field | Value |
|-------|-------|
| Name | E5-large-v2 |
| HF Path | `intfloat/e5-large-v2` |
| Type | Sentence transformer |
| Embedding Dim | 1024 |
| Max Tokens | 512 |
| Prefix | "query: " for task exemplars, "passage: " for domain samples |

### 3.2 Implementation

```python
from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer('intfloat/e5-large-v2')

# Domain samples: prefix with "passage: "
domain_embeddings = model.encode(
    ["passage: " + text for text in domain_samples],
    convert_to_tensor=True,
    normalize_embeddings=True
)

# Task exemplars: prefix with "query: "
task_embeddings = model.encode(
    ["query: " + text for text in task_exemplars],
    convert_to_tensor=True,
    normalize_embeddings=True
)
```

---

## 4. Experiment Design

### 4.1 Core Metric

**Cosine Similarity Score:**
```python
# Per-sample similarity to task exemplars
similarities = torch.mm(domain_embeddings, task_embeddings.T)  # [N_domain, N_task]
mean_similarity_per_sample = similarities.mean(dim=1)  # [N_domain]

# Per-domain aggregation
domain_scores = {}
for domain in domains:
    mask = (domain_labels == domain)
    domain_scores[domain] = mean_similarity_per_sample[mask].mean().item()
```

### 4.2 Success Criteria

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Score computability | All 8 domains produce valid scores | Basic existence check |
| Non-trivial variance | std(domain_scores) > 0.05 | Scores must differentiate domains |
| Reproducibility | Variance < 5% across 3 runs | Numerical stability |
| Compute time | < 30 minutes on single GPU | Practical feasibility |

### 4.3 Statistical Analysis

1. **Descriptive stats:** mean, std, min, max of domain scores
2. **Distribution plot:** Bar chart of domain similarity scores
3. **Reproducibility:** 3 runs with different random seeds, report variance
4. **ANOVA:** F-test across domains (p < 0.05 required)

---

## 5. Baseline Comparison (within h-e1)

| Baseline | Description | Expected Outcome |
|----------|-------------|------------------|
| Random embeddings | Replace E5 with random vectors | std ≈ 0 (no discrimination) |
| Uniform sampling | Equal samples from all domains | Establishes reference distribution |

---

## 6. Execution Plan

### 6.1 Steps

| Step | Action | Output |
|------|--------|--------|
| 1 | Download/verify The Pile subset | `data/h-e1/pile_8domains.parquet` |
| 2 | Download/verify MMLU validation | `data/h-e1/mmlu_val.parquet` |
| 3 | Load E5-large-v2, verify GPU | Model loaded on CUDA |
| 4 | Embed domain samples | `embeddings/domain_emb.pt` |
| 5 | Embed task exemplars | `embeddings/task_emb.pt` |
| 6 | Compute cosine similarities | `results/similarities.csv` |
| 7 | Aggregate per domain | `results/domain_scores.json` |
| 8 | Statistical analysis | `results/h-e1_analysis.md` |
| 9 | Generate visualizations | `figures/domain_similarity_bar.png` |

### 6.2 Resource Requirements

| Resource | Estimate |
|----------|----------|
| GPU Memory | ~4 GB (E5-large inference) |
| Wall Time | 20-30 minutes |
| Storage | ~2 GB (embeddings + data) |

---

## 7. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OOM on large batch | Batch size = 32, gradient checkpointing off |
| HuggingFace download fail | Use cached datasets, fallback mirrors |
| Low variance | If std < 0.05, try alternative embedder (BGE-large) |
| MMLU format issues | Validate parsing on 10 samples before full run |

---

## 8. Output Artifacts

| Artifact | Path | Format |
|----------|------|--------|
| Domain embeddings | `embeddings/domain_emb.pt` | PyTorch tensor |
| Task embeddings | `embeddings/task_emb.pt` | PyTorch tensor |
| Similarity matrix | `results/similarities.csv` | CSV |
| Domain scores | `results/domain_scores.json` | JSON |
| Analysis report | `results/h-e1_analysis.md` | Markdown |
| Bar chart | `figures/domain_similarity_bar.png` | PNG |

---

## 9. Pass/Fail Decision

**PASS if ALL:**
- [ ] All 8 domains produce valid similarity scores
- [ ] std(domain_scores) > 0.05
- [ ] Reproducibility variance < 5% across 3 runs
- [ ] ANOVA p < 0.05 (domains differ significantly)

**FAIL if ANY:**
- [ ] Any domain fails to produce valid score
- [ ] std(domain_scores) ≤ 0.05 (insufficient discrimination)
- [ ] Reproducibility variance ≥ 5%

---

## 10. Code Skeleton

```python
"""h-e1: E5-large embedding similarity computation"""

import torch
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# Config
DOMAINS = ['pile-cc', 'wikipedia', 'github', 'arxiv', 
           'stackexchange', 'pubmed', 'books3', 'openwebtext2']
SAMPLES_PER_DOMAIN = 1000
SEED = 42

def load_pile_subset(domains, n_samples):
    """Load and sample from The Pile domains."""
    # Implementation: load from HF, filter by domain, sample
    pass

def load_mmlu_validation():
    """Load MMLU validation as task exemplars."""
    ds = load_dataset("cais/mmlu", "all", split="validation")
    return [f"{row['question']} A: {row['choices'][0]} B: {row['choices'][1]} "
            f"C: {row['choices'][2]} D: {row['choices'][3]}" for row in ds]

def compute_domain_scores(domain_emb, task_emb, domain_labels):
    """Compute mean cosine similarity per domain."""
    sims = torch.mm(domain_emb, task_emb.T)
    mean_sims = sims.mean(dim=1)
    
    scores = {}
    for domain in set(domain_labels):
        mask = [l == domain for l in domain_labels]
        scores[domain] = mean_sims[mask].mean().item()
    return scores

def main():
    model = SentenceTransformer('intfloat/e5-large-v2')
    
    # Load data
    domain_texts, domain_labels = load_pile_subset(DOMAINS, SAMPLES_PER_DOMAIN)
    task_texts = load_mmlu_validation()
    
    # Embed
    domain_emb = model.encode(["passage: " + t for t in domain_texts],
                               convert_to_tensor=True, normalize_embeddings=True)
    task_emb = model.encode(["query: " + t for t in task_texts],
                            convert_to_tensor=True, normalize_embeddings=True)
    
    # Compute scores
    scores = compute_domain_scores(domain_emb, task_emb, domain_labels)
    
    # Validate
    values = list(scores.values())
    std = np.std(values)
    print(f"Domain scores: {scores}")
    print(f"Std: {std:.4f}")
    print(f"PASS: {std > 0.05}")
    
    with open("results/domain_scores.json", "w") as f:
        json.dump({"scores": scores, "std": std, "pass": std > 0.05}, f, indent=2)

if __name__ == "__main__":
    main()
```

---

## Document Status

**Status:** COMPLETE
**Created:** 2026-08-28
**Next Phase:** Phase 3 (Implementation Planning)

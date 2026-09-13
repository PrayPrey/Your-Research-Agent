# Phase 2C: Experiment Brief for H-M1

## Hypothesis Summary

**ID:** h-m1  
**Type:** MECHANISM  
**Statement:** Mode 3 response pairs have lower semantic similarity than Mode 1 response pairs (Cohen's d > 0.3)  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-e1 (VALIDATED)

## Success/Falsification Criteria

| Criterion | Threshold | Statistical Test |
|-----------|-----------|------------------|
| Success | Cohen's d > 0.3 (Mode 1 similarity > Mode 3 similarity) | Welch's t-test, p < 0.05 |
| Falsification | Cohen's d < 0.1 OR opposite direction | Same test, p ≥ 0.05 or negative d |

---

## Dataset Specification

### Primary Dataset

| Field | Value |
|-------|-------|
| Name | Reuse h-e1 mode classification outputs |
| Type | standard (derived from lmsys/chatbot_arena_conversations) |
| Source | h-e1 pipeline outputs: `rm_scores.parquet`, `mode_distribution.json` |
| Size | Full h-e1 dataset (~20K+ battles with mode labels) |
| Required Fields | `response_a`, `response_b`, `mode_label` |

### Sample Selection

1. **Mode 1 (Aligned-Confident):** Low human entropy, low RM variance
   - Expected: ~25% of samples (~5K+)
2. **Mode 3 (Misaligned-Confident):** High human entropy, low RM variance
   - Validated: 23.7% of samples (~4.7K+)

### Minimum Sample Size

- Require n ≥ 500 per mode for reliable Cohen's d estimation
- h-e1 validation confirms both modes exceed this threshold

---

## Model Specification

### Semantic Similarity Model

| Field | Value |
|-------|-------|
| Model | sentence-transformers/all-MiniLM-L6-v2 |
| Type | Sentence Transformer (bi-encoder) |
| Embedding Dim | 384 |
| Speed | Fast (~1000 sentences/sec on GPU) |
| HuggingFace | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 |

### Similarity Computation

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# For each battle (response_a, response_b):
emb_a = model.encode(response_a)
emb_b = model.encode(response_b)

# Cosine similarity via model.similarity() or sklearn
similarity = model.similarity([emb_a], [emb_b])[0][0]
# Range: [-1, 1], typically [0, 1] for same-domain text
```

---

## Implementation Approach

### Dependencies

```
sentence-transformers>=2.2.0
scipy>=1.10.0
numpy>=1.24.0
pandas>=2.0.0
torch>=2.0.0
tqdm
```

### Pipeline Steps

1. **Data Loading** (1 min)
   - Load h-e1 outputs: mode labels + response pairs
   - Filter to Mode 1 and Mode 3 samples only

2. **Embedding Computation** (10-20 min on GPU)
   - Encode all response_a texts
   - Encode all response_b texts
   - Batch size: 64-128 (MiniLM is small)
   - Cache embeddings to disk

3. **Similarity Calculation** (1 min)
   - Cosine similarity for each (response_a, response_b) pair
   - Store per-battle similarity scores

4. **Statistical Comparison** (1 min)
   - Split by mode: similarities_mode1, similarities_mode3
   - Welch's t-test (unequal variance)
   - Cohen's d with pooled standard deviation

---

## Statistical Analysis

### Cohen's d Formula (Pooled SD)

```python
from numpy import mean, std, sqrt

def cohen_d(x, y):
    """Cohen's d for independent samples with unequal n."""
    nx, ny = len(x), len(y)
    dof = nx + ny - 2
    pooled_std = sqrt(((nx - 1) * std(x, ddof=1)**2 + 
                       (ny - 1) * std(y, ddof=1)**2) / dof)
    return (mean(x) - mean(y)) / pooled_std
```

### Interpretation

| Cohen's d | Effect Size |
|-----------|-------------|
| < 0.2 | Negligible |
| 0.2 - 0.5 | Small |
| 0.5 - 0.8 | Medium |
| > 0.8 | Large |

**Hypothesis requires d > 0.3** (small-to-medium effect)

### Expected Direction

- Mode 1 (Aligned-Confident): RMs and humans agree → responses likely similar
- Mode 3 (Misaligned-Confident): RMs disagree with humans → responses likely diverse/divergent

**Expected: mean(similarity_mode1) > mean(similarity_mode3)**

---

## Output Specification

### Primary Outputs

| File | Description |
|------|-------------|
| `embeddings.npz` | Cached embeddings for all responses |
| `similarity_scores.parquet` | Per-battle similarity with mode labels |
| `statistical_results.json` | Cohen's d, t-test results, CI |

### Success Output Format

```json
{
  "hypothesis_id": "h-m1",
  "mode_1_n": 5200,
  "mode_3_n": 4700,
  "mode_1_mean_similarity": 0.72,
  "mode_3_mean_similarity": 0.58,
  "mode_1_std": 0.15,
  "mode_3_std": 0.18,
  "cohens_d": 0.85,
  "t_statistic": 42.3,
  "p_value": 1e-200,
  "ci_95_d": [0.80, 0.90],
  "result": "CONFIRMED",
  "effect_interpretation": "large"
}
```

---

## Compute Requirements

| Resource | Estimate |
|----------|----------|
| GPU | 1x any GPU (MiniLM is 22M params) |
| VRAM | ~1GB |
| Time | 30-60 min total |
| Storage | ~500MB for embeddings |

### CPU-Only Fallback

MiniLM runs on CPU at ~100 sentences/sec. For 40K responses:
- Time: ~7 minutes (acceptable)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Mode sample size too small | h-e1 validates >20% for Mode 3; Mode 1 should be similar |
| Similarity scores homogeneous | Sensitivity analysis with alternative models |
| Embedding model bias | Secondary check with all-mpnet-base-v2 |
| Non-normal distributions | Bootstrap CI for Cohen's d |

### Alternative Models (Sensitivity Analysis)

| Model | Dim | Notes |
|-------|-----|-------|
| all-mpnet-base-v2 | 768 | Higher quality, slower |
| paraphrase-MiniLM-L6-v2 | 384 | Tuned for paraphrase detection |

---

## Literature Grounding

| Paper | Relevance |
|-------|-----------|
| Sentence-BERT (Reimers & Gurevych, 2019) | Foundation for sentence embeddings |
| SimCSE (Gao et al., 2021) | Contrastive learning for similarity |
| Cohen (1988) | Effect size conventions (d = 0.2/0.5/0.8) |
| Sawilowsky (2009) | Extended effect size rules |

---

## Dependency on H-E1

### Required from H-E1

1. Mode classification per battle (mode_label ∈ {1, 2, 3, 4})
2. Response pairs (response_a, response_b)
3. Validated Mode 3 exists (23.7% confirmed)

### H-E1 Output Files Used

```
h-e1/code/outputs/
├── mode_distribution.json    # Mode labels per battle
├── rm_scores.parquet         # Contains response texts
└── battles_classified.csv    # Battle ID → mode mapping
```

---

## Validation Checklist

- [ ] H-E1 outputs loaded successfully
- [ ] Mode 1 and Mode 3 samples extracted (n ≥ 500 each)
- [ ] Embeddings computed for all responses
- [ ] Similarity scores computed
- [ ] Welch's t-test executed
- [ ] Cohen's d calculated with CI
- [ ] Results serialized to JSON

---

## Phase 3 Handoff

Ready for implementation planning with:
- Reuses h-e1 mode classification (no redundant RM scoring)
- Standard sentence-transformers pipeline
- Clear statistical test (Welch's t-test + Cohen's d)
- Small compute requirements
- Well-defined output schema

**Estimated Implementation Complexity:** LOW (simple embedding + statistical comparison)

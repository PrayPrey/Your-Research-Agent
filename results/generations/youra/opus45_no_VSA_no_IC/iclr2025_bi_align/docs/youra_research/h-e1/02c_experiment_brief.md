# Phase 2C: Experiment Brief for H-E1

## Hypothesis Summary

**ID:** h-e1  
**Type:** EXISTENCE  
**Statement:** Mode 3 (Misaligned-Confident: high human entropy, low RM variance) constitutes >10% of Chatbot Arena samples  
**Gate:** MUST_WORK  

## Success/Falsification Criteria

| Criterion | Threshold | Statistical Test |
|-----------|-----------|------------------|
| Success | Proportion > 10% | One-sided binomial test, p < 0.05 |
| Falsification | Proportion < 5% OR 95% CI includes 10% | Same test, p ≥ 0.05 |

---

## Dataset Specification

### Primary Dataset

| Field | Value |
|-------|-------|
| Name | lmsys/chatbot_arena_conversations |
| Type | standard |
| Source | HuggingFace Datasets |
| Access | Requires agreement to ToS |
| Size | ~33K battles (original release) |
| Required Fields | `conversation_a`, `conversation_b`, `winner` |

### Filtering Criteria

1. **Valid battles only**: Must have `winner` in {`model_a`, `model_b`, `tie`, `tie (bothbad)`}
2. **Multi-turn support**: Extract final assistant response from each conversation
3. **Minimum sample**: Use full dataset (no subsampling); expect 20K+ usable battles

### Human Entropy Calculation

Since individual battles have binary outcomes (no soft labels), human entropy is computed at the **model-pair level**:

```
For each (model_a, model_b) pair:
  - Count wins for A, B, ties
  - Normalize to probability distribution P = [p_a, p_b, p_tie]
  - Entropy H = -Σ p_i * log2(p_i)
  - High entropy: H > median(all pair entropies)
```

Alternative (if model IDs unavailable): Use prompt-level aggregation where same/similar prompts appear multiple times.

---

## Model Specification

### RM Ensemble

Use RewardBench-compatible pipelines for consistent inference:

| Model | HuggingFace ID | Type | Size |
|-------|---------------|------|------|
| OpenAssistant | OpenAssistant/reward-model-deberta-v3-large-v2 | Classifier | 0.4B |
| PairRM | llm-blender/PairRM | Pairwise | 0.4B |
| ArmoRM | RLHFlow/ArmoRM-Llama3-8B-v0.1 | MoE | 8B |

### Variance Calculation

```python
# For each response pair (response_a, response_b):
scores_a = [rm.score(prompt, response_a) for rm in [openassistant, pairrm, armorm]]
scores_b = [rm.score(prompt, response_b) for rm in [openassistant, pairrm, armorm]]

# Normalize scores to [0, 1] via z-score then sigmoid
scores_a_norm = [zscore_sigmoid(s) for s in scores_a]
scores_b_norm = [zscore_sigmoid(s) for s in scores_b]

# Variance of normalized preference signal
pref_signal = [a - b for a, b in zip(scores_a_norm, scores_b_norm)]
rm_variance = np.var(pref_signal)

# Low variance: rm_variance < median(all rm_variances)
```

---

## Implementation Approach

### Dependencies

```
datasets>=2.14.0
transformers>=4.40.0
torch>=2.0.0
rewardbench>=0.1.4  # Unified RM inference
scipy>=1.10.0       # Binomial test
pandas>=2.0.0
tqdm
```

### Pipeline Steps

1. **Data Loading** (5 min)
   - Load lmsys/chatbot_arena_conversations
   - Filter valid battles
   - Extract prompt + response pairs

2. **RM Scoring** (2-4 hours on single GPU)
   - Score all responses with 3 RMs
   - Cache scores to disk (resume support)
   - Batch size: 8-16 depending on GPU memory

3. **Mode Classification** (1 min)
   - Compute human entropy per model-pair
   - Compute RM variance per battle
   - Median split on both dimensions
   - Assign 4 modes: (Low-H, Low-V), (Low-H, High-V), (High-H, Low-V), (High-H, High-V)

4. **Statistical Testing** (1 min)
   - Count Mode 3 samples
   - One-sided binomial test: H0: p ≤ 0.10 vs H1: p > 0.10
   - Report proportion, 95% CI, p-value

---

## Output Specification

### Primary Outputs

| File | Description |
|------|-------------|
| `mode_distribution.json` | Counts and proportions for all 4 modes |
| `statistical_results.json` | Binomial test results, CI, p-value |
| `rm_scores.parquet` | Cached RM scores for all responses |

### Success Output Format

```json
{
  "hypothesis_id": "h-e1",
  "mode_3_count": 3500,
  "total_count": 20000,
  "proportion": 0.175,
  "ci_95_lower": 0.168,
  "ci_95_upper": 0.182,
  "p_value": 0.0001,
  "result": "CONFIRMED",
  "statistical_power": 0.99
}
```

---

## Compute Requirements

| Resource | Estimate |
|----------|----------|
| GPU | 1x A100 (40GB) or 2x RTX 3090 |
| VRAM | ~20GB peak (ArmoRM) |
| Time | 3-5 hours total |
| Storage | ~2GB for scores cache |

### Fallback for Limited Compute

If ArmoRM unavailable due to memory:
- Use OpenAssistant + PairRM only (2 models)
- Document limitation in results
- Variance less stable but still meaningful

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Dataset ToS rejection | Use public arena-hard-auto subset instead |
| Model-pair entropy not computable | Fall back to prompt-cluster entropy |
| RM scores not comparable | Z-score normalization per model |
| Low Mode 3 count | Sensitivity analysis at 5%, 8%, 10% thresholds |

---

## Literature Grounding

| Paper | Relevance |
|-------|-----------|
| CHARM (Zhu et al., 2026) | RM calibration with Arena Elo; validates Arena as RM ground truth |
| Reward Model Ensembles (Eisenstein et al., 2023) | Ensemble variance as proxy for uncertainty |
| Variance-aware Reward Modeling (Fang et al., 2026) | Variance from pairwise preferences; anchor guidance |
| RewardBench (Lambert et al., 2024) | Unified RM evaluation; implementation patterns |

---

## Validation Checklist

- [ ] Dataset loads successfully
- [ ] All 3 RMs produce valid scores
- [ ] Mode classification yields 4 non-empty groups
- [ ] Statistical test completes
- [ ] Mode 3 proportion computed with CI
- [ ] Results serialized to JSON

---

## Phase 3 Handoff

Ready for implementation planning with:
- Clear data pipeline
- Known model APIs (RewardBench)
- Defined output schema
- Statistical test specified
- Compute requirements estimated

**Estimated Implementation Complexity:** MEDIUM (standard ML pipeline, no custom training)

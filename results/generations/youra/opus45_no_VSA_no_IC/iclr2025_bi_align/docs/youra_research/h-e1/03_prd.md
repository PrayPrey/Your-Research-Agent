# Product Requirements Document: H-E1

## Hypothesis
**ID:** h-e1  
**Type:** EXISTENCE  
**Statement:** Mode 3 (Misaligned-Confident: high human entropy, low RM variance) constitutes >10% of Chatbot Arena samples  
**Gate:** MUST_WORK

---

## Executive Summary

Validate existence of Mode 3 disagreement pattern in Chatbot Arena data. Success requires demonstrating >10% of samples fall into high-human-entropy, low-RM-variance quadrant with statistical significance (p < 0.05).

---

## Problem Statement

Current RM alignment assumes human preferences correlate with RM confidence. Mode 3 represents cases where humans disagree (high entropy) but RMs confidently agree (low variance) — indicating systematic blind spots. Quantifying this mode's prevalence is prerequisite for downstream mechanism/comparison hypotheses.

---

## Functional Requirements

### FR-1: Data Pipeline
| Requirement | Specification |
|-------------|---------------|
| Dataset | lmsys/chatbot_arena_conversations |
| Size | Full dataset (~33K battles, expect 20K+ valid) |
| Filtering | Valid battles only (winner in {model_a, model_b, tie, tie (bothbad)}) |
| Output | Structured records with prompt, response_a, response_b, winner |

### FR-2: RM Scoring
| Model | HuggingFace ID | Type |
|-------|----------------|------|
| OpenAssistant | OpenAssistant/reward-model-deberta-v3-large-v2 | Classifier |
| PairRM | llm-blender/PairRM | Pairwise |
| ArmoRM | RLHFlow/ArmoRM-Llama3-8B-v0.1 | MoE |

- Score all responses with 3 RMs
- Normalize via z-score + sigmoid to [0,1]
- Compute RM variance per battle

### FR-3: Human Entropy Calculation
- Aggregate at model-pair level
- Entropy H = -Σ p_i * log2(p_i) for P = [p_a, p_b, p_tie]
- High entropy: H > median(all pair entropies)

### FR-4: Mode Classification
- Median split on human entropy and RM variance
- 4 modes: (Low-H, Low-V), (Low-H, High-V), (High-H, Low-V), (High-H, High-V)
- Mode 3 = High-H, Low-V

### FR-5: Statistical Testing
- One-sided binomial test: H0: p ≤ 0.10 vs H1: p > 0.10
- Report proportion, 95% CI, p-value
- Success: p-value < 0.05 AND proportion > 0.10

### FR-6: Ablation - 2-Model Fallback
- If ArmoRM unavailable due to VRAM
- Use OpenAssistant + PairRM only
- Document limitation in results

### FR-7: Ablation - Prompt-Cluster Entropy
- Alternative if model IDs unavailable
- Cluster similar prompts, compute entropy within clusters

---

## Non-Functional Requirements

| NFR | Specification |
|-----|---------------|
| Compute | 1x A100 (40GB) or 2x RTX 3090 |
| VRAM | ~20GB peak (ArmoRM) |
| Runtime | 3-5 hours total |
| Storage | ~2GB for scores cache |
| Reproducibility | Cache RM scores to parquet |

---

## Success Criteria

| Criterion | Threshold | Test |
|-----------|-----------|------|
| Success | Mode 3 proportion > 10% | Binomial p < 0.05 |
| Falsification | Proportion < 5% OR CI includes 10% | Same test p ≥ 0.05 |

---

## Output Artifacts

| File | Description |
|------|-------------|
| mode_distribution.json | Counts/proportions for all 4 modes |
| statistical_results.json | Binomial test, CI, p-value |
| rm_scores.parquet | Cached RM scores |

---

## Dependencies

```
datasets>=2.14.0
transformers>=4.40.0
torch>=2.0.0
rewardbench>=0.1.4
scipy>=1.10.0
pandas>=2.0.0
tqdm
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Dataset ToS rejection | Use arena-hard-auto subset |
| Model-pair entropy not computable | Prompt-cluster entropy fallback |
| RM scores not comparable | Z-score normalization per model |
| Low Mode 3 count | Sensitivity analysis at 5%, 8%, 10% |

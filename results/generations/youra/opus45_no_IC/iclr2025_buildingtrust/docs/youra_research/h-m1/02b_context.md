# Phase 2B Context: H-M1

**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Statement:** LLMs produce category-specific confidence distributions on TruthfulQA

## Gate Condition
- **Type:** MUST_WORK
- **Pass Condition:** KS test p < 0.05 for majority of cluster pairs
- **Fail Action:** PIVOT clustering

## Prerequisites
- **h-e1:** COMPLETED (PASS - ANOVA p=0.00012 < 0.05, ECE range=0.099 > 0.05)

## Experimental Setup (from Phase 2B Section 1.3)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA (standard) | 38 category labels enable cluster-level analysis |
| **Model** | Llama-2-7B (primary) | Open model with logit access |

**Dataset Details:**
- Source: https://github.com/sylinrl/TruthfulQA
- Path: TruthfulQA.csv
- Size: 817 questions, 38 categories → 7 clusters

**Model Details:**
- Type: decoder-only transformers
- Source: HuggingFace Hub

## Verification Protocol
1. Extract softmax confidence for all TruthfulQA predictions
2. Group by cluster, compute confidence histograms
3. Run pairwise Kolmogorov-Smirnov tests
4. Visualize cluster-level confidence distributions
5. Report distribution statistics per cluster

## Success Criteria (PoC)
- **Primary:** KS test p < 0.05 for majority of cluster pairs
- **Secondary:** Mean confidence differs by >0.1 across clusters

## Variables
- **Independent:** Semantic cluster
- **Dependent:** Confidence distribution (histogram)
- **Controlled:** Model, binning strategy

## Continuation Context
Building on h-e1 results which confirmed category-dependent ECE variation exists (F=8.45, p=0.00012). This mechanism hypothesis tests whether the underlying confidence distributions differ across clusters.

## Source
Phase 2A causal_mechanism.steps[0]

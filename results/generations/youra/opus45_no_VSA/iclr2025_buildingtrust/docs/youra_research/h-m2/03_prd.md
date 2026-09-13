# Product Requirements Document
## H-M2: Instruction-Tuning Effect on BSI and PC1,residual

Generated: 2026-08-08
Hypothesis Type: MECHANISM
Gate: SHOULD_WORK

---

## Executive Summary

Validate whether instruction-tuning systematically improves behavioral stability (BSI) and trustworthiness (PC1,residual) across matched base/instruct model pairs using paired statistical tests.

---

## Problem Statement

Prior work (H-E1) established that a latent trustworthiness factor (λ₁=2.277) exists across LLMs. This hypothesis tests whether instruction-tuning is a causal mechanism that increases this factor, measured through:
1. Behavioral Stability Index (BSI) on paraphrase consistency
2. PC1,residual scores from trustworthiness benchmarks

---

## Functional Requirements

### FR-1: Model Pair Management
- **FR-1.1:** Load 16 matched base/instruct model pairs from HuggingFace
- **FR-1.2:** Support model families: Llama-2, Llama-3, Llama-3.1, Llama-3.2, Mistral, Mixtral, Qwen2, Gemma, Gemma-2, Phi-3
- **FR-1.3:** Handle parameter ranges from 1B to 72B

### FR-2: BSI Evaluation
- **FR-2.1:** Load PAWS-Wiki test set (8,000 pairs)
- **FR-2.2:** Load PAWS-QQP dev set (677 pairs)
- **FR-2.3:** Implement paraphrase detection task for each model
- **FR-2.4:** Compute agreement scores between original and paraphrased inputs
- **FR-2.5:** Calculate BSI = mean agreement across all pairs

### FR-3: PC1,residual Computation
- **FR-3.1:** Reuse H-E1 validated residualization pipeline
- **FR-3.2:** Load 6 benchmark scores: TruthfulQA, MMLU, AdvGLUE, BBH, GSM8K, WinoGrande
- **FR-3.3:** Residualize against log(params) and release_date
- **FR-3.4:** Apply PCA to extract PC1 scores

### FR-4: Statistical Analysis
- **FR-4.1:** Compute paired differences: Δ_BSI = instruct - base
- **FR-4.2:** Compute paired differences: Δ_PC1 = instruct - base
- **FR-4.3:** Run paired t-test for BSI (scipy.stats.ttest_rel)
- **FR-4.4:** Run paired t-test for PC1 (scipy.stats.ttest_rel)
- **FR-4.5:** Calculate Cohen's d effect sizes
- **FR-4.6:** Run Wilcoxon signed-rank test (robustness check)
- **FR-4.7:** Compute correlation between Δ_BSI and Δ_PC1

### FR-5: Ablation: Few-Shot Prompting
- **FR-5.1:** Implement few-shot (3-shot) prompting for base models
- **FR-5.2:** Compare zero-shot instruct vs few-shot base BSI

---

## Non-Functional Requirements

### NFR-1: Performance
- Support 80GB VRAM for 70B models
- Complete evaluation in <8h on A100

### NFR-2: Reproducibility
- Fixed random seeds
- Greedy decoding (temperature=0)
- Deterministic batch ordering

### NFR-3: Storage
- ~500GB for model weights
- Results in CSV/JSON format

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Δ_BSI > 0 | p < 0.05 paired t-test |
| Δ_PC1 > 0 | p < 0.05 paired t-test |
| Both must pass | Conjunctive test |

---

## Data Requirements

| Dataset | Source | Size |
|---------|--------|------|
| PAWS-Wiki | google-research-datasets/paws | 8,000 test pairs |
| PAWS-QQP | google-research-datasets/paws | 677 dev pairs |
| Benchmark scores | Open LLM Leaderboard | 6 benchmarks × 32 models |

---

## Dependencies

- H-E1: PC1,residual computation pipeline (VALIDATED)
- HuggingFace Transformers
- scipy.stats for statistical tests
- sklearn.decomposition for PCA

---

## Out of Scope

- Training new models
- Fine-tuning experiments
- Cross-family comparisons (only within-family pairs)

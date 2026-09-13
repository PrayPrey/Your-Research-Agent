# Product Requirements Document: H-M2

**Hypothesis:** Removing high-CCR examples causes ≥1.5× larger accuracy drop than random removal (95% CI excludes zero and random mean)
**Date:** 2026-08-08
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Executive Summary

This experiment tests the causal necessity of high-CCR (Contamination-Correlated Response) examples for benchmark performance. Building on H-M1's validated CCR measurement methodology, we perform removal intervention experiments: removing high-CCR examples vs. random removal, then measuring differential accuracy degradation on MMLU.

**Success Criterion:** Degradation ratio ≥1.5 with 95% bootstrap CI excluding 1.0.

---

## Problem Statement

H-M1 established that perplexity-filtered training produces higher CCR than random sampling. H-M2 addresses: *Are high-CCR examples causally necessary for benchmark performance, or merely correlated?*

**Hypothesis:** If high-CCR examples drive contamination-induced benchmark inflation, removing them should cause disproportionately larger accuracy drops than random removal.

---

## Functional Requirements

### FR-1: CCR-Based Example Identification
- Load CCR scores from H-M1 output
- Identify high-CCR examples (top 5% by CCR score)
- Create removal masks for high-CCR and random subsets

### FR-2: Removal Intervention Training
- Train Pythia-1B on 3 conditions:
  - Baseline (no removal)
  - High-CCR removal (remove top 5% CCR examples)
  - Random removal (remove random 5% examples)
- 5 seeds per condition (15 training runs total)
- 3 removal fractions: 1%, 2%, 5%

### FR-3: MMLU Evaluation
- Evaluate all trained models on full MMLU test set (14,042 samples)
- Use lm-evaluation-harness for standardized evaluation
- Record per-model accuracy

### FR-4: Degradation Ratio Computation
- Compute: (baseline_acc - high_ccr_acc) / (baseline_acc - random_acc)
- Bootstrap CI estimation (10,000 resamples)
- Test whether CI excludes 1.0

### FR-5: Visualization Generation
- Gate metrics bar chart with 95% CI error bars
- Accuracy drop by removal fraction
- Bootstrap distribution of degradation ratio

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds for all experiments
- Deterministic training (set all random states)
- Version-locked dependencies

### NFR-2: Computational Efficiency
- Mixed precision training (fp16)
- Gradient checkpointing for memory efficiency
- 10,000 training steps per run (subset training)

### NFR-3: Statistical Rigor
- 5 seeds per condition for variance estimation
- Bootstrap CI with 10,000 resamples
- Effect size reporting

---

## Data Specifications

### Training Data
- **Source:** RedPajama-V2 (perplexity-filtered from H-M1)
- **CCR Scores:** From H-M1 TRAK-based CCR computation
- **Removal Sets:**
  - High-CCR: Examples with CCR > 95th percentile
  - Random: Random selection of equal size

### Evaluation Data
- **MMLU:** cais/mmlu (14,042 test samples)
- **Full test set** for statistical power

---

## Model Specifications

### Base Model
- **Model:** Pythia-1B (EleutherAI/pythia-1b)
- **Parameters:** 1 billion
- **Architecture:** GPT-NeoX

### Training Configuration
- Optimizer: AdamW (lr=1e-4, weight_decay=0.01)
- Schedule: Cosine with 10% warmup
- Batch size: 512 tokens/GPU, 8 gradient accumulation
- Steps: 10,000

---

## Success Criteria

### Primary Gate (MUST_WORK)
1. Degradation ratio ≥ 1.5
2. 95% bootstrap CI excludes 1.0
3. 95% CI excludes random removal mean

### Secondary Metrics
- Consistent effect across removal fractions (1%, 2%, 5%)
- Monotonic relationship: larger CCR removal → larger degradation

---

## Dependencies

### Prerequisites
- H-M1 validation completed (CCR methodology validated)
- H-M1 CCR scores available for RedPajama corpus

### External Dependencies
- PyTorch, Transformers, datasets
- lm-evaluation-harness
- TRAK (for CCR scoring inheritance)

---

## Deliverables

1. `run_removal_experiment.py` - Main experiment script
2. `RemovalIntervention` class - High-CCR/random removal logic
3. `evaluate_degradation.py` - Degradation ratio + bootstrap CI
4. `figures/` - Required visualizations
5. `04_validation.md` - Validation report

---

*Generated from Phase 2C experiment brief (02c_experiment_brief.md)*

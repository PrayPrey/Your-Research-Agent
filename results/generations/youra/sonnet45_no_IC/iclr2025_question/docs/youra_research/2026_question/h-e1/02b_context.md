# Phase 2B Context: H-E1

**Hypothesis ID:** h-e1
**Type:** Existence
**Date:** 2026-07-13

## Hypothesis Statement

Under foundation model uncertainty quantification settings, if we measure the correlation between consistency-based scores (C) and conformal prediction interval membership (I), then we observe 0.3 < ρ(C,I) < 0.7, because consistency methods capture epistemic uncertainty (generative inconsistency) while conformal methods capture aleatoric uncertainty (inherent data ambiguity), representing distinct but complementary information sources.

## Rationale

This hypothesis validates the core assumption (A1) that consistency and conformal methods measure non-redundant aspects of uncertainty. If ρ > 0.8 (redundant) or ρ < 0.2 (independent), the entire HBC joint calibration approach collapses to baseline performance. This is the foundation for all subsequent mechanism hypotheses.

## Experimental Setup

### Dataset

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Primary Dataset** | TruthfulQA (standard) | Tests epistemic uncertainty (model knowledge gaps), widely benchmarked for hallucination detection |
| **Secondary Dataset** | HH-RLHF (standard) | Tests aleatoric uncertainty (value alignment ambiguity), provides complementary uncertainty signal |
| **Tertiary Dataset** | SQuAD (standard) | Mixed-uncertainty baseline, established benchmark |

**Dataset Details:**
- **TruthfulQA**: 
  - Source: https://github.com/sylinrl/TruthfulQA
  - Type: standard
  - Path: To be auto-downloaded
  - Hypothesis Fit: Directly tests epistemic uncertainty via knowledge gaps
  
- **HH-RLHF**:
  - Source: Anthropic
  - Type: standard
  - Path: To be auto-downloaded
  - Hypothesis Fit: Tests aleatoric uncertainty via value alignment ambiguity

- **SQuAD**:
  - Source: Stanford
  - Type: standard
  - Path: To be auto-downloaded
  - Hypothesis Fit: Mixed uncertainty baseline for comparison

### Model

**Model**: Llama-2-7B
**Type**: Autoregressive transformer LLM
**Source**: Meta AI, HuggingFace Hub

**Hypothesis Fit**: 
- Widely benchmarked (reproducibility)
- Supports sampling (required for consistency methods)
- 7B size manageable for multi-sample experiments
- Established baselines on TruthfulQA/SQuAD

## Success Criteria

**MUST_WORK Gate:**
- Primary: 0.3 ≤ ρ ≤ 0.7 on all three datasets (TruthfulQA, HH-RLHF, SQuAD)
- Secondary: p < 0.05 for two-tailed significance test on each dataset
- Statistical Power: n ≥ 1000 per dataset

## Verification Protocol

1. Generate consistency scores C(x) using SelfCheckGPT (5 samples, NLI+BERTScore ensemble) for n≥1000 validation samples per dataset
2. Compute conformal prediction intervals I(x) with 90% coverage target, binary indicator I_binary(x) = 1 if y ∈ I(x) else 0
3. Calculate Pearson correlation ρ(C, I_binary) on validation set for each dataset
4. Perform two-tailed significance test (p<0.05) to verify correlation differs from extreme values (ρ ≠ 0.9, ρ ≠ 0.1)
5. Verify sweet spot: 0.3 ≤ ρ ≤ 0.7 on ALL three datasets

## Gate Conditions

**Type**: MUST_WORK
**Prerequisites**: None (foundation hypothesis)
**Failure Response**: If ρ > 0.8 on any dataset, methods redundant → PIVOT to single-method optimization (abandon HBC). If ρ < 0.2 on any dataset, methods independent → EXPLORE alternative integration approaches or ABANDON HBC.

## Baseline Methods for Comparison

| Method | Performance | Dataset |
|--------|-------------|---------|
| SelfCheckGPT (Manakul et al., 2023) | Strong hallucination detection empirically, no statistical guarantees | WikiBio, multiple domains |
| COIN conformal prediction (Wang et al., 2025) | 90%+ coverage with FDR control, computationally expensive | TruthfulQA, factuality benchmarks |
| FactTest (Nie et al., 2024) | Hypothesis testing framework with Type I/II error control | General factuality evaluation |

**Best Baseline Performance:** Independent cascade (SelfCheckGPT → COIN) achieves ECE ~0.06-0.08 on TruthfulQA (inferred from discussion, to be validated)

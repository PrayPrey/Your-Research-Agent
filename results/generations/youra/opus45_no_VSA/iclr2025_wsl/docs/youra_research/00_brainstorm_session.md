---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Weight Space Geometric Signatures"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-10
**Facilitator:** Research Question Architect
**Participant:** Anonymous
**Mode:** UNATTENDED (ROUTE_TO_0 - Failure Recovery)

---

## Executive Summary

**Initial Interest:** Neural Network Weights as a New Data Modality - extracting geometric signatures from weight spaces that reliably predict model properties.

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction with failure context)

---

## Starting Context

The research area stems from the ICLR 2025 Workshop on Neural Network Weights as a New Data Modality. Over a million neural network models are publicly available on platforms like Hugging Face, creating opportunities to treat neural network weights as analyzable data.

**Source:** Workshop CFP with mandatory feasibility constraints (existing datasets/benchmarks only).

---

## Lessons from Previous Attempts

### Summary of 7 Failed/Partial Runs

**Previous Research Direction:** Weight space learning for model property prediction, focusing on learned embeddings (SANE, CISE, NFN) and contrastive representation learning.

**What Failed and Why:**

| Hypothesis | Failure Type | Root Cause |
|------------|--------------|------------|
| h-e1 (Run 1) | IMPLEMENTATION_PROXY_MISMATCH | Random projection proxy ≠ trained SANE encoder. R² = -2.95 vs baseline 0.01 |
| h-e1 (Run 2) | PARTIAL_CRITERIA_MET | 36.4% models stable (CV<0.3) vs 50% target. Large models unstable |
| h-m1 (Run 1) | HYPOTHESIS_FALSIFIED | ED PR >> EcD PR — bounded d* is CONTRASTIVE-INDUCED, not intrinsic |
| h-m2 (Run 1) | MUST_WORK_GATE_FAILED | Single-layer NFN lacks capacity for ranking. AUC 0.47 vs HyperRep 0.78 |
| h-m1 (limitation) | PARTIAL | 3/4 geometry metrics significant; alpha (power-law) failed p=0.55 |
| h-e2 (pivot) | REQUIRES_REDESIGN | OrbitVar 0.000158 vs 0.1 required — random-init encoders near-equivariant |

**Critical Lessons:**

1. **Pretrained encoders required** — random projections/random-init encoders do not work
2. **Contrastive loss drives bounded dimensionality** — not intrinsic to weight manifolds
3. **Architecture capacity must match task** — single-layer NFN insufficient for ranking
4. **Model size affects stability** — larger models (ResNet152) show CV > 1.0
5. **Effective dimensionality metrics work** — r_eff, PR, d_MLE show large effect sizes; alpha does not discriminate

### How This Direction Avoids Past Pitfalls

**NEW APPROACH:** Focus on **geometric signatures extractable WITHOUT learned encoders** — spectral properties, weight statistics, and layer-wise patterns that are:
1. Directly computable (no pretrained checkpoint needed)
2. Architecture-aware (normalize by model capacity)
3. Based on metrics that showed promise (r_eff, PR, d_MLE — NOT alpha)

---

## Session Plan

ROUTE_TO_0 Auto-Fill: Generate research question that:
- Avoids learned embedding approaches (h-e1, h-e2 failures)
- Avoids contrastive-intrinsic assumptions (h-m1 falsified)
- Uses direct weight statistics (h-e1 Run 2 showed stability correlates with architecture)
- Focuses on effective dimensionality (limitation record: 3/4 metrics worked)

---

## Technique Sessions

**Failure-Informed Direction Selection:**

From failure records, the following showed PROMISE:
1. **Spectral features ARE extractable** (h-e1 Run 2) — existence confirmed
2. **Effective dimensionality metrics discriminate** (h-m1 limitation) — r_eff, PR, d_MLE with large effect sizes
3. **Group normalization models achieve perfect stability** (h-e1 Run 2) — CV = 0.0
4. **Mechanism verification infrastructure works** (h-e1 Run 1) — output shape, variance, decorrelation

**Avoiding pitfalls:**
- NO random projection proxies for learned encoders
- NO assumptions about intrinsic bounded dimensionality
- NO single-layer architectures for complex tasks
- NO architecture-agnostic thresholds

**Selected New Direction:** Architecture-Aware Geometric Signatures
- Use direct spectral computation (no learned encoder)
- Normalize by architecture family (ResNet vs ViT vs ConvNeXt)
- Focus on r_eff, PR, d_MLE (not alpha)
- Target model property prediction with architecture-specific baselines

---

## Research Question Development

### Initial Question

Can architecture-normalized geometric signatures (effective dimensionality, participation ratio) of neural network weights predict model properties more reliably than architecture-agnostic statistics?

### Refined Question

How do architecture-specific geometric signatures (layer-wise effective dimensionality, participation ratio, spectral decay patterns) of pretrained model weights correlate with model performance, and can architecture-aware normalization improve prediction accuracy across diverse model families?

### Detailed Sub-Questions

1. Which geometric metrics (r_eff, PR, d_MLE) show strongest correlation with model accuracy within architecture families?
2. How should geometric signatures be normalized across different architecture capacities (parameter count, depth, width)?
3. Do normalization-type patterns (BatchNorm vs GroupNorm vs LayerNorm) create distinct geometric signature clusters?
4. Can architecture-family-specific predictors outperform universal predictors for model property estimation?
5. What is the minimum model zoo size required for statistically significant within-family predictions?

---

## Reference Papers

1. **"Predicting Neural Network Accuracy from Weights" (Unterthiner et al., 2020)** - Baseline methodology
   - Relevance: Direct predecessor, establishes benchmark

2. **"Git Re-Basin: Merging Models Modulo Permutation Symmetries" (Ainsworth et al., 2023)** - Permutation symmetry handling
   - Relevance: Weight alignment for fair comparison

3. **"Model Soups: Averaging Weights of Multiple Fine-tuned Models" (Wortsman et al., 2022)** - Weight space operations
   - Relevance: Existing benchmarks, model zoo methodology

4. **"Heavy-Tailed Self-Regularization in Deep Neural Networks" (Martin & Mahoney, 2019)** - Spectral analysis of weights
   - Relevance: Effective dimensionality, power-law analysis

5. **"Measuring the Intrinsic Dimension of Objective Landscapes" (Li et al., 2018)** - Dimensionality estimation
   - Relevance: r_eff, PR computation methodology

---

## Validation Results

### So What Test

**Impact Statement:** If architecture-aware geometric signatures predict model properties:
- Enable efficient model selection within architecture families
- Provide interpretable features (spectral, not black-box embeddings)
- Inform architecture design based on geometric patterns
- Reduce need for expensive learned embeddings

**Significance:** Medium-High — addresses failure modes of learned embedding approaches

### Feasibility Check

| Criterion | Status | Notes |
|-----------|--------|-------|
| Existing datasets | PASS | timm model zoo (150+ pretrained models) |
| Existing benchmarks | PASS | Accuracy prediction correlation/MAE |
| No learned encoder needed | PASS | Direct spectral computation |
| Architecture metadata available | PASS | Model cards provide architecture info |
| No human evaluation | PASS | Automated metric comparison |
| Avoids past failure modes | PASS | No random projections, architecture-aware |

**Overall Feasibility:** APPROVED (failure-informed)

---

## Phase 1 Input Package

<phase1-input>

### research_question
How do architecture-specific geometric signatures (layer-wise effective dimensionality, participation ratio, spectral decay patterns) of pretrained model weights correlate with model performance, and can architecture-aware normalization improve prediction accuracy across diverse model families?

### detailed_question
1. Which geometric metrics (r_eff, PR, d_MLE) show strongest correlation with model accuracy within architecture families?
2. How should geometric signatures be normalized across different architecture capacities (parameter count, depth, width)?
3. Do normalization-type patterns (BatchNorm vs GroupNorm vs LayerNorm) create distinct geometric signature clusters?
4. Can architecture-family-specific predictors outperform universal predictors for model property estimation?
5. What is the minimum model zoo size required for statistically significant within-family predictions?

### reference_papers
1. "Predicting Neural Network Accuracy from Weights" (Unterthiner et al., 2020) - Baseline methodology
2. "Heavy-Tailed Self-Regularization in Deep Neural Networks" (Martin & Mahoney, 2019) - Spectral analysis
3. "Measuring the Intrinsic Dimension of Objective Landscapes" (Li et al., 2018) - Dimensionality estimation
4. "Git Re-Basin: Merging Models Modulo Permutation Symmetries" (Ainsworth et al., 2023) - Weight alignment
5. "Model Soups: Averaging Weights of Multiple Fine-tuned Models" (Wortsman et al., 2022) - Model zoo benchmarks

</phase1-input>

---

## Session Insights

### Key Discoveries

1. Previous attempts failed due to reliance on learned encoders without pretrained checkpoints
2. Contrastive loss creates bounded dimensionality — not intrinsic to weight manifolds
3. Effective dimensionality metrics (r_eff, PR, d_MLE) show large effect sizes — alpha does not
4. Architecture-aware analysis may resolve stability issues (GroupNorm models showed CV=0.0)

### Techniques Used

- Failure record analysis (7 Serena Memory files)
- Root cause extraction and pitfall identification
- Promise-signal preservation (what worked in partial results)
- Constraint-aware question reformulation

### Areas for Further Exploration

1. Per-architecture-family geometric baselines
2. Normalization layer impact on spectral properties
3. Training dynamics reflected in weight geometry
4. Spectral signatures vs learned embeddings tradeoff

---

## Next Steps

1. **Phase 1:** Literature search on spectral weight analysis, architecture-aware model analysis
2. **Phase 2A:** Generate hypotheses about architecture-specific geometric predictors
3. **Phase 2B:** Design within-family vs cross-family prediction experiments
4. Proceed with direct spectral computation (no learned encoder dependencies)

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 Recovery)*
*Learned from: 7 failure/limitation records*
*Ready for: Phase 1 - Targeted Research*

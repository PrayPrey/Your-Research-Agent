# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HierarchicalGenomeFM-v1
**Confidence Level:** 0.75

**Main Hypothesis:**
Under conditions of matched multi-scale genomic data (DNA sequence, gene expression, spatial transcriptomics), if a 3-level hierarchical foundation model with sparse bidirectional cross-scale attention is trained, then cross-scale prediction accuracy will exceed ensemble baselines by 15-25%, because bidirectional information flow enables both bottom-up feature extraction and top-down contextual modulation analogous to visual cortex hierarchical processing.

**Alternative Hypothesis (H0):**
There is no significant difference in cross-scale prediction accuracy between the proposed hierarchical bidirectional model and ensemble baselines that combine separately-trained single-scale models with late fusion; the bidirectional cross-scale attention mechanism provides no additional benefit over simpler multi-modal combination strategies.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Architecture Design | Independent | 3-level hierarchical model: L1 (Mamba/Hyena, 100kb-1Mb), L2 (gene-token Transformer), L3 (ViT for spatial), sparse top-k attention (k=100-1000) | Binary: hierarchical vs. ensemble |
| Training Objective | Independent | Multi-task: seq→expr + expr→spatial + hierarchical contrastive loss | Multi-task vs. single-task |
| Sparsity Parameter (k) | Independent | Top-k attention mechanism between hierarchical levels | k ∈ {100, 250, 500, 1000} |
| Cross-Scale Prediction Accuracy | Dependent | Spearman correlation for cross-scale predictions; downstream classification accuracy | 0.0 - 1.0 (Spearman ρ) |
| Computational Efficiency | Dependent | Training time (GPU-hours), memory (GB), inference latency (ms) | Training: 100-500 GPU-hrs; Memory: 20-80GB |
| Data Source | Controlled | Human Cell Atlas + 10x Genomics matched datasets | Fixed |
| Model Size | Controlled | ~100M parameters total across all levels | Fixed at 100M ± 10% |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: DNA Sequence Features (Level 1)
    ↓ [regulatory encoding]
Step 2: Gene Expression Patterns (Level 2)
    ↓ [cell identity determination]
Step 3: Spatial Organization (Level 3)
    ↓ [hierarchical integration]
Step 4: Unified Cross-Scale Representation
    ↓ [bidirectional refinement]
Outcome: Superior Cross-Scale Prediction Performance
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | HyenaDNA (Nguyen 2023) | SOTA on 12/17 regulatory prediction tasks with 1M context | Strong |
| Step2 → Step3 | HESCAPE Benchmark (2025) | Cross-modal contrastive learning improves gene mutation classification | Medium |
| Step3 → Step4 | DNALongBench (2025) | Long-range dependencies up to 1Mb critical for genomic tasks | Strong |
| Step4 → Outcome | Top-down perceptual inference (Csikor 2025) | Hierarchical inference with bidirectional flow predicts V1/V2 activity | Strong |

**Key Tension:**
- **Tension:** HESCAPE benchmark shows contrastive pretraining improves mutation classification BUT degrades direct gene expression prediction. DNALongBench shows foundation models benefit from long context BUT batch effects interfere with cross-modal alignment.
- **Resolution:** This verification plan tests whether sparse attention with hierarchical structure can overcome batch effects by learning scale-specific representations before cross-scale alignment.

### 1.4 Key Assumptions

1. **Cross-Domain Transfer Validity**
   - *Assumption:* Genomic hierarchy is sufficiently analogous to visual cortex hierarchy for bidirectional attention to provide computational benefits
   - *Consequence if violated:* Revert to bottom-up only architecture

2. **Data Availability**
   - *Assumption:* Human Cell Atlas contains >10,000 matched multi-scale samples
   - *Consequence if violated:* Fall back to semi-supervised approach with fewer matched samples

3. **Sparse Attention Sufficiency**
   - *Assumption:* Sparse top-k attention (k=100-1000) captures most important cross-scale interactions
   - *Consequence if violated:* Increase k or use different sparsity pattern

4. **Semi-Supervised Learning Benefit**
   - *Assumption:* Training on partial multi-scale data improves representation quality
   - *Consequence if violated:* Restrict training to fully matched samples only

### 1.5 Scope & Boundaries

**Applies to:** Human genomic data (cancer, immune, developmental), cross-scale prediction tasks, foundation model pre-training with fine-tuning

**Does NOT apply to:** Non-human species (initially), protein structure, drug response without fine-tuning, real-time inference

**Limitations:** Sparse attention may miss rare interactions; batch effects may interfere; ~100 GPU-hours required

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Cross-Scale Prediction vs. Baselines)**:
Hierarchical model with bidirectional cross-scale attention will achieve cross-scale prediction accuracy (Spearman ρ) exceeding ensemble baselines by 15-25%.

*Measurement*: Spearman ρ for sequence→expression and expression→spatial predictions
*Statistical test*: Paired t-test, n ≥ 25 runs
*Success Criteria*: Cross-scale Spearman ρ > baseline + 0.10 (p < 0.05)
*Falsification*: Cross-scale Spearman ρ ≤ baseline - 0.05 triggers rejection

**Secondary Predictions:**

**P2 (Mechanism Validation)**: Removing top-down attention reduces accuracy by 5-15%

**P3 (Efficiency)**: Sparse attention (k=500) maintains ≥95% performance with 40-60% less training time

**Falsification Criteria:**

1. **Primary Failure**: Cross-scale Spearman ρ ≤ baseline - 0.05
2. **Mechanism Failure**: Removing bidirectional attention shows <3% difference
3. **Efficiency Failure**: Sparse attention drops performance >10%
4. **Scalability Failure**: Model fails to train on Human Cell Atlas scale

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 25 (5 seeds × 5 folds), Cohen's d = 0.8, power = 0.8
**Test**: Paired t-test, α = 0.05 (one-tailed), Bonferroni correction
**Report**: Mean difference, 95% CI, Cohen's d, p-value
**Ablation**: Full model vs. no top-down vs. no sparse vs. no contrastive (ANOVA + Tukey HSD)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does cross-scale prediction benefit from joint hierarchical training compared to separate single-scale models?"
- Maps to: Primary prediction P1
- Verification type: Empirical comparison
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is bidirectional cross-scale attention the mechanism responsible for improved cross-scale prediction?"
- Maps to: Causal mechanism (4 sub-hypotheses: H-M1 to H-M4)
  - H-M1: DNA sequence features → expression patterns
  - H-M2: Expression patterns → spatial organization
  - H-M3: Sparse attention → computational efficiency
  - H-M4: Bidirectional flow → prediction improvement
- Verification type: Ablation studies
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does HierarchicalGenomeFM outperform ensemble and adapter-based baselines on downstream tasks?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-HierarchicalGenomeFM-v1
- [x] Confidence level: 0.75
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized with evidence
- [x] Causal mechanism with N=4 steps and evidence table
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] 3 testable predictions (primary marked)
- [x] 4 falsification criteria defined
- [x] Baselines identified (ensemble, concatenation, adapter)
- [x] SH1, SH2, SH3 starting points clear

### Open Questions

1. **Data Availability:** Verify >10,000 matched multi-scale samples in Human Cell Atlas
2. **Computational Resources:** Confirm 80GB A100s sufficient or plan model parallelism
3. **Batch Effect Mitigation:** Define domain adaptation strategy for cross-dataset alignment
4. **Verification Priority:** Recommend sequential: SH1 → SH2 → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*

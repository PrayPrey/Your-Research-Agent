# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-EcoNiche-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under spatial transcriptomics data with cellular coordinates, if hierarchical multi-scale spatial encoding with learned scale parameters (σ₁, σ₂, σ₃) is applied to a single-cell foundation model, then spatial composition prediction MAE will decrease by >5% and spatial label prediction accuracy will increase by >2% compared to flat single-scale encoding, because multi-scale distance-weighted attention captures cellular microenvironment context at different spatial resolutions—analogous to how ecological niche models capture species-environment relationships across landscape scales.

**Alternative Hypothesis (H0):**
Hierarchical multi-scale spatial encoding provides no significant improvement over flat single-scale encoding; cell identity is determined primarily by intrinsic transcriptomic features rather than multi-scale spatial context.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Number of spatial scales | Independent | 1/2/3-scale hierarchical encoding with learned σ parameters | 1, 2, 3 scales |
| Attention mechanism type | Independent | Fixed k-neighbors vs learned continuous distance-weighted attention | Binary choice |
| Spatial composition prediction MAE | Dependent | Mean Absolute Error on cell type proportion prediction per spot (Nicheformer benchmark) | 0.05-0.20 |
| Spatial label prediction accuracy | Dependent | Accuracy on niche/region label classification (Nicheformer benchmark) | 70-95% |
| Base model architecture | Controlled | Nicheformer transformer backbone held constant | Fixed |
| Training dataset | Controlled | Nicheformer 110M cell dataset (57M dissociated + 53M spatial) | Fixed |
| Training epochs | Controlled | Same number of epochs across all experimental conditions | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Hierarchical Multi-Scale Encoding
        ↓ (Learned σ parameters separate spatial scales)
Step 2: Distinct Spatial Resolution Features
        ↓ (Different scales capture cell→niche→region context)
Step 3: Improved Microenvironment Representation
        ↓ (Richer context embedded for each cell)
Outcome: Better Spatial Prediction Performance
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Urban Flow Inference (Yuan et al., 2024) | Multi-scale contrastive learning improves spatial inference | Strong |
| Step2 → Step3 | GNN-SDM (Wu et al., 2025) | Patch-based aggregation captures emergent properties from neighborhood interactions | Strong |
| Step3 → Outcome | Nicheformer (Schaar et al., 2024) | Spatial pre-training enables outperformance over dissociated-only models on spatial tasks | Strong |

**Key Tension:**
- **Tension:** Nicheformer uses unified representation without explicit scale separation, yet achieves strong results; our hypothesis claims explicit hierarchy is necessary for further improvement
- **Resolution:** Ablation study comparing unified vs explicit hierarchical encoding will empirically determine if additional structural hierarchy provides measurable benefit beyond current approaches

### 1.4 Key Assumptions

1. **Cells operate at distinct spatial scales in tissue microenvironments**
   - Consequence if violated: Learned scale parameters will collapse to single effective scale; ablation study shows no benefit of hierarchy

2. **GNN message passing with distance-weighted attention captures relevant neighborhood interactions**
   - Consequence if violated: Alternative architectures (full Transformers, MLPs) may be needed

3. **Spatial context information can be transferred bidirectionally between spatial and dissociated data**
   - Consequence if violated: Dissociated→spatial prediction will fail; transfer learning approach invalid

4. **The 110M cell Nicheformer dataset is sufficient for learning hierarchical spatial representations**
   - Consequence if violated: May require larger or more diverse spatial transcriptomics datasets

### 1.5 Scope & Boundaries

**Applies to:**
- Spatial transcriptomics data with explicit cellular coordinates (10x Visium, Stereo-seq, MERFISH, Xenium)
- Tissues with clear multi-scale spatial organization (tumors, developing organs, brain regions)

**Does NOT apply to:**
- Bulk RNA-seq (no spatial information)
- Dissociated scRNA-seq without matched spatial reference data

**Known Limitations:**
- 2D spatial context only (no 3D tissue architecture)
- Static snapshot assumption (no temporal dynamics)
- Computational cost ~2x Nicheformer baseline

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Spatial Label Prediction vs SOTA ~80%):**
Our 3-scale hierarchical EcoNiche-Former will achieve spatial label prediction accuracy > 82% (vs Nicheformer baseline ~80%) with p < 0.05.

*Measurement:*
- Accuracy improvement > 2% absolute with paired t-test
- n ≥ 25 independent runs (different random seeds)
- Effect size (Cohen's d) > 0.5

*Success Criteria for Phase 2B:*
- Primary: Accuracy > 82% (p < 0.05)
- Falsification: Accuracy ≤ 78% triggers hypothesis rejection

**Secondary Predictions:**

**P2 (Mechanism Validation - Scale Separation):**
Scale attention weights will show interpretable patterns: different cell types will exhibit statistically different scale preferences (ANOVA p < 0.01 across cell type groups).

**P3 (Transfer Validation - Bidirectional):**
Cross-dataset transfer from spatial to dissociated data: predicted spatial context for scRNA-seq cells will correlate with ground truth (Pearson r > 0.5 on held-out matched spatial-dissociated pairs).

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Spatial label prediction accuracy ≤ 78%
2. **Mechanism Failure:** Scale parameters collapse to single effective scale (σ₁ ≈ σ₂ ≈ σ₃)
3. **Transfer Failure:** No significant correlation in spatial context prediction (r < 0.3)

### 1.7 SOTA Baseline (SOTA Comparison Mode)

| Method | Performance | Year |
|--------|-------------|------|
| Nicheformer | SOTA on spatial composition, label prediction | 2024 |
| scGPT-spatial | Strong on deconvolution, imputation | 2025 |
| scGPT | Baseline (no spatial training) | 2024 |

**Performance Tier:** Medium-High (70-85% accuracy range)

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 25 runs
**Statistical Test:** Paired t-test, α = 0.05 (one-tailed)
**Report Format:** Mean ± Std, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does hierarchical multi-scale spatial encoding produce distinct scale-specific representations in single-cell foundation models?"
- Verification: Analyze learned σ parameters post-training
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is multi-scale spatial attention the causal mechanism behind improved spatial prediction?"
- Decomposes into 3 sub-hypotheses (H-M1, H-M2, H-M3) based on N=3 causal chain
- Verification: Ablation studies

**SH3 (Comparison):**
"Does EcoNiche-Former outperform Nicheformer and other baselines?"
- Verification: Comparative empirical evaluation
- Critical: Determines practical value

**Total Sub-Hypotheses for Phase 2B:** 5

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-EcoNiche-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3)
- [x] Key tension identified with resolution path
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions (3 defined)
- [x] Falsification criteria defined (3 conditions)
- [x] Baselines identified: Nicheformer, scGPT, scVI
- [x] SH1, SH2, SH3 clearly defined

### Open Questions

1. **Compute Resources:** 8-GPU node sufficient for 110M cell training?
2. **Data Access:** Verify Nicheformer dataset public availability
3. **Priority Order:** Validate SH1 on smaller subset before full SH2?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*

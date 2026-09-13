# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ACPMRS-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions where training data can be characterized by data-intrinsic features (n-gram uniqueness, structural repetition, verbatim overlap), if we train a classifier on LoGra attribution scores as memorization labels, then we can predict memorization risk BEFORE training with precision ≥0.80 and recall ≥0.70, because data-intrinsic features correlate with memorization potential as causally validated by mechanistic studies.

**Alternative Hypothesis (H0):**
Data-intrinsic features do not predict memorization risk: the classifier trained on LoGra attribution scores will achieve precision ≤0.60 (no better than random baseline), indicating that memorization is primarily determined by model dynamics rather than data characteristics.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Data-intrinsic features | Independent | N-gram uniqueness score (1-5 grams), structural repetition index (LaTeX/XML pattern frequency), verbatim overlap with known copyrighted databases (Jaccard similarity ≥0.8) | Continuous scores normalized [0,1] per feature |
| Memorization risk score | Dependent | Predicted probability of high LoGra attribution; classification threshold at top 10% of attribution distribution | High (>0.7), Medium (0.3-0.7), Low (<0.3) |
| Model architecture family | Controlled | Llama-family transformer architectures; initial calibration on Llama3-8B | Fixed: Llama3-8B for calibration |
| Dataset domain | Controlled | Text-based training corpora; excludes multimodal data | Fixed: English text, 1B+ tokens |

### 1.3 Causal Mechanism

```
[Data-intrinsic features] → [Feature vector extraction] → [Classifier training on LoGra labels] → [Memorization risk prediction] → [Proactive filtering in curation pipeline]
```

**Causal Chain (N=3 steps):**

1. **Step 1: Feature Extraction** - Compute n-gram uniqueness, structural pattern frequency, verbatim overlap scores
2. **Step 2: Predictor Training** - Supervised classification using LoGra attribution scores as labels
3. **Step 3: Deployment & Filtering** - Apply predictor, attach risk scores as W3C PROV-compliant metadata

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Features → Memorization correlation | Chen et al. 2026 (MDA) | Repetitive structural data causally promotes memorization | Strong |
| LoGra as calibration signal | Choe et al. 2024 (LoGra) | 6,500x throughput improvement; validated on Llama3-8B | Strong |
| Scalability to 70B | Li et al. 2026 (LoRIF) | 20x storage reduction at frontier scale | Strong |

**Key Tension:**
- **Tension:** LoGra measures influence on model outputs (post-hoc), but we use it to predict memorization potential (pre-training).
- **Resolution:** Phase 2B will explicitly test whether high LoGra attribution samples correspond to verbatim reproduction.

### 1.4 Key Assumptions

1. **LoGra-Memorization Correlation:** LoGra attribution scores correlate with actual verbatim memorization.
   - If violated: Predictor will have low precision; false positives will filter valuable training data.

2. **Feature Computability at Scale:** Data-intrinsic features can be computed efficiently at billion-token scale.
   - If violated: Computational cost makes proactive screening impractical.

3. **Cross-Model Generalization:** Memorization patterns learned from Llama3-8B transfer to other model sizes.
   - If violated: Recalibration needed for each model family.

4. **Repetitive Structure as Catalyst:** Repetitive structural data is a primary driver of memorization.
   - If violated: Feature set needs expansion beyond structural patterns.

### 1.5 Scope & Boundaries

**Applies To:** Text-based LLMs, Llama-family architectures, English training corpora, pre-training curation

**Does NOT Apply To:** Multimodal models, non-transformer architectures, fine-tuning data, real-time inference

**Known Limitations:** May miss paraphrased copyrighted content; model-specific calibration may be needed

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Precision Target):**
The AC-PMRS classifier will achieve precision ≥0.80 and recall ≥0.70 in predicting high-memorization-risk samples.

*Measurement:* Bootstrap confidence intervals with n ≥ 1000 samples
*Falsification:* Precision ≤ 0.60 triggers hypothesis rejection

**Secondary Predictions:**

**P2 (Mechanism Validation):**
High structural repetition samples (top quartile) will have ≥2x higher LoGra attribution scores than low repetition samples.

**P3 (Downstream Impact):**
AC-PMRS filtering of top 5% highest-risk samples will reduce DE-COP detection rates by ≥30%.

**Falsification Criteria:**

1. **Primary Failure:** Precision ≤ 0.60
2. **Mechanism Failure:** No significant correlation between structural features and LoGra attribution (p > 0.10)
3. **Downstream Failure:** DE-COP detection rate unchanged after filtering

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 100 samples per class (high/low risk)
**Statistical Test:** Bootstrap confidence intervals (1000 iterations), 5-fold stratified CV
**Significance Level:** α = 0.05
**Report Format:** Mean ± Std Dev, 95% CI, ROC-AUC, feature importance

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Do data-intrinsic features significantly correlate with LoGra attribution scores in the Llama3-8B calibration dataset?"
- Verification type: Correlation analysis
- Critical: MUST PASS for hypothesis to proceed

**SH2 (Mechanism):**
"Is the proposed 3-step causal mechanism the actual path from data features to copyright risk reduction?"
- Sub-hypotheses (N=3):
  - H-M1: Feature extraction captures memorization-relevant patterns
  - H-M2: Classifier achieves target precision/recall on LoGra labels
  - H-M3: Deployment filtering reduces DE-COP detection rates
- Verification type: Causal analysis with ablation studies

**SH3 (Comparison):**
"Does AC-PMRS outperform simple n-gram matching baseline in precision while maintaining comparable recall?"
- Verification type: Comparative empirical

**Total sub-hypotheses in Phase 2B:** 5 (SH1 + H-M1 + H-M2 + H-M3 + SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-ACPMRS-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist with primary marked
- [x] Falsification criteria are defined
- [x] Baselines identified: DE-COP (reactive), n-gram matching (simple)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data Availability:** Is the LoGra calibration dataset publicly available, or regeneration via LogIX needed?
2. **Computational Resources:** Estimated 1-2 GPU-days for feature extraction + classification
3. **Priority Order:** SH1 (correlation) → H-M2 (classifier) → H-M3 (downstream impact)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*

---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Spurious Correlations — Reflection 4 (Post H-E"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-05
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Spurious correlations and shortcut learning in deep learning — Reflection 4 recovery after h-e1 MUST_WORK_FAIL, h-m2 SHOULD_WORK limitation, and Reflection 3 pivot to last-layer gradient + CLIP/DINO clustering. This reflection pivots to activation-space probing: linear probes on intermediate ResNet-50 feature maps to measure spurious vs core feature separability across robustification methods (ERM/GroupDRO/DFR/SAM).

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Continuing ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning pipeline. Full failure history: (1) h-e1 MUST_WORK_FAIL — full-model gradient cosine similarity (D≈25M) too noisy at N=100, Cohen's d=-0.330 vs threshold >0.8; (2) h-m2 SHOULD_WORK limitation — head-only Hessian λ_max shows DFR > ERM (opposite direction) due to sklearn LogisticRegression C=0.1 geometry, not spurious feature alignment; (3) Reflection 3 proposed last-layer gradient (D=2048, N≥500) + CLIP/DINO zero-shot clustering — not yet validated (this is the next iteration). Reflection 4 provides an orthogonal track: activation-space linear probing on existing WILDS Waterbirds data with known group annotations.

Source Type: Pipeline Reflection Recovery / ROUTE_TO_0 (input marked dummy — continuing from prior domain)

---

## Lessons from Previous Attempts

### What Was Tried Before

**h-e1 (Reflection 1, MUST_WORK_FAIL):** Full-model gradient cosine similarity (D≈25M) between background-stratified Waterbirds batches (N=100 per stratum, 10-epoch PoC checkpoints, 3 seeds × 4 methods). Cohen's d (ERM vs DFR) = -0.330, threshold >0.8. Root cause: gradient dimensionality too large, sample size too small, checkpoints not fully trained.

**h-m2 (Reflection 2, SHOULD_WORK limitation):** Head-only Hessian λ_max on model.fc (D=4098). Expected DFR < ERM. Actual: DFR λ_max = 211.78 > ERM λ_max = 4.90. Root cause: sklearn LogisticRegression C=0.1 creates high-norm weights independent of spurious feature alignment; backbone dominates full-model curvature.

**Reflection 3:** Proposed last-layer gradient cosine similarity (D=2048, N≥500, fully-trained izmailovpavel/spurious_feature_learning checkpoints) + CLIP/DINO annotation-free clustering (NMI ≥ 0.3). Not yet executed — this reflection is running in parallel as a fresh attempt.

### Why Previous Directions Failed

1. Gradient-space metrics (full-model or last-layer) require careful calibration: N, D, checkpoint training depth, and seed count all interact to create high CV
2. Hessian metrics are confounded by optimizer geometry (SGD vs sklearn LR produce structurally different weight distributions regardless of spurious features)
3. Both gradient and Hessian approaches are sensitive to implementation choices (batch size, layer selection, regularization) that mask the phenomenon of interest

### How This New Direction Avoids Those Pitfalls

1. **No gradients, no Hessians** — activation-space probing is purely forward-pass; no backward pass, no optimizer geometry confound
2. **Linear probe on existing feature maps** — sklearn LogisticRegression on frozen ResNet-50 layer4 features (D=2048 spatial features, not gradients) trained to predict spurious attribute (background: land vs water) from existing WILDS group_array annotations
3. **Metric is linear probe accuracy** — bounded [0,1], numerically stable, directly interpretable as "how much does this representation encode background?"
4. **Uses existing author-released checkpoints** (izmailovpavel/spurious_feature_learning) — fully trained, no 10-epoch PoC issue
5. **No new benchmarks** — Waterbirds WILDS group_array provides ground-truth spurious attribute labels; sklearn accuracy_score is existing benchmark

---

## Session Plan

ROUTE_TO_0 Mode — Auto-extracted from failure history. Single track:
- Linear probe accuracy for spurious attribute (background: land vs water) on frozen layer4 features (D=2048) from author-released ERM/GroupDRO/DFR/SAM ResNet-50 checkpoints; compare probe accuracy reduction across methods as measure of "spurious feature unlearning"

---

## Technique Sessions

ROUTE_TO_0 Mode — No interactive sessions. Failure analysis applied directly to question refinement.

---

## Research Question Development

### Initial Question

Do robustification methods (GroupDRO, DFR, SAM) reduce linear probe accuracy for spurious background attributes on Waterbirds layer4 features compared to ERM, measured on fully-trained author-released ResNet-50 checkpoints?

### Refined Question

Across fully-trained ResNet-50 checkpoints (izmailovpavel/spurious_feature_learning, 3 seeds × 4 methods = 12 checkpoints), does linear probe accuracy for the spurious background attribute (land vs water, Waterbirds WILDS group_array) on frozen layer4 features (D=2048) decrease monotonically from ERM → SAM → GroupDRO → DFR, and does this spurious probe accuracy correlate negatively with worst-group accuracy (WGA) across methods (Pearson r < -0.5, p < 0.05)?

### Detailed Sub-Questions

1. Does DFR reduce layer4 linear probe accuracy for spurious background attribute below ERM (paired t-test across 3 seeds, one-sided p < 0.05), confirming that DFR's head retraining suppresses spurious feature encoding in the backbone representation?
2. Is the ranking of spurious probe accuracy (ERM > SAM > GroupDRO > DFR) consistent with the expected robustification strength ordering across all 3 seeds?
3. Does spurious probe accuracy correlate negatively with WGA across the 12 checkpoints (3 seeds × 4 methods) with Pearson r < -0.5 and p < 0.05 (one-sided)?
4. What is the effect size (Cohen's d) for ERM vs DFR difference in layer4 spurious probe accuracy, and does it exceed 0.8 (the gate that h-e1 failed to achieve with gradient cosine similarity)?
5. Does the same linear probe pattern hold for core attribute (bird species: landbird vs waterbird), and is core probe accuracy preserved or increased by robustification methods (expected: core accuracy maintained ≥ ERM baseline)?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

ICLR 2025 Workshop significance pre-validated. Activation-space linear probing is a direct, mechanistically interpretable measure of "does this model's representation encode the spurious attribute?" — contrasting with gradient-space (h-e1) and Hessian-space (h-m2) approaches that failed due to noise and optimizer confounds. If DFR suppresses spurious feature encoding in layer4 while maintaining core feature encoding, this confirms the mechanism: DFR's head retraining changes what the backbone encodes, not just the head geometry. Real-world implications: linear probe auditing as a cheap, gradient-free tool for diagnosing spurious feature reliance in deployed models.

### Feasibility Check

All sub-questions testable immediately using existing data and models:
- Checkpoints: izmailovpavel/spurious_feature_learning on HuggingFace (ERM, GroupDRO, DFR, SAM, ResNet-50, 3 seeds each)
- Data: Waterbirds WILDS at /home/PrayPrey/.wilds_cache/waterbirds_v1.0; group_array provides spurious attribute (background) and core attribute (bird species) labels without any new annotation
- Feature extraction: Forward pass through ResNet-50 up to layer4, global average pooling → D=2048 vector; no backward pass required
- Probe: sklearn LogisticRegression (or linear SVM) on train split, evaluated on test split; accuracy_score is standard metric
- Statistics: scipy.stats.pearsonr for correlation, scipy.stats.ttest_rel for paired t-test, Cohen's d from pooled std
- No new benchmarks, no synthetic data, no human evaluation rubrics. Mandatory feasibility constraints satisfied.
- Avoids: full-model gradient (h-e1 failure), head-only Hessian (h-m2 failure), last-layer gradients (Reflection 3 — separate track)

---

## Phase 1 Input Package

<phase1-input>

### research_question
Do robustification methods (GroupDRO, DFR, SAM) reduce linear probe accuracy for spurious background attributes on frozen ResNet-50 layer4 features (Waterbirds WILDS) compared to ERM, using fully-trained author-released checkpoints — and does this spurious probe accuracy correlate negatively with worst-group accuracy (WGA) across methods?

### detailed_question
1. Does DFR reduce layer4 linear probe accuracy for spurious background attribute (land vs water, WILDS group_array) below ERM (paired t-test, one-sided p < 0.05, 3 seeds), confirming spurious feature suppression in backbone representations?
2. Is the spurious probe accuracy ranking (ERM > SAM > GroupDRO > DFR) consistent across all 3 seeds?
3. Does spurious probe accuracy correlate negatively with WGA across 12 checkpoints (Pearson r < -0.5, p < 0.05 one-sided)?
4. Does Cohen's d for ERM vs DFR in layer4 spurious probe accuracy exceed 0.8 (the gate h-e1 failed to achieve with gradient cosine similarity)?
5. Is core attribute (bird species) probe accuracy preserved or increased by robustification methods (core accuracy ≥ ERM baseline across all methods)?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

ROUTE_TO_0 Reflection 4 recovery. Three critical lessons applied: (1) h-e1 FAIL → avoid gradient-based metrics entirely (noisy, checkpoint-sensitive); (2) h-m2 limitation → avoid Hessian metrics (optimizer geometry confound); (3) Reflection 3 covers gradient/CLIP track — this reflection provides an orthogonal activation-space track. New hypothesis: layer4 linear probe accuracy is a stable, numerically bounded, gradient-free measure of spurious feature encoding that can differentiate robustification methods with sufficient statistical power at n=3 seeds.

### Techniques Used

ROUTE_TO_0 Mode (failure analysis + structured input extraction). Lessons from: failure_h-e1_run1 (MUST_WORK_FAIL gradient noise), limitation_h-m2 (SHOULD_WORK Hessian reversal), Reflection 3 brainstorm (gradient/CLIP pivot).

### Areas for Further Exploration

- Layer-wise probe accuracy across backbone (layer1–layer4) to map where spurious features are encoded and suppressed
- CelebA, MultiNLI, CivilComments probing with CLIP/BERT features (future extension, data exists)
- Probing for multiple spurious attributes simultaneously in multi-attribute datasets
- Theoretical connection between probe accuracy and model flatness (linking h-m2 insights)
- Annotation-free spurious probing using CLIP zero-shot labels as proxy for group_array

---

## Next Steps

Proceed to Phase 1 - Targeted Research. Focus on: (1) linear probing literature for spurious feature detection in vision models, (2) izmailovpavel/spurious_feature_learning checkpoint availability and feature extraction protocols, (3) Waterbirds WILDS group_array structure for spurious/core attribute labels. Avoid: full-model gradient cosine similarity (h-e1 failure), head-only Hessian (h-m2 failure), last-layer gradient cosine similarity (covered by Reflection 3 track).

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*

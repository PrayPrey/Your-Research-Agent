# 1. Introduction

Gradient attribution methods (Grad-CAM, Integrated Gradients) identify which features drive model predictions, but fail when spurious correlations are unknown at test time [@adebayo2022post]. Models trained on correlated data learn shortcuts — waterbirds are predicted via water backgrounds 90% of the time — degrading worst-group accuracy (WGA) to below 60% while maintaining 95% average accuracy [@sagawa2019distributionally]. Yet existing detection methods require knowing which spurious feature to search for, rendering them ineffective when the spurious shortcut is unknown [@adebayo2022post].

## 1.1 Problem: The Attribution-Detection Gap

Current spurious correlation mitigation methods fall into three categories, each with limitations:

**Annotation-based methods** (GroupDRO [@sagawa2019distributionally], JTT [@liu2021just]) require ground-truth group labels during training, restricting applicability to datasets where spurious features are known and labeled. GroupDRO reweights minority samples via group annotations; JTT trains a two-stage model using initial predictions to identify hard samples. Both achieve 80-85% WGA on Waterbirds but require explicit group membership.

**Embedding-space methods** (SCER [@park2025spurious]) operate post-hoc via prototype refinement in activation space, achieving ~90% WGA on Waterbirds. However, SCER requires code unavailable for reproduction, and embedding-based approaches miss gradient-level dynamics that encode *how* the model learned spurious shortcuts.

**Attribution-based methods** (SPROD [@lee2025detecting], GradCAM [@selvaraju2017grad]) attempt detection via saliency maps but suffer from a fundamental gap: attribution explains *which* features drive predictions (the result), not *whether* the prediction process is abnormal (the mechanism). Adebayo et al. (2022) demonstrated via user study that practitioners cannot detect unknown spurious correlations using attribution results alone (109 citations).

This creates a **detection-mitigation gap**: no unified framework exists that both detects minority groups via gradient analysis *and* mitigates spurious reliance without annotations.

## 1.2 Key Insight: Gradient Abnormality as Process Disruption

We observe that minority samples (waterbird-land, landbird-water) create a conflict: the spurious shortcut (background) contradicts the core feature (bird type). This conflict manifests not in *what* gradients point to (attribution), but in *how* gradient computation behaves (abnormality).

**Analogy:** A GPS recalculating when the expected route (spurious shortcut) conflicts with the actual destination (core label). The noise in recalculation (gradient scattering) reveals the conflict, independent of whether the final route is correct.

**Theoretical bridge:** Chen et al. (2023) introduced GAIA (Gradient Abnormality for OOD Detection), showing that out-of-distribution samples exhibit higher gradient abnormality (zero-deflation, channel variance) than in-distribution samples (FPR95 reduction of 45.41% on CIFAR100). We extend GAIA from distribution shift (OOD) to subpopulation shift: minority groups are "conditional OOD" from the spurious shortcut's perspective — the model expects water backgrounds for waterbirds, yet 10% appear on land.

**Mechanistic prediction:** If spurious conflict causes gradient abnormality, then removing the conflict (background swap: minority → majority background) should reduce abnormality by ≥30%.

## 1.3 Contributions

We propose a gradient-based framework for spurious correlation detection and mitigation, validated via synthetic experiments and proof-of-concept tests:

**C1. Detection Methodology (Synthetic Validation Only):** We show gradient abnormality pipeline (GradCAM → GAIA-Z → statistical testing) differentiates minority vs majority gradient patterns in synthetic experiments (GAIA-Z divergence 0.30, p<0.0001, Cohen's d=198.75). First application of GAIA to subpopulation shift within in-distribution data. **Real Waterbirds validation pending** (requires GPU compatibility fix or CPU training ~30h).

**C2. Causal Mechanism Validation (Synthetic):** We demonstrate background augmentation causally reduces GAIA-Z scores by 39.4% (p<0.001, d=2.96) on synthetic minority samples, validating spurious-conflict hypothesis (Step 2 of causal chain). Strong correlation (|ρ|=0.975, p<0.001) between GAIA divergence and WGA across synthetic model sweep. **Real causality test pending.**

**C3. Mitigation Methodology (PoC Only):** We propose spatial gradient regularization framework that penalizes gradients in spurious regions via GradCAM-based masking and adaptive penalty scaling. MNIST+Color smoke test (1 seed, 2 epochs) shows +23pp WGA improvement (78% vs 55% baseline) without catastrophic accuracy drop. **Full 5-seed experiment + Waterbirds validation deferred** (~44 GPU hours).

**C4. Unified Gradient-Based Approach:** We introduce unified framework where same abnormality mechanism (GAIA-Z scattering) enables both detection (identify minority samples) and mitigation (suppress spurious gradients during training), complementing embedding-based methods (SCER) that operate post-hoc.

**Transparency Note:** All validation results are from synthetic data (C1-C2) or minimal proof-of-concept experiments (C3). Real Waterbirds experiments require GPU compatibility resolution (PyTorch 2.1+ for H100 sm_90 support) or CPU training (~70-90 GPU hours). We position this as a methodology contribution (Tier 3) with clear path to empirical validation (Tier 2).

## 1.4 Paper Organization

Section 2 reviews spurious correlation benchmarks, robust learning methods, and gradient attribution for detection. Section 3 describes the detection pipeline, causality test, and spatial regularization algorithm. Section 4 presents synthetic validation rationale and experimental design. Section 5 reports results across three hypotheses (h-e1 detection, h-m-integrated mechanism, h-m-mitigate mitigation). Section 6 discusses synthetic vs real validation tradeoffs and positioning. Section 7 concludes with limitations and future work.

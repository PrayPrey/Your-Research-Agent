# Hypothesis H-E1 Context

**Generated:** 2026-07-13
**Source:** Phase 2B Verification Plan

---

## Hypothesis Specification

**ID:** H-E1
**Title:** Operation-Specific Weight Signal Existence
**Type:** EXISTENCE

**Statement:** Under ImageNet-trained model zoos (ResNet-50 vs ViT-Base), if operation-specific weight signals exist beyond tensor dimensions, then a binary classifier trained on operation-agnostic statistics (layer norms, spectral norms) will achieve ≥80% accuracy distinguishing ResNet from ViT.

**Rationale:** This hypothesis validates Assumption A1, which is foundational for CAPE's modular encoder design. If operation-specific signals don't exist, modular encoders reduce to SNE's set-encoding baseline (no improvement). Prof. Rex identified this as critical pre-validation requirement.

---

## Variables

- **IV:** Architecture Type (Binary: ResNet vs ViT)
- **DV:** Binary Classifier Accuracy (on operation-agnostic statistics)
- **CV:** Model zoo size (50 per architecture), ImageNet-trained, same statistical features

---

## Success Criteria

- **Primary:** Binary classifier test accuracy ≥80% (signal exists)
- **Secondary:** Norms+spectral accuracy > norms-only by ≥5% (spectral norms encode architectural information)
- **Statistical:** p < 0.05 vs random baseline (50% via permutation test)

---

## Gate Conditions

- **Type:** MUST_WORK
- **If Fail (<70% accuracy):** ABANDON modular encoder approach, fall back to SNE set-encoding baseline
- **If Partial (70-80%):** EXPLORE enhanced statistics (Fisher eigenspectrum, NTK trace)

---

## Prerequisites

None (foundational test)

---

## Experimental Setup

**Dataset:** HuggingFace Model Hub - ImageNet Vision Models
- Source: HuggingFace (huggingface.co/models), filtered for ImageNet-1K
- Path: 100 models (50 ResNet-50, 50 ViT-Base)

**Approach:**
1. Extract operation-agnostic statistics (layer-wise L2 norms, top-5 spectral norms, mean/std) from 100 models
2. Train logistic regression classifier on 70 models (35 per architecture, stratified by accuracy quantiles)
3. Test on held-out 30 models, measure test accuracy
4. Ablation: compare norms-only vs norms+spectral to identify signal source
5. If accuracy ≥80%, signal exists; if <70%, signal insufficient for modular encoding

---

## Baseline & Established Facts

**Builds On:**
- SANE same-family transfer (+2.2%), which proves architecture-specific signals exist within families
- H-E1 extends this to cross-family (ResNet vs ViT) via binary discrimination test

**Target Performance:** Binary classifier ≥80% accuracy (distinguishing ResNet from ViT)

---

## Dependencies

- **Prerequisite Hypotheses:** None
- **Blocks If Failed:** H-M-Integrated (Full CAPE mechanism cannot proceed without signal existence validation)

---

## Timeline

**Duration:** 2-3 days
**Tasks:** Dataset collection, binary classifier training, validation

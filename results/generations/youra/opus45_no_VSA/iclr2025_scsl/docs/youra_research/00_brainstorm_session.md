---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: SGD Dynamics in Spurious Correlation Learning"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-09
**Facilitator:** Research Question Architect
**Participant:** Anonymous
**Mode:** UNATTENDED (Auto-fill from ICLR 2025 SCSL Workshop CFP)

---

## Executive Summary

**Initial Interest:** Understanding the foundations of spurious correlations and shortcut learning in deep neural networks, specifically how optimization dynamics (SGD) cause models to learn spurious features before core features.

**Session Approach:** Auto-fill extraction from ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning CFP

**Session Duration:** ~5 minutes (UNATTENDED mode)

---

## Starting Context

**Source Material:** ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning: Foundations and Solutions

**Key Workshop Themes:**
1. Benchmarks for spurious correlation evaluation across modalities
2. Robustification methods for various learning paradigms
3. Foundations: mathematical formulations, SGD role, loss landscape effects

**Feasibility Constraints Applied:**
- No new benchmarks (use existing: Waterbirds, CelebA, ColorMNIST)
- No synthetic data generation
- No human evaluation required
- Must use existing real datasets

---

## Lessons from Previous Attempts

N/A - First attempt

---

## Session Plan

**Approach:** Extract feasibility-compliant research direction from workshop topics, focusing on "Foundations" track which allows theoretical/empirical investigation using existing benchmarks.

**Selected Focus Area:** "Studying the role of widely used gradient-descent-based optimization methods in reliance on shortcuts"

---

## Technique Sessions

**Auto-Fill Analysis:**

1. **Workshop Topic Filtering:** Eliminated topics requiring new benchmarks or human evaluation
2. **Feasibility Mapping:** Identified "Foundations" track as most compatible with constraints
3. **Research Gap Identification:** Time dynamics of spurious vs core feature learning during SGD training
4. **Existing Resource Verification:** Waterbirds, CelebA, ColorMNIST publicly available with group labels

---

## Research Question Development

### Initial Question

How do gradient-descent-based optimization dynamics cause deep neural networks to preferentially learn spurious correlations over core features?

### Refined Question

**What is the temporal relationship between spurious feature learning and core feature learning during SGD training, and can we identify critical training phases where intervention would most effectively redirect learning toward core features?**

### Detailed Sub-Questions

1. At what training epoch/iteration do spurious features become linearly separable in intermediate representations, relative to core features?
2. How does the learning rate schedule affect the temporal gap between spurious and core feature acquisition?
3. Do spurious features exhibit characteristic loss landscape signatures (gradient magnitude, Hessian eigenvalues) that distinguish them from core features during early training?
4. Can early stopping or learning rate interventions at identified critical phases improve worst-group accuracy without sacrificing average accuracy?
5. How do these dynamics differ across benchmark datasets with varying spurious correlation strengths (95% vs 99%)?

---

## Reference Papers

**Foundational:**
1. Sagawa et al. (2020) - "Distributionally Robust Neural Networks" - Introduces Waterbirds/CelebA benchmarks, worst-group accuracy metric
2. Shah et al. (2020) - "The Pitfalls of Simplicity Bias in Neural Networks" - Simplicity bias framework
3. Hermann & Lampinen (2020) - "What shapes feature representations?" - Feature learning dynamics

**Optimization Dynamics:**
4. Arpit et al. (2017) - "A Closer Look at Memorization in Deep Networks" - Learning dynamics, easy vs hard examples
5. Frankle et al. (2020) - "Early-Bird Tickets" - Critical learning phases in early training
6. Fort et al. (2020) - "Deep learning versus kernel learning" - Feature learning timeline

**Spurious Correlation Specific:**
7. Liu et al. (2021) - "Just Train Twice" - Two-stage training for spurious correlations
8. Idrissi et al. (2022) - "Simple Data Balancing" - Analysis of when spurious features are learned
9. Kirichenko et al. (2023) - "Last Layer Re-Training" - Evidence that core features exist but are suppressed

---

## Validation Results

### So What Test

**Impact if confirmed:** Understanding precisely when and how spurious features are learned enables:
- Targeted interventions during training (not post-hoc corrections)
- More efficient robustification (intervene at critical phase only)
- Theoretical framework for predicting shortcut vulnerability

**Who cares:** Practitioners deploying models in high-stakes domains (medical, legal); researchers developing robust training methods; foundation model developers concerned about spurious behaviors.

**Novelty:** While simplicity bias is known, the precise temporal dynamics and intervention opportunities during training are underexplored.

### Feasibility Check

| Criterion | Status | Notes |
|-----------|--------|-------|
| Existing benchmarks | PASS | Waterbirds, CelebA, ColorMNIST available |
| No new benchmark creation | PASS | Using standard worst-group accuracy |
| No synthetic data | PASS | All datasets are real images |
| No human evaluation | PASS | Automated metrics only |
| Computational tractability | PASS | Standard ResNet training, probing classifiers |
| Measurable outcomes | PASS | Epoch of linear separability, loss landscape metrics |

**Feasibility Verdict:** APPROVED

---

## Phase 1 Input Package

<phase1-input>

### research_question
What is the temporal relationship between spurious feature learning and core feature learning during SGD training, and can we identify critical training phases where intervention would most effectively redirect learning toward core features?

### detailed_question
1. At what training epoch/iteration do spurious features become linearly separable in intermediate representations, relative to core features?
2. How does the learning rate schedule affect the temporal gap between spurious and core feature acquisition?
3. Do spurious features exhibit characteristic loss landscape signatures (gradient magnitude, Hessian eigenvalues) that distinguish them from core features during early training?
4. Can early stopping or learning rate interventions at identified critical phases improve worst-group accuracy without sacrificing average accuracy?
5. How do these dynamics differ across benchmark datasets with varying spurious correlation strengths (95% vs 99%)?

### reference_papers
1. Sagawa et al. (2020) - Distributionally Robust Neural Networks - Waterbirds/CelebA benchmarks
2. Shah et al. (2020) - The Pitfalls of Simplicity Bias in Neural Networks
3. Arpit et al. (2017) - A Closer Look at Memorization in Deep Networks
4. Kirichenko et al. (2023) - Last Layer Re-Training - Evidence core features exist but suppressed
5. Liu et al. (2021) - Just Train Twice - Two-stage training dynamics

</phase1-input>

---

## Session Insights

### Key Discoveries

1. Workshop explicitly calls for "studying the role of gradient-descent-based optimization methods" - direct alignment
2. Existing benchmarks have group labels enabling spurious vs core feature analysis
3. Recent work (Kirichenko 2023) shows core features ARE learned but suppressed - suggests temporal investigation valuable
4. Loss landscape analysis tools exist (PyHessian) for feasible implementation

### Techniques Used

- Auto-fill extraction from workshop CFP
- Feasibility constraint filtering
- Gap analysis between workshop goals and existing literature

### Areas for Further Exploration

1. Extension to foundation models (if compute available)
2. Comparison across architectures (ResNet vs ViT)
3. Connection to neural tangent kernel regime vs feature learning regime

---

## Next Steps

1. **Phase 1:** Systematic literature search on SGD dynamics + spurious correlation
2. **Phase 2A:** Generate testable hypotheses about temporal learning dynamics
3. **Phase 2B:** Design probing experiments with existing benchmarks

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Mode: UNATTENDED (batch-mode)*
*Ready for: Phase 1 - Targeted Research*

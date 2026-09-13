---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Spurious Correlations and Shortcut Learning"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-21
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Robustification methods for deep learning models against spurious correlations and shortcut learning, specifically in under-explored learning paradigms and optimization-level mechanisms

**Session Approach:** Auto-Fill Mode (Structured Input Detected)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Despite remarkable advancements in AI, spurious correlations and shortcut learning persistently hinder robustness and reliability of machine learning systems. Models rely on spurious patterns rather than causal relationships, making them vulnerable in real-world scenarios with under-represented groups or minority populations. The statistical nature of ML algorithms and their inductive biases at all stages (data preprocessing, architectures, optimization) drive this phenomenon. Source Type: Workshop CFP (ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning: Foundations and Solutions)

---

## Lessons from Previous Attempts

N/A - First attempt

---

## Session Plan

Auto-extracted from structured input (ICLR 2025 Workshop CFP). Feasibility constraints applied: no new benchmarks, no synthetic data, no human evaluation, existing real datasets and benchmarks only.

---

## Technique Sessions

Auto-Fill Mode - No interactive sessions. Components extracted directly from structured workshop CFP input with feasibility filtering.

---

## Research Question Development

### Initial Question

How can deep learning models be made more robust to spurious correlations and shortcut features without requiring group annotations or knowledge of which features are spurious, particularly in optimization and self-supervised learning paradigms?

### Refined Question

Can optimization-level interventions (e.g., gradient surgery, sharpness-aware minimization, or loss landscape regularization) reduce reliance on shortcut features in self-supervised and contrastive learning settings on existing benchmark datasets, without requiring group labels or knowledge of spurious feature identity?

### Detailed Sub-Questions

1. Do standard self-supervised learning objectives (e.g., SimCLR, MoCo, DINO) exhibit differential shortcut reliance compared to supervised learning on the same existing datasets (Waterbirds, CelebA, CMNIST, UrbanCars)?

2. Does the time dynamics of learning (core vs. spurious feature acquisition order) differ between supervised and self-supervised training regimes on existing spurious correlation benchmarks?

3. Can sharpness-aware minimization (SAM) or related geometry-aware optimizers reduce shortcut reliance in self-supervised pre-training without access to group annotations, as measured on existing worst-group-accuracy benchmarks?

4. Is there a detectable signature in the loss landscape (flatness, curvature around spurious vs. core feature directions) that predicts the degree of shortcut reliance, measurable on existing trained models and datasets?

5. Can training-time interventions targeting gradient alignment between augmented views in contrastive learning mitigate shortcut adoption, verifiable on Waterbirds, CelebA, and CMNIST without new annotations?

---

## Reference Papers

Not provided - will discover in Phase 1

Key search targets for Phase 1:
- Shortcut learning in self-supervised/contrastive learning (SimCLR, MoCo, DINO + spurious correlations)
- SAM (Sharpness-Aware Minimization) and robustness to spurious features
- Loss landscape geometry and shortcut features
- Worst-group accuracy on Waterbirds, CelebA, CMNIST, UrbanCars benchmarks
- Group DRO, JTT, DFR, GEORGE (annotation-free robustification baselines)
- Time dynamics of spurious vs. core feature learning in DNNs

---

## Validation Results

### So What Test

Input from established research venue (ICLR 2025 Workshop) — significance pre-validated. The refined question addresses a critical gap: most robustification methods assume supervised learning + group annotations, but self-supervised pre-training is increasingly dominant. If shortcut reliance differs in SSL and can be addressed at the optimization level without annotations, this directly enables safer deployment of foundation models. Impact is high: SSL pre-training is used in medical imaging, NLP, computer vision — all domains where spurious correlations cause harm.

### Feasibility Check

All constraints satisfied:
- ✅ No new benchmarks required — uses Waterbirds, CelebA, CMNIST, UrbanCars (existing)
- ✅ No synthetic/generated data — all datasets are real and publicly available
- ✅ No human evaluation or annotation — worst-group accuracy is automated
- ✅ Testable immediately — SAM variants, SimCLR/MoCo/DINO are available implementations
- ✅ Clear baselines exist — Group DRO, JTT, DFR provide comparison points

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can optimization-level interventions (e.g., sharpness-aware minimization, gradient surgery, or loss landscape regularization) reduce reliance on shortcut features in self-supervised and contrastive learning settings on existing spurious correlation benchmarks, without requiring group labels or knowledge of spurious feature identity?

### detailed_question
1. Do standard self-supervised learning objectives (SimCLR, MoCo, DINO) exhibit differential shortcut reliance compared to supervised learning on Waterbirds, CelebA, CMNIST, and UrbanCars?
2. Does the temporal order of learning (core vs. spurious feature acquisition) differ between supervised and self-supervised training regimes on existing benchmarks?
3. Can SAM or related geometry-aware optimizers reduce shortcut reliance in self-supervised pre-training without group annotations, measured by worst-group accuracy on existing benchmarks?
4. Is there a detectable loss landscape signature (flatness/curvature) that predicts shortcut reliance degree, measurable on existing trained models?
5. Can gradient alignment interventions in contrastive learning (between augmented views) mitigate shortcut adoption on Waterbirds, CelebA, CMNIST without new annotations?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- The ICLR 2025 SCSL workshop highlights a critical gap: robustification methods beyond supervised learning are under-explored
- Optimization-level interventions (SAM, gradient geometry) are explicitly flagged as under-examined by the workshop
- The annotation-free setting (unknown spurious features) is the hardest and most impactful subproblem
- Self-supervised/contrastive learning paradigms are the fastest-growing area where this gap causes real harm
- Existing benchmarks (Waterbirds, CelebA, CMNIST, UrbanCars) are sufficient to test all sub-questions

### Techniques Used

Auto-Fill Mode (structured input extraction) with feasibility constraint filtering

### Areas for Further Exploration

- Reinforcement learning and spurious correlations (excluded: likely requires new environments)
- LLM/LMM robustification to spurious correlations (potential follow-up, larger compute)
- Mathematical formulations of loss landscape geometry and shortcut features
- Causal representation learning algorithms as alternative robustification approach
- Spurious correlations in graph neural networks and time series (different modality)

---

## Next Steps

Proceed to Phase 1 - Targeted Research

Key Phase 1 search targets:
1. SSL (SimCLR/MoCo/DINO) + shortcut learning / spurious correlations
2. SAM + worst-group accuracy / spurious features / robustness
3. Loss landscape geometry + shortcut features / simplicity bias
4. Annotation-free robustification methods (JTT, DFR, GEORGE, EIIL)
5. Temporal learning dynamics (core vs. spurious features, early stopping effects)

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*

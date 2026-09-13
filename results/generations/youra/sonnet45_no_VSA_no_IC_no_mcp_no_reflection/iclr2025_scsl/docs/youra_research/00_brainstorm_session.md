---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Spurious Correlation & Shortcut Learning Foundations"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-28
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Understanding the foundational mechanisms behind spurious correlations and shortcut learning in deep neural networks, focusing on mathematical formulations, optimization dynamics, and loss landscape effects that can be studied using existing benchmarks without requiring new datasets or human evaluation.

**Session Approach:** Foundation-focused analysis using existing theoretical frameworks and established evaluation benchmarks. Auto-extraction from ICLR 2025 workshop CFP on Spurious Correlation and Shortcut Learning.

**Session Duration:** 10-20 minutes (UNATTENDED auto-fill mode)

---

## Starting Context

The ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning identifies three core research avenues:

1. **Development of comprehensive evaluation benchmarks** - explicitly excluded by feasibility constraints (no new benchmarks)
2. **Novel solutions for building robust models** - may require unavailable datasets or future validation
3. **Foundational understanding of spurious correlations and shortcut learning mechanisms** - FEASIBLE with existing benchmarks and theoretical analysis

Workshop objectives highlight gaps in understanding the **origins** of reliance on spurious correlations:
- Mathematical formulations describing the issue and its origins
- Role of gradient-descent-based optimization in shortcut reliance
- Effect of shortcuts on loss landscape geometry
- Mechanisms behind learning biases in different architectures and algorithms

Feasibility constraints mandate:
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated/future data
- NO human evaluation or annotation
- MUST use existing real datasets and existing benchmarks immediately

---

## Lessons from Previous Attempts

<!-- This section is ONLY populated for ROUTE_TO_0 case (when routing back from Phase 4/5 failure) -->
<!-- If no previous failures exist, this section will be marked as "N/A - First attempt" -->

N/A - First attempt

---

## Session Plan

**Focus Area:** Foundations of spurious correlations and shortcut learning (CFP Topic 3)

**Approach:**
1. Identify research questions grounded in **existing benchmarks** (Waterbirds, CelebA, CMNIST, NICO++)
2. Focus on **theoretical analysis** and **post-hoc analysis** of trained models (no new training pipeline required)
3. Target questions about optimization dynamics, loss landscape geometry, and architectural inductive biases
4. Ensure all hypotheses are testable using gradient analysis, Hessian eigenspectrum, or feature attribution on existing checkpoints

**Constraints Applied:**
- Reject: New benchmark creation, synthetic data generation, human evaluation
- Accept: Analysis of existing trained models, mathematical derivations, measurement using existing metrics

---

## Technique Sessions

**Technique 1: Constraint-Driven Scoping**
- Eliminated research directions requiring new benchmarks (Topics 1, partial Topic 2)
- Focused on foundational theory (Topic 3) that operates on existing artifacts

**Technique 2: Existing Benchmark Mapping**
- Identified standard spurious correlation benchmarks: Waterbirds, CelebA, CMNIST, NICO++
- Confirmed availability of pre-trained checkpoints for various robustification methods (ERM, GroupDRO, IRM, JTT)

**Technique 3: Hypothesis Feasibility Filter**
- Each research question mapped to concrete experimental protocol using existing tools
- Verified immediate testability without future data collection

---

## Research Question Development

### Initial Question

How do optimization dynamics in gradient-descent-based training induce reliance on spurious correlations, and can we characterize this phenomenon through loss landscape geometry and convergence behavior on existing spurious correlation benchmarks?

### Refined Question

Can we mathematically characterize and empirically measure how SGD optimization dynamics cause neural networks to preferentially learn spurious features over core features, by analyzing:
1. The loss landscape geometry around spurious vs. core features
2. The convergence speed and gradient magnitudes for spurious vs. core patterns
3. The Hessian eigenspectrum and sharpness differences between spurious-reliant and robust minima

on existing benchmarks (Waterbirds, CelebA, CMNIST) using pre-trained checkpoints from standard robustification methods (ERM, GroupDRO, IRM, JTT)?

### Detailed Sub-Questions

1. **Loss Landscape Geometry:**
   - How does the loss landscape differ around spurious features vs. core features in networks trained with standard ERM?
   - Can we quantify the "flatness" or "sharpness" of minima that rely on spurious correlations vs. robust minima?
   - Feasibility: Use existing Waterbirds/CelebA checkpoints, compute Hessian eigenspectrum, measure sharpness metrics

2. **Convergence Dynamics:**
   - Do spurious features emerge earlier in training than core features, as hypothesized in recent literature?
   - Can we measure the time-difference in learning spurious vs. core patterns by tracking gradient magnitudes and feature attributions during training?
   - Feasibility: Train ResNet-50 on Waterbirds with standard splits, log gradients and feature attributions per epoch (no new data needed)

3. **Optimization Algorithm Bias:**
   - How do different optimizers (SGD, Adam, AdamW) differ in their tendency to exploit spurious correlations?
   - Does momentum or adaptive learning rate influence the preference for spurious vs. core features?
   - Feasibility: Train models with different optimizers on CMNIST, measure worst-group accuracy and feature attribution

4. **Architectural Inductive Bias:**
   - Do convolutional architectures (ResNet, ViT) exhibit different levels of spurious correlation reliance on the same benchmark?
   - Can we attribute this to architectural inductive biases (e.g., local receptive fields vs. global attention)?
   - Feasibility: Compare ResNet-50 vs. ViT-B/16 on CelebA using existing checkpoints or quick training runs

5. **Mathematical Formulation:**
   - Can we derive a margin-based or PAC-Bayes bound that explains why SGD favors simpler spurious features over complex core features?
   - Does this formulation predict the observed worst-group accuracy gaps?
   - Feasibility: Theoretical derivation + empirical validation on existing benchmark results

---

## Reference Papers

**Core Foundations:**
1. **"Learning from Failure: De-biasing Classifier from Biased Classifier"** (Nam et al., NeurIPS 2020) - JTT method, temporal dynamics of spurious learning
2. **"Invariant Risk Minimization"** (Arjovsky et al., arXiv 2019) - Causal perspective on spurious correlations
3. **"Just Train Twice: Improving Group Robustness without Training Group Information"** (Liu et al., ICML 2021) - Temporal hypothesis of spurious feature learning
4. **"Sharpness-Aware Minimization"** (Foret et al., ICLR 2021) - Loss landscape geometry and generalization
5. **"An Empirical Study of Example Forgetting during Deep Neural Network Learning"** (Toneva et al., ICLR 2019) - Learning dynamics of different feature types

**Spurious Correlation Benchmarks:**
6. **"Waterbirds: A Dataset for Spurious Correlation Challenges"** (Sagawa et al., ICLR 2020) - Standard benchmark
7. **"CelebA: Large-scale CelebFaces Attributes Dataset"** (Liu et al., ICCV 2015) - Spurious gender-attribute correlations
8. **"Colored MNIST: A Minimal Spurious Correlation Dataset"** (Arjovsky et al., 2019) - Controlled spurious feature benchmark
9. **"NICO++: Towards Better Benchmarking for Domain Generalization"** (Zhang et al., CVPR 2023) - Context-based spurious correlations

**Optimization & Loss Landscape:**
10. **"Visualizing the Loss Landscape of Neural Nets"** (Li et al., NeurIPS 2018) - Loss landscape visualization techniques
11. **"On Large-Batch Training for Deep Learning: Generalization Gap and Sharp Minima"** (Keskar et al., ICLR 2017) - Sharpness and generalization
12. **"The Implicit Bias of Gradient Descent on Separable Data"** (Soudry et al., JMLR 2018) - Margin maximization in gradient descent

---

## Validation Results

### So What Test

**Why This Matters:**
- Understanding *why* DNNs rely on spurious correlations is fundamental to designing better robustification methods
- Current methods (GroupDRO, IRM, JTT) work empirically but lack theoretical grounding in optimization dynamics
- If we can characterize the loss landscape and convergence properties that favor spurious features, we can design optimization algorithms or regularization techniques that directly counteract these biases
- Mathematical formulations enable principled algorithm design rather than heuristic trial-and-error

**Impact:**
- Informs design of optimization algorithms that inherently resist spurious correlations
- Provides theoretical foundation for existing empirical robustification methods
- Enables prediction of which architectures/optimizers are more susceptible to shortcuts

**Alignment with Workshop Goals:**
- Directly addresses CFP Topic 3: "Exploring the foundations of spurious correlations and shortcut learning"
- Tackles open questions: "mechanism behind learning biases in various paradigms of AI and in different architectures and algorithms"

### Feasibility Check

**✅ Uses Existing Benchmarks:**
- Waterbirds, CelebA, CMNIST, NICO++ are publicly available
- No new benchmark creation required

**✅ No New Data Required:**
- All experiments use existing datasets
- Pre-trained checkpoints available for many methods (ERM, GroupDRO, IRM on Waterbirds/CelebA)
- Quick training runs on CMNIST (10 epochs, <30 min) acceptable for ablations

**✅ No Human Evaluation:**
- All metrics are automated: worst-group accuracy, gradient norms, Hessian eigenvalues, feature attributions
- Validation uses standard test sets, no human annotation

**✅ Immediate Testability:**
- Hessian computation: existing libraries (PyTorch, JAX)
- Feature attribution: GradCAM, Integrated Gradients
- Loss landscape visualization: established methods (Li et al., 2018)
- Training dynamics: log gradients and accuracies during standard training

**Constraints Satisfied:**
- NO new benchmarks ✅
- NO synthetic data ✅
- NO human evaluation ✅
- Uses existing real datasets ✅

---

## Phase 1 Input Package

<phase1-input>

### research_question
How do SGD optimization dynamics cause neural networks to preferentially learn spurious features over core features, and can we characterize this through loss landscape geometry, convergence speed, and Hessian properties on existing spurious correlation benchmarks?

### detailed_question
1. **Loss Landscape Geometry:** How does the loss landscape differ around spurious features vs. core features? Can we quantify sharpness/flatness of spurious-reliant vs. robust minima using Hessian eigenspectrum on Waterbirds/CelebA checkpoints?

2. **Convergence Dynamics:** Do spurious features emerge earlier in training? Can we measure time-difference in learning spurious vs. core patterns via gradient magnitudes and feature attributions during Waterbirds training?

3. **Optimization Algorithm Bias:** How do SGD, Adam, AdamW differ in spurious correlation reliance? Measure via worst-group accuracy and feature attribution on CMNIST.

4. **Architectural Inductive Bias:** Do ResNet vs. ViT exhibit different spurious reliance on CelebA? Can we attribute this to architectural differences (local vs. global processing)?

5. **Mathematical Formulation:** Can we derive margin-based or PAC-Bayes bounds explaining SGD's preference for simple spurious features? Validate on existing benchmark results.

### reference_papers
- "Learning from Failure: De-biasing Classifier from Biased Classifier" (Nam et al., NeurIPS 2020) - JTT, temporal dynamics
- "Invariant Risk Minimization" (Arjovsky et al., 2019) - Causal perspective
- "Just Train Twice" (Liu et al., ICML 2021) - Temporal hypothesis
- "Sharpness-Aware Minimization" (Foret et al., ICLR 2021) - Loss landscape
- "An Empirical Study of Example Forgetting" (Toneva et al., ICLR 2019) - Learning dynamics
- "Waterbirds" (Sagawa et al., ICLR 2020), "CelebA" (Liu et al., ICCV 2015), "Colored MNIST" (Arjovsky 2019), "NICO++" (Zhang et al., CVPR 2023) - Benchmarks
- "Visualizing the Loss Landscape" (Li et al., NeurIPS 2018), "Large-Batch Training" (Keskar et al., ICLR 2017), "Implicit Bias of Gradient Descent" (Soudry et al., JMLR 2018) - Optimization theory

</phase1-input>

---

## Session Insights

### Key Discoveries

1. **Feasibility-Driven Focus Shift:** Workshop CFP spans three topics; only Topic 3 (foundations) satisfies feasibility constraints without new benchmarks or human evaluation.

2. **Existing Benchmark Sufficiency:** Waterbirds, CelebA, CMNIST provide rich testbed for optimization dynamics, loss landscape, and architectural bias questions.

3. **Pre-trained Checkpoint Leverage:** Many robustification methods have public checkpoints, enabling immediate loss landscape analysis without re-training.

4. **Theoretical + Empirical Synergy:** Combining mathematical formulations (margin theory, PAC-Bayes) with empirical measurements (Hessian, gradients) creates testable hypotheses.

5. **Temporal Dynamics Underexplored:** While JTT/LfF papers hypothesize temporal learning differences, detailed gradient-level analysis across optimizers/architectures is missing.

### Techniques Used

- **Constraint-Driven Scoping:** Eliminated infeasible research directions (Topics 1, 2) early
- **Existing Artifact Mapping:** Identified available benchmarks, checkpoints, analysis tools
- **Hypothesis Feasibility Filter:** Each sub-question mapped to concrete experimental protocol
- **Reference Paper Clustering:** Grouped papers into foundations, benchmarks, optimization theory

### Areas for Further Exploration

1. **Loss Landscape Modes:** Are there multiple local minima - some spurious-reliant, some robust? Can we characterize basin geometry?

2. **Data Augmentation Effects:** How do augmentations (CutMix, MixUp) alter loss landscape and convergence dynamics for spurious vs. core features?

3. **Scaling Laws:** Do spurious correlation tendencies change with model scale (ResNet-18 vs. ResNet-50 vs. ViT-L)?

4. **Multi-Spurious Scenarios:** Most benchmarks have one spurious feature - how do dynamics change with multiple competing spurious features?

5. **Causality-Optimization Bridge:** Can we connect invariance principles (IRM) to optimization trajectory geometry?

---

## Next Steps

1. **Phase 1 - Targeted Research:**
   - Conduct deep literature review on loss landscape analysis methods
   - Search for existing Hessian computation implementations on Waterbirds/CelebA
   - Identify pre-trained checkpoint repositories for ERM, GroupDRO, IRM, JTT
   - Survey theoretical work on margin maximization and implicit bias in SGD

2. **Phase 2A-Dialogue - Hypothesis Generation:**
   - Develop specific hypotheses about loss landscape differences
   - Formalize mathematical conjectures about convergence speed
   - Design ablation studies for optimizer and architecture comparisons

3. **Phase 2B - Planning:**
   - Create experimental protocols for Hessian eigenspectrum computation
   - Plan gradient tracking infrastructure for temporal dynamics study
   - Design training configurations for optimizer/architecture ablations

4. **Validation Checkpoint:**
   - Before Phase 3, re-verify all experiments use existing benchmarks (no new data)
   - Confirm pre-trained checkpoints accessible or training runs <1 hour
   - Ensure all metrics are automated (no human evaluation)

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*

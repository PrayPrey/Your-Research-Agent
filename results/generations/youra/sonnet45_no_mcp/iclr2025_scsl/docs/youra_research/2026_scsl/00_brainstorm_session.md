---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Optimization Dynamics of Shortcut Learning"
---

# Research Brainstorm Session Results

**Session Date:** 2026-04-24
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Understanding the optimization dynamics and loss landscape characteristics that drive spurious correlation learning in gradient-descent-based methods, focusing on observable training phenomena rather than pre-training feature properties.

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction with failure context integration)

---

## Starting Context

Despite the remarkable advancements towards generalizability and autonomy in AI systems, persistent challenges such as spurious correlations and shortcut learning continue to hinder the robustness, reliability, and ethical deployment of machine learning systems. The workshop focuses on three key avenues: (i) comprehensive evaluation benchmarks, (ii) novel solutions for building robust models, and (iii) exploring foundations to deepen understanding of these phenomena.

Source Type: ICLR 2025 Workshop CFP (Spurious Correlation and Shortcut Learning) + Previous Failure Context Recovery

---

## Lessons from Previous Attempts

### Summary of Previous Failures (3 Hypotheses - All MUST_WORK_FAIL)

**Previous Research Direction:** Automated spurious correlation detection via task-alignment dynamics
- **h-e1 (April 21):** Gradient projection ratio hypothesis - FAILED (ratio ~0.77, not predictive)
- **h-m1/h-m1-v2 (April 22):** Linear separability predicts gradients - FAILED (negative correlation r=-0.55)
- **h-e1-v2 (April 24):** Kolmogorov complexity predicts MI growth - FAILED (task-aligned features learned 2.8x-6x faster)

### Root Cause Analysis - Fundamental Flaw

**All three hypotheses assumed intrinsic feature properties (complexity, separability, correlation strength) would predict learning dynamics.** The consistent pattern across failures: **task-alignment to the training objective dominated ALL intrinsic properties.**

### Critical Insight from Failures

The observation that "task-aligned features are learned faster than spurious correlations" is **empirically robust** but represents a **symptom**, not a mechanism. The question shifts from "why are simple features learned first?" (falsified assumption) to "**what optimization dynamics cause task-aligned features to dominate?**"

### What to AVOID (Pipeline-Enforced Constraints)

- ❌ **Do NOT assume** complexity/simplicity metrics predict temporal learning order
- ❌ **Do NOT assume** correlation strength drives gradient magnitude  
- ❌ **Do NOT build** detection methods on unvalidated mechanistic assumptions
- ❌ **Do NOT propose** new benchmarks or synthetic datasets (feasibility constraint violation)
- ❌ **Do NOT require** human annotation or group labels (feasibility constraint violation)

### What Showed PROMISE (Validated Infrastructure)

- ✅ **Gradient monitoring** infrastructure works across paradigms
- ✅ **Loss landscape analysis** tools (Hessian eigenvalues, loss barriers) are implementable
- ✅ **SGD trajectory tracking** is measurable on existing benchmarks
- ✅ **Existing benchmarks** (Waterbirds, CelebA, Colored MNIST) have ground-truth spurious features
- ✅ **Task-alignment dominance** is observable and quantifiable

### Pivot Strategy - From Detection to Foundation

**Previous Direction (FAILED):** Build automated detection methods based on task-alignment observation
**New Direction (This Attempt):** **Understand the optimization foundations that CAUSE task-alignment to dominate** - directly addresses workshop track (iii) "Exploring the foundations of spurious correlations and shortcut learning"

---

## Session Plan

Investigate the role of gradient-descent-based optimization in spurious correlation learning by analyzing loss landscape characteristics and SGD dynamics. Focus on **observable training phenomena** (gradient flow patterns, loss barrier heights, basin geometry) rather than pre-training feature properties, addressing the workshop's explicit call for "studying the role of widely used gradient-descent-based optimization methods in reliance on shortcuts."

---

## Technique Sessions

ROUTE_TO_0 Auto-Fill Mode - Synthesized from failure analysis + ICLR 2025 SCSL workshop topics alignment

---

## Research Question Development

### Initial Question

What optimization dynamics in gradient-descent training cause task-aligned features to dominate early learning, and how do loss landscape characteristics differ between spurious and core feature learning trajectories?

### Refined Question

How do loss landscape geometry and SGD trajectory characteristics explain the dominance of task-aligned feature learning over spurious correlation learning in deep networks, and can these optimization dynamics inform robustification strategies?

### Detailed Sub-Questions

1. **Loss Landscape Geometry:** Do spurious features and core features occupy different regions of the loss landscape (measured via Hessian eigenvalue spectra, loss barrier heights)? Does SGD preferentially converge to core-feature basins?

2. **Gradient Flow Dynamics:** During early training, how do gradient alignment angles between spurious-feature gradients and task-loss gradients compare to core-feature alignment? Does gradient descent naturally suppress misaligned (spurious) directions?

3. **Training Trajectory Analysis:** Can we characterize SGD trajectories in feature-learning space (via representation similarity metrics) and identify when/why spurious features plateau while core features continue improving?

4. **Optimization-Informed Robustification:** Based on observed loss landscape differences, can we design optimization modifications (e.g., adaptive learning rates per feature basin, gradient projection penalties) that further suppress spurious learning without requiring group labels?

5. **Multi-Paradigm Validation (FEASIBILITY CHECK):** Do these optimization dynamics generalize to self-supervised learning (contrastive methods) and different architectures, testable on existing benchmarks (Waterbirds, CelebA, Colored MNIST)?

---

## Reference Papers

Will discover in Phase 1 through systematic literature review focusing on:
- Loss landscape analysis and visualization techniques for deep networks
- SGD trajectory dynamics and basin convergence properties
- Gradient alignment and feature learning emergence timing
- Implicit biases of gradient-descent optimization
- Optimization-based robustification methods (not requiring group annotations)

**Key difference from previous attempts:** Focus on optimization foundations (loss landscape, SGD dynamics) rather than feature-intrinsic properties (complexity, separability).

---

## Validation Results

### So What Test

**Academic Significance:** 
- Workshop **explicitly prioritizes** "studying the role of widely used gradient-descent-based optimization methods in reliance on shortcuts" and "exploring the effect of shortcuts and spurious features on the loss landscape" (Topics section)
- Addresses fundamental gap: **why** task-alignment dominates (mechanism) vs. **that** it dominates (observation from failures)
- Bridges foundations track (understanding optimization) and solutions track (optimization-informed robustification)

**Practical Impact:** 
- Optimization insights can inform algorithm design (adaptive SGD variants, gradient shaping)
- Does NOT require new benchmarks, group labels, or human annotation (feasibility-compliant)

**Novel Contribution:** 
- Inverts failure: "task-alignment dominates intrinsic properties" becomes research question, not assumption
- Focuses on **during-training dynamics** (loss landscape traversal) vs. **pre-training properties** (complexity metrics)

### Feasibility Check

**Immediate Testability:** ✅ PASS (All Constraints Satisfied)

| Constraint | Status | Evidence |
|------------|--------|----------|
| No new benchmarks | ✅ | Uses existing: Waterbirds, CelebA, Colored MNIST (ground-truth spurious features) |
| No synthetic data | ✅ | Standard benchmark datasets only |
| No human evaluation | ✅ | Automated loss landscape analysis (Hessian computation, gradient tracking) |
| Existing infrastructure | ✅ | Gradient monitoring validated across 3 hypotheses; loss landscape tools standard in literature |

**Testable Hypotheses:**
1. Hessian eigenvalue spectra differ between spurious/core feature basins (computable on trained models)
2. Gradient alignment angles predict feature learning priority (measurable during training)
3. SGD trajectories show basin preference for core features (trackable via representation metrics)

**Risk Assessment:** 
- **Low Risk:** Builds on validated gradient/MI infrastructure from previous attempts
- **Grounded:** Observation-driven (task-alignment dominance is empirically robust across 3 failures)
- **Aligned:** Directly addresses workshop's "foundations" track and "optimization methods" priority

---

## Phase 1 Input Package

<phase1-input>

### research_question
How do loss landscape geometry and SGD trajectory characteristics explain the dominance of task-aligned feature learning over spurious correlation learning in deep networks, and can these optimization dynamics inform robustification strategies?

### detailed_question
1. Do spurious features and core features occupy different regions of the loss landscape (measured via Hessian eigenvalue spectra, loss barrier heights)? Does SGD preferentially converge to core-feature basins?
2. During early training, how do gradient alignment angles between spurious-feature gradients and task-loss gradients compare to core-feature alignment? Does gradient descent naturally suppress misaligned (spurious) directions?
3. Can we characterize SGD trajectories in feature-learning space (via representation similarity metrics) and identify when/why spurious features plateau while core features continue improving?
4. Based on observed loss landscape differences, can we design optimization modifications (e.g., adaptive learning rates per feature basin, gradient projection penalties) that further suppress spurious learning without requiring group labels?
5. Do these optimization dynamics generalize to self-supervised learning (contrastive methods) and different architectures, testable on existing benchmarks (Waterbirds, CelebA, Colored MNIST)?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

**Paradigm Shift from Failures:** Three independent failures falsified the "intrinsic property → learning order" assumption. The robust empirical pattern (task-alignment dominates) shifts from assumption to explanandum - **what optimization mechanisms cause this dominance?**

**Workshop Alignment:** ICLR 2025 SCSL explicitly calls for "studying the role of widely used gradient-descent-based optimization methods" and "exploring the effect of shortcuts and spurious features on the loss landscape" - this research question directly addresses those priorities.

**Foundation → Solutions Path:** Understanding optimization dynamics (foundations track) enables optimization-informed robustification (solutions track) without requiring group labels.

### Techniques Used

ROUTE_TO_0 Failure Recovery Mode - Systematic analysis of three MUST_WORK_FAIL results to pivot from **detection methods** (building on unvalidated assumptions) to **foundational investigation** (understanding the optimization mechanisms that caused consistent observations).

### Areas for Further Exploration

- Hessian eigenvalue spectrum analysis across training (sharpness vs. flatness of spurious/core basins)
- Gradient alignment trajectory visualization (feature-gradient vs. task-gradient cosine similarity over time)
- Loss barrier measurement between local minima (spurious-dominated vs. core-dominated solutions)
- Adaptive SGD variants that penalize low-alignment gradient directions
- Extension to contrastive learning (does alignment still dominate in self-supervised objectives?)

---

## Next Steps

Proceed to Phase 1 - Targeted Research

**Research Focus:**
1. Loss landscape analysis techniques (Hessian computation, mode connectivity, basin geometry)
2. SGD trajectory characterization methods (representation tracking, convergence basin analysis)
3. Gradient alignment metrics and feature emergence timing
4. Implicit biases of gradient-descent optimization
5. Optimization-based robustification strategies (not requiring group annotations)

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
*Mode: ROUTE_TO_0 - Learned from 3 previous MUST_WORK_FAIL results and pivoted to optimization foundations*

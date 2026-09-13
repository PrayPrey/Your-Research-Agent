---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Spurious Correlation Detection via Training Dynamics"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-12
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Understanding spurious correlations and shortcut learning in deep learning - focusing on detection and mitigation methods that work WITHOUT requiring group annotations

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Reliance on spurious correlations due to simplicity bias is a well-known pitfall of deep learning models. This issue stems from the statistical nature of deep learning algorithms and their inductive biases at all stages, including data preprocessing, architectures, and optimization. Models rely on spurious patterns rather than understanding underlying causal relationships, making them vulnerable to failure in real-world scenarios where data distributions involve under-represented groups or minority populations.

Source Type: Workshop CFP (ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning)
Retrying after previous failure (H-M1 hypothesis failed MUST_WORK gate)

---

## Lessons from Previous Attempts

### What Was Tried (H-M1 Hypothesis)

**Hypothesis:** "SGD's implicit regularization drives parameters toward flat regions of the loss landscape, evidenced by decreasing Hessian trace during training."

**Approach:** Measured Hessian trace every 10 epochs during ResNet-18 fine-tuning on Waterbirds dataset using PyHessian Hutchinson method.

### Why It Failed

The hypothesis was **empirically refuted**:
- Expected: Hessian trace DECREASING (indicating flattening loss landscape)
- Observed: Hessian trace INCREASED by +363% (1460 → 6758)
- Strong positive correlation r=+0.822 (p=0.0019) with training progress

**Root Cause:** SGD does NOT exhibit implicit sharpness minimization in pretrained + fine-tuning settings. The mechanism may be specific to training-from-scratch scenarios or require different learning rate regimes.

### How THIS Direction Avoids Those Pitfalls

1. **AVOID:** Making assumptions about Hessian behavior in fine-tuning settings
2. **AVOID:** Relying on single geometric metric (Hessian trace) as primary signal
3. **PIVOT TO:** Observable training dynamics that are empirically grounded
4. **NEW FOCUS:** Detecting spurious correlation reliance through feature attribution methods, gradient-based analysis, or representation geometry - approaches that don't assume specific optimizer geometry effects

---

## Session Plan

Auto-extracted from structured input with failure-informed pivoting:
1. **AVOID** loss landscape geometry hypotheses (disproven by H-M1)
2. **FOCUS ON** detection methods that don't require mechanistic assumptions about SGD
3. **PRIORITIZE** empirically testable feature attribution approaches
4. Target: Methods that work WITHOUT group annotations

---

## Technique Sessions

Auto-Fill Mode - No interactive sessions (ROUTE_TO_0 failure recovery)

---

## Research Question Development

### Initial Question

How can we detect and mitigate reliance on spurious correlations in DNNs without requiring group annotations?

### Refined Question

Can we identify spurious feature reliance through training dynamics signals (loss trajectory, gradient patterns, or representation changes) rather than assumed optimizer geometry properties, enabling detection and mitigation WITHOUT group labels?

### Detailed Sub-Questions

1. Do samples relying on spurious vs. core features show distinguishable loss trajectory patterns during training?
2. Can gradient-based attribution methods identify spurious features without group supervision?
3. Does the timing of when samples are "learned" (loss drops below threshold) correlate with spurious vs. core feature reliance?
4. Can representation space analysis (clustering, similarity) reveal spurious subgroups automatically?
5. What robustification interventions are effective once spurious-reliant samples are identified?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

Input from established research venue (ICLR 2025 Workshop) - significance pre-validated. Pivoting from disproven mechanism hypothesis to empirically-grounded detection methods. This direction enables: (1) practical spurious correlation detection without expensive annotations, (2) principled sample weighting/rebalancing, (3) safer model deployment.

### Feasibility Check

**PASS** - Meets all mandatory constraints:
- Uses existing benchmarks (Waterbirds, CelebA, MultiNLI, CivilComments)
- No new benchmarks/rubrics required
- No synthetic data needed
- No human evaluation required
- Testable immediately with existing datasets
- **Explicitly AVOIDS** the failed H-M1 approach (Hessian trace analysis)

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can we identify spurious feature reliance through training dynamics signals (loss trajectory, gradient patterns, or representation changes) rather than assumed optimizer geometry properties, enabling detection and mitigation WITHOUT group labels?

### detailed_question
1. Do samples relying on spurious vs. core features show distinguishable loss trajectory patterns during training?
2. Can gradient-based attribution methods identify spurious features without group supervision?
3. Does the timing of when samples are "learned" (loss drops below threshold) correlate with spurious vs. core feature reliance?
4. Can representation space analysis (clustering, similarity) reveal spurious subgroups automatically?
5. What robustification interventions are effective once spurious-reliant samples are identified?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

Previous attempt (H-M1) empirically disproved that SGD drives toward flat loss regions during fine-tuning. Hessian trace INCREASED, not decreased. This eliminates optimizer geometry as viable mechanistic explanation in pretrained settings. New direction focuses on observable training dynamics rather than assumed geometric properties.

### Techniques Used

ROUTE_TO_0 (Failure Recovery - learned from H-M1 MUST_WORK failure)

### Areas for Further Exploration

- Early vs. late learning dynamics as spurious/core feature signal
- Gradient-based feature attribution without group labels
- Representation clustering for automatic subgroup discovery
- Sample difficulty/memorization patterns

---

## Next Steps

Proceed to Phase 1 - Targeted Research (with failure-informed constraints: AVOID Hessian-based geometry hypotheses)

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 Failure Recovery)*
*Ready for: Phase 1 - Targeted Research*

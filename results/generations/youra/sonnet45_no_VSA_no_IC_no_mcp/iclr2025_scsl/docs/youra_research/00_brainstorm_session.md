---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Spurious Correlation Foundations and Robustness"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-24
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Investigating the foundations of spurious correlations and shortcut learning in deep neural networks, specifically focusing on understanding the mechanisms behind learning biases across different architectures and optimization algorithms.

**Session Approach:** UNATTENDED mode - auto-extraction from workshop topics and objectives.

**Session Duration:** Automated extraction (< 2 minutes)

---

## Starting Context

The ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning focuses on two primary aspects: (i) foundations and (ii) solutions. While impacts and solutions have been frequently targeted, attention has recently shifted to foundations. Recent works focus on origins of reliance on spurious correlation in DNNs - factors such as margin maximization tendency, SGD training biases, and temporal differences in learning core vs spurious patterns. However, many open questions remain regarding the mechanism behind learning biases in various AI paradigms, architectures, and algorithms.

Key constraints for research pipeline feasibility:
- REJECT: New benchmarks, rubrics, or scoring frameworks
- REJECT: Synthetic/generated data or future follow-up data
- REJECT: Human evaluation, annotation, or subjective scoring
- ACCEPT: Hypotheses testable immediately using existing real datasets and existing benchmarks

---

## Lessons from Previous Attempts

N/A - First attempt

---

## Session Plan

Focus on foundational understanding rather than benchmark creation or robustification methods. Target research questions that can be tested using existing datasets (e.g., Waterbirds, CelebA, CMNIST) and existing analysis tools. Prioritize mathematical formulations, optimization analysis, and loss landscape exploration that align with workshop's foundations track.

---

## Technique Sessions

**Technique 1: Gap Analysis**
- Workshop highlights: "lots of open questions regarding the mechanism behind learning biases in various paradigms of AI and in different architectures and algorithms remain open"
- Identified gap: Understanding architectural and algorithmic differences in spurious correlation learning

**Technique 2: Constraint Mapping**
- Feasibility constraints require existing benchmarks → focus on analysis of existing benchmark datasets
- Cannot create new datasets → must leverage existing spurious correlation benchmarks (Waterbirds, CelebA, CMNIST, etc.)

**Technique 3: Topic Alignment**
- Workshop explicitly seeks: "Presenting mathematical formulations that describe the issue and its origins"
- Workshop explicitly seeks: "Studying the role of widely used gradient-descent-based optimization methods in reliance on shortcuts"
- Workshop explicitly seeks: "Exploring the effect of shortcuts and spurious features on the loss landscape"

---

## Research Question Development

### Initial Question

How do different neural network architectures (CNNs, Transformers, ResNets) differ in their susceptibility to learning spurious correlations, and what architectural properties determine this behavior?

### Refined Question

What architectural properties (depth, width, attention mechanisms, normalization layers) and optimization dynamics (learning rate, batch size, optimizer choice) influence the temporal dynamics of spurious vs core feature learning in deep neural networks?

### Detailed Sub-Questions

1. **Temporal Learning Dynamics**: Do different architectures exhibit different temporal ordering in learning spurious vs core features? Can we quantify the "shortcut timing gap" across architectures?

2. **Architectural Components**: Which specific architectural components (batch normalization, layer normalization, attention layers, skip connections) accelerate or delay spurious correlation learning?

3. **Optimization Interactions**: How do optimization hyperparameters (learning rate schedule, batch size, optimizer choice) interact with architectural properties to influence spurious correlation susceptibility?

4. **Loss Landscape Analysis**: How does the loss landscape geometry differ between models that rely heavily on spurious correlations vs those that learn core features? Can we characterize spurious correlation susceptibility through Hessian eigenvalue spectra or local curvature?

5. **Testability**: Can these phenomena be measured and compared using existing spurious correlation benchmarks (Waterbirds, CelebA, CMNIST) without requiring new datasets or human annotation?

---

## Reference Papers

1. **Simplicity Bias in Neural Networks** - Papers studying why neural networks prefer simple solutions and how this relates to spurious correlations
2. **Temporal Dynamics of Learning** - Research on the timing differences between learning spurious vs core features during training
3. **Loss Landscape Geometry** - Studies on how loss landscape properties relate to generalization and robustness
4. **Group DRO and Spurious Correlations** - Existing work on detecting and measuring spurious correlations in standard benchmarks
5. **Architecture-specific Inductive Biases** - Research comparing how CNNs, Transformers, and other architectures differ in their learning biases

---

## Validation Results

### So What Test

**Impact**: Understanding architectural and optimization factors that influence spurious correlation learning enables:
- Principled architecture design choices for robustness
- Better optimization strategies to mitigate shortcut learning
- Theoretical foundations for understanding when and why spurious correlations emerge
- Guidance for practitioners on architecture selection for robustness-critical applications

**Novelty**: While individual factors have been studied, systematic comparison across architectures and optimization settings using temporal dynamics and loss landscape analysis provides new insights into the mechanisms behind spurious correlation susceptibility.

### Feasibility Check

✓ **Uses existing datasets**: Waterbirds, CelebA, CMNIST, ImageNet variants with known spurious correlations
✓ **Uses existing benchmarks**: Standard group robustness evaluation protocols (worst-group accuracy)
✓ **No new annotations required**: Datasets already have group labels and spurious correlation annotations
✓ **No synthetic data required**: All experiments use existing real-world datasets
✓ **Testable immediately**: Can train multiple architectures and analyze temporal dynamics and loss landscapes
✓ **Quantifiable metrics**: Worst-group accuracy, temporal learning curves, Hessian analysis, gradient statistics

**Constraints satisfied**: All mandatory feasibility constraints are met.

---

## Phase 1 Input Package

<phase1-input>

### research_question
What architectural properties and optimization dynamics influence the temporal learning dynamics of spurious vs core features in deep neural networks?

### detailed_question
Investigate how different neural network architectures (CNNs, Transformers, ResNets, ViTs) and their specific components (normalization layers, attention mechanisms, skip connections) interact with optimization hyperparameters (learning rate, batch size, optimizer choice) to determine:
(1) The temporal ordering of spurious vs core feature learning
(2) The loss landscape geometry associated with spurious correlation susceptibility
(3) The gradient flow and Hessian eigenvalue characteristics during training
(4) Quantifiable architectural properties that predict spurious correlation reliance

Test these questions using existing spurious correlation benchmarks (Waterbirds, CelebA, CMNIST) through worst-group accuracy evaluation and temporal analysis of learning dynamics.

### reference_papers
- Simplicity bias and neural network learning preferences
- Temporal dynamics of spurious vs core feature learning
- Loss landscape geometry and generalization
- Group distributionally robust optimization (DRO)
- Architectural inductive biases in CNNs and Transformers
- Hessian eigenvalue analysis and neural network training
- Optimization hyperparameters and spurious correlation learning

</phase1-input>

---

## Session Insights

### Key Discoveries

1. Workshop's foundation track explicitly seeks mathematical formulations and optimization analysis - perfect alignment with architectural/algorithmic mechanism study
2. Feasibility constraints eliminate benchmark creation approaches but enable analysis-focused investigations
3. Temporal dynamics provide testable framework for comparing architectures without new datasets
4. Loss landscape analysis offers mathematical foundation for understanding spurious correlation susceptibility

### Techniques Used

- Gap analysis (workshop topics vs open questions)
- Constraint mapping (feasibility requirements → research approach)
- Topic alignment (workshop priorities → research focus)
- Testability verification (existing benchmarks → experimental validation)

### Areas for Further Exploration

- Causal representation learning foundations
- Theoretical margin maximization analysis
- SGD bias characterization across architectures
- Multi-modal spurious correlation mechanisms (if time permits after image-based study)

---

## Next Steps

1. **Phase 1 - Targeted Research**: Conduct literature search for papers on:
   - Temporal dynamics of spurious vs core feature learning
   - Architectural comparisons in spurious correlation susceptibility
   - Loss landscape geometry and robustness
   - Optimization dynamics and shortcut learning
   - Hessian analysis and neural network training

2. **Focus Areas for Phase 1**:
   - Find existing methods for measuring temporal learning dynamics
   - Identify architectural comparison frameworks
   - Locate loss landscape analysis techniques
   - Gather information on existing spurious correlation benchmarks and evaluation protocols

3. **Expected Phase 1 Output**: Collection of relevant papers and methods for architecting Phase 2A hypotheses about architectural mechanisms behind spurious correlation learning.

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*

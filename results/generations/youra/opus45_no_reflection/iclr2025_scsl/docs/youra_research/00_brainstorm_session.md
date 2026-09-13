---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Spurious Correlation and Shortcut Learning"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-18
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Understanding foundations and solutions for spurious correlations and shortcut learning in deep learning models

**Session Approach:** Auto-Fill (Batch Mode) - Extracted from ICLR 2025 Workshop CFP

**Session Duration:** Auto-generated (UNATTENDED mode)

---

## Starting Context

The research context focuses on the ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning. Key themes:

1. **Problem Definition:** Deep learning models rely on spurious correlations due to simplicity bias, stemming from statistical nature and inductive biases in data preprocessing, architectures, and optimization
2. **Impact:** Models exploit spurious patterns instead of causal relationships, failing on under-represented groups and minority populations
3. **Research Gaps:**
   - Current group-label benchmarks offer limited robustness guarantees
   - Human annotation doesn't scale and misses non-perceptual spurious correlations
   - Limited investigation beyond supervised learning
   - Foundation models need study as both tools and subjects
4. **Emerging Focus:** Origins of spurious correlation reliance (margin maximization, SGD biases, learning dynamics of core vs spurious patterns)

**MANDATORY FEASIBILITY CONSTRAINTS:**
- No new benchmarks/rubrics/scoring frameworks
- No synthetic/generated data
- No human evaluation/annotation
- Only existing real datasets and benchmarks

---

## Lessons from Previous Attempts

N/A - First attempt

---

## Session Plan

Auto-Fill mode: Extract research question from workshop CFP topics, constrained by feasibility requirements.

---

## Technique Sessions

**Technique:** Constraint-Guided Extraction

Applied feasibility constraints to workshop topics to identify testable research directions:

| Topic Area | Feasibility | Rationale |
|------------|-------------|-----------|
| New benchmarks | REJECT | Violates constraint: no new benchmarks |
| LLM/LMM robustness | ACCEPT | Can use existing benchmarks (Waterbirds, CelebA, MultiNLI, WILDS) |
| New robustification methods | ACCEPT | Can evaluate on existing benchmarks |
| Causal representation learning | PARTIAL | Only if using existing datasets |
| Mathematical foundations | ACCEPT | Theoretical + existing benchmark validation |
| SGD/optimization role | ACCEPT | Can study on existing datasets |
| Loss landscape effects | ACCEPT | Empirical study on existing benchmarks |

**Selected Direction:** Studying the role of optimization dynamics in spurious correlation reliance, specifically the temporal difference in learning core vs spurious features, validated on existing benchmarks.

---

## Research Question Development

### Initial Question

How do gradient-descent-based optimization methods contribute to the reliance on spurious correlations in deep neural networks?

### Refined Question

What is the relationship between training dynamics (specifically, the temporal ordering of feature learning during SGD optimization) and the model's reliance on spurious correlations, and can this relationship be exploited to improve worst-group robustness without requiring group annotations?

### Detailed Sub-Questions

1. **Learning Dynamics:** Do spurious features get learned earlier than core features during training, and does this temporal pattern correlate with final model reliance on spurious correlations?

2. **Intervention Timing:** Can early-stopping or learning rate scheduling based on feature learning dynamics reduce spurious correlation reliance?

3. **Architecture Effects:** How do different architectures (ResNet, ViT, MLP-Mixer) differ in their temporal learning patterns of spurious vs core features?

4. **Annotation-Free Detection:** Can the temporal dynamics of loss curves on different data subsets serve as a proxy for detecting spurious correlations without explicit group labels?

5. **Transferability:** Do findings on standard spurious correlation benchmarks (Waterbirds, CelebA, ColoredMNIST) generalize to WILDS benchmarks?

---

## Reference Papers

1. **Sagawa et al. (2020)** - "Distributionally Robust Neural Networks for Group Shifts" - Introduces group DRO and Waterbirds/CelebA benchmarks
   - *Relevance:* Baseline method and benchmark datasets

2. **Liu et al. (2021)** - "Just Train Twice: Improving Group Robustness without Training Group Information" - JTT method
   - *Relevance:* Annotation-free robustification baseline

3. **Nam et al. (2020)** - "Learning from Failure: Training Debiased Classifier from Biased Classifier" - LfF method
   - *Relevance:* Uses learning dynamics for debiasing

4. **Idrissi et al. (2022)** - "Simple Data Balancing Achieves Competitive Worst-Group-Accuracy" - DFR method
   - *Relevance:* Simple baseline, benchmark results

5. **Shah et al. (2020)** - "The Pitfalls of Simplicity Bias in Neural Networks"
   - *Relevance:* Foundational work on simplicity bias

6. **Pezeshki et al. (2021)** - "Gradient Starvation: A Learning Proclivity in Neural Networks"
   - *Relevance:* Gradient dynamics and feature learning order

---

## Validation Results

### So What Test

**Research Impact:**
- Understanding temporal feature learning could enable **annotation-free** robustification methods
- Practical benefit: Removes need for expensive group annotations
- Theoretical contribution: Mechanistic understanding of why DNNs prefer spurious features

**Who Benefits:**
- ML practitioners deploying models in fairness-critical domains
- Researchers studying DNN learning dynamics
- Healthcare/legal/finance applications requiring robust models

### Feasibility Check

| Criterion | Status | Notes |
|-----------|--------|-------|
| Existing datasets | ✓ PASS | Waterbirds, CelebA, ColoredMNIST, WILDS available |
| Existing benchmarks | ✓ PASS | Standard worst-group accuracy metrics |
| No human annotation | ✓ PASS | Datasets already annotated |
| No synthetic data | ✓ PASS | All real image/attribute datasets |
| Testable immediately | ✓ PASS | Can start experiments now |

---

## Phase 1 Input Package

<phase1-input>

### research_question
What is the relationship between training dynamics (specifically, the temporal ordering of feature learning during SGD optimization) and the model's reliance on spurious correlations, and can this relationship be exploited to improve worst-group robustness without requiring group annotations?

### detailed_question
1. Do spurious features get learned earlier than core features during training, and does this temporal pattern correlate with final model reliance on spurious correlations?
2. Can early-stopping or learning rate scheduling based on feature learning dynamics reduce spurious correlation reliance?
3. How do different architectures (ResNet, ViT, MLP-Mixer) differ in their temporal learning patterns of spurious vs core features?
4. Can the temporal dynamics of loss curves on different data subsets serve as a proxy for detecting spurious correlations without explicit group labels?
5. Do findings on standard spurious correlation benchmarks (Waterbirds, CelebA, ColoredMNIST) generalize to WILDS benchmarks?

### reference_papers
1. Sagawa et al. (2020) - "Distributionally Robust Neural Networks for Group Shifts" - Group DRO baseline and benchmarks
2. Liu et al. (2021) - "Just Train Twice: Improving Group Robustness without Training Group Information" - JTT annotation-free baseline
3. Nam et al. (2020) - "Learning from Failure: Training Debiased Classifier from Biased Classifier" - LfF dynamics-based method
4. Idrissi et al. (2022) - "Simple Data Balancing Achieves Competitive Worst-Group-Accuracy" - DFR simple baseline
5. Shah et al. (2020) - "The Pitfalls of Simplicity Bias in Neural Networks" - Simplicity bias foundation
6. Pezeshki et al. (2021) - "Gradient Starvation: A Learning Proclivity in Neural Networks" - Gradient dynamics

</phase1-input>

---

## Session Insights

### Key Discoveries

1. Workshop emphasizes **foundations** as emerging research direction - temporal learning dynamics fits this gap
2. Feasibility constraints naturally filter toward **optimization/dynamics** research (no new data needed)
3. Multiple existing methods (LfF, JTT) already use learning dynamics - opportunity to unify understanding

### Techniques Used

- Constraint-Guided Extraction (feasibility filtering)
- Topic Clustering (workshop themes to research angles)
- Gap Analysis (foundations vs solutions emphasis)

### Areas for Further Exploration

1. Connection between gradient starvation and spurious correlation
2. Role of batch normalization in spurious feature amplification
3. Contrastive learning dynamics on biased datasets
4. Multi-modal spurious correlations in CLIP-style models

---

## Next Steps

1. **Phase 1:** Conduct targeted literature search on training dynamics and spurious correlations
2. Identify specific experimental protocols from existing papers
3. Select primary benchmark (Waterbirds recommended for initial experiments)
4. Define measurable proxies for "feature learning timing"

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*

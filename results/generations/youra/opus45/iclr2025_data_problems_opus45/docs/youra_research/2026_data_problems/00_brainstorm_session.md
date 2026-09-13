---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Data Attribution Efficiency in FM"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-24
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Data problems in foundation models, specifically efficient data attribution methods that can scale to FM training data sizes while maintaining accuracy for practical applications like data valuation and copyright attribution

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction with failure context integration)

---

## Starting Context

Foundation models (FMs) have become central to modern machine learning, with data playing a crucial role in their development and sparking increased attention to data-related challenges such as curation and attribution. A key challenge in the DATA-FM workshop scope is developing efficient techniques for attributing model outputs to specific training data, evaluating data attribution methods, and supporting data marketplaces that ensure fair compensation.

**Source Type:** Workshop CFP (ICLR 2025 DATA-FM Workshop)
**Recovery Context:** Retrying after THREE previous Phase 4 MUST_WORK failures (h-e1, h-m2, h-m3)

---

## Lessons from Previous Attempts

### CRITICAL: Complete Topic Pivot Required

All three previous failures (h-e1, h-m2, h-m3) focused on **model collapse mechanisms**. This entire research direction has been systematically falsified:

### Previous Attempt 1: Temporal Ordering (h-e1) - METHODOLOGY_NOT_DEMONSTRATED

**What was tried:** Testing whether temporal ordering of data (real-first vs. synthetic-first) affects model collapse dynamics.

**Why it failed:**
- No actual synthetic data generation was implemented (`model.generate()` not used)
- Both "real" and "synthetic" groups used real data samples
- Cohen's d = 0.0 indicated no effect because the fundamental mechanism was absent
- Cannot study collapse effects without inducing actual collapse

**Lesson:** Complex synthetic data generation is error-prone and hard to implement correctly.

### Previous Attempt 2: Hessian Spectral Properties (h-m2) - HYPOTHESIS_FALSIFIED

**What was tried:** Testing whether Hessian spectral properties (spectral norm/trace ratio) increase during model collapse.

**Why it failed:**
- **Hypothesis FALSIFIED with OPPOSITE results**: Spectral ratio DECREASED (not increased)
- Trace INCREASED from 2643 to 4090 (landscape became MORE complex, not less)
- Correlation with entropy was only r = 0.14 (insufficient)
- Curvature concentration is NOT the mechanism of model collapse

**Lesson:** Loss landscape curvature-based hypotheses about collapse are empirically unfounded.

### Previous Attempt 3: Gradient-Representation Link (h-m3) - HYPOTHESIS_FALSIFIED

**What was tried:** Testing whether gradient concentration causes representation homogenization.

**Why it failed:**
- **Strong statistical refutation**: Correlation was r = -0.624 (OPPOSITE of predicted +0.5)
- PR INCREASED 13.67% when it should have decreased
- 0/4 seeds showed positive correlation (expected 3/4)
- The causal chain from gradient dynamics to representation collapse is broken

**Lesson:** Representation degeneration metrics (PR, SGC) do NOT track gradient dynamics as theorized.

### How THIS Direction Avoids Those Pitfalls

**Complete Topic Pivot:** Instead of studying model collapse mechanisms (3x failed), pivot to **Data Attribution** - a completely different CFP topic that:

1. **Does NOT require synthetic data generation** (h-e1 failure mode avoided)
2. **Does NOT assume curvature/gradient mechanisms** (h-m2, h-m3 failure modes avoided)
3. **Uses existing trained models and real data** - no experimental data generation needed
4. **Has established evaluation methods** - existing attribution benchmarks available
5. **Is empirically grounded** - can measure attribution accuracy directly

**Why Data Attribution:**
- Workshop explicitly calls for "efficient techniques for attributing model outputs to specific training data"
- Existing benchmarks and methods to compare against (influence functions, TracIn, TRAK)
- Computation/accuracy tradeoffs are measurable, not mechanism hypotheses
- Real-world applications: data valuation, copyright, model debugging

---

## Session Plan

Auto-extracted from structured input with complete topic pivot - focusing on:
1. Data Attribution, Interpretability, and Data Marketplaces (PRIMARY - new direction)
2. Benchmarks and Evaluations (using existing attribution evaluation methods)
3. Legal and Technical Solutions for Data Copyright Protection (downstream application)

**Feasibility-First Approach:** Compare existing data attribution methods on established benchmarks with focus on efficiency-accuracy tradeoffs at FM scale.

---

## Technique Sessions

ROUTE_TO_0 Mode - Complete topic pivot (model collapse → data attribution) based on systematic failure analysis

---

## Research Question Development

### Initial Question

How can data attribution methods scale to foundation model training data sizes while maintaining sufficient accuracy for practical applications like data valuation and copyright detection?

### Refined Question

**Do gradient-based attribution approximations (e.g., TRAK, influence function approximations) maintain rank-order accuracy compared to exact methods when applied at different computational budgets, and what is the Pareto frontier of the computation-accuracy tradeoff across existing methods?**

This question is:
- **Empirically testable**: Compare methods on same benchmarks, measure computation vs. accuracy
- **Feasible**: Uses existing attribution methods with available implementations
- **Novel**: Systematic Pareto analysis of attribution methods at FM scale is underexplored
- **Avoids ALL previous failures**: No synthetic data, no mechanism hypotheses, no collapse assumptions
- **Significant**: Practical guidance for practitioners choosing attribution methods under resource constraints

### Detailed Sub-Questions

1. **Method Comparison**: What is the rank-order correlation (Spearman/Kendall) between exact influence functions and efficient approximations (TRAK, FastIF, Arnoldi approximation) on standard attribution benchmarks?

2. **Computation Scaling**: How does attribution accuracy degrade as computation budget decreases (fewer gradient samples, lower-rank approximations, smaller probe sets)?

3. **Task Transfer**: Do attribution rankings generalize across tasks (classification → generation) or must attribution be recomputed per downstream task?

4. **Data Scale Effects**: At what training data scale do different approximation methods diverge most from exact attribution, and why?

5. **Practical Thresholds**: What minimum computation budget is needed to achieve top-k accuracy (identifying most influential training examples) for typical FM applications?

---

## Reference Papers

Not provided - will discover in Phase 1

**Expected relevant topics for Phase 1 search:**
- TRAK: Attributing Model Behavior at Scale (Park et al., 2023)
- Influence Functions in Deep Learning (Koh & Liang, 2017)
- FastIF: Scalable Influence Functions (Guo et al., 2021)
- Data Shapley and data valuation methods
- TracIn: Tracing Gradient Descent (Pruthi et al., 2020)
- Attribution benchmarks and evaluation protocols

---

## Validation Results

### So What Test

**Significance:** Data attribution is critical for:
1. **Data marketplaces**: Fair compensation requires knowing which training data contributed to model capabilities
2. **Copyright compliance**: Identifying when model outputs are attributable to copyrighted training data
3. **Model debugging**: Finding which training examples cause specific model behaviors
4. **Data curation**: Selecting high-value training data for FM development

**Impact:** Results would provide:
1. Practical guidance for practitioners on which attribution method to use given their compute budget
2. Pareto frontier characterizing the fundamental computation-accuracy tradeoff
3. Understanding of when approximations fail and why
4. Recommendations for minimum viable attribution at FM scale

### Feasibility Check

**Feasibility Assessment:** HIGH

- **Data Requirements**: Uses existing trained models and standard attribution benchmarks (no new data generation)
- **Method Requirements**: All compared methods have public implementations (TRAK, influence functions, TracIn)
- **Computational Requirements**: Comparing efficiency requires running methods at various budgets - computationally tractable
- **Evaluation**: Uses existing attribution accuracy metrics (rank correlation, top-k accuracy) - NO new benchmarks needed
- **Constraints Satisfied**:
  - No new benchmarks required (uses existing attribution evaluation protocols)
  - No human evaluation required (automated rank correlation metrics)
  - Uses existing real datasets and trained models
  - Testable immediately with available tools and implementations

**Avoiding Previous Failures:**
- **Unlike h-e1**: No synthetic data generation needed; works with existing trained models
- **Unlike h-m2**: No loss landscape mechanism hypotheses; directly measures attribution accuracy
- **Unlike h-m3**: No gradient-representation causal chains; focuses on input-output attribution
- **Complete topic pivot**: From model collapse to data attribution - entirely different research area

---

## Phase 1 Input Package

<phase1-input>

### research_question
Do gradient-based attribution approximations (e.g., TRAK, influence function approximations) maintain rank-order accuracy compared to exact methods when applied at different computational budgets, and what is the Pareto frontier of the computation-accuracy tradeoff across existing methods?

### detailed_question
1. What is the rank-order correlation (Spearman/Kendall) between exact influence functions and efficient approximations (TRAK, FastIF, Arnoldi approximation) on standard attribution benchmarks?
2. How does attribution accuracy degrade as computation budget decreases (fewer gradient samples, lower-rank approximations, smaller probe sets)?
3. Do attribution rankings generalize across tasks (classification → generation) or must attribution be recomputed per downstream task?
4. At what training data scale do different approximation methods diverge most from exact attribution, and why?
5. What minimum computation budget is needed to achieve top-k accuracy (identifying most influential training examples) for typical FM applications?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- Three consecutive failures (h-e1, h-m2, h-m3) in the model collapse research direction indicate fundamental issues with that approach
- Complete topic pivot is necessary: model collapse mechanisms have been systematically falsified
- Data attribution is an explicit CFP topic with existing benchmarks and implementations
- Efficiency-accuracy tradeoffs are directly measurable (unlike mechanism hypotheses)
- Practical applications (copyright, data valuation) provide clear significance

### Techniques Used

ROUTE_TO_0 Mode (failure-informed complete topic pivot with feasibility constraints)

### Areas for Further Exploration

- Connection to data valuation: How do attribution methods relate to Shapley-based data value?
- Privacy implications: Does attribution enable membership inference attacks?
- Multi-modal attribution: How do methods extend to vision-language models?
- Dynamic attribution: How does attribution change during training?

---

## Next Steps

Proceed to Phase 1 - Targeted Research

**Phase 1 Focus:**
1. Literature review on data attribution methods (influence functions, TRAK, TracIn, data Shapley)
2. Survey of attribution benchmarks and evaluation protocols
3. Identify available implementations and their computational requirements
4. Collect information on existing efficiency-accuracy comparisons

**Key Differences from Previous Attempts:**
- **Complete topic pivot**: From model collapse to data attribution
- **Focus on MEASUREMENT not MECHANISM**: Compare existing methods rather than test hypotheses about underlying processes
- **Use EXISTING implementations and benchmarks**: No novel experimental setups that could fail
- **Practical orientation**: Pareto frontiers provide actionable guidance

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 Recovery - 4th Attempt)*
*Ready for: Phase 1 - Targeted Research*

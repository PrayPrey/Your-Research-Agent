# Phase 2A Extended: Hypothesis Clarification Summary

**Date:** 2026-02-06
**Author:** Claude Sonnet 4.5 (YouRA Phase 2A-Extended)
**Source Round:** Round 1 (FEASIBLE)
**Original Hypothesis:** Causal Mechanistic Tracing for Dynamic LLM Evaluation
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

**Hypothesis ID:** H-CMT-001
**Confidence Level:** 85%

This document presents the scientific clarification of the "Causal Mechanistic Tracing" hypothesis, which proposes a diagnostic evaluation framework for causal reasoning in Large Language Models. By integrating mechanistic interpretability techniques (activation patching, causal tracing) with rung-stratified causal reasoning tasks (Pearl's 3-level hierarchy), the framework aims to localize causal reasoning capabilities to specific model components (attention heads, layers) and provide diagnostic insights beyond aggregate performance metrics.

**Key Innovation:** First integration of mechanistic interpretability with structured causal reasoning evaluation, enabling component-level diagnosis of WHY and WHERE LLMs fail at causal reasoning.

**Gap Addressed:** Gap 2 - Scalable Evaluation of Causal Reasoning Beyond Benchmarks (current benchmarks show 57.6% accuracy but provide no diagnostic insights)

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Main Hypothesis:**
Applying mechanistic interpretability techniques (causal tracing, activation patching) to rung-stratified causal reasoning tasks (Pearl's 3-level hierarchy) enables localization and characterization of causal reasoning capabilities in Large Language Models at the component level, providing diagnostic insights that predict failure modes on held-out tasks significantly above chance (AUC > 0.65) and above random component baseline (Cohen's d > 0.5).

**Alternative Hypothesis (H0):**
Causal reasoning in LLMs is fully distributed, resulting in uniform performance degradation when any component is patched, making component-level diagnosis impossible (task-relevant patches ≈ random patches, AUC ≤ 0.55).

### 1.2 Variables

| Type | Name | Operationalization | Measurement |
|------|------|-------------------|-------------|
| **IV** | Component Patched | Attention head (L, H) or MLP layer L | Categorical: 150 components |
| **IV** | Causal Task Rung | Pearl's hierarchy level | Rung 1/2/3 |
| **DV** | Causal Accuracy | Task correctness | Continuous: [0, 1] |
| **DV** | Performance Drop | Accuracy change from patching | Δ accuracy |
| **DV** | Component Importance | Effect size of ablation | Cohen's d |
| **Control** | Model Architecture | LLM family/size | GPT-2, LLaMA-7B, GPT-3.5 |
| **Control** | Question Complexity | Causal graph size | 2-4 node graphs |

### 1.3 Causal Mechanism

**Chain:** Activation Patching → Component Isolation → Performance Change → Circuit Identification → Failure Prediction

**Evidence for Links:**
- Patching → Isolation: HIGH (Li et al. 2025 - Causal Tracing in VLMs)
- Component → Performance: HIGH (pyvene library, mechanistic interpretability literature)
- Differential Rungs → Circuits: LOW (novel empirical question to be tested)
- Circuits → Prediction: MEDIUM (Parry et al. 2025 - MechIR in IR domain)

**Key Tension:** Does abstract causal reasoning exhibit localized processing (like concrete tasks) or distributed processing that resists component-level decomposition?

### 1.4 Key Assumptions

1. Activation patching effects are interpretable (testable via pure ablation comparison)
2. CLadder + Lee et al. benchmarks adequately sample causal reasoning (testable via cross-benchmark consistency)
3. Performance variance is low (testable via random seed replication)
4. Components analyzable independently despite residual connections (mitigated by activation patching)

**Note:** Pilot phase empirically validates assumptions 1 & 4 before full-scale experiments.

### 1.5 Scope & Boundaries

**In Scope:**
- Transformer LLMs (GPT-2, LLaMA, Claude)
- Explicit Pearl rung tasks (CLadder, Lee et al.)
- Models with activation access
- English-language prompts
- Static evaluation

**Out of Scope:**
- Non-transformer architectures
- Implicit causal reasoning
- API-only models (no activation access)
- Multi-turn conversations
- Non-English languages

**Limitations:**
- May find distributed processing (null model enables rigorous reporting)
- Residual connections complicate attribution (mitigated but not eliminated)
- Compute-intensive (10-50 GPU-hours per model)
- Cross-domain transfer from concrete tasks unproven

### 1.6 Testable Predictions

**P1 (Primary):** Task-relevant component patches cause performance drops significantly larger than random patches (d > 0.5, p < 0.01 for ≥20% of components)

**P2 (Secondary):** Component importance rankings differ across Pearl rungs (Spearman ρ < 0.6, p < 0.05 for Rung 1 vs. 3)

**P3 (Tertiary):** Circuit analysis predicts held-out task performance above chance (AUC > 0.65, p < 0.05)

**Falsification Criteria:**
- No localization (d < 0.3 for >80% of components)
- No rung differentiation (ρ > 0.8 for all rung pairs)
- No predictive power (AUC < 0.55)
- Pilot phase failure (no localization in A→B→C tasks)

### 1.7 SOTA Baseline

**Baseline:** CLadder Benchmark (Static Evaluation)
- Best LLM: 57.6% accuracy
- Output: Aggregate accuracy per rung

**Proposed Method:** Causal Mechanistic Tracing
- Output: Component Causal Map, Localization Score, Rung-Specific Circuits, Failure Mode Classification

**Key Improvements:**
- Diagnostic depth: Component-level attribution (vs. aggregate only)
- Predictive power: AUC 0.65-0.75 for failure prediction (vs. 0.50 baseline)
- Actionability: "Target components X, Y" (vs. "model fails")

### 1.8 Statistical Verification

**Pilot Phase (Month 1):**
- Tasks: A→B→C transitive reasoning
- Models: GPT-2-small, LLaMA-7B
- Decision gate: d > 0.1, p < 0.05

**Full Evaluation (Months 2-3):**
- Dataset: CLadder (~1000 tasks) + Lee et al. (500 tasks)
- Models: GPT-2-small, LLaMA-7B, GPT-3.5-turbo
- Components: 150 per model, 3 seeds
- Compute: 30-50 GPU-hours per model

**Analysis:**
- P1: Two-sample t-test with Bonferroni correction
- P2: Spearman correlation + permutation test
- P3: Logistic regression + 5-fold CV, AUC-ROC

---

## 2. Contribution Summary

**Theoretical:**
Establishes that diagnostic evaluation of reasoning capabilities requires mechanistic component-level analysis, not just aggregate performance metrics. First formal framework integrating mechanistic interpretability with structured causal reasoning evaluation.

**Methodological:**
Introduces "Causal Mechanistic Tracing" protocol combining:
1. Rung-stratified tasks (Pearl's hierarchy)
2. Activation patching (component isolation)
3. Null model comparison (rigorous validation)
4. Data-driven component identification (no predefined patterns)
5. Circuit-based failure prediction (diagnostic precision)

**Practical:**
Provides actionable model development guidance: identify which components to enhance for better causal reasoning. Enables targeted interventions (specific attention heads/layers) rather than wholesale retraining. Applicable to any LLM and causal reasoning benchmark.

---

## 3. Key Related Work

| Work | Type | Relation |
|------|------|----------|
| Lee et al. (2025) - Benchmarking LLM Causal Reasoning | Paper | **Foundation** - Establishes evaluation gap (57.6%, no diagnostics) |
| Li et al. (2025) - Causal Tracing in VLMs | Paper | **Methodology** - Provides causal tracing technique |
| Parry et al. (2025) - MechIR | Paper | **Methodology** - Task-specific mechanistic framework template |
| Do et al. (2025) - CaSE | Paper | **Inspiration** - Stepwise evaluation approach |
| CLadder (causalNLP) | Dataset | **Foundation** - Rung-stratified causal tasks |
| pyvene (Stanford) | Tool | **Methodology** - Activation patching implementation |
| vedantpalit - Causal Tracing BLIP | Code | **Methodology** - Reference causal tracing implementation |
| Neuroscience lesion studies | Domain | **Inspiration** - Systematic ablation methodology |

**Differentiation:**
- Li et al.: VLMs + object recognition → This work: LLMs + abstract causal reasoning
- Parry et al.: IR tasks → This work: Causal reasoning evaluation
- Do et al.: Stepwise (not mechanistic) → This work: Component-level mechanistic

**Novel Integration:** First work combining mechanistic interpretability with rung-stratified causal evaluation.

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):** Causal reasoning in LLMs exhibits measurable component-level localization above random baseline
- Verification: Pilot phase on A→B→C tasks, decision gate d > 0.1

**SH2 (Mechanism):** Different Pearl rungs engage different computational circuits
- Verification: Component importance ranking comparison across rungs (Spearman ρ < 0.6)

**SH3 (Comparison):** Circuit-based diagnosis outperforms aggregate evaluation in predicting held-out failures
- Verification: AUC comparison (circuit-based vs. random predictor, DeLong test p < 0.05)

### Readiness Checklist

- ✅ Testable predictions defined (P1, P2, P3)
- ✅ Falsification criteria specified
- ✅ Variables operationalized
- ✅ Statistical verification plan complete
- ✅ Null model baseline included
- ✅ Pilot phase with decision gate
- ✅ Assumptions explicitly stated and testable
- ✅ SOTA baseline comparison defined
- ✅ Compute requirements estimated (30-50 GPU-hours)
- ✅ Timeline projected (2-3 months)

### Open Questions for Phase 2B

1. **Exact activation patching protocol:** Should we use mean-difference patching, zero-ablation, or noise-corrupted patching? (Requires literature review of pyvene best practices)

2. **Component selection strategy:** Should we test all components or use iterative pruning (test layers first, then drill down to heads)? (Trade-off: thoroughness vs. compute)

3. **Localization score threshold:** What localization score value (0-1 scale) qualifies as "meaningful localization"? (Requires pilot data to calibrate)

4. **Cross-model comparison:** Should we prioritize within-family comparisons (GPT-2 vs. GPT-3) or cross-family (GPT vs. LLaMA)? (Depends on generalization goals)

5. **Failure mode taxonomy:** Should we pre-define failure categories (e.g., "intervention failure") or discover them data-driven via clustering? (Methodological choice)

---

**Document Status:** ✅ READY FOR PHASE 2B

**Next Phase:** Phase 2B - Verification Planning
- Decompose main hypothesis into sub-hypotheses (SH1-SH3)
- Design verification experiments for each sub-hypothesis
- Establish priority order and dependencies
- Define success criteria and validation protocols

---

*Generated by YouRA Phase 2A-Extended Workflow (YOLO Mode)*
*Date: 2026-02-06*
*Processing Time: ~15 minutes*

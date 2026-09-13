# Verification Plan: Conditional Basin Recovery for Neural-Symbolic Constraint Integration

**Date:** 2026-05-12
**Hypothesis ID:** H-ConditionalBasinRecovery-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under locally factorizable constraint systems with explicit graph structure (SAT, typed CSPs), if a two-stage neural-symbolic architecture combines learned constraint-graph message-passing (Stage 1) with temperature-annealed Gumbel-softmax refinement (Stage 2), then discrete violation rates reduce to <2% with ≥2× computational throughput over rejection sampling, because Stage 1 places solutions in recoverable basins (d/n < 0.15, H > 2.5) where gradient-discrete alignment (cosine > 0.7) enables Stage 2 local refinement to converge to discrete satisfying assignments.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in discrete violation rates or computational throughput between the two-stage constraint-integrated architecture and standard generate-then-verify rejection sampling baselines when both are evaluated under equal hardware and batch constraints.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Multi-tier validation suite (standard) | Small SAT instances enable exhaustive Basin Recovery analysis; HumanEval tests real-world code synthesis impact |
| **Model** | Two-stage neural-symbolic architecture | Architecture directly implements the causal mechanism: learned heuristics for basin entry + annealed refinement for local convergence |

**Dataset Details:**
- Source: Combination of synthetic (3-SAT generators) and real-world (HumanEval-Contracts)
- Path: To be generated: Random 3-SAT (≤15 vars for exhaustive, 50-200 vars for scalability), HumanEval with formal contracts

**Model Details:**
- Type: Custom (GNN Stage 1 + Gumbel-softmax Stage 2)
- Source: Novel combination of NeuroSAT-style message-passing and temperature-annealed refinement

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| LLM + Post-hoc Verification | 60-75% contract satisfaction on first attempt | HumanEval, MBPP with formal specs |
| SATNet | 99.7% discrete validity on Sudoku (9×9) | Small structured constraint problems |
| NeuroSAT | 30% search reduction on industrial SAT instances | Random and structured SAT benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Stage 1 errors are locally correctable - violations are diffuse and within recoverable Hamming distance | Prof. Pax argued structured near-solutions from message-passing create favorable basin entry conditions vs. random violations | Stage 2 refinement degrades to random search if violations are concentrated or distant from satisfying assignments |
| A2 | Gradient-discrete alignment remains stable during annealing process | Gumbel-softmax annealing maintains differentiability while introducing discretization; cosine similarity metric quantifies alignment | If gradients decouple from discrete improvement at low temperatures, convergence fails despite basin proximity |
| A3 | Constraint systems have locally factorizable structure enabling graph-based message passing | Prof. Pax scoped applicability to SAT, typed CSPs, finite-domain constraints with low-order interactions | Method fails on globally coupled constraints or quantified FOL without local structure |
| A4 | Compositional amplification arises from covariance reduction in shared representations, not emergent reasoning | Prof. Rex distinguished covariance shaping from true compositional deduction; Dr. Ally scoped claims accordingly | If independent vs. coupled contract tests show no amplification even for independent cases, shared representations provide no benefit |
| A5 | Throughput advantages persist under batched rejection parallelism on modern accelerators | Gradient refinement parallelizes across variables; rejection sampling parallelizes across samples - architecture comparison needed | If batched rejection achieves similar throughput to integration under matched hardware, novelty reduces to sample efficiency only |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** Conditional Basin Recovery (CBR) framework characterizing geometry of constraint-satisfiability basins in neural parameter space.

**Key Innovation:** Mechanistic theory of when continuous optimization can solve discrete problems, with measurable phase boundaries (d/n, entropy, gradient alignment).

**Differentiation:**
- **vs. SATNet (Wang et al., 2019):** SATNet used single-stage relaxation limited to small problems; we combine learned heuristics (Stage 1) with local refinement (Stage 2) and provide basin geometry theory explaining when/why it works
- **vs. NeuroSAT (Selsam et al., 2019):** NeuroSAT only learned search heuristics without refinement; we add gradient-based local refinement and characterize the basin recovery conditions enabling the combination
- **vs. Post-hoc verification:** Rejection sampling wastes computation and provides no gradient signal; we integrate constraints during generation with measurable computational advantage (≥2× throughput)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Basin Entry Heterogeneity**

**Statement**: Under locally factorizable constraint systems (SAT, typed CSPs), Stage 1 learned constraint-graph message-passing generates structured near-solutions with measurable heterogeneity in violation patterns (d/n range > 0.20, entropy H > 2.0) sufficient to support basin recovery stratification.

**Rationale** (2-3 sentences):
Validates that learned heuristics produce diverse basin entry conditions rather than uniform violations. This heterogeneity is essential for testing the recovery phase transition hypothesis. Without variation in d/n and entropy, we cannot empirically validate basin boundaries.

**Variables** (from Phase 2A):
- Independent: Constraint family (SAT, typed CSP), problem difficulty (clause-to-variable ratio)
- Dependent: d/n distribution statistics, violation entropy H, heterogeneity range
- Controlled: Stage 1 architecture (GNN message-passing), training data distribution

**Verification Protocol** (3-5 steps):
1. Train Stage 1 GNN on random 3-SAT and typed CSP instances until convergence
2. Generate 1000+ near-solutions across constraint families and difficulty levels
3. Compute d/n and entropy H for each generated solution
4. Measure distribution statistics: range, variance, quartile boundaries
5. Verify d/n range > 0.20 and entropy range supports stratification analysis

**Success Criteria** (PoC: Direction-based):
- Primary: d/n distribution exhibits range > 0.20 (e.g., Q1=0.05, Q3=0.30)
- Secondary: Entropy H distribution exhibits range > 2.0 with sufficient density

**Failure Response**:
- IF fails: EXPLORE alternative Stage 1 architectures or constraint representations to increase violation pattern diversity

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 1.6 (Testable Predictions P1 - basin recovery stratification requires variation)

---

---
**H-M1: Stage 1 Structured Near-Solutions**

**Statement**: Stage 1 learned message-passing on constraint graphs generates structured near-solutions satisfying >85% of constraints, because GNN expressiveness enables learning DPLL-like search strategies as demonstrated by NeuroSAT's 30% search reduction on industrial instances.

**Rationale**:
Validates that Stage 1 achieves the pre-conditioning requirement for Stage 2 effectiveness. >85% clause satisfaction is the hypothesized threshold for recoverable basin entry. This establishes the foundation for the two-stage mechanism.

**Variables**:
- Independent: Constraint family, problem difficulty, Stage 1 architecture configuration
- Dependent: Clause satisfaction percentage, constraint violation count
- Controlled: Training procedure, GNN depth/width, message-passing iterations

**Verification Protocol**:
1. Train Stage 1 GNN with NeuroSAT-style message-passing on constraint graphs
2. Evaluate on held-out SAT and CSP instances across difficulty levels
3. Measure clause satisfaction percentage for generated near-solutions
4. Compare against random baseline and pure encoder baseline
5. Verify >85% satisfaction threshold is met consistently

**Success Criteria**:
- Primary: Mean clause satisfaction >85% across constraint families
- Secondary: Satisfaction rate significantly exceeds random baseline (p < 0.01)

**Failure Response**:
- IF fails: PIVOT to alternative learned heuristic architectures or adjust training objectives

**Dependencies**: H-E1 (requires heterogeneous near-solutions exist)

**Source**: Phase 2A Section 1.3 Causal Step 1 (Learned heuristics generate structured near-solutions)

---

---
**H-M2: Basin Entry Criteria Satisfaction**

**Statement**: Stage 1 outputs satisfy basin entry criteria (d/n < 0.15, violation entropy H > 2.5), because structured message-passing creates diffuse violation patterns with >85% clause satisfaction, enabling Stage 2 local refinement feasibility.

**Rationale**:
Tests whether Stage 1 places solutions in the hypothesized recoverable basin region. This is the critical link between learned heuristics and refinement effectiveness. Basin entry criteria determine whether Stage 2 can succeed.

**Variables**:
- Independent: Stage 1 architecture, constraint difficulty
- Dependent: Normalized Hamming distance d/n, violation entropy H
- Controlled: Constraint family, instance size, satisfaction threshold

**Verification Protocol**:
1. Generate near-solutions using trained Stage 1 from H-M1
2. For solutions with >85% clause satisfaction, compute d/n and H
3. Measure proportion meeting basin criteria (d/n < 0.15, H > 2.5)
4. Stratify by constraint difficulty and compare against basin boundary
5. Verify sufficient density of solutions in recoverable basin region

**Success Criteria**:
- Primary: ≥60% of >85%-satisfied solutions meet basin criteria (d/n < 0.15, H > 2.5)
- Secondary: Basin entry rate increases with higher satisfaction percentages

**Failure Response**:
- IF fails: EXPLORE modifications to Stage 1 loss function or architecture to bias toward diffuse violations

**Dependencies**: H-M1 (requires >85% clause satisfaction established)

**Source**: Phase 2A Section 1.3 Causal Step 2 (Basin entry criteria enable Stage 2 recovery)

---

---
**H-M3: Gradient-Discrete Alignment Maintenance**

**Statement**: Temperature-annealed Gumbel-softmax in Stage 2 maintains gradient-discrete alignment (cosine > 0.7) during refinement, because annealing addresses train-test mismatch by gradually introducing discretization while ensuring continuous gradients correlate with discrete improvement directions.

**Rationale**:
Validates the mechanism by which continuous optimization can solve discrete problems. Gradient-discrete alignment is hypothesized to be a better predictor of recovery than Hamming distance alone. This tests the theoretical foundation of the approach.

**Variables**:
- Independent: Annealing schedule (linear, exponential, cosine), temperature range
- Dependent: Gradient-discrete cosine similarity, recovery success rate
- Controlled: Stage 1 initialization quality (d/n, H), constraint instance

**Verification Protocol**:
1. Initialize Stage 2 from Stage 1 outputs meeting basin criteria
2. During annealing, measure cosine similarity between Gumbel-softmax gradients and optimal single-variable flip directions
3. Track alignment throughout refinement process across temperature schedule
4. Stratify recovery outcomes by alignment levels
5. Test prediction: alignment > 0.7 predicts >90% recovery even at d/n = 0.20

**Success Criteria**:
- Primary: Gradient-discrete alignment predicts recovery better than d/n alone (AUC improvement)
- Secondary: Recovery >90% when alignment > 0.7, <50% when alignment < 0.4

**Failure Response**:
- IF fails: EXPLORE alternative annealing schedules or gradient-based refinement methods

**Dependencies**: H-M2 (requires basin entry criteria satisfied)

**Source**: Phase 2A Section 1.3 Causal Step 3 (Gradient alignment enables continuous-to-discrete solution)

---

---
**H-M4: Local Convergence in Recoverable Basin**

**Statement**: Stage 2 converges to discrete satisfying assignment through local gradient-based search in recoverable basin, achieving >95% recovery probability when basin criteria met (d/n < 0.15, H > 2.5, alignment > 0.7), because contraction mapping theory supports local convergence under these conditions.

**Rationale**:
Tests the complete two-stage mechanism end-to-end. This validates the basin recovery phase transition hypothesis: sharp boundary at d/n ≈ 0.15 with >95% recovery inside, <20% outside. Demonstrates the system achieves the target <2% violation rate.

**Variables**:
- Independent: Initial d/n, entropy H, gradient alignment
- Dependent: Recovery probability, discrete violation rate, convergence steps
- Controlled: Annealing schedule, Stage 2 optimization hyperparameters

**Verification Protocol**:
1. Use controlled degradation: from satisfying assignments, flip k variables to induce specific d/n levels
2. Run Stage 2 refinement from degraded states across d/n spectrum
3. Measure recovery probability as function of (d/n, H, alignment)
4. Fit logistic curve to identify phase transition point d₀ and sharpness β
5. Verify sharp transition: >95% at d/n < 0.15, <20% at d/n > 0.30

**Success Criteria**:
- Primary: Basin recovery exhibits sharp phase transition with d₀ ≈ 0.15 ± 0.03, β > 50
- Secondary: Discrete violation rate <2% on HumanEval-Contracts when basin entry criteria met

**Failure Response**:
- IF fails: PIVOT to alternative refinement mechanisms or recalibrate basin boundary thresholds

**Dependencies**: H-M3 (requires gradient alignment maintained)

**Source**: Phase 2A Section 1.3 Causal Step 4 (Local convergence to discrete solutions)

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | d/n range > 0.20, entropy range > 2.0 | Explore alternative Stage 1 architectures |
| H-M1 | MUST_WORK | Mean clause satisfaction >85% | Pivot to alternative learned heuristics |
| H-M2 | MUST_WORK | ≥60% of solutions meet basin criteria | Explore Stage 1 loss modifications |
| H-M3 | SHOULD_WORK | Alignment predicts recovery better than d/n alone | Explore alternative annealing schedules |
| H-M4 | SHOULD_WORK | Sharp phase transition at d₀ ≈ 0.15 | Pivot or recalibrate thresholds |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1, H-M1 | 2-3 weeks |
| Phase 2: Basin Entry | H-M2 | 1-2 weeks |
| Phase 3: Refinement Mechanism | H-M3, H-M4 | 2-3 weeks |

**Total Duration:** 5-8 weeks

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-05-12*

# Verification Plan: Multi-Objective Pareto Trade-offs in Finite-Compute Data Attribution

**Date:** 2026-03-26
**Hypothesis ID:** H-AttributionPareto-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under finite-compute constraints (<=100 gradient-equivalent operations), if we compare multiple data attribution methods (TRAK, TracIn, IF, FastIF) across standardized quality dimensions, then non-degenerate Pareto trade-offs emerge across rank preservation, magnitude fidelity, and normalized stability, because non-convex deep learning geometry creates structural metric decoupling that does not exist in convex settings.

### 1.2 Alternative Hypothesis (H0)
All three attribution quality metrics (rank correlation, magnitude correlation, normalized stability) are monotone functions of a single approximation error norm ||phi_hat - phi||_2, and any observed trade-offs are finite-sample artifacts that disappear as compute increases.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | CIFAR-10 (Track A) + MNLI (Track A NLP) (standard) | Standard benchmarks with manageable size for LOO ground truth estimation; prior attribution work uses these datasets |
| **Model** | ResNet-18 (vision) + BERT-base (NLP) | Small enough for LOO retraining, large enough to exhibit non-convex deep network behavior |

**Dataset Details:**
- Source: torchvision, HuggingFace datasets
- Path: Loaded via standard APIs

**Model Details:**
- Type: CNN + Transformer
- Source: torchvision, HuggingFace transformers

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| TRAK | 0.7-0.9 Spearman correlation with LOO on image classification | CIFAR-10, ImageNet subsets |
| Influence Functions | Theoretically optimal but fragile in practice | Various classification tasks |
| TracIn | Competitive with IF on some benchmarks | BERT fine-tuning |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | LOO influence can be meaningfully estimated as E_xi[theta^(-i) - theta] over training randomness | Standard definition used across influence function literature | Target functional undefined; all comparisons meaningless |
| A2 | Basin variance does not completely dominate LOO effects in deep networks | TRAK achieves 0.7-0.9 correlation, suggesting signal exceeds noise | Cannot distinguish method performance from target stochasticity |
| A3 | The three metrics (rank, magnitude, stability) capture genuinely different aspects of attribution quality | Used in different downstream applications (debugging, valuation, auditing) | Multi-objective framing collapses to single-objective |
| A4 | Compute budget can be meaningfully normalized via gradient-equivalent operations | Standard primitive in attribution literature (HVPs, gradient computations) | Cannot compare methods at matched compute |
| A5 | R=10 retraining seeds provides sufficient statistical power for variance estimation | Standard practice in LOO validation studies | Variance-of-variance artifacts may mask true trade-offs |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First rigorous multi-objective Pareto characterization of data attribution methods connecting method design choices to downstream use case requirements.

**Key Innovation:** Testing whether attribution is fundamentally a single well-posed problem or a family of related but distinct problems (rank vs magnitude vs stability).

**Differentiation from Prior Work:**
- TRAK (Park et al. 2023): Reports single-metric comparisons (LDS); we characterize multi-metric Pareto structure
- Basu et al. (2020): Shows when IF fails; we characterize trade-offs across multiple methods at fixed compute
- DataInf (Kwon et al. 2023): Optimizes for LoRA efficiency; we compare all methods under unified framework

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | BLOCKED |
| H-M2 | Mechanism | MUST_WORK | H-M1 | BLOCKED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | BLOCKED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Pareto Trade-offs Exist in Finite-Compute Attribution

**Statement**: Under finite-compute constraints (<=100 gradient-equivalent operations), if we compare multiple data attribution methods across standardized quality metrics, then at least one method pair exhibits statistically significant metric crossings (Method A > B on rho_r but A < B on rho_m), because different method designs inherently optimize different quality dimensions.

**Rationale**: This is the foundational existence claim. If no Pareto trade-offs exist, all methods would show universal dominance or parallel performance curves, and multi-objective optimization would be unnecessary. Proving existence justifies the entire research program.

**Variables**:
- Independent: Attribution method (TRAK, TracIn, IF, FastIF), Compute budget (10-100 gradient-equivalents)
- Dependent: Rank preservation (rho_r), Magnitude fidelity (rho_m), Normalized stability (S)
- Controlled: Dataset (CIFAR-10), Model (ResNet-18), Seeds (R=10 for LOO, 3 for method variance)

**Verification Protocol**:
1. Train ResNet-18 on CIFAR-10 with 5000 training examples and compute LOO ground truth via 10 retrains.
2. Run all four attribution methods at each of 5 compute budget levels (10, 25, 50, 75, 100).
3. Compute three metrics (rho_r, rho_m, S) for each method-budget combination.
4. Construct Pareto fronts at each budget level and test for non-dominance via bootstrap CIs (1000 resamples).
5. Identify method pairs with CI-separated metric crossings at >=2 compute levels.

**Success Criteria** (PoC: Direction-based):
- Primary: >=1 method pair shows CI-separated metric crossings at >=2 compute levels
- Secondary: Pareto front contains >=2 non-dominated methods at majority of budget levels

**Failure Response**:
- IF fails: ABANDON (if all methods show universal dominance, multi-objective framing is invalid)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A SH1 (Existence), Prediction P2

---

#### H-M1: Convex Baseline Establishes Metric Coupling

**Statement**: In convex settings (logistic regression), if we compute attribution quality metrics at varying compute budgets, then cross-metric partial correlations will be >= 0.95, because convex optimization has a unique minimum with closed-form LOO influence.

**Rationale**: This establishes the baseline expectation. Convex coupling proves that metrics CAN be correlated when geometry is simple, making deep network decoupling meaningful by contrast.

**Variables**:
- Independent: Compute budget (10-100 gradient-equivalents), Attribution approximation method
- Dependent: Cross-metric partial correlation corr(rho_r, rho_m | budget)
- Controlled: Logistic regression on CIFAR-10 features, Fixed regularization

**Verification Protocol**:
1. Extract features from pre-trained ResNet-18 and train logistic regression on CIFAR-10.
2. Compute exact LOO influence (closed-form solution available for convex models).
3. Run attribution approximations at varying compute budgets.
4. Compute cross-metric partial correlations at each budget level.
5. Verify correlation >= 0.95 across all budget levels.

**Success Criteria** (PoC: Direction-based):
- Primary: corr(rho_r, rho_m | budget) >= 0.95 at all 5 compute levels
- Secondary: R^2 from single-error-axis regression >= 0.95

**Failure Response**:
- IF fails (correlation < 0.90): PIVOT (metrics are definitionally inconsistent; redefine metrics)

**Dependencies**: H-E1 (existence must be established first)

**Source**: Phase 2A Causal Step 1, Prediction P1

---

#### H-M2: Deep Network Geometry Decouples Metrics

**Statement**: In non-convex deep networks (ResNet-18), if we regress attribution quality metrics on approximation error norm ||phi_hat - phi||_2, then R^2 drops from ~1.0 (convex baseline) to <0.80, because loss landscape geometry creates multiple optimization paths that differently weight quality dimensions.

**Rationale**: This tests the mechanistic claim that decoupling is structural, not an artifact of approximation quality. If R^2 remains high, trade-offs would reflect convergence rates, not fundamental incompatibilities.

**Variables**:
- Independent: Model regime (convex vs deep), Approximation error norm ||phi_hat - phi||_2
- Dependent: R^2 from single-axis metric regression
- Controlled: Same attribution methods, Same compute normalization

**Verification Protocol**:
1. Use convex R^2 values from H-M1 as baseline.
2. Train ResNet-18 on CIFAR-10 and compute LOO ground truth via 10 retrains.
3. For each method-budget pair, compute approximation error norm and all three metrics.
4. Fit linear regression of each metric on approximation error norm.
5. Compare R^2 values between convex and deep regimes.

**Success Criteria** (PoC: Direction-based):
- Primary: R^2_deep < 0.80 for at least one metric (vs R^2_convex >= 0.95)
- Secondary: Cross-metric correlations drop below 0.85 in deep regime

**Failure Response**:
- IF fails (R^2 >= 0.95 in deep): EXPLORE (single-error-axis model holds; trade-offs are artifacts)

**Dependencies**: H-M1 (convex baseline must be established)

**Source**: Phase 2A Causal Step 2, Prediction P3

---

#### H-M3: Method Design Creates Irreducible Trade-offs

**Statement**: In deep networks, if we compare methods with different design paradigms (random projection vs HVP iteration vs gradient similarity), then methods will show persistent relative advantages on different metrics across compute levels, because design choices embed different bias-variance trade-offs.

**Rationale**: This connects trade-offs to method design, providing actionable guidance. If trade-offs are method-specific, practitioners can choose methods based on their use case (rank for debugging, magnitude for valuation, stability for auditing).

**Variables**:
- Independent: Method design paradigm (TRAK=projection, IF=HVP, TracIn=gradient similarity)
- Dependent: Relative metric rankings across compute levels, Top-k disagreement (Jaccard)
- Controlled: Same deep model, Same compute normalization

**Verification Protocol**:
1. Use method outputs from H-E1 experiments.
2. For each compute level, rank methods separately on each metric.
3. Identify persistent patterns (e.g., TRAK always best on rho_r, IF always best on S).
4. Compute top-k Jaccard similarity between methods' influential example sets.
5. Perform retraining-without-top-k experiment to measure downstream accuracy differences.

**Success Criteria** (PoC: Direction-based):
- Primary: Top-k Jaccard < 0.70 (>30% disagreement between methods)
- Secondary: Retraining experiments show t-test p < 0.05 on downstream accuracy differences

**Failure Response**:
- IF fails (Jaccard >= 0.90): EXPLORE (methods agree on influential examples despite metric differences)

**Dependencies**: H-M2 (decoupling must be established)

**Source**: Phase 2A Causal Step 3, Prediction P4

---

## 2.5 Risk Analysis

### Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 | All (H-E1, H-M1-3) | Critical |
| R2 | A2 | H-E1, H-M2 | High |
| R3 | A3 | H-E1, H-M3 | Medium |
| R4 | A4 | All | Medium |
| R5 | A5 | H-M1, H-M2 | Low |

### Risk Details & Mitigation Strategies

**Risk R1: Target Functional Undefined**
- **Source Assumption:** A1 - LOO influence can be meaningfully estimated as E_xi[theta^(-i) - theta]
- **Description:** If training randomness (basin variance) makes the target functional unstable, all influence estimates become noise and comparisons are meaningless.
- **Affected Hypotheses:** All (H-E1, H-M1, H-M2, H-M3)
- **Severity:** Critical
- **Mitigation Strategy:**
  1. **Prevention:** Run basin variance check FIRST: compute ||theta_xi - theta_xi'|| vs ||theta^(-i) - theta||
  2. **Detection:** If basin variance > 50% of LOO variance, target is ill-defined
  3. **Response:**
     - PIVOT: Switch to relative rankings only (Spearman, not Pearson)
     - SCOPE: Restrict to lower-variance models (smaller networks)
     - ABORT: If basin dominates even in small models, fundamental limitation
- **Early Warning Indicators:**
  - Large variance across random seeds in LOO estimates
  - Poor correlation between different LOO approximation methods

**Risk R2: Basin Variance Dominates Signal**
- **Source Assumption:** A2 - Basin variance does not completely dominate LOO effects in deep networks
- **Description:** Even if target is defined, basin-to-basin variance may make method differences undetectable.
- **Affected Hypotheses:** H-E1, H-M2
- **Severity:** High
- **Mitigation Strategy:**
  1. **Prevention:** Use sigma_LOO normalization (inflation ratio S = Var_runs / sigma_LOO^2)
  2. **Detection:** If all methods have S > 2.0 (variance inflation > 2x target), signal weak
  3. **Response:**
     - PIVOT: Increase R from 10 to 20 retrains for tighter variance estimates
     - SCOPE: Focus on rank-based metrics only (robust to magnitude noise)
- **Early Warning Indicators:**
  - Inflation ratios S >> 1 across all methods
  - Bootstrap CIs too wide to detect crossings

**Risk R3: Metrics Not Orthogonal**
- **Source Assumption:** A3 - The three metrics capture genuinely different aspects of attribution quality
- **Description:** If rank, magnitude, and stability are highly correlated even in deep networks, multi-objective framing is unnecessary.
- **Affected Hypotheses:** H-E1, H-M3
- **Severity:** Medium
- **Mitigation Strategy:**
  1. **Prevention:** Measure cross-metric correlations early (before full experiments)
  2. **Detection:** If corr(rho_r, rho_m) > 0.95 and corr(rho_m, S) > 0.95 in deep networks
  3. **Response:**
     - PIVOT: Redefine metrics to capture orthogonal aspects (PCA on metric space)
     - SCOPE: Focus on most discriminative metric pair
- **Early Warning Indicators:**
  - Cross-metric correlations > 0.90 in pilot experiments
  - Single PCA component explains > 90% of metric variance

**Risk R4: Compute Normalization Fails**
- **Source Assumption:** A4 - Compute budget can be meaningfully normalized via gradient-equivalent operations
- **Description:** If methods have incomparable computational primitives, matched-compute comparison is invalid.
- **Affected Hypotheses:** All
- **Severity:** Medium
- **Mitigation Strategy:**
  1. **Prevention:** Verify gradient-equivalent mapping for each method before experiments
  2. **Detection:** If wall-clock time varies > 5x at "matched" compute, normalization broken
  3. **Response:**
     - PIVOT: Report Pareto fronts in wall-clock time instead of gradient-equivalents
     - SCOPE: Compare only within method families (all HVP-based, all projection-based)
- **Early Warning Indicators:**
  - Large wall-clock discrepancies at matched gradient-equivalents
  - Memory usage varies dramatically across methods

**Risk R5: Insufficient Statistical Power**
- **Source Assumption:** A5 - R=10 retraining seeds provides sufficient statistical power for variance estimation
- **Description:** If R=10 is too few, variance estimates are unstable and bootstrap CIs unreliable.
- **Affected Hypotheses:** H-M1, H-M2
- **Severity:** Low
- **Mitigation Strategy:**
  1. **Prevention:** Run variance-of-variance check with R=10 subsamples
  2. **Detection:** If 95% CI on sigma_LOO spans > 50% of point estimate, R too low
  3. **Response:**
     - PIVOT: Increase to R=20 (double computation but halve uncertainty)
     - SCOPE: Use asymptotic approximations instead of bootstrap
- **Early Warning Indicators:**
  - High variance in bootstrap CI widths across examples
  - Instability in Pareto front composition across bootstrap replicates

### Risk Summary

| ID | Risk | Source | Severity | Primary Mitigation |
|----|------|--------|----------|-------------------|
| R1 | Target undefined | A1 | Critical | Basin check FIRST |
| R2 | Basin dominates | A2 | High | sigma_LOO normalization |
| R3 | Metrics correlated | A3 | Medium | Cross-metric check early |
| R4 | Compute mismatch | A4 | Medium | Wall-clock fallback |
| R5 | Low power | A5 | Low | Increase R if needed |

**Risk Distribution:** Critical: 1, High: 1, Medium: 2, Low: 1

---

## 3. Execution

### 3.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────────────┐
    │  H-E1: Pareto Trade-offs Exist          │
    │  Gate: MUST_WORK                        │
    │  Prerequisites: None                    │
    └─────────────────────────────────────────┘
                      │
                      ▼
[Level 1 - Mechanism Step 1]
    ┌─────────────────────────────────────────┐
    │  H-M1: Convex Baseline Coupling         │
    │  Gate: MUST_WORK                        │
    │  Prerequisites: H-E1                    │
    └─────────────────────────────────────────┘
                      │
                      ▼
[Level 2 - Mechanism Step 2]
    ┌─────────────────────────────────────────┐
    │  H-M2: Deep Network Decoupling          │
    │  Gate: MUST_WORK                        │
    │  Prerequisites: H-M1                    │
    └─────────────────────────────────────────┘
                      │
                      ▼
[Level 3 - Mechanism Step 3]
    ┌─────────────────────────────────────────┐
    │  H-M3: Method Design Trade-offs         │
    │  Gate: SHOULD_WORK                      │
    │  Prerequisites: H-M2                    │
    └─────────────────────────────────────────┘
                      │
                      ▼
                 [COMPLETE]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Path Length: 4 hypotheses (sequential)
═══════════════════════════════════════════════════════════
```

### 3.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|-----------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | Foundation |
| 1 | H-M1 | H-E1 | MUST_WORK | Mechanism |
| 2 | H-M2 | H-M1 | MUST_WORK | Mechanism |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Mechanism |

### 3.3 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | >=1 method pair with CI-separated metric crossings at >=2 compute levels | ABANDON: Multi-objective framing invalid |
| H-M1 | MUST_WORK | corr(rho_r, rho_m \| budget) >= 0.95 at all compute levels | PIVOT: Redefine metrics |
| H-M2 | MUST_WORK | R^2_deep < 0.80 for at least one metric | EXPLORE: Single-error-axis model holds |
| H-M3 | SHOULD_WORK | Top-k Jaccard < 0.70 (>30% disagreement) | EXPLORE: Methods agree on influential examples |

### 3.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ W1-2       │ W3-4       │ W5         │ W6
─────────────────────┼────────────┼────────────┼────────────┼────────────
PHASE 1: Foundation
  H-E1 (Existence)   │ ██████████ │            │            │
  [Gate 1: MUST]     │            │ ◆          │            │
─────────────────────┼────────────┼────────────┼────────────┼────────────
PHASE 2: Mechanisms
  H-M1 (Convex)      │            │ ██████████ │            │
  H-M2 (Decoupling)  │            │            │ ██████████ │
  H-M3 (Design)      │            │            │            │ ██████████
  [Gate 2: MUST]     │            │            │            │          ◆
═══════════════════════════════════════════════════════════════════════════
Legend: ██████████ = Active work (2 weeks) | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════════════
```

### 3.5 Critical Path Analysis

| Metric | Value |
|--------|-------|
| Critical Path | H-E1 → H-M1 → H-M2 → H-M3 |
| Total Duration | 6 weeks |
| Formula | 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) |
| Slack Available | 0 weeks (fully sequential) |

### 3.6 Resource Summary

| Resource | Allocation |
|----------|------------|
| Total Hypotheses | 4 |
| Existence (H-E) | 1 |
| Mechanism (H-M) | 3 |
| Condition (H-C) | 0 |
| Verification Phases | 2 |
| Total Duration | 6 weeks |
| Execution Mode | Sequential chain |

### 3.7 Execution Order

| Step | Action | Week | Gate |
|------|--------|------|------|
| 1 | Execute H-E1 (Pareto Trade-offs Exist) | W1-2 | |
| 2 | Evaluate Gate 1 | W2 | MUST_WORK: If fail → ABANDON |
| 3 | Execute H-M1 (Convex Baseline) | W3-4 | |
| 4 | Execute H-M2 (Deep Decoupling) | W5 | |
| 5 | Execute H-M3 (Method Design) | W6 | |
| 6 | Evaluate Gate 2 | W6 | MUST_WORK (H-M1, H-M2), SHOULD_WORK (H-M3) |
| Final | Verification Complete | | |

**Total Duration:** 6 weeks

---

## 4. Dialectical Analysis

### 4.1 Thesis

**Core Claim:** Multi-objective Pareto trade-offs exist in finite-compute data attribution methods, arising from structural properties of non-convex deep learning geometry.

**Supporting Premises:**
1. In convex settings, all attribution metrics are monotone functions of a single approximation error norm
2. Non-convex deep networks create multiple optimization paths that differently weight quality dimensions
3. Different method designs (random projection vs HVP iteration) inherently prioritize different quality dimensions
4. TRAK achieves 0.7-0.9 rank correlation while IF shows fragility patterns inconsistent with single-error-axis theory

**Conclusion:** Data attribution methods exhibit non-degenerate Pareto trade-offs across rank preservation, magnitude fidelity, and normalized stability, with these trade-offs being structural rather than artifacts of finite-sample convergence.

**Strengths:**
- Clear causal mechanism connecting loss landscape geometry to metric decoupling
- Testable predictions with quantitative thresholds
- Convex baseline provides falsification backbone
- Multiple independent evidence sources from prior work

**Weaknesses:**
- Ground truth estimation requires expensive LOO retraining
- Basin variance may dominate signal in very deep networks
- Results may not transfer to FM scale (7B+ parameters)

**Confidence:** 0.75

### 4.2 Antithesis (Null Hypothesis H0)

**Counter-Claim:** All attribution quality metrics are monotone functions of a single approximation error norm ||phi_hat - phi||_2, and observed trade-offs are finite-sample artifacts that disappear as compute increases.

**Supporting Premises:**
1. A single well-defined target functional (LOO influence) exists
2. All methods attempt to approximate this same target
3. Differences in metric performance reflect convergence rates, not fundamental incompatibilities
4. With sufficient compute, all methods should converge to the same ranking

**Conclusion:** Trade-offs observed in attribution methods are not structural but arise from finite-sample effects and insufficient approximation quality, implying that with enough compute, one method would dominate all metrics.

**Strengths:**
- Parsimonious explanation - single error axis is simpler
- Consistent with asymptotic convergence theory
- Would imply clear method ranking without trade-offs

**Weaknesses:**
- Does not explain why TRAK shows different bias-variance profiles than IF
- Fails to account for Basu et al. fragility findings
- Cannot explain why different methods succeed on different downstream tasks

**Confidence:** 0.25

### 4.3 Synthesis

**Balanced Assessment:** The verification plan resolves the dialectic by empirically testing both the thesis (structural trade-offs) and antithesis (single-axis convergence) through controlled experiments with falsifiable criteria.

**Resolution Path:**
1. **H-E1** directly tests whether Pareto non-dominance exists at matched compute
2. **H-M1** establishes convex baseline where single-axis theory should hold (correlation >= 0.95)
3. **H-M2** tests structural decoupling via R^2 drop from convex to deep regime
4. **H-M3** connects method design to metric prioritization for practical guidance
5. **Gate conditions** allow early detection of antithesis support

**Outcome Possibilities:**

| Outcome | Description | Interpretation |
|---------|-------------|----------------|
| Full Support | All hypotheses pass, R^2 drops in deep regime | Thesis validated: trade-offs are structural |
| Partial Support | H-E1/H-M1 pass, H-M3 fails | Nuanced: trade-offs exist but methods converge on influential examples |
| No Support | H-E1 fails or R^2 remains >= 0.95 in deep | Antithesis supported: single-error-axis model holds |

**Synthesis Confidence:** 0.80

### 4.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution Test |
|--------|-----------------|----------------------|-----------------|
| Existence | Pareto non-dominance exists | Artifacts of finite sample | H-E1: CI-separated crossings |
| Mechanism | Geometry causes decoupling | Same target, different rates | H-M2: R^2 drop test |
| Scope | Applies to finite-compute regime | May vanish with more compute | Compare across 5 budget levels |
| Practical Impact | Different methods for different uses | One method dominates eventually | H-M3: Top-k disagreement test |

**Overall Robustness:** High - the verification plan has clear falsification criteria for both positions
**Confidence in Plan:** 0.75

---

## 5. Executive Summary

**Main Hypothesis:** H-AttributionPareto-v1
- Multi-objective Pareto trade-offs exist in finite-compute data attribution
- Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A pre-mapped)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (Gate 1: Foundation, Gate 2: Mechanisms)

**Risk Assessment:** Medium
- Primary concerns: Basin variance dominating signal (R2), metric orthogonality (R3)

**Immediate Action:** Begin Phase 1 with H-E1 (Pareto Trade-offs Existence Test)

---

## 6. Conclusions

### 6.1 Key Achievements
- 4 sub-hypotheses structured across 2 verification phases
- Null hypothesis H0 (single-error-axis model) directly addressed through R^2 comparison
- Dialectical synthesis provides balanced evaluation framework
- Clear falsification criteria for both thesis and antithesis positions

### 6.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Demonstrate Pareto non-dominance exists via CI-separated metric crossings
- Gate 1: MUST PASS → If fail, ABANDON multi-objective framing

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Establish convex baseline coupling (correlation >= 0.95)
- H-M2: Demonstrate deep network metric decoupling (R^2 < 0.80)
- H-M3: Connect method design to metric prioritization (Jaccard < 0.70)
- Gate 2: H-M1, H-M2 must pass; H-M3 should pass

### 6.3 Critical Decision Points

| Gate | Hypothesis | Pass Action | Fail Action |
|------|------------|-------------|-------------|
| Gate 1 | H-E1 | Proceed to Phase 2 | ABANDON: Multi-objective framing invalid |
| Gate 2 | H-M1 | Continue chain | PIVOT: Redefine metrics |
| Gate 2 | H-M2 | Continue chain | EXPLORE: Single-axis model holds |
| Gate 2 | H-M3 | Complete verification | EXPLORE: Methods converge on examples |

### 6.4 Open Questions
- Does Pareto structure persist at FM scale (7B+ parameters)?
- Do LoRA methods show metric recoupling due to low-rank parameterization?
- What is the optimal compute allocation strategy for multi-objective practitioners?

### 6.5 Recommendations

**Immediate Actions:**
1. Begin H-E1 with basin variance check as prerequisite
2. Set up LOO ground truth computation infrastructure (1000 examples x 10 retrains)

**Resource Allocation:**
- Allocate 6 weeks for critical path (fully sequential)
- Reserve additional time for potential R=20 if variance too high

**Failure Management:**
- Document all partial results for future reference
- Execute PIVOT/EXPLORE strategies per hypothesis specifications

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml
- **Hypothesis ID:** H-AttributionPareto-v1
- **Gap ID:** gap-1-pareto-frontier

### B. MCP Tool Usage Summary
- **Total MCP calls:** 6
- **Tools used:**
  - `mcp__clearThought__scientificmethod`: 3 calls (H-E1, H-M integrated, experiment design)
  - `mcp__clearThought__structuredargumentation`: 3 calls (thesis, antithesis, synthesis)

### C. Established Facts (BUILD_ON - Not Re-tested)
1. TRAK achieves 0.7-0.9 rank correlation with LOO (Park et al. 2023)
2. Influence functions are fragile in deep networks (Basu et al. 2020)
3. No unified multi-metric benchmark exists (Phase 1 literature review)

---

*Generated by YouRA Phase 2B (Compact v1.0) | 2026-03-26*

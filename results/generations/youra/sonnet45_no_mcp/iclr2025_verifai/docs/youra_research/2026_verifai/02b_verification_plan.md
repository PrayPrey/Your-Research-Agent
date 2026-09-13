# Verification Plan: Learned Compute Allocation for Neural Theorem Proving via Confidence Geometry

**Date:** 2026-04-20
**Hypothesis ID:** H-ConfidenceGeometry-v1
**Confidence:** 0.8
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under neural theorem proving with LLM-based tactic suggestion (e.g., LeanDojo), if we deploy a learned compute allocator using LLM confidence geometry (softmax entropy trajectory std dev) combined with symbolic divergence signals (state hash collisions, proof state growth) and search tree metrics (backtrack frequency, branching factor), then proof success rate per unit compute improves by >15% compared to fixed-timeout baselines, because LLM confidence trajectories encode the manifold structure of successful proof spaces, and divergence from this manifold (detected via confidence instability) correlates with probable non-termination.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in proof success rate per unit compute between the learned allocator and fixed-timeout baseline (improvement <5% or allocator underperforms).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LeanDojo Benchmark (standard) | Standard benchmark for neural theorem proving, provides baseline for comparison |
| **Model** | LeanDojo ReProver | State-of-the-art LLM-based prover with accessible confidence scores via DojoCritic interface |

**Dataset Details:**
- Source: Yang et al., 2023 - 98,734 theorems from Lean math library
- Path: https://github.com/lean-dojo/LeanDojo

**Model Details:**
- Type: Retrieval-augmented LLM for theorem proving
- Source: Yang et al., 2023

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| LeanDojo ReProver | 48.9% success rate on held-out theorems | LeanDojo benchmark (98,734 theorems) |
| Fixed timeout strategies (Z3) | Not applicable (different domain) | N/A |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | LLM confidence trajectories encode proof space geometric structure | Theoretical: confidence reflects training distribution manifold. Empirical validation planned via Phase 1 correlation study. | Confidence derivative signal has no predictive power (correlation < 0.3), hypothesis fails Phase 1 gate |
| A2 | Extended-timeout experiments (100× normal budget) approximate true non-termination | Ground truth generation strategy. Some theorems may succeed with 1000× compute, but 100× is practical proxy. | Ground truth labels are noisy, reducing signal correlation and allocator performance |
| A3 | Portfolio allocation mitigates false positive risk on unconventional proofs | Reduce budget rather than abort. Stress test addressed. | High false positive rate (>20%) on valid but unconventional proofs, reducing net benefit |
| A4 | 15% computational overhead from meta-reasoning is acceptable | 450ms overhead per 3-second proof = 15% | If overhead > 20%, efficiency gains are marginal or negative |
| A5 | LeanDojo DojoCritic plugin interface provides sufficient observability | Architectural analysis confirms get_tactics() exposes softmax probabilities | Cannot extract confidence signals without forking LeanDojo codebase, reducing adoption |

### 1.6 Research Gap & Novelty

First work to treat proof search resource allocation as meta-learning problem using LLM confidence geometry. Establishes confidence trajectories as encoding proof space manifold structure—general principle for neural reasoning systems.

**Key Innovation:** Portfolio allocation framework for proof search combining learned (confidence geometry) and symbolic (hash collisions, state growth) signals. Theoretical insight: neural models encode geometric properties of successful reasoning trajectories.

**Differentiation:**
- **LeanDojo [Yang et al., 2023]**: Focuses on tactic prediction (what to try), we focus on resource allocation (when to quit). Orthogonal and combinable.
- **Fixed timeout strategies in Z3, SMT solvers**: Adaptive, learned termination heuristics vs. fixed resource limits. Content-aware via LLM confidence.
- **Symbolic divergence detection (cyclic state detection)**: Hybrid approach: LLM adds semantic similarity detection that symbolic methods miss.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Prerequisites | Gate |
|----|------|-------------------|---------------|------|
| H-E1 | Existence | LLM confidence derivatives correlate with proof termination | None | MUST_WORK |
| H-M1 | Mechanism | Confidence reflects proof space familiarity | H-E1 | MUST_WORK |
| H-M2 | Mechanism | Confidence instability signals divergence | H-M1 | SHOULD_WORK |
| H-M3 | Mechanism | Hybrid signals trigger budget reduction | H-M2 | SHOULD_WORK |
| H-M4 | Mechanism | Portfolio allocation improves efficiency | H-M3 | SHOULD_WORK |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Confidence-Timeout Correlation Existence

**Type:** EXISTENCE

**Statement:** Under neural theorem proving with LeanDojo ReProver, if we extract confidence derivatives (std dev of softmax entropy) from the first 15 proof steps, then these derivatives correlate with eventual timeout outcomes (r > 0.3), because confidence instability reflects the model's uncertainty about unfamiliar proof states.

**Rationale:** This hypothesis validates the foundational assumption that LLM confidence signals contain predictive information about proof termination. Without this correlation, the entire approach fails.

**Variables:**
- Independent: Confidence derivative (std dev of softmax entropy over first 15 steps)
- Dependent: Timeout outcome (success vs. timeout at 100× normal budget)
- Controlled: Base model (ReProver), dataset split (60/20/20), theorem selection (100 extended-timeout experiments)

**Verification Protocol:**
1. Run 100 extended-timeout experiments (100× normal = 300s budget per theorem)
2. Extract confidence trajectories from first 15 steps via LeanDojo get_tactics()
3. Calculate std dev of softmax entropy for each theorem
4. Label outcomes as success/timeout based on 300s results
5. Compute Pearson r and Spearman ρ correlations

**Success Criteria (PoC: Direction-based):**
- Primary: Correlation coefficient r > 0.3 OR ρ > 0.3
- Secondary: Confidence derivative separates success/timeout clusters visually

**Failure Response:**
- IF fails: PIVOT to symbolic-only signals or EXPLORE alternative confidence metrics

**Dependencies:** None

**Source:** Phase 2A Prediction P2 (Confidence derivative correlates with timeout outcomes)

---

#### H-M1: Confidence Encodes Proof Space Geometry

**Type:** MECHANISM

**Statement:** Under neural theorem proving, if LLM confidence (softmax entropy) is measured during proof search, then confidence reflects familiarity with proof state patterns from training distribution, because the model's uncertainty increases when encountering states outside the manifold of successful proofs seen during training.

**Rationale:** Tests the first step of the causal chain - that confidence is a geometric proxy for proof space manifold structure, not just random noise.

**Variables:**
- Independent: Proof state characteristics (novel vs. familiar patterns)
- Dependent: LLM confidence (softmax entropy)
- Controlled: Base model (ReProver), training data distribution

**Verification Protocol:**
1. Collect proof states from successful and failed searches
2. Measure confidence at each state
3. Analyze correlation between state novelty and confidence levels
4. Verify that successful proofs show stable confidence patterns

**Success Criteria (PoC: Direction-based):**
- Primary: Successful proofs show lower variance in confidence than timeouts
- Secondary: Confidence trajectory analysis shows geometric clustering

**Failure Response:**
- IF fails: EXPLORE alternative interpretations of confidence signals

**Dependencies:** H-E1 (must establish correlation exists)

**Source:** Phase 2A Causal Step 1

---

#### H-M2: Confidence Instability Signals Divergence

**Type:** MECHANISM

**Statement:** When proof search diverges into non-terminating regions, if proof states become unfamiliar to LLM, then confidence instability (high variance in entropy) occurs, because the model detects distribution shift similar to perplexity in language models.

**Rationale:** Tests the second causal step - that diverging searches produce characteristic confidence instability that can be detected.

**Variables:**
- Independent: Search divergence status (diverging vs. converging)
- Dependent: Confidence variance (std dev of entropy)
- Controlled: Timeout threshold, state sampling frequency

**Verification Protocol:**
1. Identify diverging vs. converging searches from extended-timeout experiments
2. Extract confidence trajectories for both groups
3. Calculate variance in confidence for each trajectory
4. Compare variance distributions between groups

**Success Criteria (PoC: Direction-based):**
- Primary: Diverging searches show significantly higher confidence variance
- Secondary: Threshold detection (variance > threshold) achieves >70% precision

**Failure Response:**
- IF fails: PIVOT to combined signals without confidence component

**Dependencies:** H-M1 (must establish confidence-geometry link)

**Source:** Phase 2A Causal Step 2

---

#### H-M3: Hybrid Signals Trigger Budget Reduction

**Type:** MECHANISM

**Statement:** When confidence instability (std dev of entropy > threshold) is combined with symbolic signals (state hash collisions, exponential growth) and search tree metrics (high backtrack frequency), if these signals exceed thresholds, then budget reduction is triggered, because the three-signal hybrid provides stronger evidence of probable non-termination than any single signal.

**Rationale:** Tests the third causal step - that combining learned and symbolic signals produces reliable termination detection.

**Variables:**
- Independent: Signal values (confidence variance, hash collisions, backtrack frequency)
- Dependent: Termination decision accuracy
- Controlled: Threshold settings, signal weighting

**Verification Protocol:**
1. Implement three-signal hybrid detector
2. Test on extended-timeout experiment dataset
3. Measure precision and recall for termination prediction
4. Compare against single-signal ablations

**Success Criteria (PoC: Direction-based):**
- Primary: Combined model outperforms all single-signal ablations
- Secondary: Achieves >0.5 correlation with ground truth labels

**Failure Response:**
- IF fails: EXPLORE optimal signal combination or threshold tuning

**Dependencies:** H-M2 (must establish confidence instability detection)

**Source:** Phase 2A Causal Step 3

---

#### H-M4: Portfolio Allocation Improves Efficiency

**Type:** MECHANISM

**Statement:** When portfolio allocation reallocates saved compute from terminated searches to alternative proof strategies, if the allocator reduces budgets for high-risk searches while preserving resources for promising attempts, then overall success rate per unit compute improves by >15%, because avoiding futile searches outweighs the 15% overhead cost from meta-reasoning.

**Rationale:** Tests the final causal step - that the complete system produces measurable efficiency gains despite overhead costs.

**Variables:**
- Independent: Allocation strategy (Learned vs. Fixed vs. Uniform vs. Depth-first)
- Dependent: Proof success rate per unit compute (theorems proven / GPU-seconds)
- Controlled: Total compute budget (1000 GPU-seconds), base model (ReProver)

**Verification Protocol:**
1. Implement complete allocator with all signals
2. Run controlled experiment with fixed 1000 GPU-second budget
3. Compare learned allocator vs. three baseline strategies
4. Measure theorems proven per GPU-second for each condition
5. Statistical testing (two-tailed t-test, p<0.05)

**Success Criteria (PoC: Direction-based):**
- Primary: Learned allocator achieves >15% improvement vs. fixed timeout
- Secondary: Statistical significance p<0.05, allocator doesn't underperform any baseline

**Failure Response:**
- IF fails: PIVOT to refined allocation strategy or DOCUMENT as negative result

**Dependencies:** H-M3 (must establish signal reliability)

**Source:** Phase 2A Causal Step 4

---

## 3. Risk Analysis

### 3.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 | H-E1, H-M1, H-M2 | High |
| R2 | A2 | H-E1, H-M4 | Medium |
| R3 | A3 | H-M3, H-M4 | Medium |
| R4 | A4 | H-M4 | Medium |
| R5 | A5 | All hypotheses | Low |

### 3.2 Mitigation Strategies

**Risk R1: Confidence Geometry Assumption Fails**

**Source Assumption:** A1 - LLM confidence trajectories encode proof space geometric structure

**Description:** If confidence shows no correlation with proof space geometry (random patterns across successful/failed searches), the entire confidence-based approach fails.

**Affected Hypotheses:** H-E1, H-M1, H-M2

**Severity:** High (invalidates core mechanism)

**Mitigation Strategy:**
1. **Prevention:** Phase 1 validation with 100 extended-timeout experiments before full implementation
2. **Detection:** Monitor correlation coefficients (r, ρ) during Phase 1; threshold: r > 0.3
3. **Response:**
   - PIVOT: Switch to symbolic-only signals if r < 0.3
   - SCOPE: Reduce to hybrid approach with less weight on confidence
   - ABORT: If all signals fail correlation test

**Early Warning Indicators:**
- Correlation coefficient r < 0.2 in preliminary tests
- No visual separation in confidence distributions between success/timeout groups

---

**Risk R2: Ground Truth Approximation Inaccuracy**

**Source Assumption:** A2 - Extended-timeout experiments (100× normal budget) approximate true non-termination

**Description:** If 100× timeout threshold is too conservative, ground truth labels become noisy, reducing signal correlation and allocator performance.

**Affected Hypotheses:** H-E1, H-M4

**Severity:** Medium (affects measurement quality)

**Mitigation Strategy:**
1. **Prevention:** Test multiple timeout thresholds (50×, 100×, 200×) to characterize sensitivity
2. **Detection:** Monitor label flip rate when extending timeout further
3. **Response:**
   - PIVOT: Adjust timeout threshold based on sensitivity analysis
   - SCOPE: Acknowledge limitation in paper, focus on relative comparison
   - ABORT: Not applicable (affects all approaches equally)

**Early Warning Indicators:**
- High label flip rate (>20%) when extending from 100× to 200×
- Ground truth inconsistency across multiple runs

---

**Risk R3: High False Positive Rate on Unconventional Proofs**

**Source Assumption:** A3 - Portfolio allocation mitigates false positive risk on unconventional proofs

**Description:** If allocator terminates valid but unconventional proof paths, false positive rate (>20%) reduces net benefit of the approach.

**Affected Hypotheses:** H-M3, H-M4

**Severity:** Medium (undermines efficiency gains)

**Mitigation Strategy:**
1. **Prevention:** Portfolio allocation reduces budget rather than aborting completely
2. **Detection:** Track false positive rate in Phase 2 validation set
3. **Response:**
   - PIVOT: Adjust threshold to favor recall over precision
   - SCOPE: Focus on high-confidence termination cases only
   - ABORT: If false positive rate consistently >30%

**Early Warning Indicators:**
- False positive rate >20% in validation set
- Unconventional proofs (long, deep searches) systematically terminated

---

**Risk R4: Meta-Reasoning Overhead Exceeds Gains**

**Source Assumption:** A4 - 15% computational overhead from meta-reasoning is acceptable

**Description:** If overhead exceeds 20%, efficiency gains from avoiding futile searches become marginal or negative.

**Affected Hypotheses:** H-M4

**Severity:** Medium (threatens overall efficiency)

**Mitigation Strategy:**
1. **Prevention:** Optimize allocator implementation, cache repeated calculations
2. **Detection:** Measure actual overhead during Phase 2 experiments
3. **Response:**
   - PIVOT: Implement faster feature extraction (e.g., sampling instead of full trajectory)
   - SCOPE: Apply allocator only to long-running searches
   - ABORT: If overhead consistently >25% with no optimization path

**Early Warning Indicators:**
- Measured overhead >18% in initial experiments
- Feature extraction dominates compute time

---

**Risk R5: DojoCritic Interface Insufficient**

**Source Assumption:** A5 - LeanDojo DojoCritic plugin interface provides sufficient observability

**Description:** If get_tactics() doesn't expose required confidence signals, implementation requires forking LeanDojo codebase, reducing adoption.

**Affected Hypotheses:** All hypotheses

**Severity:** Low (affects implementation complexity, not validity)

**Mitigation Strategy:**
1. **Prevention:** Verify DojoCritic API in Phase 0 setup
2. **Detection:** Test confidence extraction in hello-world proof
3. **Response:**
   - PIVOT: Fork LeanDojo if necessary (implementation complexity increases)
   - SCOPE: Not applicable
   - ABORT: Not applicable (technical hurdle, not scientific invalidity)

**Early Warning Indicators:**
- get_tactics() doesn't return softmax probabilities
- DojoCritic API changed in recent LeanDojo version

---

### 3.3 Risk Summary

Critical Risks: 0
High Risks: 1 (R1)
Medium Risks: 3 (R2, R3, R4)
Low Risks: 1 (R5)

**Risk Management Strategy:** Phase 1 (signal correlation study) acts as critical gate to validate R1 early. Portfolio allocation framework addresses R3 by design. Multiple timeout thresholds address R2. Overhead optimization addresses R4.

---

## 4. Execution

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - First Mechanism]
    H-M1 ← H-E1
         │
         ▼
[Level 2 - Second Mechanism]
    H-M2 ← H-M1
         │
         ▼
[Level 3 - Third Mechanism]
    H-M3 ← H-M2
         │
         ▼
[Level 4 - Fourth Mechanism]
    H-M4 ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

**Dependency Hierarchy:**

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

---

### 4.2 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses (6 weeks)
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │ W7      │ W8
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │         │
  [Gate 1]       │         │ ◆       │         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │         │
  H-M2           │         │         │ ████    │         │         │
  H-M3           │         │         │         │ ████    │         │
  H-M4           │         │         │         │         │ ████    │
  [Gate 2]       │         │         │         │         │         │ ◆
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼────────
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════════════════
```

**Critical Path Analysis:**

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 6 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4) = 7 weeks (reduced to 6 with overlap)

Slack Available: 0 weeks (all sequential)

---

### 4.3 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Correlation r > 0.3 OR ρ > 0.3 | STOP, reassess entire hypothesis |
| H-M1 | MUST_WORK | Confidence-geometry link demonstrated | PIVOT to symbolic-only approach |
| H-M2 | SHOULD_WORK | Instability detection works | Document limitation, continue |
| H-M3 | SHOULD_WORK | Hybrid signals outperform single-signal | Refine combination strategy |
| H-M4 | SHOULD_WORK | >15% improvement, p<0.05 | Document as negative/partial result |

---

### 4.4 Execution Order

**Step 1**: Execute H-E1 (Foundation) - Week 1-2
**Step 2**: Evaluate Gate 1 → If pass (r > 0.3), proceed; else STOP
**Step 3**: Execute H-M1 (Confidence-geometry link) - Week 3-4
**Step 4**: Evaluate Gate 2a → If H-M1 fails, PIVOT to symbolic-only
**Step 5**: Execute H-M2 (Instability detection) - Week 5
**Step 6**: Execute H-M3 (Hybrid signals) - Week 6
**Step 7**: Execute H-M4 (Portfolio allocation) - Week 7
**Step 8**: Evaluate Gate 2 → Assess overall system performance
**Final**: Verification complete, prepare for Phase 5 baseline comparison

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:** Under neural theorem proving with LLM-based tactic suggestion, deploying a learned compute allocator using LLM confidence geometry combined with symbolic and search tree signals improves proof success rate per unit compute by >15% compared to fixed-timeout baselines, because LLM confidence trajectories encode proof space manifold structure.

**Supporting Evidence:**
1. LLM confidence reflects training distribution manifold (theoretical foundation from language model research)
2. Confidence instability correlates with distribution shift (analogous to perplexity in language models)
3. Portfolio allocation framework reduces false positive risk while maintaining efficiency
4. LeanDojo provides accessible interface (DojoCritic) for confidence extraction

**Strengths:**
- Clear causal mechanism with 4-step chain
- Testable predictions with quantitative thresholds (r > 0.3, >15% improvement)
- Combines learned (confidence) and symbolic (hash collisions) signals for robustness
- Incremental validation through Phase 1 gate (signal correlation study)

**Expected Outcomes:**
- Primary: >15% proof success rate improvement per unit compute (p<0.05)
- Secondary: Correlation r > 0.3 between confidence derivative and timeout
- Tertiary: Hybrid three-signal model outperforms single-signal ablations

---

### 5.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in proof success rate per unit compute between the learned allocator and fixed-timeout baseline (improvement <5% or allocator underperforms).

**Counter-Arguments:**
1. **LLMs trained only on successful proofs**: Model never saw non-terminating searches during training, so confidence may be uninformative about divergence (out-of-distribution problem)
2. **Fixed timeouts may be near-optimal**: LeanDojo's 30-step default may already represent a well-tuned heuristic, leaving little room for improvement
3. **Overhead cost undermines gains**: 15% meta-reasoning overhead may consume most efficiency gains from avoiding futile searches
4. **False positives on unconventional proofs**: Allocator may terminate valid but unusual proof strategies that don't match training distribution patterns

**Potential Failure Points:**
- R1: Confidence geometry assumption fails (correlation < 0.3) → H-E1 fails Phase 1 gate
- R2: Ground truth labels are noisy → Signal correlation weak even if mechanism valid
- R3: High false positive rate (>20%) → Net efficiency gain disappears
- R4: Overhead exceeds 20% → Efficiency gains marginal or negative

**Conditions Under Which H0 Would Be Supported:**
- If H-E1 fails (correlation r < 0.3 AND ρ < 0.3)
- If H-M4 shows improvement <5% or allocator underperforms fixed timeout
- If false positive rate >20% cancels out true positive gains
- If overhead consistently >20% despite optimization attempts

---

### 5.3 Synthesis

**Balanced Assessment:**

The hypothesis H-ConfidenceGeometry-v1 presents a testable claim that LLM confidence geometry provides a learnable signal for compute allocation in neural theorem proving. However, the null hypothesis raises valid concerns regarding out-of-distribution generalization (LLMs never trained on diverging proofs) and the trade-off between meta-reasoning overhead and efficiency gains.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Phase 1 signal correlation study (100 extended-timeout experiments) validates that confidence derivatives contain predictive information before building complex systems
2. **Sequential mechanism testing (H-M1-4):** Tests each causal chain step independently, allowing early detection of mechanism failure
3. **Gate conditions:** MUST_WORK gates at H-E1 and H-M1 provide early stopping if core assumptions fail
4. **Mitigation strategies:** Portfolio allocation (reduce budget, don't abort) addresses false positive risk; multiple timeout thresholds address ground truth sensitivity

**Conditions for Thesis Support:**
- H-E1 passes Phase 1 gate (r > 0.3 OR ρ > 0.3)
- H-M1 validates confidence-geometry link
- H-M4 achieves >15% improvement with p<0.05, statistical significance
- False positive rate <20%, overhead <20%

**Conditions for Antithesis Support:**
- H-E1 fails (correlation < 0.3) → Confidence signals uninformative
- H-M1 fails → No geometric interpretation of confidence
- H-M4 shows <5% improvement or underperforms baseline
- False positive rate >30% or overhead >25% despite optimization

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, confidence geometry principle established
2. **Partial Support:** H-E1, H-M1 pass but H-M4 shows only 8-12% improvement → Refined thesis with realistic expectations, still publishable as "efficiency gains possible but modest"
3. **Mechanism Valid, System Fails:** H-E1, H-M1, H-M2, H-M3 pass but H-M4 fails due to overhead → Confidence geometry principle valid, implementation challenge identified
4. **No Support:** H-E1 or H-M1 fail → Antithesis supported, negative result (LLM confidence not useful for termination detection)

---

### 5.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| **Existence** | Confidence derivatives correlate with timeout | May be random noise, no signal | H-E1 test with r > 0.3 threshold |
| **Mechanism** | Confidence encodes proof space geometry | LLMs never saw diverging proofs (OOD) | H-M1 tests geometric interpretation vs. training distribution shift detection |
| **Efficiency** | >15% improvement per unit compute | Fixed timeout already near-optimal | H-M4 controlled experiment with multiple baselines |
| **Overhead** | 15% overhead acceptable | Overhead may exceed gains | Phase 2 overhead measurement, optimization strategies |
| **False Positives** | Portfolio allocation mitigates risk | Unconventional proofs terminated | Phase 2 error analysis, threshold tuning |

**Overall Robustness Score:** High

**Rationale:**
- Multi-stage validation (Phase 1 → Phase 2 → Ablations) allows early failure detection
- Hybrid signal approach (confidence + symbolic + search tree) reduces reliance on any single signal
- Portfolio allocation framework addresses primary critique (false positives)
- Clear falsification criteria at each gate (r < 0.3, improvement < 5%)
- Acknowledges scope limitations (Lean + LeanDojo only, GPT-based models only)

**Confidence in Verification Plan:** 0.8 (same as hypothesis confidence)

---

## 6. Executive Summary

**Main Hypothesis:** Under neural theorem proving with LLM-based tactic suggestion (e.g., LeanDojo), deploying a learned compute allocator using LLM confidence geometry (softmax entropy trajectory std dev) combined with symbolic and search tree signals improves proof success rate per unit compute by >15% compared to fixed-timeout baselines.
- ID: H-ConfidenceGeometry-v1, Confidence: 0.8

**Verification Structure:**
- Mode: Incremental (Phase 2A data available)
- Sub-Hypotheses: 5 total
  - H-E: 1 (Existence), H-M: 4 (Mechanism steps)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (Gate 1 after H-E1, Gate 2 after H-M4)

**Risk Assessment:** Medium
- Primary concerns: Confidence geometry assumption (R1), false positive rate (R3)
- Mitigation: Phase 1 signal correlation study, portfolio allocation framework

**Immediate Action:** Begin Phase 1 with H-E1 (100 extended-timeout experiments to validate confidence-timeout correlation)

---

## 7. Conclusions

### 7.1 Key Achievements

- 5 hypotheses across 2 verification phases
- H0 addressed: "No significant difference in proof success rate per unit compute (improvement <5% or allocator underperforms)"
- Sequential dependency chain with clear gate conditions enables early failure detection

### 7.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Validate confidence derivatives correlate with timeout (r > 0.3)
- Gate 1: MUST PASS (if fails, entire hypothesis invalidated)

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Confidence encodes proof space geometry
- H-M2: Confidence instability signals divergence
- H-M3: Hybrid signals trigger budget reduction
- H-M4: Portfolio allocation improves efficiency by >15%
- Gate 2: H-M1 must pass, later failures document limitations

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess hypothesis (confidence signals uninformative)
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → PIVOT to symbolic-only approach
   - OPTIONAL FAIL (H-M2-4) → Document limitation, refine implementation

### 7.4 Open Questions

- Does signal correlation in Phase 1 exceed 0.3 threshold?
- What is the false positive rate on unconventional proof paths?
- Does the approach generalize to other proof assistants (Coq, Isabelle)?

### 7.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 (100 extended-timeout experiments)
   - Set up LeanDojo environment with DojoCritic interface
   - Prepare measurement infrastructure for confidence extraction

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path (2 weeks H-E1, 4 weeks H-M1-4)
   - Reserve 2-week buffer for failures and iterations
   - Estimated compute: 70 GPU-hours total (8 hours Phase 1, 42 hours Phase 2, 20 hours ablations)

3. **Failure Management:**
   - Document all failures with error analysis
   - Execute PIVOT strategies defined in risk mitigation
   - If H-E1 fails, consider negative result publication

---

## Appendices

### A. Phase 2A Reference
- **Source:** /home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_verifai/docs/youra_research/20260420_verifai/03_refinement.yaml
- **Hypothesis ID:** H-ConfidenceGeometry-v1
- **Established Facts:** 3 BUILD_ON claims (LeanDojo baseline, existing timeout strategies, DojoCritic interface)

### B. Related Work Summary
- **LeanDojo ReProver:** 48.9% success rate baseline
- **Fixed timeout strategies:** Z3 resource limits (non-adaptive)
- **Novelty:** First work treating proof search allocation as meta-learning using confidence geometry

---

*Generated by YouRA Phase 2B Planning Workflow v7.7.0 | 2026-04-20*

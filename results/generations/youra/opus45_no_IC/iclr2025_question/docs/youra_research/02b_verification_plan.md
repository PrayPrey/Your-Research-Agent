# Verification Plan: Conditional Transfer of Uncertainty-Based Hallucination Detectors

**Date:** 2026-08-10
**Hypothesis ID:** H-ConditionalTransfer-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the scope of factual QA and claim verification benchmarks, if a semantic entropy-based hallucination detector is calibrated on one benchmark and tested on another, then transfer success (AUROC degradation ≤ 0.08) depends on uncertainty distribution similarity between benchmarks, because similar error-generation processes produce similar uncertainty distributions, and thresholds calibrated on one distribution remain effective on statistically similar distributions.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in AUROC degradation between within-cluster and cross-cluster benchmark transfers (i.e., benchmark clustering does not predict transfer success).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Multi-benchmark suite (standard) | Covers factual recall, claim verification, and hallucination detection—the domains where transfer is to be tested |
| **Model** | Llama-2-7B, Mistral-7B | Open-weight models with accessible logits required for semantic entropy computation |

**Dataset Details:**
- Source: Public benchmarks
- Path: TriviaQA, NQ, HaluEval-QA, FEVER, PopQA, SQuAD

**Model Details:**
- Type: Open-weight LLM
- Source: HuggingFace

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Semantic Entropy (Kuhn 2023) | 0.85 AUROC | TriviaQA (in-distribution) |
| SelfCheckGPT (Manakul 2023) | High consistency correlation | WikiBio |
| P(True) (Kadavath 2022) | Calibration improves with scale | Various |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Semantic entropy is a valid proxy for model uncertainty about factual correctness | Kuhn 2023 achieves ~0.85 AUROC; method peer-reviewed in Nature | Entire uncertainty-based detection paradigm breaks down |
| A2 | Bidirectional entailment reliably clusters semantically equivalent generations | Standard NLI methodology; DeBERTa-v3-large achieves ~90% accuracy on MNLI | Semantic entropy computation becomes unreliable |
| A3 | 10 generations per query adequately samples the uncertainty distribution | Kuhn 2023 uses 5-20 generations; 10 is within standard range | Distribution estimates become noisy; clustering unreliable |
| A4 | KDE accurately represents the uncertainty distribution for JS-divergence computation | Standard nonparametric density estimation; robust to distributional assumptions | JS-divergence values may not reflect true distribution differences |
| A5 | AUROC is an appropriate metric for hallucination detection performance | Standard in detection literature; threshold-agnostic ranking metric | Results may not generalize to precision/recall-based deployment criteria |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First systematic investigation of cross-benchmark transfer for uncertainty-based hallucination detectors

**Key Innovation:** Empirical benchmark taxonomy via distribution clustering (JS-divergence + hierarchical clustering)

**Differentiation:**
- Prior work (Kuhn 2023): Evaluated single benchmarks; no transfer analysis
- SelfCheckGPT (Manakul 2023): WikiBio only; no cross-benchmark evaluation
- Xue 2025: Cross-model focus; same benchmark per model

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Benchmark Clustering Structure Exists

**Type:** EXISTENCE
**Statement:** Under the scope of factual QA and claim verification benchmarks, if semantic entropy distributions are computed for each benchmark and clustered via JS-divergence, then meaningful clusters emerge (silhouette > 0.5), because benchmarks testing similar error types produce similar uncertainty distributions.

**Rationale:**
This hypothesis validates the foundational claim that benchmarks naturally cluster based on uncertainty distribution similarity. Without demonstrable clustering structure, the transfer prediction mechanism has no basis.

**Variables:**
- Independent: Benchmark identity (6 benchmarks)
- Dependent: Silhouette score of hierarchical clustering
- Controlled: Model family, sampling temperature (0.7), generation count (10)

**Verification Protocol:**
1. Generate 10 completions per query for 1,000 queries per benchmark using Llama-2-7B
2. Compute semantic entropy per query via bidirectional entailment clustering
3. Build KDE of entropy distributions per benchmark
4. Compute 6×6 JS-divergence matrix
5. Apply hierarchical clustering with Ward linkage
6. Calculate silhouette score

**Success Criteria (PoC: Direction-based):**
- Primary: Silhouette score > 0.5
- Secondary: 2-4 meaningful clusters discovered

**Failure Response:**
- IF fails: ABANDON (entire transfer hypothesis invalid)

**Dependencies:** None

**Source:** Phase 2A SH1, Prediction P1

---

#### H-M1: LLM Uncertainty Reflects Error Processes

**Type:** MECHANISM
**Statement:** Under the scope of factual QA benchmarks, if LLMs generate responses with output_hidden_states enabled, then semantic entropy signals correlate with error-generation processes, because models exhibit higher uncertainty on questions where their knowledge is incomplete or conflicting.

**Rationale:**
This mechanism step validates that semantic entropy captures meaningful uncertainty rather than random noise. It establishes the link between model internals and error likelihood.

**Variables:**
- Independent: Question difficulty/error type
- Dependent: Semantic entropy value
- Controlled: Model architecture, sampling parameters

**Verification Protocol:**
1. Compute semantic entropy for each query
2. Compare entropy distributions between correct and incorrect responses
3. Calculate effect size (Cohen's d) for entropy separation
4. Verify entropy correlates with known difficulty indicators

**Success Criteria:**
- Primary: Entropy is significantly higher for incorrect responses (p < 0.05)
- Secondary: Cohen's d > 0.3

**Failure Response:**
- IF fails: PIVOT to alternative uncertainty signal

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---

#### H-M2: Similar Error Processes Produce Similar Distributions

**Type:** MECHANISM
**Statement:** Under the scope of factual recall benchmarks (TriviaQA, NQ, PopQA), if benchmarks test similar cognitive processes (factual recall), then their uncertainty distributions are similar (JS-divergence < 0.15), because the same error-generation mechanism produces statistically similar entropy patterns.

**Rationale:**
This step tests whether benchmarks with intuited-similar error types actually cluster together, validating the theoretical link between error process and distribution shape.

**Variables:**
- Independent: Benchmark pair type (same vs different error family)
- Dependent: Pairwise JS-divergence
- Controlled: Entropy computation methodology

**Verification Protocol:**
1. Compute pairwise JS-divergence for all 15 benchmark pairs
2. Categorize pairs by intuited error family
3. Compare JS-divergence distributions between same-family and cross-family pairs
4. Statistical test for significant difference

**Success Criteria:**
- Primary: Same-family JS-divergence < Cross-family JS-divergence (p < 0.05)
- Secondary: Mean same-family JS-div < 0.15

**Failure Response:**
- IF fails: EXPLORE alternative clustering criteria

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---

#### H-M3: Within-Cluster Transfer Success

**Type:** MECHANISM
**Statement:** Under the scope of within-cluster benchmark pairs, if a threshold is calibrated on source benchmark (70% train), then applying it to target benchmark (30% test) achieves AUROC degradation ≤ 0.08, because similar distributions preserve threshold effectiveness.

**Rationale:**
This is the core transfer claim—demonstrating that calibration transfers within statistically similar benchmarks. It directly tests the practical utility of benchmark clustering.

**Variables:**
- Independent: Within-cluster benchmark pair
- Dependent: AUROC degradation (source - target)
- Controlled: Train/test split (70/30), threshold calibration method

**Verification Protocol:**
1. Identify within-cluster benchmark pairs from H-E1 clustering
2. For each pair: calibrate threshold on source 70%, evaluate on target 30%
3. Compute AUROC on both source test and target test
4. Calculate degradation for each pair
5. Report mean and 95% CI for within-cluster degradation

**Success Criteria:**
- Primary: Mean within-cluster AUROC degradation ≤ 0.08
- Secondary: 95% CI upper bound < 0.12

**Failure Response:**
- IF fails: EXPLORE tighter cluster criteria

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3, Prediction P2

---

#### H-M4: Cross-Cluster Transfer Failure

**Type:** MECHANISM
**Statement:** Under the scope of cross-cluster benchmark pairs, if a threshold is calibrated on source benchmark, then applying it to target benchmark shows AUROC degradation > 0.15, because dissimilar distributions require recalibration.

**Rationale:**
This completes the contrast—showing that transfer fails across dissimilar benchmarks. Combined with H-M3, it validates that clustering predicts transfer success.

**Variables:**
- Independent: Cross-cluster benchmark pair
- Dependent: AUROC degradation (source - target)
- Controlled: Same as H-M3

**Verification Protocol:**
1. Identify cross-cluster benchmark pairs from H-E1 clustering
2. For each pair: calibrate threshold on source 70%, evaluate on target 30%
3. Compute AUROC on both source test and target test
4. Calculate degradation for each pair
5. Report mean and 95% CI for cross-cluster degradation

**Success Criteria:**
- Primary: Mean cross-cluster AUROC degradation > 0.15
- Secondary: Significant difference from within-cluster (p < 0.05)

**Failure Response:**
- IF fails: EXPLORE alternative distance metrics

**Dependencies:** H-M3

**Source:** Phase 2A Causal Step 4, Prediction P3

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Silhouette > 0.5 | ABANDON |
| H-M1 | MUST_WORK | p < 0.05, Cohen's d > 0.3 | PIVOT |
| H-M2 | SHOULD_WORK | Same < Cross (p < 0.05) | EXPLORE |
| H-M3 | SHOULD_WORK | Degradation ≤ 0.08 | EXPLORE |
| H-M4 | SHOULD_WORK | Degradation > 0.15 | EXPLORE |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Risk Mapping

| Risk ID | Source | Description | Severity | Affected |
|---------|--------|-------------|----------|----------|
| R1 | A1 | Semantic entropy fails as uncertainty proxy | Critical | All |
| R2 | A2 | Entailment clustering unreliable | High | H-E1, H-M1 |
| R3 | A3 | 10 generations insufficient | Medium | H-E1 |
| R4 | A4 | KDE misrepresents distributions | Medium | H-E1, H-M2 |
| R5 | A5 | AUROC inappropriate for deployment | Low | H-M3, H-M4 |

### 4.2 Mitigation Strategies

**R1 (Critical): Semantic Entropy Validity**
- Prevention: Validate on established benchmark (TriviaQA) before transfer experiments
- Detection: Monitor in-distribution AUROC during H-M1
- Response: If AUROC < 0.70 in-distribution, ABANDON

**R2 (High): Entailment Clustering**
- Prevention: Use DeBERTa-v3-large (90% MNLI accuracy)
- Detection: Spot-check clusterings manually on sample queries
- Response: If clustering pathological, try sentence-BERT similarity

**R3 (Medium): Generation Count**
- Prevention: Use 10 generations (middle of Kuhn's 5-20 range)
- Detection: Compute entropy variance; flag if > 0.5
- Response: If noisy, increase to 15 generations

**R4 (Medium): KDE Accuracy**
- Prevention: Use Scott's rule for bandwidth
- Detection: Visual inspection of KDEs
- Response: Try histogram-based divergence

**R5 (Low): AUROC Appropriateness**
- Prevention: Report precision/recall alongside AUROC
- Detection: Check correlation between AUROC and F1
- Response: Add threshold-specific metrics to Phase 5

---

## 5. Dependency Graph

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - Clustering Structure)
         │
         ▼
[Level 1 - Mechanism Chain]
    H-M1 (Uncertainty reflects errors) ← H-E1
         │
         ▼
    H-M2 (Similar processes → similar distributions) ← H-M1
         │
         ▼
    H-M3 (Within-cluster transfer succeeds) ← H-M2
         │
         ▼
    H-M4 (Cross-cluster transfer fails) ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3-4 │ W5   │ W6   │ W7
─────────────────┼──────┼──────┼──────┼──────┼──────
PHASE 1: Foundation
  H-E1           │██████│      │      │      │
  [Gate 1]       │      │ ◆    │      │      │
─────────────────┼──────┼──────┼──────┼──────┼──────
PHASE 2: Mechanisms
  H-M1           │      │██████│      │      │
  H-M2           │      │      │████  │      │
  H-M3           │      │      │      │████  │
  H-M4           │      │      │      │      │████
  [Gate 2]       │      │      │      │      │   ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Semantic entropy-based hallucination detectors transfer successfully between benchmarks with similar uncertainty distributions (within-cluster), but fail across dissimilar distributions (cross-cluster). Benchmark families emerge empirically from JS-divergence clustering.

**Supporting Evidence:**
1. Semantic entropy achieves ~0.85 AUROC in-distribution (Kuhn 2023)
2. Calibration theory supports threshold transfer within similar distributions
3. Domain adaptation literature shows distribution similarity predicts transfer success

**Strengths:**
- Grounded in established uncertainty quantification theory
- Clear causal mechanism with 4 testable steps
- Practical implications for detector deployment

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in AUROC degradation between within-cluster and cross-cluster benchmark transfers (i.e., benchmark clustering does not predict transfer success).

**Counter-Arguments:**
1. Benchmark differences may be driven by surface features (question length, vocabulary) rather than error processes
2. JS-divergence may not capture semantically meaningful distribution differences
3. 6 benchmarks may be insufficient for reliable clustering

**Potential Failure Points:**
- Clustering produces trivial or arbitrary groupings (silhouette < 0.5)
- Within-cluster transfer fails despite distribution similarity
- Cross-cluster transfer succeeds despite distribution dissimilarity

### 6.3 Synthesis

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence before mechanism
2. **Sequential mechanism testing (H-M1-M4):** Tests causal chain step-by-step
3. **Gate conditions:** Allow early detection of H0 support

**Conditions for Thesis Support:**
- H-E1: Silhouette > 0.5 (meaningful clusters)
- H-M3: Within-cluster degradation ≤ 0.08
- H-M4: Cross-cluster degradation > 0.15
- Significant difference between within and cross (p < 0.05)

**Conditions for Antithesis Support:**
- H-E1 fails (no clustering structure)
- H-M3 and H-M4 show similar degradation
- Clustering does not predict transfer success

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated
2. **Partial Support:** Some H-M fail → Refined thesis with limitations
3. **No Support:** H-E1 fails → Antithesis supported

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Clusters exist | May be artifact | H-E1 silhouette test |
| Mechanism | Error process drives clustering | Surface features drive | H-M1-M2 correlation tests |
| Transfer | Predicts success | Random correlation | H-M3-M4 contrast |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary

**Main Hypothesis:** Cross-benchmark transfer of semantic entropy detectors depends on uncertainty distribution similarity
- ID: H-ConditionalTransfer-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: Semantic entropy validity (R1), entailment clustering (R2)

**Immediate Action:** Begin Phase 1 with H-E1 (benchmark clustering)

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-ConditionalTransfer-v1)
- **Schema Version:** 10.0.0
- **Discussion Exchanges:** 15

### B. Established Facts (BUILD ON - Not Re-Tested)
- Semantic entropy detects hallucinations with ~0.85 AUROC in-distribution
- Model calibration (P(True)) improves with model scale
- Bidirectional entailment reliably clusters semantic equivalence

### C. MCP Tool Usage Summary
- **Total MCP calls:** 2 (scientificmethod x1, structuredargumentation x1)
- **Research Mode:** Incremental

---

*Generated by Phase 2B Planning Workflow*
*Steps Completed: step-00 through step-10*
*Status: complete*
*Completed At: 2026-08-10*

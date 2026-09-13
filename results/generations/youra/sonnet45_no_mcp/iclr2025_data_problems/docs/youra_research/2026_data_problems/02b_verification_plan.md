# Verification Plan: Gradient-Geometric Data Scheduling for Foundation Models

**Date:** 2026-04-15
**Hypothesis ID:** H-GradGeomSchedule-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## Section 0: Established Facts & Scope Reduction

### Build-On Claims (DO NOT Re-Verify)

The following claims have established evidence and will NOT be re-tested:

| Claim | Status | Evidence |
|-------|--------|----------|
| Path dependence in non-convex SGD optimization is fundamental | BUILD_ON | Extensive prior work on loss landscape geometry, basin selection |
| Existing benchmarks (MMLU, Big-Bench) are sufficient | BUILD_ON | Widely adopted, validated for domain coverage |
| Transformer models benefit from diverse pretraining data | BUILD_ON | GPT-3, PaLM, Llama empirical validation |

**Scope Reduction:** 75% of baseline claims established, focusing verification on NEW contribution.

### Prove-New Claims (PRIMARY VERIFICATION TARGET)

| Claim | Target |
|-------|--------|
| Temporal domain ordering affects performance through gradient geometry | Phase 2B-4 Verification |

**Instructions for Phase 2B-4:**
Build on established optimization theory (path dependence, gradient covariance) and existing benchmarks. Focus verification on proving the NEW claim: temporal ordering affects performance through measurable gradient geometry changes with predictive power from corpus statistics.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under foundation model pretraining with mixed-domain corpora, if training domains are ordered from high to low diversity (measured by corpus statistics: vocabulary entropy, syntactic complexity, semantic spread), then final model performance, continual learning robustness, and out-of-distribution generalization improve significantly, because early high-diversity data establishes broader gradient covariance geometry through path-dependent optimization that persists throughout training.

### 1.2 Alternative Hypothesis (H0)

There is no statistically significant difference in final model performance, gradient covariance geometry, or continual learning robustness between diversity-ranked domain orderings and static mixture schedules when total per-domain token counts are matched. Any observed differences are within stochastic variance bounds (±0.5% performance, <5% geometric metrics).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Mixed-Domain Pretraining Corpus (standard) | Multi-domain corpus enables diversity-ranked scheduling experiments with established benchmark evaluation |
| **Model** | Transformer Decoder (GPT-style) | Transformer architecture with clear gradient-based representation formation, scales validated (1B, 7B) |

**Dataset Details:**
- Source: C4 (web), GitHub (code), arXiv (scientific), BookCorpus (books), legal corpus for continual learning injection
- Path: publicly_available_datasets

**Model Details:**
- Type: autoregressive_language_model
- Source: standard_architecture

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Best Static Mixture | To be measured (baseline) | C4, GitHub, arXiv, BookCorpus | Ad-hoc ratio selection, no temporal dynamics, no geometric mechanism understanding |
| Two-phase training | Common practice | General → domain-specific | Sharp transitions only, no systematic schedule optimization |
| DoReMi domain reweighting | State-of-art static mixing | Multi-domain pretraining | Static ratios throughout training, no temporal composition |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Path dependence primacy: early gradient updates have disproportionate influence | Established optimization theory for SGD | If early-late symmetric, temporal ordering effects vanish |
| A2 | Diversity-covariance coupling: corpus diversity correlates with gradient covariance rank | To be validated (Phase 1: Spearman ρ ≥ 0.7) | If ρ < 0.5, corpus statistics cannot predict optimal schedules |
| A3 | Geometric persistence: early gradient covariance structure persists | To be measured via CKA (≥10% higher similarity) | If CKA ≤ reversed schedules, path dependence weakens |
| A4 | Subspace orthogonality benefits: broader early subspaces reduce interference | To be measured via Fisher overlap (≥10% higher) | If forgetting reduction occurs without Fisher changes, claim falsified |
| A5 | Scaling persistence: path-dependent effects remain at increased capacity | To be validated at 7B (≥0.5% effect size) | If effects vanish at 7B, contribution narrows to small-model only |

### 1.6 Research Gap & Novelty

**Gap:** Existing work on data mixing optimizes static ratios (DoReMi) or uses ad-hoc two-phase training, but ignores temporal dynamics and lacks optimization-theoretic grounding for schedule design.

**Novelty:** First work to establish temporal data composition as a first-class design principle with optimization-theoretic grounding and predictive power from corpus statistics. Key innovation: Predictive diversity law enabling a priori schedule optimization without expensive hyperparameter searches, validated across six experimental phases.

**Differentiation:**
- vs Curriculum learning: Applies to domain sources with geometric mechanism validation, not individual example difficulty
- vs DoReMi: Temporal dynamics with path-dependent gradient geometry, not static ratio tuning
- vs Multi-phase training: Smooth curriculum schedules with parametric sweep, geometric mechanism validation
- vs Continual learning regularization: Pretraining-time intervention (data scheduling geometry) vs post-hoc regularization

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Prerequisites | Gate |
|----|------|-------------------|---------------|------|
| H-E1 | Existence | Diversity-ranked scheduling improves performance vs static mixture | None | MUST_WORK |
| H-M1 | Mechanism | Early high-diversity establishes broader gradient covariance | H-E1 | MUST_WORK |
| H-M2 | Mechanism | Path-dependent optimization crystallizes representational subspaces | H-M1 | SHOULD_WORK |
| H-M3 | Mechanism | Later specialization operates within established broad subspace | H-M2 | SHOULD_WORK |
| H-M4 | Mechanism | Broader geometry enables robust downstream adaptation | H-M3 | SHOULD_WORK |

**Total:** 5 hypotheses (1 Existence + 4 Mechanism)

---

### 2.2 Hypothesis Specifications

#### H-E1: Performance Improvement via Diversity-Ranked Scheduling

**Type:** EXISTENCE

**Statement:** Under foundation model pretraining with mixed-domain corpora, if training domains are ordered from high to low diversity (measured via corpus statistics), then final model performance on multi-domain benchmarks exceeds best static mixture baseline by ≥2.0% absolute at 1B scale and ≥0.5% absolute at 7B scale, because temporal ordering enables optimization trajectory advantages.

**Rationale:**
This hypothesis validates the existence of the core phenomenon: that temporal ordering matters for final performance. It establishes the foundation for mechanistic investigation by demonstrating measurable improvement before exploring why it occurs.

**Variables:**
- **Independent:** Domain Ordering Schedule (static vs diversity-ranked vs reversed vs shuffled)
- **Dependent:** Composite benchmark performance (MMLU + Big-Bench + domain-specific, 0-100%)
- **Controlled:** Total tokens per domain, learning rate schedule, model architecture (1B/7B), optimizer hyperparameters

**Verification Protocol:**
1. Train 4 conditions (static, diversity-ranked, reversed, shuffled) at 1B with n=5 seeds
2. Measure composite performance on MMLU + Big-Bench + domain benchmarks
3. Perform statistical significance testing with Bonferroni correction
4. Repeat at 7B scale with power analysis (n=5, ≥70% power)
5. Validate ≥2.0% improvement at 1B, ≥0.5% at 7B with p<0.05

**Success Criteria:**
- **Primary:** Diversity-ranked > static by ≥2.0% absolute at 1B (p<0.05, 95% CI excluding zero)
- **Secondary:** Diversity-ranked > static by ≥0.5% absolute at 7B (statistically significant, power ≥70%)

**Gate:**
- **Type:** MUST_WORK
- **If Fail:** STOP and reassess entire hypothesis - if no performance improvement exists, mechanism investigation is premature

**Prerequisites:** None (foundation hypothesis)

**Source:** Phase 2A Section 1.6 Prediction P1, SH1

---

#### H-M1: Early Diversity Shapes Gradient Covariance

**Type:** MECHANISM

**Statement:** Under diversity-ranked scheduling, if training begins with high-diversity domains (broad vocabulary, varied syntax), then gradient covariance rank (participation ratio) at 25% training exceeds reversed schedule by ≥15%, because high-diversity data induces higher-rank gradient covariance matrices measurable via participation ratio.

**Rationale:**
This hypothesis tests the first link in the causal chain: whether corpus diversity actually shapes early gradient geometry. It validates assumption A2 (diversity-covariance coupling) through direct measurement.

**Variables:**
- **Independent:** Domain ordering (diversity-ranked vs reversed)
- **Dependent:** Gradient Covariance Rank (Participation Ratio) at 10%/25%/50%/100% checkpoints
- **Controlled:** Probe dataset (10K tokens/domain, identical seeds), measurement methodology

**Verification Protocol:**
1. Compute participation ratio at 10%, 25%, 50%, 100% training for diversity-ranked and reversed schedules
2. Compare early checkpoint PR (25%) between conditions
3. Validate diversity metrics (vocabulary entropy, syntactic complexity, semantic spread) correlate with PR across 6-8 domains (Spearman ρ ≥ 0.7)
4. Ensure measurement uses fixed probe dataset for reproducibility

**Success Criteria:**
- **Primary:** PR@25% for diversity-ranked ≥ 15% higher than reversed (directional ordering holds)
- **Secondary:** Diversity metrics correlate with early PR (Spearman ρ ≥ 0.7 across domains)

**Gate:**
- **Type:** MUST_WORK
- **If Fail:** Mechanism chain breaks at first step - diversity-PR coupling assumption (A2) violated

**Prerequisites:** H-E1 (existence must be established)

**Source:** Phase 2A Section 1.3 Causal Step 1, Assumption A2

---

#### H-M2: Path-Dependent Optimization Crystallizes Subspaces

**Type:** MECHANISM

**Statement:** Under diversity-ranked scheduling, if early high-diversity establishes broader gradient covariance, then representational subspace persistence (CKA similarity between 25% and 100% checkpoints) exceeds reversed schedule by ≥10%, because path-dependent SGD basin selection constrains subspaces for subsequent learning.

**Rationale:**
This hypothesis tests whether early geometry persists through training (assumption A3), validating that temporal ordering has lasting effects beyond immediate training dynamics.

**Variables:**
- **Independent:** Domain ordering (diversity-ranked vs reversed)
- **Dependent:** Layer-wise CKA similarity between 25% and 100% checkpoints (0-1 range)
- **Controlled:** CKA estimation (bootstrapped, 1000 samples, 95% CI)

**Verification Protocol:**
1. Compute layer-wise bootstrapped CKA similarity (1000 samples, 95% CI) between 25% and 100% checkpoints
2. Compare CKA persistence: diversity-ranked vs reversed
3. Validate ≥10% higher similarity for diversity-ranked across ≥70% of layers
4. Ensure directional ordering holds across layer depths

**Success Criteria:**
- **Primary:** CKA persistence (25%→100%) for diversity-ranked ≥ 10% higher than reversed
- **Secondary:** Directional ordering holds across ≥70% of layers

**Gate:**
- **Type:** SHOULD_WORK
- **If Fail:** Document limitation - early geometry may not persist, but existence (H-E1) remains valid

**Prerequisites:** H-M1 (early gradient covariance established)

**Source:** Phase 2A Section 1.3 Causal Step 2, Assumption A3

---

#### H-M3: Later Specialization Within Established Subspace

**Type:** MECHANISM

**Statement:** Under diversity-ranked scheduling, if early geometry persists, then later low-diversity domain training (code, scientific papers) refines without collapsing geometry, preserving gradient subspace orthogonality measured via within-batch diversity entropy remaining ≥5% higher than reversed.

**Rationale:**
This hypothesis tests whether the broad early geometry accommodates later specialization without destructive interference, validating the "refine without collapse" mechanism.

**Variables:**
- **Independent:** Domain ordering (diversity-ranked vs reversed)
- **Dependent:** Within-batch entropy at 50%/75%/100% training checkpoints
- **Controlled:** Batch construction methodology, diversity metric calculation

**Verification Protocol:**
1. Monitor within-batch entropy throughout training (especially 50%+ where low-diversity domains appear)
2. Compare diversity-ranked vs reversed at late checkpoints (50%, 75%, 100%)
3. Validate diversity-ranked maintains ≥5% higher within-batch entropy
4. Use cumulative-matched controls to disambiguate ordering vs total exposure

**Success Criteria:**
- **Primary:** Within-batch entropy at 75%/100% for diversity-ranked ≥ 5% higher than reversed
- **Secondary:** Cumulative-matched reversed shows same effect, confirming ordering matters (not just total exposure)

**Gate:**
- **Type:** SHOULD_WORK
- **If Fail:** Document limitation - specialization may reduce diversity more than expected, but core mechanism (H-M1, H-M2) remains

**Prerequisites:** H-M2 (subspace persistence established)

**Source:** Phase 2A Section 1.3 Causal Step 3

---

#### H-M4: Broader Geometry Enables Robust Adaptation

**Type:** MECHANISM

**Statement:** Under diversity-ranked scheduling with established broad geometry, if a new domain (legal text) is injected with fixed budget, then catastrophic forgetting is ≤50% of reversed schedule AND Fisher overlap is ≥10% higher, because higher gradient subspace orthogonality reduces gradient interference during adaptation.

**Rationale:**
This hypothesis tests the downstream consequence of broad geometry: improved continual learning robustness with coupled geometric and performance validation (assumption A4).

**Variables:**
- **Independent:** Domain ordering (diversity-ranked vs reversed)
- **Dependent:** Δ accuracy on original benchmarks post-injection (percentage points), Fisher overlap (dimensionless)
- **Controlled:** Injection domain (legal text), injection budget (fixed tokens), frozen optimizer state before injection

**Verification Protocol:**
1. Train models (diversity-ranked vs reversed) to 100% completion
2. Inject fixed-budget legal domain continuation
3. Measure Δ accuracy on original benchmarks (≥5 benchmarks for robustness)
4. Compute Fisher overlap using diagonal empirical Fisher on 5K-token probe set
5. Validate coupled requirement: forgetting reduction AND Fisher overlap increase

**Success Criteria:**
- **Primary (coupled):** Forgetting ≤ 50% of reversed (p<0.01) AND Fisher overlap ≥ 10% higher
- **Secondary:** If only one criterion met, geometric stability claim weakens (must have both)

**Gate:**
- **Type:** SHOULD_WORK
- **If Fail:** Continual learning benefit is high-risk/high-reward - failure narrows contribution to in-distribution performance

**Prerequisites:** H-M3 (geometry preservation during late training)

**Source:** Phase 2A Section 1.3 Causal Step 4, Assumption A4

---

## 3. Risk Analysis

### 3.1 Assumption-to-Risk Mapping

| Risk | Source | Description | Severity | Affected Hypotheses |
|------|--------|-------------|----------|---------------------|
| R1 | A1 | Path dependence symmetry: Early-late gradient contributions may be symmetric | High | H-E1, H-M1 |
| R2 | A2 | Diversity-PR correlation failure: Corpus statistics may not predict gradient rank (ρ < 0.5) | Critical | H-M1, all dependent |
| R3 | A3 | Geometric non-persistence: Early geometry may not persist through later training | High | H-M2, H-M3, H-M4 |
| R4 | A4 | Fisher-forgetting decoupling: Forgetting reduction may occur without Fisher overlap changes | Medium | H-M4 |
| R5 | A5 | Scaling effect vanishing: Path-dependent effects may disappear at 7B scale | High | All hypotheses |

### 3.2 Mitigation Strategies

**Risk R1: Path Dependence Symmetry**
- **Prevention:** Use shuffled-order control to disambiguate gradient primacy vs curriculum coherence
- **Detection:** Monitor early vs late gradient statistics (variance, rank) across checkpoints
- **Response:**
  - PIVOT: If shuffled = diversity-ranked, publish as curriculum coherence (still novel)
  - SCOPE: Narrow claim to "early high-diversity beneficial" without strict path-dependence
  - ABORT: Only if static mixture = diversity-ranked (no effect at all)

**Risk R2: Diversity-PR Correlation Failure**
- **Prevention:** Phase 1 cross-domain analysis validates correlation BEFORE main experiments
- **Detection:** Spearman ρ < 0.7 in Phase 1 correlation test
- **Response:**
  - PIVOT: If 0.5 ≤ ρ < 0.7, reduce "predictive law" claim to "correlation observed"
  - SCOPE: If ρ < 0.5, abandon predictive framework, focus on empirical curriculum effect
  - ABORT: Only if ρ < 0.3 AND no performance improvement (H-E1 also fails)

**Risk R3: Geometric Non-Persistence**
- **Prevention:** Multi-checkpoint measurement (10%, 25%, 50%, 100%) to track persistence trajectory
- **Detection:** CKA persistence ≤ reversed schedules
- **Response:**
  - PIVOT: Focus on early-stage effects (first 25% training) without persistence claims
  - SCOPE: Narrow to "early geometry shapes early performance" without long-term persistence
  - ABORT: Only if H-E1 also fails (no performance benefit)

**Risk R4: Fisher-Forgetting Decoupling**
- **Prevention:** Coupled requirement (BOTH forgetting reduction AND Fisher overlap increase)
- **Detection:** Only one criterion met in H-M4 validation
- **Response:**
  - PIVOT: Continual learning as exploratory finding, not primary claim
  - SCOPE: Focus on in-distribution performance (H-E1) without continual learning generalization
  - ABORT: N/A (H-M4 is SHOULD_WORK, not MUST_WORK)

**Risk R5: Scaling Effect Vanishing**
- **Prevention:** Power analysis at 7B (n=5) with explicit effect size threshold (≥0.5%)
- **Detection:** Effect size < 0.5% or non-significant at 7B
- **Response:**
  - PIVOT: Contribution = small-model regularization technique (still publishable)
  - SCOPE: Narrow applicability to 1B-3B range with scaling as open question
  - ABORT: Only if effect completely reverses at 7B (diversity-ranked < static)

### 3.3 Risk Summary

| Risk Category | Count | Critical Path Impact |
|---------------|-------|---------------------|
| Critical | 1 (R2) | Blocks predictive law claim |
| High | 3 (R1, R3, R5) | Narrows contribution scope |
| Medium | 1 (R4) | Affects secondary claim only |
| Low | 0 | - |

**Overall Risk Level:** Medium-High
- **Primary concerns:** Diversity-PR correlation (R2), scaling persistence (R5)
- **Mitigation:** Pre-registered protocols, contribution tiers (5/5 = field-defining, 4/5 = strong, 3/5 = publishable)

---

## 4. Execution Planning

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
    H-M1 (Early diversity → gradient covariance)
         │ ← H-E1
         ▼
[Level 2 - Persistence]
    H-M2 (Path-dependent crystallization)
         │ ← H-M1
         ▼
[Level 3 - Specialization]
    H-M3 (Late specialization preservation)
         │ ← H-M2
         ▼
[Level 4 - Downstream Robustness]
    H-M4 (Continual learning robustness)
         │ ← H-M3
         ▼
    [TERMINAL]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Sequential Execution: All hypotheses must run in order
═══════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | If Fail |
|-------|-----------|---------------|-----------|---------|
| 0 | H-E1 | None | MUST_WORK | STOP, reassess hypothesis |
| 1 | H-M1 | H-E1 | MUST_WORK | Mechanism chain breaks |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Document limitation |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Document limitation |
| 4 | H-M4 | H-M3 | SHOULD_WORK | Narrow to in-distribution |

### 4.3 Verification Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │ W7      │
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │         │
  [Gate 1]       │         │ ◆       │         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │         │
  [Gate 2]       │         │         │ ◆       │         │         │
  H-M2           │         │         │ ████    │         │         │
  H-M3           │         │         │         │ ████    │         │
  H-M4           │         │         │         │         │ ████    │
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

**Critical Path:** H-E1 (2w) → H-M1 (2w) → H-M2 (1w) → H-M3 (1w) → H-M4 (1w) = 7 weeks

### 4.4 Resource Summary

- **Total Hypotheses:** 5
  - Existence: 1 (H-E1)
  - Mechanism: 4 (H-M1 to H-M4)
  - Condition: 0
- **Verification Phases:** 2
  1. Foundation (H-E1)
  2. Mechanisms (H-M1 to H-M4)
- **Total Duration:** 7 weeks
- **Critical Path Length:** 7 weeks (all sequential)
- **Execution Mode:** Sequential chain (no parallelization)
- **GPU Hours:** ~45K total (per Phase 2A estimate)

### 4.5 Execution Order

1. **Week 1-2:** Execute H-E1 (Foundation) - Establish existence of performance improvement
2. **Gate 1:** Evaluate results → If PASS, proceed to mechanisms
3. **Week 3-4:** Execute H-M1 (First mechanism) - Validate diversity-PR coupling
4. **Gate 2:** Evaluate H-M1 → If PASS (ρ ≥ 0.7), mechanism chain validated
5. **Week 5:** Execute H-M2 (Persistence) - CKA similarity testing
6. **Week 6:** Execute H-M3 (Specialization) - Within-batch entropy monitoring
7. **Week 7:** Execute H-M4 (Robustness) - Continual learning injection test
8. **Final:** Synthesis across all hypotheses for contribution tier determination

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:**
Under foundation model pretraining with mixed-domain corpora, temporal ordering of training domains from high to low diversity shapes early gradient covariance geometry through path-dependent optimization, producing measurable performance, robustness, and continual learning benefits predictable from diversity metrics alone.

**Supporting Evidence:**
1. Non-convex optimization theory establishes path dependence in SGD (established theory)
2. Four-step causal mechanism with measurable geometric proxies (PR, CKA, Fisher overlap)
3. Five testable predictions with pre-registered quantitative thresholds

**Strengths:**
- Grounded in established optimization theory (path dependence is not novel)
- Clear causal mechanism with step-by-step validation
- Predictive framework from corpus statistics (practical value)
- Six-phase validation with pre-registered criteria (rigorous)

**Expected Outcomes:**
- Primary: ≥2.0% improvement at 1B, ≥0.5% at 7B (P1)
- Secondary: ≥15% higher PR, ≥10% higher CKA persistence (P3)
- Tertiary: ≤50% forgetting with ≥10% Fisher overlap (P4)

### 5.2 Antithesis

**Null Hypothesis (H0):**
There is no statistically significant difference in final model performance, gradient covariance geometry, or continual learning robustness between diversity-ranked domain orderings and static mixture schedules when total per-domain token counts are matched. Any observed differences are within stochastic variance bounds (±0.5% performance, <5% geometric metrics).

**Counter-Arguments:**
1. **Baseline limitations:** Static mixture may already implicitly optimize ordering through validation tuning, making explicit scheduling redundant
2. **Assumption violations:**
   - A2 violation: Diversity metrics may not correlate with PR (ρ < 0.5)
   - A3 violation: Early geometry may wash out during later training
   - A5 violation: Effects may vanish at 7B scale (capacity overwhelms ordering)
3. **Scope limitations:** Effects may be taxonomy-dependent (domain bucketing artifacts), not general law

**Potential Failure Points:**
- Risk R2 (Critical): Diversity-PR correlation fails → predictive law collapses
- Risk R5 (High): Scaling effects vanish → contribution narrows to small models
- Risk R3 (High): Geometry doesn't persist → mechanism weakens

**Conditions Under Which H0 Would Be Supported:**
- If performance improvement < 0.5% or non-significant at 1B
- If diversity metrics don't correlate with PR (ρ < 0.5)
- If cumulative-matched controls show identical effects (ordering doesn't matter, only total exposure)
- If all mechanism hypotheses (H-M1 to H-M4) fail despite H-E1 passing

### 5.3 Synthesis

**Balanced Assessment:**

The hypothesis H-GradGeomSchedule-v1 presents a testable claim that temporal data composition affects model training through path-dependent gradient geometry, establishing data scheduling as a first-class design principle. However, the null hypothesis raises valid concerns regarding the generality of corpus-statistics prediction (A2), the persistence of early geometry effects (A3), and scaling robustness (A5).

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence before investigating mechanism - if no performance improvement exists, mechanism exploration is premature
2. **Sequential mechanism testing (H-M1 to H-M4):** Tests each causal chain step independently with explicit falsifiers
3. **Gate conditions:** Allow early detection of H0 support (e.g., Gate 1 failure → STOP immediately)
4. **Contribution tiers:** Accept contingent outcomes (5/5 phases = field-defining, 4/5 = strong, 3/5 = publishable)

**Conditions for Thesis Support:**
- H-E1 and H-M1 both pass (MUST_WORK gates) → Core claim validated
- Diversity-PR correlation ≥ 0.7 (Phase 1) → Predictive law supported
- 4-5 validation phases met → Strong to field-defining contribution

**Conditions for Antithesis Support:**
- H-E1 fails (no performance improvement) → No phenomenon exists
- H-M1 fails (diversity-PR correlation < 0.5) → Predictive framework collapses
- Cumulative-matched controls eliminate ordering effects → Simple reweighting, not temporal dynamics

**Nuanced Outcome Possibilities:**
1. **Full Support (5/5 phases):** All hypotheses pass → Field-defining predictive law
2. **Strong Support (4/5 phases):** Core mechanisms validated, one phase fails → Strong contribution with caveats (e.g., scaling limits, taxonomy dependence)
3. **Partial Support (3/5 phases):** H-E1 + H-M1 pass, later mechanisms fail → Publishable curriculum effect, narrower scope
4. **Gradient Primacy Alternative:** Shuffled = diversity-ranked → Curriculum coherence (still publishable, different interpretation)
5. **No Support (≤2/5 phases):** H-E1 or H-M1 fail → H0 supported, major revision required

### 5.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| **Existence** | Performance improvement exists | May be stochastic noise or baseline artifact | H-E1 with n=5 seeds, power analysis at 7B |
| **Mechanism** | Causal chain: diversity → PR → persistence → robustness | Alternative explanations (e.g., simple reweighting) | Cumulative-matched controls, shuffled-order disambiguation |
| **Predictability** | Corpus statistics predict optimal schedules | Diversity metrics may not correlate with PR | Phase 1 correlation test (pre-registered ρ ≥ 0.7 threshold) |
| **Generality** | Applies across domains and scales | Taxonomy-dependent or small-model artifact | Phase 3 robustness test (Kendall τ ≥ 0.6), Phase 2 at 7B |
| **Persistence** | Early geometry persists through training | May wash out during later training | CKA persistence measurement (H-M2) |

**Overall Robustness Score:** Medium-High
- **Strengths:** Pre-registered protocols, contribution tiers, multiple controls (cumulative-matched, shuffled)
- **Weaknesses:** High-risk dependencies (A2 correlation, A5 scaling), mechanism chain fragility (H-M1 failure breaks subsequent tests)

**Confidence in Verification Plan:** 0.80
- Well-structured with clear gates and failure responses
- Honest acknowledgment of contingencies and alternative outcomes
- Six-phase validation provides multiple lines of evidence

---

## 6. Executive Summary

**Main Hypothesis:** H-GradGeomSchedule-v1, Confidence: 0.80
- Temporal ordering of training domains from high to low diversity improves foundation model performance through path-dependent gradient geometry

**Verification Structure:**
- **Mode:** Incremental (Phase 2A available, 75% scope reduction)
- **Sub-Hypotheses:** 5 total
  - H-E: 1 (Existence)
  - H-M: 4 (Mechanism chain)
- **Phases:** 2 phases over 7 weeks
- **Critical Gates:** 2 decision points (Gate 1: Foundation, Gate 2: First mechanism)

**Risk Assessment:** Medium-High
- **Primary concerns:**
  - Diversity-PR correlation failure (R2, Critical)
  - Scaling effect vanishing at 7B (R5, High)
- **Mitigation:** Pre-registered protocols, contribution tiers, extensive controls

**Immediate Action:** Begin Phase 2C with H-E1 experiment design

---

## 7. Conclusions

### 7.1 Key Achievements

- 5 hypotheses across 2 phases with clear dependency chain
- H0 addressed: No significant difference when total per-domain tokens matched (within ±0.5% performance, <5% geometric metrics)
- 75% scope reduction through established facts (path dependence, existing benchmarks, diverse pretraining benefits)
- Sequential verification with 2 MUST_WORK gates and 3 SHOULD_WORK hypotheses

### 7.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Diversity-ranked scheduling improves performance vs static mixture
- Gate 1: MUST PASS (if fail → STOP, reassess hypothesis)

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Early high-diversity establishes broader gradient covariance
  - Gate 2: MUST PASS (if fail → mechanism chain breaks, predictive law collapses)
- H-M2: Path-dependent optimization crystallizes representational subspaces
  - SHOULD WORK (if fail → document limitation, early geometry doesn't persist)
- H-M3: Later specialization operates within established broad subspace
  - SHOULD WORK (if fail → document limitation, specialization reduces diversity more than expected)
- H-M4: Broader geometry enables robust downstream adaptation
  - SHOULD WORK (if fail → narrow to in-distribution performance, continual learning benefit is secondary)

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - **FAIL →** STOP, reassess entire hypothesis (no phenomenon exists)
   - **PASS →** Proceed to Phase 2 mechanism testing

2. **Gate 2 (Mechanisms):** H-M1 must pass (diversity-PR correlation ≥ 0.7)
   - **CRITICAL FAIL →** Predictive law collapses to post-hoc explanation, pivot to empirical curriculum effect
   - **PASS →** Mechanism chain validated, continue sequential testing

### 7.4 Open Questions

- Optimal diversity metric combination (vocabulary entropy vs syntactic vs semantic)?
- Transition smoothness parameter tuning (step function vs linear vs cosine interpolation)?
- Domain granularity sensitivity (how to partition 'web' or 'code' without taxonomy dependence)?
- Scaling law integration (how to incorporate temporal composition into Chinchilla-style formulas)?
- Adaptive scheduling algorithms based on runtime gradient statistics?

### 7.5 Recommendations

**Immediate Actions:**
1. Start Phase 2C with H-E1 experiment design
2. Set up measurement infrastructure (PR computation, CKA similarity, Fisher overlap)
3. Pre-register all protocols before execution

**Resource Allocation:**
- Allocate 7 weeks for critical path execution
- Reserve 2-week buffer for gate failures and PIVOT execution
- Secure GPU resources (~45K GPU-hours total per Phase 2A estimate)

**Failure Management:**
- Document all failures with root cause analysis
- Execute PIVOT strategies per risk mitigation (R1-R5)
- Use contribution tiers: 5/5 phases = field-defining, 4/5 = strong, 3/5 = publishable

---

## Appendices

### A. Phase 2A Reference
- **Source:** /docs/youra_research/20260415_data_problems/03_refinement.yaml
- **Hypothesis ID:** H-GradGeomSchedule-v1
- **Causal Chain:** 4 steps (diversity → PR → persistence → robustness)
- **Confidence:** 0.80

### B. Scope Reduction Summary
- **Build-On Claims:** 3 (path dependence, existing benchmarks, diverse pretraining benefits)
- **Prove-New Claims:** 1 (temporal ordering via gradient geometry)
- **Efficiency Gain:** 75% of baseline claims excluded from re-verification

### C. Hypothesis-Risk Mapping
- H-E1 affected by: R1 (path dependence symmetry), R5 (scaling vanishing)
- H-M1 affected by: R2 (diversity-PR correlation - CRITICAL)
- H-M2 affected by: R3 (geometric non-persistence)
- H-M3 affected by: R3 (geometric non-persistence)
- H-M4 affected by: R4 (Fisher-forgetting decoupling)

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-04-15*
*Mode: Incremental (Phase 2A available) | UNATTENDED execution*

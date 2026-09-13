# Verification Plan: API Contracts for ML Reproducibility

**Date:** 2026-07-11
**Hypothesis ID:** H-APIContracts-v1
**Confidence:** 0.78
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under ML reengineering workflows (computer vision focus), if researchers validate library behavioral assumptions via executable API contracts at environment-setup time, then environment-stage API defects reduce by ≥30% relative to version-pinning + CI baseline (≥25% marginal reduction over CI-only), with ≥5-hour earlier detection (lifecycle shift from training-stage to environment-stage), because contracts proactively intercept assumption violations through composition-level invariants (structural, metamorphic, cross-library) that execute in ≤10 seconds before any training begins.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in environment-stage API defect rate or time-to-detection between version-pinning + CI-only and version-pinning + CI + API contracts.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Jiang et al. 348-Defect Corpus + Live GitHub Repos (standard + real-world) | Jiang et al. provides ecological validity (real reengineering defects); live trial tests marginal value in practice |
| **Model** | API contract validation framework | Contracts are the 'model' — hypothesis tests their defect detection efficacy |

**Dataset Details:**
- Source: Published dataset (Jiang et al. 2023) + ≥1K stars CV repos from GitHub
- Path: Phase 1: Retrospective coding, Phase 2: Version-Transition Benchmark, Phase 3: Randomized trial on live repos

**Model Details:**
- Type: API contract validation framework
- Source: Pre-built library for PyTorch/HuggingFace/JAX + auto-generation pipeline

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| No-CI (Control) | Version pinning only, no automated testing | Mirrors 75% of ML repos per Wolter et al. |
| CI-Only (Best-Practice Baseline) | pytest + integration tests + version pinning | Current best practice |
| Execution-Only (Adversarial Baseline) | Import + minimal forward pass | Catches obvious crashes, not subtle invariant violations |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | ≥40% of environment-stage API defects are expressible as version-stable, lightweight executable invariants | 88% of environment defects are interface defects — if structural/binding assumptions, likely contractable | If <40% contractability, the 30% reduction claim becomes implausible |
| A2 | Libraries document behavioral invariants with sufficient precision for auto-generation | Many docstrings specify return types, shapes, mathematical properties | Auto-generation limited; fallback to manual curation for Category B (metamorphic) invariants |
| A3 | Invariants remain stable across adjacent minor library versions (±2 releases) | Semantic versioning conventions — minor versions preserve documented API behavior | If invariants change frequently, contracts become brittle and high-maintenance |
| A4 | ML researchers will adopt contracts if provided as pre-built library with one-line validation | Wolter et al. shows low-friction interventions can shift adoption | If adoption friction too high, field-level impact limited despite technical efficacy |
| A5 | Contract failures provide actionable error messages that guide debugging faster than trial-and-error | h-e1 run 1: hours debugging empty tuple → would be <10s with contract assert message | If error messages unclear, time-to-resolution may not improve despite earlier detection |

### 1.6 Research Gap & Novelty

**Gap:** 88% of environment defects are interface defects, 46% are API defects (Jiang et al., 2023). Yet 75% of ML repos lack automated testing, <50% specify dependencies (Wolter et al., 2025). Current practice relies on version pinning + manual debugging.

**Novelty:** First systematic measurement of API defect contractability in ML context. Library-level behavioral abstraction with cross-repo reusability + auto-generation from documentation + lifecycle-stage shift as measurable outcome.

**Differentiation:**
- vs. Property-based testing (QuickCheck, Hypothesis): Applied specifically to ML API reproducibility layer, not general software testing
- vs. Design-by-Contract (Eiffel, dependent types): Lightweight pre-training validation (≤10s), not full formal verification
- vs. Integration testing (pytest, tox): Library-level invariants (cross-repo reusable) vs repo-specific test suites
- vs. Wolter et al. 2025 reproducibility measurement: Concrete intervention with measurable defect reduction, not just practice gap survey
- vs. Jiang et al. 2023 defect taxonomy: Preventive tooling with empirical validation, not descriptive characterization

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Contractability of Environment-Stage API Defects**

**Type:** EXISTENCE
**Statement:** Under ML reengineering workflows, if API behavioral invariants (structural, metamorphic, composition-level) are expressible as lightweight executable contracts, then ≥40% of environment-stage API defects from Jiang et al.'s corpus are contractable with ≤10s validation time and version stability across ±2 minor releases.

**Rationale:** This hypothesis validates the foundational assumption (A1) that a sufficient proportion of real-world API defects can be expressed as executable contracts. Without this, the entire approach becomes impractical.

**Variables:**
- Independent: Defect type (structural, metamorphic, composition-level)
- Dependent: Contractability rate (% of defects expressible as contracts)
- Controlled: Repository maturity, defect corpus source (Jiang et al. 2023)

**Verification Protocol:**
1. Load Jiang et al. 348-defect corpus, filter for environment-stage API defects
2. Two independent coders apply 3-question filter: (1) Documented invariant exists? (2) Evaluable in ≤10s? (3) Version-stable ±2 releases?
3. Calculate contractability rate with 95% CI, check inter-rater reliability (Cohen's kappa ≥0.7)
4. Stratify by defect category (structural, metamorphic, composition-level)
5. Compare contractability rate to 40% threshold

**Success Criteria:**
- Primary: Contractability rate ≥40% with 95% CI lower bound >35%
- Secondary: Inter-rater reliability Cohen's kappa ≥0.7

**Gate:**
- Type: MUST_WORK
- If Fail: If <40%, PIVOT to structural-only contracts with reduced scope claims

**Prerequisites:** None (foundation)

**Source:** Phase 2A Prediction P1, Assumption A1

---
**H-M1: Structural Invariant Validation at Import Time**

**Type:** MECHANISM
**Statement:** Under ML reengineering workflows, if contracts validate documented structural invariants (return types, tensor shapes, non-null outputs) at import time, then these contracts detect structural API violations before any training code executes.

**Rationale:** This tests the first step of the causal mechanism. Structural invariants are the most basic and easily documentable category, forming the foundation for more complex contract types.

**Variables:**
- Independent: Contract presence (structural validation enabled/disabled)
- Dependent: Structural API defect detection rate at environment-stage
- Controlled: Library versions, import sequence

**Verification Protocol:**
1. Implement structural contracts for PyTorch/HuggingFace APIs (return types, tensor shapes, non-null checks)
2. Deploy to test repos with known structural violations from Jiang et al. corpus
3. Measure detection rate at import time vs. runtime
4. Verify execution time ≤10s for import-time validation
5. Test version stability across ±2 minor releases

**Success Criteria:**
- Primary: Structural contracts detect ≥80% of structural API defects at import time
- Secondary: Execution time ≤10s, false positive rate <5%

**Gate:**
- Type: MUST_WORK
- If Fail: If detection rate <60%, mechanism fails — reassess contract design

**Prerequisites:** H-E1 (contractability validated)

**Source:** Phase 2A Causal Step 1

---
**H-M2: Metamorphic Property Enforcement via Lightweight Probes**

**Type:** MECHANISM
**Statement:** Under ML reengineering workflows, if contracts enforce metamorphic mathematical properties (softmax sums, dropout identity) via lightweight probes, then mathematical invariant violations are detected at environment-stage before training begins.

**Rationale:** Tests the second causal step. Metamorphic properties are version-stable mathematical guarantees that don't require full inference, enabling fast validation.

**Variables:**
- Independent: Metamorphic contract presence (enabled/disabled)
- Dependent: Metamorphic property violation detection rate
- Controlled: Library versions, probe complexity (≤10s constraint)

**Verification Protocol:**
1. Implement metamorphic contracts (softmax sums to 1, dropout identity on eval mode, etc.)
2. Deploy to test repos with known mathematical invariant violations
3. Measure detection rate and execution time
4. Test version stability across library updates
5. Validate false positive rate on valid library usage

**Success Criteria:**
- Primary: Metamorphic contracts detect ≥70% of mathematical invariant violations
- Secondary: Execution time ≤10s, version stability across ±2 releases

**Gate:**
- Type: SHOULD_WORK
- If Fail: If detection rate <50%, document limitation — structural contracts still viable

**Prerequisites:** H-M1 (structural validation working)

**Source:** Phase 2A Causal Step 2

---
**H-M3: Cross-Library Composition-Level Contract Validation**

**Type:** MECHANISM
**Statement:** Under ML reengineering workflows, if cross-library composition-level contracts validate binding assumptions (device placement, tensor layout consistency), then cross-library interaction defects are detected at environment-stage.

**Rationale:** Tests the third causal step. Many API defects arise from cross-library interactions (Torch + CUDA + Transformers version triads), requiring composition-level validation.

**Variables:**
- Independent: Composition-level contract presence (enabled/disabled)
- Dependent: Cross-library defect detection rate
- Controlled: Library version combinations, device configurations

**Verification Protocol:**
1. Implement composition-level contracts for common library triads (PyTorch + CUDA + Transformers)
2. Deploy to test repos with known cross-library interaction failures
3. Measure detection rate for composition-level defects
4. Validate execution time ≤10s for composition checks
5. Test robustness across version combinations

**Success Criteria:**
- Primary: Composition contracts detect ≥60% of cross-library interaction defects
- Secondary: Execution time ≤10s, applicable to ≥3 distinct repos

**Gate:**
- Type: SHOULD_WORK
- If Fail: If detection rate <40%, document as manual curation requirement

**Prerequisites:** H-M2 (metamorphic validation working)

**Source:** Phase 2A Causal Step 3

---
**H-M4: Lifecycle Shift to Environment-Stage Detection**

**Type:** MECHANISM
**Statement:** Under ML reengineering workflows with CI + Contracts deployed, if contracts execute at environment-setup time, then defect detection shifts from training-stage (median 68% per Jiang et al.) to environment-stage, with ≥5-hour earlier median time-to-first-failure compared to CI-only baseline.

**Rationale:** Tests the final causal step and key outcome. Lifecycle shift is the practical benefit — earlier detection saves researcher time and enables faster debugging.

**Variables:**
- Independent: Validation strategy (No-CI / CI-only / CI+Contracts)
- Dependent: Time-to-first-failure (hours), stage-of-first-failure (environment vs. training)
- Controlled: Repository maturity, reporter type

**Verification Protocol:**
1. Conduct randomized PR-level trial on live GitHub repos (≥1K stars CV repos)
2. Stratify by repo maturity and reporter type (58% re-users per Jiang et al.)
3. Measure time-to-first-failure from CI log timestamps
4. Measure stage-of-first-failure (environment vs. training)
5. Calculate marginal detection improvement: CI+Contracts vs. CI-only

**Success Criteria:**
- Primary: Median time-to-first-failure reduced by ≥5 hours with CI+Contracts vs. CI-only
- Secondary: CI+Contracts detects ≥25% more environment-stage API defects than CI-only (marginal improvement)

**Gate:**
- Type: SHOULD_WORK
- If Fail: If lifecycle shift <3h, insufficient practical impact — document as incremental improvement

**Prerequisites:** H-M3 (composition validation working)

**Source:** Phase 2A Causal Step 4, Predictions P2 & P3

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
| H-E1 | MUST_WORK | Contractability ≥40% | PIVOT to structural-only contracts |
| H-M1 | MUST_WORK | Detection rate ≥80% for structural defects | Reassess contract design |
| H-M2 | SHOULD_WORK | Detection rate ≥70% for metamorphic violations | Document limitation |
| H-M3 | SHOULD_WORK | Detection rate ≥60% for composition defects | Document as manual curation |
| H-M4 | SHOULD_WORK | Lifecycle shift ≥5h, marginal detection ≥25% | Document as incremental improvement |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1 (2w), H-M2 (1w), H-M3 (1w), H-M4 (2w) | 6 weeks |

**Total Duration:** 8 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 (Contractability assumption) | H-E1, H-M1 | Critical |
| R2 | A2 (Documentation precision) | H-M1, H-M2, H-M3 | High |
| R3 | A3 (Version stability) | H-M2, H-M3, H-M4 | High |
| R4 | A4 (Adoption friction) | H-M4 | Medium |
| R5 | A5 (Error message clarity) | H-M4 | Medium |

### 4.2 Mitigation Strategies

**Risk R1: Low Contractability Rate**

**Source Assumption:** A1 - ≥40% of environment-stage API defects are expressible as version-stable, lightweight executable invariants

**Description:** If contractability rate <40%, the 30% defect reduction claim becomes implausible.

**Affected Hypotheses:** H-E1, H-M1

**Severity:** Critical

**Mitigation Strategy:**
1. **Prevention:** Pilot study on 50-defect sample before full corpus coding
2. **Detection:** Track contractability rate by defect category (structural, metamorphic, composition)
3. **Response:**
   - PIVOT: Focus on structural-only contracts (typically >60% contractable)
   - SCOPE: Reduce claims from 30% to 15-20% defect reduction
   - ABORT: If contractability <25%, hypothesis invalidated

**Early Warning Indicators:**
- Pilot study contractability <35%
- Structural defects <50% contractable

---

**Risk R2: Insufficient Documentation Precision**

**Source Assumption:** A2 - Libraries document behavioral invariants with sufficient precision for auto-generation

**Description:** If documentation too vague, auto-generation fails, requiring manual contract curation.

**Affected Hypotheses:** H-M1, H-M2, H-M3

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Survey top 10 ML libraries for documentation quality before design
2. **Detection:** Track auto-generation success rate by library
3. **Response:**
   - PIVOT: Hybrid approach (auto-generation + manual curation)
   - SCOPE: Focus on well-documented libraries (PyTorch, HuggingFace)
   - ABORT: If manual curation >80% of contracts, auto-generation claim invalid

**Early Warning Indicators:**
- Auto-generation success rate <40%
- Manual curation required for >60% of contracts

---

**Risk R3: Version Instability (High False Positive Rate)**

**Source Assumption:** A3 - Invariants remain stable across adjacent minor library versions (±2 releases)

**Description:** If invariants change frequently, contracts become brittle (false positives >5%).

**Affected Hypotheses:** H-M2, H-M3, H-M4

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Version-Transition Benchmark on 20 real PyTorch/HuggingFace version deltas
2. **Detection:** Track false positive rate on valid library usage
3. **Response:**
   - PIVOT: Version-specific contracts (sacrifices cross-version reusability)
   - SCOPE: Focus on LTS library versions only
   - ABORT: If false positive rate >8%, contracts too brittle for adoption

**Early Warning Indicators:**
- False positive rate >5% in benchmark
- Breaking changes in >20% of minor version updates

---

**Risk R4: Low Adoption Due to Friction**

**Source Assumption:** A4 - ML researchers will adopt contracts if provided as pre-built library with one-line validation

**Description:** If adoption friction too high, field-level impact limited despite technical efficacy.

**Affected Hypotheses:** H-M4

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** User study on 10 researchers for usability feedback
2. **Detection:** Track adoption rate in randomized trial
3. **Response:**
   - PIVOT: Improve UX (auto-detect libraries, zero-config setup)
   - SCOPE: Target research labs with existing CI infrastructure
   - ABORT: If adoption rate <20% in trial, distribution model needs redesign

**Early Warning Indicators:**
- User study feedback indicates >2 steps to setup
- Trial adoption rate <30%

---

**Risk R5: Unclear Error Messages**

**Source Assumption:** A5 - Contract failures provide actionable error messages that guide debugging faster than trial-and-error

**Description:** If error messages unclear, time-to-resolution may not improve despite earlier detection.

**Affected Hypotheses:** H-M4

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Error message templates with actionable guidance (e.g., "Expected tensor shape [B, C, H, W], got [B, H, W]")
2. **Detection:** User study on error message comprehension
3. **Response:**
   - PIVOT: Improve error message formatting (include fix suggestions, relevant docs)
   - SCOPE: Focus on high-frequency defect patterns
   - ABORT: If debugging time not reduced, lifecycle shift benefit negated

**Early Warning Indicators:**
- User study comprehension <70%
- Debugging time not reduced in trial

---

### 4.3 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Low contractability rate | A1 | Critical | H-E1, H-M1 | Pilot study, PIVOT to structural-only |
| R2 | Insufficient documentation | A2 | High | H-M1-3 | Survey libraries, hybrid auto+manual |
| R3 | Version instability | A3 | High | H-M2-4 | Version-Transition Benchmark, LTS focus |
| R4 | Low adoption friction | A4 | Medium | H-M4 | User study, UX improvements |
| R5 | Unclear error messages | A5 | Medium | H-M4 | Error message templates, user testing |

**Critical Risks:** 1
**High Risks:** 2
**Medium Risks:** 2

---

## 5. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 to 4 - Mechanisms]
    H-M1 ← H-E1
         │
         ▼
    H-M2 ← H-M1
         │
         ▼
    H-M3 ← H-M2
         │
         ▼
    H-M4 ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.1 Verification Phases with Gate Conditions

**Phase 1 - Foundation**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | Contractability validation | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP, reassess entire hypothesis.

**Phase 2 - Core Mechanisms** (4 hypotheses)
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST PASS |
| H-M2 | H-M1 | Should pass |
| H-M3 | H-M2 | Should pass |
| H-M4 | H-M3 | Should pass |

→ **Gate 2**: H-M1 must pass. Later H-M failures = document limitation.

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

---

## 6. Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3-4 │ W5 │ W6 │ W7-8 │
─────────────────┼──────┼──────┼────┼────┼──────┤
PHASE 1: Foundation
  H-E1           │ ████ │      │    │    │      │
  [Gate 1]       │      │ ◆    │    │    │      │
─────────────────┼──────┼──────┼────┼────┼──────┤
PHASE 2: Mechanisms
  H-M1           │      │ ████ │    │    │      │
  H-M2           │      │      │ ██ │    │      │
  H-M3           │      │      │    │ ██ │      │
  H-M4           │      │      │    │    │ ████ │
  [Gate 2]       │      │      │    │    │    ◆ │
─────────────────┼──────┼──────┼────┼────┼──────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 8 weeks
═══════════════════════════════════════════════════════════════════
```

### 6.1 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Total Duration:** 8 weeks
- Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 2 (H-M4) = 8 weeks

**Slack Available:** 0 weeks (all sequential)

### 6.2 Resource Summary

**Total Hypotheses:** 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)

**Verification Phases:** 2
1. Foundation (H-E1)
2. Mechanisms (H-M1-4)

**Total Duration:** 8 weeks
**Critical Path Length:** 8 weeks
**Execution Mode:** Sequential chain

### 6.3 Execution Order

**Step 1**: Execute H-E1 (Foundation) - Week 1-2
**Step 2**: Evaluate Gate 1 → If pass, proceed
**Step 3**: Execute H-M1 (First mechanism) - Week 3-4
**Step 4**: Execute H-M2 to H-M4 sequentially - Week 5-8
**Step 5**: Evaluate Gate 2 → If pass, proceed to Phase 5
**Final**: Verification complete

---

## 7. Dialectical Analysis

### 7.1 Thesis

**Core Claim:** Under ML reengineering workflows, executable API contracts at environment-setup time reduce environment-stage API defects by ≥30% with ≥5-hour earlier detection through proactive invariant validation.

**Supporting Evidence:**
1. 88% of environment defects are interface defects, 46% are API defects (Jiang et al., 2023)
2. Structural/metamorphic invariants are version-stable and documentable
3. Lifecycle shift from training-stage (68% of defects) to environment-stage is measurable

**Strengths:**
- Based on empirical defect corpus (Jiang et al. 2023)
- Clear 4-step causal mechanism with testable predictions
- Addresses real pain point (75% of ML repos lack testing)

**Expected Outcomes:**
- Primary: ≥40% contractability rate
- Secondary: ≥25% marginal detection improvement
- Tertiary: ≥5-hour lifecycle shift

### 7.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in environment-stage API defect rate or time-to-detection between version-pinning + CI-only and version-pinning + CI + API contracts.

**Counter-Arguments:**
1. Baseline CI-only already catches many API defects (marginal value may be low)
2. Documentation quality varies across libraries (auto-generation may fail)
3. Version instability may cause high false positive rates (>5%)

**Potential Failure Points:**
- Contractability rate <40% (A1 violated)
- Auto-generation success rate <40% (A2 violated)
- False positive rate >5% (A3 violated)

**Conditions Under Which H0 Would Be Supported:**
- If contractability <40% (H-E1 fails)
- If structural contract detection rate <80% (H-M1 fails)
- If marginal detection improvement <15% (insufficient practical impact)

### 7.3 Synthesis

**Balanced Assessment:**

The hypothesis H-APIContracts-v1 presents a testable claim that executable API contracts can reduce environment-stage API defects by ≥30% through proactive invariant validation. However, the null hypothesis raises valid concerns regarding contractability limits, documentation quality, and marginal value over existing CI practices.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes contractability ≥40% before mechanism testing
2. **Sequential mechanism testing (H-M1-4):** Tests each causal step independently
3. **Gate conditions:** Allow early detection of H0 support (PIVOT strategies at each gate)

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1)
- Contractability ≥40% is confirmed
- Marginal detection improvement ≥25%
- Lifecycle shift ≥5 hours

**Conditions for Antithesis Support:**
- H-E1 fails (contractability <40%)
- H-M1 fails (structural detection <60%)
- Marginal improvement <15% (incremental, not breakthrough)

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, 30% defect reduction claim supported
2. **Partial Support:** H-E1 + H-M1 pass, H-M2-4 partial → Refined thesis with structural-only contracts (15-20% reduction)
3. **No Support:** H-E1 or H-M1 fail → Antithesis supported, contractability assumption invalid

### 7.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | ≥40% of defects contractable | Documentation too vague | H-E1 blinded coding test |
| Mechanism | 4-step causal chain valid | CI-only already catches many | H-M1-4 sequential tests with marginal value measurement |
| Scope | Applies to environment-stage API defects | Limited to well-documented libraries | Stratification by library in trial |
| Performance | ≥30% defect reduction | Marginal improvement <15% | Randomized trial with CI-only baseline |

**Overall Robustness Score:** Medium-High
- Strong empirical foundation (Jiang et al. corpus)
- Clear causal mechanism with falsifiable predictions
- Risk: Contractability assumption (A1) is critical and untested

**Confidence in Verification Plan:** 0.78

---

## 8. Executive Summary

**Main Hypothesis:** Under ML reengineering workflows, executable API contracts at environment-setup time reduce environment-stage API defects by ≥30% with ≥5-hour earlier detection through proactive invariant validation.
- ID: H-APIContracts-v1, Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (Phase 2A pre-mapped)
- Sub-Hypotheses: 5 total
  - H-E: 1, H-M: 4
- Phases: 2 phases over 8 weeks
- Critical Gates: 2 decision points (Gate 1: H-E1, Gate 2: H-M1)

**Risk Assessment:** Medium
- Primary concerns: Contractability rate <40% (R1), documentation quality (R2)

**Immediate Action:** Begin Phase 1 with H-E1 (blinded retrospective coding on Jiang et al. corpus)

---

## 9. Conclusions

### 9.1 Key Achievements
- 5 hypotheses across 2 phases (Foundation + Mechanisms)
- H0 addressed: No significant difference in defect rate/time-to-detection between CI-only and CI+Contracts
- Sequential verification with PIVOT strategies at each gate

### 9.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Contractability validation (≥40% of defects expressible as contracts)
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (6 weeks)
- H-M1: Structural invariant validation (detection rate ≥80%)
- H-M2: Metamorphic property enforcement (detection rate ≥70%)
- H-M3: Cross-library composition validation (detection rate ≥60%)
- H-M4: Lifecycle shift to environment-stage (≥5h earlier, ≥25% marginal detection)
- Gate 2: H-M1 must pass

### 9.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess hypothesis (contractability <40% invalidates approach)
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Execute PIVOT to structural-only contracts
   - OPTIONAL FAIL (H-M2-4) → Document limitation, proceed with reduced scope

### 9.4 Open Questions
- What is the actual contractability rate for environment-stage API defects in Jiang et al. corpus?
- Can auto-generation achieve >60% success rate across top 10 ML libraries?
- What is the false positive rate on real version transitions (±2 minor releases)?

### 9.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 (blinded retrospective coding)
   - Recruit 2 independent coders for inter-rater reliability

2. **Resource Allocation:**
   - Allocate 8 weeks for critical path (H-E1 → H-M1 → H-M2 → H-M3 → H-M4)
   - Reserve 2-week buffer for PIVOT execution if gates fail

3. **Failure Management:**
   - Document all failures with root cause analysis
   - Execute PIVOT strategies (structural-only, hybrid auto+manual, LTS versions)
   - Update verification_state.yaml with gate satisfaction status

---

## 10. Appendices

### A. Phase 2A Reference
- **Source:** /workspace/TEST_scope/docs/youra_research/03_refinement.yaml
- **ID:** H-APIContracts-v1
- **Causal Chain:** 4 steps (structural → metamorphic → composition → lifecycle shift)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 2
- **Tools:** scientificmethod (hypothesis + experiment stages)
- **Inquiries:** H-E1-verification, H-M-integrated (decomposed to H-M1-4)

---

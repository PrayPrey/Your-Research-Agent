# Verification Plan: Error-Type-Gated Fine-Grained Execution Feedback

**Date:** 2026-08-19
**Hypothesis ID:** H-ErrorGatedFeedback-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## Executive Summary

**Main Hypothesis:** Under controlled RL fine-tuning of code LLMs, if fine-grained execution feedback is applied only to errors with reliable source localization (U_line category), then training sample efficiency improves compared to unconditional fine-grained application, because gating reduces noisy credit assignment from unreliably-localized errors.
- ID: H-ErrorGatedFeedback-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total
  - H-E: 1, H-M: 4
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: Effect size may be small (~10-15% U_ignore frequency), error categorization accuracy

**Immediate Action:** Begin Phase 1 with H-E1

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under controlled RL fine-tuning of code LLMs (same model, dataset, compute budget), if fine-grained execution feedback is applied only to errors with reliable source localization (U_line category errors where traceback provides accurate line numbers), then training sample efficiency improves compared to unconditional fine-grained application, because gating reduces noisy credit assignment from unreliably-localized errors.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in sample efficiency or final accuracy between error-type-gated and unconditional fine-grained feedback application.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | APPS (standard) | 5000 training problems provides statistical power; standard code RL benchmark |
| **Model** | CodeT5-large | Same as RLTF baseline; 770M parameters trainable on available compute |

**Dataset Details:**
- Source: https://github.com/hendrycks/apps
- Path: datasets/apps/

**Model Details:**
- Type: encoder-decoder
- Source: Salesforce/codet5-large

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| RLTF combined (coarse+fine+adaptive) | ~35% pass@1 | APPS |
| CodeRL | ~30% pass@1 | APPS |
| VeRPO | +8.83 pass@1 over GRPO | LiveCodeBench, MBPP, HumanEval |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | RLTF error categorization accurately reflects localization reliability | RLTF Appendix B; based on Python exception types | Gating would not separate reliable from unreliable localization |
| A2 | Error type distribution shifts during training (more U_line later) | Training dynamics: early syntax errors, later logic errors | Phase interaction prediction fails |
| A3 | Gradient signal-to-noise at error tokens correlates with efficiency | Standard RL theory: noisy gradients slow convergence | P4 gradient metric wouldn't explain P1 |
| A4 | U_ignore errors occur frequently enough (~10-15%) | Prof. Pax estimate from APPS analysis | Effect size too small to detect |
| A5 | RLTF codebase accurately implements described reward scheme | Open-source code matches paper; verified | Replication fails |

### 1.6 Research Gap & Novelty

**Key Innovation:** Error-type-gated application of fine-grained feedback based on localization reliability.

**Gap:** No prior work tests conditional application of feedback based on error type as a credit assignment reliability signal. RLTF applies all feedback unconditionally; VeRPO addresses cardinality bias but not localization reliability.

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

#### H-E1: Error-Type Gating Improves Sample Efficiency

**Type:** EXISTENCE
**Statement:** Under controlled RL fine-tuning on APPS, if fine-grained feedback is applied only to U_line errors, then training reaches 30% pass@1 >10% faster than unconditional application.

**Rationale:** This establishes whether error-type gating produces any measurable benefit before testing mechanism. RLTF shows multi-granularity helps; we test whether selective application further improves efficiency.

**Variables:**
- Independent: feedback_gating_strategy (fine_always vs fine_gated)
- Dependent: sample_efficiency (steps to 30% pass@1)
- Controlled: base_model, dataset, compute_budget, coarse_reward

**Verification Protocol:**
1. Train CodeT5-large on APPS with Fine-always (RLTF default) for 5 epochs across 3-5 seeds
2. Train identical setup with Fine-gated (U_line only) across 3-5 seeds
3. Log pass@1 at each checkpoint; record steps to reach 30% threshold
4. Compare distributions with paired t-test (p<0.05)
5. Compute efficiency ratio: (Steps_fine_always - Steps_fine_gated) / Steps_fine_always

**Success Criteria:**
- Primary: Efficiency ratio > 0.10 (Fine-gated 10%+ faster)
- Secondary: p<0.05 on paired t-test

**Failure Response:**
- IF fails: PIVOT to examining other efficiency thresholds (20%, 40%)

**Dependencies:** None

**Source:** Phase 2A SH1, Prediction P1

---

#### H-M1: Fine-Grained Feedback Targets Error Line Tokens

**Type:** MECHANISM
**Statement:** Under RLTF's fine-grained reward scheme, if an error occurs, then reward penalties are applied specifically to tokens at the error line location via traceback parsing.

**Rationale:** This validates the first causal step - that fine-grained feedback actually localizes credit to specific tokens. Without this, gating would have no mechanism to operate on.

**Variables:**
- Independent: error occurrence with traceback
- Dependent: gradient distribution across tokens
- Controlled: reward scheme (RLTF Eq 4-5), model architecture

**Verification Protocol:**
1. Generate failing code samples that produce errors with tracebacks
2. Apply RLTF fine-grained reward calculation
3. Compute gradients and measure concentration at error-line tokens
4. Verify >80% of penalty gradient concentrates within ±2 lines of traceback location
5. Document any systematic localization failures

**Success Criteria:**
- Primary: Gradient concentration at error-line > gradient_other_lines
- Secondary: >80% penalty within ±2 lines

**Failure Response:**
- IF fails: EXPLORE alternative localization mechanisms

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---

#### H-M2: Error Localization Varies by Type

**Type:** MECHANISM
**Statement:** Under RLTF's error categorization, if errors are classified as U_line vs U_ignore, then U_line errors have significantly higher localization accuracy than U_ignore errors.

**Rationale:** Tests whether RLTF's categorization actually separates reliable from unreliable localization. This is the foundation for gating logic.

**Variables:**
- Independent: error category (U_line vs U_ignore)
- Dependent: localization accuracy (correct line identification rate)
- Controlled: error traceback format, Python version

**Verification Protocol:**
1. Collect 500+ error samples from APPS training, categorized by RLTF rules
2. For each error, compare traceback-reported line to actual bug location
3. Compute accuracy per category: correct_line / total_errors
4. Compare U_line accuracy vs U_ignore accuracy
5. Statistical test: chi-square for accuracy difference

**Success Criteria:**
- Primary: U_line accuracy > U_ignore accuracy (p<0.05)
- Secondary: U_line accuracy >80%, U_ignore accuracy <60%

**Failure Response:**
- IF fails: PIVOT to refined categorization scheme

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---

#### H-M3: Unreliable Localization Causes Gradient Noise

**Type:** MECHANISM
**Statement:** Under fine-grained feedback with U_ignore errors, if penalties are applied at traceback-reported locations, then gradient signal concentrates at wrong tokens, measurably increasing noise.

**Rationale:** Tests the noise injection mechanism - when localization is unreliable, gradients go to wrong places, harming learning.

**Variables:**
- Independent: error type (U_line vs U_ignore) with fine-grained penalty
- Dependent: gradient_error_line / gradient_other ratio
- Controlled: penalty magnitude, model state

**Verification Protocol:**
1. Sample 200+ training examples with U_line errors, 200+ with U_ignore errors
2. Apply fine-grained penalty to each
3. Compute gradient concentration ratio for each sample
4. Compare distributions: mean ratio(U_line) vs mean ratio(U_ignore)
5. Test whether U_ignore shows significantly lower concentration (noisier)

**Success Criteria:**
- Primary: gradient_concentration(U_line) > gradient_concentration(U_ignore)
- Secondary: Difference statistically significant (p<0.05)

**Failure Response:**
- IF fails: EXPLORE whether noise manifests differently

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3

---

#### H-M4: Gating Removes Noise, Improves Signal

**Type:** MECHANISM
**Statement:** Under fine-gated feedback (U_line only), if U_ignore errors are excluded from fine-grained penalties, then overall gradient signal-to-noise improves compared to fine-always.

**Rationale:** Final mechanism step - proves that gating actually improves gradient quality, explaining the efficiency gain in H-E1.

**Variables:**
- Independent: gating strategy (fine_always vs fine_gated)
- Dependent: aggregate gradient signal-to-noise ratio
- Controlled: training samples, model checkpoints

**Verification Protocol:**
1. Train with Fine-always, log gradient metrics at checkpoints
2. Train with Fine-gated, log gradient metrics at checkpoints
3. Compute signal-to-noise: mean(gradient_at_correct_location) / std(gradient_noise)
4. Compare across training: Fine-gated SNR vs Fine-always SNR
5. Correlate SNR improvement with efficiency improvement from H-E1

**Success Criteria:**
- Primary: Fine-gated SNR > Fine-always SNR
- Secondary: SNR improvement correlates with efficiency gain (r>0.5)

**Failure Response:**
- IF fails: EXPLORE alternative explanations for efficiency gain

**Dependencies:** H-M3

**Source:** Phase 2A Causal Step 4, Prediction P4

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Efficiency ratio > 0.10 | STOP, reassess hypothesis |
| H-M1 | MUST_WORK | Gradient concentration at error line | STOP, localization broken |
| H-M2 | SHOULD_WORK | U_line > U_ignore accuracy | Document limitation |
| H-M3 | SHOULD_WORK | Concentration difference significant | Document limitation |
| H-M4 | SHOULD_WORK | Fine-gated SNR > Fine-always SNR | Document limitation |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks |

**Total Duration:** 6 weeks

---

## 4. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanism Chain]
    H-M1 ← H-E1 (Fine-grained targets error line)
         │
         ▼
    H-M2 ← H-M1 (Localization varies by type)
         │
         ▼
    H-M3 ← H-M2 (Unreliable causes noise)
         │
         ▼
    H-M4 ← H-M3 (Gating improves signal)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

---

## 5. Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1-2     │ W3-4     │ W5       │ W6
────────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 1: Foundation │          │          │          │
  H-E1              │ ████████ │          │          │
  [Gate 1]          │          │ ◆        │          │
────────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 2: Mechanisms │          │          │          │
  H-M1              │          │ ████████ │          │
  H-M2              │          │          │ ████     │
  H-M3              │          │          │     ████ │
  H-M4              │          │          │          │ ████
  [Gate 2]          │          │          │          │     ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### Critical Path Analysis

- Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
- Total Duration: 6 weeks (2 + 4)
- Slack Available: 0 weeks (fully sequential)

### Resource Summary

- Total Hypotheses: 5
  - Existence: 1 (H-E1)
  - Mechanism: 4 (H-M1 to H-M4)
- Verification Phases: 2
- Execution Mode: Sequential chain

---

## 6. Risk Analysis

### 6.1 Assumption-Risk Mapping

| Risk | Source | Description | Severity | Affected |
|------|--------|-------------|----------|----------|
| R1 | A1 | RLTF categorization doesn't reflect actual localization reliability | High | H-M2, H-M3 |
| R2 | A2 | Error distribution doesn't shift during training | Medium | H-M4 |
| R3 | A3 | Gradient noise doesn't correlate with efficiency | Medium | H-M3, H-M4 |
| R4 | A4 | U_ignore frequency too low (<10%) for detectable effect | High | H-E1 |
| R5 | A5 | RLTF implementation bugs break replication | Low | All |

### 6.2 Mitigation Strategies

**Risk R1: Categorization Accuracy**
- Prevention: Pre-validate categorization on 500 error samples before main experiment
- Detection: Monitor accuracy per category during H-M2
- Response: PIVOT to empirically-derived categories if RLTF scheme fails

**Risk R2: Distribution Shift**
- Prevention: Track error type distribution at each checkpoint
- Detection: Analyze first vs last quartile distributions
- Response: Effect may exist even without shift; document as limitation

**Risk R3: Gradient-Efficiency Correlation**
- Prevention: Include gradient metrics from epoch 1
- Detection: Compute correlation coefficient during H-M4
- Response: If no correlation, mechanism explanation is wrong but effect may still exist

**Risk R4: Effect Size**
- Prevention: Power analysis suggests 5 seeds for ~10% effect detection
- Detection: Early stopping if no signal after 3 seeds
- Response: PIVOT to lower efficiency thresholds (5%) or larger model

**Risk R5: Implementation Bugs**
- Prevention: Code review against paper equations
- Detection: Unit tests for reward calculation
- Response: Fix bugs and re-run

### 6.3 Risk Summary Table

| ID | Risk | Severity | Likelihood | Mitigation |
|----|------|----------|------------|------------|
| R1 | Categorization accuracy | High | Medium | Pre-validate on 500 samples |
| R2 | No distribution shift | Medium | Low | Track distributions |
| R3 | No gradient correlation | Medium | Medium | Include early metrics |
| R4 | Small effect size | High | Medium | Use 5 seeds |
| R5 | Implementation bugs | Low | Low | Code review |

---

## 7. Dialectical Analysis

### 7.1 Thesis

**Core Claim:** Error-type-gated fine-grained execution feedback improves code generation training efficiency by concentrating credit assignment where error localization is reliable.

**Supporting Evidence:**
1. RLTF demonstrates multi-granularity feedback improves over single-signal (Table 3 ablation)
2. VeRPO shows aggregation strategy matters (cardinality bias)
3. RL theory: credit assignment noise slows convergence

**Strengths:**
- Clear causal mechanism grounded in RL theory
- 4 testable predictions with explicit falsification criteria
- Builds on established RLTF framework

**Expected Outcomes:**
- Primary: Fine-gated reaches 30% pass@1 >10% faster than Fine-always
- Secondary: Error distribution shifts toward U_line during training
- Tertiary: Gradient concentration higher for Fine-gated

### 7.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in sample efficiency or final accuracy between error-type-gated and unconditional fine-grained feedback application.

**Counter-Arguments:**
1. U_ignore errors are only 10-15% of total - effect may be too small to detect
2. Error localization "noise" may actually provide beneficial exploration
3. RLTF already handles error types internally; explicit gating redundant

**Potential Failure Points:**
- H-E1: Effect size <5%, undetectable with available compute
- H-M2: U_line/U_ignore distinction doesn't map to localization quality
- H-M4: Gradient noise is beneficial, not harmful

**Conditions Under Which H0 Would Be Supported:**
- If efficiency ratio <= 0 (Fine-gated same or slower)
- If U_line accuracy equals U_ignore accuracy
- If gradient concentration shows no difference

### 7.3 Synthesis

**Balanced Assessment:**

The hypothesis H-ErrorGatedFeedback-v1 presents a testable claim grounded in credit assignment theory. However, the null hypothesis raises valid concerns about effect magnitude given the low U_ignore frequency (~10-15%).

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes effect exists before mechanism testing
2. **Sequential mechanism testing (H-M1-4):** Tests each causal step independently
3. **Gate conditions:** Allow early detection of H0 support at H-E1 or H-M1

**Conditions for Thesis Support:**
- H-E1 and H-M1 pass (MUST_WORK)
- Efficiency improvement >10% with p<0.05
- Mechanism chain validates (gradient concentration improves)

**Conditions for Antithesis Support:**
- H-E1 fails (no efficiency improvement)
- H-M1 fails (localization doesn't work as expected)

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, paper ready
2. **Partial Support:** H-E1 passes but H-M3/M4 fail → Effect exists but mechanism unclear
3. **No Support:** H-E1 or H-M1 fail → Antithesis supported, pivot needed

### 7.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Gating improves efficiency | Effect too small | H-E1 with 5 seeds |
| Mechanism | Credit assignment theory | Exploration benefit | H-M3 gradient analysis |
| Scope | Applies to code RL broadly | APPS-specific | Document as limitation |
| Performance | >10% efficiency gain | Marginal improvement | Multiple thresholds |

**Overall Robustness Score:** Medium
**Confidence in Verification Plan:** 0.75

---

## 8. Conclusions

### 8.1 Key Achievements

- 5 hypotheses across 2 phases defined with clear verification protocols
- H0 addressed: No difference between gated and unconditional application
- Risk mitigation strategies for all 5 key assumptions

### 8.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Establish efficiency improvement exists
- Gate 1: MUST PASS - If fails, stop and reassess

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Fine-grained targets error line tokens
- H-M2: Localization varies by error type
- H-M3: Unreliable localization causes gradient noise
- H-M4: Gating removes noise, improves signal
- Gate 2: H-M1 must pass

### 8.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess hypothesis entirely
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Localization mechanism broken
   - OPTIONAL FAIL → Document as limitation, effect still valid

### 8.4 Open Questions

- Exact U_ignore frequency on APPS (need empirical measurement)
- Optimal error type granularity beyond binary U_line vs not
- Extension to multi-file codebases

### 8.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 experiment setup
   - Pre-validate error categorization on 500 samples

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path
   - Reserve 12 GPU-days compute budget
   - Plan for 5 seeds per condition

3. **Failure Management:**
   - Document all failures with metrics
   - Execute PIVOT strategies if H-E1 fails
   - Consider lower efficiency thresholds (5%)

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (H-ErrorGatedFeedback-v1)
- **Round Table Convergence:** 15 exchanges, all 6 criteria met

### B. Established Facts (Scope Reduction)
- BUILD_ON: Multi-granularity feedback advantage, aggregation bias
- PROVE_NEW: Error-type gating, distribution shift
- Scope Reduction: 50% (2/4 claims established)

### C. MCP Tool Usage Summary
- **Mode:** NO_MCP (batch execution)
- **Analysis:** Manual hypothesis generation from Phase 2A structure

---

**Status:** COMPLETE
**Generated:** 2026-08-19
**Workflow:** Phase 2B Planning (Incremental Mode)

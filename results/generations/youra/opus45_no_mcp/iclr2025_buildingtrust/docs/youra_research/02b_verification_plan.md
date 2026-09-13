# Verification Plan: CoT + Verbalized Confidence for Super-Additive Calibration

**Date:** 2026-08-19
**Hypothesis ID:** H-CoTCalibration-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under multiple-choice QA tasks (TruthfulQA, MMLU), if chain-of-thought prompting is combined with explicit confidence verbalization, then Expected Calibration Error (ECE) will be at least 0.03 lower than the better single intervention (CoT-only or confidence-only), because reasoning chain generation surfaces uncertainty signals that inform more calibrated confidence judgments.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in ECE between the CoT+confidence condition and the better of CoT-only or confidence-only conditions (null: ΔECE < 0.03).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA + MMLU (standard) | TruthfulQA tests adversarial misconceptions; MMLU tests general knowledge. Together they cover calibration across factual domains. |
| **Model** | GPT-3.5-turbo + Llama-2-70B-chat | Two major model families ensure findings aren't model-specific; chat models follow prompting instructions reliably. |

**Dataset Details:**
- Source: HuggingFace datasets
- Path: truthful_qa, cais/mmlu

**Model Details:**
- Type: instruction-tuned chat models
- Source: OpenAI API, HuggingFace/Together AI

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Standard zero-shot prompting | ECE ~0.15-0.25 typical (model-dependent) | TruthfulQA |
| Temperature scaling post-hoc | ECE reduction of ~30-50% post-training | Various |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Verbalized confidence can be reliably extracted from model outputs | Xiong et al. 2023 showed >95% extraction success with constrained prompts | Systematic extraction failures could bias ECE estimates |
| A2 | ECE is a valid measure of calibration quality for this setting | Standard metric since Guo et al. 2017; ACE as robustness check | Findings might not reflect true calibration; mitigated by multiple metrics |
| A3 | CoT and confidence verbalization can be cleanly isolated in prompts | Prompt design explicitly separates components | Interaction effects confounded with prompt artifacts |
| A4 | Effects generalize across model families if tested on multiple | Testing GPT and Llama families provides initial generalization evidence | Findings may be model-specific rather than general |
| A5 | TruthfulQA and MMLU provide representative coverage of QA calibration | Widely used benchmarks; one adversarial, one general | Results may not transfer to other QA domains |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** Systematic ablation quantifying individual and combined contributions of CoT and confidence verbalization to calibration.

**Key Innovation:** First calibration budget breakdown showing practitioners which intervention component is essential vs. optional.

**Differentiation:**
- Tian et al. 2023: Test prompting strategies but don't isolate CoT from confidence systematically
- Xiong et al. 2023: Evaluate confidence elicitation methods but don't include CoT combination
- Wei et al. 2022 (CoT): Focus on accuracy, not calibration

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | pending |
| H-M1 | Mechanism | MUST_WORK | H-E1 | pending |
| H-M2 | Mechanism | MUST_WORK | H-M1 | pending |
| H-M3 | Mechanism | MUST_WORK | H-M2 | pending |
| H-M4 | Mechanism | MUST_WORK | H-M3 | pending |

---

### 2.2 Hypothesis Specifications

---
#### H-E1: ECE Measurability Verification

**Statement**: Under multiple-choice QA tasks, if CoT+confidence prompting is applied, then ECE can be reliably computed across all 5 conditions, because confidence values are extractable and accuracy is determinable.

**Rationale**: Validates that the experimental infrastructure works. ECE computation requires both confidence extraction and accuracy measurement to succeed. This gates all subsequent mechanism tests.

**Variables**:
- Independent: Prompting strategy (5 levels)
- Dependent: ECE (15-bin, range [0,1])
- Controlled: Temperature=0, model family, dataset

**Verification Protocol**:
1. Run all 5 conditions on 100-item pilot sample from TruthfulQA.
2. Extract confidence scores using regex pattern 'Confidence: (\d+)%'.
3. Verify >95% extraction success rate per Xiong et al. 2023 baseline.
4. Compute ECE for each condition and verify values in valid range [0,1].

**Success Criteria (PoC)**:
- Primary: Confidence extraction >95% success rate
- Secondary: ECE computable for all 5 conditions

**Failure Response**: IF fails → PIVOT (revise extraction prompt)

**Dependencies**: None

**Source**: Phase 2A SH1, Prediction P1

---
#### H-M1: CoT Forces Explicit Reasoning Articulation

**Statement**: Under CoT prompting conditions, if the model is prompted with "Let's think step by step", then outputs will contain multi-step reasoning chains, because CoT prompts activate sequential reasoning patterns.

**Rationale**: Validates Step 1 of the causal mechanism. Without explicit reasoning in output, no uncertainty markers can surface. This is foundational to the super-additivity hypothesis.

**Variables**:
- Independent: CoT prompt presence (yes/no)
- Dependent: Reasoning chain presence (binary), step count
- Controlled: Temperature=0, model, dataset

**Verification Protocol**:
1. Generate responses for CoT conditions on 500+ items from TruthfulQA.
2. Parse outputs for multi-step reasoning patterns (numbered steps, transition words).
3. Compare reasoning presence rate: CoT vs baseline conditions.
4. Verify CoT outputs have significantly more reasoning steps.

**Success Criteria (PoC)**:
- Primary: >90% of CoT outputs contain multi-step reasoning
- Secondary: Mean step count in CoT > 2

**Failure Response**: IF fails → EXPLORE (test alternative CoT formulations)

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1, Wei et al. 2022

---
#### H-M2: Reasoning Chains Reveal Uncertainty Indicators

**Statement**: Under CoT+confidence conditions, if reasoning chains are generated, then outputs will contain uncertainty indicators (hedging words, qualifications, alternatives), because complex reasoning surfaces epistemic uncertainty.

**Rationale**: Validates Step 2 of causal mechanism. The hypothesis predicts reasoning chains contain signals that inform confidence. Finding no hedging markers would falsify the mechanism.

**Variables**:
- Independent: Reasoning chain presence
- Dependent: Hedging marker count (might, possibly, alternatively, however)
- Controlled: Temperature=0, item difficulty distribution

**Verification Protocol**:
1. Extract reasoning chains from CoT+confidence outputs on full TruthfulQA (817 items).
2. Count hedging markers using keyword list: might, possibly, could, perhaps, alternatively, however, uncertain.
3. Compare marker frequency across item difficulty levels.
4. Verify markers are present and vary with difficulty.

**Success Criteria (PoC)**:
- Primary: Hedging markers present in >30% of CoT outputs
- Secondary: Marker frequency correlates with item difficulty

**Failure Response**: IF fails → EXPLORE (expand hedging marker dictionary)

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2, Prediction P2

---
#### H-M3: Uncertainty Markers In-Context for Confidence

**Statement**: Under sequential generation, if hedging markers appear before confidence verbalization, then the confidence estimate has access to these signals, because autoregressive generation keeps prior tokens in context.

**Rationale**: Validates Step 3 of causal mechanism. This is an architectural property of autoregressive LLMs—prior tokens are always in context. The test verifies this holds in practice.

**Variables**:
- Independent: Marker presence before confidence token
- Dependent: Positional relationship verification
- Controlled: Output format, generation order

**Verification Protocol**:
1. Parse CoT+confidence outputs to identify confidence statement position.
2. Verify hedging markers appear before confidence in token sequence.
3. Confirm output format enforces CoT-then-confidence ordering.
4. Document any format violations.

**Success Criteria (PoC)**:
- Primary: >99% of outputs have correct CoT-then-confidence ordering
- Secondary: Hedging markers precede confidence in >95% of cases where markers exist

**Failure Response**: IF fails → PIVOT (enforce stricter output format)

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3

---
#### H-M4: Confidence Incorporates Uncertainty Signals

**Statement**: Under CoT+confidence conditions, if hedging markers are present in reasoning, then verbalized confidence correlates negatively with marker count, because the model incorporates uncertainty signals into its confidence judgment.

**Rationale**: This is the core mechanism test. The super-additivity hypothesis predicts that uncertainty markers inform confidence, producing better calibration. This is operationalized as hedging-confidence correlation.

**Variables**:
- Independent: Hedging marker count
- Dependent: Verbalized confidence score (0-100%)
- Controlled: Temperature=0, item correctness

**Verification Protocol**:
1. Extract (hedging_count, confidence_score) pairs from CoT+confidence outputs on full test set.
2. Compute Spearman correlation between hedging count and confidence.
3. Verify negative correlation (more hedging = lower confidence).
4. Check correlation holds across both model families.

**Success Criteria (PoC)**:
- Primary: Spearman r < -0.2 (moderate negative correlation)
- Secondary: Correlation significant at p < 0.05

**Failure Response**: IF fails → EXPLORE (analyze failure modes by item type)

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, Prediction P2

---

## 3. Risk Analysis

### 3.1 Assumption-Based Risks

| ID | Risk | Source | Severity | Description |
|----|------|--------|----------|-------------|
| R1 | Confidence extraction failure | A1 | High | Regex pattern fails to extract confidence from model outputs |
| R2 | ECE metric invalidity | A2 | Medium | ECE may not capture true calibration quality in this setting |
| R3 | Prompt component confounding | A3 | High | CoT and confidence cannot be cleanly isolated, causing attribution errors |
| R4 | Model-specific effects | A4 | Medium | Results don't generalize across GPT and Llama families |
| R5 | Dataset coverage bias | A5 | Medium | TruthfulQA/MMLU don't represent broader QA calibration needs |

### 3.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Impact |
|------|---------------------|--------|
| R1 | H-E1 (critical), H-M4 | Blocks all downstream if extraction fails |
| R2 | H-E1, H-M4 | Invalidates primary metric interpretation |
| R3 | H-M1, H-M2, H-M3 | Confounds mechanism attribution |
| R4 | All (H-E1 to H-M4) | Limits generalization claims |
| R5 | All (H-E1 to H-M4) | Limits domain transfer claims |

### 3.3 Mitigation Strategies

**R1 (Confidence Extraction):**
- Prevention: Use constrained output format with explicit "Confidence: X%" template
- Detection: Monitor extraction success rate per condition; alert if <95%
- Response: PIVOT to alternative extraction (top-k logprobs) or stricter prompt

**R2 (ECE Validity):**
- Prevention: Include ACE and Brier Score as robustness checks
- Detection: Compare metric agreement across conditions
- Response: Report all three metrics; interpret conservatively if divergent

**R3 (Prompt Confounding):**
- Prevention: Token-padding control isolates token-count effects
- Detection: Check if token-padding matches CoT+conf improvement
- Response: If confounded, report as limitation; narrow claims

**R4 (Model-Specific):**
- Prevention: Test on both GPT-3.5-turbo and Llama-2-70B-chat
- Detection: Compare effect sizes across families
- Response: If divergent, report model-specific findings

**R5 (Dataset Coverage):**
- Prevention: Use both adversarial (TruthfulQA) and general (MMLU) benchmarks
- Detection: Compare effect transfer ratio P3
- Response: If ratio outside 0.5-2.0, report domain-specific findings

### 3.4 Risk Summary

| ID | Severity | Likelihood | Mitigation Status |
|----|----------|------------|-------------------|
| R1 | High | Low | Strong (constrained format, >95% prior success) |
| R2 | Medium | Low | Strong (multiple metrics) |
| R3 | High | Medium | Strong (token-padding control) |
| R4 | Medium | Medium | Adequate (2 families) |
| R5 | Medium | Medium | Adequate (2 benchmark types) |

**Critical Risks:** 0 | **High Risks:** 2 | **Medium Risks:** 3 | **Low Risks:** 0

---

## 4. Execution

### 4.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 4.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Extraction >95%, ECE computable | STOP: Reassess infrastructure |
| H-M1 | MUST_WORK | >90% CoT outputs have multi-step reasoning | PIVOT: Revise CoT prompt |
| H-M2 | SHOULD_WORK | Hedging markers in >30% outputs | EXPLORE: Expand marker dictionary |
| H-M3 | SHOULD_WORK | >99% correct CoT-then-confidence ordering | PIVOT: Enforce stricter format |
| H-M4 | MUST_WORK | Spearman r < -0.2 (p < 0.05) | EXPLORE: Analyze failure modes |

### 4.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks |

**Total Duration:** 7 weeks

---

## 5. Dependency Graph & Timeline Visualization

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - ECE Measurability)
         │
         ▼
[Level 1 - Mechanism]
    H-M1 (CoT Forces Reasoning)
         │
         ▼
[Level 2 - Mechanism]
    H-M2 (Reasoning Reveals Uncertainty)
         │
         ▼
[Level 3 - Mechanism]
    H-M3 (Markers In-Context)
         │
         ▼
[Level 4 - Mechanism]
    H-M4 (Confidence Incorporates Signals)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|------------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | MUST_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │ W7
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │         │ ◆       │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │         │ ████    │
  H-M4           │         │         │         │         │ ████
  [Gate 2]       │         │         │         │         │     ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Total Duration:** 7 weeks
- Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4)

**Slack Available:** 0 weeks (fully sequential chain)

**Gate Decision Points:**
- Gate 1 (Week 2): H-E1 must pass to proceed
- Gate 2 (Week 7): Final mechanism validation

### 5.5 Resource Summary

**Total Hypotheses:** 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0

**Verification Phases:** 2
1. Foundation (H-E1): Infrastructure validation
2. Mechanisms (H-M1-4): Causal chain verification

**Compute Requirements:**
- TruthfulQA: 817 items × 5 conditions × 2 models = ~8,170 API calls
- MMLU sample: 1,000 items × 5 conditions × 2 models = ~10,000 API calls
- Total: ~18,170 inference calls

### 5.6 Execution Order

1. **Step 1**: Execute H-E1 (Foundation) - Week 1-2
   - Run pilot on 100 items, verify extraction and ECE computation
2. **Step 2**: Evaluate Gate 1 → If pass, proceed
3. **Step 3**: Execute H-M1 (CoT Reasoning) - Week 3-4
   - Generate CoT outputs on full TruthfulQA (817 items)
4. **Step 4**: Execute H-M2 (Uncertainty Markers) - Week 5
   - Extract and count hedging markers
5. **Step 5**: Execute H-M3 (In-Context Verification) - Week 6
   - Verify positional relationships
6. **Step 6**: Execute H-M4 (Confidence Correlation) - Week 7
   - Compute hedging-confidence correlation
7. **Step 7**: Evaluate Gate 2 → Determine hypothesis status

---

## 6. Dialectical Analysis

### 6.1 Overview

This dialectical analysis evaluates the main hypothesis (H-CoTCalibration-v1) against its null hypothesis using the Thesis-Antithesis-Synthesis framework. The goal is to ensure robust verification planning by considering opposing viewpoints and identifying conditions under which each position would be supported.

### 6.2 Thesis Statement

**Core Claim:** Chain-of-thought prompting combined with explicit confidence verbalization produces super-additive calibration improvements (ECE ≥0.03 lower than best single intervention) because reasoning chain generation surfaces uncertainty signals that inform confidence judgments.

**Supporting Evidence:**
1. CoT prompting produces step-by-step reasoning (Wei et al. 2022, widely replicated)
2. Verbalized confidence can be reliably extracted (Xiong et al. 2023, >95% success)
3. Autoregressive generation ensures prior tokens (including hedging) are in-context

**Strengths:**
- Clear causal mechanism with 4 testable steps
- Builds on established individual intervention effects
- Quantitative success threshold (0.03 ECE) enables decisive falsification

**Expected Outcomes:**
- P1: ECE(CoT+Conf) ≤ min(ECE(CoT), ECE(Conf)) - 0.03
- P2: Hedging markers correlate with lower confidence (r > 0.2)
- P3: Effect transfers across TruthfulQA and MMLU (ratio 0.7-1.3)

### 6.3 Antithesis Development

**Null Hypothesis (H0):** There is no significant difference in ECE between the CoT+confidence condition and the better of CoT-only or confidence-only conditions (ΔECE < 0.03).

**Counter-Arguments:**
1. Token-count confound: More tokens (from CoT) alone may improve calibration without meaningful "self-reading"
2. Prompt artifact: Combined prompt may have confounding structural effects
3. Model-specific effects: Results may not generalize across architectures

**Potential Failure Points:**
- R1: Confidence extraction fails systematically, biasing ECE estimates
- R3: CoT and confidence cannot be cleanly isolated in prompts
- Token-padding control shows same improvement as CoT (trivial explanation)

**Conditions Under Which H0 Would Be Supported:**
- ΔECE < 0.03 between combined and best single intervention
- Token-padding control matches CoT+confidence ECE improvement
- No correlation between hedging markers and confidence (r ≤ 0)
- Effect doesn't transfer across datasets (ratio outside 0.5-2.0)

### 6.4 Synthesis

**Balanced Assessment:**

The hypothesis H-CoTCalibration-v1 presents a testable claim that combining CoT with confidence verbalization produces super-additive calibration gains. However, the null hypothesis raises valid concerns about token-count confounds and prompt artifacts.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes measurement infrastructure before mechanism testing
2. **Sequential mechanism testing (H-M1-M4):** Tests each causal chain step independently
3. **Token-padding control:** Directly tests the trivial "more tokens" explanation
4. **Multi-model testing:** Tests generalization across GPT and Llama families

**Conditions for Thesis Support:**
- H-E1 passes (extraction >95%, ECE computable)
- H-M4 passes (r < -0.2 between hedging and confidence)
- Token-padding control shows less improvement than CoT+confidence
- Effect size consistent across models and datasets

**Conditions for Antithesis Support:**
- H-E1 fails (cannot reliably measure calibration)
- H-M1 fails (CoT doesn't produce reasoning chains)
- Token-padding matches CoT+confidence improvement
- No hedging-confidence correlation

**Nuanced Outcome Possibilities:**
1. **Full Support:** All gates pass, super-additivity confirmed across conditions
2. **Partial Support:** Some H-M fail; refined claim with documented limitations
3. **No Support:** H-E1 or H-M1 fail; mechanism invalidated

### 6.5 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | ECE measurable across conditions | Extraction may fail | H-E1 validates extraction (>95%) |
| Mechanism | Reasoning surfaces uncertainty | May be token-count artifact | Token-padding control isolates effect |
| Correlation | Hedging informs confidence | Correlation may be spurious | Measure across difficulty levels |
| Generalization | Effect transfers across settings | Model/dataset specific | Test 2 models × 2 datasets |

**Overall Robustness Score:** High

**Confidence in Verification Plan:** 0.75

The verification plan is robust because:
- Token-padding control directly addresses the primary alternative explanation
- Sequential hypothesis testing allows early failure detection
- Multiple metrics (ECE, ACE, Brier) provide robustness checks
- Multi-model, multi-dataset design addresses generalization concerns

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** CoT + verbalized confidence produces super-additive calibration gains (ECE ≥0.03 improvement)
- ID: H-CoTCalibration-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 3 decision points (H-E1, H-M1, H-M4)

**Risk Assessment:** Medium
- Primary concerns: Prompt confounding (R3), model-specific effects (R4)

**Immediate Action:** Begin Phase 1 with H-E1 (ECE measurability validation)

### 7.2 Final Summary

**Key Achievements:**
- 5 hypotheses across 2 phases with clear gate conditions
- H0 addressed: Token-padding control directly tests alternative explanation
- Dialectical analysis confirms verification plan robustness

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: ECE measurability across all 5 prompting conditions
- Gate 1: MUST PASS (extraction >95%, ECE computable)

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: CoT forces explicit reasoning articulation
- H-M2: Reasoning chains reveal uncertainty indicators
- H-M3: Uncertainty markers in-context for confidence
- H-M4: Confidence incorporates uncertainty signals
- Gate 2: H-M1 and H-M4 must pass

### 7.3 Conclusions

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL: STOP, reassess extraction methodology
   - PASS: Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 and H-M4 must pass
   - CRITICAL FAIL: Execute failure response (PIVOT/EXPLORE)
   - OPTIONAL FAIL (H-M2, H-M3): Document as limitation

**Open Questions:**
- Does mechanism hold equally for both model families (GPT vs Llama)?
- What is the optimal CoT prompt formulation for calibration (vs accuracy)?
- Are there question types where combined prompting hurts calibration?

**Recommendations:**

1. **Immediate Actions:**
   - Run H-E1 pilot on 100-item TruthfulQA sample
   - Validate confidence extraction regex pattern
   - Set up ECE, ACE, Brier Score computation pipeline

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path
   - ~18,170 API calls total across conditions
   - Reserve 2-week buffer for failures/pivots

3. **Failure Management:**
   - Document all gate failures with analysis
   - Execute PIVOT strategies before abandoning
   - Report partial findings even if full support not achieved

### 7.4 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (H-CoTCalibration-v1)
- Schema version: 10.0.0
- Convergence: All 6 criteria met after 10 exchanges

**B. MCP Tool Usage Summary**
- Total MCP calls: 0 (no MCP tools available in this execution)
- Phase 2A provided pre-mapped hypothesis structure
- Incremental mode: Reduced from 10-14 to 1-3 calls (theoretical)

---

## 8. State & Pipeline

### 8.1 Verification State Status

**State File:** verification_state.yaml
**Status:** Generated
**Sub-Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)

| Hypothesis | Type | Initial Status | Gate |
|------------|------|----------------|------|
| h-e1 | EXISTENCE | READY | MUST_WORK |
| h-m1 | MECHANISM | NOT_STARTED | MUST_WORK |
| h-m2 | MECHANISM | NOT_STARTED | SHOULD_WORK |
| h-m3 | MECHANISM | NOT_STARTED | SHOULD_WORK |
| h-m4 | MECHANISM | NOT_STARTED | MUST_WORK |

### 8.2 Pipeline Tasks Updated

**Note:** Archon MCP not available in this execution. Manual task update required:
- Phase 2B: Mark as "done"
- Phase 2C: Mark as "doing"

### 8.3 Hypothesis Tasks Created

**Note:** Archon MCP not available. Hypothesis tasks to be created manually or in Phase 2C:
- Hypothesis H-E1: ECE Measurability Verification
- Hypothesis H-M1: CoT Forces Explicit Reasoning
- Hypothesis H-M2: Reasoning Reveals Uncertainty
- Hypothesis H-M3: Markers In-Context
- Hypothesis H-M4: Confidence Incorporates Signals

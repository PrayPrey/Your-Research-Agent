# Verification Plan: Alignment-Induced Error Type Divergence

**Date:** 2026-03-24
**Hypothesis ID:** H-ErrorTypeDivergence-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under code generation on standard benchmarks (HumanEval+, MBPP+), if a model is aligned with execution-based RL (binary pass/fail reward) vs preference-based DPO (pairwise preference logits), then the conditional error type distribution P(error_type | failure) will differ systematically, because RL's reward topology creates optimization pressure toward syntactic validity and execution robustness (concentrating failures in semantic assertion errors), while DPO's preference signal emphasizes surface plausibility without explicit execution feedback (concentrating failures in execution errors like syntax and runtime failures).

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in conditional error type distribution P(error_type | failure) between RL-aligned and DPO-aligned code generation models. The alignment method does not systematically affect the composition of failure types.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval+ and MBPP+ (standard) | Provides execution-based evaluation with detailed error messages for taxonomy classification; 164 + 378 = 542 problems total |
| **Model** | CodeRL-770M (RL) vs DPO-finetuned CodeLlama-7B (DPO) | CodeRL explicitly uses execution-based RL; CodeLlama DPO uses preference-based alignment |

**Dataset Details:**
- Source: evalplus/evalplus (1701 GitHub stars)
- Path: Loaded via evalplus library

**Model Details:**
- Type: Encoder-decoder (CodeT5) vs Decoder-only (CodeLlama)
- Source: salesforce/CodeRL (564 stars), community DPO fine-tunes

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| CodeRL | 35.0% pass@1 | HumanEval |
| DPO-aligned CodeLlama | ~45% pass@1 | HumanEval |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | RL training does NOT pre-filter candidates by error type | CodeRL training procedure uses all generated candidates | Error type distribution may reflect data curation rather than optimization dynamics |
| A2 | DPO preference pairs NOT constructed with execution-based filtering | Need to verify dataset construction for specific DPO models | DPO may have implicit execution feedback, reducing expected divergence |
| A3 | ICSE 2025 taxonomy can be reliably automated via error message parsing | Error categories produce distinct error messages | Manual annotation required, violating feasibility constraints |
| A4 | Alignment objective effects are detectable above pipeline artifact noise | Staged design: Stage 1 tests existence; Stage 2 isolates causality | Stage 2 controlled training essential; Stage 1 alone insufficient |
| A5 | Effect persists across taxonomy granularities (coarse to fine-grained) | Real mechanistic effects should manifest at multiple levels | Effect is taxonomically shallow and not genuine inductive bias |

### 1.6 Research Gap & Novelty

**Research Gap:** No prior work has examined alignment method effects on error TYPE distribution rather than overall pass rate.

**Key Innovation:** Reframes alignment from performance metric to failure-mode engineering tool - alignment objectives as inductive biases over error geometry.

**Differentiation:**
- 'Is DPO Superior to PPO?' (2024): Compared aggregate performance; we compare conditional error distributions
- ICSE 2025 Error Taxonomy: Categorized errors without stratifying by alignment method
- h-e1 gradient analysis: Analyzed gradient-level dynamics; we analyze behavioral outcomes

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | SHOULD_WORK | H-E1 | BLOCKED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | BLOCKED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | BLOCKED |

---

### 2.2 Hypothesis Specifications

---
#### H-E1: Error Type Distribution Divergence

**Statement**: Under code generation on HumanEval+/MBPP+, if a model is aligned with RL (binary execution reward) vs DPO (pairwise preference), then P(syntax+runtime | failure, RL) < P(syntax+runtime | failure, DPO), because RL's zero-reward basin creates pressure toward syntactic validity first.

**Rationale**: This is the foundational existence test. If error type distributions don't differ between alignment methods, the entire mechanism hypothesis chain is falsified. The h-e1 gradient anti-correlation finding suggests fundamentally different optimization objectives should manifest behaviorally.

**Variables**:
- Independent: alignment_method (RL_execution vs DPO_preference)
- Dependent: error_type_distribution P(error_type | failure)
- Controlled: evaluation_benchmark, sampling_parameters, error_taxonomy

**Verification Protocol**:
1. Generate n=10 samples per problem at T=0.8 for CodeRL-770M and CodeLlama-7B-DPO on HumanEval+/MBPP+.
2. Execute all samples using EvalPlus harness, capturing full error traces.
3. Classify failures using ICSE 2025 taxonomy via automated error message parsing (syntax, runtime, assertion).
4. Compute conditional error type proportions P(type | failure, method) for each alignment method.
5. Run chi-square test on error_type × alignment_method contingency table; compute Cramér's V.

**Success Criteria** (PoC: Direction-based):
- Primary: Chi-square test p < 0.05 AND Cramér's V > 0.05
- Secondary: Effect direction matches prediction (RL lower syntax+runtime proportion)

**Failure Response**:
- IF fails: PIVOT to alternative behavioral metrics or ABANDON error-type framing

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A SH1, Prediction P1

---
#### H-M1: Zero-Reward Basin Effect

**Statement**: Under RL training with binary execution reward, if all non-executable programs receive zero reward regardless of semantic proximity, then the optimization landscape creates a flat basin over execution failures, because the reward signal provides no gradient information to distinguish "almost works" from "completely broken."

**Rationale**: This mechanism step explains WHY RL should produce different error distributions. The binary reward topology is the causal driver - it treats syntax errors and runtime crashes identically, creating pressure to first achieve execution before optimizing semantics.

**Variables**:
- Independent: reward_signal_type (binary_execution vs preference_based)
- Dependent: gradient_information_on_failures (measurable via loss landscape analysis if needed)
- Controlled: base_model_architecture, training_data

**Verification Protocol**:
1. Analyze RL training procedure (CodeRL) to confirm binary reward structure.
2. Verify that all execution failures (syntax, runtime) receive identical zero reward.
3. Document reward topology difference from DPO's preference-based signal.
4. Test behavioral prediction: RL failures should be concentrated in assertion errors (code runs but wrong output).
5. Validate via assertion error proportion comparison between methods.

**Success Criteria** (PoC: Direction-based):
- Primary: P(assertion | failure, RL) > P(assertion | failure, DPO)
- Secondary: Documented reward topology difference between training objectives

**Failure Response**:
- IF fails: EXPLORE whether CodeRL uses modified reward structure

**Dependencies**: H-E1 must pass (existence of distribution difference)

**Source**: Phase 2A Causal Step 1

---
#### H-M2: Syntactic Validity Pressure

**Statement**: Under RL optimization with zero-reward basin, if models learn to avoid execution failures first, then remaining failures concentrate in semantic assertion errors (code runs but produces wrong output), because syntactic validity is a necessary condition for any positive reward.

**Rationale**: This step connects the reward topology to the observed error distribution. Models under RL pressure must first produce syntactically valid, executable code to receive any feedback - semantic correctness becomes secondary optimization target.

**Variables**:
- Independent: alignment_method (RL vs DPO)
- Dependent: execution_depth (lines executed / total lines before failure)
- Controlled: evaluation_benchmark, code_complexity

**Verification Protocol**:
1. Instrument execution environment to track lines executed before failure.
2. For each failure, compute execution_depth = lines_executed / total_lines.
3. For failures reaching test execution, compute test_coverage = assertions_reached / total_assertions.
4. Compare mean execution depth between RL and DPO failures using t-test.
5. Verify RL failures occur "deeper" in execution flow than DPO failures.

**Success Criteria** (PoC: Direction-based):
- Primary: mean(execution_depth | failure, RL) > mean(execution_depth | failure, DPO) with t-test p < 0.05
- Secondary: Higher test coverage for RL failures before assertion failure

**Failure Response**:
- IF fails: EXPLORE alternative execution metrics or PIVOT to test coverage analysis

**Dependencies**: H-M1 must pass (reward topology confirmed)

**Source**: Phase 2A Causal Step 2, Prediction P2

---
#### H-M3: Preference Surface Plausibility

**Statement**: Under DPO optimization with pairwise preference signal, if human rankings favor code that "looks correct" over code that "runs but is ugly," then failures concentrate in execution errors (syntax, runtime), because the preference signal emphasizes surface plausibility without explicit execution feedback.

**Rationale**: This step explains the complementary DPO mechanism. Human preferences can implicitly favor "almost correct but crashes" over "completely wrong but runs," because humans judge code readability and style more easily than execution correctness.

**Variables**:
- Independent: preference_signal_construction (execution-filtered vs unfiltered)
- Dependent: error_type_proportion (syntax+runtime vs assertion among failures)
- Controlled: preference_dataset_characteristics

**Verification Protocol**:
1. Document DPO training procedure for CodeLlama-7B-DPO model used.
2. Verify whether preference pairs were constructed with or without execution filtering.
3. Analyze error distribution: DPO failures should have higher syntax+runtime proportion.
4. Test robustness at multiple taxonomy granularities (coarse 3-bin, ICSE, LlmFix 19-cause).
5. Verify Cramér's V > 0.03 at all granularity levels for effect robustness.

**Success Criteria** (PoC: Direction-based):
- Primary: P(syntax+runtime | failure, DPO) > P(syntax+runtime | failure, RL)
- Secondary: Effect persists at fine-grained taxonomy (V > 0.03 at LlmFix level)

**Failure Response**:
- IF fails: EXPLORE whether DPO dataset already incorporates execution filtering

**Dependencies**: H-M2 must pass (execution depth difference confirmed)

**Source**: Phase 2A Causal Step 3, Prediction P3

---

## 3. Risk Analysis

### 3.1 Risk Identification

**Risk R1: RL Pre-Filtering Confound**
- **Source Assumption:** A1 - RL training does NOT pre-filter candidates by error type
- **Description:** If CodeRL's training procedure already filters candidates by error type, the observed error distribution reflects data curation rather than optimization dynamics
- **Severity:** HIGH
- **Likelihood:** Low (CodeRL documentation suggests all candidates used)
- **Detection:** Review CodeRL training procedure documentation before experiments

**Risk R2: DPO Execution Filtering**
- **Source Assumption:** A2 - DPO preference pairs NOT constructed with execution-based filtering
- **Description:** Modern DPO pipelines often pre-filter candidates by execution success, which would give DPO implicit execution feedback and reduce expected effect size
- **Severity:** HIGH
- **Likelihood:** Medium-High (common practice in DPO pipelines)
- **Detection:** Verify DPO dataset construction methodology for specific model used

**Risk R3: Taxonomy Automation Failure**
- **Source Assumption:** A3 - ICSE 2025 taxonomy can be reliably automated via error message parsing
- **Description:** If error classification cannot be reliably automated, manual annotation would be required, violating feasibility constraints
- **Severity:** MEDIUM
- **Likelihood:** Low (syntax/runtime/assertion produce distinct error messages)
- **Detection:** Validate parser accuracy on 100 random samples before full run

**Risk R4: Pipeline Confound in Stage 1**
- **Source Assumption:** A4 - Alignment effects detectable above pipeline artifact noise
- **Description:** Stage 1 uses existing models with unknown pipeline differences - any detected effect could be confounded by training data, hyperparameters, or architecture differences
- **Severity:** MEDIUM (mitigated by exploratory framing)
- **Likelihood:** Medium
- **Detection:** Compare multiple models per alignment type if available

**Risk R5: Taxonomic Artifact**
- **Source Assumption:** A5 - Effect persists across taxonomy granularities
- **Description:** If effect only appears at coarse taxonomy (3-bin) but disappears at finer granularity, it suggests binning artifact rather than genuine mechanistic difference
- **Severity:** MEDIUM
- **Likelihood:** Low-Medium
- **Detection:** Test at multiple granularities (coarse, ICSE, LlmFix 19-cause)

### 3.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Impact |
|------|--------|---------------------|----------|--------|
| R1 | A1 | H-E1, H-M1 | HIGH | Invalidates foundation if RL data curated |
| R2 | A2 | H-E1, H-M3 | HIGH | Reduces effect size, may mask divergence |
| R3 | A3 | H-E1, H-M1, H-M2, H-M3 | MEDIUM | Blocks automated analysis |
| R4 | A4 | H-E1 (Stage 1 only) | MEDIUM | Limits causal interpretation |
| R5 | A5 | H-M3 | MEDIUM | Questions mechanism depth |

### 3.3 Mitigation Strategies

**R1 Mitigation: RL Pre-Filtering Confound**
1. **Prevention:** Document CodeRL training procedure from original paper/code before experiments
2. **Detection:** Check if training code filters candidates by execution status
3. **Response:**
   - PIVOT: Use different RL-aligned model with documented all-candidate training
   - SCOPE: Frame results as "CodeRL-specific" rather than "RL-general"
   - ABORT: If all available RL models use error-type filtering

**R2 Mitigation: DPO Execution Filtering**
1. **Prevention:** Select DPO model with documented preference pair construction
2. **Detection:** Review model card and training documentation for execution filtering
3. **Response:**
   - PIVOT: Find DPO model without execution filtering (may reduce options)
   - SCOPE: Acknowledge reduced effect size expectation in analysis
   - ABORT: N/A - even filtered DPO still lacks explicit execution reward

**R3 Mitigation: Taxonomy Automation Failure**
1. **Prevention:** Build parser using ICSE 2025 error patterns; test on 100 samples
2. **Detection:** Measure parser accuracy; flag ambiguous cases for review
3. **Response:**
   - PIVOT: Manual annotation of flagged cases only (hybrid approach)
   - SCOPE: Use only clearly classifiable errors (document exclusion rate)
   - ABORT: If >20% errors unclassifiable by parser

**R4 Mitigation: Pipeline Confound in Stage 1**
1. **Prevention:** Frame Stage 1 as exploratory hypothesis testing
2. **Detection:** Document all known pipeline differences between models
3. **Response:**
   - PIVOT: Proceed to Stage 2 controlled training regardless of Stage 1 results
   - SCOPE: Limit Stage 1 claims to "association" not "causation"
   - ABORT: N/A - Stage 2 addresses this by design

**R5 Mitigation: Taxonomic Artifact**
1. **Prevention:** Pre-register multi-granularity analysis plan
2. **Detection:** Compute Cramér's V at each granularity level
3. **Response:**
   - PIVOT: Report effect as "coarse-grained" phenomenon if fine-grained fails
   - SCOPE: Focus on practical implications even if mechanism shallow
   - ABORT: If effect only appears at 3-bin level (pure binning artifact)

### 3.4 Risk Summary

| ID | Risk | Source | Severity | Likelihood | Mitigation |
|----|------|--------|----------|------------|------------|
| R1 | RL Pre-Filtering | A1 | HIGH | Low | Document training procedure |
| R2 | DPO Execution Filtering | A2 | HIGH | Medium-High | Verify dataset construction |
| R3 | Taxonomy Automation | A3 | MEDIUM | Low | Validate parser on samples |
| R4 | Pipeline Confound | A4 | MEDIUM | Medium | Frame Stage 1 as exploratory |
| R5 | Taxonomic Artifact | A5 | MEDIUM | Low-Medium | Multi-granularity testing |

**Risk Distribution:**
- Critical Risks: 0
- High Risks: 2 (R1, R2)
- Medium Risks: 3 (R3, R4, R5)
- Low Risks: 0

**Key Consensus from Expert Panel:**
- R2 (DPO execution filtering) is highest probability risk - verify before proceeding
- Stage 1 should be explicitly framed as exploratory
- Stage 2 controlled training essential for causal claims
- Multi-granularity taxonomy testing provides built-in falsification mechanism

---

## 4. Dependency Structure

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
        DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════════════

[Level 0 - Foundation]
                    ┌─────────────────────────────────┐
                    │  H-E1: Error Type Divergence    │
                    │  Gate: MUST_WORK               │
                    │  Prerequisites: None            │
                    └─────────────────────────────────┘
                                    │
                                    ▼
[Level 1 - Mechanism Step 1]
                    ┌─────────────────────────────────┐
                    │  H-M1: Zero-Reward Basin        │
                    │  Gate: MUST_WORK               │
                    │  Prerequisites: H-E1            │
                    └─────────────────────────────────┘
                                    │
                                    ▼
[Level 2 - Mechanism Step 2]
                    ┌─────────────────────────────────┐
                    │  H-M2: Syntactic Validity       │
                    │  Gate: SHOULD_WORK             │
                    │  Prerequisites: H-M1            │
                    └─────────────────────────────────┘
                                    │
                                    ▼
[Level 3 - Mechanism Step 3]
                    ┌─────────────────────────────────┐
                    │  H-M3: Preference Plausibility  │
                    │  Gate: SHOULD_WORK             │
                    │  Prerequisites: H-M2            │
                    └─────────────────────────────────┘
                                    │
                                    ▼
                            [VERIFICATION COMPLETE]

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Depth: 4 levels (sequential execution required)
Parallelization: None (strict dependency chain)
═══════════════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | If Fails |
|-------|------------|---------------|-----------|----------|
| 0 | H-E1 | None | MUST_WORK | STOP - Reassess entire hypothesis |
| 1 | H-M1 | H-E1 | MUST_WORK | STOP - Mechanism invalidated |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Document limitation, continue |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Document limitation, complete |

**Gate Definitions:**
- **MUST_WORK**: Hypothesis must pass for pipeline to continue. Failure = pipeline stop.
- **SHOULD_WORK**: Hypothesis expected to pass. Failure = document as limitation, continue.

**Verification Phases:**

| Phase | Hypotheses | Purpose | Gate |
|-------|------------|---------|------|
| Phase 1 - Foundation | H-E1 | Establish existence of error distribution difference | MUST PASS |
| Phase 2 - Mechanisms | H-M1, H-M2, H-M3 | Validate causal mechanism chain | H-M1 MUST PASS |

---

## 5. Execution

### 5.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 5.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Chi-square p<0.05, Cramér's V>0.05 | STOP - Reassess entire hypothesis |
| H-M1 | MUST_WORK | P(assertion\|failure,RL) > P(assertion\|failure,DPO) | STOP - Mechanism invalidated |
| H-M2 | SHOULD_WORK | Execution depth (RL) > Execution depth (DPO), p<0.05 | Document limitation, continue |
| H-M3 | SHOULD_WORK | Effect persists at fine-grained taxonomy (V>0.03) | Document limitation, complete |

### 5.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1 - Foundation | H-E1 | 2 weeks |
| Phase 2 - Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |

**Total Duration:** 5 weeks

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════
           VERIFICATION TIMELINE - 4 Hypotheses (5 Weeks Total)
═══════════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ W1      │ W2      │ W3      │ W4      │ W5      │
──────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation   │         │         │         │         │         │
  H-E1 (Existence)    │ ████████│█████████│         │         │         │
  [Gate 1] ◆          │         │         │◆        │         │         │
──────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms   │         │         │         │         │         │
  H-M1 (Zero-Reward)  │         │         │█████████│         │         │
  H-M2 (Validity)     │         │         │         │█████████│         │
  H-M3 (Preference)   │         │         │         │         │█████████│
  [Gate 2] ◆          │         │         │         │         │         │◆
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 (sequential, no parallelization)
═══════════════════════════════════════════════════════════════════════════
```

### 5.5 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3

**Duration Breakdown:**
- H-E1 (Foundation): 2 weeks - Model evaluation, error collection, chi-square analysis
- H-M1 (Zero-Reward Basin): 1 week - Reward topology documentation, assertion proportion analysis
- H-M2 (Syntactic Validity): 1 week - Execution depth measurement, t-test analysis
- H-M3 (Preference Plausibility): 1 week - Multi-granularity taxonomy testing

**Total Critical Path Duration:** 5 weeks
**Slack Available:** 0 weeks (all hypotheses sequential)
**Parallelization Opportunities:** None (strict dependency chain)

### 5.6 Resource Summary

**Hypothesis Distribution:**
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0

**Verification Phases:** 2
1. Foundation (H-E1) - Establishes existence of error distribution difference
2. Mechanisms (H-M1-M3) - Validates causal mechanism chain

**Compute Resources:**
- Model inference: CodeRL-770M, CodeLlama-7B-DPO
- Evaluation: EvalPlus harness (HumanEval+ 164, MBPP+ 378 problems)
- Samples: 10 per problem × 542 problems × 2 models = ~10,840 generations
- Analysis: Chi-square, t-test, Cramér's V computation

**Data Requirements:**
- HumanEval+ and MBPP+ benchmark data (publicly available via evalplus)
- Error traces with full error messages for taxonomy classification

### 5.7 Execution Order

**Step 1:** Execute H-E1 (Foundation) - Week 1-2
- Generate samples from both models on HumanEval+/MBPP+
- Classify errors using ICSE 2025 taxonomy
- Compute chi-square test and Cramér's V

**Step 2:** Evaluate Gate 1 - End of Week 2
- Pass condition: Chi-square p<0.05 AND Cramér's V>0.05
- If FAIL: STOP pipeline, reassess entire hypothesis

**Step 3:** Execute H-M1 (Zero-Reward Basin) - Week 3
- Document CodeRL reward topology
- Analyze assertion error proportions
- Verify mechanism step 1

**Step 4:** Execute H-M2 (Syntactic Validity) - Week 4
- Instrument execution depth measurement
- Compute t-test on execution depth
- Verify mechanism step 2

**Step 5:** Execute H-M3 (Preference Plausibility) - Week 5
- Test at multiple taxonomy granularities
- Compute Cramér's V at coarse/intermediate/fine levels
- Verify mechanism step 3

**Step 6:** Evaluate Gate 2 - End of Week 5
- Verify H-M1 passed (MUST_WORK)
- Document any H-M2/H-M3 limitations

**Final:** Verification complete - Proceed to Phase 5 (Baseline Comparison) or synthesis

---

## 6. Dialectical Analysis

### 6.1 Analysis Overview

This dialectical analysis evaluates the hypothesis through Thesis-Antithesis-Synthesis framework, using the null hypothesis (H0) from Phase 2A as the foundation for antithesis development. The goal is to ensure robust verification by considering opposing viewpoints and producing a balanced assessment that acknowledges both potential outcomes.

### 6.2 Thesis Statement

**Core Claim:** Execution-based RL and preference-based DPO alignment methods induce systematically different error type distributions among failed code generations, with RL concentrating failures in semantic assertion errors and DPO concentrating failures in execution errors.

**Supporting Premises:**
1. RL binary execution reward creates flat zero-reward basin over all non-executable programs, creating optimization pressure toward syntactic validity first
2. DPO pairwise preference signal from human rankings can implicitly favor "almost-correct-but-crashes" over "completely-wrong-but-runs"
3. h-e1 experiment demonstrated RL and DPO gradients are fundamentally anti-correlated across all 48 layers, suggesting different optimization objectives
4. Reward topology analysis shows binary execution signal provides no gradient information to distinguish near-correct from far-incorrect non-executing code

**Strengths:**
- Clear mechanistic explanation grounded in reward topology analysis
- Testable with existing benchmarks (HumanEval+, MBPP+) and publicly available models
- Falsifiable via explicit statistical criteria (chi-square p < 0.05, V > 0.05)
- Supported by prior h-e1 finding of gradient anti-correlation

**Weaknesses:**
- Stage 1 uses existing models with unknown pipeline differences
- DPO datasets may already incorporate execution filtering, reducing expected effect
- Effect size may be small if modern training pipelines have converged

**Confidence:** 0.80

### 6.3 Antithesis Development

**Null Hypothesis (H0):** There is no significant difference in conditional error type distribution P(error_type | failure) between RL-aligned and DPO-aligned code generation models. The alignment method does not systematically affect the composition of failure types.

**Counter-Arguments:**
1. Modern DPO pipelines commonly pre-filter candidates by execution success, giving DPO implicit execution feedback similar to RL
2. Pipeline artifacts (training data, hyperparameters, architecture differences) may overwhelm any genuine alignment effect
3. Gradient anti-correlation does not necessarily translate to behavioral output differences - models may converge to similar failure modes despite different optimization paths
4. The error taxonomy may be too coarse to capture subtle alignment effects, or fine-grained taxonomy may lack statistical power

**Conditions Under Which H0 Would Be Supported:**
- Chi-square test p > 0.05 for error type × alignment method contingency table
- Cramér's V < 0.05 indicating negligible association strength
- No significant execution depth difference (t-test p > 0.10)
- Effect disappears at fine-grained taxonomy (V < 0.03 at LlmFix level)

**Confidence:** 0.40 (lower than thesis due to h-e1 gradient evidence)

### 6.4 Synthesis

**Resolution:** The verification plan resolves the thesis-antithesis dialectic through a staged experimental design that separates exploratory hypothesis testing (Stage 1) from causal confirmation (Stage 2), with explicit gate conditions allowing early detection of null hypothesis support.

**How the Plan Addresses the Dialectic:**

1. **Stage 1 (Exploratory):** Uses existing models to test existence of effect
   - If no effect detected → Thesis falsified early, minimal effort wasted
   - If effect detected → Proceed to Stage 2 for causal confirmation

2. **Stage 2 (Confirmatory):** Trains same base model with RL vs DPO objectives
   - Isolates alignment objective as causal factor
   - Addresses pipeline confound concern from antithesis

3. **Sequential Gate Structure:** H-E1 → H-M1 → H-M2 → H-M3
   - MUST_WORK gates at H-E1 and H-M1 allow early stopping
   - Prevents pursuit of false positive if foundation fails

4. **Multi-Granularity Testing:** Coarse → ICSE → LlmFix 19-cause
   - Distinguishes genuine mechanistic effects from binning artifacts
   - Addresses taxonomy artifact concern from antithesis

**Outcome Possibilities:**
| Outcome | Gate Results | Interpretation |
|---------|--------------|----------------|
| Full Support | All pass | Thesis validated, mechanism confirmed |
| Partial Support | H-E1, H-M1 pass; H-M2/M3 fail | Refined thesis with documented limitations |
| No Support | H-E1 or H-M1 fail | Antithesis supported, pivot required |

**Synthesis Confidence:** 0.75

### 6.5 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Error distribution differs by alignment | May be artifact of pipeline | H-E1 test with chi-square |
| Mechanism | Reward topology drives difference | Alternative explanations exist | H-M1-M3 sequential tests |
| Scope | Applies to code generation broadly | Limited to specific conditions | Multi-benchmark testing |
| Causality | Alignment objective is causal | Confounds overwhelm signal | Stage 2 controlled training |
| Granularity | Effect is mechanistically deep | Binning artifact | Multi-granularity taxonomy |

**Overall Robustness Score:** HIGH

**Justification:**
- Verification plan explicitly addresses all major antithesis concerns
- Staged design allows early failure detection
- Multiple independent mechanism tests (error type, execution depth, taxonomy robustness)
- Clear decision criteria for thesis vs antithesis support

**Confidence in Verification Plan:** 0.80

**Remaining Uncertainties:**
- Actual effect size in Stage 1 (may be reduced by DPO filtering)
- Computational cost of Stage 2 if Stage 1 shows marginal signal
- Generalization beyond CodeT5/CodeLlama model families

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Alignment-Induced Error Type Divergence in Code Generation
- ID: H-ErrorTypeDivergence-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1: H-E1, Gate 2: H-M1)

**Risk Assessment:** MEDIUM
- Primary concerns: DPO execution filtering (R2), Pipeline confounds (R4)

**Immediate Action:** Begin Phase 2C experiment design for H-E1

### 7.2 Final Summary

**Key Achievements:**
- 4 hypotheses across 2 phases defined with verification protocols
- Null hypothesis (H0) addressed through dialectical analysis
- Risk mitigation strategies for all 5 identified risks
- Sequential dependency chain with clear gate conditions

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Error type distribution differs between RL and DPO aligned models
- Gate 1: MUST PASS (chi-square p<0.05, Cramér's V>0.05)

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Zero-reward basin effect on RL optimization
- H-M2: Syntactic validity pressure creating execution depth difference
- H-M3: Preference surface plausibility in DPO
- Gate 2: H-M1 MUST PASS

**Critical Decision Points:**
1. Gate 1 (Foundation): H-E1 must pass → FAIL = STOP pipeline
2. Gate 2 (Mechanisms): H-M1 must pass → FAIL = Mechanism invalidated

### 7.3 Conclusions

**Open Questions:**
- What is the actual effect size given existing model pipeline differences?
- Do modern DPO datasets already incorporate execution filtering?
- Does the effect generalize beyond CodeT5/CodeLlama to other model families?

**Recommendations:**

1. **Immediate Actions:**
   - Proceed to Phase 2C experiment design for H-E1
   - Document CodeRL and DPO model training procedures before experiments
   - Validate error taxonomy parser on 100 samples

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path execution
   - Reserve 1-2 weeks buffer for potential Stage 2 controlled training

3. **Failure Management:**
   - Document all hypothesis failures with detailed analysis
   - Execute PIVOT strategies from mitigation plan on gate failures
   - Write Serena memory on significant findings for future pipeline runs

### 7.4 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-ErrorTypeDivergence-v1)
- Schema Version: 10.0.0

**B. MCP Tool Usage Summary**
- Total MCP calls: 7
- Tools used:
  - mcp__clearThought__scientificmethod: 4 calls (hypothesis + experiment stages)
  - mcp__clearThought__collaborativereasoning: 1 call (risk analysis)
  - mcp__clearThought__structuredargumentation: 3 calls (thesis-antithesis-synthesis)

**C. Scope Reduction**
- BUILD_ON claims: 3 (not re-verified)
- PROVE_NEW claims: 2 (verification targets)
- Scope reduction: 60%

---

## 8. Phase 2B Completion Status

- verification_state.yaml: CREATED (schema v3.5)
- Pipeline tasks updated: Phase 2B → done, Phase 2C → doing
- Hypothesis tasks created: 4 tasks (H-E1, H-M1, H-M2, H-M3)

**Archon Task IDs:**
- H-E1: e99d6538-85cf-422e-b0a2-3d07aef95b90
- H-M1: 108cbb81-3397-4e96-b250-1c3a8b9d0db9
- H-M2: 4aa8f030-084e-4f4f-b0a1-078a8c42853e
- H-M3: f3a75704-893b-4bfb-881c-f2e42cc1c042

---

*Generated by YouRA Phase 2B (v6.0) | 2026-03-24*

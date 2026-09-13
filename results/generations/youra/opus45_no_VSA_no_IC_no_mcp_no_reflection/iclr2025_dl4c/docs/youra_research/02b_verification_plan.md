# Verification Plan: Reward Information Bandwidth for Code LLM Training

**Date:** 2026-08-29
**Hypothesis ID:** H-RewardBandwidth-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under PPO training of CodeLlama-7B on MBPP with fixed compute budget,
if reward function provides higher information bandwidth (continuous + categorical vs. binary),
then model reaches pass@1 > 0.3 in fewer training samples,
because denser feedback enables gradient updates to more precisely target error-inducing code patterns.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in samples-to-threshold between reward bandwidth conditions
(H0: μ_LOW = μ_MEDIUM = μ_HIGH).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | MBPP + HumanEval (standard) | MBPP provides training data, HumanEval provides held-out evaluation with test suites for execution feedback |
| **Model** | CodeLlama-7B-Instruct | Open model with code specialization, sufficient capacity for RLEF, used in prior work |

**Dataset Details:**
- Source: https://github.com/google-research/google-research/tree/master/mbpp, https://github.com/openai/human-eval
- Path: downloaded via datasets library

**Model Details:**
- Type: decoder-only transformer
- Source: https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| LOW (Binary) | reward = 1 if all_tests_pass else 0 | MBPP/HumanEval |
| MEDIUM (Continuous) | reward = num_passed / num_total | MBPP/HumanEval |
| HIGH (Categorical + Continuous) | reward = 0.5 × pass_rate + 0.5 × error_score | MBPP/HumanEval |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Error types form meaningful ordering reflecting distance to correct solution | Execution stages: parse → execute → assert → pass represent clear progression | Error_score weighting would be arbitrary, HIGH condition loses principled grounding |
| A2 | CodeLlama-7B has sufficient capacity to learn from fine-grained signals | 7B parameter models have shown ability to learn code generation via RL (PPOCoder) | Model might not have capacity to use additional signal, masking true effect |
| A3 | PPO training is stable enough to attribute effects to reward function | TRL library provides stable PPO implementation, PPOCoder demonstrated stability | Training instability would add noise, requiring more seeds |
| A4 | HumanEval is representative of code generation quality | HumanEval is standard benchmark used by CodeRL, RLTF, PPOCoder | Results might not generalize to other code generation tasks |
| A5 | 5 seeds per condition provides sufficient statistical power | Power analysis with σ ≈ 0.03 achieves 80% power for effect size d = 0.8 | May fail to detect smaller true effects |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First controlled comparison of feedback granularities under matched conditions

**Key Innovation:** Information bandwidth framing—conceptualizing feedback as bits per gradient update

**Differentiation:**
- CodeRL (2022): Used binary only, no comparison to finer-grained alternatives
- RLTF (2023): Showed multi-granularity but lacked controlled ablation with matched infrastructure
- PPOCoder (2023): Focused on PPO algorithm, not feedback granularity comparison

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| h-e1 | EXISTENCE | MUST_WORK | None | READY |
| h-m1 | MECHANISM | MUST_WORK | h-e1 | NOT_STARTED |
| h-m2 | MECHANISM | SHOULD_WORK | h-m1 | NOT_STARTED |
| h-m3 | MECHANISM | SHOULD_WORK | h-m2 | NOT_STARTED |
| h-c1 | CONDITION | SHOULD_WORK | h-m3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Existence of Bandwidth Effect**

**Type:** EXISTENCE
**Statement:** Under PPO training on MBPP, if reward provides higher bandwidth, then model convergence differs, because more information per update enables different learning dynamics.

**Rationale:** Before testing mechanism, must confirm the phenomenon exists. If HIGH and LOW conditions show identical learning curves, the mechanism hypothesis is moot.

**Variables:**
- Independent: Reward bandwidth level (LOW/MEDIUM/HIGH)
- Dependent: Samples-to-threshold (pass@1 > 0.3 on HumanEval)
- Controlled: Model (CodeLlama-7B), Dataset (MBPP), Algorithm (PPO), Epochs (3), Seeds (5)

**Verification Protocol:**
1. Train CodeLlama-7B with PPO under all 3 conditions.
2. Log pass@1 on HumanEval every 1000 samples.
3. Record samples-to-threshold for each seed.
4. Compare distributions across conditions.

**Success Criteria (PoC: Direction-based):**
- Primary: HIGH < LOW in samples-to-threshold
- Secondary: Learning curves visibly separate

**Failure Response:**
- IF fails: STOP — reassess hypothesis foundation

**Dependencies:** None

**Source:** Phase 2A SH1

---
**H-M1: Information Content Difference**

**Type:** MECHANISM
**Statement:** Higher bandwidth rewards provide more bits of information per gradient update.

**Rationale:** Tests first causal step. If information content is similar across conditions (mutual information analysis), the mechanism foundation fails.

**Variables:**
- Independent: Reward structure
- Dependent: Mutual information between reward signal and code quality
- Controlled: Same training data, same model

**Verification Protocol:**
1. Compute MI(reward, error_type) for each condition.
2. Compare bits per update across LOW/MEDIUM/HIGH.
3. Verify HIGH > MEDIUM > LOW in information content.

**Success Criteria:**
- Primary: Information ordering matches bandwidth ordering
- Secondary: Measurable bit difference

**Failure Response:**
- IF fails: PIVOT — alternative information measure

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---
**H-M2: Error-Type Discrimination**

**Type:** MECHANISM
**Statement:** Denser signal enables model to distinguish between error types during training.

**Rationale:** Tests second causal step. If error-type distribution is identical across conditions throughout training, credit assignment hypothesis fails.

**Variables:**
- Independent: Reward bandwidth
- Dependent: Error-type distribution per epoch (syntax/runtime/assertion/pass)
- Controlled: Same infrastructure

**Verification Protocol:**
1. Track error-type proportions per epoch per condition.
2. Compare distributions at epochs 1, 2, 3.
3. Test for significant differences using chi-square.

**Success Criteria:**
- Primary: HIGH shows faster error-type distribution shift
- Secondary: Syntax errors decrease faster in HIGH

**Failure Response:**
- IF fails: Document limitation

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2-3

---
**H-M3: Convergence Speed Difference**

**Type:** MECHANISM
**Statement:** More informative gradient directions result in faster convergence.

**Rationale:** Tests final causal link. This directly measures the primary prediction P1.

**Variables:**
- Independent: Reward bandwidth
- Dependent: Samples-to-threshold (pass@1 > 0.3)
- Controlled: All training infrastructure

**Verification Protocol:**
1. Use same training runs from H-E1.
2. Compute mean and variance of samples-to-threshold.
3. Run statistical test (ANOVA + post-hoc).
4. Calculate effect size (Cohen's d).

**Success Criteria:**
- Primary: p < 0.05 for HIGH vs LOW comparison
- Secondary: Cohen's d > 0.8

**Failure Response:**
- IF fails: Analyze effect size for minimum detectable effect

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 4, Prediction P1

---
**H-C1: Weighting Sensitivity**

**Type:** CONDITION
**Statement:** The 0.5/0.5 weighting between pass_rate and error_score is robust within ±0.2 range.

**Rationale:** Tests boundary condition. If results are highly sensitive to exact weighting, finding is less generalizable.

**Variables:**
- Independent: Weighting parameter (0.3/0.7 to 0.7/0.3)
- Dependent: Samples-to-threshold
- Controlled: All other parameters

**Verification Protocol:**
1. Run HIGH condition with 3 weight variants.
2. Compare samples-to-threshold across weights.
3. Assess sensitivity of results to weighting.

**Success Criteria:**
- Primary: All weight variants outperform LOW
- Secondary: Variance across weights < variance across conditions

**Failure Response:**
- IF fails: Document optimal weighting, narrow scope

**Dependencies:** H-M3

**Source:** Phase 2A Known Limitations

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-C1
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Conditions show different convergence | STOP, reassess |
| H-M1 | MUST_WORK | Information ordering confirmed | PIVOT measure |
| H-M2 | SHOULD_WORK | Error distribution differs | Document limitation |
| H-M3 | SHOULD_WORK | Statistical significance achieved | Analyze effect size |
| H-C1 | SHOULD_WORK | Weighting robust | Document optimal |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1 (Foundation) | H-E1 | 2 weeks |
| Phase 2 (Mechanisms) | H-M1, H-M2, H-M3 | 4 weeks |
| Phase 2.5 (Conditions) | H-C1 | 1 week |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 (Error ordering arbitrary) | H-M1, H-M2 | High |
| R2 | A2 (Model capacity) | H-E1, H-M1 | Medium |
| R3 | A3 (PPO instability) | All | High |
| R4 | A4 (HumanEval representativeness) | H-M3 | Medium |
| R5 | A5 (Statistical power) | H-M3 | Medium |

### 4.2 Mitigation Strategies

**R1: Error Ordering Validity**
- Prevention: Validate ordering with pilot study
- Detection: Monitor if error_score correlates with code quality
- Response: PIVOT to alternative ordering or remove categorical component

**R2: Model Capacity**
- Prevention: Use proven model (PPOCoder validated 7B)
- Detection: Monitor gradient norms and loss curves
- Response: Reduce learning rate or try smaller model

**R3: PPO Instability**
- Prevention: Use TRL library defaults, proven stable
- Detection: Monitor reward variance and policy KL
- Response: Add more seeds, reduce learning rate

**R4: Benchmark Representativeness**
- Prevention: Use standard benchmark for comparability
- Detection: N/A (limitation accepted)
- Response: Document scope limitation

**R5: Statistical Power**
- Prevention: Power analysis completed (80% power for d=0.8)
- Detection: Monitor effect sizes early
- Response: Add seeds if effect smaller than expected

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanism]
    H-M1 ← H-E1
         │
         ▼
    H-M2 ← H-M1
         │
         ▼
    H-M3 ← H-M2
         │
         ▼
[Level 2 - Condition]
    H-C1 ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-C1
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3-4 │ W5 │ W6 │ W7
─────────────────┼──────┼──────┼────┼────┼────
PHASE 1: Foundation
  H-E1           │██████│      │    │    │
  [Gate 1]       │      │ ◆    │    │    │
─────────────────┼──────┼──────┼────┼────┼────
PHASE 2: Mechanisms
  H-M1           │      │██████│    │    │
  H-M2           │      │      │████│    │
  H-M3           │      │      │    │████│
  [Gate 2]       │      │      │    │    │◆
─────────────────┼──────┼──────┼────┼────┼────
PHASE 2.5: Conditions
  H-C1           │      │      │    │    │████
═══════════════════════════════════════════════════════════════════
Legend: ██ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Higher reward bandwidth accelerates code LLM training convergence.

**Supporting Evidence:**
1. Information theory: more bits per update enables finer gradient targeting
2. Error-type ordering provides principled distance-to-correct metric
3. PPO credit assignment benefits from denser signal

**Strengths:**
- Grounded in established information theory
- Clear, falsifiable predictions
- Controlled experimental design

### 6.2 Antithesis

**Null Hypothesis (H0):** No significant difference in samples-to-threshold between conditions.

**Counter-Arguments:**
1. Additional signal may add noise rather than information
2. Binary reward may be sufficient for discrete pass/fail outcomes
3. Model may not have capacity to utilize fine-grained signal

**Conditions Under Which H0 Would Be Supported:**
- If all conditions converge at similar rates (within noise)
- If gradient analysis shows no difference in update directions
- If error-type distributions remain identical across conditions

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis presents a testable claim grounded in information theory. The null hypothesis raises valid concerns about whether additional signal adds value or noise.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence before mechanism
2. **Sequential mechanism testing (H-M*):** Tests causal chain step-by-step
3. **Gate conditions:** Allow early detection of H0 support

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated
2. **Partial Support:** Some H-M fail → Refined thesis with limitations
3. **No Support:** H-E1 fails → Antithesis supported

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Effect exists | May be artifact | H-E1 test |
| Mechanism | Causal chain valid | Alternative explanations | H-M1-3 tests |
| Scope | Applies broadly | Limited conditions | H-C1 test |
| Performance | Better than binary | Marginal improvement | Phase 5 |

**Overall Robustness Score:** Medium-High
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Higher reward bandwidth accelerates code LLM training.
- ID: H-RewardBandwidth-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 3, H-C: 1)
- Phases: 3 phases over 7 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: Error ordering validity (R1), PPO stability (R3)

**Immediate Action:** Begin Phase 1 with H-E1

### 7.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Existence of bandwidth effect
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Information content difference
- H-M2: Error-type discrimination
- H-M3: Convergence speed difference
- Gate 2: H-M1 must pass

**Phase 2.5: Conditions** (1 week)
- H-C1: Weighting sensitivity
- Gate 2.5: Narrow scope on failure

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess hypothesis
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Execute failure response
   - OPTIONAL FAIL → Document limitation

3. **Gate 2.5 (Conditions):** Narrow scope
   - Failures narrow but don't invalidate

### 7.4 Open Questions

- Does error_type information add value beyond continuous pass_rate?
- Is 0.5/0.5 weighting optimal, or should weights be learned?
- Does bandwidth effect scale with model size?

### 7.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1
   - Set up training infrastructure with TRL

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path
   - Reserve buffer for additional seeds if needed

3. **Failure Management:**
   - Document all failures with effect sizes
   - Execute PIVOT strategies as defined

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-RewardBandwidth-v1)

### B. Established Facts (BUILD_ON)
- Binary rewards work for code LLM training (CodeRL 2022)
- Multi-granularity feedback shows promise (RLTF 2023)
- PPO training is stable for code LLMs (PPOCoder 2023)
- Process rewards help in reasoning tasks (Let's Verify 2023)

### C. MCP Tool Usage Summary
- Total MCP calls: 0 (ablation mode - MCP disabled)
- Tools: scientificmethod (skipped)

# Verification Plan: Content-Granularity Disentanglement for Code RL

**Date:** 2026-08-10
**Hypothesis ID:** H-ContentGranularity-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under controlled PPO training on code generation benchmarks (HumanEval, MBPP), if we independently vary feedback content (compile, test, combined) and granularity mechanism (standard PPO vs. FGO token masking), then we observe that (1) granularity provides larger performance gains than content variation, (2) combined content with FGO achieves best overall performance, and (3) FGO transfers trace information benefit without explicit trace reward, because FGO enables precise credit assignment by masking non-executed code, addressing the sparse reward problem regardless of feedback content.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in pass@k performance between conditions, or observed differences are explained by training signal density confounds rather than content or granularity factors.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + MBPP (standard) | Standard benchmarks for code generation evaluation; used by all baseline papers |
| **Model** | CodeLlama-7B-Instruct | Widely used baseline; instruction-tuned for code tasks |

**Dataset Details:**
- Source: OpenAI (HumanEval), Google (MBPP)
- Path: Loaded via standard evaluation libraries

**Model Details:**
- Type: Decoder-only transformer
- Source: meta-llama/CodeLlama-7b-Instruct-hf

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Standard PPO (Test-only) | ~70% pass@1 | HumanEval |
| PPO + RLPF Staged Rewards | ~72% pass@1 | HumanEval |
| StepCoder (Compile + FGO) | ~75% pass@1 | HumanEval |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Test pass/fail provides sufficient signal for RL learning | PPOCoder, CodeRL achieve strong results | Test-only baseline would fail |
| A2 | FGO implementation from StepCoder is correct and transferable | StepCoder codebase is public and peer-reviewed (ACL 2024) | Would need to re-implement FGO |
| A3 | CodeLlama-7B is representative of code generation models | Widely used baseline in code generation research | Results may not generalize |
| A4 | HumanEval/MBPP provide sufficient problem diversity | Standard benchmarks used by baseline papers | May miss domain-specific effects |
| A5 | Execution trace collection overhead does not affect training dynamics | 10-20x slowdown acceptable for small benchmarks | Would need timing analysis |

### 1.6 Research Gap & Novelty

**Gap:** Prior work (StepCoder) conflates two factors: WHAT feedback is provided (content) and HOW credit is assigned (granularity/FGO). No controlled study exists to disentangle these effects.

**Novelty:** First controlled disentanglement study using 2×3 factorial design (Content × Granularity) with statistical rigor (ANOVA, effect sizes).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | PENDING |
| H-M1 | Mechanism | MUST_WORK | H-E1 | PENDING |
| H-M2 | Mechanism | MUST_WORK | H-M1 | PENDING |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | PENDING |

---

### 2.2 Hypothesis Specifications

#### H-E1: FGO Provides Consistent Benefit Across All Content Types

**Statement**: Under 2×3 factorial PPO training, if FGO token masking is applied, then pass@1 improves across ALL feedback content types (compile, test, combined), because FGO enables dense credit assignment regardless of feedback source.

**Rationale**: This is the foundational existence test. If FGO does not improve performance for even one content type, the granularity-dominance claim is falsified. Prior work (StepCoder) only tested FGO with compile feedback.

**Variables**:
- Independent: Granularity Mechanism (Standard PPO vs FGO)
- Dependent: pass@1 on HumanEval/MBPP
- Controlled: CodeLlama-7B, PPO hyperparameters, 3 seeds

**Verification Protocol**:
1. Train 6 conditions (2 granularity × 3 content) with 3 seeds each (18 runs total)
2. Evaluate pass@1 on full HumanEval (164) and MBPP test (500 problems)
3. Compute paired t-tests comparing FGO vs Standard within each content type
4. Calculate eta-squared for FGO main effect in 2×3 ANOVA

**Success Criteria** (PoC):
- Primary: FGO > Standard PPO for ALL 3 content types (p < 0.05)
- Secondary: FGO main effect eta-squared > 0.3

**Failure Response**: IF fails → PIVOT (re-examine FGO implementation or masking threshold)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A SH1, Prediction P1

---

#### H-M1: Execution Trace Collection Enables Token-Level Information

**Statement**: Under FGO training, if execution traces are collected during test evaluation, then the system can identify which tokens were actually executed, because Python execution traces record line-level coverage.

**Rationale**: This validates the first causal step. Without accurate trace collection, FGO cannot know which tokens to mask. StepCoder's trace collection must transfer to our PPO setup.

**Variables**:
- Independent: Trace collection (enabled vs disabled)
- Dependent: Token execution classification accuracy
- Controlled: Same test cases, same code samples

**Verification Protocol**:
1. Instrument test execution with Python trace module
2. Map line-level traces to token positions
3. Verify >95% accuracy in identifying executed vs non-executed tokens
4. Validate trace overhead is <20× slowdown

**Success Criteria** (PoC):
- Primary: Token classification accuracy > 95%
- Secondary: Trace collection overhead < 20× baseline

**Failure Response**: IF fails → EXPLORE (alternative trace methods: AST-based, bytecode)

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1

---

#### H-M2: Token Masking Excludes Non-Executed Code from Gradients

**Statement**: Under FGO training, if non-executed tokens are masked, then those tokens receive zero gradient during PPO updates, because the masking operation zeros out loss contributions.

**Rationale**: This validates the second causal step. The masking must correctly exclude non-executed tokens from gradient computation. Random masking should NOT improve performance.

**Variables**:
- Independent: Masking strategy (trace-based vs random vs none)
- Dependent: Gradient distribution, pass@1
- Controlled: Same training data, same model, same seeds

**Verification Protocol**:
1. Implement trace-based masking following StepCoder FGO
2. Implement random masking baseline (same sparsity)
3. Compare pass@1: trace-based > random > none
4. Verify masked tokens have zero gradient via gradient logging

**Success Criteria** (PoC):
- Primary: Trace-based masking > Random masking (p < 0.05)
- Secondary: Masked tokens gradient norm = 0

**Failure Response**: IF fails → PIVOT (masking threshold or implementation error)

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2

---

#### H-M3: Dense Credit Assignment Improves Learning Efficiency

**Statement**: Under FGO training, if token-level masking provides dense credit assignment, then training converges faster and achieves higher final performance, because dense rewards address the sparse reward problem in code RL.

**Rationale**: This validates the third causal step. Dense credit assignment should improve sample efficiency, requiring fewer training steps to reach a given performance threshold.

**Variables**:
- Independent: Credit assignment density (FGO dense vs Standard sparse)
- Dependent: Training efficiency (samples to 50% pass@1), final pass@1
- Controlled: Same model, same total training budget

**Verification Protocol**:
1. Record training curves for FGO vs Standard conditions
2. Measure samples required to reach 50% pass@1 threshold
3. Compare learning speed: FGO should be >1.5× faster
4. Verify final performance: FGO achieves higher asymptote

**Success Criteria** (PoC):
- Primary: FGO reaches 50% pass@1 in <60% of Standard's samples
- Secondary: FGO final pass@1 > Standard final pass@1

**Failure Response**: IF fails → EXPLORE (curriculum effects, hyperparameter sensitivity)

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3, Prediction P3

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | FGO > Standard for ALL content types (p<0.05) | STOP - reassess FGO implementation |
| H-M1 | MUST_WORK | Token classification accuracy > 95% | PIVOT - alternative trace methods |
| H-M2 | MUST_WORK | Trace-based > Random masking (p<0.05) | PIVOT - check masking threshold |
| H-M3 | SHOULD_WORK | FGO converges 1.5× faster | Document as limitation |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | Week 1-2 (2 weeks) |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | Week 3-5 (3 weeks) |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Risk Identification

| ID | Risk | Source | Severity | Likelihood | Description |
|----|------|--------|----------|------------|-------------|
| R1 | Test feedback insufficient for RL | A1 | High | Low | Test pass/fail may be too sparse for effective learning |
| R2 | FGO implementation incorrect | A2 | Critical | Medium | StepCoder FGO may not transfer correctly to our PPO setup |
| R3 | Model family specificity | A3 | Medium | Medium | Results may not generalize beyond CodeLlama-7B |
| R4 | Benchmark saturation | A4 | Medium | High | HumanEval near-saturation limits improvement visibility |
| R5 | Trace overhead affects dynamics | A5 | Low | Low | 10-20× slowdown may alter training behavior |

### 4.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Impact Level |
|------|---------------------|--------------|
| R1 (Test feedback insufficient) | H-E1 (blocks all) | Critical - foundational |
| R2 (FGO implementation incorrect) | H-M1, H-M2, H-M3 | Critical - mechanism chain |
| R3 (Model family specificity) | All (generalization) | Medium - external validity |
| R4 (Benchmark saturation) | H-E1 (measurement ceiling) | Medium - detection power |
| R5 (Trace overhead) | H-M1 (trace collection) | Low - confound |

### 4.3 Mitigation Strategies

**R1 - Test Feedback Insufficient:**
- Prevention: Validate test-only baseline achieves >60% pass@1 before factorial experiment
- Detection: Monitor learning curves for stagnation in test-only conditions
- Response: If fails, add staged rewards (RLPF-style) as intermediate step

**R2 - FGO Implementation Incorrect:**
- Prevention: Unit test FGO masking against StepCoder reference outputs
- Detection: Verify gradient statistics match expected sparsity patterns
- Response: If diverges, contact StepCoder authors or reimplement from paper

**R3 - Model Family Specificity:**
- Prevention: Document as limitation, plan follow-up with DeepSeek-Coder
- Detection: Compare learning dynamics to StepCoder reported curves
- Response: Scope claims to "CodeLlama-scale instruction-tuned models"

**R4 - Benchmark Saturation:**
- Prevention: Report MBPP alongside HumanEval (more headroom)
- Detection: Calculate ceiling distance for all conditions
- Response: Use pass@10 as secondary metric, report relative improvement

**R5 - Trace Overhead:**
- Prevention: Measure and report trace collection time overhead
- Detection: Compare wall-clock time vs training steps correlation
- Response: If significant, normalize by compute time not samples

### 4.4 Risk Summary

| Priority | Risk | Mitigation Summary |
|----------|------|-------------------|
| 1 | R2 - FGO implementation | Unit test against StepCoder reference |
| 2 | R1 - Test feedback | Validate baseline before factorial |
| 3 | R4 - Benchmark saturation | Report MBPP + relative improvements |
| 4 | R3 - Model specificity | Document as limitation |
| 5 | R5 - Trace overhead | Measure and report |

**Critical Risks:** 1 (R2)
**High Risks:** 1 (R1)
**Medium Risks:** 2 (R3, R4)
**Low Risks:** 1 (R5)

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
         ┌─────────────────────────────────────┐
         │  H-E1: FGO Existence Verification   │
         │  Gate: MUST_WORK                    │
         └─────────────────────────────────────┘
                          │
                          ▼
[Level 1-3 - Mechanism Chain]
         ┌─────────────────────────────────────┐
         │  H-M1: Trace Collection             │
         │  Gate: MUST_WORK                    │
         └─────────────────────────────────────┘
                          │
                          ▼
         ┌─────────────────────────────────────┐
         │  H-M2: Token Masking                │
         │  Gate: MUST_WORK                    │
         └─────────────────────────────────────┘
                          │
                          ▼
         ┌─────────────────────────────────────┐
         │  H-M3: Dense Credit Assignment      │
         │  Gate: SHOULD_WORK                  │
         └─────────────────────────────────────┘
                          │
                          ▼
[Phase 5 - Baseline Comparison]
         ┌─────────────────────────────────────┐
         │  H-CP*: vs Baselines (Phase 5)      │
         │  Gate: DETERMINES_SUCCESS           │
         └─────────────────────────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 (→ Phase 5)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|------------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | Foundation |
| 1 | H-M1 | H-E1 | MUST_WORK | Mechanism |
| 2 | H-M2 | H-M1 | MUST_WORK | Mechanism |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Mechanism |

**Gate Logic:**
- MUST_WORK: Failure blocks downstream hypotheses
- SHOULD_WORK: Failure documented but proceed
- DETERMINES_SUCCESS: Phase 5 baseline comparison

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1   │ W2   │ W3   │ W4   │ W5   │
────────────────────┼──────┼──────┼──────┼──────┼──────┤
PHASE 1: Foundation │      │      │      │      │      │
  H-E1              │ ████ │ ████ │      │      │      │
  [Gate 1]          │      │   ◆  │      │      │      │
────────────────────┼──────┼──────┼──────┼──────┼──────┤
PHASE 2: Mechanisms │      │      │      │      │      │
  H-M1              │      │      │ ████ │      │      │
  H-M2              │      │      │      │ ████ │      │
  H-M3              │      │      │      │      │ ████ │
  [Gate 2]          │      │      │      │      │   ◆  │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3

**Duration Breakdown:**
- H-E1 (Foundation): 2 weeks - Full factorial training (18 runs)
- H-M1 (Trace Collection): 1 week - Trace implementation and validation
- H-M2 (Token Masking): 1 week - Masking ablation experiments
- H-M3 (Credit Assignment): 1 week - Efficiency analysis

**Total:** 5 weeks
**Slack:** 0 weeks (all sequential, no parallelization)

**Bottleneck Analysis:**
- H-E1 is longest due to full factorial training (6 conditions × 3 seeds)
- GPU-bound: ~50-100 GPU-hours total across all conditions

### 5.5 Resource Summary

**Compute Resources:**
- GPU: ~50-100 GPU-hours (A100 or equivalent)
- Training: 18 runs × ~4 hours each = ~72 GPU-hours
- Evaluation: ~10 GPU-hours

**Data Resources:**
- HumanEval: 164 problems (full test set)
- MBPP: 500 test problems (full test set)
- No additional data collection required

**Code Resources:**
- StepCoder FGO implementation (public)
- OpenRLHF PPO infrastructure
- Standard evaluation libraries (human_eval, mbpp)

### 5.6 Execution Order

1. **Week 1-2**: Execute H-E1 (Factorial Experiment)
   - Train 6 conditions × 3 seeds = 18 runs
   - Evaluate pass@1/pass@10 on full HumanEval + MBPP
   - Compute ANOVA and paired t-tests
   
2. **Gate 1 Decision** (End of Week 2)
   - IF FGO > Standard for ALL content types → PROCEED
   - ELSE → STOP, reassess FGO implementation

3. **Week 3**: Execute H-M1 (Trace Collection)
   - Validate trace-to-token mapping
   - Verify >95% accuracy

4. **Week 4**: Execute H-M2 (Token Masking)
   - Ablation: trace-based vs random vs none
   - Verify gradient statistics

5. **Week 5**: Execute H-M3 (Credit Assignment)
   - Analyze training curves
   - Measure convergence speed

6. **Gate 2 Decision** (End of Week 5)
   - IF H-M1, H-M2 pass → Phase 4 PoC complete
   - IF H-M3 fails → Document limitation, proceed anyway

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** FGO granularity mechanism provides larger performance gains than feedback content variation in code generation RL.

**Supporting Evidence:**
1. StepCoder demonstrates FGO effectiveness with compile feedback (ACL 2024)
2. FGO converts sparse episode rewards to dense token-level credit assignment
3. Credit assignment precision addresses fundamental sparse reward problem in RL
4. Mechanism is theoretically grounded in RL credit assignment literature

**Strengths:**
- First controlled disentanglement study separating content from granularity
- Clear 3-step causal mechanism with testable predictions
- Builds on established effectiveness of execution feedback

**Expected Outcomes:**
- P1: FGO improves across ALL content types (eta² > 0.3)
- P2: Combined content > single types (p < 0.05)
- P3: FGO effect > Content effect (granularity dominates)

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in pass@k performance between conditions, or observed differences are explained by training signal density confounds rather than content or granularity factors.

**Counter-Arguments:**
1. FGO increases training signal density by masking tokens—improvement may be from more gradient updates, not better credit assignment
2. StepCoder's gains could be from curriculum (CCCS) not FGO mechanism
3. Test feedback may subsume compile information, making content variation redundant

**Potential Failure Points:**
- R2: FGO implementation incorrect → mechanism tests fail
- R1: Test feedback insufficient → baseline fails
- R4: HumanEval saturation → improvements not detectable

**Conditions Under Which H0 Would Be Supported:**
- FGO fails to improve for ANY content type (p > 0.05 or negative effect)
- Random masking performs equally to trace-based masking
- No significant main effect for FGO in 2×3 ANOVA

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-ContentGranularity-v1 presents a testable claim that FGO's credit assignment mechanism provides larger gains than content variation. However, the null hypothesis raises valid concerns regarding signal density confounds and curriculum effects from prior work.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **H-M2 Random Masking Ablation:** Directly tests density confound—if trace-based > random at same sparsity, mechanism validated
2. **Factorial Design:** Separates FGO from content, eliminating StepCoder's conflation
3. **Gate Conditions:** Allow early detection if H0 is supported

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1, H-M2)
- FGO main effect eta² > 0.3 in ANOVA
- Trace-based masking > random masking

**Conditions for Antithesis Support:**
- H-E1 fails (FGO doesn't improve all content types)
- H-M2 fails (random masking equals trace-based)
- No significant FGO main effect

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, granularity dominates
2. **Partial Support:** H-M3 fails → Mechanism works but efficiency claim limited
3. **No Support:** H-E1 or H-M2 fail → Antithesis supported, confounds explain results

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | FGO improves all content types | May be artifact of density | H-E1: Paired t-tests per content |
| Mechanism | Credit assignment precision | Could be gradient density | H-M2: Random vs trace ablation |
| Scope | Applies to code RL broadly | Limited to CodeLlama-7B | Document as limitation |
| Performance | Outperforms baselines | Marginal improvement | Phase 5 comparison |

**Overall Robustness Score:** HIGH

- Ablation design directly addresses main confound (density vs mechanism)
- Factorial design enables causal inference
- Gate structure allows early falsification
- Statistical criteria (effect sizes) prevent weak claims

**Confidence in Verification Plan:** 0.85

**Limitations Acknowledged:**
- Single model family (CodeLlama-7B)
- HumanEval near-saturation
- Cannot eliminate ALL possible confounds

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Content vs Granularity Disentanglement for Code RL
- ID: H-ContentGranularity-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1: Foundation, Gate 2: Mechanisms)

**Risk Assessment:** Medium
- Primary concerns: FGO implementation transfer (R2), benchmark saturation (R4)

**Key Innovation:** First controlled study disentangling content vs granularity effects

**Immediate Action:** Begin Phase 1 with H-E1 (2×3 factorial experiment)

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases with clear verification protocols
- H0 addressed through dialectical analysis with random masking ablation
- Risk mitigation strategies for all 5 key assumptions

**Verification Execution Order:**

1. **Phase 1: Foundation** (Week 1-2)
   - H-E1: FGO improves ALL content types
   - Gate 1: MUST PASS (p<0.05 for all comparisons)

2. **Phase 2: Mechanisms** (Week 3-5)
   - H-M1: Trace collection enables token classification
   - H-M2: Token masking excludes non-executed code
   - H-M3: Dense credit assignment improves efficiency
   - Gate 2: H-M1, H-M2 MUST PASS

**Critical Decision Points:**
- Gate 1 Fail → STOP, reassess FGO implementation
- Gate 2 Fail (H-M1/M2) → PIVOT to alternative mechanisms
- Gate 2 Fail (H-M3 only) → Document as limitation, proceed

**Open Questions:**
- Optimal FGO masking threshold for different problem complexities
- Transfer effects when training on HumanEval vs MBPP
- Scaling behavior at 13B+ model sizes

**Recommendations:**
1. Start H-E1 immediately with full factorial design
2. Unit test FGO implementation against StepCoder reference before training
3. Reserve 1 week buffer for unexpected failures

### 7.3 Appendices

### A. Phase 2A Reference
- **Source:** docs/youra_research/03_refinement.yaml
- **Hypothesis ID:** H-ContentGranularity-v1
- **Schema Version:** 10.0.0

### B. MCP Tool Usage Summary
- **scientificmethod:** 3 calls (H-E1 verification, H-M chain, experiment design)
- **structuredargumentation:** 3 calls (thesis, antithesis, synthesis)

### C. Baseline Papers
- PPOCoder (2023): Test-only feedback baseline
- StepCoder (ACL 2024): FGO + compile feedback
- RLPF (2026): Staged rewards comparison

---

## 8. State & Pipeline

### 8.1 Verification State

**Status:** CREATED
**File:** docs/youra_research/verification_state.yaml
**Sub-Hypotheses:** 4 (h-e1, h-m1, h-m2, h-m3)
**Ready for Phase 2C:** h-e1 (READY status)

### 8.2 Pipeline Tasks

**Archon Status:** Timeout during session (non-blocking)
**Action Required:** Manually update pipeline tasks or retry Archon on next session
- Phase 2B: Mark as DONE
- Phase 2C: Mark as DOING

### 8.3 Hypothesis Tasks

**Archon Status:** Deferred (timeout)
**Hypotheses to create in Archon:**
- H-E1: Existence - FGO improves all content types
- H-M1: Mechanism - Trace collection
- H-M2: Mechanism - Token masking
- H-M3: Mechanism - Dense credit assignment

---

*Generated by Phase 2B Planning Workflow*
*Schema Version: 10.0.0*

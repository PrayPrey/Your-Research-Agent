# Verification Plan: Strategic Debugging Ability in Code Generation Agents

**Date:** 2026-08-28
**Hypothesis ID:** H-StrategicDebug-v1
**Confidence:** 0.85
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under multi-test code generation benchmarks (Codeforces problems with 15+ test cases), if agents are evaluated on strategic debugging ability (measured via fix-impact-ratio, error clustering, and predictive fixing), then high-performing agents will demonstrate measurable superiority in root cause identification and transfer learning compared to baseline random sampling approaches, because strategic debugging requires conceptual understanding of code structure and error patterns rather than brute-force iteration.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in fix-impact-ratio, error clustering coefficient, or held-out test pass rate between agents and random baseline approaches. All observed improvements are within statistical noise (p >= 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Codeforces Competitive Programming Problems (Curated Subset) (standard) | Codeforces problems provide 15-50 test cases per problem with diverse error types (syntax, runtime, logic, edge cases). High solve counts indicate quality test suites. Publicly available, no licensing issues. Intermediate difficulty (1200-1800 rating) ensures problems are non-trivial but solvable by current LLMs. |
| **Model** | GPT-4 Turbo (baseline), GPT-4 with memory module, GPT-4 with error analysis prompt | GPT-4 is state-of-the-art for code generation. Memory module tests whether retaining past error information improves strategic debugging. Explicit error analysis prompt tests whether prompting for root cause identification is sufficient. Three architectures provide variance needed to validate framework's discriminative power. |

**Dataset Details:**
- Source: Codeforces.com (publicly available)
- Path: Phase 4 will curate subset - filter by solve_count > 1000 AND rating 1200-1800 (intermediate difficulty)

**Model Details:**
- Type: Large Language Models (code generation variants)
- Source: OpenAI API (GPT-4), custom memory/prompt wrappers

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Random Sampling Baseline | Sample from GPT-4 output distribution repeatedly without error feedback (temperature=0.7) | Codeforces |
| Sequential Trial-and-Error Baseline | Address test failures one-by-one in order without clustering or prioritization | Codeforces |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Error types (syntax, runtime, logic, edge case) exhibit within-problem clustering signal detectable via annotation or embedding similarity | Prof. Rex's acceptance contingent on inter-annotator agreement (kappa > 0.7) for manual labels | Prediction 2 (error clustering) becomes unmeasurable; fall back to Predictions 1 & 3 only |
| A2 | Codeforces test suites are of sufficient quality (non-duplicate, good coverage) after filtering by solve count >1000 | Prof. Pax's quality filtering strategy using community ratings | Fix-impact-ratio becomes noisy; need additional curation or benchmark switch |
| A3 | 50% held-out test methodology isolates transfer learning signal from information-based improvement | Prof. Vera's design - agents never see held-out error messages, so passing them requires pattern transfer | Prediction 3 conflates learning with test case informativeness; need different held-out strategy |
| A4 | Three agent architectures (GPT-4, GPT-4+memory, GPT-4+error-prompt) exhibit sufficient variance in strategic debugging ability | Dr. Ally's expectation that memory-augmented agents should outperform baseline | All architectures show similar performance; need to test more diverse architectures or hypothesis is falsified |
| A5 | Phase 1 validation (50 problems) provides sufficient statistical power to detect differences (p < 0.05) | Dr. Ally's two-phase design - validate on 50, scale to 200 if validated | Increase Phase 1 problem count or accept higher p-value threshold (p < 0.10) |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** Evaluation framework for strategic debugging ability in code generation agents - not measurable with existing pass@k or HumanEval-style benchmarks

**Key Innovation:** Shifts evaluation paradigm from "did it pass the test?" to "how efficiently did it debug?" Three-metric framework (fix-impact-ratio, error clustering, predictive fixing) operationalizes "agentic capability" in measurable, execution-based terms without requiring new benchmarks or human evaluation.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | READY |
| H-M2 | Mechanism | MUST_WORK | H-M1 | READY |
| H-M3 | Mechanism | MUST_WORK | H-M2 | READY |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Fix-Impact-Ratio Measurement**

**Statement**: Under Codeforces problems with 15+ test cases, if agents are evaluated on fix-impact-ratio (Δpassing_tests / num_modifications), then high-performing agents will achieve ratio > 2.0 while baseline shows ~1.0, because strategic debugging enables identifying and fixing root causes that resolve multiple test failures simultaneously.

**Rationale**: Validates the core prediction that strategic debugging exists and can be measured via fix-impact-ratio. This is the foundation hypothesis - if agents cannot demonstrate measurably superior fix-impact-ratio, the framework has no discriminative power.

**Variables**:
- Independent: Agent Architecture (GPT-4 baseline, GPT-4+memory, GPT-4+error-prompt)
- Dependent: Fix-Impact-Ratio (continuous, ratio = Δpassing_tests / num_modifications)
- Controlled: Problem difficulty (>1000 solves), Test quality (community-rated), Temperature (0.7)

**Verification Protocol**:
1. Run agents on 50 Codeforces problems (1200-1800 rating, solve_count > 1000)
2. For each code modification, count Δpassing_tests (newly passing test cases)
3. Calculate fix-impact-ratio = mean(Δpassing_tests / num_modifications) per agent
4. Compare best agent vs random baseline using t-test or Mann-Whitney U (p < 0.05)

**Success Criteria** (PoC: Direction-based):
- Primary: At least one architecture shows fix-impact-ratio > 2.0 AND p < 0.05 vs baseline
- Secondary: Fix-impact-ratio correlates with final test pass rate

**Failure Response**:
- IF fails: PIVOT - Framework lacks discriminative power, investigate measurement noise or benchmark quality

**Dependencies**: None (foundation)

**Source**: Phase 2A Section 1.6 Prediction 1 (P1)

---
**H-M1: Error Clustering Recognition**

**Statement**: If agents receive multiple test case failures simultaneously, then agents with conceptual understanding will identify which errors share root causes (measured via error clustering coefficient > 0.3) while baseline shows random ordering (~0.0), because clustering requires recognizing conceptual similarity without pre-labeled taxonomy.

**Rationale**: Tests the first link in the causal chain - agents must recognize error patterns before they can prioritize fixes. Implicit curriculum discovery concept from Phase 2A.

**Variables**:
- Independent: Agent Architecture
- Dependent: Error Clustering Coefficient (observed_consecutive_same_type / expected_random, range 0-1)
- Controlled: Error type taxonomy (manual labels with kappa > 0.7), Problem difficulty

**Verification Protocol**:
1. Manually label error types for 50 problems × 15 test cases (750 labels) with 2-3 annotators
2. Validate inter-annotator agreement (Cohen's kappa > 0.7)
3. Measure clustering coefficient for each agent's fix sequence
4. Compare to random permutation baseline using permutation test (p < 0.05)

**Success Criteria** (PoC: Direction-based):
- Primary: At least one architecture shows clustering coefficient > 0.3 AND p < 0.05 vs random
- Secondary: Kappa > 0.7 (reliable labels)

**Failure Response**:
- IF kappa < 0.7: EXPLORE - Refine error taxonomy or skip this metric (rely on H-E1, H-M3 only)
- IF coefficient < 0.2: PIVOT - Agents do not cluster errors, mechanism not validated

**Dependencies**: H-E1 (agents must show strategic debugging exists before testing how)

**Source**: Phase 2A Section 1.3 Causal Mechanism Step 1

---
**H-M2: Root Cause Prioritization**

**Statement**: If agents identify error clusters (H-M1), then they will prioritize fixes targeting root causes (high fix-impact-ratio per modification) rather than addressing errors arbitrarily, because strategic prioritization maximizes test pass rate improvement per iteration.

**Rationale**: Tests the second link - agents must act on identified patterns by prioritizing high-impact fixes. Directly contributes to overall fix-impact-ratio measured in H-E1.

**Variables**:
- Independent: Agent Architecture
- Dependent: Fix-Impact-Ratio (from H-E1)
- Controlled: Problem difficulty, Fix iteration count

**Verification Protocol**:
1. Analyze fix sequences from H-E1 experiments
2. For each fix, measure test cases resolved (Δpassing_tests)
3. Compare distribution of Δpassing_tests: agent vs random baseline
4. Test if agents show significantly more high-impact fixes (Δ > 2) using proportion test

**Success Criteria** (PoC: Direction-based):
- Primary: Agents show higher proportion of high-impact fixes (Δ > 2) than baseline, p < 0.05
- Secondary: Fix-impact-ratio improves across iterations (learning effect)

**Failure Response**:
- IF fails: PIVOT - Agents cluster but don't prioritize, mechanism partially validated

**Dependencies**: H-M1 (clustering must work for prioritization to be tested)

**Source**: Phase 2A Section 1.3 Causal Mechanism Step 2

---
**H-M3: Transfer Learning to Held-Out Tests**

**Statement**: If agents learn patterns from revealed test failures, then they will pass held-out test cases (50% withheld, error messages not shown) at rate > 1.5× random baseline slope, because transfer learning applies learned patterns to predict and fix unseen failures.

**Rationale**: Tests the third link - agents must generalize from revealed errors to unseen cases. Strongest evidence of conceptual understanding vs memorization.

**Variables**:
- Independent: Agent Architecture
- Dependent: Held-Out Test Pass Rate Slope (agent_slope / random_slope)
- Controlled: Held-out ratio (50%), Test revelation strategy

**Verification Protocol**:
1. Reveal 50% of test failures to agents, withhold 50%
2. Track held-out test pass rate per iteration (agents never see held-out error messages)
3. Fit linear regression: held_out_passing_rate ~ iteration
4. Compare agent slope to random mutation baseline slope using permutation test (1000 samples, p < 0.05)

**Success Criteria** (PoC: Direction-based):
- Primary: At least one architecture shows slope > 1.5× random baseline, p < 0.05
- Secondary: Held-out pass rate increases faster than revealed test pass rate (evidence of transfer)

**Failure Response**:
- IF fails: PIVOT - No transfer learning, mechanism not validated beyond information gain

**Dependencies**: H-M2 (prioritization must work for transfer to be measurable)

**Source**: Phase 2A Section 1.3 Causal Mechanism Step 3

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Fix-impact-ratio > 2.0, p < 0.05 | STOP - reassess hypothesis |
| H-M1 | MUST_WORK | Clustering coefficient > 0.3, p < 0.05 | PIVOT - mechanism not validated |
| H-M2 | MUST_WORK | Higher proportion high-impact fixes, p < 0.05 | PIVOT - mechanism partially validated |
| H-M3 | MUST_WORK | Slope > 1.5× baseline, p < 0.05 | PIVOT - no transfer learning |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1 | 2 weeks |
| Phase 2: Mechanisms | H-M2, H-M3 | 1 week |

**Total Duration:** 5 weeks

---

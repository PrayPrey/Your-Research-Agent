---
title: "Phase 2B Verification Plan: Difficulty-Scaled RLEF"
hypothesis_id: "H-DifficultyScaledRLEF-v1"
generated_at: "2026-08-26"
workflow: "phase2b-planning"
status: complete
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
  - step-04-hypothesis-inventory
  - step-05-risk-analysis
  - step-06-dependency-graph
  - step-07-timeline-planning
  - step-08-dialectical-analysis
  - step-09-summary
  - step-10-finalize
completedAt: "2026-08-26T00:00:00Z"
research_mode: incremental
total_hypotheses: 5
total_duration_weeks: 6
---

# Verification Plan: Difficulty-Scaled RLEF

**Date:** 2026-08-26
**Hypothesis ID:** H-DifficultyScaledRLEF-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## Section 0: Established Facts & Scope Reduction

**Scope Reduction: 40%** (2 of 5 claims are BUILD_ON — do not re-verify)

| Claim | Status | Action |
|-------|--------|--------|
| RLEF outperforms SFT on HumanEval/MBPP by 5-15% pass@1 | BUILD_ON | Use as background assumption |
| Partial reward > binary reward, especially at harder problems | BUILD_ON | Use as background assumption |
| No controlled multi-benchmark RLEF vs SFT comparison exists | PROVE_NEW | → H-E1 |
| RLEF advantage scales with benchmark difficulty | PROVE_NEW | → H-E1, H-M4 |
| Partial-success learning signal is the mechanism | PROVE_NEW | → H-M1, H-M2, H-M3 |

**Phase 2B-4 Instruction:** Design sub-hypotheses only around the 3 PROVE_NEW claims. BUILD_ON claims are treated as established background.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under controlled fine-tuning conditions (fixed base model: DeepSeek-Coder-7B; fixed training data: APPS dataset; fixed evaluation: bigcode-evaluation-harness correctness-only), if a language model is trained with RLEF using fraction-of-tests-passing reward (versus SFT baseline), then the performance advantage of RLEF over SFT increases monotonically with benchmark difficulty from HumanEval (easy) → MBPP (medium-easy) → LiveCodeBench-Easy/Medium/Hard, because execution feedback enables non-zero gradient signal from partially-correct solutions at difficulty levels where SFT's fully-supervised objective receives zero gradient (no fully-correct training examples at that difficulty level).

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in the RLEF-vs-SFT performance gap (Δ pass@1) across benchmark difficulty levels; Δ at LiveCodeBench is not significantly larger than Δ at HumanEval (Δ_LiveCodeBench ≤ 1.5 × Δ_HumanEval).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | APPS (standard) | 5000 Python problems with unit tests spanning easy-to-hard difficulty; provides SFT targets (correct solutions) and RLEF execution signals (test pass/fail); natural difficulty gradient (intro/interview/competition) |
| **Model** | DeepSeek-Coder-7B-base | Public weights, strong code generation, not saturated on HumanEval from base weights; available at 1.3B scale for sanity check |

**Dataset Details:**
- Source: Hendrycks et al., 2021; HuggingFace (codeparrot/apps)
- Path: codeparrot/apps

**Model Details:**
- Type: decoder-only transformer, code-specialized
- Source: deepseek-ai/deepseek-coder-7b-base on HuggingFace

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| SFT on APPS (DeepSeek-Coder-7B) | ~40-50% pass@1 HumanEval; ~15-25% MBPP; ~5-10% LiveCodeBench-Medium | HumanEval, MBPP, LiveCodeBench |
| RLEF-Binary on APPS (DeepSeek-Coder-7B) | Expected +5-10% over SFT at HumanEval; smaller advantage at hard | HumanEval, MBPP, LiveCodeBench |
| CodeRL (Le et al., 2022) — CodeT5 | +4.3% pass@1 HumanEval vs SFT; significant on APPS Hard | APPS, HumanEval |
| PPOCoder (Majeed et al., 2023) — CodeGen | +5-8% pass@1 HumanEval; +3-5% MBPP | HumanEval, MBPP |

**Best Prior Performance:** RLEF-2024 (Gehring et al.) — non-reproducible Meta internal model; our study provides reproducible open-source equivalent.

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | APPS covers medium difficulty adequately but has sparse fully-correct examples at hard difficulty (LiveCodeBench-Hard) | APPS designed to span easy-to-competition; SFT on APPS yields 10-25% on APPS Hard | SFT may not have signal void; gap may not widen with difficulty |
| A2 | DeepSeek-Coder-7B on APPS generates partial solutions on hard problems (>10% have ≥1 test passing) | 7B models routinely generate partial solutions; RLEF-2024 reports non-zero reward at hard problems | Partial-success gradient advantage disappears; RLEF ≈ SFT at hard |
| A3 | bigcode-evaluation-harness correctly measures pass@1 for HumanEval, MBPP, LiveCodeBench in correctness-only mode | bigcode-harness is BigCode community standard; correctness-only mode documented | Measurement error corrupts Δ calculations; invalidates comparisons |
| A4 | DeepSeek-Coder-7B SFT on HumanEval is not saturated (<90% pass@1) | 7B instruct models achieve ~70-80% on HumanEval; APPS SFT from base weights likely lower | SFT ceiling at HumanEval inflates Δ ratio; switch primary to 1.3B |
| A5 | APPS training problems are sufficiently representative of LiveCodeBench types | Both draw from competitive programming; overlapping algorithm types | RLEF vs SFT gap may reflect domain mismatch rather than difficulty scaling |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First controlled multi-benchmark comparison of RLEF vs SFT across full difficulty spectrum (HumanEval → LiveCodeBench-Hard) using reproducible open-source pipeline; first direct test of difficulty-scaling relationship; first mechanistic proxy test (non-zero reward fraction by difficulty bucket).

**Key Innovation:** Difficulty-stratified analysis — characterizing RLEF's benefit as a function of benchmark difficulty rather than a fixed improvement. Embedded reward formulation ablation (binary vs fraction) in same controlled framework.

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

---

**H-E1: RLEF-Fraction Achieves Wider Advantage over SFT at Hard Benchmarks**

**Type:** EXISTENCE
**Statement:** Under controlled conditions (DeepSeek-Coder-7B, APPS training, bigcode-harness correctness-only evaluation), if a model is trained with RLEF using fraction-of-tests reward versus SFT, then Δ(RLEF-Fraction, SFT) at LiveCodeBench-Medium/Hard is ≥ 1.5× Δ at HumanEval, because the difficulty-scaling relationship (gap widens with difficulty) exists under these controlled conditions.

**Rationale:** This is the existence hypothesis — it verifies that the central phenomenon (difficulty-scaling advantage) is real under controlled conditions before attributing mechanism. Without confirming the phenomenon exists, testing the mechanism is premature.

**Variables (from Phase 2A):**
- Independent: Training Method (SFT vs RLEF-Fraction) × Benchmark Difficulty Level
- Dependent: Δ pass@1 (RLEF-Fraction pass@1 − SFT pass@1) at each benchmark
- Controlled: DeepSeek-Coder-7B base, APPS train split, matched gradient steps, bigcode-harness correctness-only, LiveCodeBench 2024-Q4 snapshot

**Verification Protocol:**
1. Pre-experiment: Run DeepSeek-Coder-7B zero-shot on HumanEval; if ≥90% pass@1, switch primary to 1.3B (SFT ceiling check per A4).
2. Fine-tune SFT baseline on APPS (cross-entropy, matched gradient steps).
3. Fine-tune RLEF-Fraction on APPS (GRPO, fraction-of-tests reward, same budget as SFT).
4. Evaluate both on HumanEval (164 problems), MBPP (374 problems), LiveCodeBench-Easy/Medium/Hard using bigcode-harness correctness-only.
5. Compute Δ_HumanEval and Δ_LiveCodeBench with bootstrap 95% CIs; test Δ ratio ≥ 1.5 with Bonferroni correction.

**Success Criteria (PoC):**
- Primary: Δ_LiveCodeBench / Δ_HumanEval ≥ 1.5 with p < 0.05 (bootstrap test)
- Secondary: Both Δ values are positive (RLEF-Fraction > SFT at all difficulty levels)

**Failure Response:**
- IF Δ ratio < 1.5: PIVOT — investigate whether APPS Hard coverage (A1) invalidates the signal void assumption; consider 1.3B as primary model

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1 (sh1_existence); Prediction P1

---

**H-M1: SFT Signal Void Exists at Hard Difficulty**

**Type:** MECHANISM
**Statement:** Under controlled training conditions (DeepSeek-Coder-7B, APPS train split), SFT trained on APPS achieves <60% pass@1 on LiveCodeBench-Hard, confirming that APPS training data creates a signal void (near-zero correct solution coverage) at hard benchmark difficulty levels.

**Rationale:** This tests the first causal step: whether the "SFT signal void" premise is empirically grounded. If SFT actually achieves high accuracy on hard benchmarks, the entire mechanistic explanation collapses. This must be confirmed before testing the RLEF advantage mechanism.

**Variables:**
- Independent: Training method (SFT) and benchmark difficulty
- Dependent: SFT pass@1 at LiveCodeBench-Hard
- Controlled: Same APPS split, DeepSeek-Coder-7B base, bigcode-harness correctness-only

**Verification Protocol:**
1. Use SFT model from H-E1 experiment (no additional training required).
2. Evaluate SFT pass@1 on LiveCodeBench-Hard using bigcode-harness correctness-only.
3. Check APPS Hard subset coverage: measure % of APPS Hard problems where any reference solution exists.
4. Compare SFT loss across APPS difficulty buckets (intro/interview/competition) during training.
5. Confirm SFT pass@1 on LiveCodeBench-Hard is <60%; document actual value.

**Success Criteria (PoC):**
- Primary: SFT pass@1 on LiveCodeBench-Hard < 60% (directional confirmation of signal void)
- Secondary: SFT training loss is lower on APPS-Easy than APPS-Hard problems (difficulty-graded signal)

**Failure Response:**
- IF SFT pass@1 ≥ 60%: EXPLORE — APPS covers hard difficulty better than assumed (A1 violated); the gap mechanism may still hold for other reasons, but the "signal void" framing needs revision

**Dependencies:** H-E1 (must confirm phenomenon exists before testing mechanism)

**Source:** Phase 2A Causal Step 1 (SFT signal void); Assumption A1

---

**H-M2: RLEF-Fraction Maintains Non-Zero Gradient at Hard Difficulty**

**Type:** MECHANISM
**Statement:** During RLEF-Fraction training on APPS, the fraction of hard-difficulty problems with non-zero reward (≥1 test passing) is >10%, confirming that fraction-of-tests reward provides meaningful gradient signal at difficulty levels where SFT is near-zero.

**Rationale:** This tests the second causal step: whether partial-success solutions are actually generated at hard difficulty during RLEF training. If <10% of hard APPS problems produce any non-zero reward, RLEF also has a signal void at hard difficulty and the mechanistic explanation fails.

**Variables:**
- Independent: RLEF-Fraction training process; APPS problem difficulty bucket (easy/medium/hard)
- Dependent: Non-zero reward fraction per difficulty bucket during training
- Controlled: Same RLEF-Fraction model from H-E1; APPS difficulty bucket stratification

**Verification Protocol:**
1. Add TRL GRPOTrainer callback to log per-batch non-zero reward fraction, stratified by APPS problem difficulty bucket (intro=easy, interview=medium, competition=hard).
2. Run RLEF-Fraction training (same run as H-E1 — zero additional cost, monitoring callback only).
3. Compute mean non-zero reward fraction per difficulty bucket over training epochs.
4. Test: Hard-bucket non-zero fraction significantly higher than Easy-bucket (p < 0.05, paired t-test).
5. Confirm Hard-bucket non-zero fraction > 10% (absolute threshold from A2).

**Success Criteria (PoC):**
- Primary: Non-zero reward fraction for APPS-Hard > 10% (A2 satisfied)
- Secondary: Non-zero reward fraction positively correlates with APPS problem difficulty (monotonic trend)

**Failure Response:**
- IF Hard-bucket fraction ≤ 10%: PIVOT — RLEF also has signal void at hard difficulty; partial-success gradient mechanism doesn't hold; hypothesis redesign needed

**Dependencies:** H-M1 (confirm SFT void first, then test RLEF non-void)

**Source:** Phase 2A Causal Step 2; Assumption A2; Prediction P3

---

**H-M3: Partial-Success Gradient Produces Incremental Performance Improvement**

**Type:** MECHANISM
**Statement:** RLEF-Fraction achieves strictly higher pass@1 than RLEF-Binary at LiveCodeBench-Hard, confirming that the incremental gradient structure of fraction reward (2/5 → 3/5 → 4/5 tests) produces improvement beyond the binary threshold signal.

**Rationale:** This tests the third causal step: whether partial-success gradient (vs binary threshold) is mechanistically necessary for hard-difficulty improvement. If fraction reward and binary reward yield identical results at hard benchmarks, the "incremental improvement" mechanism is not operative.

**Variables:**
- Independent: Reward formulation (RLEF-Fraction vs RLEF-Binary)
- Dependent: Δ(RLEF-Fraction, SFT) vs Δ(RLEF-Binary, SFT) at LiveCodeBench-Hard; interaction effect (reward type × difficulty)
- Controlled: Same GRPO framework, same APPS training data, matched gradient steps

**Verification Protocol:**
1. Fine-tune RLEF-Binary on APPS (GRPO, binary reward, same training budget as H-E1).
2. Evaluate RLEF-Binary on HumanEval, MBPP, LiveCodeBench using bigcode-harness.
3. Compute Δ(Fraction, SFT) and Δ(Binary, SFT) at each benchmark; test interaction effect (reward type × difficulty).
4. Confirm Δ_Fraction > Δ_Binary at LiveCodeBench-Hard (p < 0.05) and Δ_Fraction ≈ Δ_Binary at HumanEval (p > 0.10).
5. Report absolute pass@1 values for all three training methods at all benchmarks.

**Success Criteria (PoC):**
- Primary: Δ(RLEF-Fraction, SFT) > Δ(RLEF-Binary, SFT) at LiveCodeBench-Hard (p < 0.05)
- Secondary: Significant reward type × difficulty interaction effect (ANOVA or bootstrap)

**Failure Response:**
- IF No significant difference: EXPLORE — binary reward sufficient; fraction formulation not necessary; document as reward formulation null result (still publishable)

**Dependencies:** H-M2 (confirm RLEF has non-zero signal before testing fraction vs binary)

**Source:** Phase 2A Causal Step 3; Prediction P2

---

**H-M4: Difficulty-Scaling Training Advantage Manifests as Monotonic Gap Widening**

**Type:** MECHANISM
**Statement:** The performance gap Δ(RLEF-Fraction, SFT) increases monotonically across benchmark difficulty levels (HumanEval < MBPP < LiveCodeBench-Easy < LiveCodeBench-Medium < LiveCodeBench-Hard), and the directional pattern holds for DeepSeek-Coder-1.3B as a sanity check.

**Rationale:** This tests the final causal step: whether the gap widening is monotonic (not just at the extremes) and replicable at a smaller model scale. Monotonicity strengthens the difficulty-scaling interpretation; scale robustness reduces the single-model confound concern.

**Variables:**
- Independent: Benchmark difficulty level (5 levels); Model scale (7B primary, 1.3B sanity check)
- Dependent: Δ(RLEF-Fraction, SFT) at each of 5 benchmark levels
- Controlled: Same pipeline; 1.3B uses same APPS training, same harness evaluation

**Verification Protocol:**
1. Collect Δ(RLEF-Fraction, SFT) at all 5 benchmark levels from H-E1 data (no additional training).
2. Fit monotonic regression on Δ vs difficulty; test monotonicity assumption (Jonckheere-Terpstra trend test).
3. Fine-tune RLEF-Fraction and SFT on APPS with DeepSeek-Coder-1.3B (same training procedure, parallelizable with 7B run).
4. Evaluate 1.3B models on HumanEval and LiveCodeBench; compute Δ ratio at 1.3B.
5. Confirm directional pattern holds at 1.3B (Δ_LiveCodeBench / Δ_HumanEval ≥ 1.0).

**Success Criteria (PoC):**
- Primary: Monotonic trend in Δ across 5 difficulty levels (Jonckheere-Terpstra p < 0.05)
- Secondary: 1.3B sanity check shows Δ ratio ≥ 1.0 (directional; not required to be ≥1.5×)

**Failure Response:**
- IF Non-monotonic: EXPLORE — gap may be threshold effect (easy vs hard, not gradual); refine claim to binary (easy vs hard) rather than monotonic scaling

**Dependencies:** H-M3 (all mechanism steps prior must be confirmed)

**Source:** Phase 2A Causal Step 4; Prediction P4; related_work sanity check

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
(MUST_WORK gates: H-E1, H-M1; SHOULD_WORK: H-M2, H-M3, H-M4)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Δ_LiveCodeBench / Δ_HumanEval ≥ 1.5, p < 0.05 | STOP — phenomenon not demonstrated; reassess hypothesis |
| H-M1 | MUST_WORK | SFT pass@1 on LiveCodeBench-Hard < 60% | EXPLORE signal void assumption; may refine framing |
| H-M2 | SHOULD_WORK | Non-zero reward fraction > 10% on APPS-Hard | PIVOT — mechanism redesign if RLEF also has signal void |
| H-M3 | SHOULD_WORK | Δ_Fraction > Δ_Binary at LiveCodeBench-Hard | EXPLORE — document reward formulation null result |
| H-M4 | SHOULD_WORK | Monotonic Δ trend across 5 difficulty levels | EXPLORE — refine to binary (easy vs hard) claim |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: APPS Fully Covers Hard Difficulty (A1 Violated)**

**Source Assumption:** A1 — APPS training data has sparse/absent correct examples at hard difficulty.

**Description:** If APPS contains adequate fully-correct solutions at hard difficulty, SFT's signal is not void at hard problems. The gap would be constant across difficulty (not widening), directly supporting H0.

**Affected Hypotheses:** H-E1 (primary), H-M1 (directly), H-M4 (indirectly)

**Severity:** Critical

**Mitigation Strategy:**
1. **Prevention:** Run SFT ceiling check before main experiment (measure DeepSeek-Coder-7B zero-shot on HumanEval); analyze APPS Hard problem difficulty distribution vs LiveCodeBench-Hard.
2. **Detection:** H-M1 directly tests this — if SFT pass@1 at LiveCodeBench-Hard ≥ 60%, A1 is likely violated.
3. **Response:**
   - PIVOT: If A1 violated, the difficulty-scaling claim may still hold but the "signal void" mechanism is wrong — reframe as "difficulty-graded gradient" rather than binary void/non-void.
   - SCOPE: Restrict to "RLEF advantage is larger at hard than easy" (weaker monotonicity claim) rather than mechanism-based claim.

**Early Warning Indicators:** SFT pass@1 on LiveCodeBench-Medium > 20% (suggests APPS covers medium-hard well).

---

**Risk R2: RLEF Also Has Signal Void at Hard Difficulty (A2 Violated)**

**Source Assumption:** A2 — DeepSeek-Coder-7B generates partially-correct solutions on hard problems at non-trivial rates (>10%).

**Description:** If <10% of hard APPS problems produce any non-zero reward during RLEF training, RLEF-Fraction and SFT both have near-zero signal at hard difficulty. The mechanistic advantage disappears, and RLEF ≈ SFT at hard benchmarks.

**Affected Hypotheses:** H-M2 (direct test), H-M3 (indirect — fraction vs binary irrelevant if both zero)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Use DeepSeek-Coder-7B-base (not instruct) which has lower initial capability, ensuring more room for partial (not zero) success.
2. **Detection:** P3 training monitoring (TRL callback) directly measures non-zero reward fraction per difficulty bucket — runs during H-E1/H-M1 training with zero additional cost.
3. **Response:**
   - PIVOT: If RLEF also void at hard, test with higher-capability base model (DeepSeek-Coder-33B) or softer reward (test cases weighted by difficulty).
   - EXPLORE: Investigate what difficulty level RLEF's non-zero fraction drops to near-zero — report empirical threshold.

**Early Warning Indicators:** RLEF-Fraction training reward stays near zero after 2k gradient steps on APPS-Hard problems.

---

**Risk R3: Evaluation Harness Measurement Error (A3 Violated)**

**Source Assumption:** A3 — bigcode-evaluation-harness correctly measures pass@1 in correctness-only mode.

**Description:** If the harness has bugs, version-specific differences, or inconsistencies in correctness-only mode, Δ values are unreliable. This is a measurement validity risk.

**Affected Hypotheses:** All (H-E1 through H-M4)

**Severity:** High (affects all comparisons)

**Mitigation Strategy:**
1. **Prevention:** Pin exact bigcode-harness version and commit hash; use LiveCodeBench 2024-Q4 snapshot to avoid contamination; run baseline validation on known models (e.g., DeepSeek-Coder-7B-Instruct published benchmark numbers).
2. **Detection:** Cross-check HumanEval/MBPP results against published DeepSeek-Coder-7B numbers for sanity.
3. **Response:** SCOPE — if harness issues detected, fall back to custom evaluation script for HumanEval/MBPP only (well-understood benchmarks); report LiveCodeBench as secondary only.

**Early Warning Indicators:** SFT pass@1 on HumanEval deviates >15% from expected based on base model capability.

---

**Risk R4: SFT Ceiling at HumanEval Inflates Δ Ratio (A4 Violated)**

**Source Assumption:** A4 — SFT on APPS achieves <90% pass@1 on HumanEval (adequate headroom for RLEF improvement).

**Description:** If APPS SFT is already saturated at HumanEval (≥90% pass@1), Δ_HumanEval is artificially compressed, inflating the Δ ratio (making the difficulty-scaling effect look larger than it is).

**Affected Hypotheses:** H-E1 (Δ ratio calculation), H-M4 (monotonicity)

**Severity:** High (threatens validity of Δ ratio metric)

**Mitigation Strategy:**
1. **Prevention:** SFT ceiling check is Step 1 of H-E1 verification protocol — run zero-shot before any fine-tuning.
2. **Detection:** If SFT pass@1 at HumanEval ≥ 90%, switch primary model to DeepSeek-Coder-1.3B.
3. **Response:** SCOPE — use 1.3B as primary model for all experiments; 7B becomes secondary/ablation.

**Early Warning Indicators:** DeepSeek-Coder-7B zero-shot on HumanEval >80% (close to ceiling concern).

---

**Risk R5: APPS-LiveCodeBench Domain Mismatch (A5 Violated)**

**Source Assumption:** A5 — APPS training data is representative of LiveCodeBench problem types.

**Description:** If APPS and LiveCodeBench draw from systematically different algorithmic domains, the RLEF vs SFT gap at LiveCodeBench may reflect domain transfer difficulty rather than difficulty-scaling mechanism.

**Affected Hypotheses:** H-E1, H-M4 (cross-benchmark comparisons)

**Severity:** Medium (confound, not invalidation)

**Mitigation Strategy:**
1. **Prevention:** Report APPS vs LiveCodeBench problem-type distribution as supplementary analysis (Prof. Rex's recommendation from Phase 2A).
2. **Detection:** If APPS covers <30% of LiveCodeBench algorithmic categories, domain mismatch is a concern.
3. **Response:** EXPLORE — report distribution analysis and discuss as limitation; gap finding may still hold under mismatch but mechanism explanation is nuanced.

**Early Warning Indicators:** LiveCodeBench problems cluster in categories rarely seen in APPS training data.

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: APPS covers hard difficulty | A1 | H-E1, H-M1, H-M4 | Critical |
| R2: RLEF signal void at hard | A2 | H-M2, H-M3 | High |
| R3: Harness measurement error | A3 | All (H-E1 → H-M4) | High |
| R4: SFT ceiling at HumanEval | A4 | H-E1, H-M4 | High |
| R5: APPS-LiveCodeBench mismatch | A5 | H-E1, H-M4 | Medium |

**Risk Summary:** 1 Critical, 3 High, 1 Medium. Primary mitigations (SFT ceiling check, TRL monitoring callback, harness pinning) are zero/low-cost additions to the main experiment.

---

## 5. Execution Plan

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
    MUST_WORK: Δ_LiveCodeBench / Δ_HumanEval ≥ 1.5
         │
         ▼
[Level 1 - First Mechanism]
    H-M1 ← H-E1
    MUST_WORK: SFT pass@1 on LiveCodeBench-Hard < 60%
         │
         ▼
[Level 2 - Second Mechanism]
    H-M2 ← H-M1
    SHOULD_WORK: Non-zero reward fraction > 10% on APPS-Hard
         │
         ▼
[Level 3 - Third Mechanism]
    H-M3 ← H-M2
    SHOULD_WORK: Δ_Fraction > Δ_Binary at LiveCodeBench-Hard
         │
         ▼
[Level 4 - Fourth Mechanism]
    H-M4 ← H-M3
    SHOULD_WORK: Monotonic Δ trend across 5 difficulty levels

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis   │ W1-2    │ W3-4    │ W5      │ W6      │
───────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1             │ ████████│         │         │         │
  [Gate 1: MUST]   │       ◆ │         │         │         │
───────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1 (SFT void)  │         │ ████████│         │         │
  [Gate 2: MUST]   │         │       ◆ │         │         │
  H-M2 (non-zero)  │         │         │ ████    │         │
  H-M3 (frac>bin)  │         │         │     ████│         │
  H-M4 (monotonic) │         │         │         │ ████████│
  [Gate 3: SHOULD] │         │         │         │       ◆ │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

**Note:** H-M1 uses SFT model from H-E1 (no additional training). H-M2 uses TRL callback from H-E1 RLEF training (zero additional cost). H-M3 adds RLEF-Binary training. H-M4 adds 1.3B runs (parallelizable with H-M3).

### 5.4 Critical Path Analysis

```
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 6 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4, parallelizable with H-M3 for 1.3B) = 6 weeks

Slack Available: 0 weeks (all sequential — each depends on prior)

Note on Efficiency:
- H-M1 uses SFT model from H-E1: no additional training
- H-M2 uses monitoring callback from H-E1 RLEF run: zero additional compute
- H-M3 adds RLEF-Binary: 1 additional training run
- H-M4 adds 1.3B sanity check + monotonicity analysis: parallelizable with H-M3
```

### 5.5 Resource Summary

```
Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (none required)

Training Runs Required:
1. SFT on APPS (DeepSeek-Coder-7B) — used for H-E1, H-M1
2. RLEF-Fraction on APPS (DeepSeek-Coder-7B) — with P3 monitoring callback; used for H-E1, H-M2
3. RLEF-Binary on APPS (DeepSeek-Coder-7B) — used for H-M3
4. SFT on APPS (DeepSeek-Coder-1.3B) — used for H-M4
5. RLEF-Fraction on APPS (DeepSeek-Coder-1.3B) — used for H-M4

Evaluation Runs: 5 models × 5 benchmarks = 25 bigcode-harness evaluations
Phases: 2 (Foundation, Mechanisms)
Critical Path: 6 weeks
Execution Mode: Sequential chain (with some parallelization in Phase 2)
```

### 5.6 Execution Order

```
Step 1: SFT ceiling check — run DeepSeek-Coder-7B zero-shot on HumanEval
Step 2: [If SFT ceiling ≥90%] switch primary model to DeepSeek-Coder-1.3B
Step 3: Fine-tune SFT baseline on APPS (Week 1-2)
Step 4: Fine-tune RLEF-Fraction on APPS with P3 monitoring callback (Week 1-2, parallel with Step 3)
Step 5: Evaluate H-E1 — all benchmarks for SFT and RLEF-Fraction (end Week 2)
Step 6: Gate 1 decision — if H-E1 MUST_WORK fails, STOP and reassess
Step 7: Evaluate H-M1 — SFT on LiveCodeBench-Hard (uses Step 3 model) (Week 3)
Step 8: Gate 2 decision — if H-M1 MUST_WORK fails, EXPLORE and refine framing
Step 9: Analyze H-M2 — P3 monitoring data from Step 4 (Week 3, zero additional cost)
Step 10: Fine-tune RLEF-Binary on APPS + evaluate H-M3 (Week 4-5)
Step 11: Fine-tune 1.3B models + evaluate H-M4 monotonicity analysis (Week 5-6)
Step 12: Gate 3 decision — SHOULD_WORK gates; failures narrow scope but don't block
Step 13: Verification complete — proceed to Phase 2C experiment design for each hypothesis
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Under controlled conditions, RLEF with fraction-of-tests-passing reward achieves progressively larger advantage over SFT as benchmark difficulty increases (HumanEval → LiveCodeBench-Hard), because execution feedback enables non-zero gradient from partially-correct solutions where SFT's all-or-nothing objective receives zero gradient.

**Supporting Evidence:**
1. Causal mechanism: 4-step chain from APPS coverage sparsity at hard difficulty → SFT signal void → RLEF partial-success gradient → widening performance gap
2. Literature: RLEF-2024 (Gehring et al.) reports partial > binary reward more at hard problems; RLTF confirms coverage reward > binary; multiple studies confirm RLEF > SFT on easy benchmarks
3. Testable predictions: P1 (Δ ratio ≥ 1.5), P2 (fraction > binary at hard), P3 (non-zero reward fraction > 10% at hard), P4 (1.3B sanity check)

**Strengths:**
- Clear 4-step mechanistic chain with independent falsifiers at each step
- P3 mechanistic proxy test requires zero additional experimental cost (TRL callback)
- Established that RLEF > SFT at easy benchmarks (BUILD_ON) — only the difficulty-scaling claim is new
- All controls operationalized (model, data, eval protocol, compute)

**Expected Outcomes:**
- Primary (P1): Δ_LiveCodeBench / Δ_HumanEval ≥ 1.5, p < 0.05
- Secondary (P2): Δ_Fraction > Δ_Binary at hard; Δ_Fraction ≈ Δ_Binary at easy
- Mechanism (P3): Non-zero reward fraction positively correlates with APPS difficulty

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in Δ(RLEF, SFT) across benchmark difficulty levels; Δ_LiveCodeBench ≤ 1.5 × Δ_HumanEval.

**Counter-Arguments:**
1. APPS coverage: APPS was designed to span easy-to-competition difficulty; it may contain adequate correct solutions at competition level, negating the SFT signal void premise (A1)
2. Binary reward sufficiency: Prior work (RLTF) shows binary reward improvements; fraction reward may not add measurable benefit beyond binary at hard difficulty (challenging H-M3)
3. Evaluation confound: LiveCodeBench problem types may differ from APPS training types, meaning the gap reflects domain mismatch rather than difficulty-scaling mechanism (A5)

**Potential Failure Points:**
- R1 (Critical): APPS covers hard difficulty → gap remains constant, not widening
- R2 (High): RLEF has near-zero non-zero reward at hard → both SFT and RLEF have signal void
- R4 (High): SFT saturates at HumanEval → Δ_HumanEval artificially compressed → inflated Δ ratio

**Conditions Under Which H0 Would Be Supported:**
- If Δ_LiveCodeBench / Δ_HumanEval < 1.5 (not significantly different from 1.0)
- If non-zero reward fraction is uniform across APPS difficulty buckets (P3 fails)
- If SFT achieves >60% pass@1 on LiveCodeBench-Hard (H-M1 fails, A1 violated)

### 6.3 Synthesis

**Balanced Assessment:** The hypothesis H-DifficultyScaledRLEF-v1 presents a testable claim with a clear causal mechanism and pre-specified quantitative falsifiers. The null hypothesis raises valid empirical concerns — specifically whether APPS training data actually creates a signal void at hard difficulty, and whether the partial-success gradient is mechanistically necessary beyond binary reward. The verification plan directly addresses this dialectic through sequential hypothesis testing with gate conditions.

**Resolution Path:**
1. **Foundation verification (H-E1):** Establishes existence of difficulty-scaling phenomenon before attributing mechanism — prevents premature mechanism testing.
2. **Sequential mechanism testing (H-M1 → H-M4):** Tests each causal step independently with its own falsifier; failure at any step provides diagnostic information without invalidating the entire study.
3. **Gate conditions:** MUST_WORK gates at H-E1 and H-M1 allow early detection of H0 support; SHOULD_WORK gates at H-M2/3/4 allow nuanced findings without full invalidation.

**Conditions for Thesis Support:**
- H-E1 MUST_WORK gate passes (Δ ratio ≥ 1.5)
- H-M1 MUST_WORK gate passes (SFT void confirmed)
- At least directional support for H-M2/3 (partial-success mechanism active)

**Conditions for Antithesis Support:**
- H-E1 fails (gap does not widen with difficulty; H0 supported directly)
- H-M1 fails (SFT does not have signal void at hard difficulty; mechanism premise wrong)
- P3 monitoring shows uniform non-zero reward fraction (H-M2 fails; RLEF also void)

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 + H-M1-4 all pass → Complete causal chain validated → Strong thesis support
2. **Partial Support:** H-E1 passes; some H-M fail → Phenomenon confirmed but mechanism partially wrong → Refined claim with empirically-tested limitations
3. **Mechanism Alternative:** H-E1 passes; H-M1 fails (SFT not void) → Gap exists but not via signal void mechanism → Alternative mechanism investigation
4. **No Support:** H-E1 fails → Antithesis supported; difficulty-scaling relationship does not hold in controlled conditions

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Difficulty-scaling gap exists | Gap may be constant across difficulty | H-E1 test (Δ ratio ≥ 1.5, pre-specified) |
| Mechanism Step 1 | SFT void at hard difficulty | APPS may cover hard difficulty adequately | H-M1 test (SFT pass@1 < 60%) |
| Mechanism Step 2 | RLEF has non-zero signal at hard | RLEF may also have signal void at hard | H-M2 test (P3 monitoring, >10% non-zero) |
| Mechanism Step 3 | Fraction > binary at hard | Binary reward may be sufficient | H-M3 test (Δ_Fraction > Δ_Binary) |
| Scope | Pattern holds across scales | 7B-specific effect | H-M4 test (1.3B sanity check) |

**Overall Robustness Score:** High
- Pre-specified quantitative thresholds (1.5× ratio, 10% non-zero fraction)
- Bootstrap CIs + Bonferroni correction for multiple comparisons
- Mechanistic proxy test (P3) at zero additional cost provides independent evidence
- 1.3B sanity check reduces single-model confound

**Confidence in Verification Plan:** 0.80 (from Phase 2A)

---

## 7. Executive Summary & Appendices

### 7.1 Executive Summary

**Main Hypothesis:** H-DifficultyScaledRLEF-v1 (Confidence: 0.80)
- RLEF with fraction-of-tests reward achieves progressively larger advantage over SFT as benchmark difficulty increases (HumanEval → LiveCodeBench-Hard), due to partial-success gradient signal

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue complete; 40% scope reduction applied)
- Sub-Hypotheses: 5 total — H-E1 (1 existence) + H-M1-4 (4 mechanism steps)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 MUST_WORK (H-E1, H-M1) + 3 SHOULD_WORK (H-M2/3/4)

**Risk Assessment:** High (1 Critical, 3 High, 1 Medium risk)
- Primary concerns: APPS coverage at hard difficulty (R1/Critical); RLEF signal void at hard (R2/High)
- All mitigations are low/zero-cost additions to main experiment

**Immediate Action:** SFT ceiling check → then begin H-E1 training (parallel SFT + RLEF-Fraction with P3 monitoring callback)

### 7.2 Conclusions

**Key Achievements:**
- 5 hypotheses across 2 phases covering complete causal chain (existence → mechanism steps 1-4)
- H0 directly tested: Δ_LiveCodeBench ≤ 1.5 × Δ_HumanEval (falsified by H-E1)
- P3 mechanistic proxy test embedded at zero additional experimental cost

**Verification Execution Order:**

Phase 1 — Foundation (2 weeks):
- H-E1: RLEF-Fraction achieves Δ ratio ≥ 1.5 across difficulty levels
- Gate 1: MUST PASS — if not, STOP and reassess

Phase 2 — Core Mechanisms (4 weeks):
- H-M1: SFT signal void confirmed at LiveCodeBench-Hard — Gate 2: MUST PASS
- H-M2: RLEF non-zero reward fraction > 10% on APPS-Hard
- H-M3: RLEF-Fraction > RLEF-Binary at LiveCodeBench-Hard
- H-M4: Monotonic gap widening across 5 difficulty levels + 1.3B sanity check

**Critical Decision Points:**

1. Gate 1 (Foundation — H-E1): MUST_WORK
   - FAIL → STOP; difficulty-scaling phenomenon not demonstrated; H0 supported; route to Phase 0 for hypothesis redesign
   - PASS → Proceed to Phase 2 mechanism testing

2. Gate 2 (First Mechanism — H-M1): MUST_WORK
   - CRITICAL FAIL (SFT pass@1 ≥ 60%) → EXPLORE signal void assumption; may continue with refined framing
   - PASS → Proceed to H-M2/3/4 (SHOULD_WORK, non-blocking)

3. Gates 3-5 (H-M2/3/4): SHOULD_WORK
   - Failures narrow scope and provide nuanced findings; do not block Phase 5

**Open Questions (from Phase 2A):**
- Does difficulty-scaling hold at 13B or 34B model scale?
- Does RLEF trained on APPS transfer to SWE-bench (zero-shot)?
- What is the optimal RLEF training curriculum (easy-first, hard-first, mixed)?
- How does APPS test quality variability (1-20 tests/problem) affect reward signal?

**Recommendations:**

1. Immediate Actions:
   - SFT ceiling check (zero-shot HumanEval before fine-tuning)
   - Add TRL monitoring callback for P3 non-zero reward fraction tracking
   - Pre-register P1-P4 predictions to prevent p-hacking (Prof. Rex recommendation)

2. Resource Allocation:
   - 5 training runs (3 × 7B + 2 × 1.3B); 25 bigcode-harness evaluations
   - 1.3B runs parallelizable with 7B runs to compress total timeline

3. Failure Management:
   - Document all gate results and non-zero reward monitoring data
   - H-M2 failure (RLEF signal void) is a publishable null result with mechanistic value

### 7.3 Appendices

**A. Phase 2A Reference:**
- Source: `docs/youra_research/03_refinement.yaml` (ID: H-DifficultyScaledRLEF-v1)
- Schema version: 10.0.0; VALIDATED status; all 6 convergence criteria met at Exchange 12

**B. MCP Tool Usage Summary:**
- Total MCP calls: 0 (no_MCP session — LLM scientific method reasoning used)
- Fallback: Direct causal chain analysis from Phase 2A 03_refinement.yaml

**C. Scope Reduction Details:**
- BUILD_ON (skipped): 2 claims (RLEF > SFT established; partial > binary established)
- PROVE_NEW (tested): 3 claims → mapped to H-E1 + H-M1/M2/M3/M4
- Efficiency gain: 40% of total claims are pre-established background

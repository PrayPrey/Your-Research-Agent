# Verification Plan: Difficulty-Stratified Calibration Fingerprint of LLM Code Verifiers via P(True)

**Date:** 2026-03-18
**Hypothesis ID:** H-CalibDiff-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under k=5 self-contained difficulty stratification on HumanEval+/MBPP+ (542 problems),
if LLMs predict code correctness via P(True) logprob elicitation stratified by
difficulty tiers bootstrapped from their own pass@1 distribution (hard = pass@1 = 0.0,
easy = pass@1 ≥ 0.6),
then Expected Calibration Error differs systematically between difficulty tiers
(ΔECE = ECE(hard) - ECE(easy) ≠ 0, with primary prediction ΔECE > 0),
because LLM confidence signals derived from pre-training distributions do not
adequately reflect task-specific difficulty structure, leading to greater calibration
failure on problems where the model rarely generates correct solutions.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in Expected Calibration Error between hard-tier and
easy-tier problems (ΔECE ≤ 0 or |ΔECE| < 0.03 across ≥2/3 model families after
controlling for base-rate accuracy differences), indicating that LLM P(True) calibration
is uniform across difficulty levels or that apparent differences are fully explained by
base-rate accuracy coupling.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval+ and MBPP+ (EvalPlus) (standard) | Augmented test suite (~760 tests/problem) provides reliable correctness oracle. 542 problems total (164 + 378) provides sufficient n for ECE per tier. Already validated in Run 3. |
| **Model** | Llama3-8B, CodeLlama-7B, DeepSeek-Coder-6.7B | Three families span general-purpose to code-specialized spectrum. Previously validated in Run 3 with successful P(True) elicitation. |

**Dataset Details:**
- Source: Liu et al. 2023 (EvalPlus); https://github.com/evalplus/evalplus
- Path: evalplus Python package (install via pip)

**Model Details:**
- Type: HuggingFace decoder-only LLMs
- Source: NousResearch/Meta-Llama-3-8B, codellama/CodeLlama-7b-hf, deepseek-ai/deepseek-coder-6.7b-base

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| P(True) for factual Q&A (Kadavath et al. 2022) | ECE ~0.05 for 52B model on HumanEval (high base-rate regime); calibration scales with model size | Various factual Q&A; HumanEval (code, high accuracy only) |
| ECE for vision models (Guo et al. 2017) | Modern NNs: ECE 4-13% uncalibrated; temperature scaling reduces to <1% | CIFAR-10/100, ImageNet, document classification |
| EvalPlus pass@k measurement (Liu et al. 2023) | Pass rates drop 28.9% under augmented tests; even canonical solutions fail >10% | HumanEval+, MBPP+ |

**Best baseline ECE from Run 3:** llama3-8b=0.4895, codellama-7b=0.5218, deepseek-coder=0.1358 (non-stratified)

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | k=5 solutions provide sufficient pass@1 estimate for tier stratification despite high binomial variance | With 542 problems and 3 models, hard tier expected ~100-150 problems per model; sufficient for ECE with n≥20 | Tier membership dominated by sampling noise; ΔECE unreliable. Mitigation: label as pilot, use 6-point curve |
| A2 | EvalPlus augmented tests provide reliable ground-truth correctness labels | Liu et al. 2023: ~760 tests per problem; Run 3 validated EvalPlus API | ECE biased upward due to label noise in hard tiers. Mitigation: compare standard vs. augmented |
| A3 | P(True) logprob captures genuine confidence, not surface features | Kadavath et al. 2022 showed P(True) correlates with correctness in factual Q&A | ΔECE confounds calibration quality with prompt sensitivity. Mitigation: partial correlation for solution length |
| A4 | Self-contained difficulty (model-specific pass@1) is a meaningful proxy for intrinsic problem hardness | Model-specific difficulty captures the model's own competence landscape; consistent across k trials | Difficulty tiers measure calibration consistency, not intrinsic difficulty — still valid but reframes contribution |
| A5 | Three-model comparison provides architectural signal (general vs. code-adapted vs. code-specialized) | DeepSeek-Coder trained specifically on code; CodeLlama fine-tuned from Llama; Llama3 general-purpose | Architecture differences confound code-specialization claim. Mitigation: label as exploratory |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First empirical calibration-difficulty fingerprint for LLM code verifiers — measures whether P(True) confidence degrades with difficulty using self-contained bootstrap.

**Key Innovation:** Self-contained pass@1 bootstrap difficulty stratification eliminates all external CSV/leaderboard dependencies. Produces model-specific difficulty tiers reflecting each model's own competence landscape.

**Differentiation from Prior Work:**
- Kadavath 2022: P(True) for factual Q&A only — no difficulty stratification, no code tasks
- Guo 2017: ECE for vision models — no LLMs, no difficulty stratification, no code tasks
- Liu 2023 EvalPlus: Measures pass rates, not calibration — no P(True), no ECE
- **This work:** First intersection of P(True) + ECE + EvalPlus + self-contained difficulty bootstrap

**Scope Reduction:** 57% of claims are BUILD_ON (pre-validated). Only ΔECE measurement, calibration-difficulty fingerprint, and temperature scaling probe require new verification.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Gate | Prerequisites | Status |
|----|------|-------------------|------|---------------|--------|
| H-E1 | EXISTENCE | k=5 bootstrap yields n≥20 per tier per model on HumanEval+/MBPP+ | MUST_WORK | None | READY |
| H-M1 | MECHANISM | k=5 solution generation + EvalPlus oracle produces valid pass@1 values | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | Pass@1-based difficulty stratification yields model-specific tiers reflecting competence | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | P(True) logprob elicitation produces calibrated confidence signals for code verification | MUST_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | ΔECE = ECE(hard) - ECE(easy) > 0 in ≥2/3 model families; persists after global T scaling | MUST_WORK | H-M3 | NOT_STARTED |

**Total: 5 hypotheses** (H-E: 1, H-M: 4, H-C: 0)

---

### 2.2 Hypothesis Specifications

---
**H-E1: Tier Sample Size Viability**

**Type:** EXISTENCE
**Statement:** Under k=5 self-contained solution generation on HumanEval+/MBPP+ (542 problems), if we stratify problems by pass@1 per model (hard = 0/5 correct, easy = ≥3/5 correct), then each tier will contain n≥20 problems per model per benchmark, enabling reliable ECE computation with M=15 bins.

**Rationale:** Reliable ECE computation requires sufficient samples per tier. The n≥20 threshold per (model, benchmark) combination ensures each calibration bin has meaningful population. This is the foundational check that gates all subsequent mechanism hypotheses.

**Variables:**
- IV: Difficulty tier assignment (hard/easy by pass@1 from k=5 solutions)
- DV: Tier sample size n per (model, benchmark) pair; threshold n≥20
- CV: 3 model families fixed; 542 total problems; EvalPlus augmented oracle

**Verification Protocol:**
1. Reuse Run 3 solutions (k=5 per problem, 3 models) or regenerate with fixed seed.
2. Run EvalPlus check_correctness for each (problem, solution) pair.
3. Compute pass@1 = correct_count/5 per (problem, model).
4. Assign tiers: hard = pass@1=0.0, easy = pass@1≥0.6, medium = excluded.
5. Count n_hard and n_easy per (model, benchmark); verify n≥20 for each.

**Success Criteria:**
- Primary: n_hard ≥ 20 AND n_easy ≥ 20 for ≥2/3 models on ≥1 benchmark
- Secondary: 6-point pass@1 distribution reported (0.0–1.0 histogram per model)

**Gate:**
- Type: MUST_WORK
- If Fail: Relax hard threshold to pass@1≤0.2; if still underpowered, PIVOT to pooled (HumanEval+ + MBPP+) analysis or label as underpowered pilot

**Dependencies:** None (foundation)
**Source:** Phase 2A Section 5 (sh1_existence), Prediction P1 (viability precondition)

---
**H-M1: Solution Generation + Oracle Validation**

**Type:** MECHANISM (Step 1 of 4)
**Statement:** Under EvalPlus augmented test execution, if k=5 solutions are generated per problem per model using temperature sampling and evaluated via EvalPlus check_correctness, then pass@1 values are reliably computed with ≥95% problem coverage (≤5% generation failures), because the Run 3 infrastructure is validated and reusable with minimal modifications.

**Rationale:** The solution generation pipeline is the entry point to the entire experiment. Run 3 confirmed this works for all 542 problems × 3 models. H-M1 re-validates the pipeline with the new self-contained bootstrap focus and confirms no regression. Without this, tier stratification in H-M2 is impossible.

**Variables:**
- IV: k=5 solution generation (temperature sampling, 3 models, 542 problems)
- DV: Problem coverage rate (fraction with valid k=5 solutions); pass@1 values in {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}
- CV: Fixed random seed; EvalPlus augmented tests only; same 3 model checkpoints as Run 3

**Verification Protocol:**
1. Load existing Run 3 solution files from h-e1/code/src/h_e1/ if available.
2. If solutions missing, regenerate with fixed seed (temperature=0.8, k=5).
3. Run EvalPlus check_correctness for each (problem, solution) pair.
4. Compute pass@1 per (problem, model); verify 6-point distribution.
5. Report coverage rate: fraction of problems with valid evaluations.

**Success Criteria:**
- Primary: Coverage ≥ 95% (≤27 problems with generation failures across 542)
- Secondary: pass@1 distribution non-trivial (not all 0.0 or all 1.0)

**Gate:**
- Type: MUST_WORK
- If Fail: Debug EvalPlus API compatibility; fallback to vanilla HumanEval/MBPP oracle with note

**Dependencies:** H-E1 (confirms tier viability)
**Source:** Phase 2A Causal Step 1

---
**H-M2: Difficulty Stratification Quality**

**Type:** MECHANISM (Step 2 of 4)
**Statement:** Under model-specific pass@1 stratification from H-M1, if problems are assigned to hard (pass@1=0.0) and easy (pass@1≥0.6) tiers per model, then tier assignments reflect genuine competence differences (Jaccard similarity of hard-tier problem sets across models > 0.3), because problems that are structurally hard tend to be hard across different architectures.

**Rationale:** Confirming cross-model tier overlap validates that difficulty tiers capture intrinsic problem properties rather than pure model idiosyncrasy. A Jaccard > 0.3 is a minimal signal that the self-contained bootstrap produces meaningful stratification beyond random assignment.

**Variables:**
- IV: Model-specific pass@1 tier assignments per (problem, model)
- DV: Jaccard similarity of hard-tier problem sets between model pairs; 6-point histogram shape
- CV: EvalPlus oracle for all evaluations; hard threshold fixed at pass@1=0.0

**Verification Protocol:**
1. Compute hard-tier problem sets per model from H-M1 pass@1 values.
2. Calculate Jaccard similarity for all 3 model pairs (Llama3/CodeLlama, Llama3/DeepSeek, CodeLlama/DeepSeek).
3. Report 6-point pass@1 histogram (0.0–1.0) for each model.
4. Document cross-model overlap statistics.
5. Label tier assignments: model-specific (primary) vs. consensus-hard (exploratory).

**Success Criteria:**
- Primary: At least 1 of 3 model pairs has Jaccard > 0.3 for hard-tier overlap
- Secondary: Bimodal or skewed pass@1 distribution (not uniform)

**Gate:**
- Type: SHOULD_WORK
- If Fail: Proceed with model-specific tiers only; reframe contribution as "competence-boundary calibration" rather than "difficulty-conditioned calibration"

**Dependencies:** H-M1
**Source:** Phase 2A Causal Step 2

---
**H-M3: P(True) Logprob Elicitation**

**Type:** MECHANISM (Step 3 of 4)
**Statement:** Under zero-shot P(True) prompting for each (problem, solution) pair, if logprob(True) and logprob(False) are extracted from the model's output distribution and normalized as confidence c = logprob(True)/(logprob(True)+logprob(False)), then confidence values are non-degenerate (not all ≈0.5 or all ≈1.0) and vary meaningfully across problems and models, because Run 3 validated P(True) values of 0.57–0.91 for all 3 models.

**Rationale:** P(True) elicitation is the core confidence mechanism. Degenerate outputs (all near 0.5 = pure uncertainty, all near 1.0 = overconfidence) would render ECE computation uninformative. Run 3 confirmed non-degenerate values, but this needs verification with the updated prompting approach for code verification specifically.

**Variables:**
- IV: P(True) prompt format ("Is this code correct? True/False" appended to problem+solution)
- DV: Distribution of c values across (problem, solution) pairs; standard deviation of c per model
- CV: Zero-shot format only; same 3 models; logprob extraction via output_scores=True

**Verification Protocol:**
1. For each (problem, solution) pair in hard+easy tiers, construct P(True) prompt.
2. Run model.generate(output_scores=True) to extract logprob(True) and logprob(False).
3. Compute c = softmax([logprob(True), logprob(False)])[0].
4. Report distribution statistics: mean, std, min, max per model.
5. Verify std(c) > 0.05 (non-degenerate distribution).

**Success Criteria:**
- Primary: std(c) > 0.05 for all 3 models (non-degenerate confidence signals)
- Secondary: c values span range 0.2–0.9 (not collapsing to extremes)

**Gate:**
- Type: MUST_WORK
- If Fail: Try alternative prompt format ("Does this solution pass all tests?"); if still degenerate, report as mechanism failure and PIVOT

**Dependencies:** H-M2
**Source:** Phase 2A Causal Step 3

---
**H-M4: ΔECE Measurement and Temperature Scaling Probe**

**Type:** MECHANISM (Step 4 of 4)
**Statement:** Under M=15-bin ECE computation per difficulty tier using P(True) confidence from H-M3, if ΔECE = ECE(hard) - ECE(easy) is measured with 1000-sample bootstrap 95% CIs and compared to a tier-specific null baseline (constant confidence = tier accuracy), then ΔECE > 0 (with CI excluding zero) in ≥2/3 model families AND ΔECE ≥ 0.03 persists after global temperature scaling (T fitted on 20% holdout), because LLM confidence from pre-training does not align with difficulty structure and global temperature scaling cannot correct difficulty-conditioned miscalibration.

**Rationale:** This is the core measurement contribution. ΔECE > 0 confirms difficulty-conditioned calibration failure. Persistence after global T scaling confirms structural (not globally correctable) miscalibration. Both the null baseline comparison and temperature scaling probe are pre-registered controls that distinguish structural from spurious ΔECE.

**Variables:**
- IV: Difficulty tier (hard vs. easy) per model; global temperature T (pre/post scaling)
- DV: ECE per tier (M=15 bins); ΔECE = ECE(hard) - ECE(easy); excess ECE above null baseline; post-scaling ΔECE
- CV: M=15 fixed (sensitivity over {10,15,20}); 20% holdout for T fitting; zero-shot P(True) prompt

**Verification Protocol:**
1. Compute ECE(hard) and ECE(easy) per model with M=15 bins and bootstrap 95% CIs.
2. Compute ΔECE and check if CI excludes zero; count families with ΔECE > 0.
3. Compute tier-null ECE (constant confidence = tier accuracy); compute excess ECE per tier.
4. Fit global T on 20% holdout (NLL minimization); recompute tier-stratified ECE post-scaling.
5. Run M-sensitivity analysis over {10, 15, 20}; report ΔECE stability.

**Success Criteria:**
- Primary: ΔECE ≥ 0.03 in ≥2/3 model families with 95% CI excluding zero (P1)
- Secondary: Excess ECE larger in hard tier than easy tier p<0.05 bootstrap (P2); ΔECE persists post-T-scaling (P3)

**Gate:**
- Type: MUST_WORK
- If Fail: ΔECE ≤ 0 = publish as null result (uniform calibration); ΔECE collapses after T = publish as "globally correctable" finding

**Dependencies:** H-M3
**Source:** Phase 2A Causal Step 4, Predictions P1-P3

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | n≥20 per tier in ≥2/3 models | Relax threshold; if still underpowered: STOP |
| H-M1 | MUST_WORK | Coverage ≥95% with non-trivial pass@1 | Debug EvalPlus; fallback vanilla oracle |
| H-M2 | SHOULD_WORK | Jaccard>0.3 for ≥1 model pair | Proceed with model-specific framing |
| H-M3 | MUST_WORK | std(c)>0.05 for all 3 models | Try alternative prompt; if degenerate: PIVOT |
| H-M4 | MUST_WORK | ΔECE≥0.03, CI excludes zero in ≥2/3 families | Publish null/negative result |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1 → H-M2 → H-M3 → H-M4 | 5 weeks |
| **Total** | **5 hypotheses** | **7 weeks** |

**Total Duration:** 7 weeks (formula: 2 + 4 + 0 condition weeks)

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Tier Underpowering** (Source: A1)
- Description: k=5 granularity causes too few problems in hard or easy tier (n<20), making ECE unreliable
- Severity: High | Likelihood: Medium
- Affected Hypotheses: H-E1, H-M4
- Mitigation:
  1. Prevention: Report 6-point histogram early; verify tier sizes before H-M4
  2. Detection: Check n_hard and n_easy immediately after H-E1 execution
  3. Response: SCOPE — relax hard threshold to pass@1≤0.2; pool benchmarks; label as pilot

**Risk R2: Oracle Label Noise** (Source: A2)
- Description: EvalPlus augmented tests miscategorize edge-case solutions, inflating ECE
- Severity: Medium | Likelihood: Low
- Affected Hypotheses: H-M3, H-M4
- Mitigation:
  1. Prevention: Use EvalPlus augmented (not vanilla) throughout
  2. Detection: Compare ECE under vanilla vs. augmented test suites
  3. Response: SCOPE — report label noise sensitivity analysis

**Risk R3: P(True) Prompt Sensitivity** (Source: A3)
- Description: P(True) logprob captures prompt format artifacts rather than genuine confidence
- Severity: High | Likelihood: Low
- Affected Hypotheses: H-M3, H-M4
- Mitigation:
  1. Prevention: Fix zero-shot prompt format; use same format for all models
  2. Detection: Check std(c) > 0.05 in H-M3; if degenerate, flag
  3. Response: PIVOT — try 2-3 alternative prompt formats; partial correlation for solution length

**Risk R4: Model-Idiosyncratic Difficulty** (Source: A4)
- Description: Pass@1-based difficulty tiers reflect model quirks rather than intrinsic problem hardness
- Severity: Low | Likelihood: Medium
- Affected Hypotheses: H-M2
- Mitigation:
  1. Prevention: Report cross-model Jaccard similarity in H-M2
  2. Detection: If Jaccard < 0.3 across all pairs, tiers are model-specific
  3. Response: REFRAME — contribution becomes "calibration at model competence boundary" (still valid)

**Risk R5: Architecture Confound** (Source: A5)
- Description: P4 architecture comparison is underpowered (N=1 per category), overstates specialization effect
- Severity: Low | Likelihood: High
- Affected Hypotheses: H-M4 (exploratory P4 only)
- Mitigation:
  1. Prevention: Label P4 as exploratory throughout
  2. Detection: N=1 per architecture = confirmed underpowered
  3. Response: SCOPE — report P4 as "exploratory trend, not confirmatory result"

### 4.2 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Tier underpowering (n<20) | A1 | High | H-E1, H-M4 | Relax threshold; pool benchmarks |
| R2 | Oracle label noise | A2 | Medium | H-M3, H-M4 | Sensitivity analysis vanilla vs. augmented |
| R3 | P(True) prompt sensitivity | A3 | High | H-M3, H-M4 | Alternative formats; correlation control |
| R4 | Model-idiosyncratic difficulty | A4 | Low | H-M2 | Reframe as competence-boundary calibration |
| R5 | Architecture confound | A5 | Low | H-M4 (P4) | Label exploratory; do not overstate |

**Critical Risks:** 0 | **High:** 2 (R1, R3) | **Medium:** 1 (R2) | **Low:** 2 (R4, R5)

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (EXISTENCE - no dependencies)
    Gate: MUST_WORK
         │
         ▼
[Level 1 - Mechanism: Solution Generation]
    H-M1 ← H-E1
    Gate: MUST_WORK
         │
         ▼
[Level 2 - Mechanism: Difficulty Stratification]
    H-M2 ← H-M1
    Gate: SHOULD_WORK
         │
         ▼
[Level 3 - Mechanism: P(True) Elicitation]
    H-M3 ← H-M2
    Gate: MUST_WORK
         │
         ▼
[Level 4 - Mechanism: ΔECE Measurement]
    H-M4 ← H-M3
    Gate: MUST_WORK

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
No parallelization (fully sequential chain)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|------------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | MUST_WORK |
| 4 | H-M4 | H-M3 | MUST_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis   │ W1-2    │ W3-4    │ W5      │ W6      │ W7
───────────────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 1: Foundation
  H-E1             │ ████████│         │         │         │
  [Gate 1]         │       ◆ │         │         │         │
───────────────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 2: Mechanisms
  H-M1             │         │ ████████│         │         │
  H-M2             │         │         │ ████    │         │
  H-M3             │         │         │         │ ████    │
  H-M4             │         │         │         │         │ ████
  [Gate 2]         │         │         │         │         │    ◆
───────────────────┼─────────┼─────────┼─────────┼─────────┼─────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 7 weeks
  Formula: 2 (H-E1) + 4 (H-M1–M4) + 0 (H-C) = 7 weeks
Slack Available: 0 weeks (fully sequential)
Bottleneck: H-M4 (core measurement; largest computational load)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0
Verification Phases: 2
  1. Foundation (H-E1): 2 weeks
  2. Mechanisms (H-M1–M4): 5 weeks
Total Duration: 7 weeks
Critical Path Length: 7 weeks
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Execution Order:**
- Step 1: Execute H-E1 (Foundation) — Week 1-2
- Step 2: Evaluate Gate 1 → If pass, proceed
- Step 3: Execute H-M1 (Solution generation + oracle) — Week 3-4
- Step 4: Execute H-M2 (Difficulty stratification quality) — Week 5
- Step 5: Execute H-M3 (P(True) elicitation) — Week 6
- Step 6: Execute H-M4 (ΔECE measurement + temperature scaling) — Week 7
- Step 7: Evaluate Gate 2 → Route to Phase 5 (baseline comparison) or publish

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Core Claim: LLM confidence signals (P(True) logprob) exhibit
systematically higher miscalibration on problems where the model
rarely generates correct code (hard tier) compared to easy-tier
problems — measured as ΔECE ≥ 0.03 with CI excluding zero.

Supporting Evidence:
1. Causal mechanism validated: Run 3 confirmed P(True) values
   0.57–0.91 for 3 models; ECE_overall computed successfully
2. A priori plausibility: LLMs trained on large corpora don't have
   task-specific difficulty feedback; confidence reflects distributional
   frequency, not problem-specific correctness probability
3. Four pre-registered predictions (P1–P4) with explicit falsification
   thresholds; null baseline comparison controls base-rate confound

Strengths:
- Measurement paper framing (analogous to Guo 2017): publishable
  regardless of ΔECE sign
- Self-contained bootstrap: zero external dependencies, fully replicable
- Run 3 infrastructure: minimal new implementation required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Null Hypothesis (H0): ΔECE ≤ 0 or |ΔECE| < 0.03 in ≥2/3 model
families after controlling for base-rate accuracy differences,
indicating uniform P(True) calibration across difficulty levels.

Counter-Arguments:
1. Base-rate coupling: ΔECE may be mechanically induced by accuracy
   differences — hard tier has lower mean accuracy, which alone
   changes ECE geometry (null baseline comparison addresses this)
2. k=5 sampling noise: With only 6 possible pass@1 values, hard tier
   assignment is unstable — a single different solution changes tier
   membership (Mitigated by pilot framing + explicit n reporting)
3. Architecture comparison (P4): N=1 per architecture category makes
   any cross-model conclusions exploratory only

Conditions Under Which H0 Would Be Supported:
- ΔECE ≤ 0 in ≥2/3 model families (negative calibration-difficulty slope)
- |ΔECE| < 0.03 everywhere after null-baseline subtraction
- Global T scaling collapses ΔECE to within bootstrap noise
- P(True) values degenerate (all ≈0.5): mechanism doesn't activate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Balanced Assessment:
H-CalibDiff-v1 presents a well-scoped measurement study with
pre-registered controls that address every major antithesis concern.
The null baseline comparison (P2) isolates structural from
accuracy-mediated effects. The temperature scaling probe (P3)
distinguishes globally correctable from difficulty-conditioned
miscalibration. Both positive and null ΔECE outcomes are publishable.

Resolution Path:
1. H-E1 (Foundation): Confirms sufficient tier samples exist
2. H-M1–M2 (Infrastructure): Validates solution generation + stratification
3. H-M3–M4 (Core measurement): Tests P1–P3 with pre-registered controls
4. Gate conditions: Early detection if any critical step fails

Nuanced Outcome Possibilities:
1. Full Support (P1 + P2 + P3 confirmed): ΔECE structural and
   not correctable globally → Formal oracle needed in hard-problem VerifAI
2. Partial Support (P1 confirmed, P3 failed): ΔECE real but globally
   correctable → Temperature scaling is sufficient for VerifAI pipelines
3. Null Result (ΔECE ≈ 0): LLM confidence uniform across difficulty →
   P(True) is a reliable cheap soft verifier without difficulty conditioning
4. No Support (H-E1 or H-M3 fails): Pilot methodology insufficient;
   increase k for future work

Overall Robustness: HIGH (all major concerns pre-registered as controls)
Confidence in Plan: 0.80
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence (H-E1) | k=5 bootstrap yields n≥20 per tier | Sample sizes too small with k=5 | H-E1 gate: verify empirically before proceeding |
| Mechanism P(True) (H-M3) | Logprob captures genuine confidence | Prompt-sensitivity artifact | Non-degenerate std(c)>0.05 check; alternative prompt test |
| Core measurement (H-M4) | ΔECE>0 structural | Base-rate accuracy coupling | Null baseline comparison pre-registered as P2 |
| Temperature scaling (H-M4) | ΔECE persists post-T | Global T corrects all | Temperature scaling probe pre-registered as P3 |
| Architecture (P4) | Code-specialized better calibrated | N=1 per category | Labeled exploratory; not used for primary claim |

**Overall Robustness Score:** HIGH
**Confidence in Verification Plan:** 0.80

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-CalibDiff-v1 — Difficulty-Stratified Calibration Fingerprint of LLM Code Verifiers via P(True)
- ID: H-CalibDiff-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (57% scope reduction from BUILD_ON facts)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4, H-C: 0)
- Phases: 2 phases over 7 weeks
- Critical Gates: 4 MUST_WORK + 1 SHOULD_WORK

**Risk Assessment:** Medium
- Primary concerns: R1 (tier underpowering), R3 (P(True) prompt sensitivity)

**Immediate Action:** Begin Phase 2C → Phase 3 → Phase 4 with H-E1 first

### 7.2 Conclusions

**Key Achievements:**
- 5 hypotheses spanning foundation + 4-step causal mechanism chain
- H0 addressed: uniform calibration hypothesis with null baseline controls
- All major objections (base-rate confound, k=5 granularity, architecture underpowering) converted to pre-registered controls

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: k=5 bootstrap yields n≥20 per tier — Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Solution generation + EvalPlus oracle validation
- H-M2: Difficulty stratification quality (cross-model Jaccard)
- H-M3: P(True) logprob elicitation non-degeneracy
- H-M4: ΔECE measurement + temperature scaling probe — Gate 2: H-M1+H-M3+H-M4 must pass

**Critical Decision Points:**
1. Gate 1 (H-E1): FAIL → Relax threshold; if underpowered → STOP
2. Gate 2 (H-M1): FAIL → Debug oracle; if irreparable → PIVOT
3. Gate 2 (H-M3): FAIL → Alternative prompt; if degenerate → PIVOT
4. Gate 2 (H-M4): FAIL → Publish null result (both outcomes publishable)

**Open Questions:**
- Exact tier sample sizes (n_hard, n_easy) per model — depends on model-specific pass rates
- Whether ΔECE direction (positive vs. negative) holds across all 3 model families
- Whether global temperature scaling eliminates ΔECE (determines structural vs. correctable miscalibration)
- Whether partial correlation for solution length affects ΔECE magnitude

**Recommendations:**
1. Immediate: Start Phase 2C experiment design for H-E1 first
2. Resource: Reuse Run 3 infrastructure (h-e1/code/src/h_e1/) — minimal new code
3. Failure: Document all gate results; publish regardless of ΔECE sign

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-CalibDiff-v1, schema v10.0.0)
- Generated: 2026-03-18, 15 discussion exchanges, convergence on all 6 criteria

**B. MCP Tool Usage Summary**
- Total MCP calls: 3 (mcp__clearThought__scientificmethod)
- Call 1: H-E1 hypothesis+experiment+analysis stages
- Call 2a: H-M1-M2 mechanism steps 1-2 hypothesis+experiment stages
- Call 2b: H-M3-M4 mechanism steps 3-4 hypothesis+experiment stages

---

*Generated by YouRA Phase 2B (v6.0) | 2026-03-18*

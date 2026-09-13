---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-03-15T17:00:00"
hypothesis_id: H-RatioReward-v1
date: "2026-03-15"
---

# Verification Plan: Prescreening-Gated R_ratio vs R_binary — Within-Group Variance Amplification in GRPO

**Date:** 2026-03-15
**Hypothesis ID:** H-RatioReward-v1
**Confidence:** 0.72
**Total Hypotheses:** 5

---

## 0. Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON — Do NOT Re-Verify)

| # | Claim | Evidence |
|---|-------|----------|
| EF-1 | GRPO computes group-relative advantages without critic; within-group reward dispersion is sole learning signal | DeepSeekMath [Shao et al., 2024] |
| EF-2 | S_term > 0.85 (APPS competition/interview) is completely intractable for Qwen2.5-Coder-7B — k_pass=0 across all seeds | 5 prior h-e1 Phase 4 failures |
| EF-3 | APPS introductory problems show ~15% test case average for GPT-Neo — partial correctness exists at introductory level | APPS benchmark [Hendrycks et al., 2021] |
| EF-4 | Binary execution reward (R_binary) is universal baseline in GRPO-for-code literature | PPOCoder, DRIVE, G2RPO-A |
| EF-5 | Process-level reward granularity improves over binary outcome reward (+5.1% on MBPP) | PRLCoder [Ye et al., 2025] |

### 0.2 Claims Requiring Proof (PROVE_NEW)

| # | Claim |
|---|-------|
| PN-1 | Under Binomial(T,q) model, E[Var(r_ratio)] > E[Var(r_binary)] for T>1 — needs empirical validation on APPS test-case distributions |
| PN-2 | R_ratio reduces ZRF ≥20% and increases gradient SNR ≥1.5× vs R_binary — central experimental question |

**Scope Reduction:** 67% (5 of 7 claims are established facts; only 2 claims require new verification)

> Phase 2B-4 instruction: Treat GRPO algorithm correctness, APPS availability, S_term>0.85 intractability, and partial correctness at introductory level as ESTABLISHED FACTS requiring no re-verification. Focus experiments on PROVE_NEW claims.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under GRPO-based RLEF training on APPS introductory problems (difficulty=0) prescreened to S_term ∈ [0.3, 0.55] with Qwen2.5-Coder-7B-Instruct + SFT checkpoint (max_new_tokens=1024, temperature=0.8, G=8 rollouts per prompt), if R_ratio is defined as per-rollout fraction of test cases passed (r_i = tests_passed_i / total_tests_i), then R_ratio will produce: (a) earlier ZRF escape (ZRF_ratio(t*) < 0.8 × ZRF_binary(t*) for some t* in first 25% of training) with log-rank p < 0.05, and (b) gradient SNR under R_ratio ≥ 1.5× that under R_binary in the first 25% of training, because R_ratio preserves within-group reward heterogeneity that R_binary clips to {0,1}, enabling GRPO's group-relative advantage normalization to produce informative graded policy gradients.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in ZRF trajectory (log-rank p ≥ 0.05) or gradient SNR (ratio < 1.5×) between R_ratio and R_binary on the prescreened APPS introductory subset under identical GRPO hyperparameters (same initialization, KL penalty, learning rate, batch size G=8, token budget).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | APPS (Automated Programming Progress Standard) — Introductory Split (standard) | APPS introductory problems (difficulty=0) provide sufficient test-case granularity (avg ~13 test cases) for R_ratio to differ from R_binary. Prescreened to S_term ∈ [0.3, 0.55] via empirical pass@8 inference. |
| **Model** | Qwen2.5-Coder-7B-Instruct + SFT Checkpoint | 7B model with SFT checkpoint known to be in partial-tractability regime on APPS introductory at S_term ∈ [0.3, 0.55]. Completely intractable on competition/interview (proven by 5 prior failures). |

**Dataset Details:**
- Source: codeparrot/apps on HuggingFace
- Path: ~/.cache/huggingface/datasets/codeparrot___apps

**Model Details:**
- Type: 7B LLM fine-tuned for code generation
- Source: h-e1/code/sft_checkpoint/ (SFT from 3 epochs on APPS)

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| R_binary GRPO (primary baseline) | ZRF=1.0 at S_term>0.85; expected ZRF<1.0 at prescreened S_term∈[0.3,0.55] | APPS introductory, prescreened |
| PPOCoder [Shojaee et al., 2023] | 17.77% pass rate | APPS (all levels) |
| GHPO [Liu et al., 2025] | +5% over GRPO baseline | Math reasoning benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | APPS introductory problems have T > 1 test cases per problem | APPS benchmark: avg ~13 test cases per problem | R_ratio = R_binary at T=1; no variance advantage possible |
| A2 | Within-group pass fraction distribution non-degenerate for prescreened problems | GPT-Neo ~15% test case average (not all-or-nothing); prescreening checks this | All rollouts pass all or fail all → R_ratio ≡ R_binary; uninformative experiment |
| A3 | Per-test-case pass fraction monotonically related to solution quality | PRLCoder shows per-statement signals informative; APPS test cases are progressive checks | R_ratio provides misleading gradient signals if test cases non-monotone |
| A4 | SFT checkpoint operates in partial-tractability regime on prescreened S_term ∈ [0.3, 0.55] | 5 prior failures confirm S_term>0.85 intractable; new design targets empirically-calibrated tractability | k_pass=0 on prescreened subset → degenerate GRPO; prescreening gate with ≥10% threshold catches this |
| A5 | APPS test cases approximately independent | APPS reports test cases as separate input/output pairs without stated dependencies | Correlated test cases reduce effective T, shrinking variance advantage of R_ratio |

### 1.6 Research Gap & Novelty

**Gap:** No prior empirical comparison of R_ratio vs R_binary under controlled GRPO training with prescreening-gated partial-tractability regime. No formal prescreening protocol for tractability-gated GRPO on APPS. No operational definition of gradient SNR for GRPO reward function comparison.

**Novelty:** First empirical comparison of R_ratio vs R_binary under GRPO specifically on APPS with prescreened partial-tractability gate. Within-group reward variance amplification framing: R_ratio's advantage is information-theoretically grounded in GRPO's group-relative advantage normalization, not merely 'more non-zero gradients'. Binomial(T,q) analytic model proving E[Var(r_ratio)] > E[Var(r_binary)] for all T>1, 0<q<1.

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

**Total: 5 hypotheses** (1 Existence + 4 Mechanism; 0 Condition — boundaries already established by prior failures)

---

### 2.2 Hypothesis Specifications

---
**H-E1: Prescreening Variance Gate — R_ratio Within-Group Variance Advantage**

**Type:** EXISTENCE
**Statement:** Under APPS introductory problems (difficulty=0) with Qwen2.5-Coder-7B-Instruct + SFT checkpoint (pass@8, temperature=0.8, max_new_tokens=1024), if prescreening inference is run on problems with S_term ∈ [0.3, 0.55], then (a) fraction(k_pass ≥ 1) ≥ 10% and (b) E[Var(r_ratio within group)] / E[Var(r_binary within group)] ≥ 1.5× across ≥80% of problem groups, because the Binomial(T,q) model analytically predicts E[Var(r_ratio)] = q(1-q) >> E[Var(r_binary)] = q^T(1-q^T) for T>1.

**Rationale:** Before any GRPO training, we must confirm the variance advantage is real in practice. This hypothesis validates the fundamental prerequisite for the entire experimental design: that R_ratio actually provides different within-group information than R_binary on the prescreened problem set. The Binomial model is analytically confirmed but requires empirical validation on actual APPS test-case distributions.

**Variables:**
- Independent: Problem subset selection (S_term ∈ [0.3, 0.55] APPS introductory)
- Dependent: fraction(k_pass ≥ 1), E[Var(r_ratio)]/E[Var(r_binary)] ratio
- Controlled: Model (Qwen2.5-Coder-7B + SFT), temperature=0.8, k=8, max_new_tokens=1024

**Verification Protocol:**
1. Run pass@8 inference (k=8, temperature=0.8, max_new_tokens=1024) on APPS introductory problems with S_term ∈ [0.3, 0.55].
2. Compute fraction(k_pass ≥ 1) across all problem groups in the prescreened subset.
3. For each problem group, compute Var(r_ratio) and Var(r_binary) from 8 rollouts; average across groups.
4. Compute the variance ratio E[Var(r_ratio)] / E[Var(r_binary)] and check ≥1.5× across ≥80% of groups.
5. Gate decision: PASS if both fraction ≥10% AND variance ratio ≥1.5×; FAIL otherwise.

**Success Criteria:**
- Primary: fraction(k_pass ≥ 1) ≥ 10% on prescreened S_term ∈ [0.3, 0.55] subset
- Primary: E[Var(r_ratio)] / E[Var(r_binary)] ≥ 1.5× across ≥80% of problem groups

**Gate:**
- Type: MUST_WORK
- If Fail: STOP entire experiment — R_ratio cannot provide variance advantage in this regime; return to Phase 0 for problem regime redesign

**Prerequisites:** None

**Source:** Phase 2A Section 1.6 (P1), Section 5 (SH1)

---
**H-M1: Graded Advantage Diversity — R_ratio Produces Multi-Level Normalized Advantages**

**Type:** MECHANISM
**Statement:** Under GRPO training on the prescreened APPS introductory subset (S_term ∈ [0.3, 0.55]) with Qwen2.5-Coder-7B-Instruct + SFT, if R_ratio is computed as tests_passed_i/total_tests_i per rollout, then the per-step advantage distribution under R_ratio shows significantly more distinct advantage levels (≥5 distinct levels vs ≤2 for R_binary) within each group of G=8 rollouts, because GRPO's group-relative normalization A_i = (r_i - mean(r))/std(r) preserves the continuous variance of R_ratio while collapsing R_binary to near-binary {−,+}.

**Rationale:** This step establishes the first causal link: that the mathematical mechanism (graded vs binary advantages) actually manifests in practice under GRPO normalization. Without this, the ZRF escape claim has no mechanistic basis.

**Variables:**
- Independent: Reward function (R_ratio vs R_binary)
- Dependent: Number of distinct advantage levels per group, std(A_i) within group
- Controlled: Same model, hyperparameters, problem set as H-E1

**Verification Protocol:**
1. Initialize GRPO training under both R_ratio and R_binary conditions with identical hyperparameters.
2. Log per-rollout rewards r_i and computed advantages A_i = (r_i - mean(r))/std(r) for each group in first 10% of training steps.
3. Count distinct advantage values (within numerical precision ε=0.01) per group for both conditions.
4. Compare mean number of distinct advantage levels and std(A_i) distributions between conditions.
5. Statistical test: Mann-Whitney U test on distinct-level counts (R_ratio vs R_binary), p < 0.05.

**Success Criteria:**
- Primary: Mean distinct advantage levels under R_ratio ≥ 5 vs ≤ 2 under R_binary
- Secondary: std(A_i) significantly higher under R_ratio (p < 0.05)

**Gate:**
- Type: MUST_WORK
- If Fail: Core mechanism broken — R_ratio's advantage normalization collapses; investigate advantage normalization interaction with R_ratio definition

**Prerequisites:** H-E1 (variance advantage confirmed)

**Source:** Phase 2A Section 1.3 (Step 2), causal_steps[1]

---
**H-M2: Gradient Covariance Amplification — R_ratio Produces Higher Cov(r_i, ‖∇θ log π‖)**

**Type:** MECHANISM
**Statement:** Under GRPO training on the prescreened subset, the covariance Cov(r_i, ‖∇θ log π(o_i)‖) is significantly higher under R_ratio than R_binary in the first 25% of training steps, because graded advantages from R_ratio create stronger alignment between reward-weighted policy gradient direction and actual reward signal, enabling the policy to learn solution styles that partially satisfy test cases.

**Rationale:** This step validates the information-theoretic mechanism: that graded advantages actually translate into more informative gradient signals. Supported by PRLCoder's process supervision finding (+5.1%), but untested in the GRPO reward-function comparison context.

**Variables:**
- Independent: Reward function (R_ratio vs R_binary)
- Dependent: Cov(r_i, ‖∇θ log π(o_i)‖) per training step
- Controlled: Model, hyperparameters, problem set (same prescreened subset)

**Verification Protocol:**
1. During GRPO training, log per-rollout rewards r_i and per-rollout gradient norms ‖∇θ log π(o_i)‖ for each group.
2. Compute Cov(r_i, ‖∇logπ‖) per training step (empirical estimator over group of G=8).
3. Average covariance over first 25% of training steps for both conditions.
4. Compare mean covariance (R_ratio vs R_binary) using paired t-test across 3 seeds.
5. PASS if mean Cov(R_ratio) > mean Cov(R_binary) with p < 0.05.

**Success Criteria:**
- Primary: Mean Cov(r_i, ‖∇logπ‖) under R_ratio > under R_binary (p < 0.05, paired t-test across seeds)
- Secondary: Effect size Cohen's d > 0.5

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document as limitation — covariance diagnostic does not confirm mechanism Step 3; proceed to H-M3 but note uncertainty

**Prerequisites:** H-M1 (graded advantages confirmed)

**Source:** Phase 2A Section 1.3 (Step 3), causal_steps[2]

---
**H-M3: Gradient SNR Amplification — R_ratio Achieves ≥1.5× Higher Gradient SNR**

**Type:** MECHANISM
**Statement:** Under GRPO training on the prescreened APPS introductory subset, gradient SNR defined as |E[A_i]|/std(A_i) per training step is ≥1.5× higher under R_ratio than R_binary in the first 25% of training steps, because graded normalized advantages reduce the noise-to-signal ratio in the policy gradient update direction.

**Rationale:** This directly tests Prediction P3 from Phase 2A. Gradient SNR is the operational metric linking the advantage diversity (H-M1) and covariance (H-M2) findings to a practical training quality indicator. This is a SHOULD_WORK gate because the advantage normalization key tension may partially erase the SNR advantage.

**Variables:**
- Independent: Reward function (R_ratio vs R_binary)
- Dependent: Gradient SNR = |E[A_i]|/std(A_i) per step
- Controlled: Same hyperparameters, problem set, 3 seeds per condition

**Verification Protocol:**
1. During GRPO training, compute per-step gradient SNR = |E[A_i]|/std(A_i) from GRPO training logs for both conditions.
2. Average gradient SNR over first 25% of training steps for each seed and condition (6 runs: 3 seeds × 2 conditions).
3. Compute SNR ratio: mean_SNR(R_ratio) / mean_SNR(R_binary) across seeds.
4. Statistical test: paired t-test on per-seed SNR ratios, p < 0.05.
5. PASS if mean SNR ratio ≥ 1.5× with p < 0.05.

**Success Criteria:**
- Primary: Mean gradient SNR (R_ratio) ≥ 1.5 × Mean gradient SNR (R_binary) over first 25% of training
- Secondary: Consistent direction across all 3 seeds

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document — advantage normalization may erase variance benefit at intermediate pass rates; this is the pre-registered key tension

**Prerequisites:** H-M2 (covariance amplification verified)

**Source:** Phase 2A Section 1.6 (P3), causal_steps[2]

---
**H-M4: ZRF Escape Acceleration — R_ratio Produces Earlier ZRF Escape (Log-Rank p < 0.05)**

**Type:** MECHANISM
**Statement:** Under GRPO training on prescreened APPS introductory (S_term ∈ [0.3, 0.55]) with 3 seeds × 2 conditions (6 runs total), R_ratio produces earlier ZRF escape than R_binary: there exists step t* in first 25% of training where ZRF_ratio(t*) < 0.8 × ZRF_binary(t*), confirmed by log-rank test p < 0.05 on time-to-ZRF-escape survival curves, because earlier policy differentiation toward partial solutions (from graded advantages and higher gradient covariance) increases probability of achieving full-pass solutions faster.

**Rationale:** This is the primary outcome hypothesis — directly testing Prediction P2 from Phase 2A and the central claim of H-RatioReward-v1. All prior mechanism steps (H-M1–M3) build toward this. ZRF escape is the operational definition of "the reward signal is working" in GRPO.

**Variables:**
- Independent: Reward function (R_ratio vs R_binary)
- Dependent: ZRF per training step (fraction of steps with mean group reward = 0.0); time-to-ZRF-escape survival curves
- Controlled: Same model, hyperparameters, prescreened problem set, seeds (42, 1337, 2024)

**Verification Protocol:**
1. Run full GRPO training with both R_ratio and R_binary conditions (3 seeds each) on prescreened subset for defined training steps.
2. Log ZRF (fraction of training steps with mean group reward = 0.0) per step for all 6 runs.
3. Define ZRF escape event: first step where ZRF drops below 0.5 (or alternative: first step with mean group reward > 0).
4. Construct time-to-ZRF-escape survival curves for R_ratio (n=3) vs R_binary (n=3) conditions.
5. Log-rank test on survival curves; also check if ZRF_ratio(t*) < 0.8 × ZRF_binary(t*) for some t* in first 25% of steps.

**Success Criteria:**
- Primary: Log-rank test p < 0.05 (survival curves statistically distinguishable)
- Primary: ZRF_ratio(t*) < 0.8 × ZRF_binary(t*) for some t* in first 25% of training steps
- Secondary: 2 of 3 seeds show consistent direction

**Gate:**
- Type: SHOULD_WORK
- If Fail: H0 supported — no ZRF advantage for R_ratio; document as null result; hypothesis requires reformulation or scope narrowing

**Prerequisites:** H-M3 (gradient SNR advantage verified)

**Source:** Phase 2A Section 1.6 (P2), causal_steps[3], core_statement

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Risk Analysis

#### 3.2.1 Assumption-to-Risk Mapping

**Risk R1 (from A1): T=1 Degenerate Problem Subset**
- Description: Some APPS introductory problems may have only T=1 test case, making R_ratio ≡ R_binary for those problems
- Severity: Medium
- Likelihood: Low (APPS avg ~13 test cases; but tail distribution unknown)
- Affected: H-E1, all downstream

**Mitigation R1:**
1. Prevention: Prescreening step explicitly filters problems with T=1 (exclude from experiment set)
2. Detection: Compute T distribution from APPS introductory before prescreening; flag problems with T≤2
3. Response: SCOPE — restrict experiment to T≥3 problems; document as T-distribution sensitivity analysis

---

**Risk R2 (from A2): Degenerate Within-Group Distribution**
- Description: Rollouts within each group of G=8 may all pass or all fail every test, making within-group variance Var(r_ratio) ≈ 0 ≈ Var(r_binary)
- Severity: High (Critical gate for H-E1)
- Likelihood: Low (prescreening gate specifically designed to catch this)
- Affected: H-E1 (MUST_WORK gate)

**Mitigation R2:**
1. Prevention: H-E1 prescreening explicitly checks E[Var(r_ratio)]/E[Var(r_binary)] ≥ 1.5× — degenerate distribution fails this gate
2. Detection: If variance ratio < 1.5×, immediately flag as A2 violation
3. Response: ABANDON H-E1 — return to Phase 0 for regime redesign if distribution is fully degenerate; PIVOT to different S_term range if partially degenerate

---

**Risk R3 (from A3): Non-Monotone Test Case Ordering**
- Description: If passing test 3 does not imply closer to passing test 4, R_ratio provides misleading gradient signals
- Severity: Medium
- Likelihood: Low-Medium (APPS test cases designed as checks, but order may not be strictly progressive)
- Affected: H-M1, H-M2, H-M3, H-M4

**Mitigation R3:**
1. Prevention: Analyze test case pass-rate correlations from prescreening data; check if pass fractions are approximately Binomial
2. Detection: Plot per-problem pass fraction distribution from prescreening; compare to Binomial(T, q) fit
3. Response: SCOPE — document as limitation if non-monotone; R_ratio advantage may still hold even without strict monotonicity (just requires variance in within-group pass fractions)

---

**Risk R4 (from A4): SFT Checkpoint Out of Partial-Tractability Regime**
- Description: Despite targeting S_term ∈ [0.3, 0.55], the SFT checkpoint may have k_pass=0 on the selected subset
- Severity: Critical (entire experiment fails if prescreening gate fails)
- Likelihood: Low-Medium (5 prior failures at S_term>0.85; new regime designed to be tractable)
- Affected: H-E1 (fraction(k_pass≥1) ≥ 10% check)

**Mitigation R4:**
1. Prevention: Prescreening gate with fraction(k_pass≥1) ≥ 10% threshold explicitly catches this
2. Detection: If H-E1 prescreening fails fraction gate, A4 is violated
3. Response: ABORT current hypothesis — expand S_term range to [0.2, 0.6] and re-prescreene; or try different model checkpoint

---

**Risk R5 (from A5): Correlated APPS Test Cases**
- Description: APPS test cases within a problem may not be independent (passing test i makes passing test i+1 more likely)
- Severity: Medium
- Likelihood: Medium (APPS test case design philosophy unclear; some competitive programming problems have sequential test cases)
- Affected: H-E1 (Binomial model validity), H-M1–M4 (variance advantage magnitude)

**Mitigation R5:**
1. Prevention: Pre-register that Binomial model is an approximation; test-case independence is a stated assumption
2. Detection: Compute empirical variance ratio from prescreening data vs theoretical Binomial prediction; if empirical < theoretical, some correlation exists
3. Response: SCOPE — document as limitation; R_ratio still provides variance advantage even under partial correlation (just smaller magnitude)

---

#### 3.2.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 (T=1 subset) | A1 | H-E1, all downstream | Medium |
| R2 (degenerate distribution) | A2 | H-E1 (MUST_WORK) | High |
| R3 (non-monotone tests) | A3 | H-M1, H-M2, H-M3, H-M4 | Medium |
| R4 (checkpoint intractable) | A4 | H-E1 (fraction gate) | Critical |
| R5 (correlated test cases) | A5 | H-E1 (Binomial validity), H-M1–M4 | Medium |

#### 3.2.3 Risk Summary

| ID | Risk | Source | Severity | Affected | Primary Mitigation |
|----|------|--------|----------|----------|-------------------|
| R1 | T=1 degenerate problems | A1 | Medium | H-E1+ | Filter T≤2 problems in prescreening |
| R2 | Degenerate within-group distribution | A2 | High | H-E1 | Variance ratio gate in H-E1 prescreening |
| R3 | Non-monotone test case ordering | A3 | Medium | H-M1–4 | Empirical pass-fraction analysis from prescreening |
| R4 | SFT checkpoint out of regime | A4 | Critical | H-E1 | Prescreening fraction gate (≥10%) |
| R5 | Correlated test cases | A5 | Medium | H-E1, H-M1–4 | Document as limitation; Binomial approximation |

**Critical Risks: 1, High Risks: 1, Medium Risks: 6, Low Risks: 0**

#### 3.2.4 Additional Risks (ClearThought Collaborative Reasoning — MCP)

**Risk R6 (Statistical Power): Low n=3 per Condition for Log-Rank Test**
- Description: Log-rank test with n=3 per group (R_ratio, R_binary) has limited statistical power — may fail to detect real ZRF escape difference
- Severity: Medium | Likelihood: Medium
- Affected: H-M4
- Mitigation: Pre-register power analysis assuming effect size from Phase 2A estimates; document n=3 as known limitation; report effect size alongside p-value

**Risk R7 (GRPO-Specific): Advantage Normalization Erasure at p≈0.5**
- Description: Z-score normalization A_i=(r_i-mean(r))/std(r) may erase R_ratio variance advantage when within-group pass fractions are homogeneous near p≈0.5 — the pre-registered key_tension from Phase 2A
- Severity: Medium | Likelihood: Medium
- Affected: H-M1, H-M2, H-M3, H-M4
- Mitigation: Pre-register H-M2 covariance diagnostic; report per-step std(r) to detect when normalization is erasing signal; this is a known theoretical concern with pre-registered response (document as limitation)

**Risk R8 (Infrastructure): Gradient Norm Computation Overhead for H-M2**
- Description: Computing per-rollout gradient norms ‖∇θ log π(o_i)‖ requires full backward passes for each of G=8 rollouts per step, potentially 2-4× training overhead
- Severity: Medium | Likelihood: High
- Affected: H-M2
- Mitigation: Implement as optional diagnostic; if full backward passes too costly on H100 NVL, approximate via parameter norm changes between steps; if approximation inadequate, H-M2 can be marked as inconclusive without blocking H-M3/M4

---

## 4. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (EXISTENCE — Prescreening Variance Gate)
    Gate: MUST_WORK
         │
         ▼
[Level 1 - Mechanism Step 1]
    H-M1 (MECHANISM — Graded Advantage Diversity)
    Gate: MUST_WORK
    ← Requires: H-E1
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2 (MECHANISM — Gradient Covariance Amplification)
    Gate: SHOULD_WORK
    ← Requires: H-M1
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3 (MECHANISM — Gradient SNR ≥1.5×)
    Gate: SHOULD_WORK
    ← Requires: H-M2
         │
         ▼
[Level 4 - Primary Outcome]
    H-M4 (MECHANISM — ZRF Escape Acceleration)
    Gate: SHOULD_WORK
    ← Requires: H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 4.1 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|-----------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | Phase 1: Foundation |
| 1 | H-M1 | H-E1 | MUST_WORK | Phase 2: Mechanisms |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Phase 2: Mechanisms |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Phase 2: Mechanisms |
| 4 | H-M4 | H-M3 | SHOULD_WORK | Phase 2: Mechanisms |

### 4.2 Verification Phases with Gate Conditions

**Phase 1 — Foundation**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | Prescreening: fraction(k_pass≥1)≥10% AND variance ratio≥1.5× | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP, reassess problem regime and return to Phase 0.

**Phase 2 — Core Mechanisms** (4 hypotheses)
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST PASS |
| H-M2 | H-M1 | SHOULD PASS |
| H-M3 | H-M2 | SHOULD PASS |
| H-M4 | H-M3 | SHOULD PASS |

→ **Gate 2**: H-M1 must pass. H-M2–M4 failures = document as limitations, not blockers.

---

## 5. Timeline Planning (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2    │ W3-4    │ W5      │ W6      │ W7
──────────────────┼─────────┼─────────┼─────────┼─────────┼──────
PHASE 1: Foundation
  H-E1            │ ████████│         │         │         │
  [Gate 1] ◆      │         │ ◆       │         │         │
──────────────────┼─────────┼─────────┼─────────┼─────────┼──────
PHASE 2: Mechanisms
  H-M1            │         │ ████████│         │         │
  [Gate 2] ◆      │         │         │ ◆       │         │
  H-M2            │         │         │ ████    │         │
  H-M3            │         │         │         │ ████    │
  H-M4            │         │         │         │         │ ████
──────────────────┼─────────┼─────────┼─────────┼─────────┼──────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
Formula: 2 (H-E1) + 2 (H-M1) + 1 + 1 + 1 (H-M2,3,4) = 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.1 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Duration Breakdown:
  H-E1:  2 weeks (prescreening inference + analysis)
  H-M1:  2 weeks (GRPO logging + advantage analysis)
  H-M2:  1 week  (covariance computation from logs)
  H-M3:  1 week  (SNR computation from same logs)
  H-M4:  1 week  (ZRF analysis + log-rank test)

Total Duration: 7 weeks
Slack Available: 0 weeks (fully sequential chain)

Note: H-M2, H-M3, H-M4 can partially overlap since they
analyze the same GRPO training run logs — practical
execution may be 5-6 weeks.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.2 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (boundaries established by prior failures)

Verification Phases: 2
1. Foundation (H-E1): prescreening-only, no training
2. Mechanisms (H-M1–M4): 6 GRPO training runs (3 seeds × 2 conditions)
   Note: H-M2–M4 analyze the same training runs as H-M1

GPU Requirement: 1× H100 NVL (single GPU per run; 6 runs sequential)
Training Runs: 6 (3 seeds × R_ratio + 3 seeds × R_binary)
Total Duration: 7 weeks (5-6 weeks if H-M2–M4 analyzed in parallel)
Critical Path Length: 7 weeks
Execution Mode: Sequential chain with gate checkpoints
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Execution Order

**Step 1**: Execute H-E1 (Foundation/Prescreening) — Week 1-2
**Step 2**: Evaluate Gate 1 → If pass, proceed
**Step 3**: Execute H-M1 (Graded Advantage Diversity) — Week 3-4; concurrent GRPO training for both conditions
**Step 4**: Evaluate Gate 2 → H-M1 must pass
**Step 5**: Execute H-M2 (Covariance Amplification) — Week 5; from same training logs
**Step 6**: Execute H-M3 (Gradient SNR) — Week 6; from same training logs
**Step 7**: Execute H-M4 (ZRF Escape) — Week 7; from same training logs + log-rank test
**Final**: All 5 hypotheses verified → Phase 2C complete per hypothesis

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: R_ratio will produce earlier ZRF escape (log-rank p<0.05)
and gradient SNR ≥1.5× compared to R_binary in GRPO training on
prescreened APPS introductory problems.

Supporting Evidence:
1. Binomial(T,q) analytic model proves E[Var(r_ratio)] > E[Var(r_binary)]
   for all T>1 and 0<q<1 — analytically confirmed in 15-exchange dialogue
2. GRPO's group-relative normalization preserves R_ratio's continuous
   variance while collapsing R_binary to near-binary advantages
3. PRLCoder [Ye et al., 2025] shows process-level granularity improves
   binary outcome reward (+5.1%), validating the granularity principle

Strengths:
- Strong analytic foundation (Binomial model, GRPO formulation)
- Clear mechanism (variance heterogeneity → graded advantages → better gradients)
- Testable with existing infrastructure (no new benchmarks needed)
- Prescreening gate ensures experimental tractability
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis Development (H0-Based)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): No significant difference in ZRF trajectory
(log-rank p ≥ 0.05) or gradient SNR (ratio < 1.5×) between R_ratio
and R_binary under identical GRPO hyperparameters.

Counter-Arguments:
1. GRPO advantage normalization (z-scoring) may erase R_ratio's variance
   advantage: at intermediate p≈0.5, after normalization both reward
   functions may produce similarly distributed advantages
2. Binary reward (R_binary) bootstraps from rare full-pass events —
   even with ZRF, occasional full-pass rollouts drive learning;
   R_ratio's partial gradients may not accelerate this
3. Test-case independence assumption (A5) likely violated for competitive
   programming problems, shrinking effective variance advantage

Potential Failure Points:
- R1: T=1 degenerate problems reduce effective sample size
- R4: SFT checkpoint may still be partially intractable even at S_term ∈ [0.3, 0.55]
- Key tension: z-score normalization partially erases variance gains at p≈0.5

Conditions Under Which H0 Would Be Supported:
- E[Var(r_ratio)]/E[Var(r_binary)] < 1.5× in prescreening (fails H-E1)
- Advantage distribution under R_ratio collapses to near-binary (fails H-M1)
- Log-rank test on ZRF escape curves: p ≥ 0.05 (H0 for H-M4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

H-RatioReward-v1 presents an analytically grounded claim that R_ratio's
within-group variance advantage translates to faster ZRF escape under
GRPO. The Binomial model provides strong theoretical support, and the
prescreening protocol ensures the experimental regime is tractable.
However, the H0 raises valid concerns about GRPO's advantage normalization
potentially erasing the variance benefit, particularly at intermediate
pass rates where z-scoring could homogenize advantages.

Resolution Path:
1. H-E1 (Foundation): Empirically validates variance advantage pre-training
   — directly addresses "does the variance benefit exist in practice?"
2. H-M1 (Graded Advantages): Tests whether normalization preserves or
   erases the advantage diversity
3. H-M2–M3 (Covariance + SNR): Mechanistic chain validation before
   committing to full training
4. H-M4 (ZRF Escape): Primary outcome with pre-registered statistical test

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-M1–M4 all pass → R_ratio validated as ZRF escape mechanism
2. Partial Support: H-E1 + H-M1 pass, H-M3/M4 fail → Variance advantage exists but
   does not translate to ZRF escape; mechanism incomplete; publish as null result with mechanistic insights
3. No Support: H-E1 fails → Fundamental regime mismatch; return to Phase 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Binomial model + prescreening confirm variance advantage | Distribution may be degenerate | H-E1 empirical gate |
| Mechanism | GRPO normalization preserves R_ratio's graded advantages | Z-score normalization erases variance gains at p≈0.5 | H-M1 advantage distribution test |
| Gradient | Cov(r, ‖∇logπ‖) higher under R_ratio | Normalization may erase covariance advantage | H-M2 diagnostic |
| ZRF Escape | Graded gradients accelerate ZRF escape | R_binary bootstraps from rare full-pass; R_ratio may not help | H-M4 log-rank test |
| Test Cases | Binomial model valid (independent tests) | Sequential test dependencies reduce effective T | Empirical sub-Binomial check in H-E1 |

**Overall Robustness Score:** Medium-High (strong analytic foundation, but key tension around advantage normalization at p≈0.5 is pre-registered unresolved concern)

**Confidence in Verification Plan:** 0.72

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-RatioReward-v1 — R_ratio produces earlier ZRF escape and ≥1.5× gradient SNR vs R_binary in GRPO on prescreened APPS introductory (S_term ∈ [0.3, 0.55])
- ID: H-RatioReward-v1, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (67% scope reduction from established facts)
- Sub-Hypotheses: 5 total (H-E1 + H-M1–4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points (Gate 1: H-E1 MUST_WORK; Gate 2: H-M1 MUST_WORK)

**Risk Assessment:** Medium
- Primary concerns: R4 (SFT checkpoint tractability) and advantage normalization erasing variance benefit

**Immediate Action:** Begin Phase 1 with H-E1 (prescreening inference, no GRPO training needed)

### 7.2 Conclusions

**Key Achievements:**
- 5 hypotheses structured across 2 phases with 2 mandatory gates
- H0 addressed: No significant ZRF or SNR difference between R_ratio and R_binary
- 67% scope reduction: 5 of 7 prior claims are established facts (no re-verification needed)
- 4-step causal chain explicitly decomposed into testable H-M1–M4

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Prescreening confirms fraction(k_pass≥1) ≥ 10% AND variance ratio ≥ 1.5×
- Gate 1: MUST PASS — if fail, return to Phase 0

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Graded advantage diversity (MUST_WORK — GRPO normalization preserves variance)
- H-M2: Gradient covariance amplification (SHOULD_WORK — from same training logs)
- H-M3: Gradient SNR ≥ 1.5× (SHOULD_WORK — from same training logs)
- H-M4: ZRF escape log-rank p < 0.05 (SHOULD_WORK — primary outcome)
- Gate 2: H-M1 must pass; H-M2–M4 failures documented as limitations

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 variance gate must pass
   - FAIL → STOP, return to Phase 0 for regime redesign
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 advantage diversity must pass
   - FAIL → Execute failure response (MUST_WORK violation)
   - PASS → H-M2–M4 can continue even with failures (document limitations)

**Open Questions:**
- Is the Binomial independence assumption for APPS test cases empirically valid? (Checkable from prescreening)
- Does Cov(r_i, ‖∇logπ‖) actually favor R_ratio? (Verifiable from prescreening backward passes)
- At what S_term threshold does R_ratio's variance advantage begin to erode?
- Does the ZRF escape advantage persist beyond first 25% of training?

**Recommendations:**

1. **Immediate Actions:**
   - Start H-E1 prescreening: run pass@8 inference on APPS introductory S_term ∈ [0.3, 0.55]
   - Set up logging infrastructure for advantage distributions and gradient covariance before H-M1

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path (5-6 weeks if H-M2–M4 analyses run in parallel after same training)
   - 6 training runs total (3 seeds × 2 conditions) — run one at a time on single H100 NVL

3. **Failure Management:**
   - Document all prescreening statistics (T distribution, variance ratio) regardless of H-E1 gate result
   - Pre-register all success criteria and statistical tests before running experiments

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-RatioReward-v1, 15 exchanges, CONVERGED)
- Generated: 2026-03-15T16:00:00, schema v10.0.0

**B. MCP Tool Usage Summary**
- Total MCP calls (Phase 2B): 3 (Archon: 3 for pipeline/task management)
- ClearThought tools: scientificmethod used inline for hypothesis validation (4-step causal chain analysis)
- Exa tools: Not required (Phase 2A research already comprehensive)

---

*Generated by YouRA Phase 2B (v6.0) | 2026-03-15*

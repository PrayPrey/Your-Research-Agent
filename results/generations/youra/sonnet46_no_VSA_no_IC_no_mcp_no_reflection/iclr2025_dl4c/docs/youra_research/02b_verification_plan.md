---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
hypothesis_id: H-RewardGranularity-v1
research_mode: incremental
status: complete
completedAt: "2026-08-31T00:00:00Z"
---

# Verification Plan: Reward Granularity vs. Generalization in RLEF for Code LLMs

**Date:** 2026-08-31
**Hypothesis ID:** H-RewardGranularity-v1
**Confidence:** 0.72
**Total Hypotheses:** 4 (H-E1, H-M1, H-M2, H-M3)

---

## Section 0: Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON — Do NOT Re-Verify)

| Claim | Evidence |
|-------|----------|
| All published RLEF papers for code (CodeRL, PPOCoder, RLEF/Gehring) use binary pass/fail reward exclusively | CodeRL (2207.01780), PPOCoder (2301.13379), RLEF/Gehring (2410.02089). Confirmed by Phase 1 review. |
| GRPO is superior to PPO for code LLM post-training in stability and compute efficiency | DAPO (2503.14476): GRPO eliminates critic network, 2-3x faster than PPO. |
| RLEF outperforms SFT alone for code generation post-training | CodeRL: ~5pp HumanEval improvement over SFT. RLEF/Gehring: SWE-bench improvement over SFT. |
| APPS dataset supports partial-credit evaluation natively (k/n test cases per problem) | APPS (2105.09938): 10,000 problems with multi-test-case structure. |

### 0.2 PROVE_NEW Claims (Experimental Targets)

| Claim | Sub-Hypothesis |
|-------|----------------|
| No published work has conducted a controlled ablation of reward signal granularity in RLEF for code LLMs | Motivates entire study |
| Ratio reward improves in-distribution performance (HumanEval/MBPP) vs. binary reward | H-E1, H-M1 |
| Reward-evaluation alignment affects cross-benchmark transfer in RLEF | H-M2, H-M3 |

**Scope Reduction:** 50% (4 BUILD_ON claims skipped; only 3 PROVE_NEW claims targeted)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under RLEF post-training with GRPO on APPS training data for 7B-class code LLMs, if reward signal granularity is increased from binary (0/1) to ratio (k/n passing tests) to output-similarity (continuous token overlap), then in-distribution performance (HumanEval, MBPP) increases with granularity while out-of-distribution generalization (LiveCodeBench) shows a non-monotonic pattern and SWE-bench-lite transfer favors binary reward over ratio/similarity, because training-evaluation reward alignment — not just reward density — determines cross-benchmark generalization: models trained with misaligned reward (ratio training → binary test evaluation) learn partial-solution strategies that underperform the test metric compared to models whose training reward format directly matches the evaluation criterion.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in HumanEval pass@1, LiveCodeBench relative gain, or SWE-bench-lite resolve rate between models post-trained with binary, ratio, or output-similarity execution reward signals, after controlling for training steps, model scale, and training data.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | APPS (Automated Programming Progress Standard) (standard) | APPS has native multi-test-case structure (k/n tests per problem) enabling ratio reward computation without dataset modification. 10,000 problems at mixed difficulty levels. Standard training data for RLEF code papers. |
| **Model** | DeepSeek-Coder-6.7B-instruct | 7B-class open-weight code LLM with strong HumanEval/MBPP baselines; available weights and inference code; representative of current RLEF-capable models. |

**Dataset Details:**
- Source: Hendrycks et al. 2021 (arXiv: 2105.09938)
- Path: https://github.com/hendrycks/apps (HuggingFace: codeparrot/apps)

**Model Details:**
- Type: Decoder-only transformer, code-specialized
- Source: deepseek-ai/DeepSeek-Coder (HuggingFace)

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| CodeRL (Le et al., 2022) — binary RLEF with PPO on APPS | ~18% HumanEval pass@1 (vs. ~13% SFT) | APPS, HumanEval | Binary reward only; no reward granularity comparison; PPO not GRPO |
| RLEF/Gehring et al. (2024) — binary RLEF on SWE-bench | Competitive SWE-bench-lite resolve rate | GitHub issues, SWE-bench | Binary reward only; no HumanEval/LiveCodeBench comparison; proprietary model |
| DAPO (Yu et al., 2025) — GRPO for code/math RL | Competitive with PPO-based methods, more stable | Code and math reasoning | Algorithm paper; does not study reward granularity; binary reward assumed |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | APPS test cases are sufficiently non-redundant to make ratio reward informative | APPS problems from competitive programming sources have diverse test cases including edge cases | Ratio reward degenerates to binary reward in expectation; study underestimates ratio reward's true effect |
| A2 | DeepSeek-Coder-6.7B is representative of 7B-class code LLMs for RLEF post-training | Leading open-weight code model; StarCoder2-7B validation planned | Findings may be model-architecture-specific; scale to other architectures requires additional experiments |
| A3 | LiveCodeBench's contamination resistance holds (APPS training data does not contain LiveCodeBench problems) | LiveCodeBench uses post-2023 problems; APPS published 2021 from prior contest years | LCB scores reflect contamination rather than genuine generalization |
| A4 | 1000 GRPO training steps is sufficient to observe meaningful reward-granularity differences | CodeRL showed ~5pp HumanEval improvement; GRPO converges faster than PPO | Null result may reflect insufficient training rather than true null effect |
| A5 | Output-similarity reward (token-level F1) provides meaningful signal for code correctness beyond binary | Token F1 is commonly used in NLP evaluation; captures structural similarity even for wrong answers | Similarity reward may be too noisy (code with different variable names but correct logic gets low F1) |

### 1.6 Research Gap & Novelty

**Gap:** No published work has conducted a controlled ablation of reward signal granularity in RLEF for code LLMs. All prior RLEF papers (CodeRL, PPOCoder, RLEF/Gehring, DAPO) use binary reward exclusively, treating reward formulation as a fixed design choice.

**Key Innovation:** The training-evaluation reward alignment principle — reward format should match downstream evaluation metric, not just maximize information density. This is a general design principle for RLEF pipelines. The counter-intuitive prediction (ratio reward may hurt LiveCodeBench generalization) is the highest-impact contribution if confirmed.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement Summary | Gate | Prerequisites | Status |
|----|------|-------------------|------|---------------|--------|
| H-E1 | EXISTENCE | Ratio reward provides detectably different training signal than binary in GRPO | MUST_WORK | None | READY |
| H-M1 | MECHANISM | Reward signal format shifts optimal policy target from all-pass to expected-coverage maximization | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | Training-evaluation reward alignment determines cross-benchmark generalization direction | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | Similarity reward does not outperform binary on binary-evaluated benchmarks despite denser signal | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Reward Signal Differentiation Existence

**Type:** EXISTENCE
**Statement:** Under GRPO post-training on APPS for DeepSeek-Coder-6.7B, if ratio reward (k/n test cases) is used instead of binary reward (0/1), then (a) per-step gradient norms will differ between conditions at training step ≤500, and (b) HumanEval pass@1 at checkpoint 200 will show a directional difference ≥1pp, because ratio reward provides differentiated signal across partially-correct completions within all-failing groups where GRPO binary reward assigns identical zero reward.

**Variables:**
- IV: Reward signal granularity (binary vs. ratio)
- DV: Per-step gradient norms (during training); HumanEval pass@1 at step 200
- CV: Model (DeepSeek-Coder-6.7B), algorithm (GRPO), training data (APPS), hyperparameters

**Success Criteria:**
- Gradient norm difference between binary and ratio conditions is statistically distinguishable (95% bootstrap CI) at ≥1 checkpoint within first 500 steps
- Directional HumanEval difference ≥1pp at step-200 checkpoint (direction: ratio ≥ binary, OR ratio < binary for policy target shift evidence)

**Gate:**
- Type: MUST_WORK
- If Fail: If gradient norms are equivalent AND no directional HumanEval difference exists at step 200, mechanism Step 1 of causal chain is falsified → revisit whether GRPO group normalization fully compensates for binary reward sparsity; pivot study to focus on Steps 2-3 only

**Prerequisites:** None

**Verification Protocol:**
Run GRPO post-training for binary and ratio reward conditions on APPS (same problems, same hyperparameters). Monitor per-step gradient norms for both conditions and log to file. Evaluate HumanEval pass@1 at step 200. Compare gradient norms using bootstrap confidence intervals (n=1000 bootstrap samples over step window 100-500). Evaluate whether directional difference ≥1pp exists for HumanEval at checkpoint 200. Pre-screen APPS training problems to retain only those with ≥5 non-redundant test cases (A1 assumption validation). Use minimum 164 HumanEval problems for evaluation. Report gradient norm trajectories and checkpoint evaluation curves.

---

#### H-M1: Policy Target Shift

**Type:** MECHANISM
**Statement:** Under GRPO post-training on APPS with ratio reward for DeepSeek-Coder-6.7B, if the optimal policy target shifts from all-pass maximization (binary) to expected-coverage maximization (ratio), then ratio-trained models will achieve higher in-distribution pass@1 on HumanEval (≥3pp) and MBPP, but will show lower or equal 10/10-test-pass rates on APPS validation set compared to binary-trained models, because ratio reward incentivizes models to reliably pass high fractions of tests without consistently achieving all-pass on hard problems.

**Variables:**
- IV: Reward condition (binary vs. ratio)
- DV: HumanEval pass@1 (primary); MBPP pass@1; APPS validation all-pass rate at 1000 steps
- CV: Model, algorithm, training data, steps (1000)

**Success Criteria:**
- pass@1(ratio) - pass@1(binary) ≥ 0.03 on HumanEval (P1 criterion), 95% bootstrap CI excluding 0
- APPS validation all-pass rate: ratio-trained ≤ binary-trained (policy target shift signature)

**Gate:**
- Type: MUST_WORK
- If Fail: If pass@1(ratio) - pass@1(binary) < 0.03 OR APPS all-pass rates are equivalent, policy target shift mechanism is not detectable → study still valid as null finding for H-M1; proceed to H-M2 to check alignment effect independently

**Prerequisites:** H-E1

**Verification Protocol:**
Complete GRPO post-training for binary and ratio conditions to 1000 steps. Evaluate HumanEval (164 problems) and MBPP (374 problems) pass@1 at final checkpoint. Evaluate APPS validation all-pass rate (minimum 500 held-out problems) to check 10/10 vs. partial-pass distribution. Compute bootstrap CIs for all pairwise comparisons. Evaluate StarCoder2-7B secondary model if compute allows. Full standard MBPP test set (374 problems); full HumanEval (164 problems). Report learning curves at every 200-step checkpoint.

---

#### H-M2: Training-Evaluation Alignment

**Type:** MECHANISM
**Statement:** Under GRPO post-training on APPS, if training reward format matches test-time evaluation format (binary training → binary test evaluation), then binary-trained models will show equal or better LiveCodeBench relative gain and SWE-bench-lite resolve rate than ratio-trained models, because partial-solution strategies learned under ratio reward underperform binary evaluation metrics in OOD settings where no partial credit is awarded.

**Variables:**
- IV: Reward condition (binary vs. ratio vs. similarity)
- DV: LiveCodeBench relative gain (RLEF - SFT delta, post-2023 problems); SWE-bench-lite resolve rate (pass@3, n=300)
- CV: Model, algorithm, training data, steps (1000)

**Success Criteria:**
- LiveCodeBench: (HumanEval_gain - LCB_gain)_ratio > (HumanEval_gain - LCB_gain)_binary (P2 criterion — ratio widens the in-distribution vs. OOD gap)
- SWE-bench-lite: resolve_rate(binary) ≥ resolve_rate(ratio), with 95% bootstrap CI on at least one comparison

**Gate:**
- Type: MUST_WORK
- If Fail: If ratio-trained models show proportionally similar LiveCodeBench gains (no widening gap), training-evaluation alignment mechanism is not confirmed → reframe study as "reward granularity affects in-distribution performance but not OOD generalization direction"; report as partial finding

**Prerequisites:** H-M1

**Verification Protocol:**
Evaluate all three reward conditions on LiveCodeBench (post-2023 problems only, verify contamination cutoff relative to APPS). Use relative improvement metric: RLEF_gain = pass@1(RLEF) - pass@1(SFT baseline). Evaluate SWE-bench-lite (300 issues, pass@3, Docker-isolated environment). Compute bootstrap CIs (n=1000) for all comparisons. Use full LiveCodeBench post-2023 problems available (minimum 500 for statistical power); full SWE-bench-lite 300 issues. Report per-benchmark results matrix across all three reward conditions.

---

#### H-M3: Similarity Reward Boundary Condition

**Type:** MECHANISM
**Statement:** Under GRPO post-training on APPS with output-similarity reward (mean token-level F1), if similarity reward is the densest reward signal (continuous per test case), then similarity-trained models will NOT outperform binary-trained models on binary-evaluated benchmarks (HumanEval, LiveCodeBench, SWE-bench-lite), despite achieving higher in-distribution metrics where token overlap correlates with correctness, because token-level F1 of code outputs is a noisy proxy for execution correctness that rewards structural similarity over semantic equivalence.

**Variables:**
- IV: Reward condition (binary vs. similarity)
- DV: HumanEval pass@1; LiveCodeBench relative gain; SWE-bench-lite resolve rate
- CV: Model, algorithm, training data, steps (1000)

**Success Criteria:**
- pass@1(similarity) ≤ pass@1(binary) on LiveCodeBench and SWE-bench-lite (or statistically indistinguishable)
- If similarity outperforms binary on HumanEval: must underperform on LiveCodeBench OOD (alignment mechanism confirmed for similarity too)

**Gate:**
- Type: SHOULD_WORK
- If Fail: If similarity reward consistently outperforms binary across all benchmarks, the training-evaluation alignment hypothesis requires revision — dense reward with format mismatch can still generalize; report as interesting boundary condition finding

**Prerequisites:** H-M2

**Verification Protocol:**
Same GRPO training run as H-M1/H-M2 (three-way comparison already covers similarity condition). No additional training needed — H-M3 reuses the similarity reward experimental condition results from H-M1 and H-M2. Analyze similarity vs. binary comparisons across all four evaluation benchmarks. Check token-F1 correlation with execution correctness on APPS validation set (diagnostic: does high token-F1 correlate with passing execution?). Report all benchmark comparisons for similarity condition.

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
(Phase A: Existence)  (Phase B: Mechanism Steps)  (Phase C: Boundary)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Gradient norms differ OR HumanEval directional diff ≥1pp at step-200 | Causal step 1 falsified; pivot to steps 2-3 only |
| H-M1 | MUST_WORK | pass@1(ratio) - pass@1(binary) ≥ 3pp on HumanEval | Null finding for H-M1; continue to H-M2 independently |
| H-M2 | MUST_WORK | Ratio widens HumanEval-LCB gap AND binary ≥ ratio on SWE-bench-lite | Reframe as partial finding; alignment mechanism not confirmed |
| H-M3 | SHOULD_WORK | Similarity ≤ binary on LCB and SWE-bench-lite | Report as boundary condition finding; revise alignment hypothesis |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase A: Setup & Pre-screening | APPS test case analysis, SFT baseline | ~1 week |
| Phase B: GRPO Training (3 conditions × 1000 steps) | H-E1, H-M1, H-M3 training | ~2 weeks (~300 GPU-hours) |
| Phase C: Evaluation & Analysis | H-M2, H-M3 evaluation + statistics | ~1 week |
| Phase D: Secondary Validation | StarCoder2-7B (if compute) | ~1 week (optional) |

**Total Duration:** ~4-5 weeks (primary); +1 week for optional secondary validation

---

## 4. Risk Analysis

### 4.1 Risk Identification

| Risk ID | Risk Description | Severity | Probability | Linked Assumption | Linked Hypothesis |
|---------|-----------------|----------|-------------|-------------------|-------------------|
| R1 | APPS test case redundancy: ratio reward degenerates to binary | HIGH | MEDIUM | A1 | H-E1, H-M1 |
| R2 | GRPO group normalization neutralizes gradient density advantage of ratio reward | HIGH | MEDIUM | — | H-E1 |
| R3 | 1000 GRPO steps insufficient for differential effects to emerge | MEDIUM | MEDIUM | A4 | H-M1, H-M2 |
| R4 | LiveCodeBench difficulty confound: absolute scores not comparable | MEDIUM | LOW | A3 | H-M2 |
| R5 | Similarity reward (token-F1) too noisy for code — rewards wrong-but-similar code | MEDIUM | MEDIUM | A5 | H-M3 |
| R6 | SWE-bench-lite n=300 provides insufficient statistical power | LOW | HIGH | — | H-M2, H-M3 |
| R7 | DeepSeek-Coder-6.7B architecture-specific behavior | LOW | LOW | A2 | H-M1, H-M2 |

### 4.2 Risk-Hypothesis Mapping

| Hypothesis | Primary Risks | Secondary Risks |
|------------|--------------|-----------------|
| H-E1 | R1, R2 | R3 |
| H-M1 | R1, R3 | R2, R5 |
| H-M2 | R3, R4, R6 | R1, R7 |
| H-M3 | R5 | R6 |

### 4.3 Mitigation Strategies

| Risk | Mitigation | Implementation |
|------|------------|----------------|
| R1 (APPS redundancy) | Pre-screen APPS: retain only problems with ≥5 non-redundant test cases | Before training; run test case diversity analysis |
| R2 (GRPO normalization) | Gradient norm monitoring diagnostic: log per-step gradient norms for both conditions | During training; compare at 100-step intervals |
| R3 (Insufficient steps) | Checkpoint evaluation every 200 steps; extend to 2000 steps if no signal at 1000 | Evaluation plan; compute reserve |
| R4 (LCB difficulty) | Use relative improvement metric: RLEF_gain = pass@1(RLEF) - pass@1(SFT) | Metric design (Prof. Rex recommendation) |
| R5 (Token-F1 noise) | Diagnostic: correlate token-F1 with execution correctness on APPS validation | Pre-experiment validation of similarity reward |
| R6 (SWE-bench-lite power) | Use pass@3 and bootstrap CIs with n=1000; report effect sizes not just p-values | Statistical analysis plan |
| R7 (Architecture specificity) | StarCoder2-7B secondary validation | Optional experiment if primary results are strong |

### 4.4 Risk Summary

**Highest Risk Scenario:** R1 + R2 both materialize → ratio reward is neither informationally superior nor gradient-density superior to binary → H-E1 and H-M1 fail → study becomes null finding paper. **Mitigation:** Pre-screening (R1) + monitoring (R2) are diagnostics that run before final analysis; if both trigger, pivot to reporting the null finding as evidence that GRPO already handles binary reward sparsity (itself a novel contribution).

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization

```
┌─────────────────────────────────────────────────────────┐
│              VERIFICATION DAG                            │
│         H-RewardGranularity-v1                          │
└─────────────────────────────────────────────────────────┘

[PHASE A: EXISTENCE]
        │
        ▼
   ┌─────────┐
   │   H-E1  │  MUST_WORK gate
   │ Gradient│  "Does ratio reward provide
   │ & Chkpt │   different training signal?"
   └────┬────┘
        │ PASS
        ▼
[PHASE B: MECHANISM]
        │
        ▼
   ┌─────────┐
   │   H-M1  │  MUST_WORK gate
   │ Policy  │  "Does reward format shift
   │ Target  │   the optimal policy?"
   └────┬────┘
        │ PASS
        ▼
   ┌─────────┐
   │   H-M2  │  MUST_WORK gate
   │ Alignment│  "Does binary training align
   │ Effect  │   with binary evaluation OOD?"
   └────┬────┘
        │ PASS
        ▼
[PHASE C: BOUNDARY]
        │
        ▼
   ┌─────────┐
   │   H-M3  │  SHOULD_WORK gate
   │Similarity│  "Does similarity reward fail
   │ Boundary │   on binary benchmarks?"
   └─────────┘

Note: H-M1, H-M2, H-M3 share the same 3 training runs.
      Only evaluation differs. H-M3 reuses H-M1/H-M2 data.
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Depends On | Can Proceed If Predecessor Fails? |
|-------|------------|------------|----------------------------------|
| 1 | H-E1 | None | N/A |
| 2 | H-M1 | H-E1 | Yes (H-E1 partial — causal step 1 not confirmed; H-M1 tests step 2) |
| 3 | H-M2 | H-M1 | Yes (H-M2 tests alignment independently of policy target magnitude) |
| 4 | H-M3 | H-M2 | Yes (H-M3 shares training data; can report boundary condition regardless) |

### 5.3 Gantt Timeline

```
Week │ 1        │ 2        │ 3        │ 4        │ 5 (opt)  │
─────┼──────────┼──────────┼──────────┼──────────┼──────────┤
     │ SETUP    │ TRAINING │ EVAL     │ ANALYSIS │ SEC.VAL  │
─────┼──────────┼──────────┼──────────┼──────────┼──────────┤
APPS │ ████████ │          │          │          │          │
pre- │ screen   │          │          │          │          │
─────┼──────────┼──────────┼──────────┼──────────┼──────────┤
SFT  │ ██████   │          │          │          │          │
base │ warmup   │          │          │          │          │
─────┼──────────┼──────────┼──────────┼──────────┼──────────┤
GRPO │          │ ████████ │          │          │          │
3×   │          │ training │          │          │          │
cond │          │ ~300 GPU │          │          │          │
     │          │ H-E1/M1/ │          │          │          │
     │          │ M2/M3    │          │          │          │
─────┼──────────┼──────────┼──────────┼──────────┼──────────┤
Eval │          │          │ ████████ │          │          │
HE/  │          │          │ MBPP/LCB │          │          │
MBPP │          │          │ /SWE     │          │          │
─────┼──────────┼──────────┼──────────┼──────────┼──────────┤
Stat │          │          │          │ ████████ │          │
anal │          │          │          │ Bootstrap│          │
ysis │          │          │          │ CIs,     │          │
     │          │          │          │ Tables   │          │
─────┼──────────┼──────────┼──────────┼──────────┼──────────┤
Sec. │          │          │          │          │ ████████ │
val. │          │          │          │          │StarCoder │
(opt)│          │          │          │          │ 2-7B     │
```

### 5.4 Critical Path Analysis

**Critical Path:** APPS pre-screening → SFT warmup → GRPO training (3 conditions) → SWE-bench-lite evaluation

**Bottleneck:** GRPO training (~300 GPU-hours) is the longest single phase. SWE-bench-lite evaluation (Docker isolation, pass@3) adds wall-clock time.

**Resource Summary:**
- Compute: ~300 GPU-hours (primary); ~100 GPU-hours optional (StarCoder2-7B)
- GPUs: A100 or equivalent (3 parallel runs ideal; sequential possible)
- Infrastructure: trl library (GRPO), HuggingFace model hub, SWE-bench Docker environment

**Execution Order:**
1. APPS test case pre-screening (R1 mitigation)
2. SFT baseline fine-tuning (DeepSeek-Coder-6.7B on APPS, 1 epoch)
3. GRPO training: binary + ratio + similarity (3 conditions, 1000 steps, same hyperparameters)
   - During: gradient norm monitoring (R2 mitigation), HumanEval checkpoint every 200 steps
4. Final evaluation: HumanEval (164), MBPP (374), LiveCodeBench (post-2023), SWE-bench-lite (300)
5. Statistical analysis: bootstrap CIs (n=1000) on all pairwise comparisons
6. (Optional) StarCoder2-7B secondary validation

---

## 6. Dialectical Analysis

### 6.1 Main Hypothesis Dialectical Evaluation

**Thesis:** Increasing reward signal granularity in RLEF for code LLMs improves in-distribution performance but degrades OOD generalization because training-evaluation reward alignment, not reward density alone, determines cross-benchmark transfer.

**Antithesis (H0-based):** GRPO's group normalization already converts binary rewards into effective dense signals within each training batch. Therefore, explicit reward granularity (ratio vs. binary) provides no additional gradient benefit. Any in-distribution performance difference is within noise, and binary-trained models do not generalize better to binary-evaluated OOD benchmarks because reward format is a minor factor relative to training data distribution.

**Evidence For Thesis (Thesis Strengths):**
1. GRPO group normalization operates within each generated group — it normalizes rewards across completions but cannot create signal for partially-correct solutions where binary reward assigns 0 to all; ratio reward differentiates within the all-fail group.
2. Policy target shift (Step 2) is theoretically robust: maximizing E[coverage] and maximizing P(all-pass) are mathematically distinct objectives that should yield different convergence behaviors when partial solutions are common.
3. Training-evaluation alignment (Step 3) has analogues in transfer learning: domain mismatch between training distribution and test distribution consistently degrades performance; reward format mismatch is a form of evaluation domain mismatch.
4. Counter-intuitive predictions (ratio may hurt OOD) are empirically distinguishable and practically important.

**Evidence Against (Antithesis Strengths):**
1. GRPO group normalization is a strong confound for Step 1: if the group contains both all-pass and partial-pass completions, group-relative rewards already provide differentiated signal for binary rewards.
2. 1000 training steps may be insufficient for policy target differences to manifest; both conditions may converge to similar local optima.
3. LiveCodeBench difficulty variation (not just binary format) could explain differential generalization — harder problems, not reward misalignment, may drive OOD gaps.
4. Similarity reward (token-F1) is a weak proxy for code correctness; if H-M3 fails, the "reward format matters" narrative weakens.

**Synthesis:** The thesis and antithesis are not fully incompatible. GRPO normalization partially addresses binary reward sparsity (weakening Step 1) but does NOT eliminate the policy target shift (Step 2) or the training-evaluation alignment effect (Step 3). The study's value is precisely in empirically disentangling these mechanisms: gradient norm monitoring tests Step 1; APPS all-pass rates test Step 2; LiveCodeBench relative improvement tests Step 3. Even if Step 1 is falsified (GRPO already solves sparsity), Steps 2 and 3 remain testable and novel. The study is valuable regardless of Step 1 outcome.

**Robustness Assessment:**
- **If all three predictions confirmed (P1, P2, P3):** Full support for training-evaluation alignment hypothesis. Strong workshop paper. High-impact counter-intuitive finding.
- **If P1 confirmed, P2/P3 not confirmed:** Ratio reward improves in-distribution performance but alignment effect absent. Useful practical finding: "use ratio reward for HumanEval/MBPP targets." Medium impact.
- **If P1 not confirmed, P2/P3 confirmed:** Alignment effect exists without in-distribution benefit — the most surprising outcome. GRPO already solved the density problem; what matters is format alignment only.
- **If all predictions fail (null result):** GRPO makes reward format irrelevant. Also novel: the field can adopt simpler binary rewards with confidence. Still publishable at workshop level.

---

## 7. Executive Summary & Appendices

### 7.1 Executive Summary

**Research Objective:** Determine whether reward signal granularity (binary vs. ratio vs. similarity) in RLEF post-training with GRPO affects in-distribution and OOD performance of 7B-class code LLMs, and whether training-evaluation reward alignment explains differential cross-benchmark generalization.

**Key Findings to Test:**
- H-E1: Ratio reward provides detectably different training signal (gradient norms, early checkpoint performance)
- H-M1: Ratio reward achieves ≥3pp higher HumanEval pass@1 than binary reward (P1)
- H-M2: Ratio training widens the HumanEval-to-LiveCodeBench performance gap vs. binary training (P2); binary reward achieves ≥ resolve rate on SWE-bench-lite (P3)
- H-M3: Similarity reward fails to outperform binary reward on binary-evaluated OOD benchmarks

**Execution Plan:** 4 sub-hypotheses in sequential dependency chain. Shared training infrastructure (3 GRPO conditions). Primary compute: ~300 GPU-hours. Timeline: 4-5 weeks.

**Key Risks:** APPS test case redundancy (R1) and GRPO normalization (R2) are pre-mitigated by pre-screening and gradient monitoring. Statistical power on SWE-bench-lite (R6) managed by bootstrap CIs and pass@3.

**Study Value:** Publishable at all outcome levels. Counter-intuitive null results (ratio hurts generalization) or positive results (alignment principle confirmed) both advance RLEF practitioner knowledge.

### 7.2 Open Questions

- Does GRPO group normalization already solve binary reward sparsity? (Answered by H-E1 gradient norm monitoring)
- Are APPS test cases sufficiently non-redundant for ratio reward? (Answered by pre-screening)
- Is 1000 GRPO steps sufficient? (Answered by checkpoint learning curves; extendable to 2000)
- Does similarity reward (token-F1) correlate with actual code correctness? (Answered by pre-experiment diagnostic)

### 7.3 Conclusions

**Verification Strategy:** Sequential execution (H-E1 → H-M1 → H-M2 → H-M3) with shared training infrastructure ensures maximum compute efficiency. Gates are designed to allow continuation even on MUST_WORK fails, capturing partial evidence.

**Scope:** Intentionally constrained to 7B-class code LLMs, GRPO, APPS training, four evaluation benchmarks. Scale study (1B, 13B) and multi-architecture generalization are clear extensions for a full paper.

**Decision Points:**
1. After H-E1: If gradient norms equivalent → mechanism Step 1 falsified → note as finding, pivot narrative to Steps 2-3
2. After H-M1: If <3pp HumanEval gain → null for in-distribution benefit → check if OOD effects still present
3. After H-M2: If alignment effect confirmed → strong paper; if not → report as "reward format does not determine RLEF OOD generalization"

---

*Generated by Phase 2B Planning workflow — YouRA Research Module*
*Hypothesis: H-RewardGranularity-v1*
*Date: 2026-08-31*

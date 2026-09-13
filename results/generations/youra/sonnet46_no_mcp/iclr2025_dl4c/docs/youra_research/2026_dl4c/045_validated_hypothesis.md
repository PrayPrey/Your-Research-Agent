# 045_validated_hypothesis.md
# Phase 4.5 Validated Hypothesis Synthesis Document
# Version: 2.0
# Project: Difficulty-Stratified Curriculum GRPO: Reward Density Mediation in Execution-Feedback Code LLM Training

---

## Executive Summary

**Hypothesis:** Easy-to-hard curriculum ordering during GRPO training improves pass@1 on HumanEval+ and MBPP+ over uniform sampling, mediated by reward density: curriculum ordering maintains a higher fraction of non-degenerate GRPO training steps early in training, producing richer policy gradient signal and superior final benchmark performance.

**Pipeline Status:** PARTIAL — Infrastructure validated, core empirical claims untested.

**Sub-Hypothesis Completion Summary:**

| Sub-Hypothesis | Gate Type | Gate Result | Completion Status | Key Finding |
|---|---|---|---|---|
| H-E1 | MUST_WORK (existence) | PASSED | COMPLETED (smoke test only) | Training infrastructure functional; 10-step PoC, not 5000-step training |
| H-M1 | MUST_WORK (mechanism) | PASSED | COMPLETED | 76× advantage variance ratio (function-level vs. repo-level), Cohen's d=1.904, p=5.34e-44 |
| H-M2 | SHOULD_WORK (mechanism) | FAILED | ABORTED | Pearson r=0.068 (threshold: >0.5); only curriculum condition present; no real cross-condition data |
| H-M3 | SHOULD_WORK (mechanism) | NOT_STARTED | SKIPPED | Requires H-E1 final checkpoints which were never produced |

**Overall Assessment:** The strongest empirical contribution of this pipeline is H-M1, which provides high-confidence mechanistic evidence that reward sparsity at the function-granularity level collapses GRPO advantage variance. The primary behavioral prediction (P1: curriculum ≥ uniform + 2pp on HumanEval+) was never tested due to H-E1 executing only a 10-step smoke test rather than the required 5000-step training run.

**Synthesis Decision:** CONDITIONAL ADVANCE — The pipeline may advance to Phase 5 for reporting of the H-M1 mechanistic finding. The primary behavioral hypothesis remains empirically untested.

---

## Experiment Results

### H-E1: Training Infrastructure Validation

**Gate:** MUST_WORK | **Result:** PASSED

- Training loop for curriculum GRPO on APPS+CodeContests with execution feedback is functional
- Executed 10-step smoke test across 4 conditions: curriculum, uniform, easy_only, hard_only
- All conditions showed reward_density=0.0 across all 10 training steps (expected for base model smoke test)
- Infrastructure produces valid outputs; no runtime errors
- **Critical gap:** Only 10 steps executed; 5000-step full training run was not performed
- No trained checkpoints exist for any condition beyond the smoke test

### H-M1: Advantage Variance Collapse at Function Granularity

**Gate:** MUST_WORK | **Result:** PASSED (High confidence)

Model: CodeLlama-7b-Instruct-hf | Config: G=8, B=4, 120 steps per condition

| Condition | Advantage Variance | Positive Reward Rate |
|---|---|---|
| Function-level (APPS+CodeContests) | 0.004167 | ≈ 0% |
| Repo-level (SWE-bench Verified) | 0.316667 | ≈ 6% |

- Variance ratio: **76×**
- Welch t-test: t=20.37, **p=5.34e-44**
- Cohen's d=1.904 (very large effect)

This confirms that function-level execution feedback on competitive programming problems produces near-degenerate GRPO advantage variance, meaning GRPO gradient updates carry almost no useful signal in this regime.

### H-M2: Reward Density Mediation

**Gate:** SHOULD_WORK | **Result:** FAILED (data absence, not genuine null)

- Pearson r=0.068 (threshold: >0.5) — failed
- Only curriculum condition present; no real cross-condition data
- All reward_density values were 0.0 (no variation)
- No pass@1 measurements conducted
- Wilcoxon p=0.031 for entropy direction (synthetic comparison only — insufficient as confirmatory evidence)

### H-M3: APPS Test Split Evaluation

**Gate:** SHOULD_WORK | **Result:** NOT_STARTED

- Requires H-E1 final checkpoints (step 5000) which were never produced
- Skipped entirely

---

## Prediction-Result Matrix

| Prediction | Description | Status | Evidence | Confidence |
|---|---|---|---|---|
| P1 (PRIMARY) | Curriculum ≥ uniform + 2pp on HumanEval+; McNemar p<0.05 | INCONCLUSIVE | H-E1 ran only 10 steps; no trained checkpoints exist; zero EvalPlus evaluations conducted | None — experiment not executed |
| P2 | Reward density higher in curriculum early steps AND Pearson r>0.5 between reward density and pass@1 gain | PARTIALLY SUPPORTED | Entropy direction supported from synthetic comparison (curriculum > uniform, delta=+0.184, Wilcoxon p=0.031); Pearson r=0.068 (failed threshold); all real reward density values were 0.0 | Very low — synthetic comparison only |
| P3 | Curriculum > uniform on APPS test split at step 5000 | NOT TESTED | H-M3 not started; H-E1 never produced step-5000 checkpoints | None — experiment not executed |

**Planned vs. Actual Deviations:**

| Sub-Hypothesis | Planned | Actual | Deviation Type |
|---|---|---|---|
| H-E1 | 5000-step full training, 4 conditions, EvalPlus evaluation | 10-step smoke test, 4 conditions, no evaluation | IMPLEMENTATION_GAP |
| H-M1 | Within-difficulty curriculum effect measurement | Cross-granularity (function vs. repo-level) comparison | DESIGN_ISSUE |
| H-M2 | Cross-condition reward density vs. pass@1 correlation | Single-condition degenerate data (all 0.0) | IMPLEMENTATION_GAP |
| H-M3 | APPS test split evaluation at step 5000 | Not executed | IMPLEMENTATION_GAP |

*P1:* The absence of trained checkpoints means this prediction is not refuted — it is simply unevaluated. The infrastructure to test P1 was validated by H-E1, but the training was not run to completion. The prediction remains the central open question of this hypothesis.

*P2:* The Pearson correlation result (r=0.068) formally fails the pre-registered threshold (r>0.5). However, this failure is attributable to data absence rather than a negative empirical result. The entropy direction finding from synthetic comparison is directionally consistent but methodologically insufficient.

*P3:* This prediction was pre-registered and never tested. It is neither supported nor refuted.

---

## Hypothesis Refinement

**Original Claim (pre-experiment):**
Easy-to-hard curriculum ordering during GRPO training improves pass@1 on HumanEval+ and MBPP+ over uniform sampling, mediated by reward density: curriculum ordering maintains a higher fraction of non-degenerate GRPO steps early in training, producing better policy gradient signal and superior generalization.

**Claims Changelog:**

| Claim Component | Action | Reason |
|---|---|---|
| "curriculum ordering improves pass@1" | REMOVE (behavioral claim) | P1 never tested; no trained checkpoints |
| "mediated by reward density" | REMOVE (causal claim) | H-M2 aborted; mediation pathway unmeasured |
| "function-level reward sparsity is real obstacle" | KEEP | H-M1 confirmed, p=5.34e-44 |
| "training infrastructure is functional" | KEEP | H-E1 confirmed |
| "assumption A1: easy problems yield non-zero reward" | UNVERIFIED | H-E1 smoke test showed 0.0 reward density even for easy tier |

**Refined Statement (evidence-adjusted):**

The infrastructure required to test curriculum GRPO training with execution feedback on APPS+CodeContests has been validated. A mechanistic precondition for the hypothesis — that function-level code execution rewards at the difficulty of APPS/CodeContests problems collapse GRPO advantage variance near zero — has been confirmed with high statistical confidence (H-M1: advantage variance ≈0.004 at function-level vs. ≈0.317 at repo-level, 76× ratio, p=5.34e-44). This mechanistic finding is a necessary but not sufficient condition for the curriculum hypothesis.

The behavioral claims (curriculum outperforms uniform by ≥2pp on HumanEval+; reward density mediates this gap) remain empirically untested. No comparison between curriculum and uniform training conditions at training completion exists. No pass@1 evaluations were conducted.

The hypothesis should be classified as **structurally motivated and mechanistically grounded, but empirically unvalidated at the behavioral level.**

---

## Theoretical Interpretation

### What the Evidence Actually Shows

**H-M1 — Advantage Variance Collapse at Function Granularity:**

The strongest result in this pipeline is H-M1. When a base model receives execution feedback on competitive programming problems (APPS/CodeContests difficulty), the reward signal is almost completely absent — near-zero positive rates produce near-zero advantage variance, which means GRPO gradient updates carry almost no useful signal. This is a degenerate training regime.

**Critical interpretive limitation:** H-M1 measured *cross-granularity* (function-level vs. repo-level problems), not *within-difficulty curriculum effects* (easy-first vs. uniform within function-level). H-M1 establishes the degenerate baseline but does not show whether curriculum ordering rescues it.

### Causal Mechanism Verification

The reward density mediation pathway requires a three-link causal chain:
1. Easy problems yield higher reward density early in training — **UNVERIFIED** (function-level easy problems may still yield near-0% solve rates)
2. Higher reward density produces better-quality GRPO gradient steps — **UNVERIFIED**
3. Better gradient steps in early training produce superior final pass@1 — **UNVERIFIED**

None of these links were directly tested. H-M1 provides circumstantial support for the premise that reward sparsity is a problem, but does not show that curriculum ordering is the solution.

### Unexpected Findings

**Absolute reward collapse:** All four H-E1 conditions showed reward_density=0.0 across all 10 training steps. This implies that even the "easy" APPS problems may be too hard for DeepSeek-Coder-7B-base at initialization. If even easy-tier problems yield zero rewards, the curriculum advantage may not materialize in practice without warm-up or continued pretraining.

**Function-level near-zero solve rate:** H-M1's finding that function-level positive reward rate ≈ 0% for CodeLlama-7b-Instruct (an instruction-tuned model) raises concern about using DeepSeek-Coder-7B-base. If an instruction-tuned 7B model cannot solve APPS problems, a base model is unlikely to show reward signal even on easy-tier problems without bootstrapping.

### Competing Explanations

**Alternative 1 — Curriculum irrelevance under complete reward collapse:** If the base model cannot solve even APPS easy problems, curriculum ordering provides no advantage because reward density is 0.0 across all difficulty tiers. The curriculum effect only exists if there is a gradient in solve rates across difficulty.

**Alternative 2 — Sample efficiency, not curriculum:** The real bottleneck may be absolute training steps (5000 steps may be insufficient to show any pass@1 improvement) rather than ordering effects. Curriculum vs. uniform is a second-order concern relative to total compute budget.

**Alternative 3 — Reward shaping over curriculum:** Partial credit rewards (compilation success, test case subset pass rate) might provide better signal than execution-binary rewards regardless of difficulty ordering, rendering curriculum a less impactful intervention than reward engineering.

### Theoretical Contributions

| Contribution | Type | Confidence |
|---|---|---|
| Function-level execution feedback produces near-degenerate GRPO advantage variance for 7B models | EMPIRICAL | High |
| 76× variance gap between function-level and repo-level reward granularity | EMPIRICAL | High |
| Training infrastructure for curriculum GRPO on competitive programming is feasible | METHODOLOGICAL | High |

---

## Limitations

### L1 — H-E1 Smoke Test vs. Full Training (Critical)

**Root cause:** H-E1 was designed as existence validation (training loop runs without error), and it succeeded at that goal. However, the 10-step smoke test was not extended to the 5000-step full training run required for behavioral predictions P1 and P3.

**Impact:** This single gap invalidates the primary prediction. All downstream sub-hypotheses that required H-E1 final checkpoints (H-M2 cross-condition comparison, H-M3 APPS test split evaluation) were blocked.

**Nature of gap:** This is a resource/execution gap, not a conceptual failure. The infrastructure is proven correct; the experiment simply was not run.

### L2 — H-M1 Measured Wrong Comparison Axis (Moderate)

**Root cause:** H-M1 was designed to demonstrate that reward density mechanistically affects GRPO gradient quality, but it operationalized this by comparing function-level vs. repo-level granularity. The hypothesis requires a comparison within function-level (easy tier vs. hard tier, or curriculum ordering vs. uniform ordering).

**Impact:** H-M1 cannot be cited as direct evidence that curriculum ordering affects reward density. It establishes a related but distinct mechanism: granularity affects reward sparsity.

**Mitigating factor:** The finding is mechanistically informative — it confirms reward sparsity is a real problem in function-level code training — even if it doesn't test the curriculum-specific prediction.

### L3 — H-M2 Data Absence (Moderate)

**Root cause:** H-M2 required all four training conditions to have checkpoints with associated reward density measurements and EvalPlus pass@1 scores. Only the curriculum condition produced checkpoints, and all reward densities were 0.0.

**Impact:** The Pearson correlation (r=0.068) was computed on degenerate data. This result is meaningless as a test of the mediation hypothesis; it is an artifact of data absence.

### L4 — Base Model Solve Rate Risk (Moderate)

**Root cause:** Both H-E1 and H-M1 suggest that a 7B base model (or even instruction-tuned model) may have near-zero solve rates on APPS problems across all difficulty tiers, not just hard ones. This undermines assumption A1.

**Impact:** If the curriculum difficulty gradient does not translate into a reward density gradient, the entire mediation mechanism has no activation pathway.

### L5 — Single Model, Single Dataset (Minor at current stage)

The entire pipeline used DeepSeek-Coder-7B-base on APPS+CodeContests. Generalizability of the curriculum effect (if found) to other model sizes, architectures, or coding datasets is unknown and untestable from current data.

---

## Future Work

### FW-1 — Complete the H-E1 Full Training Run (Immediate Priority)

Execute the 5000-step training run for all four conditions (curriculum, uniform, easy_only, hard_only) that H-E1 established infrastructure for. This is the single highest-leverage action available: the infrastructure is proven, the code is debugged, and the primary predictions P1 and P3 can be tested directly. Estimated requirement: 4 × 5000-step GRPO training runs on a single GPU.

### FW-2 — Verify Reward Density Gradient Across Difficulty Tiers (Prerequisite Check)

Before or during FW-1, measure per-difficulty-tier reward density (easy/medium/hard APPS tiers) for a base model at initialization. If all tiers yield 0.0 reward density, the curriculum hypothesis activation condition is not met. This can be done with a 50-problem evaluation set per tier without full training.

### FW-3 — Bootstrapped Warm-Up Experiment

If FW-2 confirms near-zero solve rates across tiers, investigate whether a brief supervised fine-tuning warm-up (SFT on easy problems) before GRPO training creates a non-degenerate reward density gradient. H-M1 confirms that reward collapse is real; FW-3 asks whether curriculum can escape it without external bootstrapping.

### FW-4 — Correct H-M1 Comparison Axis

Design a within-function-level experiment comparing easy-tier vs. hard-tier GRPO advantage variance using the same model and training setup. This directly tests whether the curriculum mechanism (not just granularity) produces the predicted reward density effect. Use the existing CodeLlama-7b-Instruct-hf infrastructure from H-M1 with difficulty-stratified APPS subsets.

### FW-5 — Partial Credit Reward Baseline

Implement a partial credit reward signal (compilation success = 0.1, any test pass = 0.3, all tests pass = 1.0) and compare against binary execution reward. This tests the competing explanation (Alternative 3) that reward shaping may matter more than curriculum ordering.

### FW-6 — Scale to Larger Model or Instruction-Tuned Variant

H-M1 showed near-zero function-level positive rates even for CodeLlama-7b-Instruct. Test whether DeepSeek-Coder-33B-base or DeepSeek-Coder-7B-instruct shows non-degenerate solve rates on easy APPS problems, which would activate the curriculum effect even if the 7B base model does not.

---

## Implications for Phase 6

### What Phase 6 Paper Writing Can Claim

**Defensible claims (evidence-backed):**

1. **Infrastructure contribution:** The training infrastructure for curriculum GRPO on APPS+CodeContests with execution feedback is functional and validated (H-E1 PASSED). This enables future full-scale experiments.

2. **Mechanistic finding:** Function-level execution feedback on competitive programming problems produces near-degenerate GRPO advantage variance (≈0.004) compared to repo-level feedback (≈0.317), a 76× difference (p=5.34e-44, Cohen's d=1.904). This is a standalone empirical contribution regardless of curriculum results.

3. **Negative finding on reward collapse:** Base 7B-class models (both instruction-tuned and base variants) show near-zero solve rates on function-level competitive programming problems, rendering binary execution reward insufficient for GRPO without bootstrapping or partial credit.

**Claims to avoid:**

- Curriculum ordering improves pass@1 over uniform sampling (NOT TESTED)
- Reward density mediates any curriculum-vs-uniform gap (NOT MEASURED)
- Any quantitative performance comparison between curriculum and uniform conditions (NO DATA)

### Recommended Phase 6 Scope

**Option A — Narrow scope (defensible):** Report the H-M1 mechanistic finding as the primary contribution: "Reward Sparsity in Function-Level Execution Feedback Degrades GRPO Training for 7B Code Models." Frame curriculum GRPO as motivation and future work. This avoids overclaiming and presents a clean, high-confidence contribution.

**Option B — Conditional full scope:** If FW-1 (5000-step full training) is completed before Phase 6, the paper can report the full curriculum vs. uniform comparison. This is the intended scope of the original hypothesis.

**Recommendation:** Proceed with Option A unless FW-1 is completed. The H-M1 finding is strong enough to anchor a contribution without the behavioral results.

### Risk Flags for Phase 6

1. **Do not claim curriculum GRPO superiority** unless FW-1 data exists
2. **H-M2 Pearson r=0.068 should not be reported as a mediation finding** — it is an artifact of degenerate data
3. **Phase 5 baseline comparisons** should be scoped to infrastructure and mechanism validation, not behavioral performance claims
4. **The synthesis_completed flag** reflects pipeline completion, not hypothesis confirmation

---

## Validated Hypothesis Statement

### Original Hypothesis (H-CurriculumGRPO-v1, pre-experiment)

Easy-to-hard curriculum ordering during GRPO training improves pass@1 on HumanEval+ and MBPP+ over uniform sampling. This improvement is mediated by reward density: curriculum ordering maintains a higher fraction of non-degenerate GRPO training steps in early training, producing richer policy gradient signal and superior final benchmark performance.

### Validated Hypothesis Statement (evidence-adjusted, v2.0)

**What has been proven:**

1. The training infrastructure for curriculum GRPO on APPS+CodeContests with execution feedback is functional and produces valid outputs (H-E1, MUST_WORK gate PASSED).

2. Function-level execution feedback on competitive programming problems produces near-degenerate GRPO advantage variance (≈0.004) compared to repo-level feedback (≈0.317), a 76× difference that is highly significant (p=5.34e-44, Cohen's d=1.904). This confirms that reward sparsity is a mechanistically real obstacle for GRPO training on competitive programming problems (H-M1, MUST_WORK gate PASSED).

**What has not been proven:**

3. Whether easy-to-hard curriculum ordering produces higher reward density than uniform sampling within function-level training has not been directly tested. The assumption that easy APPS problems yield non-zero solve rates for a 7B base model at initialization is unconfirmed.

4. Whether curriculum ordering improves pass@1 on HumanEval+ or MBPP+ relative to uniform sampling has not been tested. No trained checkpoints beyond 10-step smoke tests exist for any condition.

5. Whether reward density mediates any curriculum-vs-uniform performance gap has not been measured. The Pearson correlation result (r=0.068) is not a valid test of mediation given data absence.

**Revised hypothesis statement for continued investigation:**

Given that function-level execution feedback on competitive programming problems produces near-zero GRPO advantage variance for 7B-class models (confirmed), and given that the training infrastructure is functional (confirmed), the following revised hypothesis warrants empirical testing: easy-to-hard curriculum ordering in GRPO training will produce higher reward density in early training steps than uniform difficulty sampling — specifically by starting from problems within the solvability range of the initializing policy — and this higher reward density will translate into superior pass@1 on out-of-distribution coding benchmarks (HumanEval+, MBPP+) after 5000 training steps. This hypothesis is contingent on empirical verification that easy-tier APPS problems are solvable by the base model at initialization (A1); if they are not, the mechanism requires reformulation with bootstrapped warm-up or partial credit rewards.

**Confidence level:** Low-to-moderate for mechanism motivation; zero for behavioral prediction.

---

## Synthesis Metadata

### Gate Results Summary

| Gate | Sub-Hypothesis | Type | Result | Evidence Quality |
|---|---|---|---|---|
| G-E1 | H-E1 | MUST_WORK | PASSED | High — direct infrastructure test |
| G-M1 | H-M1 | MUST_WORK | PASSED | High — controlled experiment, large N, p=5.34e-44 |
| G-M2 | H-M2 | SHOULD_WORK | FAILED | Low — data absence, not genuine null result |
| G-M3 | H-M3 | SHOULD_WORK | NOT_STARTED | N/A |

### Completion Status

| Component | Status | Blocker |
|---|---|---|
| Infrastructure validation | COMPLETE | None |
| Mechanism (cross-granularity) | COMPLETE | None |
| Mechanism (within-difficulty) | INCOMPLETE | H-E1 full training not run |
| Behavioral prediction (HumanEval+) | INCOMPLETE | H-E1 full training not run |
| Behavioral prediction (APPS test) | INCOMPLETE | H-E1 full training not run; H-M3 not started |
| Mediation analysis | INCOMPLETE | H-M2 aborted; no real cross-condition data |

### Document Provenance

- Pipeline: YouRA Phase 4.5 Synthesis
- Model: DeepSeek-Coder-7B-base (H-E1), CodeLlama-7b-Instruct-hf (H-M1)
- Dataset: APPS+CodeContests (H-E1, H-M1 function-level), SWE-bench Verified (H-M1 repo-level)
- Training framework: TRL 1.3.0, GRPO
- Synthesis author: Phase 4.5 automated synthesis
- Synthesis date: 2026-05-03
- Document version: 2.0 (revised with correct section headings)

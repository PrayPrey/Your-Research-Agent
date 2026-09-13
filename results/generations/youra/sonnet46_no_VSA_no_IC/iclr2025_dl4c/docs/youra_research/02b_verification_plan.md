---
hypothesis_id: H-VarianceGuidedRLEF-v1
generated_at: "2026-08-21"
research_mode: incremental
scope_reduction_percentage: 75
total_hypothesis_count: 5
causal_chain_count: 4
condition_hypothesis_count: 0
transfer_validation: false
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
status: complete
completedAt: "2026-08-21"
---

# Verification Plan: Variance-Guided RLEF Subset Selection

**Date:** 2026-08-21
**Hypothesis ID:** H-VarianceGuidedRLEF-v1
**Confidence:** 0.78
**Total Hypotheses:** 5

---

## Section 0: Established Facts & Scope Reduction

**Scope Reduction: 75%** — 6 of 8 claims are BUILD_ON (established facts, not re-verified).

| Claim | Status | Evidence |
|-------|--------|----------|
| GRPO gradient identity σ=√(k(G-k))/G | BUILD_ON | bay-yearick-lab/grpo-standard-deviation-identity; VIGOR arXiv:2607.22002 |
| 69.25% zero-gradient at G=4 binary rewards | BUILD_ON | Gradient Starvation arXiv:2605.07689 |
| Difficulty-targeted selection reduces RLVR compute 23–62% | BUILD_ON | Sun et al. 2025, arXiv:2506.05316 |
| RLEF with binary execution reward improves code pass@1 | BUILD_ON | Gehring et al. 2024, arXiv:2410.02089 |
| EvalPlus correctness scoring operational in h-e1 | BUILD_ON | h-e1 environment validation |
| TRL GRPO trainer (use_vllm=False, batch=4) functional in h-e1 | BUILD_ON | h-e1 environment validation |
| Per-problem variance distribution across MBPP uncharacterized | **PROVE_NEW** | Phase 1 gap analysis |
| Variance-guided vs random selection not compared for binary RLEF | **PROVE_NEW** | Phase 1 gap analysis |

**Phase 2B–4 Instructions:** Only H-E1 and H-M1–H-M4 require new verification. BUILD_ON claims are foundations.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under short RLEF (20–50 GRPO steps, use_vllm=False, G=4, generation_batch_size=4) for code generation, if variance-guided subset selection is applied (top-50 MBPP training problems by frozen-model binary execution reward variance p_i*(1-p_i), computed via k=8 i.i.d. completions from frozen DeepSeek-Coder-7B-Instruct), then HumanEval+ pass@1 improvement per gradient step will exceed random-50 subset RLEF, because variance profiling concentrates GRPO gradient steps on problems with nonzero within-group reward variance while random selection includes ~69% zero-gradient problems that waste training capacity.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in HumanEval+ pass@1 improvement between variance-selected and random-selected RLEF subsets of equal size (N=50) at 50 GRPO steps, measured by EvalPlus correctness-based evaluation.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | MBPP (standard) | Standard benchmark for binary execution reward RLEF; h-e1 environment confirms operational; 374-problem training split provides data selection pool |
| **Model** | DeepSeek-Coder-7B-Instruct | Confirmed functional in h-e1; 7B scale balances capability with tractable training time |

**Dataset Details:**
- Source: google-research-datasets/mbpp (HuggingFace Datasets)
- Path: Training split: 374 problems; evaluation uses HumanEval+ (separate, 164 problems)

**Model Details:**
- Type: Code LLM, instruction-tuned, 7B parameters
- Source: deepseek-ai/deepseek-coder-7b-instruct-v1.5 (HuggingFace)

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Random-50 RLEF (same step budget) | To be measured | MBPP → HumanEval+ |
| Full-374 RLEF (same step budget) | Up to 13pp pass@1 (Skopin & Kotelnikov, different models) | MBPP → HumanEval+ |
| Sun et al. 2025 difficulty-targeted | 23–62% compute reduction | Math reasoning (not code) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | k=8 profiling provides stable top-50 ranking | k=8 aligns with G=4–8; MSE bounded; identity holds for any k | Selection advantage diminished but not eliminated |
| A2 | MBPP is heterogeneous for DeepSeek-Coder-7B (non-degenerate variance) | RLVR on MBPP yields up to 13pp gain; MBPP spans difficulty levels | Top-50 confounds variance with difficulty |
| A3 | Frozen-model variance rank valid proxy over 20–50 steps | Very short training regime; significant shifts require 100s–1000s steps | Selected problems move out of learning zone mid-training |
| A4 | HumanEval+ pass@1 sensitive enough (≥2pp detectable in 50 steps) | Skopin & Kotelnikov: up to 13pp at full scale; EvalPlus confirmed in h-e1 | Primary metric unmeasurable; secondary P2 still informative |
| A5 | 3-condition comparison causally identified (not confounded by init) | Random-50 randomization control; fixed seed; same base checkpoint | Single-run confounded by GRPO init variance |

### 1.6 Research Gap & Novelty

**Key Innovation:** First offline frozen-model variance profiling approach for binary execution reward RLEF data selection. All prior work (VIGOR, Sun et al. 2025, Prompt Replay, LZE) requires an active training loop — they are online methods. This "profile once, train anywhere" pattern is novel.

**Differentiation:** All prior papers target math reasoning with scalar rewards. This is the first application to binary execution reward code generation on MBPP/HumanEval+.

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
**H-E1: MBPP Variance Distribution Heterogeneity**

**Statement:** Under frozen-model profiling (k=8 i.i.d. completions per problem from DeepSeek-Coder-7B-Instruct), the MBPP training split (374 problems) exhibits a non-degenerate variance distribution where a meaningful fraction of problems have intermediate pass rates (0.25 < p_i < 0.75), yielding p_i*(1-p_i) > 0.1 for a non-trivial subset, confirming that top-50 variance-guided selection preferentially includes problems with nonzero GRPO gradient signal.

**Rationale:** This is the foundational existence check. If the MBPP variance distribution is degenerate (all p_i ≈ 0 or p_i ≈ 1 for DeepSeek-Coder-7B), variance selection provides no advantage over random and the entire hypothesis chain collapses. H-E1 must pass before any mechanism testing.

**Variables:**
- Independent: Profiling sample size (k=8, controlled)
- Dependent: p_i distribution across 374 MBPP problems; count of problems with 0.25 < p_i < 0.75
- Controlled: Frozen DeepSeek-Coder-7B-Instruct; binary_execution_reward; MBPP training split

**Verification Protocol:**
1. Run frozen-model profiling: generate k=8 completions per MBPP problem with no gradient updates.
2. Compute p_i = correct(k=8)/8 and variance_i = p_i*(1-p_i) for all 374 problems.
3. Report: histogram of p_i distribution; count of problems with 0.25 < p_i < 0.75; top-50 selected problem IDs.
4. Verify: at least 50 problems have variance_i > 0.1 (confirming selection is non-trivial).
5. Record: ranking stability diagnostic (expected variance of p_i estimate at boundary rank 50).

**Success Criteria (PoC):**
- Primary: ≥50 MBPP problems have p_i*(1-p_i) > 0.1 (enough candidates for top-50 selection)
- Secondary: Top-50 selected problems have mean p_i ∈ [0.25, 0.75]

**Failure Response:**
- IF fails (degenerate distribution): ABANDON — variance selection provides no advantage; reassess entire hypothesis.

**Dependencies:** None (foundation)

**Source:** Phase 2A Section 5 SH1; PROVE_NEW claim 1

---

**H-M1: Variance Profiling Produces Stable Per-Problem Ranking**

**Statement:** Under k=8 frozen-model profiling, the top-50 MBPP problems selected by variance_i = p_i*(1-p_i) are meaningfully different from a random-50 selection in their variance distribution, and the selected problems have higher mean variance than random-50 (confirming that the selection signal is real, not noise).

**Rationale:** H-M1 validates the first causal step: profiling correctly identifies high-variance problems. If top-50 variance-selected problems don't actually have higher variance than random-50, the mechanism is broken at the source. This test is purely from profiling output — no training needed.

**Variables:**
- Independent: Selection method (top-50 by variance vs random-50)
- Dependent: Mean variance_i of selected set; overlap between variance-50 and top-50 by alternative stability metric
- Controlled: k=8, frozen model, same 374 MBPP problems

**Verification Protocol:**
1. From profiling output (H-E1), compute mean(variance_i) for variance-50 vs random-50.
2. Verify mean(variance_i(variance-50)) > mean(variance_i(random-50)).
3. Report: rank distribution of selected problems; gap between rank-50 and rank-51 variance values.
4. Compute expected ranking stability (SE of p_i estimate at boundary rank).
5. Document: top-50 selected problem IDs for experiment reproducibility.

**Success Criteria (PoC):**
- Primary: mean(variance_i(variance-50)) > mean(variance_i(random-50)) — direction-based check
- Secondary: rank-50 variance_i > rank-51 variance_i (boundary is non-degenerate)

**Failure Response:**
- IF fails: PIVOT — k=8 insufficient for stable ranking; increase to k=16 or use alternative selection criterion.

**Dependencies:** H-E1

**Source:** Phase 2A Section 1.3 Step 1; assumption A1

---

**H-M2: Variance Selection Eliminates Near-Zero-Gradient Problems**

**Statement:** Problems in the variance-50 set have significantly lower rates of zero-gradient GRPO groups during training than random-50 problems, because variance_i ≈ 0 problems (p_i ≈ 0 or p_i ≈ 1) are excluded from variance-50, and for any such problem k=0 or k=G always occurs in the group, producing σ = 0 by the exact identity σ=√(k(G-k))/G.

**Rationale:** This is the core mechanistic test. The mathematical identity guarantees zero gradient for extreme-p_i problems. H-M2 verifies that the profiling-based selection actually changes the per-step gradient information content during training. The TRL frac_reward_zero_std metric provides direct measurement.

**Variables:**
- Independent: Selection method (variance-50 vs random-50)
- Dependent: mean frac_reward_zero_std at training steps 10, 20, 50
- Controlled: G=4, use_vllm=False, generation_batch_size=4, lr=5e-7, same base model checkpoint

**Verification Protocol:**
1. Run GRPO training for variance-50 condition (50 steps); log frac_reward_zero_std per step via TRL.
2. Run GRPO training for random-50 condition (50 steps); log frac_reward_zero_std per step.
3. Compute mean frac_reward_zero_std at checkpoints 10, 20, 50 for each condition.
4. Compare: mean_frac_zero_std(variance-50) vs mean_frac_zero_std(random-50) at each checkpoint.
5. Plot learning curves for both conditions.

**Success Criteria (PoC):**
- Primary: mean_frac_zero_std(variance-50) < mean_frac_zero_std(random-50) at ALL three checkpoints
- Secondary: Gap ≥5pp at checkpoint 10 (early signal of selection quality)

**Failure Response:**
- IF fails at all checkpoints: PIVOT — proxy doesn't filter zero-gradient problems; explore online selection.
- IF fails at some checkpoints: EXPLORE — document learning zone exhaustion dynamics.

**Dependencies:** H-M1

**Source:** Phase 2A Section 1.3 Step 2; Gradient Starvation arXiv:2605.07689

---

**H-M3: Gradient Concentration Sustains Nonzero Learning Signal Throughout Training**

**Statement:** During GRPO training on variance-50, the fraction of steps with nonzero reward variance (1 - frac_reward_zero_std) remains higher than random-50 throughout the full 50-step training budget, confirming that the frozen-model variance proxy does not degrade too quickly for problems to remain in the learning zone.

**Rationale:** A key concern (A3) is that the frozen-model proxy becomes stale as training progresses — a problem at p_i=0.45 at step 0 may reach p_i=0.85 by step 20. H-M3 tests whether the proxy is stable enough over 20–50 steps by examining whether the frac_reward_zero_std gap between variance-50 and random-50 is maintained (not just early in training).

**Variables:**
- Independent: Training step (temporal variable)
- Dependent: frac_reward_zero_std(variance-50) - frac_reward_zero_std(random-50) at each step
- Controlled: Same as H-M2

**Verification Protocol:**
1. Use TRL training logs from H-M2 experiment (no new training needed).
2. Compute the gap: frac_zero_std(random-50) - frac_zero_std(variance-50) at each step 1–50.
3. Check if gap is positive (variance-50 better) at checkpoints 10, 20, AND 50.
4. Check gap trend: stable, increasing, or decreasing (proxy degradation = decreasing gap).
5. Report: gap trajectory as secondary finding regardless of H-M4 outcome.

**Success Criteria (PoC):**
- Primary: Gap is positive at steps 10, 20, AND 50 (variance-50 consistently better)
- Secondary: Gap at step 50 ≥ 50% of gap at step 10 (proxy not fully degraded)

**Failure Response:**
- IF gap disappears by step 20: EXPLORE — document proxy degradation rate; scope hypothesis to ≤10 steps.
- IF gap positive at 10 but negative at 50: partial finding — short RLEF (≤20 steps) may benefit more.

**Dependencies:** H-M2

**Source:** Phase 2A Section 1.3 Step 3; assumption A3; key tension statement

---

**H-M4: Gradient Concentration Translates to HumanEval+ Pass@1 Improvement Advantage**

**Statement:** Under short RLEF (50 GRPO steps), variance-50 achieves ≥2pp HumanEval+ pass@1 improvement over baseline AND ≥1pp improvement over random-50, because sustained nonzero gradient signal (H-M2, H-M3) produces a superior policy improvement that generalizes from MBPP training to HumanEval+ evaluation.

**Rationale:** The final causal step: gradient concentration must translate into measurable capability improvement. This is the primary hypothesis test. The 2pp threshold ensures the effect exceeds EvalPlus evaluation noise; the 1pp gap threshold ensures variance-50 is meaningfully better than random-50, not just better than no training.

**Variables:**
- Independent: Selection method (variance-50 vs random-50 vs full-374)
- Dependent: HumanEval+ pass@1 improvement (EvalPlus step_50 - step_0), absolute pp
- Controlled: Same as H-M2; EvalPlus HumanEval+ 164 problems, k=8 eval generations

**Verification Protocol:**
1. Run EvalPlus evaluation on DeepSeek-Coder-7B-Instruct checkpoint at step 0 (baseline).
2. Run EvalPlus evaluation at step 10, 20, 50 checkpoints for variance-50, random-50, full-374.
3. Compute improvement = pass@1(step_N) - pass@1(step_0) for each condition at each checkpoint.
4. Check P1: variance_50_improvement ≥ 2pp AND (variance_50_improvement - random_50_improvement) ≥ 1pp at step 50.
5. Check P3 (conditional): if both variance-50 and full-374 ≥ 2pp, check variance_50/full_374 ≥ 0.80.

**Success Criteria (PoC):**
- Primary: variance_50_improvement ≥ 2pp AND variance_50_improvement - random_50_improvement ≥ 1pp (P1)
- Secondary: variance_50_improvement / full_374_improvement ≥ 0.80 (P3, conditional)

**Failure Response:**
- IF P1 fails but P2 passes: partial result — mechanism confirmed but insufficient for capability transfer; document as scope limitation.
- IF P1 fails AND P2 fails: ABANDON — hypothesis chain broken; route to Phase 0.

**Dependencies:** H-M3

**Source:** Phase 2A Section 1.3 Step 4; predictions P1 and P3

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥50 problems with variance > 0.1 | STOP: reassess hypothesis |
| H-M1 | MUST_WORK | mean(variance(variance-50)) > mean(variance(random-50)) | PIVOT: increase k or change criterion |
| H-M2 | SHOULD_WORK | frac_zero_std(variance-50) < frac_zero_std(random-50) at all checkpoints | PIVOT to online selection |
| H-M3 | SHOULD_WORK | Gap positive at steps 10, 20, AND 50 | EXPLORE: document proxy degradation |
| H-M4 | SHOULD_WORK | variance_50_improvement ≥ 2pp AND gap ≥ 1pp | ABANDON if P2 also fails |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1, H-M1 (profiling only) | 2 weeks |
| Phase 2: Mechanism | H-M2, H-M3 (training + logging) | 3 weeks |
| Phase 3: Capability | H-M4 (EvalPlus evaluation) | 1 week |

**Total Duration:** 6 weeks (critical path: sequential, no parallelization)

---

## 4. Sub-Hypothesis Inventory (Detailed)

*See Section 2.2 for full specifications.*

| ID | Type | Gate | Source | Brief Statement |
|----|------|------|--------|-----------------|
| H-E1 | EXISTENCE | MUST_WORK | SH1 / PROVE_NEW-1 | MBPP variance distribution is heterogeneous for DeepSeek-Coder-7B |
| H-M1 | MECHANISM | MUST_WORK | Causal Step 1 | Variance profiling produces stable, meaningful ranking |
| H-M2 | MECHANISM | SHOULD_WORK | Causal Step 2 | Variance selection lowers frac_reward_zero_std vs random |
| H-M3 | MECHANISM | SHOULD_WORK | Causal Step 3 | Gradient concentration sustained throughout 50 steps |
| H-M4 | MECHANISM | SHOULD_WORK | Causal Step 4 | Gradient concentration → HumanEval+ pass@1 advantage |

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation: Existence]
    H-E1 (EXISTENCE — MUST_WORK — no dependencies)
         │
         ▼ [Gate 1: MUST_WORK — if fails → STOP]
[Level 1 - Profiling Validity]
    H-M1 ← H-E1  (MECHANISM — MUST_WORK)
         │
         ▼ [Gate 2: MUST_WORK — if fails → PIVOT]
[Level 2 - Gradient Mechanism]
    H-M2 ← H-M1  (MECHANISM — SHOULD_WORK)
         │
         ▼
[Level 3 - Proxy Stability]
    H-M3 ← H-M2  (MECHANISM — SHOULD_WORK)
         │
         ▼
[Level 4 - Capability Transfer]
    H-M4 ← H-M3  (MECHANISM — SHOULD_WORK)
         │
         ▼
    [Phase 5: Baseline Comparison — DETERMINES_SUCCESS]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
All Sequential — No Parallelization
═══════════════════════════════════════════════════════════
```

### 5.2 Verification Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses, 6 Weeks
═══════════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ W1-2    │ W3-4    │ W5      │ W6      │
─────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1 (profiling)   │ ████████│         │         │         │
  H-M1 (rank check)  │ ████████│         │         │         │
  [Gate 1+2]         │       ◆ │         │         │         │
─────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanism
  H-M2 (training)    │         │ ████████│         │         │
  H-M3 (proxy stab.) │         │ ████████│         │         │
  [derived from logs]│         │       ◆ │         │         │
─────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 3: Capability
  H-M4 (EvalPlus)    │         │         │ ████████│ ████████│
  [Gate 3]           │         │         │         │       ◆ │
═══════════════════════════════════════════════════════════════════════
Legend: ████ = Active work │ ◆ = Gate decision point
Total Duration: 6 weeks
Critical Path: H-E1→H-M1→H-M2→H-M3→H-M4 (all sequential)
Formula: 2 (H-E1+H-M1 profiling) + 2 (H-M2+H-M3 training) + 2 (H-M4 eval) = 6 weeks
═══════════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 6 weeks
  Breakdown: 2 (profiling) + 2 (training) + 2 (evaluation)
Slack: 0 weeks (fully sequential chain)
Note: H-M3 derived from H-M2 training logs (no additional compute)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.4 Dependency Hierarchy

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Level │ Hypothesis │ Prerequisites │ Gate Type
──────┼────────────┼───────────────┼──────────
  0   │ H-E1       │ None          │ MUST_WORK
  1   │ H-M1       │ H-E1          │ MUST_WORK
  2   │ H-M2       │ H-M1          │ SHOULD_WORK
  3   │ H-M3       │ H-M2          │ SHOULD_WORK
  4   │ H-M4       │ H-M3          │ SHOULD_WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (not required)

Verification Phases: 3
1. Foundation (H-E1, H-M1) — profiling only
2. Mechanism (H-M2, H-M3) — GRPO training runs
3. Capability (H-M4) — EvalPlus evaluation

Total Duration: 6 weeks
Critical Path Length: 6 weeks
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. Risk Analysis

### 6.1 Assumption-to-Risk Mapping

| ID | Risk | Source | Severity | Affected Hypotheses |
|----|------|--------|----------|---------------------|
| R1 | k=8 ranking unstable at boundary | A1 | Medium | H-E1, H-M1 |
| R2 | Degenerate MBPP variance for 7B model | A2 | High | H-E1 (blocker) |
| R3 | Proxy degrades rapidly during training | A3 | High | H-M2, H-M3 |
| R4 | HumanEval+ below noise floor at 50 steps | A4 | Medium | H-M4 |
| R5 | Single-run confound from GRPO init variance | A5 | Medium | H-M4 |

### 6.2 Risk Details & Mitigation

**Risk R1: Unstable k=8 Ranking at Boundary**
- Source: A1
- Severity: Medium | Likelihood: Medium
- Affected: H-E1, H-M1
- Description: k=8 may be insufficient to stably rank problems near rank-50 boundary; rank-50 and rank-51 may swap on re-profiling.
- Mitigation:
  1. Prevention: Report SE of p_i estimate at boundary rank as profiling diagnostic.
  2. Detection: Compare top-50 selected IDs from two independent k=8 profiling runs (same model).
  3. Response: PIVOT — increase k to 16 if boundary instability confirmed; ranking stability diagnostic is a secondary contribution regardless.
- Early Warning: SE(p̂_50) > 0.1 indicates unstable boundary.

**Risk R2: Degenerate Variance Distribution**
- Source: A2
- Severity: High | Likelihood: Low
- Affected: H-E1 (blocker for entire chain)
- Description: If DeepSeek-Coder-7B already near-perfectly solves MBPP (p_i ≈ 1 for most problems) or completely fails (p_i ≈ 0), top-50 by variance confounds with difficulty selection.
- Mitigation:
  1. Prevention: Run H-E1 profiling first; check distribution before any training.
  2. Detection: H-E1 success criterion directly tests for non-degeneracy.
  3. Response: ABANDON — if distribution degenerate, the entire selection mechanism is invalid. Route to Phase 0.
- Early Warning: H-E1 fails (<50 problems with variance > 0.1).

**Risk R3: Proxy Degradation During Training**
- Source: A3
- Severity: High | Likelihood: Medium
- Affected: H-M2, H-M3
- Description: Frozen-model variance rank may become stale as training progresses; frac_reward_zero_std gap between variance-50 and random-50 may close by step 20–30.
- Mitigation:
  1. Prevention: Explicitly scope to short RLEF (≤50 steps); h-e1 constraint (use_vllm=False) keeps steps short anyway.
  2. Detection: H-M3 measures gap trajectory across steps 10, 20, 50.
  3. Response: EXPLORE — if gap closes, document proxy lifetime as the contribution; recommendation: use online selection for longer RLEF.
- Early Warning: frac_reward_zero_std gap < 5pp by step 20.

**Risk R4: HumanEval+ Below Noise Floor**
- Source: A4
- Severity: Medium | Likelihood: Medium
- Affected: H-M4
- Description: 50 GRPO steps on 50 problems may produce <2pp HumanEval+ improvement for any condition, making P1 untestable.
- Mitigation:
  1. Prevention: Pre-specify minimum effect size (2pp); declare P1 untestable (not failed) if no condition achieves 2pp.
  2. Detection: H-M4 evaluates all 3 conditions; if full-374 also fails to achieve 2pp, scope issue confirmed.
  3. Response: If mechanistic evidence (P2) is positive, partial result: mechanism confirmed but 50-step budget insufficient for HumanEval+ signal.
- Early Warning: full-374 achieves <2pp at step 50.

**Risk R5: Single-Run GRPO Initialization Variance**
- Source: A5
- Severity: Medium | Likelihood: High
- Affected: H-M4
- Description: Single-run GRPO training has high variance in final HumanEval+ pass@1; a 1pp gap between conditions may not be reproducible.
- Mitigation:
  1. Prevention: Use frac_reward_zero_std (P2) as primary mechanistic evidence, more robust to single-eval noise.
  2. Detection: Multi-checkpoint evaluation (10, 20, 50) shows trajectory, not just endpoint.
  3. Response: Report P2 as primary evidence; P1 as directional evidence; explicitly note single-run limitation.
- Early Warning: HumanEval+ pass@1 fluctuates >2pp between consecutive checkpoints.

### 6.3 Baseline Failure Patterns → Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| Random-50 includes ~31% informative problems | R5: gap too small to detect | Pre-specify 1pp minimum gap threshold |
| Full-374 may overwhelm 7B model in 50 steps | R4: noise floor issue | Use full-374 as ceiling, not comparison baseline |
| Sun et al. on math (not code) | Generalizability | Scope explicitly to code generation; mark as separate contribution |

### 6.4 Risk Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Risks: 0
High Risks: 2 (R2: degenerate distribution, R3: proxy degradation)
Medium Risks: 3 (R1: ranking instability, R4: noise floor, R5: init variance)
Low Risks: 0

All risks mapped to hypotheses with mitigation strategies.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Dialectical Analysis

### 7.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Core Claim: Variance-guided offline frozen-model profiling
concentrates GRPO gradient steps on nonzero-signal problems,
producing higher HumanEval+ pass@1 improvement per step than
random subset selection.

Supporting Evidence:
1. Mathematical identity σ=√(k(G-k))/G is exact — zero gradient
   is guaranteed for p_i∈{0,1} problems, not probabilistic
2. 69.25% zero-gradient groups at G=4 is empirically documented
   (Gradient Starvation arXiv:2605.07689)
3. Multiple independent papers (VIGOR, Sun et al., Prompt Replay,
   LZE) converge on intermediate-difficulty selection as the
   optimal GRPO strategy

Strengths:
- Mathematical foundation is exact, not a heuristic
- Mechanistic prediction (P2) independently falsifiable from
  capability prediction (P1)
- Offline profiling is novel vs all prior online methods
- Experiment produces publishable findings under any outcome

Expected Outcomes:
- P1: variance_50_improvement ≥ 2pp AND gap ≥ 1pp vs random-50
- P2: frac_reward_zero_std(variance-50) < frac_reward_zero_std(random-50)
- P3: variance-50 ≥ 80% of full-374 improvement (conditional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 7.2 Antithesis (H0-Based)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Null Hypothesis (H0): No significant difference in HumanEval+
pass@1 improvement between variance-50 and random-50 at 50
GRPO steps.

Counter-Arguments:
1. k=8 profiling introduces ranking noise at extreme p_i — the
   boundary between rank-50 and rank-51 may be statistically
   indistinguishable
2. Random-50 is not purely zero-gradient — ~31% of uniformly
   random problems have intermediate p_i and produce informative
   gradients; the advantage of variance selection may be marginal
3. 50 GRPO steps on 50 problems may be insufficient to move
   HumanEval+ pass@1 above EvalPlus noise floor (~3.9pp SE)

Potential Failure Points:
- R3: Proxy degrades by step 20; selected problems move out of
  learning zone; frac_reward_zero_std gap closes
- R4: HumanEval+ insensitive at this scale; P1 untestable
- R5: Single-run initialization variance swamps 1pp selection gap

Conditions Under Which H0 Supported:
- If frac_zero_std(variance-50) ≥ frac_zero_std(random-50) at
  any checkpoint (P2 fails → mechanism doesn't work)
- If variance_50_improvement < 2pp (P1 fails, even directionally)
- If proxy ranks are highly unstable (H-M1 fails)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 7.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Balanced Assessment:

H-VarianceGuidedRLEF-v1 presents a mathematically grounded
claim (exact σ identity) that is testable through a two-tier
evidence structure separating mechanistic evidence (P2:
frac_reward_zero_std — robust to pass@1 noise) from capability
evidence (P1: HumanEval+ pass@1). This structure resolves the
main antithesis concern: even if P1 fails due to noise floor,
P2 provides independent mechanism validation.

Resolution Path:
1. Foundation (H-E1): Verify non-degenerate MBPP variance before
   any training investment
2. Profiling validity (H-M1): Confirm selection signal is real
3. Mechanistic (H-M2, H-M3): Test gradient concentration directly
4. Capability (H-M4): Test if concentration → pass@1 improvement
5. Gates: H-E1 + H-M1 are MUST_WORK; later steps SHOULD_WORK

Outcome Scenarios:
1. Full Support: P1+P2 both pass → thesis validated
2. Mechanistic Only: P2 passes, P1 fails → mechanism confirmed,
   capability transfer needs longer training → refined thesis
3. Null: P2 fails → H0 supported → route to online selection

The verification plan is robust: any outcome is publishable.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 7.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Aspect          │ Thesis Position        │ Antithesis Challenge  │ Resolution
────────────────┼────────────────────────┼───────────────────────┼────────────
Existence       │ MBPP heterogeneous     │ 7B may be too capable │ H-E1 test
Profiling       │ k=8 stable ranking     │ Boundary noise        │ H-M1 test
Mechanism       │ Gradient concentrated  │ Proxy degrades fast   │ H-M2,3 test
Capability      │ Improvement generalizes│ Noise floor too high  │ H-M4 + P2 backup
Scope           │ Short RLEF (≤50 steps) │ Narrow applicability  │ Explicitly scoped

Overall Robustness Score: Medium-High
Confidence in Verification Plan: 0.78
Key Differentiator: Two-tier evidence (mechanistic + capability)
makes plan robust to HumanEval+ measurement noise.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 8. Executive Summary & Conclusions

### Executive Summary

**Main Hypothesis:** H-VarianceGuidedRLEF-v1 (confidence 0.78)
- Variance-guided offline MBPP subset selection outperforms random selection in short RLEF (≤50 GRPO steps) for code generation pass@1

**Verification Structure:**
- Mode: Incremental (75% scope reduction from Phase 2A BUILD_ON claims)
- Sub-Hypotheses: 5 total — H-E1 (1 existence) + H-M1–H-M4 (4 mechanism)
- Phases: 3 phases over 6 weeks
- Critical Gates: 2 MUST_WORK (H-E1, H-M1) + 3 SHOULD_WORK (H-M2, H-M3, H-M4)

**Risk Assessment:** Medium
- Primary concerns: R2 (degenerate variance), R3 (proxy degradation), R5 (single-run noise)

**Immediate Action:** Begin Phase 1 with H-E1 frozen-model profiling (374 MBPP problems, k=8 completions)

### Conclusions

**Key Achievements:**
- 5 hypotheses defined across 3 verification phases with two-tier evidence structure
- H0 explicitly addressed: mechanistic prediction (P2) provides evidence independent of HumanEval+ noise
- 75% scope reduction: 6 BUILD_ON claims skip re-verification

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: MBPP variance distribution profiling — MUST_WORK gate
- H-M1: Ranking validity check — MUST_WORK gate
- Gate 1+2: Both MUST PASS before training begins

**Phase 2: Core Mechanism** (2 weeks)
- H-M2: Gradient concentration during training (frac_reward_zero_std)
- H-M3: Proxy stability throughout 50 steps (derived from H-M2 logs)
- Gate: SHOULD_WORK — failure narrows scope, does not block

**Phase 3: Capability** (2 weeks)
- H-M4: HumanEval+ pass@1 improvement (EvalPlus evaluation)
- Gate: SHOULD_WORK — P2 backup if P1 fails

**Critical Decision Points:**

1. **Gate 1 (H-E1 Foundation):** MUST PASS
   - FAIL → STOP all training; reassess hypothesis; route Phase 0

2. **Gate 2 (H-M1 Profiling Validity):** MUST PASS
   - FAIL → PIVOT: increase k or change selection criterion

3. **Gate 3 (H-M2–H-M4 Mechanism Chain):** SHOULD_WORK
   - All pass → full hypothesis support; proceed Phase 5
   - P2 passes, P1 fails → partial: mechanism confirmed, scope narrowed
   - P2 fails → ABANDON; H0 supported; route Phase 0

**Open Questions:**
- What is the actual p_i distribution shape across MBPP for DeepSeek-Coder-7B-Instruct?
- How quickly does the frozen-model variance ranking degrade during GRPO training?
- Is k=8 stable enough that rank-50 and rank-51 don't swap on re-profiling?
- Does the variance-selection advantage hold for Code-LLaMA-7B? (stretch goal)

**Recommendations:**

1. Immediate Actions:
   - Run H-E1 profiling before any training investment
   - Set up frac_reward_zero_std logging in TRL before first training run

2. Resource Allocation:
   - 6 weeks total; allocate 2-week buffer for unexpected failures
   - Profiling (~19 min) is cheap; run H-E1 first to gate all training

3. Failure Management:
   - Document all failures with specific gate results
   - Report P2 even if P1 fails — mechanistic finding is independently publishable

### Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-VarianceGuidedRLEF-v1)
- Discussion: 12 exchanges, 14 citations, 6 convergence criteria met

**B. MCP Tool Usage Summary**
- Total MCP calls: 6 (2× scientificmethod H-E1+H-M, 1 additional for mechanism; 3× structuredargumentation thesis/antithesis/synthesis)
- Scope reduction applied: 75% (6 of 8 claims BUILD_ON)

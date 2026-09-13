---
hypothesis_title: "Difficulty-Stratified Curriculum GRPO: Reward Density Mediation in Execution-Feedback Code LLM Training"
hypothesis_id: "H-CurriculumGRPO-v1"
confidence_level: 0.75
total_hypothesis_count: 4
date: "2026-05-02"
research_scope_mode: "incremental"
scope_reduction_percentage: 43
causal_chain_count: 3
condition_hypothesis_count: 0
total_duration: "5 weeks"
phase_count: 2
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
completedAt: "2026-05-02T00:00:00"
---

# Verification Plan: Difficulty-Stratified Curriculum GRPO: Reward Density Mediation in Execution-Feedback Code LLM Training

**Date:** 2026-05-02
**Hypothesis ID:** H-CurriculumGRPO-v1
**Confidence:** 0.75
**Total Hypotheses:** 4
**Research Mode:** Incremental (43% scope reduction from Phase 2A established facts)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under DeepSeek-Coder-7B trained with GRPO and unit-test execution reward on APPS+CodeContests,
if training data is ordered easy→hard by APPS difficulty tiers (fixed split: steps 0-2500 from
tiers 0-2, steps 2501-5000 from tiers 3-4), then final pass@1 on HumanEval+ and MBPP+ is
significantly higher than uniform random sampling from the same dataset, because easy problems
during early training maintain higher reward density (fraction of non-degenerate GRPO steps),
producing informative group-relative advantage estimates and more effective policy gradient updates.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in final pass@1 on HumanEval+ or MBPP+ between any of the
difficulty conditions (easy-only, hard-only, uniform random, easy→hard curriculum) when trained
for equal compute budgets (5000 gradient steps) with GRPO on APPS+CodeContests.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | APPS + CodeContests (standard) | APPS provides pre-labeled difficulty tiers (integers 0-4) enabling clean difficulty stratification. CodeContests provides Div. 1/2 labels. Both confirmed to work with GRPO in H-E1. |
| **Model** | DeepSeek-Coder-7B-base | Confirmed working with TRL GRPOTrainer in H-E1. Fits on single A100 80GB. Open-weight, fully reproducible. |

**Dataset Details:**
- Source: hendrycks/apps (HuggingFace), google-deepmind/code_contests (GitHub)
- Path: Standard HuggingFace datasets API / local cache

**Model Details:**
- Type: Decoder-only transformer, 7B parameters
- Source: deepseek-ai/DeepSeek-Coder-7B-base (HuggingFace)

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Uniform GRPO on APPS+CodeContests | H-E1 validated: measurable pass@1 improvement over base model | APPS+CodeContests → HumanEval+/MBPP+ | Does not study difficulty composition effects; uniform sampling is the status quo this hypothesis challenges. |
| CodeRL (Le et al. 2022) | State-of-art at time of publication on APPS benchmark | APPS | RL+execution reward on APPS but no difficulty stratification; does not measure reward density. |
| RLEF (Gehring et al. 2024) | Outperforms SFT/RLHF baselines on code generation | HumanEval, MBPP, APPS | No difficulty curriculum analysis; training data composition not a research variable. |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | APPS difficulty tiers (0-4) correlate with DeepSeek-Coder-7B actual solve rate at start of training | APPS tiers from competitive programming difficulty ratings; H-E1 confirmed model engages with APPS | If tier 0-2 also too hard, curriculum's early phase provides no advantage; P1 likely fails |
| A2 | Reward density during early training is causally responsible (not merely correlated) with final pass@1 differences | GRPO theory: degenerate steps mathematically contribute zero gradient; H-M1 empirically confirmed | If reward density equal but pass@1 differs, mechanism claim wrong but empirical finding holds; paper attributes to problem semantic content |
| A3 | Fixed 50/50 compute split (2500 easy / 2500 hard steps) is a reasonable operationalization of curriculum | Fixed split is simplest reproducible implementation; mechanistic prediction should hold for any reasonable split | If split ratio dominates results, finding sensitive to curriculum schedule hyperparameter; requires additional ablation |
| A4 | Policy improvements from GRPO on competitive programming transfer to function-level benchmarks | H-E1 validated this transfer for uniform GRPO training | If curriculum improves APPS but not HumanEval+/MBPP+, distribution shift concern realized; finding domain-specific |
| A5 | 5000 gradient steps sufficient to observe meaningful differences between conditions | H-E1 showed measurable improvement at this compute budget | If insufficient, experiment may need longer runs; compute scope issue, not theoretical failure |

### 1.6 Research Gap & Novelty

**Gap:** No prior work has systematically ablated training data difficulty composition for execution-feedback GRPO code training. CodeRL (2022), RLEF (2024), and DeepSeek-R1 (2025) all use fixed dataset mixtures without difficulty stratification or reward density analysis.

**Novelty (three-level contribution):**
1. **Empirical:** First systematic ablation of difficulty composition for GRPO code training
2. **Mechanistic:** First reward density/entropy measurement stratified by difficulty condition with time-series mediation analysis
3. **Guidance:** Practical heuristic — select training problems where model solve rate ≈ 10-40% (Goldilocks zone for GRPO gradient informativeness)

**Key innovation:** First instantiation of Bengio et al. 2009 curriculum learning theory in GRPO execution-feedback RL for code generation.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status | Source |
|----|------|------|---------------|--------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY | SH1 (Phase 2A) |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED | Causal Step 1 (Phase 2A) |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED | Causal Step 2 (Phase 2A) |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED | Causal Step 3 (Phase 2A) |

---

### 2.2 Hypothesis Specifications

---

**H-E1: Curriculum GRPO Existence — Easy→Hard Ordering Improves pass@1**

**Type:** EXISTENCE
**Statement:** Under DeepSeek-Coder-7B trained with GRPO and unit-test execution reward on APPS+CodeContests for 5000 gradient steps, if training data is ordered easy→hard (APPS tiers 0-2 for steps 0-2500, tiers 3-4 for steps 2501-5000), then final pass@1 on HumanEval+ (164 problems) is at least 2 percentage points higher than uniform random sampling, as measured by McNemar's test (p < 0.05, one-tailed).

**Rationale:**
This is the primary existence claim: demonstrating that curriculum ordering produces a measurable, statistically significant improvement over the uniform sampling status quo (used by CodeRL, RLEF, DeepSeek-R1). Without this, the downstream mechanism hypotheses are moot. It directly addresses the PROVE_NEW claim that easy→hard curriculum GRPO improves final pass@1 over uniform sampling.

**Variables:**
- Independent: Training data difficulty ordering condition (easy→hard curriculum vs. uniform random)
- Dependent: pass@1 on HumanEval+ (primary, 164 problems) and MBPP+ (secondary, 378 problems) via EvalPlus harness
- Controlled: Base model (DeepSeek-Coder-7B-base), TRL GRPOTrainer G=8, 5000 steps, same APPS+CodeContests pool, same EvalPlus harness settings

**Verification Protocol:**
1. Train 4 conditions (easy-only, hard-only, uniform, easy→hard curriculum) for 5000 steps each on APPS+CodeContests with identical H-E1 hyperparameters (same learning rate, batch size, optimizer).
2. Save checkpoint every 500 steps (10 checkpoints per condition); evaluate each checkpoint on HumanEval+ (164 problems) using EvalPlus greedy decoding.
3. At final checkpoint, evaluate all 4 conditions on MBPP+ (378 problems) as secondary measure.
4. Apply McNemar's test (paired, one-tailed) comparing curriculum vs. uniform on HumanEval+ correct/incorrect per-problem vector.
5. Record curriculum pass@1, uniform pass@1, absolute difference, and McNemar's p-value.

**Success Criteria:**
- Primary: Curriculum HumanEval+ pass@1 ≥ uniform pass@1 + 2pp AND McNemar's p < 0.05 (one-tailed)
- Secondary: Curriculum MBPP+ pass@1 ≥ uniform MBPP+ pass@1 (directional, p < 0.05)

**Failure Response:**
- IF fails (curriculum < uniform + 2pp or p ≥ 0.05): PIVOT — re-examine whether A1 (tier difficulty correlation) held; check if easy-only outperformed both (easy-ceiling scenario); document as scope limitation and escalate to Phase 2A-Dialogue for hypothesis revision

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1, Prediction P1

---

**H-M1: Reward Density Mechanism — Difficulty Composition Determines Per-Step Reward Density**

**Type:** MECHANISM
**Statement:** Under the same 4-condition training setup as H-E1, if training data contains a higher fraction of APPS tier 0-2 problems during early training (steps 0-2500), then reward density (fraction of GRPO batches where max(rewards_per_group) > 0) is measurably higher in the curriculum condition than in the uniform condition during those steps, because GRPO advantage formula A_i = (r_i − mean) / std → 0 when all G=8 completions fail (std=0), and easier problems yield higher completion success rates.

**Rationale:**
This tests the first causal step: the mathematically guaranteed mechanism that difficulty composition controls reward density. The GRPO advantage collapse was empirically confirmed at repo level (H-M1 from prior pipeline run, ~85% degenerate steps). This hypothesis measures whether the same mechanism operates at function level stratified by difficulty tier. It is MUST_WORK because it is the mechanistic foundation for H-M2 and H-M3.

**Variables:**
- Independent: Training data difficulty ordering condition (curriculum vs. uniform, first 2500 steps)
- Dependent: Reward density = fraction of training batches where max(rewards_per_group) > 0, logged per checkpoint
- Controlled: Same as H-E1; reward density logged from TRL GRPOTrainer per-batch reward output (zero additional cost)

**Verification Protocol:**
1. From the 4-condition training runs executed in H-E1, extract per-batch reward logs for all 10 checkpoints (every 500 steps).
2. Compute reward density per checkpoint per condition: count batches where max(G=8 rewards) > 0, divided by total batches in that interval.
3. Compute mean reward density for steps 0-2500 (checkpoints 1-5) for curriculum vs. uniform conditions.
4. Test: mean reward density (curriculum, steps 0-2500) > mean reward density (uniform, steps 0-2500) using one-tailed Wilcoxon signed-rank test across 5 checkpoint observations.
5. Plot reward density time series for all 4 conditions to visualize divergence pattern.

**Success Criteria:**
- Primary: Mean reward density in curriculum condition steps 0-2500 > mean reward density in uniform condition steps 0-2500 (one-tailed p < 0.05)
- Secondary: Reward density in easy-only condition ≥ curriculum early phase (confirming tier-difficulty correlation assumption A1)

**Failure Response:**
- IF fails (no reward density difference between curriculum and uniform): EXPLORE — check if A1 violated (tier 0-2 problems also too hard for model at init); if so, document as assumption failure; paper can still report H-E1 empirical finding with different mechanistic attribution (problem coverage rather than gradient quality)

**Dependencies:** H-E1 (must confirm existence before mechanism attribution)

**Source:** Phase 2A Causal Step 1, Assumption A2

---

**H-M2: Gradient Signal Mechanism — Higher Reward Density Produces More Informative Advantage Estimates**

**Type:** MECHANISM
**Statement:** Under the 4-condition training setup, if reward density (non-degenerate batch fraction) is higher in the curriculum condition during steps 0-2500 (as verified by H-M1), then reward entropy H(p) of the G=8 reward distribution per batch is also higher in the curriculum condition during early training, and the Pearson correlation between checkpoint reward density at step T and subsequent pass@1 gain from step T to T+500 is r > 0.5 across all 4 conditions.

**Rationale:**
This tests the second causal step: that higher reward density translates to more informative gradient signal, measured via reward entropy and checkpoint-level pass@1 gain correlation. Reward entropy H(p) is richer than binary reward density — it captures the Goldilocks zone (≈4/8 successes = maximum variance in G=8 advantage estimates). The time-series correlation avoids the circularity concern raised by Prof. Rex: we measure reward density at step T predicting gain from T to T+500, not same-step correlation.

**Variables:**
- Independent: Reward density per checkpoint (continuous, computed from H-M1)
- Dependent: (a) Reward entropy H(p) of G=8 reward distribution per batch; (b) pass@1 gain per checkpoint interval
- Controlled: Same checkpoints as H-E1/H-M1; Pearson correlation computed across all 40 checkpoint observations (10 checkpoints × 4 conditions)

**Verification Protocol:**
1. From H-E1 training logs, compute reward entropy H(p) = -Σ p_i log p_i for the G=8 reward distribution at each of the 10 checkpoints per condition (p_i = fraction of completions with reward = i/G).
2. Compute pass@1 gain per 500-step interval: gain(T) = pass@1(T+500) − pass@1(T) for each checkpoint.
3. Compute Pearson correlation r between reward density at step T and pass@1 gain from T to T+500, pooling all 40 observations (10 checkpoints × 4 conditions).
4. Separately verify: mean reward entropy in curriculum condition steps 0-2500 > mean reward entropy in uniform condition steps 0-2500.
5. Report scatter plot of reward density vs. subsequent pass@1 gain with regression line and r value.

**Success Criteria:**
- Primary: Pearson r > 0.5 between checkpoint reward density and subsequent pass@1 gain (pooled across conditions and checkpoints)
- Secondary: Mean reward entropy in curriculum early phase > mean reward entropy in uniform early phase

**Failure Response:**
- IF r ≤ 0.5 but H-E1 passes: SCOPE — document that reward density mediates performance at a weaker rate than predicted; paper can still claim empirical existence finding (P1) with qualified mechanistic interpretation; no PIVOT needed

**Dependencies:** H-M1 (reward density difference must be established)

**Source:** Phase 2A Causal Step 2, Prediction P2

---

**H-M3: Generalization Mechanism — Effective Early Gradients Produce Higher Final Benchmark pass@1**

**Type:** MECHANISM
**Statement:** Under the 4-condition training setup, the curriculum condition (which has higher reward density during early training per H-M1, and higher reward entropy correlation per H-M2) achieves higher pass@1 than the uniform condition on the APPS test split (within-domain) at the final checkpoint (step 5000), confirming that better early gradient signal generalizes beyond the training distribution.

**Rationale:**
This tests the third causal step: that more effective early policy updates from better-quality gradients generalize to unseen problems both within-domain (APPS test split, harder competition problems) and motivates the cross-domain finding in H-E1. The APPS test split evaluation tests within-domain transfer — if curriculum improves both HumanEval+/MBPP+ (cross-domain, H-E1) and APPS test split (within-domain, H-M3), the mechanism generalizes beyond domain artifacts, directly addressing Prof. Rex's distribution shift concern.

**Variables:**
- Independent: Training condition (curriculum vs. uniform at step 5000)
- Dependent: pass@1 on APPS test split using standard APPS evaluation harness
- Controlled: Same final checkpoints from H-E1/H-M1/H-M2 runs; APPS evaluation harness settings consistent

**Verification Protocol:**
1. Take final checkpoints (step 5000) from all 4 conditions from the H-E1 training runs.
2. Evaluate each final checkpoint on APPS test split using the standard APPS evaluation harness (not EvalPlus).
3. Apply one-tailed test comparing curriculum vs. uniform APPS test split pass@1.
4. Also evaluate on LiveCodeBench (contamination-free, harder benchmark) as an additional secondary measure.
5. Report APPS test split pass@1 for all 4 conditions and statistical test result.

**Success Criteria:**
- Primary: Curriculum APPS test split pass@1 > uniform APPS test split pass@1 (one-tailed p < 0.05)
- Secondary: Curriculum LiveCodeBench pass@1 ≥ uniform LiveCodeBench pass@1 (directional)

**Failure Response:**
- IF fails (no within-domain transfer): SCOPE — curriculum may improve cross-domain benchmarks (HumanEval+/MBPP+) but not within-domain; this suggests distribution shift dominates over gradient quality for APPS test split; paper scopes finding to function-level benchmarks; does not invalidate H-E1 or H-M1/H-M2

**Dependencies:** H-M2 (mechanism chain must be established)

**Source:** Phase 2A Causal Step 3, Prediction P3

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Curriculum HumanEval+ pass@1 ≥ uniform + 2pp AND McNemar's p < 0.05 | STOP pipeline; reassess hypothesis; route to Phase 2A-Dialogue |
| H-M1 | MUST_WORK | Curriculum reward density steps 0-2500 > uniform reward density (p < 0.05) | EXPLORE assumption A1/A2; paper can still report H-E1 with different mechanism attribution |
| H-M2 | SHOULD_WORK | Pearson r > 0.5 (reward density → subsequent pass@1 gain) | SCOPE; qualified mechanistic claim; H-E1 empirical finding still valid |
| H-M3 | SHOULD_WORK | Curriculum APPS test split pass@1 > uniform (p < 0.05) | SCOPE; curriculum scoped to function-level benchmarks only |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 3 weeks (1 week each after first) |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Tier Difficulty Mismatch (Source: A1)**
- **Description:** APPS difficulty tiers 0-4 may not correlate with DeepSeek-Coder-7B's actual solve rate at training start. If tier 0-2 problems are also too hard for the 7B model, the curriculum's early phase provides no reward density advantage.
- **Severity:** High | **Likelihood:** Medium
- **Affected Hypotheses:** H-E1 (primary outcome at risk), H-M1 (reward density premise fails)
- **Mitigation:**
  1. Prevention: Log reward density separately for easy-only condition during first 500 steps; if reward density < 10%, flag assumption violation early
  2. Detection: Compare easy-only vs. hard-only reward density in first checkpoint (step 500); divergence confirms tier-difficulty correlation
  3. Response: If violated → PIVOT to adaptive difficulty selection (Dr. Nova's proposal) or focus paper on APPS test split within-domain results only

**Risk R2: Reward Density ≠ Causation (Source: A2)**
- **Description:** Reward density during early training may be correlated with, not causally responsible for, final pass@1 differences. The confound is problem semantic content (easy problems teach generalizable syntax patterns) rather than gradient quality.
- **Severity:** Medium | **Likelihood:** Medium
- **Affected Hypotheses:** H-M2 (mediation test), H-M3 (mechanism generalization)
- **Mitigation:**
  1. Prevention: Use time-series design (reward density at T predicts gain from T to T+500) to strengthen causal inference
  2. Detection: If P2 fails (r ≤ 0.5) but P1 holds, alternative explanation is problem coverage; report both as competing mechanisms
  3. Response: SCOPE — paper presents empirical finding as primary contribution; mechanistic claim qualified; no PIVOT needed

**Risk R3: Fixed Split Sensitivity (Source: A3)**
- **Description:** The 50/50 curriculum split (2500 easy / 2500 hard steps) may be suboptimal; a different split ratio could substantially change outcomes, making the finding sensitive to the curriculum schedule hyperparameter.
- **Severity:** Low | **Likelihood:** Low
- **Affected Hypotheses:** H-E1 (effect size may vary), all H-M hypotheses
- **Mitigation:**
  1. Prevention: Frame fixed 50/50 as "representative curriculum schedule" not "optimal curriculum" in paper
  2. Detection: If H-E1 shows marginal improvement (< 2pp), consider 70/30 or 30/70 ablation as follow-up
  3. Response: SCOPE — paper notes split ratio is a hyperparameter and recommends future ablation; does not invalidate existence claim

**Risk R4: Distribution Shift (Source: A4)**
- **Description:** GRPO training on competitive programming (APPS/CodeContests) may not transfer to function-level benchmarks (HumanEval+/MBPP+) for the curriculum condition specifically, even though H-E1 validated this transfer for uniform GRPO.
- **Severity:** High | **Likelihood:** Low (H-E1 validated transfer for uniform; curriculum should preserve transfer)
- **Affected Hypotheses:** H-E1 (primary outcome), H-M3 (cross-domain generalization)
- **Mitigation:**
  1. Prevention: Include APPS test split (within-domain) evaluation as H-M3 to distinguish within- vs. cross-domain effects
  2. Detection: If curriculum improves APPS test split (H-M3) but not HumanEval+ (H-E1 fails), distribution shift is the dominant factor
  3. Response: SCOPE — paper scopes curriculum finding to within-domain; highlights APPS test split result as main contribution

**Risk R5: Compute Budget Insufficient (Source: A5)**
- **Description:** 5000 gradient steps may be insufficient to observe statistically significant differences between difficulty conditions, particularly if the curriculum effect is small or requires more steps to manifest.
- **Severity:** Medium | **Likelihood:** Low (H-E1 showed measurable effects at same budget)
- **Affected Hypotheses:** All hypotheses (all tested at same compute budget)
- **Mitigation:**
  1. Prevention: Log pass@1 at each of 10 checkpoints; early divergence curves indicate effect will be detectable at 5000 steps
  2. Detection: If checkpoint curves show no divergence by step 2500, extend to 7500 steps for curriculum and uniform conditions only
  3. Response: If effect requires more compute → SCOPE; report directional finding and note extended training as future work

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Priority |
|------|--------|---------------------|----------|----------|
| R1: Tier Difficulty Mismatch | A1 | H-E1, H-M1 | High | 1 |
| R2: Reward Density ≠ Causation | A2 | H-M2, H-M3 | Medium | 2 |
| R3: Fixed Split Sensitivity | A3 | H-E1, H-M* | Low | 4 |
| R4: Distribution Shift | A4 | H-E1, H-M3 | High | 1 |
| R5: Compute Budget | A5 | All | Medium | 3 |

**Critical Risks:** 0 | **High:** 2 (R1, R4) | **Medium:** 2 (R2, R5) | **Low:** 1 (R3)

### 4.3 Baseline Failure Pattern Analysis

| Baseline Limitation | Risk Derived | Mitigation |
|--------------------|--------------|------------|
| CodeRL: uniform APPS sampling only | R1 — if model can't learn from easy problems, curriculum gives no advantage | Early reward density logging at checkpoint 1 |
| RLEF: no difficulty curriculum | R2 — difficulty may matter but not via reward density | Time-series mediation test (P2 design) |
| DeepSeek-R1: fixed training mix | R4 — distribution shift may dominate curriculum effect | H-M3 within-domain APPS test split evaluation |

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1: Existence — Curriculum improves pass@1
         │  MUST_WORK gate
         ▼
[Level 1 - Core Mechanism: Reward Density]
    H-M1: Difficulty composition → reward density
         │  MUST_WORK gate
         ▼
[Level 2 - Mechanism: Gradient Signal]
    H-M2: Reward density → gradient informativeness
         │  SHOULD_WORK gate
         ▼
[Level 3 - Mechanism: Generalization]
    H-M3: Gradient quality → APPS test split pass@1
             SHOULD_WORK gate

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Levels: 4 | All Sequential (no parallelization)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type | Fail Action |
|-------|-----------|---------------|-----------|-------------|
| 0 | H-E1 | None | MUST_WORK | STOP → Phase 2A-Dialogue |
| 1 | H-M1 | H-E1 | MUST_WORK | EXPLORE → qualified mechanism claim |
| 2 | H-M2 | H-M1 | SHOULD_WORK | SCOPE → empirical finding stands |
| 3 | H-M3 | H-M2 | SHOULD_WORK | SCOPE → function-level scope only |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses | 5 Weeks Total
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis   │ W1-2     │ W3-4     │ W5       │
───────────────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation
  H-E1             │ ████████ │          │          │
  [Gate 1]         │        ◆ │          │          │
───────────────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms
  H-M1             │          │ ████████ │          │
  H-M2             │          │          │ ████     │
  H-M3             │          │          │     ████ │
  [Gate 2]         │          │          │         ◆│
───────────────────┼──────────┼──────────┼──────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
Note: H-M1 logs data from H-E1 training runs (zero additional GPU time).
      H-M2 and H-M3 are analysis-only steps using H-E1 checkpoint data.
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 5 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 0.5 (H-M2) + 0.5 (H-M3)

Note on GPU efficiency:
  H-E1 requires ~9 GPU-days (4 conditions × ~14h on single A100 80GB)
  H-M1, H-M2, H-M3: analysis-only (reward logs + checkpoint evals already
  collected in H-E1 runs); negligible additional GPU compute.

Slack Available: 0 weeks (all sequential)
Bottleneck: H-E1 training (GPU compute)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0 (not needed)

Verification Phases: 2
1. Foundation (H-E1): ~9 GPU-days, 2 weeks
2. Mechanisms (H-M1-3): analysis-only from H-E1 logs, 3 weeks

GPU Compute: ~9 GPU-days (4 × 5000 steps × ~14h/condition on A100 80GB)
Evaluation overhead: ~4h per condition final eval (EvalPlus + APPS test split)
Total: ~10-11 GPU-days

Critical Path Length: 5 weeks
Execution Mode: Sequential (H-M* reuse H-E1 data)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
  → Train 4 conditions × 5000 steps with checkpoint logging
  → Collect reward density, reward entropy, and pass@1 per checkpoint
  → Evaluate final checkpoints on HumanEval+ (primary) and MBPP+

Step 2: Evaluate Gate 1 (H-E1 MUST_WORK) — End of Week 2
  → Curriculum HumanEval+ pass@1 ≥ uniform + 2pp AND McNemar's p < 0.05?
  → PASS → proceed to Phase 2
  → FAIL → STOP, document, route to Phase 2A-Dialogue

Step 3: Execute H-M1 (Reward Density Analysis) — Week 3-4
  → Analyze per-batch reward logs from H-E1 runs
  → Compute reward density per checkpoint per condition
  → One-tailed Wilcoxon test: curriculum density > uniform density (steps 0-2500)

Step 4: Execute H-M2 (Gradient Signal Analysis) — Week 5 (first half)
  → Compute reward entropy H(p) per checkpoint
  → Compute Pearson r (reward density at T → pass@1 gain T to T+500)
  → r > 0.5 across all 40 checkpoint observations?

Step 5: Execute H-M3 (APPS Test Split Generalization) — Week 5 (second half)
  → Evaluate all 4 final checkpoints on APPS test split
  → Optional: evaluate on LiveCodeBench
  → One-tailed test: curriculum APPS test pass@1 > uniform?

Step 6: Evaluate Gate 2 (H-M1 MUST_WORK) — End of Week 5
  → H-M1 passed? → document limitation if failed, proceed to synthesis
  → H-M2/H-M3 SHOULD_WORK failures → scope claim, document, proceed

Final: Verification complete → Phase 2C experiment design for each hypothesis
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Core Claim: Easy→hard curriculum GRPO training (fixed 50/50 split, APPS tiers 0-2 → 3-4) achieves
significantly higher pass@1 than uniform sampling on HumanEval+ and MBPP+, mediated by reward density.

Supporting Evidence:
1. GRPO theory (mathematical): advantage formula A_i = (r_i − mean)/std → 0 when std=0 (all fail).
   Easy problems prevent this collapse during early training — this is not speculative but guaranteed.
2. H-M1 prior evidence: ~85% degenerate steps in repo-level GRPO confirmed reward density collapse
   at scale. Function-level analog with difficulty stratification is natural extension.
3. Curriculum learning theory (Bengio et al. 2009): easy→hard ordering improves convergence in
   supervised learning; first instantiation in execution-feedback RL setting.

Strengths:
- Mechanistically grounded: advantage collapse is mathematically guaranteed, not hypothesized
- Infrastructure confirmed from H-E1: all code, hardware, datasets, harness already validated
- Falsifiable: explicit 2pp threshold, McNemar's test, r > 0.5 criterion — nothing vague
- Scope-honest: excludes repo-level (H-M1 failed there), dynamic curriculum (separate hypothesis)

Expected Outcomes:
- P1: Curriculum HumanEval+ pass@1 ≥ uniform + 2pp (McNemar's p < 0.05)
- P2: Checkpoint reward density predicts subsequent pass@1 gain (r > 0.5)
- P3: Curriculum APPS test split pass@1 > uniform (p < 0.05)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Null Hypothesis (H0): There is no significant difference in final pass@1 on HumanEval+ or MBPP+
between any of the four difficulty conditions at equal compute (5000 steps) with GRPO on
APPS+CodeContests.

Counter-Arguments:
1. Easy-ceiling concern (Prof. Rex): HumanEval+ and MBPP+ test function-level Python — semantically
   closer to APPS tiers 0-2 than tiers 3-4 (competitive programming). Easy-only training may achieve
   comparable or higher pass@1 on these benchmarks than curriculum, leaving curriculum's advantage unclear.
2. Distribution shift (Prof. Rex): APPS training (competitive programming) ≠ HumanEval+/MBPP+ eval
   (general Python function-level). Any curriculum effect may reflect problem distribution artifacts,
   not gradient quality improvements.
3. Fixed split fragility (A3): A 50/50 curriculum split is arbitrary. Different split ratios could
   yield different results; the 2pp threshold may be sensitive to this choice.

Potential Failure Points:
- R1: APPS tier 0-2 problems too hard for 7B model at init → no reward density advantage → P1 fails
- R2: Reward density correlation (P2) may be spurious — problem content (not gradient quality) drives pass@1
- R4: Distribution shift dominates → curriculum improves APPS test split but not HumanEval+/MBPP+

Conditions Under Which H0 Would Be Supported:
- If curriculum pass@1 < uniform + 2pp (P1 falsified)
- If reward density equal across conditions in early training (H-M1 mechanism absent)
- If easy-only outperforms curriculum on HumanEval+ (easy-ceiling dominates)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Balanced Assessment:
The hypothesis H-CurriculumGRPO-v1 presents a testable, mechanistically grounded claim that
easy→hard curriculum ordering systematically improves GRPO training efficiency through reward
density optimization. The antithesis raises legitimate concerns: the easy-ceiling scenario and
distribution shift are empirically unresolved, and the 50/50 split is an arbitrary hyperparameter.

Resolution Path:
The verification plan directly addresses this dialectic:
1. Foundation (H-E1): Tests existence with explicit 2pp threshold and McNemar's test — unambiguous
   falsification criterion that avoids vague "improvement" claims.
2. Mechanism (H-M1): Measures reward density separately for all 4 conditions — if easy-only ≥
   curriculum in reward density, easy-ceiling concern is empirically confirmed.
3. Mechanism (H-M2): Time-series mediation test (reward density at T → gain T to T+500) avoids
   circularity concern by using non-contemporaneous correlation.
4. Mechanism (H-M3): Within-domain APPS test split evaluation distinguishes distribution shift from
   genuine gradient improvement.

Conditions for Thesis Support:
- H-E1 MUST_WORK gate passes (curriculum ≥ uniform + 2pp, McNemar's p < 0.05)
- H-M1 MUST_WORK gate passes (curriculum reward density > uniform early training)
- H-M2 Pearson r > 0.5 confirmed

Conditions for Antithesis Support:
- H-E1 fails (no significant pass@1 improvement) → H0 supported
- H-M1 fails (no reward density difference) → mechanism absent, H0 supported for reward-density claim
- Easy-only condition outperforms curriculum on HumanEval+ → easy-ceiling dominates

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-M1 + H-M2 + H-M3 all pass → Three-level contribution validated
2. Partial Support (most likely): H-E1 + H-M1 pass, H-M2/H-M3 partial → Empirical finding
   + reward density mechanism confirmed; generalization scope defined
3. Easy-Ceiling Scenario: Easy-only ≥ curriculum on HumanEval+ → Interesting finding:
   problem difficulty distribution (not curriculum ordering) is the key variable; paper reframes
4. No Support: H-E1 fails → Hypothesis fundamentally wrong; route to Phase 2A-Dialogue for revision
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Curriculum improves pass@1 ≥ 2pp vs. uniform | Easy-only may match or exceed curriculum | H-E1 test: explicit threshold + all 4 conditions measured |
| Mechanism (Reward Density) | Higher density in early curriculum phase (mathematically guaranteed) | Density may equal uniform if tiers not discriminative | H-M1 test: separate per-condition reward density logs |
| Mechanism (Gradient Quality) | Reward entropy predicts pass@1 gain (r > 0.5) | Semantic content of easy problems drives gain, not gradient quality | H-M2: time-series Pearson correlation (non-contemporaneous) |
| Generalization | Better gradients generalize to APPS test split | Distribution shift prevents cross-domain transfer | H-M3: within-domain APPS test split evaluation |
| Scope | Fixed 50/50 split is representative | Split ratio is arbitrary; findings not generalizable | Framed as representative schedule; ablation left for future work |

**Overall Robustness Score:** High (mechanistic guarantee on reward density collapse + established H-E1 infrastructure)
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Easy→hard curriculum GRPO (fixed split, APPS tiers) achieves significantly higher pass@1 than uniform sampling on HumanEval+ and MBPP+, mediated by reward density.
- ID: H-CurriculumGRPO-v1 | Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (43% scope reduction — 4 BUILD_ON facts from H-E1/H-M1 cited as prior)
- Sub-Hypotheses: 4 total (H-E1: existence, H-M1-3: mechanism chain)
- Phases: 2 phases over 5 weeks | Gate 1 (H-E1 MUST_WORK) + Gate 2 (H-M1 MUST_WORK)
- GPU compute: ~9 GPU-days (H-M1/2/3 are analysis-only, reusing H-E1 training data)

**Risk Assessment:** Medium
- Primary concerns: R1 (tier difficulty mismatch) and R4 (distribution shift) — both High severity but Low-Medium likelihood given H-E1 infrastructure validation

**Immediate Action:** Begin Phase 2C experiment design for H-E1 (start with Foundation hypothesis)

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases with full mechanism chain from difficulty composition to benchmark performance
- H0 clearly addressed: no significant difference in pass@1 across 4 difficulty conditions
- Efficient design: H-M1/2/3 reuse H-E1 training infrastructure (zero marginal GPU cost for mechanism analysis)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Easy→hard curriculum GRPO achieves ≥ 2pp HumanEval+ improvement vs. uniform (McNemar's p < 0.05)
- Gate 1: MUST PASS — if fails, STOP and route to Phase 2A-Dialogue

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Curriculum reward density (steps 0-2500) > uniform reward density — Gate: MUST_WORK
- H-M2: Pearson r > 0.5 (reward density → subsequent pass@1 gain across checkpoints) — Gate: SHOULD_WORK
- H-M3: Curriculum APPS test split pass@1 > uniform — Gate: SHOULD_WORK
- Gate 2: H-M1 must pass; H-M2/H-M3 failures narrow scope but don't invalidate

**Critical Decision Points:**
1. Gate 1 (H-E1): MUST_WORK — fail → STOP + Phase 2A-Dialogue
2. Gate 2 (H-M1): MUST_WORK — fail → EXPLORE assumption A1/A2; paper scopes mechanistic claim
3. H-M2/H-M3 failures → SCOPE — empirical existence finding (H-E1) remains valid

**Open Questions (from Phase 2A):**
- Optimal curriculum split ratio (50/50 vs. other splits) — not explored; future work
- Reward density sweet spot generalization across model sizes — future work
- Whether dynamic difficulty selection (Dr. Nova's proposal) further improves over fixed-split curriculum — separate hypothesis
- Interaction between curriculum ordering and the model's pretraining data distribution

**Recommendations:**
1. **Immediate Actions:** Start Phase 2C with H-E1; set up TRL GRPOTrainer with custom dataset sampler and per-batch reward logging in one training run
2. **GPU Allocation:** Reserve single A100 80GB for ~10-11 GPU-days; all 4 conditions can be run sequentially on same GPU with checkpoint saving
3. **Data Collection:** Instrument H-E1 run to collect reward density, reward entropy per batch from the start — no second training pass needed for H-M1/2
4. **Early Warning:** Monitor easy-only reward density at step 500 checkpoint — if ≤ 10%, flag A1 assumption risk immediately and notify before committing full compute

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `03_refinement.yaml` (ID: H-CurriculumGRPO-v1, generated 2026-05-02)
- Supplementary: `02_synthesis.yaml`, `01_round_table/final_opinions.yaml`
- Convergence: All 6 criteria met at exchange 15; VALIDATED status; all 6 personas participated

**B. MCP Tool Usage Summary**
- MCP services: Unavailable (no-mcp environment)
- Scientific method reasoning: 2 calls performed inline (LLM-native)
- Tools used: LLM reasoning for hypothesis generation and scientific method stages

**C. Scope Reductions Applied**
- BUILD_ON (not re-verified): H-E1 infrastructure (TRL GRPOTrainer, DeepSeek-Coder-7B-base, APPS tiers, EvalPlus), GRPO advantage collapse mechanism (H-M1 prior), dataset metadata
- PROVE_NEW (new hypotheses generated): difficulty composition ablation, curriculum ordering benefit, reward density mediation

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-05-02 | UNATTENDED mode*

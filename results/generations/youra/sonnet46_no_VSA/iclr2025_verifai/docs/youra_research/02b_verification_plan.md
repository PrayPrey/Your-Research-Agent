# Verification Plan: Execution-Based Contract Strength Gap — Cross-Model Measurement on ContractEval

**Date:** 2026-08-03
**Hypothesis ID:** H-ContractStrength-v2
**Confidence:** 0.72
**Total Hypotheses:** 5
**Research Mode:** Incremental (Phase 2A available, 43% scope reduction applied)
**Steps Completed:** step-00-init-environment, step-01-init-parsing, step-02-input-hypothesis, step-03-hypothesis-generation, step-04-hypothesis-inventory

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under ContractEval's 364 HumanEval+/MBPP+ tasks, if LLM-generated programs that pass all unit tests are evaluated via execution-based contract checking (Hypothesis PBT with icontract-hypothesis strategy inference), then (a) the mean contract-failure rate exceeds EvalPlus matched-input differential-oracle failure rate by ≥10% absolute (with ≥5% absolute from contract-unique violations: output-equal-to-gt but contract-failing), (b) model rankings on contract-satisfaction differ from pass@1⋆ rankings with Kendall τ ≤ 0.6, and (c) contract-strength gap varies by ≥10% absolute between best and worst model families, because contracts encode universal properties (relational invariants, quantified conditions) that finite test suites cannot exhaustively check, causing LLM code that memorizes or correctly computes test-distribution outputs to systematically fail on out-of-distribution inputs that contracts specify must also hold.

### 1.2 Alternative Hypothesis (H0)

Execution-based contract checking provides no statistically significant additional signal beyond dense differential testing (EvalPlus 764-test-per-task): mean oracle-isolation gap ≤ 2%, Kendall τ ≥ 0.8 with pass@1⋆, and contract-satisfaction rate is explained by pass@1⋆ and model size (R² ≥ 0.85).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | ContractEval (HumanEval+/MBPP+ subset) (standard) | Primary benchmark containing all required contract annotations; built on HumanEval+/MBPP+ enabling direct EvalPlus integration for Experiment A oracle isolation |
| **Model** | Multi-model evaluation (5 models) | evalplus provides unified generation pipeline across all model families; supports n=10 samples per task per model |

**Dataset Details:**
- Source: github.com/suhanmen/ContractEval (5★, ACL 2026)
- Path: 364 tasks with Python pre/post-condition contracts

**Model Details:**
- Type: API (closed) + vLLM/HuggingFace (open)
- Source: evalplus/evalplus (1789★, NeurIPS 2023) with OpenAI/Anthropic/HuggingFace backends

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| EvalPlus / HUMANEVAL+ differential testing | Reduces pass@1 by up to 23.1% vs original HUMANEVAL; 2005 citations | HumanEval+/MBPP+ (80x and 35x more tests) |
| ContractEval SMT-based evaluation (Lim et al. 2025) | 0% contract satisfaction for 5 open-source LLMs under standard prompting | ContractEval subset of HumanEval+/MBPP+ (364 tasks) |
| PBT without formal contracts (Bose 2025) | 18-32% additional failures vs unit tests on StarCoder/CodeLlama | MBPP + HumanEval (not ContractEval) |

*Note: H-CP (baseline comparison) deferred to Phase 5. EvalPlus best baseline: 23.1% additional failures from dense testing.*

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | ContractEval's contracts are sound (reference implementations satisfy all contracts under high-budget PBT) | ContractEval contracts written by domain experts; Lim et al. 2025 (ACL 2026) implies manual validation | Oracle is unsound; contract failures may include false positives; cross-model comparisons unreliable → pre-experiment soundness check (100k examples, 2h per task) |
| A2 | icontract-hypothesis can infer valid Hypothesis strategies from ContractEval pre-conditions with acceptable filter rate (≥100 valid samples in fixed budget for ≥80% of tasks) | icontract-hypothesis docs; plasma-umass/evidence; h-e1 worked on tractable subset suggesting pre-conditions are well-structured | Experiment B has low effective sample size for high-filter tasks; per-task yield must be reported and low-yield tasks flagged |
| A3 | EvalPlus static inputs (764 tests/task) are available and map to ContractEval tasks (ContractEval is strict subset of HumanEval+/MBPP+) | ContractEval paper explicitly builds on HumanEval+/MBPP+; EvalPlus publishes all inputs as JSON; both benchmarks are public | Experiment A (oracle isolation) cannot run; fallback to synthetic matched inputs generated fresh |
| A4 | Model APIs (OpenAI, Anthropic) allow n=10 samples per task without prohibitive rate limiting (364 tasks × 10 samples) | evalplus/evalplus already supports OpenAI/Anthropic backends in production; standard API usage for benchmark evaluation | Reduce to n=5 samples; estimate cost impact; study proceeds with reduced statistical power |
| A5 | Contract-unique failure category (output-equal-to-gt but contract-failing) is non-empty: ≥5% of violations will fall into this category | h-e1 confirmed violations exist; ContractEval contracts encode relational/quantified properties not reducible to equality | Oracle strength claim fails: contracts are redundant with dense differential testing. Still a publishable negative result. |

### 1.6 Research Gap & Novelty

**Gap:** Cross-model contract-strength gap is unmeasured — no published study applies execution-based (non-SMT) contract checking across multiple LLM families (open + closed) on ContractEval. ContractEval (Lim et al. 2025) evaluates only 5 open-source models via Z3 (25.82% tractable).

**Key Innovation:** Oracle isolation experiment using EvalPlus's published 764-test static inputs re-evaluated under contract oracle — cleanly separates oracle strength from adaptive search advantage using existing infrastructure. First execution-based (100% tractable) cross-model measurement on ContractEval.

**Scope Reduction (43%):** 5 claims BUILD_ON (established by h-e1 + prior work) — not re-verified. Only 3 PROVE_NEW claims drive hypothesis generation: oracle strength beyond differential testing (P1), ranking orthogonality (P2), cross-model variation (P3).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M1 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
#### H-E1: Contract-Strength Gap Existence on Full ContractEval

**Type:** EXISTENCE
**Statement:** Under ContractEval's full 364 HumanEval+/MBPP+ tasks, if LLM-generated programs that pass all unit tests are evaluated via Hypothesis PBT with icontract-hypothesis strategy inference, then a non-zero contract-strength gap exists (mean fraction of test-passing programs failing ≥1 contract > 0), because Python-native execution checking is 100% tractable and h-e1 confirmed a 7.42% violation rate on the tractable subset.

**Rationale:** h-e1 proved contracts catch test-passing failures at 7.42% on the 25.82% Z3-tractable subset. This hypothesis extends to the full 364 tasks using execution-based checking (no tractability ceiling). It is the necessary foundation: if no gap exists on the full set, all mechanism hypotheses are moot.

**Variables:**
- IV: Verification method (Hypothesis PBT + icontract-hypothesis vs. EvalPlus differential oracle)
- DV: Contract-strength gap = fraction of test-passing programs failing ≥1 contract under Hypothesis PBT
- CV: Dataset (ContractEval 364 tasks), input budget (5k examples, seed=42, 60s), models (5 families, n=10 samples)

**Verification Protocol:**
1. Oracle soundness pre-check: run Hypothesis (100k examples, 2h wall-clock) against ContractEval reference implementations; quarantine tasks with violations.
2. Generate n=10 code samples per (model, task) via evalplus backends; filter to test-passing programs only.
3. Run Hypothesis PBT + icontract-hypothesis (5k examples, seed=42, 60s) per (model, task, program) triple.
4. Compute contract-strength gap per task; aggregate mean across 364 quarantine-filtered tasks × 5 models.
5. Bootstrap 95% CI on mean gap; verify lower bound > 0.01.

**Success Criteria:**
- Primary: mean contract-strength gap > 0 across pooled results (bootstrap 95% CI lower bound > 0.01)
- Secondary: gap replicates h-e1's 7.42% lower bound on the tractable subset

**Failure Response:** IF fails → STOP all H-M hypotheses; reassess whether contracts are too weak or icontract-hypothesis filter rate is prohibitively high across full 364 tasks.

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1 (sh1_existence), h-e1 Phase 4 established facts

---

#### H-M1: Oracle Strength — Contracts Encode Universal Properties Beyond Finite Test Suites (Static Oracle Isolation)

**Type:** MECHANISM
**Statement:** Under ContractEval's 364 tasks, if test-passing LLM programs are evaluated on EvalPlus's published 764-test static inputs simultaneously under differential oracle and contract oracle, then the mean oracle-isolation gap (contract-failure rate minus differential-failure rate) ≥ 0.10 absolute with ≥ 0.05 contract-unique mass (output-equal-to-gt but contract-failing), because ContractEval pre/post-conditions encode relational invariants and quantified conditions that ground-truth equality cannot check.

**Rationale:** This is Experiment A — the key oracle isolation design. It directly tests whether contracts are semantically richer than dense differential testing using zero new data (reuses EvalPlus's published inputs). The contract-unique failure category isolates oracle strength from input generation strategy. This is the primary contribution of the study.

**Variables:**
- IV: Oracle type (differential equality oracle vs. ContractEval contract oracle) applied to identical inputs
- DV: Oracle-isolation gap = mean(contract-failure rate) − mean(differential-failure rate) on same EvalPlus static inputs; contract-unique failure mass
- CV: EvalPlus 764 static inputs per task (fixed, published), same LLM programs evaluated under both oracles

**Verification Protocol:**
1. Load EvalPlus published JSON inputs (764 tests/task for all ContractEval tasks).
2. For each test-passing LLM program, evaluate all 764 inputs under: (a) differential oracle: f(x)==gt(x); (b) contract oracle: assert pre(x); post(f(x)).
3. Classify each failure: contract-unique = {f(x)==gt(x)} AND {post(f(x)) fails}; redundant = both oracles detect.
4. Compute oracle-isolation gap per task; Wilcoxon signed-rank test across tasks with Holm correction.
5. Bootstrap 95% CI on oracle-isolation gap and contract-unique mass; verify thresholds.

**Success Criteria:**
- Primary: mean oracle-isolation gap ≥ 0.10, Wilcoxon p < 0.01 after Holm correction
- Secondary: contract-unique failure mass ≥ 0.05 with bootstrap 95% CI lower bound > 0.03

**Failure Response:** IF fails (gap ≤ 0.02 or p > 0.05) → PIVOT: investigate contract richness stratification (AST analysis); consider whether EvalPlus inputs systematically under-sample contract-failure-inducing states.

**Dependencies:** H-E1 (existence confirmed)

**Source:** Phase 2A causal step 2, prediction P1 (primary), key tension resolution

---

#### H-M2: Contract Richness Gradient — Oracle-Isolation Gap Scales with Postcondition Complexity

**Type:** MECHANISM
**Statement:** Under ContractEval's 364 tasks stratified by postcondition complexity (AST-based: quantification, relational, structural tiers), if oracle-isolation gap is regressed on contract richness tier, then higher-richness contracts exhibit significantly larger oracle-isolation gaps (Spearman ρ ≥ 0.3, p < 0.05), because universal properties with more complex quantification are less exhaustively sampled by finite equality-based tests.

**Rationale:** This mechanistic step tests whether the oracle strength finding (H-M1) is explained by contract semantic complexity. A richness gradient validates the universal-property mechanism and strengthens the contribution. A flat gradient weakens the mechanism claim but does not invalidate the oracle-strength finding (H-M1 can still pass independently).

**Variables:**
- IV: Contract richness tier (AST-parsed: quantified/relational/structural complexity score)
- DV: Oracle-isolation gap per task (from H-M1 / Experiment A)
- CV: Same 364 tasks, same LLM programs evaluated in H-M1

**Verification Protocol:**
1. AST-parse all 364 ContractEval postconditions; categorize by complexity: simple (equality), structural (list/string predicates), relational (all/any quantification), compound (nested quantification).
2. Assign richness score per task (1-4 tier or continuous AST complexity metric).
3. Correlate per-task oracle-isolation gap (from Experiment A) with richness score.
4. Spearman ρ test; bootstrap 95% CI on ρ.
5. Report flat-gradient result honestly if ρ < 0.15.

**Success Criteria:**
- Primary: Spearman ρ ≥ 0.30 (p < 0.05) between richness tier and oracle-isolation gap
- Secondary: Higher-richness tier tasks show systematically larger contract-unique failure mass

**Failure Response:** IF fails → EXPLORE: flat gradient is a publishable finding; document as limitation; does not invalidate H-M1.

**Dependencies:** H-M1 (oracle-isolation gaps needed as input)

**Source:** Phase 2A causal step 2 evidence, Prof. Rex's objection about contract richness gradient

---

#### H-M3: Adaptive Search Contribution — Hypothesis PBT Finds Violations Beyond Static Oracle Coverage

**Type:** MECHANISM
**Statement:** Under ContractEval's 364 tasks, if Hypothesis PBT with icontract-hypothesis (5k adaptive examples) is compared to static EvalPlus oracle (764 fixed inputs) on the same LLM programs, then the adaptive PBT contract-failure rate exceeds the static oracle contract-failure rate by > 0 absolute (mean adaptive gap > oracle-isolation gap), because Hypothesis's adaptive input generation guided by pre-conditions explores input regions not covered by any fixed test set.

**Rationale:** This hypothesis separates oracle strength (H-M1/H-M2) from adaptive search advantage. Experiment B (adaptive PBT) vs. Experiment A (static oracle) directly tests the additional contribution of input generation strategy. The key_tension in Phase 2A explicitly identifies this as the central methodological challenge. If H-M3 passes but H-M1 also passes, both oracle semantics AND adaptive search contribute.

**Variables:**
- IV: Input generation strategy (static 764 EvalPlus inputs vs. adaptive Hypothesis PBT 5k examples)
- DV: Adaptive search contribution = Experiment B failure rate − Experiment A failure rate per task
- CV: Same ContractEval contracts (oracle held constant); same LLM programs; same seed/budget

**Verification Protocol:**
1. Compute Experiment A failure rate per (model, task, program) from H-M1.
2. Compute Experiment B failure rate per (model, task, program) from Hypothesis PBT (5k, seed=42, 60s).
3. Adaptive contribution = mean(Exp B − Exp A) across tasks × models.
4. Wilcoxon signed-rank test: H0 that adaptive contribution = 0; bootstrap CI.
5. Report per-task filter rates to diagnose low-yield pre-conditions.

**Success Criteria:**
- Primary: mean adaptive contribution > 0 (Wilcoxon p < 0.05) — adaptive PBT finds additional violations beyond static oracle
- Secondary: adaptive contribution > 0.03 absolute for ≥50% of tasks

**Failure Response:** IF fails (adaptive contribution ≈ 0) → PIVOT to oracle-strength interpretation: conclusion shifts to "contract semantics, not adaptive search, drives the gap" — still valid contribution via H-M1.

**Dependencies:** H-M1 (Experiment A static results needed for comparison)

**Source:** Phase 2A causal step 3, key tension (oracle strength vs. adaptive search advantage)

---

#### H-M4: Cross-Model Variation — Contract-Satisfaction Rate is Orthogonal to pass@k

**Type:** MECHANISM
**Statement:** Under ContractEval's 364 tasks evaluated across 5 LLM families, if per-model contract-satisfaction rate is regressed against pass@1⋆ and model size, then model identity explains significant additional variance (partial ΔR² ≥ 0.10) and cross-model ranking differs (Kendall τ ≤ 0.6), and contract-strength gap varies ≥ 0.10 absolute between best and worst model families (controlling for pass@k), because LLMs differ systematically in their ability to generate code satisfying universal properties beyond test-distribution correctness.

**Rationale:** This hypothesis tests whether the contract-strength measurement is a novel axis of model evaluation. If Kendall τ is high (≥ 0.8), contracts simply replicate pass@k rankings and add no model-selection value. Low τ and high ΔR² would establish that contract evaluation complements existing benchmarks for deployment-critical applications.

**Variables:**
- IV: LLM model family (GPT-4o-mini, Claude-3-haiku, DeepSeek-Coder-V2-Lite, CodeLlama-13B, CodeLlama-34B)
- DV: Per-model contract-satisfaction rate; Kendall τ vs. pass@1⋆; partial ΔR²; cross-model range
- CV: ContractEval 364 tasks, n=10 samples per model per task, Experiment B adaptive PBT results

**Verification Protocol:**
1. Compute per-model mean contract-satisfaction rate from Experiment B (Hypothesis PBT results).
2. Compute Kendall τ and Spearman ρ between contract-satisfaction and HUMANEVAL+ pass@1⋆ rankings.
3. Fit regression: contract_rate ~ pass@1⋆ + log(model_size) + model_type; compute partial ΔR² for model identity.
4. Fit mixed-effects model for P3: model family coefficient controlling for task difficulty (random effect).
5. Permutation test for τ significance; report range = max_model_gap − min_model_gap.

**Success Criteria:**
- Primary: Kendall τ ≤ 0.6 (permutation p < 0.05) AND partial ΔR² ≥ 0.10
- Secondary: cross-model contract-strength gap range ≥ 0.10 absolute, model family coefficient p < 0.05

**Failure Response:** IF fails (τ ≥ 0.8 or ΔR² < 0.05) → EXPLORE: contracts replicate pass@k; reframe contribution as negative result showing contracts are redundant for model ranking; still publishable.

**Dependencies:** H-M3 (Experiment B adaptive PBT results needed)

**Source:** Phase 2A causal step 4, predictions P2 and P3

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2
              → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Mean contract-strength gap > 0 (bootstrap CI lower > 0.01) | STOP all H-M; reassess |
| H-M1 | MUST_WORK | Oracle-isolation gap ≥ 0.10, Wilcoxon p < 0.01, contract-unique ≥ 0.05 | PIVOT; investigate richness stratification |
| H-M2 | SHOULD_WORK | Spearman ρ ≥ 0.30 between richness and oracle-isolation gap | EXPLORE; document flat gradient as limitation |
| H-M3 | MUST_WORK | Adaptive contribution > 0 (Wilcoxon p < 0.05) | PIVOT to oracle-strength-only interpretation |
| H-M4 | SHOULD_WORK | Kendall τ ≤ 0.6 AND partial ΔR² ≥ 0.10 | EXPLORE; reframe as negative result |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | Week 1-2 |
| Gate 1 | — | Week 2 (◆) |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | Week 3-6 |
| Gate 2 | — | Week 6 (◆) |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Oracle Soundness Failure (Source: A1)**
- Description: ContractEval reference implementations fail soundness check; contracts contain false positives
- Severity: High
- Likelihood: Low (domain-expert written contracts)
- Affected Hypotheses: H-E1, H-M1, H-M2, H-M3, H-M4 (all)
- Mitigation:
  1. Prevention: Run pre-experiment soundness check (100k examples, 2h per task) before any model evaluation
  2. Detection: Count tasks where reference fails ≥1 contract under high-budget PBT
  3. Response: Quarantine unsound tasks; proceed on remaining set; report quarantine rate
- Early Warning: >5% of 364 tasks fail soundness check

**Risk R2: Low icontract-hypothesis Yield (Source: A2)**
- Description: icontract-hypothesis fails to generate ≥100 valid samples for >20% of tasks; Experiment B has low coverage
- Severity: Medium
- Likelihood: Medium (complex pre-conditions in ContractEval)
- Affected Hypotheses: H-M3, H-M4 (Experiment B dependent)
- Mitigation:
  1. Prevention: Test icontract-hypothesis on sample of 20 tasks before full run
  2. Detection: Report per-task filter rate distribution; flag tasks with <100 valid samples
  3. Response: Exclude low-yield tasks from Exp B analysis; report as limitation
- Early Warning: >30% of tasks with filter rate >95%

**Risk R3: EvalPlus Input Mapping Failure (Source: A3)**
- Description: EvalPlus published inputs don't cleanly map to ContractEval task subset
- Severity: High
- Likelihood: Low (ContractEval is documented as strict HumanEval+/MBPP+ subset)
- Affected Hypotheses: H-M1, H-M2 (Experiment A dependent)
- Mitigation:
  1. Prevention: Verify task ID overlap between ContractEval and EvalPlus before starting
  2. Detection: Count exact task ID matches
  3. Response: Generate fresh matched inputs for unmatched tasks (fallback)
- Early Warning: <90% task ID overlap

**Risk R4: API Rate Limiting (Source: A4)**
- Description: OpenAI/Anthropic APIs rate-limit at scale of 364×10 samples
- Severity: Low
- Likelihood: Low (standard evalplus benchmark evaluation)
- Affected Hypotheses: H-M4 (requires all 5 models)
- Mitigation:
  1. Prevention: Use evalplus retry logic; batch requests
  2. Detection: Monitor API error rate during generation
  3. Response: Reduce to n=5 samples; estimate statistical power impact
- Early Warning: >10% API errors per model

**Risk R5: Empty Contract-Unique Category (Source: A5)**
- Description: Contract-unique failures (output-equal but contract-failing) < 5% — contracts are redundant
- Severity: High
- Likelihood: Low (h-e1 confirmed 27 such violations in tractable subset)
- Affected Hypotheses: H-M1 (primary success criterion)
- Mitigation:
  1. Prevention: h-e1 precedent provides validated lower bound; A5 is empirically grounded
  2. Detection: Classify failures in Experiment A immediately
  3. Response: Report as negative result; still publishable finding about contract redundancy
- Early Warning: Contract-unique mass <0.02 in first 50 tasks analyzed

### 4.2 Risk Summary

| ID | Risk | Source | Severity | Affected | Priority |
|----|------|--------|----------|----------|----------|
| R1 | Oracle soundness failure | A1 | High | All | 1st (pre-experiment) |
| R3 | EvalPlus input mapping failure | A3 | High | H-M1, H-M2 | 2nd (pre-experiment) |
| R5 | Empty contract-unique category | A5 | High | H-M1 | 3rd (run Exp A first) |
| R2 | Low icontract-hypothesis yield | A2 | Medium | H-M3, H-M4 | 4th (pilot test) |
| R4 | API rate limiting | A4 | Low | H-M4 | 5th (monitor) |

Critical/High Risks: 3 | Medium Risks: 1 | Low Risks: 1

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1 (EXISTENCE — no dependencies)
         │
         ▼
[Level 1 - Core Oracle: MUST_WORK]
    H-M1 ← H-E1 (Experiment A: oracle isolation)
         │
         ├──────────────────────┐
         ▼                      ▼
[Level 2a]               [Level 2b]
    H-M2 ← H-M1               H-M3 ← H-M1
    (richness gradient)        (adaptive search)
                                │
                                ▼
                          [Level 3]
                          H-M4 ← H-M3
                          (cross-model variation)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M3 → H-M4
Branch: H-M1 → H-M2 (parallel with H-M3)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 2 | H-M3 | H-M1 | MUST_WORK |
| 3 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ W1-2    │ W3-4    │ W5     │ W6     │
─────────────────────┼─────────┼─────────┼────────┼────────┤
PHASE 1: Foundation  │         │         │        │        │
  H-E1               │ ████████│         │        │        │
  [Gate 1 ◆]         │         ◆         │        │        │
─────────────────────┼─────────┼─────────┼────────┼────────┤
PHASE 2: Mechanisms  │         │         │        │        │
  H-M1 (Exp A)       │         │ ████████│        │        │
  H-M2 (richness)    │         │         │ ████   │        │
  H-M3 (Exp B)       │         │         │ ████   │        │
  H-M4 (cross-model) │         │         │        │ ████   │
  [Gate 2 ◆]         │         │         │        │     ◆  │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M3 → H-M4
Total Duration: 6 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M3) + 1 (H-M4)
Parallel Branch: H-M1 → H-M2 (Week 5, overlaps H-M3)
Slack: H-M2 has 0 slack (Week 5 only)
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
- Condition: 0 (not required)

Verification Phases: 2
1. Foundation (H-E1) — 2 weeks
2. Mechanisms (H-M1 to H-M4) — 4 weeks

Experiments: 2 (Exp A: oracle isolation; Exp B: adaptive PBT)
Models: 5 (2 closed API + 3 open HuggingFace/vLLM)
Tasks: 364 (ContractEval)
Estimated API cost: $50-100
Total Duration: 6 weeks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** LLM-generated code that passes unit tests systematically fails universal properties encoded in formal contracts, detectable via execution-based checking across model families.

**Supporting Evidence:**
1. h-e1 confirmed 7.42% violation rate in tractable subset — mechanism is empirically real
2. ContractEval contracts use list comprehensions, all/any quantification — richer than equality checks
3. EvalPlus: even 764-test dense testing leaves semantic gaps (52.9% test-passing programs fail hidden checks per OpenAI Code Monitor 2026)

**Strengths:**
- Clear causal mechanism with falsifier per step
- 100% tractable execution approach (no Z3 ceiling)
- h-e1 precedent as validated lower bound

**Expected Outcomes:**
- P1: oracle-isolation gap ≥ 0.10 with ≥ 0.05 contract-unique mass
- P2: Kendall τ ≤ 0.6, ΔR² ≥ 0.10
- P3: ≥ 0.10 cross-model range

### 6.2 Antithesis

**Null Hypothesis (H0):** Contract checking provides no additional signal beyond dense differential testing: gap ≤ 2%, τ ≥ 0.8, R² ≥ 0.85 explained by pass@1⋆ and model size.

**Counter-Arguments:**
1. EvalPlus 764-test battery is extremely dense — may already exhaust contract-failure-inducing states for many tasks
2. icontract-hypothesis filter rates may be high, giving Experiment B low effective coverage
3. ContractEval postconditions may largely be equality predicates in disguise (flat richness gradient risk)

**Potential Failure Points:**
- Experiment A gap is small (<5%) if EvalPlus inputs happen to cover contract-failure states
- Contract-unique category is empty (≥5% threshold not met) — contracts are redundant oracles
- Cross-model τ ≥ 0.8 — contract satisfaction is monotonic with functional correctness

**Conditions Under Which H0 Would Be Supported:**
- Mean oracle-isolation gap ≤ 0.02 (near-zero)
- icontract-hypothesis filter rate >95% for >50% of tasks
- Kendall τ ≥ 0.8 between contract-satisfaction and pass@1⋆

### 6.3 Synthesis

**Balanced Assessment:** The verification plan addresses the Thesis-Antithesis dialectic through structural separation:

- **Resolution via dual-experiment design:** Experiment A (static oracle isolation) separates oracle semantics from input strategy; Experiment B (adaptive PBT) adds the search contribution. Both can independently support the thesis.
- **Resolution via h-e1 precedent:** The 27 confirmed contract-unique violations in the tractable subset provide empirical grounding that the effect is real; the question is magnitude and generality.
- **Negative result value:** If H0 is supported, this is a publishable finding — contracts are redundant with dense testing — directly relevant to the VerifAI workshop's "AI as verifiers" theme.

**Conditions for Thesis Support:** H-E1 and H-M1 both pass; contract-unique mass ≥ 0.05.

**Conditions for Antithesis Support:** H-E1 passes but H-M1 fails (gap exists but is not significant vs. EvalPlus baseline); or H-E1 fails entirely.

**Nuanced Outcome Possibilities:**
1. Full Support: H-E1 + H-M1 + H-M3 pass → oracle strength AND adaptive search both contribute
2. Partial Support: H-E1 + H-M1 pass but H-M3 fails → oracle semantics only (still strong contribution)
3. Weak Support: H-E1 passes but H-M1 fails (gap < 10%) → existence confirmed but below EvalPlus baseline
4. No Support: H-E1 fails → fundamental reassessment needed

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Gap > 0 on full 364 tasks | h-e1 only on tractable subset | H-E1 test (Exp B) |
| Oracle strength | Contracts richer than equality | EvalPlus may already sample violations | H-M1 (Exp A — static oracle isolation) |
| Richness gradient | Complex contracts > simple ones | Flat gradient weakens mechanism | H-M2 (AST stratification) |
| Adaptive search | PBT explores beyond static coverage | Oracle semantics, not search, drives gap | H-M3 (Exp B vs Exp A comparison) |
| Cross-model | Model families differ systemically | Contract satisfaction ∝ pass@k | H-M4 (Kendall τ, ΔR²) |

**Overall Robustness Score:** Medium-High (primary risks are manageable; pre-experiment checks mitigate oracle soundness and mapping risks)

**Confidence:** 0.72

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-ContractStrength-v2 — Execution-based contract checking reveals ≥10% additional failures beyond dense differential testing, with model-family-specific variation, on ContractEval's 364 tasks.
- ID: H-ContractStrength-v2, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (43% scope reduction from Phase 2A established facts)
- Sub-Hypotheses: 5 total (H-E1: 1, H-M1-4: 4)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (Gate 1 after H-E1, Gate 2 after H-M4)
- Experiments: Exp A (oracle isolation, zero new data), Exp B (adaptive PBT)

**Risk Assessment:** Medium
- Primary concerns: oracle soundness failure (R1, pre-check required), EvalPlus input mapping (R3, verify before starting)

**Immediate Action:** Begin Phase 1 with H-E1 oracle soundness pre-check, then code generation

### 7.2 Conclusions

**Key Achievements:**
- 5 hypotheses across 2 phases with clear gate conditions
- H0 addressed: gap ≤ 2%, τ ≥ 0.8 would falsify thesis
- Dual-experiment design resolves oracle-strength vs. adaptive-search tension

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Contract-strength gap exists on full 364 tasks
- Gate 1: MUST PASS — failure stops all H-M testing

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Oracle strength (Experiment A — static oracle isolation)
- H-M2: Contract richness gradient (parallel with H-M3)
- H-M3: Adaptive search contribution (Experiment B vs Exp A)
- H-M4: Cross-model variation (Kendall τ, ΔR²)
- Gate 2: H-M1 and H-M3 must pass; H-M2 and H-M4 failures document limitations

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess whether execution-based checking is tractable at scale
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 MUST_WORK; H-M3 MUST_WORK
   - H-M1 CRITICAL FAIL → PIVOT to oracle-strength-only interpretation or investigate richness stratification
   - H-M3 FAIL → Reframe to oracle-semantics contribution (H-M1 still valid)
   - H-M2/H-M4 FAIL → Document as limitations; do not block Phase 4.5

**Open Questions (from Phase 2A):**
- What fraction of ContractEval tasks fail oracle soundness check against reference implementations?
- What is the Hypothesis filter rate distribution across tasks?
- Does contract richness (AST stratification) correlate with oracle-isolation gap magnitude?
- Do open-source models exhibit systematically higher violation rates than closed models?

**Recommendations:**

1. **Immediate Actions:**
   - Run oracle soundness pre-check (100k examples, 2h) before any model evaluation
   - Verify EvalPlus task ID overlap with ContractEval (expect ≥90%)
   - Pilot test icontract-hypothesis on 20 sample tasks to estimate filter rate distribution

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path (H-E1 → H-M1 → H-M3 → H-M4)
   - $50-100 API budget for 5 models × 364 tasks × n=10 samples
   - CPU-only for Hypothesis PBT (no GPU required)

3. **Failure Management:**
   - Document all failure results honestly (negative results are publishable at VerifAI)
   - Execute PIVOT strategies as specified per hypothesis
   - Pre-register all thresholds before running experiments

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-ContractStrength-v2)
- Generated at: 2026-08-03T13:00:00+00:00, schema v10.0.0

**B. MCP Tool Usage Summary**
- Total MCP calls: 3 (ClearThought scientificmethod)
- Tools: scientificmethod ×3 (H-E1 existence, M1-M2 oracle chain, M3-M4 adaptive+cross-model)
- Archon: pipeline status check + phase task transitions

---

*Phase 2B Verification Plan — Generated 2026-08-03*
*Status: complete*
*Steps Completed: step-00 through step-10*
